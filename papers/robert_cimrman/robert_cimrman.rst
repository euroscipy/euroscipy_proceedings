:author: Robert Cimrman
:email: cimrman3@ntc.zcu.cz
:institution: New Technologies Research Centre, University of West Bohemia,
              Plzeň, Czech Republic

------------------------------------------
Enhancing SfePy with Isogeometric Analysis
------------------------------------------

.. class:: abstract

   We 

.. class:: keywords

   partial differential equations, finite element method, isogeometric
   analysis, SfePy


Introduction
------------

Many problems in physics, biology, chemistry, geology and other scientific
disciplines can be described mathematically using a partial differential
equation (PDE) or a system of several PDEs. The PDEs are formulated in terms of
unknown field variables or fields, defined in some domain with a sufficiently
smooth boundary embedded in physical space.  Because only the most basic PDEs
on simple domains (circle, square, etc.) can be solved analytically, a
numerical solution scheme is needed, involving, typically:

- an approximation of the original domain by a polygonal domain;
- an approximation of continuous fields by discrete fields defined by a finite
  set of degrees of freedom (DOFs) and a (piece-wise) polynomial basis.

The above steps are called *discretization* of the continuous problem. In the
following text two discretization schemes will be briefly outlined:

- the finite element method [FEM]_ - a long-established industry
  approved method based on piece-wise polynomial approximation,
- the isogeometric analysis [IGA]_ - a quite recent generalization of FEM that
  uses NURBS-based approximation.

Then the IGA implementation in the finite element code SfePy will be presented
and illustrated using examples of PDE solutions.

All computations below were done in SfePy.

Outline of FEM and IGA
----------------------

The two discretization methods will be illustrated on a very simple PDE - the
Laplace equation - in a plane (2D) domain. The Laplace equation describes
diffusion and can be used to determine, for example, temperature or electrical
potential distribution in the domain. We will use the "temperature"
terminology and the notation from Table :ref:`notation`.

.. csv-table:: Notation. :label:`notation`
   :widths: 30 75

   symbol, meaning
   :math:`\Omega`, solution domain
   :math:`\Omega_h`, discretized solution domain
   ":math:`\Gamma_D`, :math:`\Gamma_N`", surface subdomains
   :math:`\underline{n}`, unit outward normal
   ":math:`\nabla \equiv [\frac{\partial}{\partial x_1},
   \frac{\partial}{\partial x_2}]^T`", gradient operator
   :math:`\nabla \cdot`, divergence operator
   :math:`\Delta \equiv \nabla \cdot \nabla`, Laplace operator
   :math:`C^1`, space of functions with continuous first derivatives
   :math:`H^1`, space of functions with integrable values and first derivatives
   :math:`H^1_0`, "space of functions from :math:`H^1` that are zero on
   :math:`\Gamma_D`"

The problem is as follows: Find temperature :math:`T` such that:

.. math::
   :label: strong
   :type: eqnarray

   \Delta T &=& 0 \mbox{ in } \Omega \;, \\
          T &=& \bar{T} \mbox{ on } \Gamma_D \;, \\
          \nabla T \cdot \underline{n} &=& 0 \mbox{ on } \Gamma_N \;,

where the second equation is the Dirichlet (or essential) boundary condition
and the third line is the Neumann (or natural) boundary condition and
corresponds to a flux through the boundary.

The operator :math:`\Delta` has second derivatives - that means that the
solution :math:`T` needs to have continuous first derivatives, or, it has to be
from :math:`C^1` function space - this is often not possible in examples from
practice. Instead, a *weak solution* is sought, that satisfies: Find :math:`T
\in H^1(\Omega)`

.. math::
   :label: weak
   :type: eqnarray

    \int_{\Omega} \nabla s \cdot \nabla T
    - \underbrace{\int_{\Gamma_N} s\ \nabla T \cdot \underline{n}}_{\equiv 0}
    &=& 0
    \;, \quad \forall s \in H^1_0(\Omega) \;, \\
    T &=& \bar{T} \quad \mbox{ on } \Gamma_D \;,

where the natural boundary condition appears naturally in the equation (hence
its name). The above system can be derived by multiplying the original equation
by a test function :math:`s \in H^1_0(\Omega)`, integrating over the whole
domain and then integrating by parts.

Both FEM and IGA now replace the infinite function space :math:`H^1(\Omega)` by
a finite subspace with basis with a small support on a discretized domain
:math:`\Omega_h`, see below particular basis choices. Then
:math:`T(\underline{x}) \approx \sum_{k=1}^{N} T_k \phi_k(\underline{x})`,
where :math:`T_k` are the DOFs and :math:`\phi_k` are the base
functions. Similarly, :math:`s(\underline{x}) \approx \sum_{k=1}^{N} s_k
\phi_k(\underline{x})`. Substituting those into (:ref:`weak`) we obtain

.. math::
   :type: eqnarray

   \int_{\Omega_h} \left( \sum_{j=1}^{N} s_j (\nabla \phi_j)^T \cdot
   \sum_{k=1}^{N} \nabla \phi_k T_k \right) = 0 \;.

This has to hold for any :math:`s`, so we can choose :math:`s = \phi_j` for
:math:`j = 1, \dots, N`. It is also possible to switch the sum with the
integral and put the constants :math:`T_k` out of the integral, to obtain the
discrete system:

.. math::
   :label: discrete
   :type: eqnarray

   \sum_{k=1}^{N} \int_{\Omega_h} \left((\nabla \phi_j)^T \cdot
   \nabla \phi_k \right) T_k = 0 \;.

In compact matrix notation we can write :math:`\bm{K} \bm{T} = \bm{0}`, where
the matrix :math:`\bm{K}` has components :math:`K_{ij} = \int_{\Omega_h}
(\nabla \phi_i)^T \cdot \nabla \phi_j` and :math:`\bm{T}` is the vector of
:math:`T_k`. The Dirichlet boundary conditions are satisfied by setting the
:math:`T_k` on the boundary :math:`\Gamma_D` to appropriate values.

Both methods make use of the small support and evaluate (:ref:`discrete`) as a
sum over small "elements" to obtain local matrices or vectors that are then
assembled into a global system - system of linear algebraic equations in our
case.

The particulars of domain geometry description and basis choice will now be
outlined. For both methods, we will use the domain shown in Figure
:ref:`domain`. Its geometry is described by [NURBS]_ (Non-uniform rational
B-spline) curves.

.. figure:: domain.pdf
   :scale: 50%
   :figclass: bht

   The domain with NURBS boundary. :label:`domain`

FEM
```

In this method a continuous solution domain is approximated by a polygonal
domain - *FE mesh* - composed of small basic subdomains with a simple geometric
shape (e.g. triangles or quadrilaterals in 2D, tetrahedrons or hexahedrons in
3D) - the elements. The continuous fields of the PDEs are approximated by
polynomials defined on the individual elements. This approximation is (usually)
continuous over the whole domain, but its derivatives are only piece-wise
continuous.

First we need to make a FE mesh from the NURBS description, usual in
computer-aided design (CAD) systems. While it is easy for our domain, it is a
difficult task in general, especially in 3D space. Here a cheat has been used
and the mesh depicted in Figure :ref:`fe-domain` was generated from the NURBS
description using the IGA techniques described below.

.. figure:: fe-domain.pdf
   :scale: 50%
   :figclass: bht

   The FE-discretized domain covered by quadrilateral
   elements, forming the FE mesh. :label:`fe-domain`

Having the geometry discretized, a suitable approximation of the fields has to
be devised. In (classical [1]_) FEM, the base functions with small support are
polynomials, see Figure :ref:`fem-basis-1d` for an illustration in 1D. A
:math:`k`-th base function is nonzero only in elements that share the DOF
:math:`T_k` and it is a continuous polynomial over each element.

.. [1] See the Wikipedia page for a basic overview of FEM and its many
       variations: http://en.wikipedia.org/wiki/Finite_element_method.

The basis functions are usually defined in a reference element, that are then
mapped to the physical mesh elements by an (affine) transformation. For our
mesh we will use bi-quadratic polynomials over the reference quadrilateral - a
quadratic function along each axis direction.

Several families of the element basis functions exist. In SfePy, Lagrange basis
and Lobatto (hierarchical) basis can be used on quadrilaterals, see Figure
:ref:`fe-bases`.

.. figure:: fe-bases.png
   :scale: 30%
   :figclass: w

   Bi-quadratic basis functions on the reference quadrilateral: left: Langrange
   right: Lobatto. :label:`fe-bases`

IGA
```

In IGA, the CAD geometrical description in terms of NURBS patches is used
directly for the approximation of the unknown fields, without the intermediate
FE mesh - the meshing step is removed, which is one of its principal
advantages. Our domain in Figure :ref:`domain` can be exactly described by a
single NURBS patch. Several auxiliary grids (called "meshes" as well, but do
not mistake with the FE mesh) can be drawn for the patch, see Figure
:ref:`ig-domain-grids`.

.. figure:: ig-domain-grids.pdf
   :scale: 50%
   :figclass: w

   From left to right: parametric mesh (tensor product of knot vectors),
   control mesh, Bézier mesh. :label:`ig-domain-grids`

On a single patch, such as our whole domain, the NURBS basis can be arbitrarily
smooth - this is another compelling feature not easily obtained by FEM.
The basis on the patch is uniquely determined by a *knot vector* for each axis,
and covers the whole patch, see Figure :ref:`iga-base`.

.. figure:: iga-base.png
   :scale: 12%
   :figclass: w

   The order 2 NURBS basis on the single patch domain. :label:`iga-base`

Implementation in SfePy
-----------------------

Our implementation uses a variant of IGA based on Bézier extraction operators
[BE]_ that is suitable for inclusion into existing FE codes. The code itself
does not see the NURBS description at all. The NURBS description can be
prepared, for example, using `igakit` package, a part of [PetIGA]_.

The Bézier extraction is illustrated in Figure :ref:`bezier-extraction`. It is
based on the observation that repeating a knot in the knot vector decreases
continuity of the basis in that knot by one. This can be done in such a way
that the overall shape remains the same, but the "elements" appear naturally as
given by non-zero knot spans. In [BE]_ algorithms are developed that allow
computing *Bézier extraction operator* :math:`C` for each such element such
that the original (smooth) NURBS basis function :math:`R` can be recovered from
the local Bernstein basis :math:`B` using :math:`R = CB`. The Bézier extraction
also allows construction of the Bézier mesh. The code then loops over the
Bézier elements and assembles local contributions in the usual FE sense.

In SfePy, various subdomains can be defined using *regions*, see [SfePy]_. For
this purpose, a *topological Bézier mesh* is constructed, using only the corner
vertices of the Bézier mesh, because those are interpolatory, i.e., they are in
the domain or on its boundary, unlike the other vertices, see Figure
:ref:`bezier-extraction` right.

.. figure:: bezier-extraction.pdf
   :scale: 30%
   :figclass: bht

   From left to right: NURBS basis of degree 2 that describes the second axis
   of the parametric mesh, corresponding Bernstein basis with Bézier elements
   delineated by vertical lines. :label:`bezier-extraction`

Examples
--------

Conclusion
----------

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

.. [FEM] Thomas J. R. Hughes, The Finite Element Method: Linear Static and
         Dynamic Finite Element Analysis, Dover Publications, 2000.

.. [IGA] J. Austin Cottrell, Thomas J.R. Hughes, Yuri Bazilevs. Isogeometric
         Analysis: Toward Integration of CAD and FEA. John Wiley & Sons. 2009.

.. [NURBS] Les Piegl & Wayne Tiller: The NURBS Book, Springer-Verlag 1995–1997
           (2nd ed.).

.. [BE] Michael J. Borden, Michael A. Scott, John A. Evans, and Thomas
        J.R. Hughes: Isogeometric Finite Element Data Structures based on
        Bezier Extraction of NURBS, Int. J. Numer. Meth. Engng., 87:
        15–47. doi: 10.1002/nme.2968, 2011.

.. [PetIGA] N. Collier, L. Dalcin, V.M. Calo: PetIGA: High-Performance
            Isogeometric Analysis, arxiv 1305.4452, 2013,
            http://arxiv.org/abs/1305.4452.

.. [SfePy] Robert Cimrman: SfePy - Write Your Own FE Application,
           arxiv 1404.6391, 2014,
           http://arxiv.org/abs/1404.6391.
