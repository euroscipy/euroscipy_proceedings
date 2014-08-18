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

Nuclear power in the UK is provided by a fleet of Advanced Gas-cooled Reactors (AGRs) which became operational in the 1970's. These are a second generation reactor design and have a core consisting of layers of interlocking graphite bricks, Figure :ref:`agrcore`, which act to slow neutrons from the fuel to sustain the fission reaction. Although the UK does not regularly experience significant earthquakes it is still necessary to demonstrate that the reactors could be safely shut-down if a severe earthquake were to occur.

The response of the graphite core to an earthquake is extremely complex and a series of computer models have been developed to simulate the behaviour. These models are regularly upgraded and extended as the cores change over their lives to ensure that the relevant behaviours are included. The models are analysed using the commercial Finite Element Analysis code LS-DYNA. This provides predicted positions and velocities for the thousands of graphite bricks in the core during the simulated earthquake.

By itself this raw data is not particularly informative, and a complex set of post-processing calculations is required to help engineers to assess aspects such as:

- Can the control rods still enter the core?
- Is the integrity of the fuel maintained?

This post-processing converts the raw position and velocity data into parameters describing the seismic performance of the core, assesses these parameters against acceptable limits, and presents the results in tabular or graphical form.

This paper describes a recent complete re-write of this post-processing toolset. It seeks to explore some of the software and architectural decisions made and examine the impact of these decisions on the engineering users.

.. figure:: figure1.png
   :scale: 20%

   Detail of AGR core :label:`agrcore`

Background
----------

The LS-DYNA solver produces about 120GB of binary-format data for each simulation, split across multiple files. The existing post-processing tool was based on Microsoft Excel, using VBA to decode the binary data and carry out the required calculations and Excel's graphing capabilities to plot the results. The original design of the VBA code was not particularly modular and its complexity had grown signficantly as additional post-processing calculations were included and to accomodate developments in the models themselves. In short, there was signficant "technical debt" [Cun92]_ in the code which made it difficult to determine whether new functionality would adversely impact the existing calculations.

The start of a new analysis campaign forced a reappraisal of the existing approach as these issues meant there was low confidence that the new post-processing features required could be developed in the time or budget available. The following requirements were identified as strongly desirable in any new post-processing tool:

- A far more modular and easily extensible architecture.
- More flexible plotting capabilties.
- A high-level, modern language to describe the actual post-processing calculations; these would be implemented by sesimic engineers.
- Better performance; the Excel/VBA post-processor could take **X** hours to complete which was inconvenient.
- Possibility of moving to a Linux platform later, although starting initial development on Windows; this would allow post-processing to be carried out on a future Linux analysis server to streamline the workflow and allow access to more powerful hardware.

A re-write from scratch would clearly be a major undertaking and was considered with some trepidation and refactoring the existing code would have been a more palatable first step. However futher investigation convinced us that this would not progress a significant distance towards the above goals as the Excel/VBA platform was simply too limiting.

Overall Architecture
--------------------

An initial feasibility study lead to an architecture with three distinct parts:

#. A central C++ core, ``aftershock``, which handles the binary I/O and contains an embedded Python 2.7 interpreter.
#. A set of Python "calculation scripts" which define the actual post-processing calculations to be carried out.
#. A purpose-made Python plotting package ``afterplot`` which is based on ``matplotlib`` [Hun07]_.

As the entire binary dataset is too large to fit in memory at once the ``aftershock`` core operates frame-by-frame, stepping time-wise through the data. At each frame it decodes the raw binary data and calls defined functions from the calculation scripts which have been loaded. These scripts access the data for the frame through a simple API provided by ``aftershock`` which returns lists of floats. The actual post-processing calculations defined by the scripts generally make heavy use of the ``ndarrays`` provided by ``numpy`` [Wal11]_ to carry out efficent element-wise operations. As well as decoding the binary data and maintaining the necessary state for the scripts from frame-to-frame, the ``aftershock`` core also optimises the order in which the results files are processed to minimise the number of passes required.

The split between ``afterplot`` and a set of calculation scripts results in an architecture which:

a. Has sufficent performance to handle large amounts of binary data.
b. Has a core which can be reused across all models and analyses.
c. Provides the required high-level language for "users", i.e. the seismic engineers defining the calculations.
d. Hides the complex binary file-format entirely from the users.
e. Enforces modularity, separating the post-processing into individual scripts which cannot impact each other.

With Python selected as the calculation scripting language a number of plotting packages immediately became options. However ``matplotlib`` [Hun07]_ stood out for its wide use, "*publication quality figures*" [Hun07]_ and the sheer variety and flexibility of plotting capabilities it provided. Development of the post-processing toolset could have ended at this point, leaving the script engineers to utilise ``matplotlib`` directly. However ``matplotlib``\'s versatility comes with a price in complexity and the API is not particularly intuitive; requiring seismic engineers to learn the details of this did not seem to represent good value for the client. It was therefore decided to wrap ``matplotlib`` in a package ``afterplot`` to provide a custom set of very focussed plot formats.

Plotting Architecture
---------------------
``afterplot`` provides plotting functionality via a set of plotter classes, with the user (i.e. the engineer writing a calculation script) creating an instance of the appropriate class to generate a plot. All plotter classes inherit from a ``BasePlot`` class. This base class is essentially a wrapper for a ``matplotlib`` ``Figure`` object which represents a single plotting window, plus the ``Axes`` objects which represent the plots or sub-plots this contains.

At present ``afterplot`` provides only four types of plotter, although these are expected to be sufficent for most current requirements:

#. ``LayerPlot``. This represents values on a horizontal slice through the model using a contour-type plot but using discrete markers.
#. ``ChannelPlot``. This represents the 3D geometry of a vertical column in the model by projection onto X-Z and Y-Z planes.
#. ``TimePlot``. This is a conventional X-Y plot, representing time-histories as individual series with time on the X-axis.
#. ``WfallPlot``. **FIXT:** his provides an overview of the frequency distribution of a value at every time-step during an analysis, like a series of **stacked histograms**.

Examples are shown in Figures :ref:`LayerPlot` to :ref:`WfallPlot`.

.. figure:: figure1.png
   :scale: 20%
   :figclass: bht

   LayerPlot example :label:`LayerPlot`

.. figure:: figure1.png
   :scale: 20%
   :figclass: bht

   ChannelPlot example :label:`ChannelPlot`

.. figure:: figure1.png
   :scale: 20%
   :figclass: bht

   TimePlot example :label:`TimePlot`

.. figure:: figure1.png
   :scale: 20%
   :figclass: bht

   WfallPlot example :label:`WfallPlot`

Inherently all post-processed results are associated with a three-dimensional position within the model and a time within the simulation. Some parameters or outputs may collapse one or more of these dimensions, for example if plotting a plan view of peak values through time, maximums are taken over the vertical and time axes creating a set of results with two dimensions. All plotter classes therefore accept ``numpy`` arrays with up to four dimensions (or ``axes`` in numpy terminology). The meanings and order of these dimensions are standardised, so that different "views" of the same data can easily be generated by passing an array to different plotters.

Quality Advantages
------------------
A key advantage of providing a custom plotting package is that best-practice can be enforced on the generated plots, such as the provision of titles or use of gridlines. Another example is that ``afterplot`` provides a custom   diverging colourmap as the default colourmap, based on the comprehensive discussion and methods presented in [Mor09]_. This should be significantly easier to interpret than the default colourmap provided by ``matplotlib`` in most cases.

The plotter classes can also allow alteration of *presentation*, e.g. axis limits, while preventing modification of *data*. Alteration of presentation is provided for by instance methods or GUI controls defined by the plotter classes. Modification of data is prevented simply by the lack of any interface to do this once the relevant array has been passed to the plot instance. This immutability is not intended as a security feature but simplifies quality assurance by limiting where errors can be introduced when altering presentation.

A further quality assurance feature is the capture of traceability data. When a new plot is generated, the ``baseplot`` class traverses the stack frames using the ``inspect`` module to gather information about the paths and versions of calculation scripts and other Python modules used. This data is attached to the plots to assist in reproducing published plots or debugging issues. The use of introspection to capture this data means that this feature does not require any action by the script author.

Interactive GUI
---------------
Providing a simple GUI was considered desirable to bridge the gap for users from the previous Excel-based toolset. The ``matplotlib`` documentation describes two methods of providing a GUI:

1. Using the cross-backend widgets provided in ``matplotlib.widgets``, which are fairly limited.
2. Embedding the ``matplotlib.FigureCanvas`` object directly into the window provided by a specific GUI toolset such as ``Tk``.

An alternative approach is used by ``afterplot`` which is simplier than the second approach but allows the use of the richer widgets provided by specific GUI toolsets. This approach uses the ``plyplot.figure()`` function to handle all of the initial set-up of the GUI, with additional widgets then inserted using the GUI toolset's manager. This is demonstrated below by adding a ``Tk`` button to a ``Figure`` object using the ``TkAgg`` backend:

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
Functionality to save plots to disk as images is provided by ``matplotlib`` via ``Figure.savefig()`` which can generate a variety of formats. However once a ``matplotlib`` ``Figure`` object has been closed there there is no way to regenerate it for interactive use, except for re-running the script which created it. As a complete ``aftershock`` post-processing run might take several hours to complete, this is clearly not ideal when minor presentation changes are required such as altering the limits on an axis. A means to enable an entire plotter instance , including its GUI, to be stored to disk and later restored to a new fully interactive GUI was therefore strongly desirable. While ``Figure`` objects were not pickleable at the time (this has been added in the latest version of ``matplotlib``), following the same approach that the ``pickle`` module uses internally to handle class instances enabled this to be achieved relatively simply.


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

The benefits of this approach are that neither the storing nor restoring code needs to know anything about the actual plot class - hence any plotter derived from ``BasePlot`` inherits this functionality. The only interface which storing and restoring needs to address is the plotter class parameter list. This is simple and quite robust to changes in the plotter class definition as code can always be added to handle any depreciated parameters, meaning that it should essentially always be possible to make stored plots forward-compatible with later versions of ``afterplot``. Additionally, if a plot is restored with a later version of ``afterplot`` any enhanced GUI functionality will automatically be available. For convenience a simple ``cmd`` script and short Python function also allow stored plots to be restored on user's local Windows PCs by simply double-clicking the file. Alternatively plots can be restored by a separate script which then uses the plotter class methods to alter presentational aspects, allowing batch processing of changes such as color bars or line thickness if desired.

One complication omitted from the simplifed code above is that ideally storing and restoring should be insensitive to whether parameters have been specified as positional or named arguments. Therefore the ``__new__()`` method of the ``BasePlot`` superclass uses ``inspect.getargspec()`` to convert all arguments to a dictionary of ``name:value``. Class instances are then actually stored/restored as if all parameters were provided as keyword arguments.

While this approach essentially mirrors how ``pickle`` handles class instances, implementing such complex and robust functionality in such little code is an impressive demonstration of Python's benefits.

Outcomes and Lessons Learnt
---------------------------
The overal architecture has been a success:

- Performance is significantly improved.
- Post-processing can easily be integrated with analysis runs if required.
- Maintainability and extensibility of the calculations has been vastly improved.
- Python and ``numpy`` form a vastly more usable and concise high-language for describing calculations than VBA, allowing engineers to concentrate on the logic rather than limitations imposed by the language.
- The ``aftershock`` core is reusable across different models, saving considerable effort.
- Cross-platform portability to Windows and Linux was achieved without any significant effort for the calculation scripts and plotting module, providing flexibility for future deployment.

However there were a number of challenges, some of which were expected at the outset and some which were not:

*Education and training:* As discussed a key driver for the architecture was that it was intended that the calculation scripts would be written by seismic engineers, as they were the domain experts. Some of these engineers, although not all, were already familiar with Python, often from scripting environoments provided by commercial analysis software. Others were familar with other high-level scripting languages such as VBA. In general users found it relatively simple to pick up and start developing procedural and simple object-orientated Python, although some "Pythonic" features such as generators were less familar. The use of ``numpy`` then required users to learn a third programming paradigm; vectorised element-wise operations. While the basic concepts were easily understood, learning when procedural code with explicit loops or vectorised code is more appropriate requires considerably more experience and guidance. Performance had not previously been critical for most engineers and hence basic optimisation techniques such as moving constant expressions outside of loops were not necessarily obvious. The API for the scientitic Python stack contains some subtleties and inconsistenciess too, for example the three *TODO*

- ``abs()``, ``numpy.abs()``
- ``math.exp()``, ``numpy.exp()``,
- ``math.pi``, ``scipy.pi``, ``numpy.pi``

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

.. [Cun92] W Cunningham. *The WyCash Portfolio Management System*,
           OOPSLA '92 Addendum to the proceedings on object-oriented programming systems, languages, and applications, pp. 29-30.
           http://c2.com/doc/oopsla92.html

.. [Wal11] S. Van Der Walt, S. Chris Colbert, Gaël Varoquaux. *The NumPy array: a structure for efficient numerical computation*,
           Computing in Science and Engineering, 13(2):22-30, 2011.

.. [Hun07] J. D. Hunter. *Matplotlib: A 2D Graphics Environment*,
	       Computing in Science & Engineering, 9(3):90-95, 2007.

.. [Mor09] K. Moreland. *Diverging Color Maps for Scientific Visualization*,
           Proceedings of the 5th International Symposium on Visual Computing, 2009.

