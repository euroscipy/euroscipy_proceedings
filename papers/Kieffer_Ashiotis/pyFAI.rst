:author: Jérôme Kieffer
:email: jerome.kieffer@esrf.fr
:institution: European Synchrotron Radiation Facility, Grenoble, France

:author: Giannis Ashiotis
:email: giannis.ashiotis@gmail.com
:institution: European Synchrotron Radiation Facility, Grenoble, France

-------------------------------------------------------------------------
PyFAI: a Python library for high performance azimuthal integration on GPU
-------------------------------------------------------------------------

.. class:: abstract

   The pyFAI package has been designed to reduce X-ray diffraction images
   into powder diffraction curves to be further processed by scientists.
   This contribution describes how to convert an image into a radial profile
   using the Numpy package, how the process was accelerated using Cython.
   The algorithm was parallelised, needing a complete re-design to benefit
   from massively parallel devices like graphical processing units or accelerators like
   the Intel Xeon Phi using the PyOpenCL library.


.. class:: keywords

   X-rays, powder diffraction, SAXS, HPC, parallel algorithms, OpenCL.

Introduction
============

The Python programming language is widely adopted in the scientific community
and especially in crystallography, this is why a convenient azimuthal integration
routine, one of the basic algorithms in crystallography, was requested by the synchrotron community.
The advent of pixel-detectors with their very high speed (up to 3000 frames per second)
imposed strong constraints in speed that most available programs ([FIT2D]_, [SPD]_, ...),
written in Fortran or C, could not meet.

The [pyFAI]_ project started in 2011 and aims at providing a convenient *Pythonic* interface
for azimuthal integration, so that any diffractionist can adapt it to the type of experiment
he is interested in.
This contribution describes how one of the most fundamental
algorithms used in crystallography has been implemented in Python
and how it was accelerated to match the readout speeds of today's fastest detectors.

After describing a typical experiment and explaining what is measured and how it must be transformed (section 2),
section 3 describes how the algorithm can be vectorised using [NumPy]_ and sped up with [Cython]_.
Section 4 highlights the accuracy enhancement recently introduced while section 5 focuses on
the parallelisation of the azimuthal integration task on many-core systems like Graphical Processing Units (GPU) or on accelerators via [PyOpenCL]_.
In section 6, serial and parallel implementations using [OpenMP]_ and [OpenCL]_ from various vendors and devices are benchmarked.

Description of the experiment
=============================

X-rays are electromagnetic waves, similar to visible light, except for their wavelengths which are much shorter,
typically of the size of inter-atomic distances, making them a perfect probe to analyse atomic and molecular structures.
X-rays can be elastically scattered (i.e. re-emitted with the same energy) by the electron cloud surrounding atoms.
When atoms are arranged periodically, as in a crystal, scattered X-rays interfere in a constructive way
when the difference of their optical paths is a multiple of the wavelength: :math:`2d sin(\theta) = n\lambda`.
In this formula, known as *Bragg's law*, *d* is the distance between crystal plans, :math:`\theta` is the incidence angle, :math:`\lambda` is the wavelength and n is an integer.
An X-ray beam crossing a powder-like sample made of many randomly oriented small crystals is then scattered along multiple concentric cones.
In a powder diffraction experiment, one aims at measuring the intensity of X-rays as a function of the cone aperture, averaged along each ring.
This transformation is called "azimuthal integration" as it is an averaging of the signal along the azimuthal angle.

.. figure:: HEX-2D-diffraction.png

   Debye-Scherrer cones obtained from diffraction of a monochromatic X-Ray beam by a powder of crystallised material. (Credits: CC-BY-SA  Klaus-Dieter Liss) :label:`diffraction`


Azimuthal integration
=====================

While pyFAI addresses the needs of both mono- and bi-dimensional integration in different spaces (real or reciprocal),
this contribution focuses on the algorithmic and implementation part of the method.
The coordinates in which pyFAI operates can be one of the following:

* :math:`r = \sqrt{x^2+y^2}`
* :math:`\chi = tan^{-1}(y/x)`
* :math:`2\theta = tan^{-1}(r/d)`
* :math:`q = 4 \pi sin({2 \theta} / 2)/ \lambda`

The pyFAI library was designed to feature a *Pythonic* interface and work together with [FabIO]_ for image reading (or [H5Py]_ for HDF5 files).
The following snippet of code explains the basic usage of the library: :label:`use`

.. code-block:: python

   import fabio, pyFAI
   data = fabio.open("Pilatus1M.edf").data
   ai = pyFAI.load("Pilatus1M.poni")
   tth, I = ai.integrate1d(data, 1000, unit="2th_deg",\
                                        method="numpy")

Output variables' space (*r*, *q* or :math:`2\theta`) and units can be chosen with the *unit* keyword.
The *method* keyword is used to choose one of the available algorithms for the integration.
These algorithms will be described in this contribution.
However, the experiment reported here will be limited to 1D full azimuthal integration, with a planar detector, orthogonal to the incoming beam.
In this case the conics described by the beam on the detector are concentric circles.
The generic geometry used in pyFAI has already been described in [pyFAI_ocl]_.


Test case
---------

To let the reader have an idea of the scale of the problem and the performances needed, we will work on
the simulated image of gold powder diffracting an X-ray beam of wavelength = 1.0e-10m (the intensity of all rings is the same).
The detector, which has a pixel size of 1e-4m (2048x2048 pixels), is placed at a distance of 0.1 m from the sample, orthogonal to the incident beam, which coincides with the centre of the rings.
Figure :ref:`rings` represents the input diffraction image (upper part) and the integrated profile along the azimuthal angle (lower part).
The radial unit in this case is simply the radius calculated from :math:`r=\sqrt{(x - x_c)^2 + (y - y_c)^2}`,
while crystallographers would have preferred :math:`2\theta` or the scattering vector length *q*.

.. figure:: rings2.png

   Simulated powder diffraction image (top) and integrated profile (bottom).  :label:`rings`


Naive implementation
--------------------

The initial step of any implementation is calculating the radius array, from the previous formula.
Using Numpy's slicing feature one can extract all pixels which are between r1 and r2 and average out their values:

.. code-block:: python

   def azimint_naive(data, npt, radius):
       rmax = radius.max()
       res = numpy.zeros(npt)
       for i in range(npt):
           r1 = rmax * i / npt
           r2 = rmax * (i+1) / npt
           mask_r12 = numpy.logical_and((r1 <= radius),
                        (radius < r2))
           values_r12 = data[mask_r12]
           res[i] = values_r12.mean()
       return res


The slicing operation takes tens of milliseconds and needs to be repeated thousands of times for a single image,
making each integration last 40 seconds, something that is unacceptably slow. :label:`naive`

Numpy histograms
----------------

The naive formulation in section :ref:`naive` can be re-written using histograms.
The *mean* call can be replaced with the ratio of the sum of all values divided by the number of contributing pixels:

.. code-block:: python

    values_r12.mean() = values_r12.sum() / mask_r12.sum()

The denominator, *mask_r12.sum()*, can be obtained from the histogram of *radius* values and the numerator, *values_r12.sum()*
from the histogram of *radius* weighted by the *data* in the image:

.. code-block:: python

   def azimint_hist(data, npt, radius):
       histu = np.histogram(radius, npt)[0]
       histw = np.histogram(radius, npt, weights=data)[0]
       return histw / histu

This implementation takes about 800ms which is much faster than the loop written in Python,
but can be optimised by reading the radius array from central memory only once.

Cython implementation
---------------------

Histograms were re-implemented using [Cython]_ to generate simultaneously both the
weighted and the unweighted histograms with a single memory read of the radius array.
The better use of the CPU cache decreases the integration time significantly (down to 150ms on a single core).

OpenMP support in Cython
........................

To accelerate further the code we decided to parallelise the [Cython]_ code using [OpenMP]_.
While the implementation was fast, the results we obtained were wrong (by a few percent) due to
write conflicts, not protected by atomic_add operations.
Apparently the use of atomic operation is still not yet possible in [Cython]_ (summer 2014).
Multi-threaded histogramming was made possible by having several threads running simultaneously, each working on a separate histogram,
which implies the allocation of much more memory for output arrays.

.. table:: Azimuthal integration time for a 4 Mpix image measured on two Xeon E5520 (2x 4-core hyper-threaded at 2.2 GHz) :label:`Cython`

   +----------------+----------------+
   | Implement.     | Exec. time (ms)|
   +----------------+----------------+
   | loop + mean    |     44000      |
   +----------------+----------------+
   | np.histogram   |      829       |
   +----------------+----------------+
   | Cython 1_th    |      149       |
   +----------------+----------------+
   | Cython 2_th    |        81      |
   +----------------+----------------+
   | Cython 4_th    |       59       |
   +----------------+----------------+
   | Cython 8_th    |        41      |
   +----------------+----------------+
   | Cython 16_th   |        48      |
   +----------------+----------------+


The gains in performance obtained by this method (see table :ref:`Cython`) were minor, especially when using more than 2 threads,
illustrating the limits of the paralellisation scheme.
The only way to go faster is to start thinking in parallel from the beginning
and re-design the algorithm so that it works natively with lots of threads.
This approach is the one taken by [OpenCL]_, where thousands of threads are virtually running in parallel, and is described in paragraph 5.

Pixel splitting
===============

Pixel splitting is what occurs when a pixel of the detector spans over more than one of the bins of the histogram.
When this happens, the contribution to each of the bins involved is assumed to be
proportional to the area of the pixel segment that falls into that bin.
The goal behind the addition of extra complexity to the code is that the
results obtained this way ought to be less noisy than the case where pixel splitting is ignored.
This becomes more apparent when the number of pixels falling into each bin
is small like for example for 2D integration.
Figure :ref:`bidimentional` presents the results of such an integration, performed using histograms
on the top image, i.e. without pixel splitting.
Some high frequency patterns are visible near the beam center on the left-hand side of this figure.
The bottom image was produced using pixel splitting and is
unharmed by such defects, which are related to low statistics.
Note that for 2D integration, this transformation looks like an interpolation,
but interpolation neither guarantees the conservation of the signal :math:`\sum{image} = \sum{ weighted\ histogram }`
nor that of the pixels :math:`\sum{ unweighted\ histogram } = number\ of\  pixels`.

.. figure:: integrate2d.png

   Bi-dimensional azimuthal integration of the gold diffraction image using (right) or not (left) pixel splitting :label:`bidimentional`

Bounding Box
------------

The first way pixel splitting was implemented was with a bounding box like in Fit2D [FIT2D]_.
In this case we are working with an abstraction of the pixel.
This is represented by a rectangular box circumscribing the actual pixel,
with two sides parallel to the radial axis and the other two of unit length.
Presently, instead of calculating the contribution of each segment of the pixel based on its area, we use the area of the bounding box segment instead.
This greatly simplifies the algorithm's flow, providing good performance.

The algorithm loops over all the pixels of the detector, adding their contributions to the appropriate bins.
When the whole pixel falls into only one bin, there is no pixel splitting and the algorithm proceeds as in the case of the simple histogram.
If the pixel spans over more than one bin, the contribution to the two outermost bins (left and right) is calculated first and added to them.
Then, the remaining contribution is evenly distributed among the “internal” bins (if any).
Finally, the ratio of the two histograms is calculated and returned.

The trade-off of using this simplistic pixel splitting is an overestimation of the pixel size, hence a slight blurring of the signal.

Full Pixel Splitting
--------------------

In an effort to farther improve the quality of the results of the azimuthal integration,
another pixel-splitting scheme was devised,
in which no abstraction takes place and the pixel splitting
works using the area of the actual pixel segments (assuming they are straight lines).
This introduces some additional complexity to the calculations,
making the process a bit slower.

As before, the algorithm first has to check if pixel splitting occurs.
In the case it does not, the pixel is processed like in the case of the simple histogram.
Otherwise the pixel is split according to the following steps.
Firstly, a function for each of the lines that make up the sides of the pixel being processed is defined
by calculating the slope and the point of intersection.
The area of the pixel is also required.
Next, the algorithm loops over the bins that the pixel spans over and proceeds to
integrate the four functions that were previously defined over the bounds of each bin.
Taking the absolute value of the sum of all these integrals
will yield the area of the pixel segment.
Now, the contributions to the histograms are calculated using these areas.
The difficult part here was the definition of the limits of each of the integrals in a
way that would not hinder the performance by adding many conditionals.

Discussion on the statistics
----------------------------

Using either of the two pixel splitting algorithms results in some side effects that the user should be aware of:
The fact that pixels contributing to neighbouring bins in the histogram creates some cross-correlation between those bins,
affecting, this way, the statistics of the results in a potentially unwanted manner [Stat]_.


More parallelisation
====================

For faster execution, one solution is to use many-core systems, such as
Graphical Processing Units (GPUs) or
accelerators, like the Xeon-Phi from Intel.
Those chips allocate more silicon for computing (arithmetic logic units - ALUs)
and less to branch prediction, memory pre-fetching and cache coherency, in comparison with CPUs.
Our duties as programmers is to write the code that maximises the usage of ALUs
without relying on pre-fetcher and other commodities offered by normal processors.

Typical GPUs have tens (to hundreds) of compute units able to schedule and run
dozens of threads simultaneously (in a Single Instruction Multiple Data way).
OpenCL allows the execution of the same code on processors, graphics cards or accelerators (see table :ref:`Devices`)
but the memory access pattern is important in order to make the best use of them.
Finally, OpenCL uses just-in-time (JIT) compilation, which looks very much
like Python interpreted code when interfaced with [PyOpenCL]_
(thanks to the compilation speed and the caching of the generated binary).

.. table:: Few OpenCL devices we have tested our code on. :label:`Devices`
    :class: w

    +--------------------+-----------+-----------+---------+---------+-------------+-----------+
    | Vendor / driver    | Intel     | AMD       | AMD     | Nvidia  | Nvidia      | Intel     |
    +--------------------+-----------+-----------+---------+---------+-------------+-----------+
    | Model              | 2xE5-2667 | 2xE5-2667 | V7800   |Tesla K20|GeForce 750Ti| Phi 5110  |
    +--------------------+-----------+-----------+---------+---------+-------------+-----------+
    | Type               | CPU       | CPU       | GPU     | GPU     | GPU         | ACC       |
    +--------------------+-----------+-----------+---------+---------+-------------+-----------+
    | Compute Unit       | 12        | 12        | 18      | 13      | 5           | 4x69      |
    +--------------------+-----------+-----------+---------+---------+-------------+-----------+
    | Compute Element/CU | 4:AVX     | 1         | 80      | 4x8:Warp| 4x8:Warp    | 16:AVX512 |
    +--------------------+-----------+-----------+---------+---------+-------------+-----------+
    | Core frequency     | 2900 MHz  | 2900 MHz  | 700 MHz | 705 MHz | 1100 MHz    | 1052      |
    +--------------------+-----------+-----------+---------+---------+-------------+-----------+
    | Mem. Bandwidth     | 102 GB/s  | 102 GB/s  | 128 GB/s| 208 GB/s| 88 GB/s     | 320 GB/s  |
    +--------------------+-----------+-----------+---------+---------+-------------+-----------+


Parallel algorithms
-------------------

Parallelisation of complete algorithms consists, most of the time, in their decomposition into parallel blocks.
There are a few identified parallel building blocks like:

- Map: apply the same function on all elements of a vector
- Scatter: write multiple outputs from a single input, needs atomic operation support
- Gather: write a single output from multiple inputs
- Reduction: single result from a large vector input, like an inner product
- Scan: apply subsequently an operation to all preceding elements on an vector like np.cumsum
- Sort: There are optimised sorter for parallel implementation.

These parallel building blocks will typically be one individual
kernel or a few, since kernel execution synchronises the global memory in OpenCL.
Parallel algorithmics deal with how to assemble those blocks to implement the required features.

Parallel azimuthal integration
------------------------------

Azimuthal integration, like histogramming, is a scatter operation, and hence requires
the support of atomic operations (in our case with double precision floats).
As Cython does not (yet) support atomic operations, enabling OpenMP parallelisation
results in a module that, while being functional, gives the wrong results (we measured 2%
errors on 8 cores)

To overcome this limitation, instead of looking at where input pixels go to
in the output curve,
we focus on where the output bin comes from in the input image.
This transformation is called a “scatter to gather” transformation and requires atomic operations.
In our case, it was implemented as a single threaded [Cython]_ module.

The correspondence between pixels and output bins can be stored in a look-up table (LUT)
together with the pixel weight (ratio of areas) making the integration look like a simple
(if large and sparse) matrix vector product.
The LUT size depends on whether pixels are split over multiple bins
and in order to exploit the sparse structure, both the index and the weight of each pixel have to be stored.

By making this change we switched from a “linear read / random write” forward algorithm to a
“random read / linear write” backward algorithm which is more suitable for parallelisation.
For optimal memory access patterns, the array of the LUT may be transposed depending on the underlying hardware (CPU vs GPU).

Optimisation of the sparse matrix multiplication
................................................

The compressed sparse row (CSR) sparse matrix format was introduced to
reduce the size of the data stored in the LUT.
This algorithm was implemented both in [Cython]_-[OpenMP]_ and [OpenCL]_.
Our CSR representation contains *data*, *indices* and *indptr* (row index pointer) so it is fully
compatible with the *scipy.sparse.csr.csr_matrix* constructor from [SciPy]_.
This representation is a *struct of array* which is better suited to GPUs
(strided memory access) while LUT is an *array of struct*, known to be
better adapted to CPU (better use of cache and pre-fetching).
The CSR approach presents a double benefit: first, it reduces the
size of the storage needed, as compared to the LUT, by a factor two to three,
and gives the opportunity of working with larger images on the same hardware.
Secondly, the CSR implementation in [OpenCL]_ is using an algorithm based
on multiple parallel reductions
where all threads within a workgroup are collaborating to calculate the
content of a single bin.
This makes it very well suited to run on many-core systems where hundreds
to thousands of simultaneous threads are available.

About numerical precision
.........................

Knowing the tight energy constraints, the future of high performance computing
depends on the capability of programs to use the suitable precision for their calculations.
As our detectors provide a sensitivity of 12 to 20 bits/pixel, performing all calculations
in double precision (with 52 bits mantissa) might seem excessive, the 24 bits mantissa
of single precision float being a better choice for the task (with no precision drop).
Moreover, GPU devices provide much more computing power in single precision than in double.
This factor varies from 2 on high-end professional GPUs like Nvidia Tesla to 24 on most consumer grade devices.

When using [OpenCL]_ for GPUs we used compensated arithmetics (or [Kahan]_ summation), to
reduce the error accumulation in the histogram summation (at the cost of more operations).
This allows numerically accurate results to be obtained even on cheap consumer grade hardware with the use of
single precision floating point arithmetic (32 bits).
Double precision operations are currently limited to high-price / high-performance GPUs, optimised exactly for that purpose.
The additional cost of Kahan summation (4x more arithmetic operations) is hidden by smaller data types,
a higher number of single precision units and the fact that GPUs are usually limited by the memory bandwidth anyway.

The performances of the parallel azimuthal integration can reach 750 MPixel/s
on recent computers with a mid-range graphics card.
On multi-socket servers featuring high-end GPUs like Tesla cards, the performances are equivalent, but with the
added benefit of working with multiple detectors simultaneously.

Benchmarks
==========

We present the results from several benchmark tests done using the different algorithm options available in PyFAI.
All benchmarks were performed using the same bounding box pixel splitting scheme and the resulting integrated profiles are of equivalent quality.
Execution speed has been measured using the *timeit* module, averaged over 10 iterations (best of 3).
The processing is performed on 1, 2, 4, 6, 12 and 16 Mpixel images, with pixel ranges of either 16 or 32 bits (int or uint), taken from actual diffraction experiments, which are part of the pyFAI test suite.

One small note on the benchmarks that follow. The casting for the 12 Mpixel image was done by one thread on the CPU.
That is why the processing time of the 16 Mpixel image appears to be shorter than that of the 12 Mpixel one.


Choice of the algorithm
-----------------------

The LUT contains pairs of an index and a coefficient, hence it is an *array of struct* pattern which is known to make best use of CPU caches.
On the contrary, the CSR sparse matrix representation is a *struct of array* which is better adapted to GPU.
As we can see in figure :ref:`serial-lut-csr`, both LUT and CSR outperform the serial code, and both behave similarly:
the penalty of the *array of struct* in CSR is counter-balanced by the smaller chunk of data to be transferred from central memory to CPU.

.. figure:: serial_lut_csr.png

   Comparison of azimuthal integration speed obtained using serial implementation versus 
   parallel implementations with LUT and CSR sparse matrix representation on two Intel Xeon E2667. :label:`serial-lut-csr`


OpenMP vs OpenCL
----------------

The gain in portability obtained by the use of OpenCL does not mean a sacrifice in performance when the code is run on a CPU,
as we can see in figure :ref:`openmp-opencl-intel-amda`: the OpenCL implementation outperforms the OpenMP one, in all the different CPUs it was tested on.
This could be linked to the better use of SIMD vector units by OpenCL.
The dual Xeon E5520 (a computer from 2009), running at only 2.2 GHz shows pretty good performances compared to more recent computers when using OpenMP:
it was the only one with activated hyper-threading.

.. figure:: openmp_opencl.png

   Comparison of the azimuthal integration speed between the OpenMP and OpenCL implementations. :label:`openmp-opencl-intel-amda`

The choice of the OpenCL driver on CPU affects the performance of PyFAI (figure :ref:`openmp-opencl-intel-amdb`):
on the Intel Xeon E5-1607 (Ivy bridge core), the Intel driver clearly outperforms the AMD driver.
This can be attributed to new SIMD instructions (AVX), supported by the Intel driver but not by the AMD one.
On the older Intel Xeon E-5520 (Nehalem core) which lacks those extensions, the difference in speed is much less.

.. figure:: intel_amd.png

   The effects of OpenCL driver selection on performance on different generations of CPUs. :label:`openmp-opencl-intel-amdb`

GPUs and Xeon Phi
-----------------

Figure :ref:`gpusa` compares the integration speed of the LUT and CSR implementation on two GPUs.
The CSR implementation, thanks to the multiple collaborative parallel reductions, runs much faster on all the devices used, compared to the LUT one.
Another benefit of the CSR implementation when it comes to GPUs is its lower memory usage.
The ATI GPU used in this study features only 1 GB of memory usable by OpenCL, limiting the processable size of the system.
This is the reason the benchmarks stop before reaching the largest image size.
4 Mpixel images are the largest images processable with the LUT implementation, but 12 Mpixel images are processable using the CSR one.

.. figure:: gpusa.png

   Comparison of the azimuthal integration speed between the LUT and CSR implementations on GPUs. :label:`gpusa`


In figure :ref:`gpusb`, we have gathered the results from all of the many-core devices available to us, including several GPUs as well as Intel's Xeon Phi.
As one can see, Xeon Phi (from 2012) matches the performance of the AMD GPU from 2010.
What is surprising though, is how well the consumer grade Nvidia GeForce 750Ti performs in comparison to high-end *Kepler* cards (Titan, Tesla K20) costing only a fraction of their price.


.. figure:: gpusb.png

   Comparison of the performances for several many-core accelerators: GPUs and Xeon Phi. :label:`gpusb`


Kernel timings
--------------

As stated previously, the benchmark tests were performed using the *timeit* module from Python
on the last line of the code snippet described in section :ref:`use`.
One may wonder what is the actual time spent in which part of the OpenCL code and how much is the Python overhead.
This analysis has been done using the profiling tools of OpenCL which measured the execution of every action put in queue.
To be able to perform the azimuthal integration, the image is first transfered to the device (GPU), then casted from integer to float.
All pixel-wise correction (dark current subtraction, flat field normalization, solid-angle and polarization factor correction) are applied in a single pass over each pixel of the image.
Output arrays are initialised to zero, by a separate kernel (memset) before the actual sparse-matrix-dense-vector multiplication.
Finally the three output buffers are retrieved from the device.

Table :ref:`profile` shows the execution time measured on the GeForce Titan (controlled by a pair of Xeon 5520).
The first entry in the table is the total execution time at the Python level, as measured by *timeit*: 2 ms,
while the second is the sum of all of the execution times measured by the OpenCL profiler: 1.4 ms, which highlights how little the Python overhead can be (<40%).
The most time-consuming part of the whole process is by far the memory transfer of the image (H->D meaning Host to Device, 0.8ms).
All vendors are currently working on an unified memory space, which will be available for OpenCL 2.0, which will reduce the time spent in transfers and simplify programming.
Finally the azimuthal integration takes up only 0.4 ms, that is, 20% of the total run time.
If one focuses only on the timing of the integration kernel, then he would wrongly conclude that pyFAI is able to match the speed of the fastest detectors.
For example, the 2 ms of processing time for a 1 Mpixel image of 32 bit integers, correspond to a processing rate of 2 GB/s, while our fastest storage solutions (solid-state drives)
are currently only able to provide half of that.

.. table:: OpenCl profiling of the integration of a Pilatus 1M image (981x1043 pixels of signed 32 bits integers) on a GeForce Titan, running on a dual Xeon 5520. :label:`profile`

         +-----------------+---------+
         |   Python  total | 2.030ms |
         +-----------------+---------+
         |          OpenCL | 1.445ms |
         +-----------------+---------+
         |      H->D image | 0.762ms |
         +-----------------+---------+
         |            cast | 0.108ms |
         +-----------------+---------+
         |          memset | 0.009ms |
         +-----------------+---------+
         |       correction| 0.170ms |
         +-----------------+---------+
         |       integrate | 0.384ms |
         +-----------------+---------+
         |     D->H  ratio | 0.004ms |
         +-----------------+---------+
         |     D->H u_hist | 0.004ms |
         +-----------------+---------+
         |     D->H w_hist | 0.004ms |
         +-----------------+---------+

Configuration and Drivers used
------------------------------

The computer hosting the two Intel Xeon E5-2667 (2x6 cores each, 2.9 GHZ, without hyper-threading, 8x8 GB of RAM) is a Dell PowerEdge R720 with both a Tesla K20 and an Intel Xeon phi accelerator, running Debian 7.
The computer hosting the two Intel Xeon E5520 (2x4cores, 2.27 GHz, hyper-threaded, 6x2 GB of RAM) is a Dell T7500 workstation with two Nvidia GPUs: GeForce 750Ti and Titan, running Debian 7.
The computer hosting the Intel Xeon E5-1607 (1x4cores, 3.0 GHz, without hyper-threading, 2x4 GB of RAM) is a Dell T3610 workstation with two GPUs: Nvidia GeForce 750Ti and AMD FirePro V7800, running Debian 8/Jessie.

In addition to the Debian operating system, specific OpenCL drivers were installed:

* Intel OpenCL drivers V4.4.0-117 + MPSS stack v3.2.3
* AMD APP drivers 14.4
* Nvidia CUDA drivers 340.24-2

Project description
===================

PyFAI is open-source software released under the GPL license available on GitHub (https://github.com/kif/pyFAI).
PyFAI depends on Python v2.6 or v2.7 and [NumPy]_.
In order to be able to read images from various X-ray detectors, pyFAI relies on the [FabIO]_ library.
Optional [OpenCL]_ acceleration is provided by [PyOpenCL]_.
Graphical applications for calibration and integration rely on [matplotlib]_, [PyQt]_ and
SciPy [SciPy]_ for image processing.
A C compiler is needed to build the [Cython]_ code from the related sources.
PyFAI is packaged and available in common Linux distributions like Debian and Ubuntu but it is also tested and functional under Windows and MacOSX.

Conclusions
===========

This contribution shows how one of the most central algorithm in crystallography has been implemented in Python,
optimised in Cython and ported to many-core architectures using PyOpenCL.
A 15x speed-up factor has been obtained by switching from binary code to the OpenCL code running on GPUs (400x vs NumPy).
Some of the best performances were obtained on a mid-range consumer grade Nvidia GeForce 750Ti thanks to the new *Maxwell* generation chip
running as fast as high-end graphics based on the *Kepler* architecture (like the Titan), and literally outperforming
both AMD GPUs and the Xeon-Phi accelerator card.
Programming CPUs in parallel is as easy as programming GPUs via the use of PyOpenCL interfaced with Python.


Acknowledgements
================

Claudio Ferrero (head of the Data Analysis Unit) and Andy Götz (head of the Software Group) are acknowledged for supporting the development of pyFAI.
The porting of pyFAI to OpenCL would have not been possible without the financial support of LinkSCEEM-2 (RI-261600), granting the contracts of
Dimitris Karkoulis who started the GPU porting, Zubair Nawaz who ported image distortion and one of the authors (G. Ashiotis) who is working on CSR, pixel splitting and other algorithms.
Finally, the authors would like to acknowledge their colleagues involved in the development of the library, especially Aurore Deschildre and Frédéric Picca.
The authors would like to thank all X-ray beam-lines promoting pyFAI and providing resources to further develop it: ESRF BM01, ID02, ID11, ID13, ID15, ID16, ID21, ID23, BM26, ID29, BM29 and ID30;
and also in other institutes like Soleil, Petra3, CEA, APS who provide feedback, bug reports and patches to the library.



References
==========
.. [Cython] S. Behnel, R. Bradshaw, C. Citro, L. Dalcin, D.S. Seljebotn and K. Smith.
            *Cython: The Best of Both Worlds*
            Comput. Sci. Eng., 13(2):31-39, 2011.
.. [FabIO]  E. B. Knudsen, H. O. Sorensen, J. P. Wright,  G. Goret and J. Kieffer.
            *FabIO: easy access to two-dimensional X-ray detector images in Python*,
            J. Appl. Cryst., 46:537-539, 2013.
.. [FIT2D]  A. Hammersley, O. Svensson, M. Hanfland, A. Fitch and D. Hausermann.
            *Two-dimensional detector software*,
            High Press. Res., 14:235–248, 1996.
.. [H5Py] A. Collette.
           *Python and HDF5*
           ISBN 978-1-4493-6783-1, (2013)
.. [Kahan] W. Kahan.
            *Pracniques: Further Remarks on Reducing Truncation Errors*,
            Commun. ACM,8(1):40-, Jan. 1965
.. [matplotlib] J. D. Hunter.
            *Matplotlib: A 2D Graphics Environment*,
            Comput. Sci. Eng., 9(3):90-95, 2007.
.. [NumPy] T. E. Oliphant.
         *Python for Scientific Computing*,
         Comput. Sci. Eng., 9(3):10-20, 2007.
.. [OpenCL] J.E. Stone, D. Gohara and G. Shi.
            *OpenCL: A Parallel Programming Standard for Heterogeneous Computing Systems*,
            Comput. Sci. Eng., 12(3):66-73, 2010.
.. [OpenMP] OpenMP Architecture Review Board.
            *OpenMP Application Program Interface Version 3.0*, 2008.
.. [pyFAI]  J. Kieffer and D. Karkoulis.
            *PyFAI, a versatile library for azimuthal regrouping*,
            Journal of Physics: Conference Series, 425:202012, 2013.
.. [pyFAI_ocl] J. Kieffer and J.P. Wright.
               *PyFAI: a Python library for high performance azimuthal integration on GPU*,
               Powder Diffraction, 28S2:1945-7413, 2013.
.. [PyOpenCL] A. Klöckner, N. Pinto, Y. Lee, B. Catanzaro, P. Ivanov and A. Fasih.
            *PyCUDA and PyOpenCL: A Scripting-Based Approach to GPU Run-Time Code Generation*
            Parallel Computing, 38(3):157-174, 2012.
.. [PyQt] Mark Summerfield.
         *Rapid GUI Programming with Python and Qt: The Definitive Guide to PyQt*,
         ISBN 0132354187 (2007).
.. [SciPy] E. Jones, T. E. Oliphant and  P. Peterson,
           *SciPy: Open source scientific tools for Python*, 2001.
.. [SPD] P. Bösecke.
         *Reduction of two-dimensional small- and wide-angle X-ray scattering data*,
         J. Appl. Cryst., 40:s423–s427, 2007.
.. [Stat] X. Yang, P. Juhás and S. J. L. Billinge. 
          *On the estimation of statistical uncertainties on powder diffraction and small-angle scattering data from two-dimensional X-ray detectors*,
          J. Appl. Cryst., 47:1273-1283, 2014.
