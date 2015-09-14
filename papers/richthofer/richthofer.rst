:author: Stefan Richthofer
:email: stefan.richthofer@gmx.de
:institution: Institute for Neural Computation, Ruhr-Universität Bochum

----------------------------------------------------------------------------
Garbage Collection in JyNI – How to bridge Mark/Sweep and Reference Counting
----------------------------------------------------------------------------

.. class:: abstract

   Jython is a Java-based Python-implementation and the most seamless way to
   integrate Python and Java. It achieves high efficiency by compiling
   Python-code to Java byte-code and thus letting Java's JIT optimize it – an
   approach that enables Python code to call Java functions or to subclass
   Java classes. It enables Python-code to leverage Java's
   multithreading-features and utilizes Java's built-in garbage collection.
   However, it currently does not support CPython's C-API and thus does not
   support native extensions like NumPy and Scipy. Since most scientific code
   depends on such extensions, it is usually not runnable with Jython.

   For various reasons, implementing CPython's C-API is not an easy task.
   Just to name a few issues – it offers macros to access CPython internals,
   uses a global interpreter lock in contrast to Jython and lets extensions
   perform reference-counting-based garbage collection, which is incompatible
   to Java's gc-approach. For each of the arising issues, JyNI proposes a
   feasible solution; most remarkable it emulates CPython's reference counting
   garbage collection on top of Java's mark-and-sweep-based approach (taking
   care of adjacent concepts like finalizers and weak references and their
   interference with Jython). (Note that there are vague considerations around
   to switch to mark-and-sweep-based gc in a future CPython too. So this
   algorithm might one day be even relevant to CPython in terms of running
   legacy modules.) All this is designed to be binary compatible with existing
   extension-builds so that Jython can import the original C-extensions (i.e.
   the same .dll- or .so-file that CPython would use).


.. class:: keywords

   Jython, Java, Python, CPython, extensions, integration, JNI, native, NumPy, C-API, SciPy, GC

Introduction
------------

[JyNI]_ is a compatibility layer with the goal to enable [JYTHON]_ to use native
CPython extensions like NumPy or SciPy.


Implementation
--------------

In order to bridge Jython's and CPython's concepts of PyObjects, we apply three
different techniques, depending of the PyObject's implementation details.

.. figure:: Modi.eps
   :scale: 26%

   Approaches to bridge PyObjects :label:`modi`

[JyNI_ESCP13]_ describes this in more detail.


Global interpreter lock (GIL)
.............................
The global interpreter lock is a construction in CPython that prevents multiple threads from running Python code in the same process. It is usually acquired when the execution of a Python script begins and released when it ends. However, a native extension and some parts of native CPython code can release and re-acquire it by inserting the ``Py_BEGIN_ALLOW_THREADS`` and ``Py_END_ALLOW_THREADS`` macros. This way, an extension can deal with multiple threads and related things like input events (e.g. Tkinter needs this).

In contrast to that, Jython does not have a GIL and allows multiple threads at any time, using Java's threading architecture. Since native extensions were usually developed for CPython, some of them might rely on the existence of a GIL and might produce strange behaviour if it was missing. So JyNI features a GIL to provide most familiar behaviour to loaded extensions. To keep the Java parts of Jython GIL-free and have no regression to existing multithreading features, the JyNI GIL is only acquired when a thread enters native code and released when it enters Java code again – either by returning from the native call or by performing a Java call to Jython code. Strictly speaking, it is not really global (thus calling it “GIL” is a bit misleading), since it only affects threads in native code. While there can always be multiple threads in Java, there can only be one thread in native code at the same time (unless the above mentioned macros are used).


Garbage Collection
------------------

While there are standard approaches for memory management in context of JNI,
none of these is applicable to JyNI. In this section we sketch the default
approaches, illustrate why they fail and finally provide a feasible solution.

Why is Garbage Collection an issue?
...................................

Consider a typical JNI-scenario where a native object is accessed from Java.
Usually one would have a Java-object (a “peer”) that stores the native
memory address of the C-object (a pointer to it) in a ``long``-variable. The
naive approach to do memory management would be a ``finalize``-method
in the peer-class. This finalizer would then trigger a native ``free``-call
on the stored memory-handle. However, finalizers are considered bad style in
Java as they impact GC-efficiency. The recommended approach for this scenario
is based on weak references and a reference-queue (c.f. [JREF]_).

.. figure:: OrdinaryGC.eps
   :scale: 35%

   Ordinary JNI memory management :label:`oJNImm`

Figure figure :ref:`oJNImm` sketches this procedure:

* a ``java.lang.ref.WeakReference`` is used to track the peer
* actually we use a subclass of ``java.lang.ref.WeakReference`` that stores
  a copy of the peer's stored native memory-handle
* a ``java.lang.ref.ReferenceQueue`` is registered with the weak reference
* after every run, Java-GC automatically adds cleared weak references to such
  a queue if one is registered
  (this is Java's variant of Python's weak reference callbacks)
* we poll from the reference queue and clean up the corresponding native resource
* since other native objects might need the resource we don't just call ``free``,
  but instead perform reference counting

So far, this would work. But remember, JyNI also needs the opposit scenario, where
a native peer is backed by a Java-object (see figure :ref:`nnJ0`).

.. figure:: NativeNeedsJava_0050.eps
   :scale: 35%

   A native peer backed by a Java-object :label:`nnJ0`

To prevent Java-GC from destroying the Java-backend while it is in use, JNI offers
the concept of global references – JNI-``GlobalRef``-objects. However, native code
must explicitly create and release such global references. While a native global
reference exists, the Java-side referent is immortable. Now consider the referent
would hold further references to other Java-objects. The reference chain could at
some point include an object that is a peer like shown in figure :ref:`oJNImm`. This peer
would be keeping alive a native object by holding a reference-increment on it. If
the native object also holds reference-increments of other native objects, this
can create a pathological reference cycle like illustrated in figure :ref:`aprc`.

.. figure:: NativeNeedsJava.eps
   :scale: 35%

   A pathological reference cycle :label:`aprc`

This kind of cycle cannot be cleared by Java-GC as the ``GlobalRef`` prevents it.
Native reference cycle search like known from CPython could not resolve the cycle
either, as it cannot be traced through Java-side. For debugging purposes we actually
added a traverseproc-mechanism to Jython that would allow to trace references
through Java-side, but to clear such a cycle in general just tracing Java-side
references is not sufficient; Java-side reference counting would be required. This
in turn would Jython require to have a GIL, which would be an unacceptable regression.

How JyNI solves it (basic approach)
...................................

To solve this issue, JyNI explores the native reference graph using CPython's traverseproc
mechanism. This is a mechanism PyObjects must implement in order to be tractable by
CPython's garbage collector, i.e. the code that searches for reference cycles. Basically
a ``PyObject`` exposes its references to other objects this way. While JyNI explores the native
reference graph, it mirrors it on Java-side using some minimalistic head-objects
(``JyNIGCHead`` s); see figure :ref:`rnrg`. Note that with this design, also Java-object,
especialy Jython-PyObjects can participate in the reference graph keep parts of it alive.

.. figure:: JyNIGCBasic_0108.eps
   :scale: 35%

   reflected native reference graph :label:`rnrg`

If a part of the (native) reference-graph becomes unreachable (figure :ref:`cuo`), this is
reflected (asynchronously) on Java-side. At its next run, the Java-GC will collect this
subgraph and weak references registered to a reference queue can detect deleted objects and
then release native references.

.. figure:: JyNIGCBasic_0130.eps
   :scale: 35%

   clearing unreachable objects :label:`cuo`


How JyNI solves it (hard case)
..............................

The fact that the reference-graph is mirrored asynchronously can lead to bad situations.
While JyNI features API that allows C-code to report changes of the graph, we cannot
enforce native references to report such changes. However we made sure that all builtin
types instantaneously send updates to Java-side on modification.

Now consider that a native extension changes the reference graph silently and Java's GC
runs before this change was mirrored to Java-side. In that case two types of errors could
normally happen:

1) Objects might be deleted that are still in use
2) Objects that are not in use any more persist

The design applied in JyNI makes sure that only the second error can happen and that only
temporarily, i.e. objects might persist for an additional GC-cycle or two, but not forever.
To make sure that the first kind of error cannot happen, we check a to-be-deleted native
reference subgraph for inner consistency before actually deleting it. 

.. figure:: JyNIGCHard_0050.eps
   :scale: 35%

   graph must be checked for inner consistency :label:`constcy`

If not all native reference counts are explainable within this subgraph
(c.f. figure :ref:`constcy`), we redo the exploration of participating
PyObjects and update the mirrored graph on Java-side.

.. figure:: JyNIGCHard_0080.eps
   :scale: 35%

   recreated graph :label:`recreated`

While we can easily recreate the GC-heads, there might be PyObjects that
were weakly reachable from native side and were sweeped by Java-GC. In order
to restore such objects, me must perform a resurrection
(c.f. figure :label:`resurrected`).

.. figure:: JyNIGCHard_0090.eps
   :scale: 35%

   resurrected Java-backend :label:`resurrected`

The term object-resurrection refers to a situation where an object was
garbage-collected, but has a finalizer that restores a strong reference
to the object. Note that while resurrection is not recommended – actually the
possibility of a resurrection is the main reason why finalizers are
not recommended – it is a legal operation. So certain GC-heads need to be able
to resurrect an underlying Jython-PyObject and thus must have a finalizer.
Since only certain objects can be subject to a silence reference-graph
modification, it is sufficient to let only gc-heads attached to these objects
implement finalizers – we use finalizers only where really needed.


.. Fixing finalizers and weak references


.. Weak References

Todo: Explain weak references here


Roadmap
-------

The main goal of JyNI is compatibility with NumPy and SciPy, since these extensions are of most scientific importance.
Since NumPy has dependencies on several other extensions, we will have to ensure compatibility with these extensions first.
Among these are ctypes and datetime (see previous section). In order to support ctypes, we will have to support the ``PyWeakRef`` object.


Cross-Platform support
......................

We will address cross-platform support when JyNI has reached a sufficiently stable state on our development platform.
At least we require rough solutions for the remaining gaps. Ideally, we focus
on cross-platform support when JyNI is capable of running NumPy.


References
----------
.. [PyMETA] Romain Guillebert, PyMetabiosis, Python Language Summit 2015, PyCon 2015, LWN.net, https://lwn.net/Articles/641021, Web. 2015-09-14

.. [PLS_LH] Larry Hastings, Making Python 3 more attractive, Python Language Summit 2015, PyCon 2015, LWN.net, https://lwn.net/Articles/640179, Web. 2015-09-14

.. [JyNI_ESCP13] Stefan Richthofer, JyNI - Using native CPython-Extensions in Jython, Proceedings of the 6th European Conference on Python in Science (EuroSciPy 2013), http://arxiv.org/abs/1404.6390, Web. 2015-09-15

.. [JyNI] Stefan Richthofer, Jython Native Interface (JyNI) Homepage, http://www.JyNI.org, 16 Mar. 2014, Web. 19 Mar. 2014

.. [JYTHON] Python Software Foundation, Corporation for National Research Initiatives, Jython: Python for the Java Platform, http://www.jython.org, Mar. 2014, Web. 19 Mar. 2014

.. [IRONCLAD] Resolver Systems, Ironclad, http://code.google.com/p/ironclad, 26 Aug. 2010, Web. 19 Mar. 2014

.. [CPYEXT] PyPy team, PyPy/Python compatibility, http://pypy.org/compat.html, Web. 19 Mar. 2014

.. [NP4J] Joseph Cottam, NumPy4J, https://github.com/JosephCottam/Numpy4J, 11. Dec. 2013, Web. 19 Mar. 2014

.. [JEPP] Mike Johnson, Java embedded Python (JEPP), http://jepp.sourceforge.net/, 14 May 2013, Web. 19 Mar. 2014

.. [JTK] Finn Bock, jTkinter, http://jtkinter.sourceforge.net, 30 Jan. 2000, Web. 19 Mar. 2014

.. [C-API] Python Software Foundation, Python/C API Reference Manual, http://docs.python.org/2/c-api, Web. 19 Mar. 2014

.. [JREF] Peter Haggar, IBM Corporation, http://www.ibm.com/developerworks/library/j-refs, 1 Oct. 2002, Web. 19. Mar. 2014

.. [GPL] Free Software Foundation, GNU General Public License v3, http://www.gnu.org/licenses/gpl.html, 29 June 2007, Web. 19 Mar. 2014

.. [GPL_EXC] Wikipedia, GPL linking exception, http://en.wikipedia.org/wiki/GPL_linking_exception#The_classpath_exception, 23 May 2013, Web. 19 Mar. 2014

