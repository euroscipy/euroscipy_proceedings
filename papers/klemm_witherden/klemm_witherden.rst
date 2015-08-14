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

PyFR is an open-source Python framework for solving advection-diffusion problems of the form

.. math::

  \frac{\partial u}{\partial t} + \nabla \cdot \mathbf{f}(u, \nabla u) = S( \mathbf{x}, t),

where :math:`u(\mathbf{x},t)` is a state vector representing the solution, :math:`\mathbf{f}` a flux function, and :math:`S` a source term.
A prominent example of an advection-diffusion type problem are the compressible Navier-Stokes equations of fluid dynamics.
The efficient solution of which, especially in their unsteady form, is of great interest to both industry and academic.

The pyMIC Module
----------------

The Python Offload module for the Intel(R) Many Core Architecture, follows Python's philosophy by providing an easy-to-use, but widely applicable interface to control offloading to the coprocessor.


Using pyMIC to Offload PyFR
---------------------------


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
For more information go to \url{http://www.intel.com/performance}.

Intel's compilers may or may not optimize to the same degree for non-Intel microprocessors for optimizations that are not unique to Intel microprocessors.
These optimizations include SSE2, SSE3, and SSSE3 instruction sets and other optimizations.
Intel does not guarantee the availability, functionality, or effectiveness of any optimization on microprocessors not manufactured by Intel. Microprocessor-dependent optimizations in this product are intended for use with Intel microprocessors.
Certain optimizations not specific to Intel microarchitecture are reserved for Intel microprocessors.
Please refer to the applicable product User and Reference Guides for more information regarding the specific instruction sets covered by this notice.



References
----------
.. [Atr03] P. Atreides. *How to catch a sandworm*,
           Transactions on Terraforming, 21(3):261-300, August 2003.


