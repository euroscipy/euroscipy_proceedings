:author: Mikael Mortensen
:email: mikaem@math.uio.no
:institution: University of Oslo and Center for Biomedical Computing, Simula Research Laboratory

---------------------------------------------------------------------------------------------
Massively parallel implementation in Python of a pseudo-spectral DNS code for turbulent flows
---------------------------------------------------------------------------------------------

.. class:: abstract

   Direct Numerical Simulations (DNS) of the Navier Stokes equations is a 
   valuable research tool in fluid dynamics, but there are very few publicly 
   available codes and, due to heavy number crunching, codes are usually written 
   in low-level languages. In this work a ~100 line standard scientific Python DNS code is described 
   that nearly matches the performance of pure C for thousands of processors 
   and billions of unknowns. With optimization of a few routines in Cython, 
   it is found to match the performance of a more or less identical solver 
   implemented from scratch in C++.

   Keys to the efficiency of the solver are the mesh decomposition and three 
   dimensional FFT routines, implemented directly in Python using MPI, wrapped 
   through MPI for Python, and a serial FFT module (both *numpy.fft* or *pyFFTW* may be used). 
   Two popular decomposition strategies, *slab* and *pencil*, have been 
   implemented and tested.  
   
.. class:: keywords

   computational fluid dynamics, direct numerical simulations, pseudo-spectral, python, FFT

Introduction
------------

Direct Numerical Simulations (DNS) of Navier Stokes equations have been used for decades to study fundamental aspects of turbulence and it is used extensively to validate turbulence models. DNS have been conducted on an extremely large scale on the largest supercomputers in the world. S. de Bruyn Kops [deBruynKops]_ recently simulated homogeneous isotropic turbulence on a Cray XE6 architecture using a computational mesh with close to 1 trillion nodes (:math:`8192^3`). Lee *et al* [Lee]_ simulated a turbulent channel flow on a Blue Gene/Q architecture using a mesh of size :math:`15369 \times 1536 \times 11520`.
 
All known DNS codes (at least to the  knowledge of the author) running on supercomputers are implemented in low-level languages like Fortran or C/C++. These  languages are known for excellent performance in heavy duty number crunching algorithms, which goes a long way to explain the popularity. Python, on the other hand, is a scripting language known for being very convenient to work with, but as a research tool more aimed at post-processing, visualization or fast prototyping than high performance computing. However, a lesser known fact is that Python is very convenient to program also with MPI, and that as long as number crunching is performed using vectorized expressions, a code may run on thousands of processors at speeds closing in on the optimal low-level codes.  

The purpose of this work is to describe a ~100 line pseudo-spectral DNS solver developed from scratch in Python, using nothing more than NumPy and MPI for Python (mpi4py), possibly optimized with pyFFTW and Cython. It is important to stress that the entire solver is written in Python, this is not simply a wrapper of a low-level number cruncher. The mesh is created and decomposed in Python and MPI communications are implemented using mpi4py. Two popular strategies, *slab* and *pencil*, for MPI communications of the three-dimensional Fast Fourier Transform (FFT), required by the pseudo-spectral method, will be described. The entire solver is available online (https://github.com/mikaem/spectralDNS) under the GPL license.

In this short paper we will first describe the Fourier transformed Navier Stokes equations that are solved for a triply periodic domain. We will then give a brief description of the implementation and show the results of performance tests conducted on a BlueGene/P supercomputer at the KAUST supercomputing laboratory. The performance of the scientific Python solver, as well as a version optimized with Cython, is compared to a pure C++ implementation. 

Navier Stokes in Fourier space
------------------------------

Turbulent flows are described by the Navier Stokes equations. DNS of the Navier-Stokes equations are often performed in periodic domains to allow the study of pure isotropic turbulence and to avoid inhomogeneities associated with flows near walls. The periodicity of the solution also allows us to lift the equations to Fourier space and to use highly accurate Fourier spectral discretization of space. In this work we consider a triply periodic domain and we use a spectral Fourier-Galerkin method [canuto1988]_ for the spatial discretization. To arrive at the equations being solved we first cast the Navier-Stokes equations in rotational form

.. math::
   :type: eqnarray
   :label: eqNS

   \frac{\partial \bm{u}}{\partial t} - \bm{u} \times \bm{\omega}   &=& \nu \nabla^2 \bm{u} - \nabla{P}, \\
   \nabla \cdot \bm{u} &=& 0, \\
   \bm{u}(\bm{x}+2\pi \bm{e}^i, t) &=& \bm{u}(\bm{x}, t), \quad \text{for }\, i=1,2,3,\\
   \bm{u}(\bm{x}, 0) &=& \bm{u}_0(\bm{x})

where :math:`\bm{u}(\bm{x}, t)` is the velocity vector, :math:`\bm{\omega}=\nabla \times \bm{u}` the vorticity vector, :math:`\bm{e}^i` the Cartesian unit vectors, and the modified pressure :math:`P=p+\bm{u}\cdot \bm{u}/2`, where :math:`p` is the regular pressure normalized by the constant density. The equations are periodic in all three spatial directions. If all three directions now are discretized uniformly in space using a structured computational mesh with :math:`N` points in each direction, the mesh, :math:`\bm{x}=(x,y,z)`, can be represented as

.. math::
   :label: eq:realmesh
   
   \bm{x} =(x_i, y_j, z_k) = \left\{\left( \frac{2\pi i}{N}, \frac{2\pi j}{N}, \frac{2\pi k}{N} \right): i,j,k \in 0,\ldots, N-1\right\} .


To transform the equations from real space to Fourier space we need the corresponding wavenumber mesh

.. math::
   :label: eq:wavemesh 
   
   \bm{k} = (k_x, k_y, k_z) = \left\{(l, m, n): \, l, m, n \in -\frac{N}{2}+1,\ldots, \frac{N}{2} \right\},

and to move back and forth between real and wavenumber space we use the three-dimensional Fourier transforms

.. math::
   :label: eq:ffteq
   :type: eqnarray

   u(\bm{x}, t) &=& \frac{1}{N^3}\sum_{\bm{k}} \hat{u}_{\bm{k}}(t) e^{\imath \bm{k}\cdot \bm{x}}, \\
   \hat{u}_{\bm{k}}(t) &=& \sum_{\bm{x}} u(\bm{x}, t) e^{-\imath \bm{k}\cdot \bm{x}}


where :math:`\hat{u}_{\bm{k}}(t)` is used to represent the Fourier coefficients and :math:`\imath=\sqrt{-1}` represents the imaginary unit. The exponential :math:`e^{\imath \bm{k}\cdot \bm{x}}` represents the basis functions for the spectral Fourier-Galerkin method. To simplify we use the notation

.. math::
   :label:
   :type: eqnarray

   \hat{u}_{\bm{k}}(t) &=& \mathcal{F}({u}(\bm{x}, t)) \left[= \mathcal{F}_{k_x} \left(\mathcal{F}_{k_y} \left( \mathcal{F}_{k_z} ({u}) \right) \right) \right], \\
   {u}(\bm{x}, t) &=& \mathcal{F}^{-1}(\hat{u}_{\bm{k}}(t)) \left[= \mathcal{F}^{-1}_{z}\left(\mathcal{F}^{-1}_{y}\left(\mathcal{F}^{-1}_{x}(\hat{{u}})\right)\right)\right], 

where the forward and inverse Fourier transforms are, respectively, :math:`\mathcal{F}` and :math:`\mathcal{F}^{-1}`. The square bracket shows the direction of the three consecutive transforms in three-dimensional space. The order of the directions are irrelevant, but the inverse needs to be in the opposite order of the forward transform.

In the spectral Fourier-Galerkin method it is possible to reduce the set of four partial differential equations (:ref:`eqNS`) to three ordinary differential equations. To this end Eq. (:ref:`eqNS`) is first transformed by multiplying with the test function :math:`e^{-\imath \bm{k}\cdot \bm{x}}` and integrating over the domain. The pressure may then be eliminated by dotting this transformed equation by :math:`\imath \bm{k}` and using the divergence constraint (in spectral space :math:`\nabla \cdot \bm{u} = \imath \bm{k}\cdot \bm{u}_{\bm{k}}`). The eact equation for the pressure then reads

.. math::
   :label: eq:pressure

   \hat{P}_{\bm{k}} = - \frac{\imath\bm{k} \cdot \widehat{( \bm{u} \times \bm{\omega})}_{\bm{k}} }{|\bm{k}|^2},

and this is used to eliminate the pressure from the momentum equation. We finally obtain ordinary differential equations for the three transformed velocity components

.. math::
   :label: eq:NSfinal

   \frac{d\hat{\bm{u}}_{\bm{k}}}{d t}  = \widehat{( \bm{u} \times \bm{\omega})}_{\bm{k}} - \nu |\bm{k}|^2  \hat{\bm{u}}_{\bm{k}} - \bm{k} \frac{\bm{k} \cdot \widehat{( \bm{u} \times \bm{\omega})}_{\bm{k}} }{|\bm{k}|^2}.

An explicit solver will integrate Eq. :ref:`eq:NSfinal` from given initial conditions. Any integrator may be used, here we have settled for a fourth order [Runge-Kutta]_ method.

Details of implementation
-------------------------
The major challenges one has to deal with when implementing a high performance solver for Eq. (:ref:`eq:NSfinal`) in Python are the following

* MPI
* Mesh decomposition
* Three dimensional Fourier transforms with MPI
* Vectorization (NumPy ufuncs)
* Dynamic loading of Python on a supercomputer

MPI/MPI for Python (mpi4py)
===========================

The [mpi4py]_ Python package contains wrappers for almost the entire MPI and it has been shown to be able to distribute NumPy arrays at the speed of regular C arrays. The MPI for Python module allows us to write Python code with MPI just like regular low-level languages, but with a much simpler and user-friendly syntax. Since coding is performed like in C, the Python implementation may, as such, be used as an easy to follow, working prototype for a complete low-level implementation in Fortran, C or C++.

Mesh decomposition
==================

The computational mesh is structured and the most common approaches to mesh decomposition are the *slab* and the *pencil* methods. The *slab* decomposition distributes the mesh along one single index, whereas the *pencil* distributes two of the three indices. The advantage of the *slab* decomposition is that it is generally faster than *pencil*, but it is limited to :math:`N` CPUs for a computational mesh of size :math:`N^3`. The *pencil* decomposition is slower, but has the advantage that it can be used by :math:`N^2` CPUs and thus allows for much larger simulations. Figure :ref:`slab` shows how the distributed mesh is laid out for *slab* decomposition using 4 CPUs. Notice that in real space the decomposition is along the first index, whereas in wavenumber space it is along the second index. This is because the third and final FFT is performed along the x-direction, and for this operation the mesh needs to be aligned either in the x-z plane or in the x-y plane. Here we have simply chosen the first option.

.. figure:: slabs.png
   :scale: 15%
   :figclass: bht

   From top to bottom slab decomposition of physical mesh, intermediate wavenumber mesh and final wavenumber mesh respectively. :label:`slab`


Three dimensional Fourier transforms with MPI
=============================================

The regular Python modules `numpy.fft`, `scipy.fftpack` and [pyfftw]_ all provide routines to do FFTs on regular (non-distributed) structured meshes along any given axis. Any one of these modules may be used, and the only challenge is that the FFTs need to be performed in parallel with MPI. None of the regular Python modules have routines to do FFT in parallel, and the main reason for this is that the FFTs need to be performed on a distributed mesh, where the mesh is distributed before the FFT routines are called. In this work we present 3D FFT routines with MPI for both the *slab* and the *pencil* decomposition. The FFTs themselves are performed on data local to one single processor, and hence the serial FFT of any provider may be used. All other operations required to perform the 3D FFT are implemented in Python. This includes both transpose operations and an MPI call to the `Alltoall` function. The entire Python implementation of the 3D FFT with MPI for a *slab* mesh is shown below


.. code-block:: python

    from pyfftw import fft, ifft, rfft2, irfft2, empty

    # Preallocated work array for MPI
    U_mpi = empty((num_processes, Np, Np, Nf), 
                  dtype=complex)

    def fftn_mpi(u, fu):
        """FFT in three directions using MPI."""
        Uc_hatT = rfft2(u, axes=(1,2))
        for i in range(num_processes): 
            U_mpi[i] = Uc_hatT[:, i*Np:(i+1)*Np]
        comm.Alltoall([U_mpi, mpitype], [fu, mpitype])    
        fu = fft(fu, axis=0)
        return fu

    def ifftn_mpi(fu, u):
        """Inverse FFT in three directions using MPI.
           Need to do ifft in reversed order of fft."""
        Uc_hat = ifft(fu, axis=0)
        comm.Alltoall([Uc_hat, mpitype], [U_mpi, mpitype])
        for i in range(num_processes):
            Uc_hatT[:, :, i*Np:(i+1)*Np] = U_mpi[i]
        u = irfft2(Uc_hatT, axes=(2,1))
        return u


Note that merely one single work array needs to be pre-allocated for the collective call to `Alltoall`. The `pyFFTW` wrapping of the `libFFTW` library allocates internally work arrays for both input and output arrays, and the pointers `Uc_hatT` and `Uc_hat` above are simply references to this internal storage. 

For short of space the implementation for the *pencil* decomposition is not shown here, but it requires about twice the amount of code since the mesh needs to be transformed and distributed twice (along two indices).

Vectorization and NumPy ufuncs
==============================

Besides the FFTs, the major computational cost of the pseudo-spectral solver lies in element-wise multiplications, divisions, subtractions and additions that are required to assemble the right hand side of Eq (:ref:`eq:NSfinal`). For efficiency it is imperative that the NumPy code is vectorized, thus avoiding for-loops that are very expensive in Python. When properly vectorized the element-wise operations are carried out by NumPy universal functions (so called ufuncs), calling compiled C-code on loops over the entire (or parts of) the data structures. When properly set up many arithmetic operations may be performed at near optimal speed, but, unfortunately, complex expressions are known to be rather slow compared to low-level implementations due to multiple calls to the same loop and the creation of temporary arrays. The [numexpr]_ module has actually been created with the specific goal of speeding up such element-wise complex expressions. Besides `numexpr`, the most common ways of speeding up scientific Python code is through [Cython]_, [Numba]_ or [weave]_.

Two bottlenecks appear in the standard scientific Python implementation of the pseudo spectral solver. The first is the *for* loops seen in the *fftn_mpi/ifftn_mpi* functions previously described. The second is the cross product that needs to be computed in Eq. (:ref:`eq:NSfinal`). A straight forward vectorized implementation and usage of the cross product is 

.. code-block:: python

    import numpy

    def cross(c, a, b):
        """Regular c = a x b"""
        #c[:] = numpy.cross(a, b, axis=0) 
        c[0] = a[1]*b[2] - a[2]*b[1]
        c[1] = a[2]*b[0] - a[0]*b[2]
        c[2] = a[0]*b[1] - a[1]*b[0]
        return c

    # Usage
    N = 200
    U = numpy.zeros((3, N, N, N))
    W = numpy.zeros((3, N, N, N))
    F = numpyzeros((3, N, N, N))
    F = cross(U, W, F)

The cross product actually makes 6 calls to the multiply ufunc, 3 to subtract, and also requires temporary arrays for storage. Each ufunc loops over the entire computational mesh and as such it is not unexpected that the computation of the cross product becomes a bottleneck. The built-in `numpy.cross` (shown in the cross code listing) uses ufuncs as well and runs approximately as fast as the code shown. Moving this routine to Numba or Cython we can hardcode the loop over the mesh just once and speed-up is approximately a factor of 5. A Numba implementation is shown below

.. code-block:: python

    from numba import jit, float64 as float

    @jit(float[:,:,:,:](float[:,:,:,:], 
         float[:,:,:,:], float[:,:,:,:]), nopython=True)
    def cross(a, b, c):
        for i in xrange(a.shape[1]):
            for j in xrange(a.shape[2]):
                for k in xrange(a.shape[3]):
                    a0 = a[0,i,j,k]
                    a1 = a[1,i,j,k]
                    a2 = a[2,i,j,k]
                    b0 = b[0,i,j,k]
                    b1 = b[1,i,j,k]
                    b2 = b[2,i,j,k]
                    c[0,i,j,k] = a1*b2 - a2*b1
                    c[1,i,j,k] = a2*b0 - a0*b2
                    c[2,i,j,k] = a0*b1 - a1*b0
        return c

The Numba code works out of the box and is compiled on the fly by a just-in-time compiler. A Cython version looks very similar, but requires compilation into a module that is subsequently imported back into python. The Cython code below uses fused types to generate code for single and double precision simultaneously.


.. code-block:: python

    cimport numpy as np
    ctypedef fused T:
        np.float64_t
        np.float32_t

    def cross(np.ndarray[T, ndim=4] a,
              np.ndarray[T, ndim=4] b,
              np.ndarray[T, ndim=4] c):
        cdef unsigned int i, j, k
        cdef T a0, a1, a2, b0, b1, b2
        for i in xrange(a.shape[1]):
            for j in xrange(a.shape[2]):
                for k in xrange(a.shape[3]):
                    a0 = a[0,i,j,k]
                    a1 = a[1,i,j,k]
                    a2 = a[2,i,j,k]
                    b0 = b[0,i,j,k]
                    b1 = b[1,i,j,k]
                    b2 = b[2,i,j,k]
                    c[0,i,j,k] = a1*b2 - a2*b1
                    c[1,i,j,k] = a2*b0 - a0*b2
                    c[2,i,j,k] = a0*b1 - a1*b0
        return c

In addition, both *scipy.weave* and *numexpr* have been tested as well, but they have been found to be slower than Numba and Cython. 

Dynamic loading of Python on supercomputers
===========================================

The dynamic loading of Python on supercomputers can be very slow due to bottlenecks in the filesystem when thousands of processors attempt to open the same files. A solution to this problem has been provided by the scalable Python version developed by J. [Enkovaara]_ and used by [GPAW]_, where CPython is modified slightly such that during import operations only a single process performs the actual I/O, and MPI is used for broadcasting the data to other MPI ranks. With scalable Python the dynamic loading times are kept at approximately 30 seconds for a full rack (4096 cores).


Parallel scaling on Blue Gene/P
-------------------------------

In this section we compare the performance of the solver with a pure C++ implementation on Shaheen, a Blue Gene/P supercomputer at the KAUST supercomputing Laboratory. The C++ solver we are comparing with has been implemented using the Python solver as prototype and the only real difference is that the C++ solver is using the 3D FFT routines from [FFTW]_ with MPI included. For optimization we are only considering the Cython implementation, because we were not able to install Numba on Shaheen.

The solver is run for a Taylor Green test case initialized as 

.. math::
   :label: TG
   :type: eqnarray

    u(x, y, z) &=& \sin(x)  \cos(y) \cos(z), \notag \\
    {v}(x, y, z) &=&-\cos(x) \sin(y) \cos(z), \notag\\
    {w}(x, y, z) &=& 0, \notag

with a Reynolds number of 1600 and a time step of 0.001. At first the implementation is verified by running the solver for a time :math:`t=[0, 20]` and comparing the results to a previously verified reference solution, generated from a well tested and established low-level pseudo-spectral solver and utilized by the annual International Workshop on High-Order [CFD]_ Methods. From start to finish, over 20,000 time steps, the L2 error norm of the solution computed by our solver never strays more than 1e-6 from the reference solution.

.. figure:: weak.png
   :scale: 50%
   :figclass: bht

   Weak scaling of various versions of the DNS solver. The slab decomposition uses :math:`4 \cdot 64^3` nodes per core, whereas the pencil decomposition uses :math:`2 \cdot 64^3`. The C++ solver uses slab decomposition and MPI communication is performed through the FFTW library. The top figure is for a standard scientific Python solver, whereas the lower figure has some key routines optimized by Cython.  :label:`weak`

.. figure:: strong.png
   :scale: 50%
   :figclass: bht

   Strong scaling of various versions of the DNS solver. The C++ solver uses slab decomposition and MPI communication is performed through the FFTW library. The top figure is for a standard scientific Python solver, whereas the lower figure has some key routines optimized by Cython. :label:`strong`

Next the weak scaling of the solver is tested by running the case for increasing number of processors, keeping the number of mesh nodes per CPU constant. Since the FFT is known to scale with problem size as :math:`N \log_2 N`, and  assuming further that FFT is the major cost, the ideal weak scaling computing time should then scale proportional to :math:`\log_2 N`. The upper panel of Figure :ref:`weak`, shows the scaling of the scientific Python solver, both with *slab* and *pencil* decomposition, compared also with the C++ solver. The *slab* solver uses mesh sizes of :math:`N=(2, 16, 128, 1024)`, whereas the *pencil* solver uses mesh sizes of :math:`N=(4, 32, 256, 2048)`. The scientific Python solver is evidently 30-40 % slower, but scaling is good - indicating that the MPI communications are performing at the level of C++. The lower panel of Figure :ref:`weak` shows the performance of the solver when certain routines, most notably the cross product and the for-loop in the routines *fftn_mpi/ifftn_mpi*, have been computed with Cython. The results show that the Python solver now operates very close to the speed of pure C++, and the scaling is equally good. Note that the largest simulations in Figure :ref:`weak` are using a computational box of size :math:`2048^3` - approximately 8 billion mesh nodes.

Strong scaling is tested for a computational box of size :math:`512^3`, for a various number of processors larger than 64. For *slab* decomposition the maximum number of CPUs is now 512, whereas for *pencil* :math:`512^2` CPUs can be used. The top panel of Figure :ref:`strong` shows the performance of the scientific Python solvers. Evidently, the performance is degrading when the number of mesh nodes per CPU becomes lower and the number of processors increases. The main reason for this poor performance can be found in the implementation of the 3D FFT, where there is a for-loop over the number of processors. When this for-loop (as well as a few other routines) is moved to Cython, we observe very good strong scaling, even better than the C++ implementation that is using MPI directly from within FFTW.

To further elaborate on the performance of the code, we note that the open source pseudo-spectral C++ solver [Tarang]_ has been benchmarked on exactly the same computer (Shaheen). Furthermore, Tarang is using the same dealiasing technique and the same 4th order Runge-Kutta integrator as we are, which should open up for direct comparison of computational efficiency. In Figure 2 of [Tarang]_ it is shown that a computational box of size :math:`1024^3` is running with 512 CPUs at approximately 50 seconds per time step. In the lower panel of Figure :ref:`weak`, we see that the current optimized Cython solver is running the same box (:math:`1024^3`) with twice as many CPUs (1024) at approximately 20 seconds per time step. Assuming perfect strong scaling (which may be unfair considering Figure 2 of [Tarang]_) this would correspond to 40 seconds per time step using half the number of CPUs, which is actually 20 % faster than Tarang.  

Conclusions
-----------

In this paper we show that it is possible to write a very good solver for direct numerical simulations of turbulent flows directly in Python, with nothing more than standard modules like NumPy, SciPy and MPI for Python (mpi4py). We also show that it is possible to get a fully competitive solver, that runs with the speed of C on thousands of processors with billions of unknowns, but then it is necessary to move a few computationally heavy routines from NumPy's ufuncs to Cython or Numba. The current paper discusses only the triply periodic domain, suitable for studying isotropic turbulence. However, the use of Python/Cython for studying turbulence is not limited to only this configuration and work is currently in progress to develop efficient Python/Cython solvers for flows with one or two inhomogeneous directions.


Acknowledgements
----------------

This work is supported by the 4DSpace Strategic Research Initiative at the University of Oslo, and a Center of Excellence grant from the Research Council of Norway to the Center for Biomedical Computing at Simula Research Laboratory.

.. Customised LaTeX packages
.. -------------------------

.. Please avoid using this feature, unless agreed upon with the
.. proceedings editors.

.. ::

..   .. latex::
..      :usepackage: somepackage

..      Some custom LaTeX source here.

References
----------
.. [Lee] M. Lee, N. Malaya and R. D. Moser *Petascale Direct Numerical Simulation of Turbulent Channel Flow on Up to 786K Cores* Proceedings of the International Conference on High Performance Computing, Networking, Storage and Analysis, (2013)

.. [deBruynKops] S. de Bruyn Kops, *Classical scaling and intermittency in strongly stratified Boussinesq turbulence*, J. Fluid Mechanics vol 775, p 436-463, (2015)

.. [canuto1988] C. Canuto, M. Y. Hussaini,  A. Quarteroni, and T. A. Zang *Spectral Methods in Fluid Dynamics*, Springer-Verlag New York-Heidelberg-Berlin, 1988.

.. [Runge-Kutta] C. W. Gear, *Numerical Initial Value Problems in Ordinary Differential Equations* (Englewood Cliffs, NJ: Prentice-Hall), Chapter 2. 1971.

.. [CFD] The annual International Workshop on High-Order CFD Methods https://www.grc.nasa.gov/hiocfd/. Reference data: https://www.grc.nasa.gov/wp-content/uploads/sites/22/C3.3_datafiles.zip

.. [GPAW] J. Enkovaara, N. A. Romero, Sameer Shende and J. J. Mortensen, *GPAW - massively parallel electronic structure calculations with Python-based software*, Procedia Computer Science, 2011.

.. [Tarang] M. Verma, A. Chatterjee, K. Reddy, R. Yadav, S. PAUL, M. Chandra and R. Samtaney *Benchmarking and scaling studies of pseudo-spectral code Tarang for turbulence simulations*, Pramana Journal of Physics, (81), (4) p. 617-629, (2013)

.. [Enkovaara] https://gitorious.org/scalable-python

.. [mpi4py] https://bitbucket.org/mpi4py/

.. [pyfftw] https://github.com/hgomersall/pyFFTW

.. [FFTW] http://www.fftw.org/

.. [numexpr] https://github.com/pydata/numexpr

.. [Cython] http://cython.org/

.. [Numba] http://numba.pydata.org/

.. [weave] https://github.com/scipy/weave



