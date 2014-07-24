:author: Steve Brasier
:email: steve.brasier@atkinsglobal.com
:institution: Atkins, 500 Park Avenue, Aztec West, BS32 4RZ 



------------------------------------------------------------
A Python-based Post-processing Tool-set For Seismic Analyses
------------------------------------------------------------

.. class:: abstract

    This talk will discuss the design and implementation of a Python-based
    tool-set to aid in assessing the response of the UK's Advanced Gas
    Reactor nuclear power stations to earthquakes. The seismic analyses
    themselves are carried out with a commercial Finite Element solver, but
    understanding the raw data this produces requires customised post-processing
    and visualisation tools. Extending the existing tools had become
    increasingly difficult and a decision was made to develop a new,
    Python-based tool-set. This comprises of a post-processing framework
    ("aftershock") which includes an an embedded Python interpreter, and a
    plotting package ("afterplot") based on numpy and matplotlib.

    The new tool-set had to be significantly more flexible and easier to
    maintain than the existing code-base, while allowing the majority of 
    development to be carried out by engineers with little training in software 
    development. The resulting architecture will be described with a focus on 
    exploring how the design drivers were met and the successes and challenges 
    arising from the choices made.

.. class:: keywords

   python, numpy, matplotlib, seismic analysis, plotting

Introduction
------------

The UK has a fleet of Advanced Gas-cooled Reactors (AGRs) which became operational in the 1970's. These were a second generation reactor design and have a core consisting of layers of interlocking graphite bricks which act to slow neutrons from the fuel to sustain the nuclear reaction. Although the UK does not regularly experience significant earthquakes it is still necessary to demonstrate that the reactors could be safely shut-down if a severe earthquake were to occur.

A series of computer models have been developed to examine the behaviour of the reactors during an earthquake. These models are regularly upgraded and extended as the cores age to ensure the relevant behaviour can be modelled. The models themselves are analysed using the commercial Finite Element Analysis code LS-DYNA. This calculates predictions for the positions and velocities of the tens of thousands of bricks in the core during the simulated earthquake.

By itself, this raw data is not particularly informative and engineers seek answers to higher-level questions such as:

- Can the control rods enter the distorted core?
- Is the fuel integrity maintained?

To help us answer these questions a complex set of post-processing calculations is carried out to convert the raw data into parameters which describe the seismic performance of the core, assess these parameters against acceptable limits, and present the results in tabular or graphical form. This paper describes a recent complete re-write of this post-processing toolset and seeks to explore some of the software decisions made and their impact on the engineering users.

Background
----------

The LS-DYNA solver produces about 120GB of binary-format data for each simulation. The original post-processing suite was a Microsoft Excel-based solution, using VBA to decode the binary data and carry out calculations and writing results to workbooks for plotting using Excel's in-built graphing capabilities. The post-processor was written by engineers with no formal software development training and had gradually grown more complex over several years as the models themselves were extended. The start of a new analysis campaign forced a reappraisal of the existing approach as there was little confidence that the new post-processing features required could be developed in the time or budget available. The technical debt [Atr01]_ in the system was high; a non-modular architecture and limited adherence to software design best-practices made it difficult to be sure that changes made in one place would not impact on unrelated functionality. As well as improving maintainability and extendibility, a number of other features were considered highly desirable for the revised post-processing package, including:

- Significantly faster performance: The Excel-based package was extremely limited in its ability to take advantage of multi-core processors, and post-processing runs commonly took XX hours.
- Linux-based post-processing: The LS-DYNA solver ran on a Linux server and moving post-processing onto the same hardware offered opportunities to batch analysis and post-processing, as well as providing access to higher-performance hardware.
- Improved plotting: Excel's plotting capabilities are poor in some respects, particularly contour plots.

A ground-up re-write was considered with some trepidation as it was clear that this would be a major undertaking. However further research convinced us that refactoring the code - a more palatable first step to lowering the technical debt - would not move a significant distance towards achieving the above goals as the Excel/VBA platform was simply too limiting. A feasibility study lead to the architecture described in the next section.

Overall Architecture
--------------------

The new post-processor was split into three separate parts:

- A C++ programme ``"aftershock"``. This handles the binary file I/O and determines which order to read the various sets of results files in depending on calculation requirements. It contains an embedded Python 2.7 interpreter and provides a Python API to access the results data as built-in Python objects such as lists.
- A set of Python scripts which define the actual calculations to be carried out, generally with liberal use of the ``numpy`` package [Atr02]_.
- A custom plotting library ``"afterplot"`` based on the ``matplotlib`` [Atr04]_ Python package.

This hybrid architecture was driven a trade-off between the need for relatively high performance access to the binary data and a need for a high-level language for the actual calculations. These would be defined and implemented by domain experts who were not software engineers. As usual the choice of language partly depended on user familiarity and there was some experience within the team with Python, both as a scripting language for other analysis packages and as a numerical programming language in its own right using the ``numpy`` and ``scipy`` [Atr03]_ packages.

The C++ ``aftershock`` programme is not discussed further in this paper.

MOVE INTRO TO PLOTTER INTO HERE??

Plotting Architecture and Features
----------------------------------

With Python as the calculation scripting language a number of plotting packages immediately became options. However ``matplotlib`` stood out for its wide use, "publication quality figures" and sheer variety and flexibility of plotting capabilities it provided. However this versatility comes with a price in complexity and the API is not particularly intuitive. As an example, adding adding markers on the Y-axis of a plot - a familiar GUI operation in the existing Excel-based package - might require the user to add:

.. code-block:: python

    from matplotlib.ticker import AutoMinorLocator
    <code here>
    plt.yticks(range(0, 100, 20))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))

ADD SOME STUFF HERE ABOUT WHY THIS ISN'T OBVIOUS, And USER=ENGINEER, don't want them to have to learn matplotlib.

However consideration of existing and desirable output formats showed that there were only a handful of different types of plots. This made it feasible to provide a domain-specific plotting package which internally used ``matplotlib`` but represented each type of plot as a class. To create a plot the user (i.e. the engineer developing the calculation) creates an instance of the class.

Both the raw analysis data and post-processed results are inherently four-dimensional; each value is associated with a particular spatial location in the model and a time during the simulated earthquake. In some cases one or more of these dimensions may be "collapsed" during post-processing, for example to provide a maximum value through time. From this it was clear that data interface to the plotter classes should be by passing ``numpy`` arrays of up to four dimensions. Standardising the meaning and order of the dimensions in the plotter interface meant that the same data easily be be plotted different ways. For example an array of displacements (4-dimensional data) might be passed to a ``ChannelPlot`` object to show the physical arrangement of a vertical region of the core, or collapsed along the time axis and passed to a ``LayerPlot`` object to show peak values on a horizontal slice through the simulated core. More abstract plots can also use the same interface; for example the WaterfallPlot class takes the same 4-dimensional data and provides an overview of every location in the core throughout the analysis. Locations along the three spatial dimensions are collapsed into the vertical axis of the plot, time is plotted on the horizontal axis and values are represented by colour.

The use of four-dimensional arrays as the data interface permits each plotter to be fairly general-purpose, defining only how the data is presented, not what is calculated. The user supplies labels for the dimensions to provide meaning to the plot. However defining a specific plotter interface also permitted a significant tightening of control over plot quality as for example the interface can *require* axis labels and titles to be defined or grid-lines to be shown, rather than leaving it to the user or later checks to ensure these have been included.

ADD COLOURBAR EXAMPLES.

BASEPLOT: 
QA: traceability. Introspection/stack. Imports.

Store/restore

CHECK "USER"

CHECK CASE





Features
--------

Difficulties
------------



## EVERYTHING BELOW HERE IS FROM THE EXAMPLE ##


Twelve hundred years ago  |---| in a galaxy just across the hill...

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum sapien
tortor, bibendum et pretium molestie, dapibus ac ante. Nam odio orci, interdum
sit amet placerat non, molestie sed dui. Pellentesque eu quam ac mauris
tristique sodales. Fusce sodales laoreet nulla, id pellentesque risus convallis
eget. Nam id ante gravida justo eleifend semper vel ut nisi. Phasellus
adipiscing risus quis dui facilisis fermentum. Duis quis sodales neque. Aliquam
ut tellus dolor. Etiam ac elit nec risus lobortis tempus id nec erat. Morbi eu
purus enim. Integer et velit vitae arcu interdum aliquet at eget purus. Integer
quis nisi neque. Morbi ac odio et leo dignissim sodales. Pellentesque nec nibh
nulla. Donec faucibus purus leo. Nullam vel lorem eget enim blandit ultrices.
Ut urna lacus, scelerisque nec pellentesque quis, laoreet eu magna. Quisque ac
justo vitae odio tincidunt tempus at vitae tortor.

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

.. figure:: figure1.png

   This is the caption. :label:`egfig`

.. figure:: figure1.png
   :align: center
   :figclass: w

   This is a wide figure, specified by adding "w" to the figclass.  It is also
   center aligned, by setting the align keyword (can be left, right or center).

.. figure:: figure1.png
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
.. [Atr01] W Cunningham. *The WyCash Portfolio Management System*,
           OOPSLA '92 Addendum to the proceedings on Object-oriented programming
           systems, languages, and applications, pp. 29-30.
	   http://c2.com/doc/oopsla92.html

.. [Atr02] Numpy

.. [Atr03] Scipy

.. [Atr04] J. D. Hunter. *Matplotlib: A 2D Graphics Environment*,
	   Computing in Science & Engineering, 9(3):90-95, 2007.

.. [Atr99] P. Atreides. *How to catch a sandworm*,
           Transactions on Terraforming, 21(3):261-300, August 2003.


