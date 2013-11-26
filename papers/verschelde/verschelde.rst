:author: Jan Verschelde
:email: jan@math.uic.edu
:institution: University of Illinois at Chicago

---------------------------------
modernizing PHCpack through phcpy
---------------------------------

.. class:: abstract

   PHCpack is a large software package for solving systems of polynomial
   equations. The executable phc is menu driven and file oriented. This
   paper describes the development of phcpy, a Python interface to PHCpack.
   Instead of navigating through menus, users of phcpy solve systems in the
   Python shell or via scripts. Persistent objects replace intermediate
   files.

Introduction
------------

Our mathematical problem is to solve a system of polynomial equations in
several variables. The discrete part of the output data consists of the
number of solutions and degrees of positive dimensional solution sets.
When the input is exact or if the coefficients of the polynomial can be
given with any accuracy, the isolated solutions can be then approximated
up to any accuracy and for each positive dimensional solution component,
as many generic points as its degree can be computed.

Version 1.0 of PHCpack was archived in [Ver99]_. PHCpack incorporates two
external software packages: MixedVol [GLW05]_ and QDlib [HLB01]_.
Although the original focus was to approximate all isolated 
complex solutions, PHCpack
prototyped many of the early algorithms in numerical algebraic
geometry [SVW03]_, [SVW05]_. Recent updates are listed in [Ver10]_.

The Python interface to PHCpack got a first start when Kathy Piret met
William Stein at the software for algebraic geometry workshop at the
Institute for Mathematics and its Applications in Minneapolis in the
Fall of 2006. The first version of this interface is described in [Pir08]_.
Sage [S+13]_  offers the interface phc.py,
developed by William Stein, Marshall Hampton and Alex Jokela.
Version 0.0.1 of phcpy originated at lecture 40 of the author
in the graduate course MCS 507 in the Fall of 2012, 
as an illustration of Sphinx [Bra]_.
Version 0.1.0 was prepared for presentation at EuroSciPy 2013 (August 2013).
The current version of phcpy is 0.1.4.

We first outline in the next section the application of numerical
homotopy continuation methods to compute all isolated solutions and all
positive dimensional irreducible solution sets of a polynomial system.
Then we describe how phcpy relates to other interfaces to PHCpack. The
functionality of phcpy is then summarized briefly as the online Sphinx
documentation is more extensive and still growing. The Python interface
to PHCpack builds directly on the C interface to the Ada code.

Related software packages that apply homotopy continuation methods to
solve polynomial systems are (in alphabetical order):
Bertini [BHSW]_, [BHSW08]_,
HOMPACK90 [WSM+97]_ (the successor of HOMPACK [WBM87]_),
HOM4PS [GLL02]_, HOM4PS-2.0 [LLT08]_, NAG4M2 [Ley11]_,
PHoM [GKK+04]_, and pss3.0.5 [Mal]_.
As polynomial homotopy continuation methods
involve many algorithms from various fields of computing, every software
has its unique strengths and the statement “*no one package provides all
such capabilities*” quoted from [BHSW08]_ remains true today.

Polynomial Homotopy Continuation
--------------------------------

Our mathematical problem is to solve a polynomial
system \ :math:`f({\bf x}) = {\bf 0}` in several
variables \ :math:`{\bf x}= (x_1,x_2,\ldots,x_n)`. A homotopy connects
:math:`f({\bf x}) = {\bf 0}` to a system :math:`g({\bf x}) = {\bf 0}`
with known solutions:

.. math::

   h({\bf x},t) = \gamma (1-t) g({\bf x}) + t f({\bf x}) = {\bf 0},
   \quad \gamma \in {\mathbb C}.


For almost all values for :math:`\gamma`, the solutions of
:math:`h({\bf x},t) = {\bf 0}` are regular for all :math:`t \in [0,1)`.
Numerical continuation methods track solution paths defined
by \ :math:`h({\bf x},t) = {\bf 0}`.

For systems with natural parameters :math:`\lambda`, we
solve :math:`f({\mbox{\boldmath $\lambda$}},{\bf x}) = {\bf 0}` first
for generic values of the parameters
:math:`{\mbox{\boldmath $\lambda$}}= {\mbox{\boldmath $\lambda$}}_0` and
then use

.. math::

   h({\bf x},t) = (1-t) f({\mbox{\boldmath $\lambda$}}_0,{\bf x})
   + t f({\mbox{\boldmath $\lambda$}}_1,{\bf x}) = {\bf 0},

to solve a specific instance
:math:`f({\mbox{\boldmath $\lambda$}}_1,{\bf x}) = {\bf 0}`.
A variation to the homotopy above is the
natural parameter homotopy 

.. math::

   h({\bf x},t) = f((1-t) {\mbox{\boldmath $\lambda$}}_0
   + t {\mbox{\boldmath $\lambda$}}_1,{\bf x}) = {\bf 0},

where the path of systems in the homotopy runs entirely through
the space where the parameters live.

The schematic in Figure :ref:`figcomplexparcon` illustrates that singular
solutions along the paths are avoided by a generic choice of the
parameters \ :math:`{\mbox{\boldmath $\lambda$}}_0` at \ :math:`t=0`.

.. figure:: figcomplexparcon.eps

   A generic choice for start parameters avoids singularities
   along the paths.  :label:`figcomplexparcon`

Solving a system that has solution sets of positive dimension, e.g.: a
curve or surface, means to compute its dimension and its degree. For a
solution set of dimension \ :math:`d`, we add to the system :math:`d`
linear equations with random coefficients to reduce the problem to
computing isolated solutions. Because the coefficients of the linear
equation are random, the solutions of the system that satisfy the random
linear equations will be isolated. If the solution set has multiplicity
one, the solutions of the augmented system will be isolated points of
multiplicity one. Moreover, the number of isolated solutions of the
augmented system that lie on the :math:`d`-dimensional solution set of
the original system will be equal to the degree of the
:math:`d`-dimensional solution set. Thus a positive dimensional solution
set of dimension :math:`d` is represented by a set of :math:`d` random
linear equations and as many points in the intersection of the original
system with those random linear equations as the degree of the
:math:`d`-dimensional solution set. In numerical algebraic geometry,
this representation is called a witness set.

For sparse polynomial systems with very few monomials appearing with
nonzero coefficient (in an extreme case, we consider binomial systems
that have exactly two monomials with nonzero coefficient in each
equation), we can represent positive dimensional solution sets by
monomial maps. For example, the two equations :math:`x^2 y - zx = 0`,
:math:`x^2 z - y^2 x = 0` have as solutions three monomial maps:
:math:`(x = 0, y = \lambda_1, z = \lambda_2)`,
:math:`(x = \lambda_1, y = \lambda_1^2, z = \lambda_1^3)`, and
:math:`(x = \lambda_1, y = 0, z = 0)`, for parameters :math:`\lambda_1`
and :math:`\lambda_2`. These monomial maps form the leading terms of
Puiseux series developments for general algebraic sets.

Surveys on homotopy continuation are [AG93]_, [AG97]_, [Li03]_,
and [Wat86]_, [Wat89]_, [Wat02]_.
Book treatments are in [AG03]_, [Mor87]_, and [SW05]_.

Interfaces to PHCpack and phc
-----------------------------

This paper is mainly concerned with software problems.
There are at least three motivations to develop phcpy:

#. PHCpack is a large Ada package, its executable phc
   operates via menus, with input and output to files.
   With phcpy we provide an interpreter interface to phc.

#. The code in PHCpack lacks adequate *user* documentation
   so that many of its features are not obviously accessible to users.
   The Python modules of phcpy refactor the functionality of PHCpack
   and beautiful documentation is generated by Sphinx [Bra]_.

#. As many new algorithms were first implemented with PHCpack,
   reproducibility [SBB13]_ of published computational results
   can be automated via regression tests with Python scripts.

Because also other interfaces to PHCpack may accomplish the same goals
outlined above, we first give an overview of the interfaces to PHCpack.

The first interface to PHCpack was based on the OpenXM [MNO+11]_ protocol
for the interaction of software components. 
The virtue of this protocol is that only an executable version of the 
software is required and one does not need to compile the code.

The interfaces to PHCpack from Maple [LV04]_, MATLAB & Octave [GV08b]_, 
and Macaulay2 [GPV13]_
only require the executable phc. This type of interface works in three
stages: (1) prepare an input file for phc; (2) call phc with some
options, the input file, and the name of an output file; (3) parse the
output file to extract the results. In principle, everything that can be
done via the command-line menus of phc can thus also be performed via
Maple procedures, MATLAB, Octave, or Macaulay2 scripts.

Figure :ref:`fighoney` shows the interfaces to PHCpack.

.. figure:: fighoney.eps

   Diagram of the interfaces to PHCpack and phc.
   The interfaces PHCpack.m2, PHCmaple, PHClab, depicted to the right of the 
   antidiagonal line require only the executable version phc.
   The other interfaces PHClib, PHCmpi, and phcpy are based on the source
   code of PHCpack.  :label:`fighoney`

The C interface to PHCpack, described in [LV06]_, offers the C programmer
access to the path trackers of PHCpack. This interface was developed for
use with the Message Passing Interface [SOH+98]_ and serves also as the basis
for phcpy.  In the C interface, the data structures for polynomials and
solutions are not duplicated.  Instead of data structure duplication, one
can enter into the C interface routine a polynomial term after term. 
The interface then behaves like a state machine.

Why would phcpy be any better than the other interfaces? Leaving aside
the growing popularity of Python for scientific computing, the
replacement of files by persistent objects enabled the implementation of
a generator for the path trackers. After initialization of the homotopy
(with target, start system, and one start solution), the user can call a
“next” function to compute the next point at the solution path that
originates at the start solution given at initialization. This “next”
function (available for standard double, double double, and quad double
precision) allows a detailed investigation of the properties of a
particular solution path. In addition, it gives the user a fine control
over the order of execution. If desired, the tolerances and the step
size can be adjusted as needed in an application that plots solution
trajectories.

Another (future) application of phcpy is a web interface, such as at
https://kepler.math.uic.edu (beta version) presented by Xiangcheng Yu at
the SIAM AG 2013 conference in the first week of August 2013.

Using phcpy
-----------

The blackbox solver of PHCpack is its most widely used function. In
phcpy, this blackbox solver is available in the function solve of the
module solver. The solver takes on input a list of strings that contain
valid representations of polynomials. On return is a list of strings,
which contain the solutions of the system.

.. code-block:: python

   >>> from phcpy.solver import solve
   >>> from phcpy.phcpy2c import py2c_set_seed
   >>> f = ["x**2*y**2 + x + y;","x*y + x + y + 1;"]
   >>> py2c_set_seed(21320)
   0
   >>> s = solve(f,silent=True)
   >>> len(s)
   4
   >>> print s[0]
   t : 1.00000000000000E+00 0.00000000000000E+00
   m : 1
   the solution for t :
   x : -1.00000000000000E+00 0.00000000000000E+00
   y : -1.61803398874989E+00 0.00000000000000E+00
   == err : 2.143E-101 = rco : 4.775E-02 = res : 2.220E-16 =

With py2c_set_seed() we fix the seed of the random number generator
for the coefficients of the start system in the homotopy, which makes
for predictable runs.  Otherwise, the solve() each time generates
different coefficients in the homotopies and the order of the solutions
on return may differ.
For each solution, the triplet (err,rco,res) indicates the quality of
the solution:

-  err: the norm of the last update made by Newton’s method (forward
   error),

-  rco: estimate for the inverse condition number of the Jacobian
   matrix,

-  res: norm of the evaluated solution (backward error).

With double double and quad double arithmetic we get more accurate
solutions.

To predict the number of isolated solutions with the mixed volume:

.. code-block:: python

   >>> from phcpy.solver import mixed_volume
   >>> mixed_volume(f)
   4

Version 0.1.4 of phcpy contains the following modules:

-  solver: a blackbox solver, mixed-volume calculator, linear-product
   root count and start system, path trackers, deflation for isolated
   singular solutions.

-  examples: a selection of interesting benchmark systems.
   Typing python examples.py at the command prompt calls the
   blackbox solver on all benchmark examples, thus providing
   an automatic regression test.

-  families: some problems can be formulated for any number of
   variables.

-  phcmaps: monomial maps as solutions of binomial systems.

-  phcsols: conversion of PHCpack solution strings into Python
   dictionaries.

-  phcsets: basic tools to manipulate positive dimensional solution
   sets.

-  phcwulf: basic client/server setup to solve many systems.

-  schubert: the Pieri homotopies solve particular polynomial systems
   arising in enumerative geometry.

The number of exported functions, documented by Sphinx [Bra]_ runs in the
several hundreds. The code of version 0.1.1 of phcpy was improved with
the aid of Pylint [The]_, yielding a global rating of 9.73/10.

The Design of phcpy
-------------------

The design of phcpy is drawn in Figure :ref:`figphcpy`. This design can be
viewed as an application of a façade pattern (see Figure B.31 in [Bai08]_). 
The façade pattern plays
a strong role in converting legacy systems incrementally to more modern
software and is appropriate as phcpy should be viewed as a modernization
of PHCpack. The implementation of use\_c2phc.adb applies the chain of
responsibility pattern (see Figure B.12 in [Bai08]_),
calling handlers to specific packages in
PHCpack. That we use the name phcpy and not PyPHC indicates that phcpy
is more than just an interface.

.. figure:: figdesign.eps

   The design of phcpy depends on PHClib, a library of various 
   collections of C functions, through one file phcpy2c.c
   (with documentation in the corresponding header phcpy2c.h) 
   which encodes the Python bindings.  
   PHClib interfaces to the Ada routines of PHCpack
   through one Ada procedure use\_c2phc.adb.
   The collection of parallel programs (MPI2phc)
   using message passing (MPI) depends on PHClib.  :label:`figphcpy`

The code for phcpy builds directly on the C interface to PHCpack.
The C interface was developed to use the Message Passing Interface 
(MPI) [SOH+98]_. 
In joint work with Yusong Wang [VW02]_, [VW04a]_, [VW04b]_, 
Yan Zhuang [VZ06]_, Yun Guan [GV08a]_,
and Anton Leykin [LV05]_, [LV09]_, [LVZ06]_, 
the main program was always a C program. 
The C interface described in [LV06]_
is centered around one gateway function use\_c2phc.
To the Ada programmer, this function has the specification

.. code-block:: ada

        function use_c2phc ( job : integer;
                             a : C_intarrs.Pointer;
                             b : C_intarrs.Pointer;
                             c : C_dblarrs.Pointer ) 
                           return integer;

The prototype of the corresponding C function is

.. code-block:: c

        extern int _ada_use_c2phc ( int task,
                                    int *a,
                                    int *b,
                                    double *c );

With use\_c2phc we obtain one uniform streamlined design of the
interface: the C programmer calls one single Ada function
\_ada\_use\_c2phc. What use\_c2phc executes depends on the job number.
The (a,b,c) parameters are flexible enough to pass strings
and still provide some form of type checking (which would not
be possible had we wiped out all types with void*).

To make \_ada\_use\_c2phc usable, we have written a number of C
wrappers, responsible for parsing the arguments of the C functions to be
passed to \_ada\_use\_c2phc. The extension module and the shared object
for the implementation of phcpy is a set of wrappers defined by
phcpy2c.c and documented by phcpy2c.h. As a deliberate design decision
of phcpy, all calls to functions in PHCpack pass through the C
interface. By this design, the development of phcpy benefits the C and
C++ programmers.


Obtaining, Installing, and Contributing
---------------------------------------

PHCpack and phcpy are distributed under the GNU GPL license
(version 2 or any later version).
Recently a new repository PHCpack was added on github 
with the source code of version 2.3.84 of PHCpack,
which contains version 0.1.4 of phcpy.
Executable versions for Linux, Mac, and Windows are
available via the homepage of the author.

The code was developed on a Red Hat Enterprise Linux Workstation
(Release 6.4) and a MacBook Pro laptop (Mac OS X 10.8.5)
using the GNAT GPL 2013 compiler.
Versions 2.6.6 and 2.7.3 of Python, respectively on Linux and Mac,
were used to develop phcpy.  Packaged binary distributions of
phcpy for the platforms listed above are available via the
homepage of the author.

Although the blackbox solver of PHCpack has been in use since 1996,
phcpy itself is still very much in beta stage.
Suggestions for improvement and contributions to phcpy
will be greatly appreciated.

Acknowledgments
---------------

The author thanks Max Demenkov for his comments and questions
at the poster session at EuroSciPy 2013.  In particular the question
on obtaining all solutions along a path led to the introduction of
generator functions for the path trackers in version 0.1.4 of phcpy.

This material is based upon work supported by the National Science
Foundation under Grant No. 1115777.

References
----------

.. [AG93] E.L. Allgower and K. Georg.  *Continuation and path following*,
          Acta Numerica, pages 1-64, 1993.

.. [AG97] E.L. Allgower and K Georg.  *Numerical Path Following*,
          in P.G. Ciarlet and J.L. Lions, editors,
          Techniques of Scientific Computing (Part 2), volume 5 of 
          Handbook of Numerical Analysis, pages 3-203. North-Holland, 1997.

.. [AG03] E.L. Allgower and K.Georg.
          *Introduction to Numerical Continuation Methods*,
          volume 45 of Classics in Applied Mathematics, SIAM, 2003.

.. [Bai08] S.L. Bain.  *Emergent Design. The Evolutionary Nature of
           Professional Software Development*,
           Addison-Wesley, 2008.

.. [BHSW] D.J. Bates, J.D. Hauenstein, A.J. Sommese, and C.W. Wampler.
          *Bertini: Software for numerical algebraic geometry*,
          available at http://www.nd.edu/~sommese/bertini.

.. [BHSW08] D.J. Bates, J.D. Hauenstein, A.J. Sommese, and C.W. Wampler.
            *Software for numerical algebraic geometry: a paradigm and
            progress towards its implementation,*
            in M.E. Stillman, N.Takayama, and J. Verschelde, editors,
            Software for Algebraic Geometry, volume 148 of 
            The IMA Volumes in Mathematics and its Applications,
            pages 33-46,  Springer-Verlag, 2008.

.. [Bra] G. Brandl.  *Sphinx. Python Documentation Generator*,
         available at http://sphinx-doc.org.

.. [GLL02] T. Gao, T.Y. Li, and X. Li.  *HOM4PS*, 2002,
           available at http://www.csulb.edu/~tgao/RESEARCH/Software.htm.

.. [GLW05] T. Gao, T.Y. Li, and M. Wu.  *Algorithm 846: MixedVol: 
           a software package for mixed-volume computation*,
           ACM Trans. Math. Softw., 31(4):555-560, 2005.

.. [GKK+04] T. Gunji, S. Kim, M. Kojima, A. Takeda, K. Fujisawa,
            and T. Mizutani.  *PHoM -- a polyhedral homotopy 
            continuation method for polynomial systems*,
            Computing, 73(4):55-77, 2004.

.. [GPV13] E. Gross, S.  Petrović, and J. Verschelde.
           *PHCpack in Macaulay2*,
           The Journal of Software for Algebra and Geometry: Macaulay2,
           5:20-25, 2013.

.. [GV08a] Y. Guan and J. Verschelde.
           *Parallel implementation of a subsystem-by-subsystem solver*,
           in Proceedings of the 22th High Performance Computing Symposium,
           Quebec City, 9-11 June 2008, pages 117-123,
           IEEE Computer Society, 2008.

.. [GV08b] Y. Guan and J. Verschelde.
           *PHClab: A MATLAB/Octave interface to PHCpack*,
           in M.E. Stillman, N.Takayama, and J. Verschelde, editors,
           Software for Algebraic Geometry, volume 148 of 
           The IMA Volumes in Mathematics and its Applications,
           pages 15-32, Springer-Verlag, 2008.

.. [HLB01] Y. Hida, X.S. Li, and D.H. Bailey.
           *Algorithms for quad-double precision floating point arithmetic*,
           in 15th IEEE Symposium on Computer Arithmetic (Arith-15 2001),
           11-17 June 2001, Vail, CO, USA, pages 155-162. 
           IEEE Computer Society, 2001.
           Shortened version of Technical Report LBNL-46996,
           software at http://crd.lbl.gov/~dhbailey/mpdist/qd-2.3.9.tar.gz.

.. [LLT08] T.L. Lee, T.Y. Li, and C.H. Tsai.
           *HOM4PS-2.0: a software package for solving polynomial systems by
           the polyhedral homotopy continuation method*,
           Computing, 83(2-3):109-133, 2008.

.. [Ley11] A. Leykin. *Numerical algebraic geometry*,
           The Journal of Software for Algebra and Geometry: Macaulay2,
           3:5-10, 2011.

.. [LV04] A. Leykin and J. Verschelde.
          *PHCmaple: A Maple interface to the numerical homotopy algorithms
          in PHCpack*, in Quoc-Nam Tran, editor, Proceedings of the Tenth
          International Conference on Applications of Computer Algebra 
          (ACA'2004), pages 139-147, 2004.

.. [LV05] A. Leykin and J. Verschelde.
          *Factoring solution sets of polynomial systems in parallel*,
          In T. Skeie and C.-S. Yang, editors, Proceedings of the 2005
          International Conference on Parallel Processing Workshops.
          14-17 June 2005.  Oslo, Norway. High Performance Scientific 
          and Engineering Computing, pages 173-180,
          IEEE Computer Society, 2005.

.. [LV06] A. Leykin and J. Verschelde.
          *Interfacing with the numerical homotopy algorithms in PHCpack*,
          in N. Takayama and A. Iglesias, editors, Proceedings of ICMS 2006,
          volume 4151 of Lecture Notes in Computer Science, pages 354-360,
          Springer-Verlag, 2006.

.. [LV09] A. Leykin and J. Verschelde.
          *Decomposing solution sets of polynomial systems: a new parallel
          monodromy breakup algorithm*,
          The International Journal of Computational Science and
          Engineering, 4(2):94-101, 2009.

.. [LVZ06] A. Leykin, J. Verschelde, and Y. Zhuang.
           *Parallel homotopy algorithms to solve polynomial systems*,
           in N. Takayama and A. Iglesias, editors, Proceedings of ICMS 2006,
           volume 4151 of Lecture Notes in Computer Science, pages 225-234,
           Springer-Verlag, 2006.

.. [Li03] T.Y. Li.  *Numerical solution of polynomial systems by homotopy
          continuation methods*, in F. Cucker, editor,
          Handbook of Numerical Analysis. Volume XI.  Special Volume:
          Foundations of Computational Mathematics, pages 209-304.
          North-Holland, 2003.

.. [Mal] G. Malajovich.
         *pss3.0.5: Polynomial system solver, version 3.0.5*, available at 
         http://www.labma.ufrj.br/~gregorio/software.php.

.. [MNO+11] M. Maekawa, M. Noro, K. Ohara, N. Okutani, Y. Takayama,
          and Y. Tamura.
          *OpenXM -- an open system to integrate mathematical softwares*,
          2011, available at http://www.OpenXM.org.

.. [Mor87] A. Morgan.  *Solving polynomial systems using continuation 
           for engineering and scientific problems*,
           Prentice-Hall, 1987.
           Volume 57 of Classics in Applied Mathematics Series, SIAM 2009.

.. [Pir08] K. Piret.
           *Computing Critical Points of Polynomial Systems using PHCpack
           and Python*, PhD thesis, University of Illinois at Chicago, 2008.

.. [SOH+98] M. Snir, S. Otto, S. Huss-Lederman, D. Walker, and J. Dongarra.
            *MPI - The Complete Reference Volume 1, The MPI Core*,
            Massachusetts Institute of Technology, second edition, 1998.

.. [S+13] W.A. Stein et al.
          *Sage Mathematics Software (Version 5.12).*
          The Sage Development Team, 2013.  http://www.sagemath.org.

.. [SVW03] A.J. Sommese, J. Verschelde, and C.W. Wampler.
           *Numerical irreducible decomposition using PHCpack*,
           in M. Joswig and N. Takayama, editors, Algebra, Geometry, and
           Software Systems, pages 109-130. Springer-Verlag, 2003.

.. [SVW05] A.J. Sommese, J. Verschelde, and C.W. Wampler.
           *Introduction to numerical algebraic geometry*,
           in A. Dickenstein and I.Z. Emiris, editors,
           Solving Polynomial Equations. Foundations, Algorithms and
           Applications, volume 14 of 
           Algorithms and Computation in Mathematics,
           pages 301-337. Springer-Verlag, 2005.

.. [SW05] A.J. Sommese and C.W. Wampler.
          *The Numerical solution of systems of polynomials arising in
          engineering and science*,
          World Scientific Press, Singapore, 2005.

.. [SBB13] V. Stodden, J. Borwein, and D.H. Bailey.
           *``Setting the Default to Reproducible'' in Computational
           Science Research*, SIAM News, page 4, June 3, 2013.

.. [The] S.Thenault.  *Pylint. Code analysis for Python*,
         available at http://pylint.org.

.. [Ver99] J. Verschelde.
           *Algorithm 795: PHCpack: A general-purpose solver for polynomial
           systems by homotopy continuation*,
           ACM Trans. Math. Softw., 25(2):251-276, 1999.

.. [Ver10] J. Verschelde.
           *Polynomial homotopy continuation with PHCpack*,
           ACM Communications in Computer Algebra, 44(4):217-220, 2010.

.. [VW02] J. Verschelde and Y. Wang.
          *Numerical homotopy algorithms for satellite trajectory control by
          pole placement*,
          Proceedings of MTNS 2002, Mathematical Theory of Networks and Systems
          (CDROM), Notre Dame, August 12-16, 2002.

.. [VW04a] J. Verschelde and Y. Wang.
           *Computing dynamic output feedback laws*,
           IEEE Transactions on Automatic Control, 49(8):1393--1397, 2004.

.. [VW04b] J. Verschelde and Y. Wang.
           *Computing feedback laws for linear systems with a parallel Pieri
           homotopy*, In Y. Yang, editor, Proceedings of the 2004 
           International Conference on Parallel Processing Workshops,
           15-18 August 2004, Montreal, Quebec, Canada. 
           High Performance Scientific and Engineering Computing,
           pages 222-229, IEEE Computer Society, 2004.

.. [VZ06] J. Verschelde and Y. Zhuang.
          *Parallel implementation of the polyhedral homotopy method*,
          In T.M. Pinkston and F. Ozguner, editors, Proceedings of the
          2006 International Conference on Parallel Processing Workshops,
          14-18 Augustus 2006, Columbus, Ohio,
          High Performance Scientific and Engineering Computing,
          pages 481-488, IEEE Computer Society, 2006.

.. [Wat86] L.T. Watson.  *Numerical linear algebra aspects of globally
           convergent homotopy methods*,
           SIAM Rev., 28(4):529-545, 1986.

.. [Wat89] L.T. Watson.  *Globally convergent homotopy methods: a tutorial*,
           Appl. Math. Comput., 31(Spec. Issue):369-396, 1989.

.. [Wat02] L.T. Watson.  *Probability-one homotopies in computational science*,
           J. Comput. Appl. Math., 140(1&2):785-807, 2002.

.. [WBM87] L.T. Watson, S.C. Billups, and A.P. Morgan.
           *Algorithm 652: HOMPACK: a suite of codes for globally convergent
           homotopy algorithms*,
           ACM Trans. Math. Softw., 13(3):281-310, 1987.

.. [WSM+97] L.T. Watson, M. Sosonkina, R.C. Melville, A.P. Morgan,
            and H.F. Walker. *Algorithm 777: HOMPACK90: A suite of
            Fortran 90 codes for globally convergent homotopy algorithms*,
            ACM Trans. Math. Softw., 23(4):514-549, 1997.
