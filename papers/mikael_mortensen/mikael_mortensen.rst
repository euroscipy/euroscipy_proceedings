:author: Mikael Mortensen
:email: mikaem@math.uio.no
:institution: University of Oslo

---------------------------------------------------------------------------------------------
Massively parallel implementation in Python of a pseudo-spectral DNS code for turbulent flows
---------------------------------------------------------------------------------------------

.. class:: abstract

   Direct Numerical Simulations (DNS) of the Navier Stokes equations is a 
   valuable research tool in fluid dynamics, but there are very few publicly 
   available codes and, due to heavy number crunching, codes are usually written 
   in low-level languages. In this work I describe a pure Python DNS code 
   that nearly matches the performance of pure C for thousands of processors 
   and billions of unknowns. With optimization of a few routines in Cython, 
   it is found to match the performance of a more or less identical solver 
   implemented from scratch in C++.

.. class:: keywords

   computational fluid dynamics, direct numerical simulations, pseudospectral, python

Introduction
------------

Direct Numerical Simulations (DNS) of Navier Stokes equations have been used for decades to study fundamental aspects of turbulence and it is used extensively to validate turbulence models. DNS have been conducted on an extremely large scale on the largest supercomputers in the world. S. de Bruyn Kops [deBruynKops]_ recently simulated homogeneous isotropic turbulence on a Cray XE6 architecture using a computational mesh with close to 1 trillion nodes (:math:`8192^3`). Lee *et al* [Lee]_ simulated a turbulent channel flow on a Blue Gene/Q architecture using a mesh of size :math:`15369 \times 1536 \times 11520`.
 

Because of the extremely heavy number crunching implied by DNS, researchers aim at highly optimized implementations running on massively parallel computing platforms. The largest known DNS simulations performed today are using hundreds of billions of degrees of freedom. Normally, this demands a need for developing tailored, hand-tuned codes in low-level languages like Fortran, C or C++, and with spectral methods the implementations have a reputation for being difficult, resulting in few DNS codes being openly available and easily accessible to the public and the common fluid mechanics researcher.

In this talk I will describe a ~100 line pseudo-spectral DNS solver developed from scratch in Python, using nothing more than numpy and mpi4py, possibly optimized with pyfftw and Cython. It is important to stress that the entire solver is written in Python, this in not simply a wrapper of a low-level number cruncher. The mesh is created and decomposed in Python and MPI communications are implemented using mpi4py. Two popular strategies, slab and pencil, for MPI communications of the three-dimensional Fast Fourier Transform (FFT), required by the pseudo-spectral method, will be described. In fact, I will show the entire 5 lines of Python code required to perform a 3D FFT on a massively parallel computer.

Performance tests of the pseudo-spectral DNS solver has been conducted on a BlueGene/P supercomputer at KAUST supercomputing laboratory and weak scaling results are shown in the figure below. Two MPI decompositions, slab and pencil, are shown respectively in blue and red and a pure C++ solver using the FFTW library with slab decomposition is shown in green. Ideal scaling is shown as a black line. Scaling is evidenced all the way up to the largest problem in this test, which is for a substantial computational box of size 1024^3.

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


In transforming the equations from real space to Fourier space we will be needing the corresponding wavenumber mesh

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

An explicit solver will integrate Eq. :ref:`eq:NSfinal` from given initial conditions. Any integrator may be used, here we have settled for a fourth order Runge Kutta method.

Detail of implementation
------------------------
The major challenges one has to deal with when implementing a high performance solver for Eq. (:ref:`eq:NSfinal`) in Python is the following

* MPI
* Mesh decomposition
* Three dimensional Fourier transforms with MPI
* Vectorization (numpy ufuncs)
* Dynamic loading of Python on a supercomputer

MPI/mpi4py
==========

The [mpi4py]_ Python package contains wrappers for almost the entire MPI and it has been shown to be able to distribute numpy arrays at the speed of regular C arrays. The mpi4py module allows us to write Python code with MPI just like regular low-level languages, but with a much simpler and user-friendly syntax. Since coding is performed like in C, Python implementation may, as such, be used as an easy to follow, working prototype for a complete low-level implementation in Fortran, C or C++.

Mesh decomposition
==================

The computational mesh is structured and the most common approaches to mesh decomposition are the *slab* and the *pencil* methods. The *slab* decomposition distributes the mesh along one single index, whereas the *pencil* distributes two of the three indices. The advantage of the *slab* decomposition is that it is generally faster than *pencil*, but it is limited to :math:`N` CPUs for a computational mesh of size :math:`N^3`. The *pencil* decomposition is slower, but has the advantage that it can be used by :math:`N^2` CPUs and thus allows for much larger simulations. Figure :ref:`slab` shows how the distributed mesh is laid out for *slab* decomposition using 4 CPUs. Notice that in real space the decomposition is along the first index, whereas in wavenumber space it is along the second index. This is because the third and final FFT is performed along the x-direction, and for this operation the mesh needs to be aligned either in the x-z plane or in the x-y plane. Her we have simply chosen the first option.

.. figure:: slabs.png
   :scale: 15%
   :figclass: bht

   From top to bottom slab decomposition of physical mesh, intermediate wavenumber mesh and final wavenumber mesh respectively. :label:`slab`


Three dimensional Fourier transforms with MPI
=============================================

The regular Python modules `numpy.fft`, `scipy.fftpack`, [pyfftw]_ all provide routines to do FFTs on regular (non-distributed) structured meshes along any given axis. Any one of these modules may be used, and the only challenge is that the FFTs need to be performed in parallel with MPI. None of the regular Python modules have routines to do FFT in parallel, and the main reason for this is that the FFTs need to be performed on a distributed mesh, where the mesh is distributed before the FFT routines are called. In this work we present 3D FFT routines with MPI for both the *slab* and the *pencil* decomposition. The FFTs themselves are performed on data local to one single processor, and hence the serial FFT of any provider may be used. All other operations required to perform the 3D FFT are implemented in Python. This includes both transpose operations and an MPI call to the `Alltoall` function. The entire Python implementation of the 3D FFT with MPI for a *slab* mesh is shown below


.. code-block:: python

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


Note that merely one single work array needs to be pre-allocated for the collective call to `Alltoall`. The `pyfftw` wrapping of the `libFFTW` library allocates internally work arrays for both input and output arrays, and the pointers `Uc_hatT` and `Uc_hat` above are simply references to this internal storage. 

For short of space the implementation for the *pencil* decomposition is not shown here, but it requires about twice the amount of code since the mesh needs to be transformed and distributed twice (along two indices).

Vectorization and numpy ufuncs
==============================

Besides the FFTs, the major computational cost of the pseudospectral solver lies in element-wise multiplications, divisions, subtractions and additions that are required to assemble the right hand side of Eq (:ref:`eq:NSfinal`). For efficiency it is imperative that the numpy code is vectorized, thus avoiding for-loops that are very expensive in Python. When properly vectorized the element-wise operations are carried out by numpy universal functions (so called ufuncs), calling compiled C-code on loops over the entire (or parts of) the data structures. When properly set up many arithmetic operations may be performed at near optimal speed, but, unfortunately, complex expressions are known to be rather slow compared to low-level implementations due to multiple calls to the same loop and the creation of temporary arrays. The [numexpr]_ module has actually been created with the specific goal of speeding up such element-wise complex expressions. Besides `numexpr`, the most common ways of speeding up pure Python code is through [cython]_, [numba]_ or [weave]_.

Two bottlenecks appear in the pure Python implementation of the pseudo spectral solver. The first is the *for* loops seen in the *fftn_mpi/ifftn_mpi* functions previously described. The second is the cross product that needs to be computed in Eq. (:ref:`eq:NSfinal`). A straight forward vectorized implementation and usage of the cross product is 

.. code-block:: python

    def cross(c, a, b):
        """Regular c = a x b"""
        #c[:] = numpy.cross(a, b, axis=0) 
        c[0] = a[1]*b[2] - a[2]*b[1]
        c[1] = a[2]*b[0] - a[0]*b[2]
        c[2] = a[0]*b[1] - a[1]*b[0]
        return c

    # Usage
    N = 200
    U = zeros((3, N, N, N))
    W = zeros((3, N, N, N))
    F = zeros((3, N, N, N))
    F = cross(U, W, F)

The cross product actually makes 6 calls to the multiply ufunc, 3 to subtract and also requires temporary arrays for storage. Each ufunc loops over the entire computational mesh and as such it is not unexpected that the computation of the cross product becomes a bottleneck. The built-in `numpy.cross` uses ufuncs as well and runs approximately as fast as the code shown. Moving this routine to numba or cython we can hardcode the loop over the mesh just once and speed-up is approximately a factor 5. A numba implementation is shown below

.. code-block:: python

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
.. [Lee] Lee, Myoungkyu and Malaya, Nicholas and Moser, Robert D. *Petascale Direct Numerical Simulation of Turbulent Channel Flow on Up to 786K Cores* Proceedings of the International Conference on High Performance Computing, Networking, Storage and Analysis, (2013)

.. [deBruynKops] S. de Bruyn Kops, *Classical scaling and intermittency in strongly stratified Boussinesq turbulence*, J. Fluid Mechanics vol 775, p 436-463, (2015)

.. [canuto1988] Canuto, C. and Hussaini, M. Y. and Quarteroni, A. and Zang, T. A. *Spectral Methods in Fluid Dynamics*, Springer-Verlag New York-Heidelberg-Berlin, 1988.

.. [mpi4py] https://bitbucket.org/mpi4py/

.. [pyfftw] https://github.com/hgomersall/pyFFTW

.. [numexpr] https://github.com/pydata/numexpr

.. [cython] http://cython.org/

.. [numba] http://numba.pydata.org/

.. [weave] https://github.com/scipy/weave



