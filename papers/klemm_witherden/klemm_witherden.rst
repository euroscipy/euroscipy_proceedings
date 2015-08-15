:author: Michael Klemm
:email: michael.klemm@intel.com
:institution: Intel Deutschland GmbH, Germany

:author: Freddie Witherden
:email: freddie@witherden.org
:institution: Imperial College London, UK

:author: Peter Vincent
:email: p.vincent@imperial.ac.uk
:institution: Imperial College London, UK


--------------------------------------
Using the pyMIC Offload Module in PyFR
--------------------------------------

.. class:: abstract

    To be written...

.. class:: keywords

  TBD



Introduction
------------

To be written...

Related Work
------------


Introduction to PyFR
--------------------

PyFR [Wit14]_ is an open-source Python framework for solving advection-diffusion problems of the form

.. math::

  \frac{\partial u}{\partial t} + \nabla \cdot \mathbf{f}(u, \nabla u) = S( \mathbf{x}, t),

where :math:`u(\mathbf{x},t)` is a state vector representing the solution, :math:`\mathbf{f}` a flux function, and :math:`S` a source term.
A prominent example of an advection-diffusion type problem are the compressible Navier-Stokes equations of fluid dynamics.
The efficient solution of which, especially in their unsteady form, is of great interest to both industry and academia.
PyFR is based around the flux reconstruction (FR) approach of Huynh [Huy07]_.
FR is both high-order accurate in space and can operate unstructured grids.
In FR the computational domain of interest is first discretized into an mesh of conforming elements.
Inside of each element two sets of points are defined: one in the interior of the element, commonly termed the *solution points*, and another on the surface of the element, termed the *flux points*.

In FR the solution polynomial inside of each element, as defined by the values of :math:`u` at the solution points, is discontinuous across elements.
This gives rise to a so-called Riemann problem on the interfaces between elements.
By solving this problem it is possible to obtain a common normal flux polynomial along each interface of an element.
This polynomial can then be used to *correct* the divergence of the discontinuous flux inside of each element to yield an approximation of :math:`\nabla \cdot \mathbf{f}` that sits in the same polynomial space as the solution.
Once the semi-discretized form has been obtained it can then be used to march the solution forwards in time.
Accomplishing this requires two distinct kinds of operations (i) interpolating/correcting quantities between flux/solution points, and (ii) evaluating quantities (such as the flux) at either individual solution points or pairs of flux points.
When moving quantities, say from the solution points to the flux points, the value at each flux point is given as a weighted sum of the quantity at each solution point

.. math::

    q^{(f)}_{e,i} = \sum_j \alpha_{e,ij} q^{(u)}_{e,j},

where :math:`q` represents the quantity, :math:`e` the element number, :math:`i` the flux point number, and :math:`\alpha_{e,ij}` is a matrix of coefficients that encodes the numerics.
This can be identified as a matrix-vector product; or in the case of an :math:`N`-element simulation, :math:`N` matrix-vector products.
If the quantities are first mapped from physical space to a reference space then the :math:`\alpha_{e,ij}` coefficients become identical for each element of a given type.
Hence, the above operation can be reduced to a single matrix-matrix product.
Depending on the order of accuracy between :math:`{\sim}50\%` and :math:`{\sim}85\%` of the wall clock time in an FR code is spent performing such multiplications.
The remaining time is spent in the point-wise operations.
These kernels are a generalization on the form ``f(in1[i], in2[i], ..., &out1[i])``.
As there are no data dependencies between iterations the point-wise kernels are both trivial to parallelize and highly bound by available memory bandwidth.
Given that both matrix multiplication and point-wise evaluation are amenable to acceleration we note
that it is possible to offload all computation within an FR step.
This property is highly desirable as it avoids the need to continually transfer data across the relatively slow PCIe bus.

Our Python implementation of FR, PyFR, has been designed to be compact, efficient, scalable, and performance portable across a range of hardware platforms.
This is accomplished through the use of pluggable *backends*.
Each backend in PyFR exposes a common interface for

#. memory management;
#. matrix multiplication;
#. run time kernel generation, compilation, and invocation.

Kernels are written *once* in a restrictive C-like domain specific language (DSL) which the backend then translates into the native language of the backend.
In PyFR the DSL is built on top of the popular Mako templating engine [Bay15]_.
The specification of the DSL exploits the fact that—at least for point-wise operations—the major parallel programming languages C/OpenMP, CUDA, and OpenCL differ only in how kernels are prototyped and how elements are iterated over.
In addition to portability across platforms the use of a run-time based templating language confers several other advantages.
Firstly, Mako permits Python expressions to be used inside templates to aid in generating the source code for a kernel.
This is significantly more flexible than the C pre-processor and much simpler than C++ templates.
Secondly, as the end result is a Python string it is possible to post-process the code before it is compiled.
A use case for this capability within PyFR is to ensure that when running at single precision that all floating point constants are suffixed by ``.f``.
Doing so helps to avoided unwanted auto-promotion of expressions and avoids the need for awkward casts inside the kernel itself.
Moreover, it is also trivial to allow for user-defined functions and expressions to be inserted into a kernel.
PyFR, for example, permits the form of source term, :math:`S(\mathbf{x},t)`, to be specified as part of the input configuration file.
Without runtime code generation this would require an expression evaluation library and is unlikely to be competitive with the code generated by an optimizing compiler.
Currently, backends exist within PyFR for targetting generic CPUs through a C/OpenMP backend, NVIDIA GPUs via a CUDA backend based on PyCUDA [Klö12]_, and any device with an OpenCL runtime via an OpenCL backend based on PyOpenCL [Klö12]_.
Using these backends PyFR has been shown to be performance portable across a range of platforms [Wit15]_.
Sustained performance in excess of 50% of peak FLOPs has been achieved on both Intel CPUs and NVIDIA GPUs.

To scale out across multiple nodes PyFR has support for distributed memory parallelism using MPI.
This is accomplished through the mpi4py wrappers [Dal15]_.
Significant effort has gone into ensuring that communication is overlapped with computation with all MPI requests being both persistent and non-blocking.
On the Piz Daint supercomputer at CSCS PyFR has been found to exhibit near perfect weak scalability up to 2000 NVIDIA K20X GPUs [Vin15]_.
The wire format used by PyFR for MPI buffers is independent of the backend being used.
It is therfore possible for different MPI ranks to use different backends.
This enables simulations to be run on heterogeneous clusters containing a mix of CPUs and accelerators.
However, as discussed in [Wit15]_, this capability comes at the cost of a more complicated domain decomposition process.

PyFR v1.0.0 is released under a three-clause new style BSD license and is available from http://pyfr.org.
Key functionality summarised below.

Dimensions
    2D, 3D

Elements
    Triangles, quadrilaterals, hexahedra, tetrahedra, prisms, pyramids

Spatial orders
    Arbitary

Time steppers
    RK4, RK45[2R+], TVDRK3

Precisions
    Single, Double

Backends
    C/OpenMP, CUDA, OpenCL

Communication
    MPI

File format
    Parallel HDF5

Systems
    Euler, compressible Navier-Stokes


The pyMIC Module
----------------

The Python Offload module for the Intel(R) Many Core Architecture [KlEn14]_, follows Python's philosophy by providing an easy-to-use, but widely applicable interface to control offloading to the coprocessor.
A programmer can start with a very simplistic, maybe non-optimal, offload solution and then refine it by adding more complexity to the program and exercising more fine-grained control over data transfers and kernel invocation.
The guiding principle is to allow for a first, quickly working implementation in an application, and then offer the mechanisms to incrementally increase complexity to improve the first offload solution.
Because Numpy is a well-known and widely used package for (multi-dimensional) array data in scientific Python codes, pyMIC is crafted to blend well with Numpy's ``ndarray`` class and its corresponding array operations.

To foster cross-languge compatibility and to support Python extension modules written in C/C++ and Fortran, pyMIC integrates well with other offload programming models for the Intel coprocessor, succh as Intel(R) Language Extensions for Offloading (LEO) and OpenMP 4.0 ``target`` constructs.
Programmers can freely mix and match offloading on the Python level with offloading performed in extension modules.
For instance, one could allocate and transfer an ``ndarray`` on the Python level through pyMIC's interfaces and then use the data from within an offloaded C/C++ region in an extension module.

Design
``````


Using pyMIC to Offload PyFR
---------------------------

Although PyFR can be run on the Intel Xeon Phi using the OpenCL backend this is configuration is not optimal.
As was outlined in section 2 the performance of PyFR depends heavily on the presence of a highly tuned matrix multiplication library.
For the Phi this is the Intel Math Kernel Library (MKL).
However, as MKL does not provide an OpenCL interface it is necessary to implement these kernels using pure OpenCL code.
This is known to be a challenging problem [McI14]_.
Hence, in order to take full advantage of the capabilities of the Phi a native approach is required.

One possible approach here is to move PyFR in its entirety onto the Phi itself and then run with the C/OpenMP backend.
However, this requires that Python, along with dependencies such as NumPy, be cross-compiled for the Phi; a significant undertaking.
Additionally, as ICC does not run natively on the Phi an additional set of scripts would also be required to ‘offload’ the compilation of runtime generated kernels onto the host.
Moreover, with this approach the initial start up phase would also be run on the Phi itself.
As the single threaded performance of the Phi is significantly less than that of a recent Xeon CPU this is likely to result in a substantial increase in the start up time of PyFR.
It was therefore decided to add a native MIC backend into PyFR.

On account of its need to target CUDA and OpenCL the PyFR backend interface is relatively low-level.
At start up the solver code in PyFR allocates large blocks of memory which it then slices up into smaller pieces.
A backend must therefore provide a means of both allocating memory and copying regions of this memory to/from the host.
In contrast to this pyMIC is a relatively high-level library whose core tenant is an ``ndarray`` type.
While writing the MIC backend for PyFR we therefore had to add a low level interface to pyMIC that enables raw memory to be allocated on the device and fine grained copying to/from this memory.

The resulting backend consists of approximately 700 lines of pure Python code and 200 lines of Mako templates.
As the native programming language for the Phi is OpenMP annotated C code the DSL translation engine for the MIC is almost identical to the one used in the existing C/OpenMP backend with the only changes being around how arguments are passed into kernels.
These generated kernels are then compiled at runtime using ICC on the host to produce a shared library.
This library is then given to pyMIC which takes care of migrating it onto the device.

Matrix multiplications are handled by invoking a native kernel which itself calls out to the ``cblas_sgemm`` and ``cblas_dgemm`` routines from MKL.



Performance Results
-------------------

To be written...




Conclusion and Future Work
--------------------------

To be written...



Acknowledgments
---------------
Peter Vincent and Freddie Witherden would like to thank the Engineering and Physical Sciences Research Council for their support via a Doctoral Training Grant and an Early Career Fellowship (EP/K027379/1).

Intel, Xeon, and Xeon Phi are trademarks or registered trademarks of Intel Corporation or its subsidiaries in the United States and other countries.

* Other names and brands are the property of their respective owners.

Software and workloads used in performance tests may have been optimized for performance only on Intel microprocessors.
Performance tests, such as SYSmark and MobileMark, are measured using specific computer systems, components, software, operations and functions.
Any change to any of those factors may cause the results to vary.
You should consult other information and performance tests to assist you in fully evaluating your contemplated purchases, including the performance of that product when combined with other products.
For more information go to http://www.intel.com/performance.

Intel's compilers may or may not optimize to the same degree for non-Intel microprocessors for optimizations that are not unique to Intel microprocessors.
These optimizations include SSE2, SSE3, and SSSE3 instruction sets and other optimizations.
Intel does not guarantee the availability, functionality, or effectiveness of any optimization on microprocessors not manufactured by Intel. Microprocessor-dependent optimizations in this product are intended for use with Intel microprocessors.
Certain optimizations not specific to Intel microarchitecture are reserved for Intel microprocessors.
Please refer to the applicable product User and Reference Guides for more information regarding the specific instruction sets covered by this notice.



References
----------
.. [Bay15] M Bayer.  Mako: templates for Python. http://www.makotemplates.org

.. [Dal15] L Dalcin. mpi4py: MPI for python, http://mpi4py.scipy.org/

.. [Huy07] HT Huynh. A flux reconstruction approach to high-order schemes including discontinuous Galerkin methods. AIAA paper, 4079:2007, 2007.

.. [KlEn14] M. Klemm and J. Enkovaara. *pyMIC: A Python Offload Module for the Intel(R) Xeon Phi(tm) Coprocessor*, 4th Workshop on Python for High Performance and Scientific Computing, November 2014, New Orleans, LA, Online at http://www.dlr.de/sc/Portaldata/15/Resources/dokumente/pyhpc2014/submissions/pyhpc2014_submission_8.pdf.

.. [Klö12] A Klöckner, N Pinto, Y Lee, B Catanzaro, P Ivanov, and A Fasih. PyCUDA and PyOpenCL: A scripting-based approach to GPU run-time code generation. Parallel Comput., 38(3):157–174, 2012.

.. [McI14] S McIntosh-Smith and T Mattson, High Performance Parallelism Pearls: Chapter 22, Morgan Kaufmann, 2014.

.. [Vin15]  PE Vincent, FD Witherden, AM Farrington, G Ntemos, BC Vermeire, JS Park, and AS Iyer. PyFR: Next-Generation High-Order Computational Fluid Dynamics on Many-Core Hardware. Paper AIAA-2015-3050, 22nd AIAA Computational Fluid Dynamics Conference, 22–26 June 2015, Dallas, Texas, USA.

.. [Wit14] FD Witherden, AM Farrington, and PE Vincent. PyFR: An open source framework for solving advection–diffusion type problems on streaming architectures using the flux reconstruction approach. Computer Physics Communications, 185(11):3028–3040, 2014.

.. [Wit15] FD Witherden, BC Vermeire, and PE Vincent.  Heterogeneous computing on mixed unstructured grids with PyFR.  Accepted for publication in Computers & Fluids, 2015.


