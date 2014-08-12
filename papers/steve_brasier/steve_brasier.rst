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
- A Linux platform; this would allow post-processing to be carried out on the analysis server to streamline the workflow and allow access to more powerful hardware.

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

The plotter classes can also enforce a demarcation between alteration of *presentation*, e.g. color-bar limits, and alteration of *data*. Alteration of presentation is provided for through methods or GUI features defined by the plotter classes. Alteration of data is prevented as there is no interface to the data itself once the relevant array has been passed to the plot instance. This is not a security feature but simplifies quality assurance by limiting where errors could be introduced.

Another quality assurance feature is the provision of traceability data. The ``baseplot`` class traveses the stack frames using the ``inspect`` module when a new plot is generated, gathering information about paths and versions of scripts and modules used. The use of this approach means that no additional effort from the script author is required to gather this information.

Interactive GUI
---------------
Providing a simple GUI was considered desirable to bridge the gap for users from the previous Excel-based toolset. The ``matplotlib`` documentation describes two methods of providing a GUI:

1. Using the cross-backend widgets provided in ``matplotlib.widgets``, which are fairly limited.
2. Embedding the ``matplotlib.FigureCanvas`` object directly into the window provided by a specific GUI toolset, e.g. ``Tk``.

A third option is used by ``afterplot`` which is simplier than the second approach but allows the use of the richer widgets provided by specific GUI toolsets. This approach uses the ``plyplot.figure()`` function to handle all of the initial set-up of the GUI, with additional widgets then inserted using the GUI toolset's manager. This is demonstrated below adding a ``Tk`` button to a ``Figure`` object with the ``TkAgg`` backend:

.. code-block:: python

    import Tkinter as Tk
    # ADD USE
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


Th





-------------------------


x are used to pass the data to plot to all plott is passed to plot classes as has All plot classes have a very similar interface by which data is passed to them. Inherantly provided

However consideration of the existing post-processor and the new calculation scripts to be developed showed that in fact there were only a handful of separate types of plots required, although each type might be used to present multiple datasets. This made it feasible to provide a domain-specific plotting package, ``afterplot``. This internally uses ``matplotlib``, but provides plotter classes to the user. To create a plot the user  creates an instance of the appropriate class, passing the data to be plotted as well as subsiduary information such as titles as the parameters.

All of the plotter classes are derived from a base class ``BasePlot`` which essentially wraps the ``matplotlib.Figure`` object to provide additional functionality. At present four plotter classes are defined:



These classes all use a similar interface for the data to be plotted; all data is inherently four-dimensional as each value is associated with a particular spatial location in the model and a time during the simulated earthquake. In some cases one or more of these dimensions may be "collapsed" by the calculation scripts, for example when plotting  maximum values over time. 

The development of a custom plotting package also permitted a significant standardisation of presentation which improves quality overall. For example the interface *requires* axis labels and titles to be defined and grid-lines to be shown on plots, rather than leaving it to the user to adhere to a best-practice guide or relying on review to ensure these have been included. As another example it noted that the default ``matplotlib`` colour scale for contour-type plots was not particularly easy to interprete. It was discovered that this is an area of active research and the WHAT BAR was identified as a STUFF ABOUT CLARITY; ALSO WANT TO SAY SOME STUFFA BOUT HOW WELL FOUNDED IT WAS. **ADD COLOURBAR EXAMPLES.**

A key consideration in the design of ``afterplot`` control of which aspects of a plot are modifiable after creation. For example the title of a plot defines what the data shows, and therefore should not be changeable, but the colour ranges on a contour-type plot will often need adjustment to clearly show the specific data displayed. In ``afterplot`` there is therefore a distinction made between *data* and *presentation*. The former is "write-once" and provided through the arguments to the plotter class, whereas the plot class may provide GUI controls or API methods to modify the latter.

An alternative GUI methodology
------------------------------

Storing and Restoring Plots
---------------------------

Saving plots as static images is provided by methods of ``matplotlib's`` ``Figure`` objects. However once a ``Figure`` window has been closed there is no way to regenerate it for interactive use except for re-running the script which created it. As a complete ``aftershock`` post-processing run might take several hours to complete, this is clearly not ideal. It was therefore desirable to find a way to enable an entire plotter instance including its GUI to be stored to disk and later restored to a new interactive GUI. ``Figure`` objects were not pickleable at the time and although this has been added in the latest version of ``matplotlib`` pickling the custom GUI described above would still have been problematic. The approach used was therefore as follows:


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

The benefits of this approach are that neither the storing nor restoring code needs to know anything about the actual plot class - hence any plotter derived from ``BasePlot`` inherits this functionality. The only interface for which storing and restoring needs to address is the parameter list. This is simple and quite robust to changes in the plotter class as code can be added to handle any depreciated parameters if the signature changes. It also means that if stored plots are restored by a later version of ``afterplot`` any added functionality provided by the updated plotter class will automatically be available to the restored plot.

One signficant complication omitted from the simplifed code above is that ideally storing and restoring should be totally insensitive to whether parameters have been specified as positional or named arguments. Therefore the ``__new__()`` method of the ``BasePlot`` superclass has to use information provided by ``inspect.getargspec()`` to convert all arguments to a dictionary of ``name:value``, and stores/restores them all as ``**kwargs``.

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


