:author: Stefan Richthofer
:email: stefan.richthofer@gmx.de
:institution: Institute for Neural Computation, Ruhr-Universität Bochum

---------------------------------------------------------
JyNI - Using native CPython-Extensions in Jython
---------------------------------------------------------

.. class:: abstract

   Jython is a Java-based Python implementation and the most
   seamless way to integrate Python and Java. However, it does
   not support native extensions written for CPython like NumPy
   and SciPy. Since most scientific Python-code fundamentally
   depends on exactly such native extensions directly or indirectly,
   it usually cannot be run with Jython. JyNI (Jython Native Interface)
   aims to close this gap. It is a layer that enables Jython-users to
   load native CPython-extensions and access them from Jython the
   same way as they would do in CPython. In order to leverage the JyNI
   functionality, you just have to put it on the Java-classpath when
   Jython is launched. It neither requires you to recompile the
   extension-code, nor to build a customized Jython-fork.
   That means, it is binary compatible with existing extension-builds.

   At the time when this abstract is written, JyNI does not fully implement
   the Python C-API and we are in fact just capable to load simple examples
   that only involve most basic built-in types. The concept is rather complete
   though and our goal is to provide the C-API needed to load NumPy as soon
   as possible. After that we will focus on SciPy and others.

   We expect that our work will also enable Java developers to use
   CPython-extensions like NumPy in their Java-code.

   For further information visit our project homepage at www.jyni.org.

.. class:: keywords

   Jython, Java, Python, CPython, extensions, integration, JNI, native, NumPy, C-API, SciPy

Introduction
------------

[JyNI]_ is a compatibility layer with the goal to enable
[JYTHON]_ to use native CPython extensions like NumPy
or SciPy. This way we aim to enable scientific Python
code to run on Jython.

.. figure:: Extensions180.eps
   :scale: 30%

   Extensions

Since Java is rather present in industry, while Python
is more present in science, JyNI is an important step
to lower the cost of using scientific code in industrial
environments.

.. figure:: JyNI180.eps
   :scale: 30%

   JyNI

Because of the complexity of the Python C-API, the task of developing JyNI revealed to be a true challenge.
Especially the frequent occurrence of preprocessor macros in the public C-API allows for no naive approaches like directly delegating every C-API call to Jython.
It turned out, that most built-in types need individual fixes, considerations and adjustments to allow seamless integration with Jython.

There have been similar approaches for other Python implementations, namely [IRONCLAD]_ for IronPython and [CPYEXT]_ for PyPy.
As far as we know, these suffer from equal difficulties as JyNI and also did not yet reach a satisfying compatibility level for
current Python versions.

Another interesting work is NumPy4J [NP4J]_, which provides Java interfaces for NumPy by embedding the CPython interpreter.
It features automatic conversion to Java-suitable types and thus allows easy integration with other Java frameworks.
A more general approach is Jepp [JEPP]_, which also works via embedding the CPython interpreter.
It also includes conversion methods between basic Python- and Java-types, but is not specifically NumPy-aware.
However, none of these approaches aims for integration
with Jython. In contrast to that, JyNI is entirely based on Jython. Though large parts are derived from CPython, the main
Python runtime is provided by Jython and JyNI delegates most C-API calls to Jython directly or indirectly.
Indirect delegation happens, if objects must be mirrored due to occurrence of direct access macros in the official C-API.
We give more details on this in the implementation-section.


Usage
-----

Thanks to Jython's hooking capabilities, it is sufficient to place ``JyNI.jar`` on the classpath (and some native libraries on the library path) when Jython is launched.
Then Jython should “magically” be able to load native extensions, as far as the needed Python C-API is already implemented by JyNI.
No recompilation, no forking – it just works with original Jython and original extensions.

Note that  the naive way does not actually set the classpath for Jython::

   java -cp "[...]:JyNI.jar:[JyNI binaries folder]"
      -jar jython.jar

The correct way is::

   java -cp "[...]:JyNI.jar:[JyNI binaries folder]:
      jython.jar" org.python.util.jython

Alternatively, one can use Jython's start-script::

   jython -J-cp "[...]:JyNI.jar:[JyNI binaries folder]"

Usually the JVM does not look for native library files on the classpath.
To ease the configuration, we built into JyNI's initializer-code that it also searches for
native libraries on the classpath. Alternatively you can place ``libJyNI.so`` and
``libJyNI-loader.so`` anywhere the JVM finds them, i.e. on the java library path (``java.library.path``) or the system's library path (``LD_LIBRARY_PATH``).

To get an impression of JyNI, proceed as described in the following subsection.

Instructions to run ``JyNIDemo.py``
...................................

* Go to [JyNI]_, select the newest release in the download section and get the sources and binaries appropriate for your system (32 or 64 bit).
* Extract ``JyNI-Demo/src/JyNIDemo.py`` from the sources.
* To launch it with CPython, extract ``DemoExtension.so`` from the bin archive.
* ``JyNIDemo.py`` adds the extension folder via ``sys.path.append([path])``.
  You can modify that line so it finds your extracted ``DemoExtension.so`` or delete the line and put
  ``DemoExtension.so`` on the pythonpath.
* If you launch ``JyNIDemo.py`` with Jython, it won't work.
  Put ``JyNI.jar``, ``libJyNI-Loader.so`` and ``libJyNI.so`` on Jython's classpath.
  ``libJyNI-Loader.so`` and ``libJyNI.so`` can alternatively be placed somewhere on the Java library path.

Jython should now be able to run ``JyNIDemo.py`` via ::

   java -cp "[...]:JyNI.jar:[JyNI binaries folder]:
      jython.jar" org.python.util.jython JyNIDemo.py

Be sure to use Jython 2.7 (beta) or newer.


Capabilities
------------

JyNI is currently available for Linux only. Once it is sufficiently complete and stable, we will work out a cross platform version compilable on Windows, Mac-OS and others.
The following built-in types are already supported:

* Number types ``PyInt``, ``PyLong``, ``PyFloat``, ``PyComplex``
* Sequence types ``PyTuple``, ``PyList``, ``PySlice``
* Data structure types ``PyDict``, ``PySet``, ``PyFrozenSet``
* Operational types ``PyModule``, ``PyClass``, ``PyInstance``, ``PyMethod``
* Singleton types ``PyNone``, ``PyNotImplemented``, ``PyEllipsis``
* Miscellaneous types ``PyBool``, ``PyString``
* Natively defined types (you cannot subclass them (yet) in Jython)
* Exception types

The function families ``PyArg_ParseTuple`` and ``Py_BuildValue`` are also supported.


Implementation
--------------

To create JyNI we took the source code of CPython 2.7 and stripped away all functionality that can be provided by Jython and is not needed for mirroring objects (see below). We kept the interface unchanged and implemented it to delegate calls to Jython via JNI and vice versa.
The most difficult thing is to present JNI-``jobject``'s from Jython to extensions such that they look like ``PyObject*`` from Python (C-API). For this task, we use the three different approaches explained below, depending on the way a native type is implemented.

In this section, we assume that the reader is familiar with the Python [C-API]_ and has some knowledge about the C programming language, especially about the meaning of pointers and memory allocation.


Python wraps Java
.................

The best integration with Jython is obtained, if ``PyObject*`` is only a stub that
delegates all its calls to Jython (figure :ref:`pwj`). This is only possible, if Jython features a
suitable counterpart of the ``PyObject`` (i.e. some subclass of ``org.python.core.PyObject``
with similar name, methods and functionality).

Further, there must not exist macros
in the official C-API that directly access the ``PyObject``'s memory. Consequently, one
cannot use ``tp_dictoffset`` to obtain the object's dictionary or ``offset`` from
``PyMemberDef`` to access the object's members.

Since members are usually only accessed via generic
getter or setter methods that also look for a ``PyGetSetDef`` with the right name, we usually re-implement
the members as get-sets. Also the dictionary access is usually performed in methods we can safely
rewrite to versions that get the dictionary from Jython.

.. figure:: PythonWrapsJava.eps
   :scale: 35%

   Python wraps Java :label:`pwj`

Examples for this method are
``PyDict``, ``PySlice`` and ``PyModule``.

The only cases where this approach fails are thus

* if Jython has no corresponding type
* if the Python C-API features macros to access the Object's memory directly

We deal with these cases in the following.


Mirroring objects
.................

If the Python C-API provides macros to access an object's data, we cannot setup
the object as a stub, because the stub would not provide the memory-positions needed
by the macros. To overcome this issue, we mirror the object if its C-API features
such direct access macros (figure :ref:`miro`).

.. figure:: MirrorMode.eps
   :scale: 35%

   Objects are mirrored :label:`miro`

Examples, where this approach is successfully applied are ``PyTuple``, ``PyList``, ``PyString``, ``PyInt``, ``PyLong``, ``PyFloat`` and ``PyComplex``.

The difficulty here is to provide a suitable synchronization between the counterparts.
If the CPython object is modified by C-code, these changes must be reflected immediately on Jython-side.
The problem here is, that such changes are not reported; they must be detected. Performing the synchronization when the C-call returns to Jython is only suitable, if no multiple threads exist.
However most of the affected objects are immutable anyway, so an initial data-synchronization is sufficient.

``PyList`` is an example for an affected object that is mutable via a macro. For ``PyList``, we
perform an individual solution. The Jython class ``org.python.core.PyList`` uses a variable of type ``java.util.List`` (which is an interface) to store its back-end. We wrote a wrapper, that provides access to the memory of the C-struct of ``PyListObject`` and implements the ``java.util.List`` interface on Java-side. If a ``PyList`` is mirrored, we replace its back-end by our wrapper. If it was initially created on Jython-side, we insert all its elements into the C counterpart on initialization.

``PyCell`` and ``PyByteArray`` are other examples that need mirror-mode, but are mutable. However, we have rough ideas how to deal with them, but since they are not used by NumPy, we don't put priority on implementing them. 


Java wraps Python
.................

If Jython provides no counterpart of an object type, the two approaches described above are not feasible. 
Typically, this occurs, if an extension natively defines its own ``PyType``-objects, but there are also examples for this in the original Python C-API. If the types were previously known, we could simply implement Jython counterparts for them and apply one of the two approaches above. However, we decided to avoid implementing new Jython objects as far as possible and solve this case with one single general approach.
``PyCPeer`` extends ``org.python.core.PyObject`` and redirects the basic methods to a native ``PyObject*`` (figure :ref:`jwp`).
The corresponding ``PyObject*``-pointer is tracked as a java-``long`` in ``PyCPeer``. Currently ``PyCPeer`` supports attribute access by delegating ``__findattr_ex__``. Further it delegates the methods ``__str__``, ``__repr__`` and ``__call__``. A more exhaustive support is planned.

.. figure:: JavaWrapsPython.eps
   :scale: 35%

   Java wraps Python :label:`jwp`

An example from the C-API is ``PyCFunction``.


Object lookup
.............

Every mentioned approach involves tying a ``jobject`` to a ``PyObject*``. To resolve this connection
as efficient as possible, we prepend an additional header before each ``PyObject`` in memory.
If a ``PyGC_Head`` is present, we prepend our header even before that, as illustrated in figure :ref:`objl`.

.. figure:: MemoryIllustration.eps
   :scale: 35%

   Memory layout :label:`objl`

In the source, this additional header is called ``JyObject`` and defined as follows:

.. code-block:: c

   typedef struct
   {
      jobject jy;
      unsigned short flags;
      JyAttribute* attr;
   } JyObject;

``jy`` is the corresponding ``jobject``, ``flags`` indicates which of the above mentioned approaches is used, whether a ``PyGC_Head`` is present, initialization-state and synchronization behavior. 
``attr`` is a linked list containing ``void``-pointers for various purpose. However, it
is intended for rare use, so a linked list is a sufficient data-structure with minimal overhead. A ``JyObject`` can use it to save pointers to data that must be deallocated along with the ``JyObject``. Such pointers typically arise when formats from Jython must be converted to a version that the original
``PyObject`` would have contained anyway.

To reserve the additional memory, allocation is adjusted wherever it occurs. This is done consequently, also where allocation occurs inline, like in most number types. The adjustment also occurs in ``PyObject_Malloc``. Though this method might not only be used for ``PyObject``-allocation, we always prepend space for a ``JyObject``. We regard this slight overhead in non-``PyObject`` cases as preferable over potential segmentation-fault if a ``PyObject`` is created via ``PyObject_NEW`` or ``PyObject_NEW_VAR``.
For these adjustments to apply, an extension must be compiled with the ``WITH_PYMALLOC``-flag activated.
Otherwise several macros would direct to the raw C-methods ``malloc``, ``free``, etc., where the neccessary
extra memory would not be reserved. So an active ``WITH_PYMALLOC`` flag is crucial for JyNI to work.
However, it should be not much effort to recompile affected extensions with an appropriate ``WITH_PYMALLOC``-flag value.

``PyType``-objects are treated as a special case, as their memory is not dynamically allocated. We resolve them simply via a lookup-table when converting from ``jobject`` to ``PyObject*`` and via a name lookup by Java-reflection if converting the other way.

The macros ``AS_JY(o)`` and ``FROM_JY(o)``, defined in ``JyNI.h``, perform the necessary pointer arithmetics to get the ``JyObject``-header from a ``PyObject*`` and vice versa. They are not intended for direct use, but are used internally by the high-level conversion-functions described below, as these also consider special cases like singletons or ``PyType``-objects.

The other lookup-direction is done via a hash map on Java-side. JyNI stores the ``PyObject*`` pointers as Java ``Long`` objects and looks them up before doing native calls. It then directly passes the pointer to the native method.

The high-level conversion-functions

.. code-block:: c

   jobject JyNI_JythonPyObject_FromPyObject
      (PyObject* op);
   PyObject* JyNI_PyObject_FromJythonPyObject
      (jobject jythonPyObject);

take care of all this, do a lookup and automatically perform initialization if the lookup fails.
Of course the ``jobject`` mentioned in these declarations may not be an arbitrary ``jobject`` but one that extends ``org.python.core.PyObject``.
Singleton cases are also tested and processed appropriately. ``NULL`` converts to ``NULL``.
Though we currently see no use-case for it, one can use the declarations in ``JyNI.h`` as JyNI C-API. With the conversion methods one could write hybrid extensions that do C-,
JNI- and Python-calls natively.



Roadmap
-------

The main goal of JyNI is compatibility with NumPy and SciPy, since these extensions are of most scientific importance.
Since NumPy has dependencies on several other extensions, we will have to ensure compatibility with these extensions first.
Among these are ctypes and datetime. For datetime there exists a Python- and Java-based implementation for Jython,
which however is not suitable to fulfill NumPy's dependency, since the original datetime module features a C-API section that
is used by NumPy. So we will have to enhance JyNI's loading procedure to overwrite specific Jython module-imports with imports
of the original native ones. At least, the latest JyNI development version is already capable of using the original native
CPython datetime module. In order to support ctypes, we will have to support the ``PyWeakRef``-object. Further there are
also other remaining built-in types, we still need to implement.

Garbage Collection
..................

To provide garbage collection for native extensions, we will adopt the original CPython garbage collector source and
use it in parallel with the Java garbage collector.
This is not really a lightweight solution, but the only way to provide CPython behavior for native extensions in a most
familiar fashion. The CPython garbage collector will be responsible to collect mirrored objects, native stubs and objects
created by native extensions. While in mirror case, the corresponding objects can be collected independently,
in wrapper case we will ensure that the stub keeps the corresponding object alive by maintaining a non-weak reference.
After the stub has been garbage collected by either collector, the reference that keeps the back-end alive vanishes and
the back-end can be collected by the other collector.

Cross-Platform support
......................

We will address cross-platform support when JyNI has reached a sufficiently stable state on our development platform.
At least we require rough solutions for the remaining gaps. Ideally, we focus
on cross-platform support when JyNI is capable of running NumPy.


License
-------

JyNI is released under the GNU [GPL]_ version 3.
To allow for commercial use, we add the classpath exception [GPL_EXC]_ like known from GNU Classpath to it.

.. GNU GPL v3 applies by its formulation found at [GPL]_.

.. The formulation of the classpath exception is as follows:

	"Linking this library statically or dynamically with other modules is
	making a combined work based on this library.  Thus, the terms and
	conditions of the GNU General Public License cover the whole
	combination.

	As a special exception, the copyright holders of this library give you
	permission to link this library with independent modules to produce an
	executable, regardless of the license terms of these independent
	modules, and to copy and distribute the resulting executable under
	terms of your choice, provided that you also meet, for each linked
	independent module, the terms and conditions of the license of that
	module.  An independent module is a module which is not derived from
	or based on this library.  If you modify this library, you may extend
	this exception to your version of the library, but you are not
	obligated to do so.  If you do not wish to do so, delete this
	exception statement from your version."

We were frequently asked, why not LGPL, respectively what the difference to LGPL is.
In fact, the GPL with classpath exception is less restrictive than LGPL.
[GPL_EXC]_ states this as follows:
The LGPL would additionally require you to "allow modification of the portions of the library you use".
For C/C++ libraries this especially requires distribution of the compiled .o-files from the pre-linking stage.
Further you would have to allow "reverse engineering (of your program and the library) for debugging such modifications".

References
----------
.. [JyNI] Stefan Richthofer, Jython Native Interface (JyNI) Homepage, http://www.JyNI.org, 29 Sep. 2013, Web. 29 Sep. 2013

.. [JYTHON] Python Software Foundation, Corporation for National Research Initiatives, Jython: Python for the Java Platform, http://www.jython.org, Sep. 2013, Web. 29 Sep. 2013

.. [IRONCLAD] Resolver Systems, Ironclad, http://code.google.com/p/ironclad, 26 Aug. 2010, Web. 29 Sep. 2013

.. [CPYEXT] PyPy team, PyPy/Python compatibility, http://pypy.org/compat.html, Web. 29 Sep. 2013

.. [NP4J] Joseph Cottam, NumPy4J, https://github.com/JosephCottam/Numpy4J, 02. Sep. 2013, Web. 29 Sep. 2013

.. [JEPP] Mike Johnson, Java embedded Python (JEPP), http://jepp.sourceforge.net/, 14 May 2013, Web. 29 Sep. 2013

.. [GPL_EXC] Wikipedia, GPL linking exception, http://en.wikipedia.org/wiki/GPL_linking_exception#The_classpath_exception, 23 May 2013, Web. 29 Sep. 2013

.. [C-API] Python Software Foundation, Python/C API Reference Manual, http://docs.python.org/2/c-api, Web. 29 Sep. 2013

.. [GPL] Free Software Foundation, GNU General Public License v3, http://www.gnu.org/licenses/gpl.html, 29 June 2007, Web. 29 Sep. 2013
