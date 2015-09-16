:author: Stefan Richthofer
:email: stefan.richthofer@gmx.de
:institution: Institute for Neural Computation, Ruhr-Universität Bochum

-------------------------------------------------------------------------------
Garbage Collection in JyNI – How to bridge Mark/Sweep and Reference Counting GC
-------------------------------------------------------------------------------

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

As virtual-machine-languages, Python and Java both depend on native language bindings/extensions in many scenarios. Especially scientific code mostly relies on NumPy or native interfaces to some computation- or control-framework that connects Python to problem-specific hardware or libraries.
Developing and maintaining such bindings is usually a difficult and error-prone task. One major goal of the JyNI-project is to let Python and Java – with the help of [JYTHON]_ – share their pools of language-bindings, vastly enriching both ecosystems.

While Jython already enables Python-code to access Java-frameworks and also native JNI Java/C-extensions, it currently locks out all CPython-specific extensions. Remember that this does not only affect the actual C-extensions, but also all Python-frameworks that have a – maybe single, subtle – dependency on such an extension. Dependencies can include:

* Libraries like NumPy that are written directly in terms of the C-API. These libraries, which in turn link native libraries like BLAS, are widely used in the Python ecosystem, especially in scientific code.

* Cython is a popular tool to build optimized C-code from Python source that has been annotated with types and other declaration, using the C-API to link.

* The ctypes and CFFI modules, comparable to JNA and JFFI in the Java-world respectively, are other popular means of providing support for C bindings, also all written to use the C-API.

* SWIG, Pyrex (from which Cython was derived) and Boost.Python are further tools that create extensions using the C-API.

[JyNI]_ (Jython Native Interface) is going to improve this situation. It is a compatibility layer that implements CPython's C-API on top of JNI and Jython. This way it enables Jython to load native CPython-extensions and use them the same way as one would do in CPython. To leverage this functionality, no modification to Python code or C-extension source-code is required – one just needs to add JyNI.jar to Jython's classpath (along with its binary libraries). That means JyNI is binary compatible with existing builds of CPython-extensions.
 
Developing JyNI is no trivial task, neither is it completed yet. Main reason for this is Python's rather complex C-API that allows to access internal structures, methods and memory-positions directly or via C-macros (in some sense CPython simply exposes its own internal API via a set of public headers). Existing extensions frequently *do* make use of this, so it is not a purely academical concern. Concepts like Python's global interpreter lock (GIL), exception-handling and the buffer-protocol are further aspects that complicate writing JyNI. [PyMETA_PLS15]_ mentions the same issues from PyPy's perspective and confirms the difficulty of providing CPython's native API.

By far the most complex issue overall – and main focus of this paper – is garbage collection. Unlike JNI, CPython offers C-level access to its garbage collector (GC) and extensions can use it to manage their memory. Note that in contrast to Java's mark-and-sweep-based GC, CPython's GC uses reference-counting and performs reference-cycle-search. Adopting the original CPython-GC for native extensions is no feasible solution in JyNI-context as pure Java-objects can become part of reference-cycles that would be untraceable and cause immortal trash. Section :ref:`why-is-garbage-collection-an-issue` describes this issue in detail.

.. Further we plan to have a GIL-free mode. Note that CPython mainly needs the GIL, because reference 
   counters are not atomic. Our GIL-free mode would completely substitutes extensions' reference 
   counting by Java-GC. However this mode can break some extensions depending on how they internally 
   use Python-references. It additionally will have an increased demand on reference-handles on Java 
   side, so developers must consider for each extension individually whether GIL-free mode is feasible 
   and valuable (JyNI will presumably allow to set this mode per-extension).

While there are conceptual solutions for all mentioned issues, JyNI does not yet implement the complete C-API and currently just works as a proof of concept. However we are working to provide sufficient C-API to use ctypes (many Python-libraries, e.g. for graphics and 3D-plotting etc. have this as the single native dependency), NumPy, SciPy (multiarray libraries with blas- and lapack-bindings; frequently used in scientific code and machine learning frameworks) and other important extensions as soon as possible.

Overview
........

JyNI's basic functionality has been described in detail in [JyNI_ESCP13]_. After giving a short comprehension in section :ref:`implementation` we will focus on garbage collection in section :ref:`garbage-collection`. For usage examples and a demonstration-guide also see [JyNI_ESCP13]_.


Related Work
............
 
There have been similar efforts in other contexts.

* [JEP]_ and [JPY]_ can bridge Java and Python by embedding the CPython interpreter. However, none of 
  these approaches aims for integration with Jython. In contrast to that, JyNI is entirely based on 
  Jython and its runtime.

* [IRONCLAD]_ is a JyNI-equivalent approach for IronPython.

* [PyMETA]_ provides C-extension API support in PyPy to some extent by embedding the CPython 
  interpreter. Thus its approach is comparable to [JEP]_ and [JPY]_.

* [CPYEXT]_ refers to PyPy's in-house (incomplete) C-extension API support.

None of the named approaches reached a sufficient level of functionality/compatibility, at least not for current language versions (some of them used to work to some extend, but became unmaintained). In the Python ecosystem the C-extension API has been an ongoing issue since its beginning. PyPy famously has been encouraging developers to favor CFFI above C-extension API, as it is the only existing approach that has been designed to be well portable to other Python implementations. However even if this effort would work out, there would be so many legacy extensions around that a serious move to CFFI won't be done in foreseeable future.

For some of these projects JyNI's GC-approach might be a relevant inspiration, as they face the same problem if it comes to native extensions. There are even vague considerations for CPython to switch to mark-and-sweep-based GC one day to enable a GIL-free version (c.f. [PY3_PLS15]_). Backgroung here is the fact that reference-counting-based garbage collection is the main reason why CPython needs a GIL: Reference-counters are not atomic and atomic reference-counters yield insufficient performance.
In context of a mark-and-sweep-based garbage collection in a future CPython the JyNI GC-approach could be potentially adopted to support legacy extensions and provide a smooth migration path.

.. - follow-up paper of [JyNI_ESCP13]_
   - issues stated by PyMetabiosis
   - CPython attempts to remove GIL in future
   - platforms
   - related work: PyMetabiosis, Jep, JPy, IronClad


Implementation
--------------

In order to bridge Jython's and CPython's concepts of PyObjects, we apply three
different techniques, depending of the PyObject's implementation details.

.. figure:: Modi.eps
   :scale: 26%
   :figclass: h

   Approaches to bridge PyObjects. *Left*: Native PyObject wraps Java. *Center*: Java-PyObject wraps native one. *Right*: Objects are mirrored. :label:`modi`

The basic approach is to back the C-API of PyObject by a Java-PyObject via JNI.
This would avoid data-sync issues, but is only feasible if there are matching counterparts of the PyObject type in Jython and CPython (:ref:`modi`, left).
For CPython-specific types we can do it the other way round  (:ref:`modi`, center). Another problem is that CPython API defines macros in pulic headers that access PyObjects' internal data. To deal with these, we sometimes have to mirror the object (:ref:`modi`, right).
This might involve data-sync issues, but luckily macors mostly exist for immutable types, so initial synchronization is sufficient. [JyNI_ESCP13]_ describes this in more detail.


Global interpreter lock (GIL)
.............................

The global interpreter lock is a construction in CPython that prevents multiple threads from running Python code in the same process. It is mainly needed, because CPython uses reference-counting-based garbage collection and reference counters are not atomic.
It is usually acquired when the execution of a Python script begins and released when it ends. However, a native extension and some parts of native CPython code can release and re-acquire it by inserting the ``Py_BEGIN_ALLOW_THREADS`` and ``Py_END_ALLOW_THREADS`` macros. This way, an extension can deal with multiple threads and related things like input events (e.g. Tkinter needs this).

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
   :scale: 42%
   :figclass: H

   Ordinary JNI memory management :label:`oJNImm`

Figure figure :ref:`oJNImm` sketches the following procedure:

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
   :scale: 42%
   :figclass: H

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
   :scale: 42%
   :figclass: H

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

.. latex::
   \begin{figure}[H]\noindent\makebox[\columnwidth][c]{\includegraphics[scale=0.42]{JyNIGCBasic_0108.eps}}
   \caption{reflected native reference graph \DUrole{label}{rnrg}}
   \end{figure}

If a part of the (native) reference-graph becomes unreachable (figure :ref:`cuo`), this is
reflected (asynchronously) on Java-side. At its next run, the Java-GC will collect this
subgraph and weak references registered to a reference queue can detect deleted objects and
then release native references.

.. figure:: JyNIGCBasic_0130.eps
   :scale: 42%
   :figclass: H

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
   :scale: 42%
   :figclass: H

   graph must be checked for inner consistency (GC ran before orange connection was mirrored to Java-side) :label:`constcy`

If not all native reference counts are explainable within this subgraph
(c.f. figure :ref:`constcy`), we redo the exploration of participating
PyObjects and update the mirrored graph on Java-side.

.. figure:: JyNIGCHard_0080.eps
   :scale: 42%
   :figclass: H

   recreated graph :label:`recreated`

While we can easily recreate the GC-heads, there might be PyObjects that
were weakly reachable from native side and were sweeped by Java-GC. In order
to restore such objects, me must perform a resurrection
(c.f. figure :label:`resurrected`).

.. figure:: JyNIGCHard_0090.eps
   :scale: 42%
   :figclass: H

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

.. [PyMETA] Romain Guillebert, PyMetabiosis, https://github.com/rguillebert/pymetabiosis, Web. 2015-09-15

.. [PyMETA_PLS15] Romain Guillebert, PyMetabiosis, Python Language Summit 2015, PyCon 2015, LWN.net, https://lwn.net/Articles/641021, Web. 2015-09-14

.. [PY3_PLS15] Larry Hastings, Making Python 3 more attractive, Python Language Summit 2015, PyCon 2015, LWN.net, https://lwn.net/Articles/640179, Web. 2015-09-14

.. [JyNI_ESCP13] Stefan Richthofer, JyNI - Using native CPython-Extensions in Jython, Proceedings of the 6th European Conference on Python in Science (EuroSciPy 2013), http://arxiv.org/abs/1404.6390, 2014-05-01, Web. 2015-09-16

.. [JyNI] Stefan Richthofer, Jython Native Interface (JyNI) Homepage, http://www.JyNI.org, 2015-08-17, Web. 2015-09-16

.. [JYTHON] Python Software Foundation, Corporation for National Research Initiatives, Jython: Python for the Java Platform, http://www.jython.org, 2015-09-11, Web. 2015-09-16

.. [IRONCLAD] IronPython team, Ironclad, https://github.com/IronLanguages/ironclad, 2015-01-02, Web. 2015-09-16

.. [CPYEXT] PyPy team, PyPy/Python compatibility, http://pypy.org/compat.html, Web. 19 Mar. 2014

.. [JEP] Mike Johnson/Jep Team, Jep - Java Embedded Python, https://github.com/mrj0/jep, 2015-09-13, Web. 2015-09-16

.. [JPY] Brockmann Consult GmbH, jpy, https://github.com/bcdev/jpy, 2015-09-10, Web. 2015-09-16

.. [C-API] Python Software Foundation, Python/C API Reference Manual, http://docs.python.org/2/c-api, 2014-03-19

.. [JREF] Peter Haggar, IBM Corporation, http://www.ibm.com/developerworks/library/j-refs, 1 Oct. 2002, Web. 7 Apr. 2014

