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
    (``aftershock``) which includes an embedded Python interpreter, and a
    plotting package (``afterplot``) based on ``numpy`` and ``matplotlib``.

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

The UK has a fleet of Advanced Gas-cooled Reactors (AGRs) which became operational in the 1970's. These are a second generation reactor design and have a core consisting of layers of interlocking graphite bricks, **ADD FIGURE** which act to slow neutrons from the fuel to sustain the fission reaction. Although the UK does not regularly experience significant earthquakes it is still necessary to demonstrate that the reactors could be safely shut-down if a severe earthquake were to occur.

A series of computer models have been developed to examine the behaviour of the reactors during an earthquake. These models are regularly upgraded and extended as the cores change over their lives to ensure that the relevant behaviours can be simulated. The models themselves are analysed using the commercial Finite Element Analysis code LS-DYNA. This calculates predicted positions and velocities for the thousands of graphite bricks in the core during the simulated earthquake. However engineers seek answers to high-level questions such as:

- Can the control rods still enter the core?
- Is the integrity of the fuel maintained?

To help answer these questions a complex set of post-processing calculations is required. These convert the raw position and velocity data into parameters describing the seismic performance of the core, assess these parameters against acceptable limits, and present the results in tabular or graphical form.

This paper describes a recent complete re-write of this post-processing toolset. It seeks to explore some of the software and architectural decisions made and examine the impact of these decisions on the engineering users.

Background
----------

The LS-DYNA solver produces about 120GB of binary-format data for each simulation, split across multiple files. The original post-processing suite was a Microsoft Excel-based solution which used VBA to decode the binary data and carry out calculations. The results were output to workbooks for plotting using Excel's graphing capabilities. This post-processor was written by engineers with no formal software development training and had gradually grown more complex over several years as the models themselves were extended.

The start of a new analysis campaign forced a reappraisal of the existing approach as there was low confidence that the new post-processing features required could be developed in the time or budget available. The technical debt [Atr01]_ in the system was high and a non-modular architecture made it difficult to guarantee that changes made in one place would not have an impact on unrelated functionality. As well as improving maintainability and extendibility, a number of other features were considered highly desirable for the revised post-processing package, including:

- Significantly faster performance: The Excel-based package was extremely limited in its ability to take advantage of multi-core processors, and post-processing runs commonly took *X* hours.
- Linux-based post-processing: The LS-DYNA solver ran on a Linux server. Moving post-processing onto the same hardware offered opportunities to batch analysis and post-processing, as well as providing access to higher-performance hardware than was available when using Excel and a Windows platform.
- Improved plotting: While convenient, Excel's plotting capabilities are limited in some respects.

A ground-up re-write was considered with some trepidation as it was clear that this would be a major undertaking. A more palatable first step would have been refactoring the existing code. However futher investigation convinced us that this would not progress a significant distance towards the above goals as the Excel/VBA platform was simply too limiting.

Overall Architecture
--------------------

An initial feasibility study lead to an archtecture with a central C++ core handling binary I/O. This would contain an embedded Python interpreter, allowing "user" scripts written in Python to define the actual calculations to be carried out. The C++ core, named ``aftershock``, would essentially be fixed and applicable to all of the reactor models to be analysed. By contrast the Python scripts could be developed and extended by "users", i.e. seismic engineers, as required as new seismic models were developed.

**FIGURE??**

This hybrid architecture was one solution to the trade-off between the need for the best possible performance when accessing and decoding the large quantity of binary data, versus a need for a high-level language for the actual calculations to permit them to be implemented by domain experts who were not software engineers. As usual the choice of language partly depended on user familiarity and there was some experience within the team with Python, both as a scripting language for other analysis packages and as a numerical programming language in its own right using the ``numpy`` and ``scipy`` [Atr03]_ packages.

As the entire binary dataset is too large to fit in memory at once ``aftershock`` operates frame-by-frame, stepping time-wise through the data. At each frame it calls certain functions from the scripts to carry out calculations on the data from that step. The scripts access this data through a simple Python API which returns lists of floats. The scripts may also define functions which are called by ``aftershock`` at the start and end of post-processing for initialisation or output of results. The ``aftershock`` core maintains necessary state from frame-to-frame and also optimises the order in which the results files are processed to minimise the number of passes needed. The ``aftershock`` core is not discussed further in this paper.

The calculation scripts generally make heavy use of the ``ndarrays`` provided by ``numpy`` [Atr02]_ to carry out efficent element-wise operations, although sometimes a more object-orientated approach is appropriate. As the API provided by ``aftershock`` hides all details of the actual binary file formats and how the data is split across files the engineer can concentrate entirely on the actual calculation required.

Plotting Architecture and Features
----------------------------------

Output from the calculation scripts is in some sense not an interesting aspect of post-processing, but it does form the final "product" which the client sees, whereas the rest of the post-processing toolchain is not visible. Tabular output of numerical data is straightforward and is currently handled using the ``csv`` module. However output of graphs and plots is considerably more complex. The previous Excel-based post-processor had exposed some limits to Excel's plotting capabilities, especially for contour-type plots and improvements in the types and format of plots avaiable was highly desirable. With Python as the calculation scripting language a number of plotting packages immediately became options but ``matplotlib`` [Atr04]_ stood out for its wide use, "*publication quality figures*" [Atr04]_ and sheer variety and flexibility of plotting capabilities it provided.

Development of the post-processing toolset could have ended at this point, leaving the script engineer to utilise ``matplotlib`` plots as required. However ``matplotlib's`` versatility comes with a price in complexity and the API is not particularly intuitive. As an example adding adding markers on the Y-axis of a plot - a familiar GUI operation in the existing Excel-based package - might require:

.. code-block:: python

    from matplotlib.ticker import AutoMinorLocator
    <code here>
    plt.yticks(range(0, 100, 20))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))

While this probably appears relatively straightforward to a software engineer there are various levels of abstraction being used here. Requiring the domain experts to spend time learning the details of the matplotlib API did not seem to represent good value for the client. However consideration of the existing post-processor and the new calculation scripts to be developed showed that in fact there were only a handful of separate types of plots required, although each type might be used to present multiple datasets. This made it feasible to provide a domain-specific plotting package, ``afterplot``. This internally uses ``matplotlib``, but provides plotter classes to the user. To create a plot the user  creates an instance of the appropriate class, passing the data to be plotted as well as subsiduary information such as titles as the parameters. All of the plotter classes are derived from a base class ``BasePlot`` which essentially wraps the ``matplotlib.Figure`` object to provide additional functionality. 

Four types of plotters are provided at present:

#. LayerPlot, representing values on a horizontal slice through the model using a contour-type plot with discrete markers.
#. ChannelPlot, representing the geometry of a vertical region through the model in the X-Z and Y-Z planes.
#. TimePlot, representing timehistories as individual series plotted against time.
#. WfallPlot, providing an overview of the frequency distribution of a value at every time-step during an analysis, like a series of stacked histograms.

These classes all use a similar interface for the data to be plotted; all data is inherently four-dimensional as each value is associated with a particular spatial location in the model and a time during the simulated earthquake. In some cases one or more of these dimensions may be "collapsed" by the calculation scripts, for example when plotting  maximum values over time. All plotter classes therefore accept ``numpy`` arrays with up to four dimensions (or ``axes`` in numpy terminology). The meanings and order of the dimensions are standardised, so that different "views" of the same data can easily be generated by passing it to the different plotters. In this way ``afterplot`` defines a set of conventions for data, and the calculation scripts can be thought of as essentially transforming data from the lists of floats provided by ``aftershock`` into four-dimensional arrays for plotting.

The development of a custom plotting package also permitted a significant standardisation of presentation which improves quality overall. For example the interface *requires* axis labels and titles to be defined and grid-lines to be shown on plots, rather than leaving it to the user to adhere to a best-practice guide or relying on review to ensure these have been included. As another example it noted that the default ``matplotlib`` colour scale for contour-type plots was not particularly easy to interprete. It was discovered that this is an area of active research and the WHAT BAR was identified as a STUFF ABOUT CLARITY; ALSO WANT TO SAY SOME STUFFA BOUT HOW WELL FOUNDED IT WAS.

**ADD COLOURBAR EXAMPLES.**

**TODO:** Add something about separation between scripts as provided by architecture.

An alternative GUI methodology
------------------------------
Providing a simple GUI for plots was desirable to help bridge the gap for users between the previous Excel-based tool and the new ``aftershock``-based toolset. The ``matplotlib`` documentation describes two methods of providing a GUI:

1. Using the cross-backend widgets provided by ``matplotlib.widgets``, which are fairly limited.
2. Embedding the ``matplotlib.FigureCanvas`` object directly into the window provided by the selected GUI toolset.

A third option is used for ``afterplot`` which is simplier than the second but allows the richer widgets provided by the selected GUI toolset to be used. The ``matplotlib.pyplot`` framework is intended for convenient scripting use, but as it contains an internal state machine it is generally more appropriate to use the ``matplotlib`` API directly in packages wrapping ``matplotlib``. However the ``plyplot.figure()`` function can be used to handle all of the initial set-up of the GUI, with additional widgets then inserted using the GUI toolset's manager. The below demonstrates the approach with the ``TkAgg`` backend used in ``aftershock`` by adding a button to the ``Figure`` object:

.. code-block:: python

    import Tkinter as Tk
    from matplotlib import pyplot
    class Plot(object):
        def _init__(self):
            self.figure = pyplot.figure()
            toolbar = self.figure.canvas.manager.toolbar
            window = self.figure.canvas.manager.window
            btn_next = Tk.Button(master=window,
                         text='next', command=self._next)
            btn_next.pack(side=Tk.LEFT)
            self.figure.show() ## CHECK THIS

Immutable data and flexible presentation
----------------------------------------
**TODO** Match between GUI and API: concept of data and presentation.

A key consideration in the design of ``afterplot`` is that some aspects of a plot should be modifiable after creation, and some aspects should not be.  For example the title of a plot should not be changeable, as this defines what the data shows, but the colour ranges on a contour-type plot will often need adjustment for clarity. In ``afterplot`` there is therefore a distinction made between *data* and its *presentation*. Plotter classes may provide methods or parameters to enable aspects of the presentation to be changed by the calculation script. However it was recognised 

Each plotter class may define both a GUI interface and an API which mirrors the same functionality, allowing aspects of the plot to be controlled interactively or via the calculation script. What functionality provided by the plotter's GUI and API arises from the central philosopy of ``afterplot``, which is to separate the calculation of *values* from the *presentation* of those values; the former must be tightly controlled whereas flexibility for the latter is desirable. For example, the data shown on a specific contour plot is defined entirely by the sequence of operations in the relevant calculation script, and should not be modifyable. However the color range to be used is initially indeterminate - the calculation script may set some sensible defaults (e.g. max and min of the plotted data) but what values are most appropriate will depend partly on how the plot appears with the specific data from that model.

Storing and Restoring Plots
---------------------------

Saving plots as static images is provided by methods on ``matplotlib's`` ``Figure`` objects. However once a ``Figure`` window has been closed there is no way to regenerate it apart for re-running the entire script which created it. As a complete post-processing run might take several hours to complete, re-running it simply to change presentational aspects such as a colour range was clearly not ideal. The ``baseplot`` class therefore provides additional functionality to all to enable an entire plotter instance including its GUI to be stored to disk and later restored to a new interactive GUI. A simplified description of the process is as follows:

**Storing**:

#. Create a plot instance:

    .. code-block:: python

        orig_plotter = PlotClass(args, kwargs)

#. In the ``BasePlot`` superclass, store the ``*args`` and ``**kwargs`` used to create the plot instance on the instance - these will include one or more ``ndarrays`` containing the actual data to be plotted:

    .. code-block:: python

        def __new__(cls, *args, **kwargs):                
            obj = object.__new__(cls)
            obj._args, obj._kwargs = args, kwargs
            return obj
        
#. Obtain a type object:

    .. code-block:: python

        t_plotter = type(orig_plotter)

#. Pickle the type object, args and kwargs into a file.

**Restoring**:

#. Unpickle the type object, ``args`` and ``kwargs`` from the file
#. Call the type object to create a new instance, passing it the unpickled ``args`` and ``kwargs``:

    .. code-block:: python

        new_plotter = TypeObj(*args, **kwargs)

The benefits of this approach are that:

- The restoring code does not need to know anything about the plot class at all, therefore it works for any plot class.
- The storing code only needs to be able to retrieve the args and kwargs, hence it can be implemented by ``BasePlot`` and storing/restoring “magically” works for all derived classes.

The major complication not shown in the simplifed code above is that ideally storing and restoring should be totally insensitive to whether parameters have been specified as positional or named arguments. Therefore the ``__new__()`` method of the ``BasePlot`` superclass has to use the information provided by ``inspect.getargspec()`` to convert all arguments to a dictionary of name:value, and stores/restores them as ``**kwargs``.

With this method the only interface which storing and restoring knows about is the plotter class’s arguments. This is simple and quite robust to changes in the plotter class as code can be added to handle any depreciated parameters if the signature changes. It also means that if stored plots are restored by a later version of ``afterplot`` any added functionality provided by the updated plotter class will automatically be available to the restored plot.

**TOD0:** add some comment about figures now being pickleable?

Traceability
------------
**TODO:** QA and traceability
The ``baseplot`` class also enables traceability of data on each plot. QA objects. Introspection/stack. Imports.

There is one way in which a restored plot should be different from a “live” original: the “live” plot has associated QA info (actually generated automatically by BasePlot) and this should be stored and restored.  To do this:
We require derived plot classes to take a “secret” argument _qainfo=None.

When BasePlot is __init__ed, if this is None we generate “live” qa info as a dictionary.
On storing, we update the plot’s _qainfo parameter with this dictionary
On restoring, BasePlot’s __init__ can use the info which is now in this parameter to provide the qa info.


Lessons Learnt
--------------

**TODO:**

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


