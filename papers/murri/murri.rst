:author: Riccardo Murri
:email: riccardo.murri@gmail.com
:institution: Grid Computing Competence Center, University of Zurich


---------------------------------------------------------------
Performance of Python runtimes on a non-numeric scientific code
---------------------------------------------------------------

.. class:: abstract

  The Python library FatGHol [FatGHoL]_ used in [Murri2012]_ to reckon
  the rational homology of the moduli space of Riemann surfaces is an
  example of a non-numeric scientific code: most of the processing it
  does is generating graphs (represented by complex Python objects)
  and computing their isomorphisms (a triple of Python lists; again a
  nested data structure). These operations are repeated many times
  over: for example, the spaces `M_{0,6}`:math: and `M_{1,4}`:math:
  are triangulated by 4'583'322 and 747'664 "fatgraphs", respectively.

  This is an opportunity for every Python runtime to prove its
  strength in optimization. The purpose of this experiment was to
  assess the maturity of alternative Python runtimes, in terms of:
  compatibility with the language as implemented in CPython 2.7, and
  performance speedup.

  This paper compares the results and experiences gotten by running
  FatGHol with different Python runtimes: CPython 2.7.5, PyPy 2.1,
  Cython 0.19, Numba 0.11, Nuitka 0.4.4 and Falcon.

.. class:: keywords

   python runtime, non-numeric, homology, fatgraphs


Introduction
------------

The moduli space `M_{g,n}`:math: of smooth Riemann surfaces is a
topological space, which has been subject of much research both in
algebraic geometry and in string theory. It is known since the '90s
that this space has a triangulation indexed by a special kind of
graphs [Penner1988]_ [Kontsevich1992]_ [ConantVogtmann2003]_,
nicknamed "fat graphs".

Since graphs are combinatorial and discrete objects, a computational
approach to the problem of computing topological invariants of
`M_{g,n}`:math: is now feasible; algorithms to enumerate fatgraphs and
compute their graph homology have been devised in [Murri2012]_ and
implemented in Python.

The purpose of this experiment was to assess the maturity of
alternative Python runtimes, in terms of:

(a) compatibility with the language as implemented in CPython 2.7, and
(b) performance speedup.

In particular, we were interested in the possible speedups of
a large non-numeric code.


Experiment setup
----------------

The `FatGHoL <http://fatghol.googlecode.com/>` [FatGHoL]_ program was
used as a test code.  FatGHoL computes homology of the moduli spaces
of Riemann surfaces `M_{g,n}`:math: via Penner-Kontsevich' fatgraph
simplicial complex [Penner1988]_ [Kontsevich1992]_.  The program runs
in three stages:

1. generate fatgraphs,
2. make the simplicial homology complex explicit, and
3. actually solve the homology linear system.

The last step has been disabled in the test code as it is implemented
in C++ for speed.  What remains is 100% pure Python code that runs on
Python 2.6+ (but could run on 2.5 with minimal modifications).

FatGHoL involves a large number of graph isomorphism computations:
especially during fatgraph generation, each candidate fatgraph needs
to be compared to all fatgraphs already discovered, in order to avoid
duplicates. In later stages, the isomorphism computations are cached
in memory, but in step 2.  additional data is created for each graph,
in order to pass from fatgraphs to simplices.

It is worth noting that the FatGHoL code exercises many of Python's
advanced data manipulation features, like list and dictionary
comprehensions, slicing, etc. but does not use any kind of tight
nested loops of the kind normally featured in numeric codes.

Profile data show more precisely how much work is done at the Python
level in the simpler case `M_{0,4}`:math: ::

           15787953 function calls (15728052 primitive calls) in 39.572 seconds

     Ordered by: call count

     ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    2216088    2.175    0.000    2.175    0.000 rg.py:227(<genexpr>)
     966575    0.819    0.000    0.819    0.000 rg.py:143(is_loop)
     775362    0.839    0.000    0.839    0.000 cyclicseq.py:88(__getitem__)
     775362    0.634    0.000    0.634    0.000 rg.py:170(other_end)
     722308    3.438    0.000    5.760    0.000 combinatorics.py:368(__init__)
     539039    1.689    0.000    1.689    0.000 cyclicseq.py:112(__getslice__)
  506075/447917    0.745    0.000    1.840    0.000 cache.py:181(wrapper)
     476134    1.122    0.000    1.122    0.000 combinatorics.py:441(rearranged)
     385725    0.355    0.000    0.355    0.000 rg.py:137(__init__)
     345740    0.849    0.000    0.849    0.000 rg.py:568(_first_unused_corner)
     ...


The FatGHoL code was run with seven different alternative Python
runtimes (a detailed description of each of these is given in a later
section):

* CPython 2.7.5;
* Cython 0.19.1;
* Cython 0.19.1 in "pure Python mode";
* Falcon 0.05;
* Nuitka 0.4.4;
* PyPy 2.1;
* Numba 0.10.0 and 0.11.0 with ``@autojit``.

Except for Cython in "pure Python mode" and Numba, all runtimes run
the unmodified Python code of FatGHoL.  Cython in "pure Python mode"
require the addition of decorators to the Python code that specify the
types of function arguments and local variables to increase speedup of
selected portions of the code.  Similarly, Numba uses decorators
``@jit`` or ``@autojit`` to mark functions that should be compiled to
native code (the difference between the two decorators seems to be
that ``@autojit`` infers the types at runtime, whereas ``@jit``
requires the programmer to specify them); we only used the
``@autojit`` decorator to mark the same functions that were marked as
optimization candidates in the Cython experiment.

Each Python runtime was run on 4 test cases: computing the homology of
the `M_{0,4}`:math:, `M_{0,5}`:math:, `M_{1,3}`:math:, and
`M_{2,1}`:math: moduli spaces.  The test cases take from 0.20s to more
than 2 minutes of runtime with CPython 2.7.  Each test case was run 10
times and the best time and lowest RAM occupation are reported in the
summary tables below.


Results
-------

Falcon and Numba could not run the code (see details in a later
section) and thus do not appear in the report below.

For each runtime, the total used CPU time and memory were measured:
results are given in Tables :ref:`table-cpu` and :ref:`table-mem`; a
summary graph is given in Figures :ref:`cpu-all` and :ref:`mem-all`.
Detailed comparisons are given in the other figures.

.. figure:: CPU_time_of_Python_runtimes_synopsis.pdf
   :figclass: wtb
   :align: center

   Comparison of the total CPU time used by each runtime on the
   different test cases.  The `x`:math:-axis is sorted so that the
   runtimes for CPython 2.7.5 are ascending.  The `y`:math:-axis shows
   values in seconds (smaller is better). Note that the `y`:math:-axis
   is drawn on a logarithmic scale!
   :label:`cpu-all`

.. table:: CPU time (in seconds) consumed by each Python runtime. :label:`table-cpu`
   :class: w

  +-----+----------+--------------+--------------------------+---------------+---------------+
  | Mgn | PyPy 2.1 | Nuitka 0.4.4 | Cython 0.19.1 (w/ hints) | Cython 0.19.1 | CPython 2.7.5 |
  +-----+----------+--------------+--------------------------+---------------+---------------+
  | M04 |     0.52 |         0.15 |                     0.13 |          0.14 |          0.17 |
  +-----+----------+--------------+--------------------------+---------------+---------------+
  | M05 |    10.65 |        22.25 |                    13.88 |         14.54 |         20.14 |
  +-----+----------+--------------+--------------------------+---------------+---------------+
  | M13 |    34.27 |       135.48 |                    92.55 |         93.25 |        126.27 |
  +-----+----------+--------------+--------------------------+---------------+---------------+
  | M21 |     5.25 |         6.47 |                     3.68 |          3.68 |          5.12 |
  +-----+----------+--------------+--------------------------+---------------+---------------+

The CPU time data prompt a few observations:

- PyPy gives the best results, provided the code runs long enough to
  discount for the startup time of the JIT compiler.  However, given
  enough time, the JIT compiler gives extremely good results, with
  speedups of 100% to 400% relative to CPython in the `M_{0,5}`:math:
  and `M_{1,3}`:math: cases.  In other words, for the JIT approach to
  pay off, the code needs to perform many iterations of the same code
  path (this is certainly the case for FatGHoL), because compiling a
  single function to native code takes a non-negligible amount of
  time.  The break-even point for the FatGHoL code seems to be around
  5 seconds of runtime: on `M_{2,1}`:math:, the CPU time taken by
  CPython and PyPy are almost equal.

- Cython gives consistently about a 30% speedup on unmodified Python
  code.  However, the "pure Python mode", in which Cython takes
  variable typing hints embedded in the code does not seem to give any
  advantage: results of the two runs are not significantly different.
  This might be related to a bug in the current version of Cython, see
  details in a later section.


.. figure:: Max_used_memory_of_Python_runtimes_synopsis.pdf
   :figclass: wtb
   :align: center

   Comparison of the total RAM used by each runtime on the
   different test cases.  The `x`:math:-axis is sorted so that the
   RAM usage for CPython 2.7.5 are ascending.  The `y`:math:-axis
   shows values in MBs (smaller is better).  Note that the `y`:math:-axis
   is drawn on a logarithmic scale!
   :label:`mem-all`

.. table:: Amount of RAM (MBs) consumed by each Python runtime. :label:`table-cpu`
   :class: w

  +-----+----------+--------------+--------------------------+---------------+---------------+
  | Mgn | PyPy 2.1 | Nuitka 0.4.4 | Cython 0.19.1 (w/ hints) | Cython 0.19.1 | CPython 2.7.5 |
  +-----+----------+--------------+--------------------------+---------------+---------------+
  | M04 |   217.75 |        57.81 |                    44.82 |         45.21 |         39.03 |
  +-----+----------+--------------+--------------------------+---------------+---------------+
  | M05 |   709.54 |       573.87 |                   196.67 |        196.54 |        191.89 |
  +-----+----------+--------------+--------------------------+---------------+---------------+
  | M13 |  1632.53 |      2445.68 |                   264.67 |        265.09 |        261.15 |
  +-----+----------+--------------+--------------------------+---------------+---------------+
  | M21 |   412.73 |       229.02 |                    60.79 |         61.21 |        55.515 |
  +-----+----------+--------------+--------------------------+---------------+---------------+

The large memory consumption from PyPy and Nuitka stands out in the
memory data of :ref:`table-mem`.  On the other hand, there is no
significant increase in memory usage between CPython and Cython.

The large memory usage of Nuitka can be explained by the fact that the
JIT infrastructure must keep in memory the profile and traces for all
the code paths taken.  In any long-running program, the memory should
eventually reach a steady state and not increase any further; it
should be noted however, that in these benchmarks the memory used by
the PyPy JIT framework dwarfs the memory used by the program itself.

We have no explanation for the large memory consumption of Nuitka.


.. figure:: CPU_time_of_Python_runtimes_M04.pdf
   :figclass: tbp
   :align: left

   Comparison of the total CPU time used by each runtime on the
   `M_{0,4}`:math: test case.  The `y`:math:-axis shows
   values in seconds.
   :label:`cpu-M04`

.. figure:: CPU_time_of_Python_runtimes_M05.pdf
   :figclass: tbp
   :align: left

   Comparison of the total CPU time used by each runtime on the
   `M_{0,5}`:math: test case.  The `y`:math:-axis shows
   values in seconds.
   :label:`cpu-M05`

.. figure:: CPU_time_of_Python_runtimes_M13.pdf
   :figclass: tbp
   :align: left

   Comparison of the total CPU time used by each runtime on the
   `M_{1,3}`:math: test case.  The `y`:math:-axis shows
   values in seconds.
   :label:`cpu-M13`

.. figure:: CPU_time_of_Python_runtimes_M21.pdf
   :figclass: tbp
   :align: left

   Comparison of the total CPU time used by each runtime on the
   `M_{2,1}`:math: test case.  The `y`:math:-axis shows
   values in seconds.
   :label:`cpu-M21`


.. figure:: Max_used_memory_of_Python_runtimes_M04.pdf
   :figclass: tbp
   :align: left

   Comparison of the total RAM usage by each runtime on the
   `M_{0,4}`:math: test case.  The `y`:math:-axis shows
   values in MBs.
   :label:`mem-M04`

.. figure:: Max_used_memory_of_Python_runtimes_M05.pdf
   :figclass: tbp
   :align: left

   Comparison of the total RAM usage by each runtime on the
   `M_{0,5}`:math: test case.  The `y`:math:-axis shows
   values in MBs.
   :label:`mem-M05`

.. figure:: Max_used_memory_of_Python_runtimes_M13.pdf
   :figclass: tbp
   :align: left

   Comparison of the total RAM usage by each runtime on the
   `M_{1,3}`:math: test case.  The `y`:math:-axis shows
   values in MBs.
   :label:`mem-M13`

.. figure:: Max_used_memory_of_Python_runtimes_M21.pdf
   :figclass: tbp
   :align: left

   Comparison of the total RAM usage by each runtime on the
   `M_{2,1}`:math: test case.  The `y`:math:-axis shows
   values in MBs.
   :label:`mem-M21`


Runtime systems details
-----------------------

`Cython 0.19.1 <http://cython.org/>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cython is a compiler for a superset of the Python language. It
translates Python modules to a C or C++ source that is then compiled
to a native code library that CPython can load and use. Cython
optimizes best when users decorate the source code with hints at the
types of variables and functions; it can also translate unmodified
Python code, but then no type inference is performed. Cython allows a
variety of ways for giving these type hints; its so-called "pure
Python" mode requires users to insert functions and variable
decorators in the code: the Cython compiler can act on these
directives, but the CPython interpreter will instead load a ``cython``
module which turns them into no-ops.

We tested Cython twice: on the unmodified Python sources, and with
hinting in the "pure Python" mode.  The graphs show however very
little difference between the two modes; this could be a consequence
of Cython `defect ticket #477`__.

.. __: http://trac.cython.org/cython_trac/ticket/477

Cython does its best when the source code is annotated with its
extended keywords, which allow specifying the types of variables
(which allows optimizations, e.g., in loops), or
marking certain functions as C-only (which saves time when
dereferencing variables).  This extended markup can be provided either
in the sources, or in additional ``.pxd`` files.  We have not done
this exercise, however, as the amount of coding time required to
properly mark all functions and variables is quite substantial.


`Falcon 0.05 <https://github.com/rjpower/falcon>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falcon is a Python extension module that hacks into a CPython
interpreter and changes the execution loop, implementing several
optimizations (for instance, using a register-based VM instead of a
stack-based one) that the Falcon authors think should
upstream. However, Falcon is still in early stages of development and
crashes on FatGHoL code with a segmentation fault.


`Numba <http://numba.pydata.org/>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As its website states:

  Numba is an optimizing compiler for Python; it uses the LLVM
  compiler infrastructure to compile Python syntax to machine code.
  It is NumPy-aware and can speed up code using NumPy arrays.  Other,
  less well-typed code will be translated to Python C-API calls
  effectively removing the "interpreter" but not removing the dynamic
  indirection. Numba is also not a Just-In-Time compiler.

Numba requires the code developer to use either the ``@autojit`` (use
run-time type info) or the ``@jit`` (explicitly provide type
information) decorators to mark those functions that should be
compiled. For our experiment, we used the decorator ``@autojit`` on
all functions that were decorated also in the Cython test.

Versions 0.10.0 and 0.11.0 of Numba were tested; we could not get
either version to work.

Numba version 0.10.0 dies with an internal error ("TypeError: type_container() takes exactly 1 argument (3 given)", reported as
`Issue #295`__ on Numba's GitHub issue tracker), that has
been fixed in version 0.11.

.. __: https://github.com/numba/numba/issues/295

However, Numba 0.11.0 with a "NotImplementedError: Unable to cast from
{ i64, i8* }* to { i64, i8* }" message.  This has been reported as
`Issue #350`__ on the `issue tracker`__ and is waiting for a fix.

.. __: https://github.com/numba/numba/issues/350
.. __: https://github.com/numba/numba/issues?state=open


`Nuitka 0.4.4 <http://www.nuitka.net/>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nuitka translates Python (2.6+) into a C++ program that then uses
``libpython`` to execute in the same way as CPython does, in a very
compatible way.  Although still in development, Nuitka claims that it
already:

  create[s] the most efficient native code from this. This
  means to be fast with the basic Python object handling.

Results of this experiment seem not to corroborate this claim.


`PyPy 2.1 <http://pypy.org/>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PyPy is a Python language interpreter with a Just-In-Time compiler
(and many other features!).  It can thus translate repetitive Python
code into native code on the fly.  PyPy must first be bootstrapped by
compiling itself, which takes a lot of time and RAM, but then it is a
drop-in replacement for the ``python`` command and just works.


Acknowledgements
----------------

The author acknowledges support of the Informatik Dienste of the
University of Zurich, particularly for the usage of the new SGI UV
machine for running the tests.  I would also like to thank Kay Hayen,
Marc Florisson, Russel Power and Alex Rubynstein for their readiness
to discuss and fix the bugs I reported on Nuitka, Numba, and Falcon.
Finally, I would like to express my gratitude to all those who made
remarks and inquiries at the EuroSciPy poster session, and
particularly Ronan Lamy and Denis Engemann for their insightful
comments.


References
----------

.. [Murri2012] R. Murri. *Fatgraph Algorithms and the Homology of the Kontsevich Complex*,
               arXiv preprint arXiv:1202.1820, February 2012.

.. [FatGHoL] R. Murri. *The FatGHoL software website*,
             http://fatghol.googlecode.com/

.. [Penner1988] R. C. Penner. *Perturbative series and the moduli space of Riemann surfaces*,
                J. Differential Geom, 1988.

.. [Kontsevich1992] M. Kontsevich. *Formal (non)-commutative symplectic geometry*,
                    The Gelfand Mathematical Seminars, 1990–1992.

.. [ConantVogtmann2003] J. Conant, K. Vogtmann. *On a theorem of Kontsevich*,
                        Algebr. Geom. Topol., 2003.
