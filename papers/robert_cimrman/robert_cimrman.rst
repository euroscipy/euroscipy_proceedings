:author: Robert Cimrman
:email: cimrman3@ntc.zcu.cz
:institution: New Technologies Research Centre, University of West Bohemia,
              Plzeň, Czech Republic

------------------------------------------
Enhancing SfePy with Isogeometric Analysis
------------------------------------------

.. class:: abstract

   SfePy (Simple Finite Elements in Python, http://sfepy.org) is a framework
   for solving various kinds of problems (mechanics, physics, biology, ...)
   described by partial differential equations in two or three space
   dimensions. It is based on a nowadays standard and well-established
   numerical solution technique, the finite element method. In the paper its
   enhancement with another, much more recent, numerical method, the
   isogeometric analysis, is presented. First the two methods are outlined,
   then the implementation is discussed and finally numerical examples are
   shown.

.. class:: keywords

   partial differential equations, finite element method, isogeometric
   analysis, SfePy


Introduction
------------

Many problems in physics, biology, chemistry, geology and other scientific
disciplines can be described mathematically using a partial differential
equation (PDE) or a system of several PDEs. The PDEs are formulated in terms of
unknown field variables or fields, defined in some domain with a sufficiently
smooth boundary embedded in physical space. Because only the most basic PDEs
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

Then the IGA implementation in the finite element code SfePy (http://sfepy.org)
will be presented and illustrated using examples of PDE solutions.

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
   :scale: 40%
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
   :scale: 40%
   :figclass: bht

   The FE-discretized domain covered by quadrilateral
   elements, forming the FE mesh. :label:`fe-domain`

Having the geometry discretized, a suitable approximation of the fields has to
be devised. In (classical [1]_) FEM, the base functions with small support are
polynomials, see Figure :ref:`fe-basis-1d` for an illustration in 1D. A
:math:`k`-th base function is nonzero only in elements that share the DOF
:math:`T_k` and it is a continuous polynomial over each element.

.. figure:: fe-basis-1d.pdf
   :scale: 30%
   :figclass: bht

   The 1D FE basis on three line elements with black thick line an interpolated
   function resulting from the same DOF vector for each row: top: linear,
   bottom: quadratic, left: Lagrange, right: Lobatto. Each basis function has a
   single color. :label:`fe-basis-1d`

The thick black lines in Figure :ref:`fe-basis-1d` result from interpolation of
the DOF vector generated by :math:`\sin(\frac{\pi}{2} \frac{x}{3})` evaluated
in points of maximum of each basis function. The left column of the figure
shows the Lagrange polynomial basis, which is interpolatory, i.e., a DOF value
is equal to the approximated function value in the point, called *node*, where
the basis is equal to 1. The right column of the figure shows the Lobatto
polynomial basis, that is not interpolatory for DOFs belonging to basis
functions with order greater than 1 - that is why the bottom right interpolated
function differs from the other cases. This complicates several things
(e.g. setting of Dirichlet boundary conditions - a projection is needed), but
the hierarchical nature of the basis, i.e. increasing approximation order means
adding new basis functions without modifying the existing ones, has also
advantages, for example better condition number of the matrix for higher order
approximations.

.. [1] See the Wikipedia page for a basic overview of FEM and its many
       variations: http://en.wikipedia.org/wiki/Finite_element_method.

The basis functions are usually defined in a reference element, that are then
mapped to the physical mesh elements by an (affine) transformation. For our
mesh we will use bi-quadratic polynomials over the reference quadrilateral - a
quadratic function along each axis direction, such as those in the bottom row
of Figure :ref:`fe-basis-1d`.

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
and covers the whole patch, see Figure :ref:`ig-base`.

.. figure:: ig-base.png
   :scale: 12%
   :figclass: w

   The order 2 NURBS basis on the single patch domain. :label:`ig-base`

IGA Implementation in SfePy
---------------------------

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

.. figure:: bezier-extraction.pdf
   :scale: 30%
   :figclass: bht

   From left to right: NURBS basis of degree 2 that describes the second axis
   of the parametric mesh, corresponding Bernstein basis with Bézier elements
   delineated by vertical lines. :label:`bezier-extraction`

In SfePy, various subdomains can be defined using *regions*, see [SfePy]_. For
this purpose, a *topological Bézier mesh* is constructed, using only the corner
vertices of the Bézier mesh, because those are interpolatory, i.e., they are in
the domain or on its boundary, unlike the other vertices, see Figure
:ref:`bezier-extraction` right.

Notes on Code Organization
``````````````````````````

Although the Bézier extraction technique shields the IGA-specific code from the
rest of the FEM package, the implementation was not trivial. Similar to the
Lobatto FE basis, the DOFs corresponding to the NURBS basis are not equal to
function values with the exception of the patch corners. Moreover, the IGA
fields do not work with meshes at all - they need the NURBS description of the
domain together with the Bézier extraction operators and the topological Bézier
mesh. So the original `sfepy.fem` sub-package was renamed and split into:

- `sfepy.discrete` for the general classes independent of the particular
  discretization technique (for example variables, equations, boundary
  conditions, materials, quadratures, etc.);
- `sfepy.discrete.fem` for the FEM-specific code;
- `sfepy.discrete.iga` for the IGA-specific code;
- `sfepy.discrete.common` for common functionality shared by some classes in
  `sfepy.discrete.fem` and `sfepy.discrete.iga`.

In this way, circular import dependencies were minimized.

Using IGA
`````````

As described in [SfePy]_, problems can be described either using problem
description files - Python modules containing definitions of the various
components (mesh, regions, fields, equations, ...)  using basic data types such
as ``dict`` and ``tuple``, or using the `sfepy` package classes directly
interactively or in a script. The former way is more basic and will be used in
the following.

In a FEM computation, a mesh has to be defined using:

.. code-block:: python

    filename_mesh = 'fe_domain.mesh'

In an IGA computation, a NURBS domain has to be defined instead:

.. code-block:: python

    filename_domain = 'ig_domain.iga'

where the `'.iga'` suffix is used for a custom HDF5 file that can be prepared
by functions in `sfepy.discrete.iga`.

A scalar real FE field with the approximation order 2 called 'temperature' can
be defined by:

.. code-block:: python

    # Lagrange basis is the default.
    fields = {
        'temperature' :
        ('real', 1, 'Omega', 2),
    }

    # Lobatto basis.
    fields = {
        'temperature' :
        ('real', 1, 'Omega', 2, 'H1', 'lobatto'),
    }

An analogical IGA field can be defined by:

.. code-block:: python

    fields = {
        'temperature' :
        ('real', 1, 'Omega', None, 'H1', 'iga'),
    }

Here the approximation order is `None`, as it is given by the `'.iga'` domain
file.

The above are the only changes required to use IGA - everything else remains
the same as in FEM calculations. The scalar and vector volume terms (weak
forms, linear or nonlinear) listed at
http://sfepy.org/doc-devel/terms_overview.html can be used without
modification.

Limitations
```````````

There are currently several limitations that will be addressed in future:

- general Dirichlet boundary conditions;

  - currently only constants on whole sides of the parametric mesh;

- projections of functions into the NURBS basis;
- support for surface integrals;
- linearization of results for post-processing;

  - currently the fields on a tensor-product patch are sampled by fixed
    parameter vectors and a corresponding FE-mesh is generated;

- all variables have to have the same approximation order, as the basis is
  given by the domain file;

- the domain is a single NURBS patch only.

Examples
--------

Numerical examples illustrating the IGA calculations are presented below.

Temperature Distribution
````````````````````````

.. figure:: laplace.png
   :scale: 30%
   :figclass: bht

   A solution of the 2D Laplace equation. :label:`laplace`

.. figure:: laplace-vf.png
   :scale: 30%
   :figclass: bht

   A solution of the 2D Laplace equation with volume source in a
   subdomain. :label:`laplace-vf`

Elastic Deformation
```````````````````

.. figure:: elasticity.png
   :scale: 30%
   :figclass: bht

   A solution of the 3D linear elasticity equation. The undeformed domain is
   shown as a wireframe, 10x magnified deformation. :label:`elasticity`

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
