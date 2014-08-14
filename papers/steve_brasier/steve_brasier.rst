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

A series of computer models have been developed to simulate the behaviour of the reactors during an earthquake. These models are regularly upgraded and extended as the cores change over their lives to ensure that the relevant behaviours are included. The models themselves are analysed using the commercial Finite Element Analysis code LS-DYNA, which predicts positions and velocities for the thousands of graphite bricks in the core during the simulated earthquake.

However engineers seek answers to high-level questions such as:

- Can the control rods still enter the core?
- Is the integrity of the fuel maintained?

To help answer these questions a complex set of post-processing calculations is required. These convert the raw position and velocity data into parameters describing the seismic performance of the core, assess these parameters against acceptable limits, and present the results in tabular or graphical form.

This paper describes a recent complete re-write of this post-processing toolset. It seeks to explore some of the software and architectural decisions made and examine the impact of these decisions on the engineering users.

Background
----------

The LS-DYNA solver produces about 120GB of binary-format data for each simulation, split across multiple files. The original post-processing tool was written in Microsoft Excel using VBA to decode the binary data and carry out the required calculations. The results were output to workbooks and plotted using Excel's graphing capabilities. The original design was not particularly modular and the technical debt [Atr01]_ had grown signficantly as the post-processor became more complex due to changes in the models themselves and additional requirements, making it difficult to determine whether changes would impact existing code.

The start of a new analysis campaign forced a reappraisal of the existing approach as these issues meant there was low confidence that the new post-processing features required could be developed in the time or budget available. The following requirements were identified as strongly desirable in any new post-processing tool:

- A far more modular and easily extensible architecture.
- More flexible plotting capabilties.
- Signficantly faster; the Excel/VBA post-processor could take **X** hours to complete which was inconvenient.
- Possibility of moving to a Linux platform later, although starting initial development on Windows; this would allow post-processing to be carried out on a future Linux analysis server to streamline the workflow and allow access to more powerful hardware.

A complete re-write was considered with some trepidation as it was clear that this would be a major undertaking. A more palatable first step would have been refactoring the existing code. However futher investigation convinced us that this would not progress a significant distance towards the above goals as the Excel/VBA platform was simply too limiting.

Overall Architecture
--------------------

An initial feasibility study lead to an architecture which has:

#. A central C++ core, ``aftershock``, which handles the binary I/O and contains an embedded Python 2.7 interpreter.
#. A set of Python "calculation scripts", defining the actual post-processing calculations to be carried out.
#. A Python plotting package ``afterplot``, based on ``matplotlib``.

**FIGURE??**

As the entire binary dataset is too large to fit in memory at once the ``aftershock`` core operates frame-by-frame, stepping time-wise through the data. At each frame it decodes the raw binary data and calls defined functions from the calculation scripts which have been loaded. These scripts access the raw data for this frame through a simple API which returns lists of floats, and carry out the required calculations, generally with heavy use of the ``ndarrays`` provided by ``numpy`` [Atr02]_ to carry out efficent element-wise operations. As well as decoding the binary data, the ``aftershock`` core optimises the order in which the results files are processed to minimise the number of passes required and maintains necessary state for the scripts from frame-to-frame.

The split between ``afterplot`` and a set of calculation scripts results in an architecture which:

a. Has sufficent performance to handle large amounts of binary data, and has a core which can be reused across all models and analyses.
b. Allows users, i.e. seismic engineers, to define the calculations required in a high-level language with no knowledge of the raw binary format.
c. Separates the post-processing into individual scripts which cannot impact each other, enforcing modularity.

With Python selected as the calculation scripting language a number of plotting packages immediately became options but ``matplotlib`` [Atr04]_ stood out for its wide use, "*publication quality figures*" [Atr04]_ and the sheer variety and flexibility of plotting capabilities it provided. Development of the post-processing toolset could have ended at this point, leaving the script engineers to utilise ``matplotlib`` directly as required. However ``matplotlib's`` versatility comes with a price in complexity and the API is not particularly intuitive; requiring seismic engineers to learn the details of this did not seem to represent good value for the client. It was therefore decided to wrap ``matplotlib`` in a package ``afterplot`` to provide a custom set of very focussed plot formats.

Plotting Architecture
---------------------
``afterplot`` provides each type of plotting functionality as a separate plotter class, with the user (i.e. the engineer writing a calculation script) creating an instance of this class to generate a plot. All plotter classes inherit from a ``BasePlot`` class **FIGURE**. This base class is essentially a wrapper for a ``matplotlib`` ``Figure`` object (which represents a single plotting window in ``matplotlib``) plus the ``Axes`` objects which represent the plots or sub-plots this contains.

At present ``afterplot`` provides only four types of plotter, although these are sufficent for most requirements:

#. ``LayerPlot``. This represents values on a horizontal slice through the model using a contour-type plot but using discrete markers.
#. ``ChannelPlot``. This represents the geometry of a vertical column in the model in the X-Z and Y-Z planes.
#. ``TimePlot``. This is a conventional X-Y plot, representing time-histories as individual series with time on the X-axis.
#. ``WfallPlot``. This provides an overview of the frequency distribution of a value at every time-step during an analysis, like a series of **stacked histograms**.

Inherently all post-processed results have some associated spatial position within the model and some associated time within the simulation. For some parameters one or more of these dimensions may be collapsed, e.g. in the case of a 2D plan-view of peak values through time, maximums are taken over the vertical and time axes. All plotter classes therefore accept ``numpy`` arrays with up to four dimensions (or ``axes`` in numpy terminology). The meanings and order of the dimensions are standardised, so that different "views" of the same data can easily be generated by passing it to the different plotters. In this way ``afterplot`` defines a set of conventions for data, and the calculation scripts can be thought of as essentially transforming data from the lists of floats provided by ``aftershock`` into four-dimensional arrays for plotting.

Quality Advantages
------------------
A key advantage of providing a custom plotting package is that best-practice can be enforced on the author of the calculation script, for example the provision of titles or use of gridlines. <<COLORBAR EXAMPLE>>.

The plotter classes can also enforce a demarcation between alteration of *presentation*, e.g. color-bar limits, and alteration of *data*. Alteration of presentation is provided for through methods or GUI features defined by the plotter classes. Alteration of data is prevented as there is no interface to the data itself once the relevant array has been passed to the plot instance. This is not intended as sa security feature but simplifies quality assurance by limiting where errors could be introduced.

Another quality assurance feature is the provision of traceability data. The ``baseplot`` class traveses the stack frames using the ``inspect`` module when a new plot is generated, gathering information about paths and versions of scripts and modules used. The use of this approach means that no additional effort from the script author is required to gather this information.

Interactive GUI
---------------
Providing a simple GUI was considered desirable to bridge the gap for users from the previous Excel-based toolset. The ``matplotlib`` documentation describes two methods of providing a GUI:

1. Using the cross-backend widgets provided in ``matplotlib.widgets``, which are fairly limited.
2. Embedding the ``matplotlib.FigureCanvas`` object directly into the window provided by a specific GUI toolset, e.g. ``Tk``.

An alternative approach is used by ``afterplot`` which is simplier than the second approach but allows the use of the richer widgets provided by specific GUI toolsets. This approach uses the ``plyplot.figure()`` function to handle all of the initial set-up of the GUI, with additional widgets then inserted using the GUI toolset's manager. This is demonstrated below by adding a ``Tk`` button to a ``Figure`` object using with the ``TkAgg`` backend:

.. code-block:: python

    import Tkinter as Tk
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib import pyplot
    class Plot(object):
        def _init__(self):
            self.figure = pyplot.figure()
            toolbar = self.figure.canvas.manager.toolbar
            window = self.figure.canvas.manager.window
            btn_next = Tk.Button(master=window,
                         	 text='next',
				 command=self._next)
            btn_next.pack(side=Tk.LEFT)
            self.figure.show()

Store and Restore
-----------------
As noted above plotter classes provide for the plot presentation to be altered after the plot has been created through instance methods or GUI features. Plots can then be saved to disk as images in a variety of file formats using functionality provided by ``matplotlib`` via ``Figure.savefig()``.

However once the ``Figure`` object has been closed there there is no way to regenerate it for interactive use except for re-running the script which created it. As a complete ``aftershock`` post-processing run might take several hours to complete, this is clearly not ideal when minor presentation changes are required, for example altering the limits on an axis. A means to enable an entire plotter instance - including its GUI - to be stored to disk and later restored to a new fully interactive GUI was therefore strongly desirable. While ``Figure`` objects were not pickleable at the time (this has been added in the latest version of ``matplotlib``), following the same basic approach which ``pickle`` internally uses to handle class instances enabled this to be achieved relatively simply as follows:

**Storing:**

#. When a plot instance is created, the ``__new__`` method of the ``BasePlot`` superclass binds the  supplied ``*args`` and ``**kwargs`` to attributes on the plotter instance - these will include one or more ``ndarrays`` containing the actual data to be plotted.
#. To store the instance, first a ``type`` object is obtained, then this and the ``*args`` and ``**kwargs`` are pickled.

Simplified code for the ``BasePlot`` class implementing this:

.. code-block:: python

	class BasePlot(object):
	    def __new__(cls, *args, **kwargs):
		    obj = object.__new__(cls)
		    obj._args, obj._kwargs = args, kwargs
		    return obj
	    def store(self, path):
		    data = (type(self), self._args,
		            self._kwargs)
		    with open(path, 'w') as pkl:
		        pickle.dump(data, pkl)

**Restoring**:

#. The type object, ``args`` and ``kwargs`` are unpickled from the file.
#. The type object is called to create a new instance, passing it the unpickled ``args`` and ``kwargs``.

Simplfied restoring code:

.. code-block:: python

    with open(path, 'r') as pkl:
        t_plt, args, kwargs = pickle.load(pkl)
    new_plotter = t_plt(*args, **kwargs)

The benefits of this approach are that neither the storing nor restoring code needs to know anything about the actual plot class - hence any plotter derived from ``BasePlot`` inherits this functionality. The only interface which storing and restoring needs to address is the plotter class parameter list. This is simple and quite robust to changes in the plotter class definition as code can always be added to handle any depreciated parameters, meaning that it should essentially always be possible to make stored plots forward-compatible with later versions of ``afterplot``. Additionally, if a plot is restored with a later version of ``afterplot`` any enhanced GUI functionality will automatically be available. For convenience a simple ``cmd`` script and short Python function also allow stored plots to be restored on user's local Windows PCs by simply double-clicking the file. Alternatively plots can be restored and by a separate script which then uses the plotter class methods to alter presentational aspects, allowing batch processing of changes such as color bars or line thickness if desired.

One signficant complication omitted from the simplifed code above is that ideally storing and restoring should be totally insensitive to whether parameters have been specified as positional or named arguments. Therefore the ``__new__()`` method of the ``BasePlot`` superclass uses ``inspect.getargspec()`` to convert all arguments to a dictionary of ``name:value`` and class instances are actually stored/restored as if all parameters were provided as keyword arguments.

While this approach essentially mirrors how ``pickle`` handles class instances, implementing such complex and robust functionality in such little code is an impressive demonstration of Python's benefits.

Outcomes and Lessons Learnt
---------------------------
The architecture of an ``aftershock`` core and a set of separate calculation scripts has been a success:

- Performance has been significantly improved and post-processing can easily be integrated with analysis runs if required.
- Maintainability and extensibility of the calculations has been vastly improved.
- Python + numpy vastly better language for numerical calcs than VBA with very simplistic array support, can get on with the difficult bits.
- The ``aftershock`` core is being re-used across different models.
- Cross-platform; entire stack running on Windows and Linux.

Challenges:
- Education requirements: Teach users Python. Familar with other high-level scripting languages (e.g. VBA or DSL for scripting analysis software) but still generators, etc quite new. Then teach users numpy element-based thinking - very hard.
- Still requires thinking about performance. e.g. move constants outside of loops. Some subtleties too - e.g. why sum() or numpy.sum() [bad example]
- Lack of brackets not a problem, but use of signficant whitespace was!
- Installation: Installation of Python/numpy/scipy difficult on non-administrator Windows machines.
- Embedding 2.7 interpreter signficantly difficult due to compiler version issues, although outside scope of paper to discuss.

Plotting:
- More mixed bag?
- Major problem was lack of resouces with appropriate skill level to carry out checking and code review: GUI programming and some relatively sophisticated approaches e.g. decorators used internally. Has held up wider use of ``afterplot``.
- Matplotlib GUI isn't really that great; would really help if GUI functionality to modify basic style elements of plots was included (as it is in ``Spyder`` using the ``Qt4Agg`` backend) ideally with an option to selectively disable these.


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


