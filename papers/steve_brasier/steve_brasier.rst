:author: Steve Brasier
:email: steve.brasier@atkinsglobal.com
:institution: Atkins, 500 Park Avenue, Aztec West, BS32 4RZ 



------------------------------------------------------------
A Python-based Post-processing Tool-set For Seismic Analyses
------------------------------------------------------------

.. class:: abstract

    This paper discusses the design and implementation of a Python-based
    tool-set to aid in assessing the response of the UK's Advanced Gas
    Reactor nuclear power stations to earthquakes. The seismic analyses
    themselves are carried out with a commercial Finite Element solver, but
    understanding the raw data this produces requires customised post-processing
    and visualisation tools. Extending the existing tools had become
    increasingly difficult and a decision was made to develop a new,
    Python-based tool-set. This comprises of a post-processing framework
    (``"aftershock"``) which includes an an embedded Python interpreter, and a
    plotting package (``"afterplot"``) based on numpy and matplotlib.

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

The LS-DYNA solver produces about 120GB of binary-format data for each simulation split across multiple files. The original post-processing suite was a Microsoft Excel-based solution, using VBA to decode the binary data and carry out calculations and writing results to workbooks for plotting using Excel's in-built graphing capabilities. The post-processor was written by engineers with no formal software development training and had gradually grown more complex over several years as the models themselves were extended. The start of a new analysis campaign forced a reappraisal of the existing approach as there was little confidence that the new post-processing features required could be developed in the time or budget available. The technical debt [Atr01]_ in the system was high; a non-modular architecture and limited adherence to software design best-practices made it difficult to be sure that changes made in one place would not impact on unrelated functionality. As well as improving maintainability and extendibility, a number of other features were considered highly desirable for the revised post-processing package, including:

- Significantly faster performance: The Excel-based package was extremely limited in its ability to take advantage of multi-core processors, and post-processing runs commonly took XX hours.
- Linux-based post-processing: The LS-DYNA solver ran on a Linux server and moving post-processing onto the same hardware offered opportunities to batch analysis and post-processing, as well as providing access to higher-performance hardware.
- Improved plotting: Excel's plotting capabilities are poor in some respects.

A ground-up re-write was considered with some trepidation as it was clear that this would be a major undertaking. However further research convinced us that refactoring the code - a more palatable first step to lowering the technical debt - would not move a significant distance towards achieving the above goals as the Excel/VBA platform was simply too limiting. 

Overall Architecture
--------------------

An initial feasibility study lead to an archtecture with a central C++ core handling binary I/O. This would contain an embedded Python interpreter, allowing "user" scripts written in Python to define the actual calculations to be carried out. The C++ core, named ``aftershock``, would essentially be fixed and applicable to all of the reactor models to be analysed. By contrast the Python scripts could be developed and extended by "users", i.e. seismic engineers, as required as new seismic models were developed.

FIGURE??

This hybrid architecture was one solution to the trade-off between the need for the best possible performance when accessing and decoding the large quantity of binary data, versus a need for a high-level language for the actual calculations to permit them to be implemented by domain experts who were not software engineers. As usual the choice of language partly depended on user familiarity and there was some experience within the team with Python, both as a scripting language for other analysis packages and as a numerical programming language in its own right using the ``numpy`` and ``scipy`` [Atr03]_ packages.

As the entire binary dataset is too large to fit in memory at once ``aftershock`` operates frame-by-frame, stepping time-wise through the data. At each frame it calls certain functions from the scripts to carry out calculations on the data from that step. The scripts access this data through a simple Python API which returns lists of floats. The scripts may also define functions which are called by ``aftershock`` at the start and end of post-processing for initialisation or output of results. The ``aftershock`` core maintains necessary state from frame-to-frame and also optimises the order in which the results files are processed to minimise the number of passes needed. The ``aftershock`` core is not discussed further in this paper.

The calculation scripts generally make heavy use of the ``ndarrays`` provided by ``numpy`` [Atr02]_ to carry out efficent element-wise operations, although sometimes a more object-orientated approach is appropriate. As the API provided by ``aftershock`` hides all details of the actual binary file formats and how the data is split across files the engineer can concentrate entirely on the actual calculation required.

Plotting Architecture and Features
----------------------------------

Output from the calculation scripts is in some sense not an interesting aspect of post-processing, but it does form the final "product" which the client sees, whereas the rest of the post-processing toolchain is not visible. Tabular output of numerical data is straightforward and is currently handled using the ``csv`` module. However output of graphs and plots is considerably more complex. The previous Excel-based post-processor had exposed some limits to Excel's plotting capabilities, especially for contour-type plots and improvements in the types and format of plots avaiable was highly desirable. With Python as the calculation scripting language a number of plotting packages immediately became options but ``matplotlib`` [Atr04]_ stood out for its wide use, "*publication quality figures*" [Atr04]_ and sheer variety and flexibility of plotting capabilities it provided.

Development of the post-processing toolset could have ended at this point, leaving the script engineer to utilise ``matplotlib`` to generate plots as required. However ``matplotlib's`` versatility comes with a price in complexity and the API is not particularly intuitive. As an example, adding adding markers on the Y-axis of a plot - a familiar GUI operation in the existing Excel-based package - might require:

.. code-block:: python

    from matplotlib.ticker import AutoMinorLocator
    <code here>
    plt.yticks(range(0, 100, 20))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))

While this probably appears relatively straightforward to a software engineer conceptually there are various levels of abstraction and requiring the domain experts to spend time learning the details of the matplotlib API did not seem to represent good value for money for the client.

Consideration of both the existing post-processor and the scripts under consideration showed that in fact there were only a handful of separate types of plots required, although each type might be used to present multiple datasets. This made it feasible to provide a domain-specific plotting package, ``afterplot``, which internally uses ``matplotlib`` to generate plots but provides various plotter classes to the user. To create a plot the user simply creates an instance of the appropriate class.

Plotter class interfaces
------------------------

Both the raw analysis data and post-processed results are inherently four-dimensional; each value is associated with a particular spatial location in the model and a time during the simulated earthquake. In some cases one or more of these dimensions may be "collapsed" during post-processing, for example to provide a maximum value through time. From this it was clear that data interface to the plotter classes should be by passing ``numpy`` arrays of up to four dimensions. Standardising the meaning and order of the dimensions in the plotter interface meant that the same data easily be be plotted different ways. For example a four-dimensional ``ndarray`` giving displacements through time might be passed to a ``ChannelPlot`` object to show the physical arrangement of a vertical region of the core, or collapsed along the time axis and passed to a ``LayerPlot`` object to show the peak values on a horizontal slice through the core. More abstract plots can also use the same interface.  The WaterfallPlot class takes the same 4-dimensional data and provides an overview of every location in the core throughout the analysis - locations along the three spatial dimensions are collapsed into the vertical axis of the plot, time is plotted on the horizontal axis and values are represented by colour.

The use of four-dimensional arrays as the data interface permits each plotter to be fairly general-purpose, defining only how the data is presented, not what is calculated. The user supplies labels for the dimensions to provide meaning to the plot.

The development of a custom plotting package also permitted a significant standardisation of presentation which improves quality overall. For example the interface *requires* axis labels and titles to be defined and grid-lines to be shown, rather than leaving it to the user to adhere to a best-practice guide or relying on review to ensure these have been included. It also provided an opportunity to drive best-practice across all the plots. For example the default ``matplotlib`` colour scale for contour-type plots was not considered particularly clear. It was discovered that this is an area of active research and the WHAT BAR was identified as a STUFF ABOUT CLARITY; ALSO WANT TO SAY SOME STUFFA BOUT HOW WELL FOUNDED IT WAS.

ADD COLOURBAR EXAMPLES.

Plotter functionality
---------------------

Each plotter class may define both a GUI interface and an API which mirrors the same functionality, allowing aspects of the plot to be controlled interactively or via the calculation script. What functionality provided by the plotter's GUI and API arises from the central philosopy of ``afterplot``, which is to separate the calculation of *values* from the *presentation* of those values; the former must be tightly controlled whereas flexibility for the latter is desirable. For example, the data shown on a specific contour plot is defined entirely by the sequence of operations in the relevant calculation script, and should not be modifyable. However the color range to be used is initially indeterminate - the calculation script may set some sensible defaults (e.g. max and min of the plotted data) but what values are most appropriate will depend partly on how the plot appears with the specific data from that model.

Much of the machinery for the GUI for each plotter class is provided by the base class ``baseplot``. This essentially wraps ``matplotlib.Figure`` objects but with a number of signficant extensions. Firstly, plotter classes may define custom options for the ``matplotlib`` toolbar. The ``baseplot`` class handles set-up and tear-down of the necessary widgets, depending on the backend[FOOTNOTE] in use. When adding GUIs to ``Figure`` objects the ``matplotlib`` documentation describes two alternatives:

1. Using the cross-backend widgets provided by WHAT
2. Starting from scratch calling the necessary backend functions, as documented WHERE.

However during development of it was noted a third option was possible and combined the ease of development of the first with the functionality of the second. Essentially, ``matplotlib.pyplot`` can be used to create the Figure THEN WHAT. Obviously this does not have the cross-backend functionality of the approach using ``whatever``, but the default ``WHICHEVER`` backend which is available on most ``matplotlib`` installations was found to have sufficent functionality for our purposes. CODE EXAMPLE:

The second major extension was to allow the user to store and restore plots together with their GUI. Saving of static images of plots is provided by ``matplotlib``. However with ``matplotlib`` alone, once a ``Figure`` window has been closed there is no way to regenerate it except for re-running the entire script which created it. As discussed above it was considered desirable to have the the *presentation* of data easily modifiable, while preventing modification of the actual data itself. As the entire post-processing run might take several hours to complete, re-running it simply to change presentation aspects such as the colour ranges on a contour plot was clearly not acceptable. The store/restore functionality provided by the ``baseplot`` class enables the state of an entire plot object, including its GUI, to be saved to disk, and restored later to a new interactive session. The major steps for this are described below:

Store:
- steps

Restore:
- steps

The ``baseplot`` class also enables traceability of data on each plot. QA objects. Introspection/stack. Imports.


Lessons Learnt
--------------

TODO

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


