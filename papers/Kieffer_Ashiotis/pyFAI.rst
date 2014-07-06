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

   The pyFAI package has been designed to transform X-ray diffraction images
   into powder diffraction curves to be further processed by scientists
   (Rietveld refinement, ...)
   This contribution describes how to transform an image into a radial profile
   using the Numpy package, how the process was accelerated using Cython and
   how the algorithm was parallelize, needing a complete re-design to take benefit
   of massively parallel devices like graphical processing units or accelerator like
   the Intel Xeon Phi thanks to PyOpenCL.


.. class:: keywords

   X-rays, powder diffraction, HPC, parallel algorithms, OpenCL

Introduction
============
The Python programming language is widely addopted in the scientific community
and especially in crystallography, this is why a conviniant azimuthal integration
routine, one of the basic algorithm, was requested by the synchroton community.
The avent of pixel-detectors with their very high speed (about 1000 frames per seconds)
imposed strong contrains in speed that most available programs (FIT2D, SPD),
while written in Fortran or C could not meet.

The pyFAI project started in 2011 and aims at providing a convieniant python interface
for azimuthal integration, so that any crystallographer can adapt it to the type of experiment
he is interested in.
This contribution describes how one of the most fundamental
algorithm used in crystallography has been implemented in Python
and how it was accelerated to reach the performances of today's fastest detectors.

Description of the experiment
=============================

An X-ray is an electromagnetic wave, like light except that its wavelength is much smaller, of
the size of an atom, making it a perfect probe to analyse atoms and molecules.
This X-ray is scattered (re-emmited with the same energy) by the electron cloud surrounding atoms.
When atoms are arranged periodically (in a crystal), they behave like a gratting for X-ray and reflect light with given angles.
An X-ray beam crossing a powder sample made of many small crystals is then scattered along multiple concentric cones.
In a powder diffraction experiment, one aims a measuring the intensity of X-rays as function of opening of the cone, average along each ring.
This transformation is called "azimuthal integration" as it is an averaging of the signal along the azimuthal angle.

Figure Debye-Scherrer

Azimuthal integration
=====================

Naive implementation
--------------------

Numpy implementation
--------------------

Cython implementation
---------------------

Pixel splitting
---------------

About paralleliztion
====================

Parallel algorithms
-------------------

Parallelization of algorithms require their decompostion into parallel blocks like:
 * Map: apply the same function on all element of a vector
 * Scatter: write multiple output from a single input (atomic suport)
 * Gather: write a single output from multiple inputs
 * Reduction: like a scalar product
 * Scan: like numpy.cumsum
 * Sort



The azimuthal integration, when based on histograms, is a scatter operation.
As Cython does not (yet) support atomic operation, using the OpenMP support of
Cython will result in functional code providing wrong results (we measured 2%
errors on 8 cores)

To overcome this limitation; instead of looking at where input pixels go to
in the output curve,
we instead look at where the output bin COME FROM in the input image.
This transformation is called a “scatter to gather” transformation in parallel
programming and needs atomic operation (or a single cython thread in our case)

The correspondence between pixels and output bins can be stored in a look-up table (LUT)
together with the pixel weight which make the integration look like a simple
(if large and sparse) matrix vector product.
This look-up table size depends on whether pixels are split over multiple bins
and to exploit the sparse structure, both index and weight of the pixel have to be stored.

By making this change we switched from a “linear read / random write” forward algorithm to a
“random read / linear write” backward algorithm which is more suitable for parallelization.

Optimization of the sparse mtrix multiplication
-----------------------------------------------

The compressed sparse row (CSR) sparse matrix format was introduced to reduce the size of the dat stored in the LUT.
This algorithm was implemented both in [Cython]-OpenMP and OpenCL.
The CSR approach has a double benefit: first, it reduces the size of the storage needed compared to the LUT by a factor two to three,
offering the opportunity of working with larger images on the same hardware.
Secondly, the CSR implementation in OpenCL is using an algorithm based on multiple parallel reductions
where many execution threads are collaborating to calculate the content of a single bin.
This makes it very well suited to run on GPUs and accelerators where hundreds to thousands of simultaneous threads are available.

About precision of calculation
------------------------------

Knowing the tight energy constrains in computing, the future of high performance computing
depends on the capability of programs to use the right precision for their calculation.
As out detectors provide a sensitivity of 12 to 20 bits/pixel, performing all calculation
in double precision (with 52 bits mantissa) looks oversized  and the 24 bits of mantissa
of single precision float looks better adapted (with no drop of precision).
Moreover, GPU devices provide much more computing power in single precision than in double,
this factor varies from 2 on high-end professionnal GPU like Nvida Tesla to 24 on most consumer grade devices.

When using OpenCL for the GPU we used a compensated (or Kahan_summation), to reduce the error accumulation in the histogram summation (at the cost of more operations to be done). This allows accurate results to be obtained on cheap hardware that performs calculations in single precision floating-point arithmetic (32 bits) which are available on consumer grade graphic cards. Double precision operations are currently limited to high price and performance computing dedicated GPUs. The additional cost of Kahan summation, 4x more arithmetic operations, is hidden by smaller data types, the higher number of single precision units and that the GPU is usually limited by the memory bandwidth anyway.

The performances of the parallel implementation based on a LUT, stored in CSR format, can reach 750 MPix/s on recent multi-core computer with a mid-range graphics card. On multi-socket server featuring high-end GPUs like Tesla cards, the performances are similar with the additional capability to work on multiple detector simultaneously.


Of course, no paper would be complete without some source code.  Without
highlighting, it would look like this::

   def sum(a, b):
       """Sum two numbers."""

       return a + b

With code-highlighting:

.. code-block:: python

   def sum(a, b):
       """Sum two numbers."""

       return a + b

Maybe also in another language, and with line numbers:

.. code-block:: c
   :linenos:

   int main() {
       for (int i = 0; i < 10; i++) {
           /* do something */
       }
       return 0;
   }

Or a snippet from the above code, starting at the correct line number:

.. code-block:: c
   :linenos:
   :linenostart: 2

   for (int i = 0; i < 10; i++) {
       /* do something */
   }

Important Part
--------------

It is well known [Atr03]_ that Spice grows on the planet Dune.  Test
some maths, for example :math:`e^{\pi i} + 3 \delta`.  Or maybe an
equation on a separate line:

.. math::

   g(x) = \int_0^\infty f(x) dx

or on multiple, aligned lines:

.. math::
   :type: eqnarray

   g(x) &=& \int_0^\infty f(x) dx \\
        &=& \ldots


The area of a circle and volume of a sphere are given as

.. math::
   :label: circarea

   A(r) = \pi r^2.

.. math::
   :label: spherevol

   V(r) = \frac{4}{3} \pi r^3

We can then refer back to Equation (:ref:`circarea`) or
(:ref:`spherevol`) later.

Mauris purus enim, volutpat non dapibus et, gravida sit amet sapien. In at
consectetur lacus. Praesent orci nulla, blandit eu egestas nec, facilisis vel
lacus. Fusce non ante vitae justo faucibus facilisis. Nam venenatis lacinia
turpis. Donec eu ultrices mauris. Ut pulvinar viverra rhoncus. Vivamus
adipiscing faucibus ligula, in porta orci vehicula in. Suspendisse quis augue
arcu, sit amet accumsan diam. Vestibulum lacinia luctus dui. Aliquam odio arcu,
faucibus non laoreet ac, condimentum eu quam. Quisque et nunc non diam
consequat iaculis ut quis leo. Integer suscipit accumsan ligula. Sed nec eros a
orci aliquam dictum sed ac felis. Suspendisse sit amet dui ut ligula iaculis
sollicitudin vel id velit. Pellentesque hendrerit sapien ac ante facilisis
lacinia. Nunc sit amet sem sem. In tellus metus, elementum vitae tincidunt ac,
volutpat sit amet mauris. Maecenas diam turpis, placerat at adipiscing ac,
pulvinar id metus.

.. figure:: benchmark.png

   This is the caption. :label:`egfig`

.. figure:: benchmark.png
   :align: center
   :figclass: w

   This is a wide figure, specified by adding "w" to the figclass.  It is also
   center aligned, by setting the align keyword (can be left, right or center).

.. figure:: benchmark.png
   :scale: 20%
   :figclass: bht

   This is the caption on a smaller figure that will be placed by default at the
   bottom of the page, and failing that it will be placed inline or at the top.
   Note that for now, scale is relative to a completely arbitrary original
   reference size which might be the original size of your image - you probably
   have to play with it. :label:`egfig2`

As you can see in Figures :ref:`egfig` and :ref:`egfig2`, this is how you reference auto-numbered
figures.

.. table:: This is the caption for the materials table. :label:`mtable`

   +------------+----------------+
   | Material   | Units          |
   +------------+----------------+
   | Stone      | 3              |
   +------------+----------------+
   | Water      | 12             |
   +------------+----------------+
   | Cement     | :math:`\alpha` |
   +------------+----------------+


We show the different quantities of materials required in Table
:ref:`mtable`.


.. The statement below shows how to adjust the width of a table.

.. raw:: latex

   \setlength{\tablewidth}{0.8\linewidth}


.. table:: This is the caption for the wide table.
   :class: w

   +--------+----+------+------+------+------+--------+
   | This   | is |  a   | very | very | wide | table  |
   +--------+----+------+------+------+------+--------+


Perhaps we want to end off with a quote by Lao Tse:

  *Muddy water, let stand, becomes clear.*


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
.. [Atr03] P. Atreides. *How to catch a sandworm*,
           Transactions on Terraforming, 21(3):261-300, August 2003.


