:author: Thomas Cokelaer
:email: cokelaer@ebi.ac.uk
:institution: European Bioinformatics Institute (EMBL-EBI)

:author: Julio Saez-Rodriguez
:email: saezrodriguez@ebi.ac.uk
:institution: European Bioinformatics Institute (EMBL-EBI)


--------------------------------------------------------
Diving into Human Cells with CellNOpt and BioServices
--------------------------------------------------------

.. class:: abstract

    Systems biology is an inter-disciplinary field that studies systems of biological components at different scales, which may be molecules, cells or entire species. In particular, systems biology is used for understanding functional deregulations within human cells (e.g., cancers). In this context, we present several python packages linked to **CellNOptR** (R package), which is used to build predictive logic models of signaling networks by training networks (derived from literature) to signaling (phospho-proteomic) data. The first package (**cellnopt.wrapper**) is a wrapper based on RPY2 that allows a full access to CellNOptR functionalities within Python. The second one (**cellnopt.core**) was designed to ease the manipulation and visualisation of data structures used in CellNOptR, which was achieved by using Pandas, NetworkX and matplotlib. System biology also makes extensive use of web resources and services. We will give an overview and status of **BioServices**, which allows one to access programmatically to web resources used in fife science and how it can be combined with CellNOptR.





.. class:: keywords

   systems biology, CellNOpt, BioServices, graph/network theory,
   web services, signalling networks, logic modelling, optimisation


Context and Introduction
--------------------------

System biology studies systems of biological components at different scales, which may be molecules, cells or entire species. It is a recent term that emerged in the 2000s [IDE01]_, [KIT02]_ to describe an inter-disciplinary research field in biology. In human cells, which will be considered in this paper, systems biology helps to understand functional deregulations inside the cells that are induced either by gene mutations (in the  nucleus) or extracellular signalling. Such deregulations may lead to the apparition of cancers or other diseases.

Cells are constantly stimulated by extracellular signalling. Receptors on the cell surface may be activated by those signals thereby triggering a chain of events inside the cell (signal transduction). These chain of events also called **signalling pathways** depends on many parameters such as the cell type (e.g., blood, liver). Depending on the response, the cell behaviour may be altered (shape, gene expression, etc.). These pathways are dense network of interactions between proteins that propagate the external signals down to the gene expression level (see Figure :ref:`fig:overview`).

The interactions between proteins are complex. For simplicity, we consider relationship to be of activation or inhibition types. Complex of proteins may also be formed, which means that several type of proteins may be required to activate or inhibit another protein. A classical example of pathway is the so-called P53 pathway (see Figure :ref:`fig:overview`). In a normal cell the P53 protein is inactive (inhibited by the MDM2 protein). However, upon DNA damage or other stresses, various pathways will lead to the dissociation of this P53-MDM2 complex, thereby activating P53. Consequently, P53 will either prevent further cell growth to allow a DNA repair or initiate an apoptosis (cell death) to discard the damaged cell. A deregulation of the P53 pathway would results in an uncontrolled cell proliferation, such as cancer.


.. figure:: signal_transduction.png
    :scale: 20%

    Overview of signal transduction pathways. The cell boundary (thick orange line) has receptors to external signals (e.g., survival factors IGF1). These signals propagate inside the cell via complex networks of protein interactions (e.g., activation and inhibition) down to the gene expression level inside the cell nucleus (red thick line). Image source: `wikipedia <http://en.wikipedia.org/wiki/File:Signal_transduction_v1.png>`_.     :label:`fig:overview`

It is essential to understand the behabiour of such networks to build logical model of signalling pathways that can predict novel therapeutic solutions [SAEZ]. In order to understand these networks, experimental protocol implies to perturb the cell by stimulating the cell receptors with **stimuli** and/or adding **drugs** that would inhibit the normal behaviour of some proteins. These **perturbation data** may then be used together with the networks to build logical models.
There are different type of experiments from mass-spectrometry (many proteins but few perturbations) to antibody based experimental design (few proteins but more time points and perturbations).

Yet, building logical models in the context of signalling pathways is challenging. Indeed, networks formed by protein interactions are highly complex:

- the number of protein types is large (about 20,000 in human cells)
- signalling pathways are context specific and cell-type specific ; there are about 200 human cell types (e.g., blood, liver)
- proteins may have different dynamic (from a few minutes to several hours)


The software CellNOptR [CNO12]_ provides tools to perform logic modelisation at the protein level starting from complex network of protein interactions and perturbation data sets. The core of the software consist in (1)
transforming protein network into logical networks (2) simulate the flow of
signalling within the graph using for instance a boolean formalism (3) compare real biological data with the simulated data. The software is essentially  an optimisation problem, which can be solved by various algorithms (e.g., genetic algorithm). The final goal consists in providing a protein network that is a faithful representation of the actual interactions

In this paper will only consider a boolean logic formalism although more complex ones (e.g., differential equations) are available [MAC12]_.

Although CellNOpt is originally written with the R language, which may seem
off topic, we will focus on two python packages that are related to it.
The first one called **cellnopt.wrapper** is a Python wrapper that have been written using the RPy2 package to enable full access to the R package from a python perspective.

The second python package linked to CellNOptR is **cellnopt.core**. This is a python package that combines Pandas [MCK10]_, NetworkX [ARI08]_ and [HUN07]_ to buildup a software dedicated to the manipulation of network of proteins and perturbation data sets that are the input of CellNOptR packages.


The other important aspect in system biology and when using CellNOptR is the ability to retrieve information from web resources and databases. Bioinformatics make use of a plethora of online resources (e.g., databases of gene identifiers), which are highly specialised. Resources available via server-side applications span the entire spectrum of bioinformatics (e.g., genomics, sequence analysis) and can be accessed to programmatically via web services (based either on SOAP or REST technologies)
In the context of logical modeling, resources of importance are signalling pathways (e.g., Wiki Pathway [WP09]_) and retrieval of information about proteins (e.g., UniProt [UNI14]_). In order to help us in this tasks, we developed BioServices [COK13]_ that provides a Python library to programmaticaly access to web services.

In the first part of this paper, we will briefly present the data structure used in CellNOptR and a typical pipeline. We will then demonstrates how **cellnopt.wrapper** and **cellnopt.core** can enhance user experience. In the second part,  we will quickly present **BioServices** and give an update on its status and future directions.




CellNOpt
------------

CellNOptR [CNO12]_ is a R package used for creating logic-based models of signal
transduction networks using different logic formalisms but we consider boolean logic only here below. It uses information on signaling pathways encoded as a Prior Knowledge Network (PKN), and trains it against high-throughput biochemical data to create cell-specific models. The training is performed with optimisation such as genetic algorithms. For more details see also the `www.cellnopt.org <www.cellnopt.org>`_ website.

Input data structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Network and logic model
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: PKN.png
    :scale: 35%

    Prior Knowledge Network (PKN) example. Colored nodes represent (i) stimuli (green, generally on cell surface or close to), (ii) measured proteins (blue), (iii) inhibited protein by a drug (red), (iv) silent nodes (white and grey) that do not affect the logic of the model if removed. Black edges represent activation and red edges represent inhibition. :label:`figpkn`




The PKNs gives a list of known relationship between proteins. It is built from literature or expertise from experimentalists.  One way to store the PKNs is to use  the SIF format, which is encode relationship between proteins within a tabulated-separated values file. Consider this example::

    Input1 1 Interm
    Input2 1 Interm
    Interm 1 Output

Each row is a reaction where the first element is the input protein, the third element is the affected protein, and the middle  element is the relationship, where 1 means actiation and -1 means inhibition. A visual reprensentation of this example is shown in Figure :ref:`fig:cnoproc`.; a more realistic example is provided in Figure :ref:`figpkn`. Such networks are directed graph where edges can be either activation (represented by normal black edge) or inhibition (represented by tee red edge).

In the SIF file provided above, only OR relationships are encoded: for example, the protein *Interm* is activated by *Input1* OR *Input2*.  Note that the *Interm* protein has 2 inputs. *Input1* may active *Interm* OR *Input2* may activate *Interm*. Yet, within cells, complex of proteins do exists, which means AND relationship are possible. Therefore AND relationship are required in such networks. Trasnforming the input PKN into logical model means that AND gates have to be added as soon as a protein has several inputs.

The prior knowledge network and logil model can be be used together with the data to figure out if they are compatible. This can be achieved within CellNOptR by training the model to the data measured on those proteins. Let us first look at the data structure.



DATA
^^^^^^^^

The data used in CellNOpt is made of measurements of protein activities upon different perturbations. A perturbation is an experiment made of stimuli (on cell receptor) and inhibition (caused by a drug). Such data is encoded in a format called MIDAS (see [MIDAS]_ for details), which is a CSV file format. Each measurement is made of one protein, at a given time upon a specific experiment (set of stimuli and inhibition). Figure :ref:`figmidas` gives an example of a MIDAS data file together with further explanations.



Training
^^^^^^^^^^^^

Once a PKN and a data sets are available, the PKN is transformed into a logic model by adding AND gates (if needed) and simplifying the network by removing nodes/proteins that do not change the logic of the network (see Figure :ref:`fig:cnoproc`).

The training of the prior knowledge model to the data is performed by minimising an objective function encoded as follows:

.. math::

    \theta(M) = \theta_f(M) + \alpha \theta_s(M)

where

.. math::

    \theta_f(M) = \frac{1}{N} \sum_{k=1}^K \sum_{e=1}^E \sum_{t=1}^T  (X_{k,e,t} - X_{k,e,t}^s)^2

where :math:`e` is an experiment, :math:`k` a measured protein and  :math:`t` a time point. The total number of points is :math:`N=E.K.T` where E, K and T are the total number of experiments, measured proteins and time points, respectively. :math:`X_{k,e,t}` is a measurement and :math:`X^s_{e,k,t}` the corresponding simulated measuremet returned by the simulated model :math:`M`. A model :math:`M` is a subset of the initial PKN where edges have been pruned (or not).
Finally, :math:`\theta_s` penalises the model size by summing across the number of inputs of each edge and :math:`\alpha` is a tunable parameter.


.. figure:: MIDAS.png

    MIDAS data set visualised with cellnopt.core. Each row correspond to an experiment, that is a combination of stimuli and inhibitors (drug). An experiment is summarized by the two right panels where the xaxis contains the name of the stimuli and inhibitors and a black square means stimuli (or inhibitor) is on. The right panel contains the measurements made on each proteins of interests over time. For example, the left bottom box gives us about 15 time points for the proiten AP1 in the experimental conditions where EGF and TNFA receptors are stimulated on RAF1 is inhibited. The color in the boxes indicates the rough trend othe time series (e.g., green means activation is going up, the alpha transparency indicates the strength of the signals.). :label:`figmidas`



cellnopt.wrapper
~~~~~~~~~~~~~~~~~~~~

CellNOptR provides a set of R packages available on BioConductor website, which guarantees a minimal quality. Packages are indeed multi-platform and tested regularly. However, the functional approach that has been chosen limits somehow the
user experience. In order to be able to use the Python language, we therefore decided to provide also a python wrapper. To do so, we used the RPY2 package. The cost for the implementation is reasonable: considering that the R packages in CellNOptR relies on about 16,000 lines of code (in R) and another 4,000 in C, the final python wrappers required  2000 lines of code including the documentation.

In addition to the wrappers, we also implemented a set of classes (or for each of the logical formalism) that encapsulate the R functions. The results is that **cellnopt.wrapper** provides a full access to the entire CellNOptR packages with an objected oriented approach.

Let us see how it works in pratice. Here is a classical R pipeline that reads input data and runs an optimisation (genetic algorithm) to finally plot some diagnostics plots to see the quality of the final fit:

.. code-block:: r
    :linenos:

    library(CellNOptR)
    pknmodel = readSIF(CNOdata("PKN-ToyMMB.sif"))
    cnolist = CNOlist(CNOdata("MD-ToyMMB.csv"))
    res = gaBinaryT1(cnolist, pknmodel)
    plotFit(res)
    cutAndPlotResultsT1(pknmodel, res$bString, NULL, cnolist)

On the first line, we load the library. On the second and third lines, we read the
PKN and data set. The optimisation is performed with a genetic algorithm (line 4). We plot the status of the objective function over time (line 5) and finally look at the individual fits (see Figure :ref:`figfit` for an example). Here below is the same code in Python using **cellnopt.wrapper**

.. code-block:: python
    :linenos:

    from cellnopt.wrapper import CNORbool
    b = CNORbool(cnodata("PKN-ToyMMB.sif"),
        cnodata("MD-ToyMMB.csv"))
    b.gaBinaryT1()
    b.plotFit()
    b.cutAndPlotResultsT1()

As you can see, lines in these two code snippets are equivalent. The size of the code is similar but the main difference appear to be that the first code is functional and the second is object oriented.

The interest of the second code is that it is now pure python. You can derive new classes easily, introspect the data and more importantly use python to further manipulate the results. Because object oriented is used in place of functional programming, the user interface is also simplified (no need to provide parameters anymore).

.. figure:: fit.png

    Fitness plot between the data and the best logical model. The plot is generated by CellNOptR via **cellnopt.wrapper**. See text for code snippet and more details. :label:`figfit`

.. code-block:: python
    :linenos:

    from cellnopt.core import *
    pkn = cnodata("PKN-ToyPB.sif")
    data = cnodata("MD-ToyPB.csv")
    c = CNOGraph(pkn, data)
    c.plot()

**cellnopt.wrapper** is available on
`Pypi page <http://pythonhosted.org/cellnopt.wrapper>`_ and updated together with new releases of CellNOptR.

Note, that **cellnopt.wrapper** is designed to provide a full access CellNOptR functionalties, and therefore does not provide any additional functionalities.

Yet, for end-users, it is often required to manipulate the input data in many different ways. On the network side, quick visualisation, merging of networks are often required before any training. On the data side, is it quite common to wish to removed experiments of data on the fly before training. This was the reason to develop another package dedicated to the manipulation of the data structures used in CellNOptR.

cellnopt.core
~~~~~~~~~~~~~

PKN
^^^^^^^

We are now giving an overview of **cellnopt.core** that is dedicated to the manipulation of networks and data sets compatible with CellNOptR. This is a
pure python implementation.

Let us come back on the simple SIF model presented earlier and let us see how it
can be created and visualised in Python with **cellnopt.core**. This package
provides a dedicated class to manipulate SIF file but also a  more generic and powerful class called **CNOGraph**,  which is derived from the DiGraph class available in NetworkX.

.. figure:: cellnopt_preprocess.png
    :scale: 35%

    Toy example of a logic model (left). Logical and gates are represented with the    small circles (middle).  Logic-based models may be also compressed so as to simplify the network (right panel). Here the white node is not required. Removing it does not affect the logic in the network. :label:`fig:cnoproc`

First, les us build the toy example shown in the first section. Although you can add nodes and edges using NetworkX methods, you can also simply add reactions as follows:

.. code-block:: python
    :linenos:

    from cellnopt.core import CNOGraph
    c= CNOGraph()
    c.add_reaction("Input2=Interm")
    c.add_reaction("Input1=Output")
    c.add_reaction("Interm=Output")
    c._signals = ["Output"]
    c._stimuli = ["Input1", "Input2"]
    c.plot()

where the = sign indicates an activation (inhibition are encode with !=). The results is shown in Figure :ref:`fig:cnoproc` (left panel). By default all nodes are colored in white but list of stimuli , inhibitors or signals may be provided manually (line 6,7).

The training of the model to the data may also require to add AND gates, which is performed as follows:

.. code-block:: python
    :linenos:

    c.expand_and_gates()

resulting in the model shown in Figure :ref:`fig:cnoproc` (middle panel). You can also compress the network to remove nodes that do not change the logic (see Figure :ref:`fig:cnoproc` , right panel)::

    c.compress()

One of the interest of the **CNOGraph** class is that you have also access to all DiGraph methods and algorithm available in Networkx.

Coming back on the first network (without expansion or compression), an additional nice feature implemented is the split/merge methods, which are very useful
in the context of mass-spectrometry or simply when variants of the same protein
are present in the data:

.. code-block:: python
    :linenos:

    c.split_node("Interm", ["Interm1", "Interm2"])
    c.plot()


Doing this split/merge by hand would be tedious of large networks but is automatised
with CNOgraph data structures taking into account possible AND gates and different inputs (activation/inhibition). Once the PKN is designed, you can export it in SIF format::

    c.export2sif()

You also have the ability to export the logical model into a SBML standard called SBMLQual that keeps track of the logical OR and AND gates [CHA13]_.


.. figure:: graph4.png
    :scale: 55%

    Starting from the middle panel of figure :ref:`fig:cnoproc`, CNOGraph data structure provides a method to split a node into several nodes (updating AND gates and edges automatically).


DATA
^^^^^^

We discussed about the input data and shown an example in Figure :ref:`figmidas`. CellNOptR allows one to look at these data as well but **cellnopt.core** together with Pandas and MAtplotlib gives a different experience to the user as well as much more possiblities. Here is the code snippet to generate the Figure :ref:`figmidas`:

.. code-block:: python
     :linenos:

     from cellnopt.core import *
     m = XMIDAS("MD-ToyPB.csv")
     m.plot()

The **XMIDAS** data structure is a pair of Pandas dataframe. The first dataframe stores the experiments. It is a standard dataframe where each row is an experiment and each column represent either a stimuli or inhibitor. The second dataframe stored the measurement within a multi-index dataframe where the first dimension is the cell type, the second stores the experiment name, and third is the time point. Each column correspond then to a protein.


The following command shows the time-series of all proteins in the experiment labelled "experiment_0", which appear to be the one where there is neither stimuli not inhibitors

.. code-block:: python
    :linenos:

    >>> m.df.ix['Cell'].ix['experiment_0'].plot()
    >>> m.experiments.ix['experiment_0']
    egf       0
    tnfa      0
    pi3k:i    0
    raf1:i    0
    Name: experiment_0, dtype: int64

From Figure :ref:`midascut`, we see that the *gsk3* protein is up while all others are down when there is no stimuli and no inhibitors

.. figure:: MIDAS_timecourses.png

    Example of time courses for a given combination of stimuli
    and treatments. see text for details. :label:`fig:midascut`

One issue that arise systematically when data is received from experimentalist is that it rarely in a common format; each team having its own format. Consequently, codec needs to be written. One way to somehow simplify the conversion into a MIDAS file is to think about the data as a set of unique data set. Each measurement being uniquely defined by the list of stimuli and inhibitors, a time point and a value. Splitting the data into a set of experiment, we can then build the MIDAS automatically. Here is an example:

.. code-block:: python

    from cellnopt.core import MIDASBuilder
    m = MIDASBuilder()
    e1 = Experiment("AKT", 0, {"EGFR":1}, {"AKT":0}, 0.1)
    e2 = Experiment("AKT", 5, {"EGFR":1}, {"AKT":0}, 0.5)
    e3 = Experiment("AKT", 10, {"EGFR":1}, {"AKT":0}, 0.9)
    e4 = Experiment("AKT", 0, {"EGFR":0}, {"AKT":0}, 0.1)
    e5 = Experiment("AKT", 5, {"EGFR":0}, {"AKT":0}, 0.1)
    e6 = Experiment("AKT", 10, {"EGFR":0}, {"AKT":0}, 0.1)
    for e in [e1,e2,e3,e4,e5,e6]:
    ...     m.add_experiment(e)
    m.export2midas("test.csv")
    m.xmidas.plot()

There are many more functionalities available in **cellnopt.core** especially to visualise the networks by adding attribute on the edges or nodes, described within the online documentation.

Finally, let us mention that the plotting are based on graphviz.


discussion and future directions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We will not enter into a turf wars whether Python or R is better but rather present the different approaches that have been tried within CellNOpt framework.

As mentionned earlier, CellNOptR contains  about 16,000 lines of code and 4,000 lines of C code that uses R library, which means it cannot be used as an external modules in Python without changing the code.

In order to be able to call the CellNOptR functionalities within Python, we therefore decided to use RPY2. After some learning about RPY2 itself, the wrapping could be done systematically and easily resulting in 2000 lines of code.

One issue is that you do not want to rewrite the entire documentation, which is avialble within the R packages. The solution was to use a decorator that fetches the R documentation and appedn it to the pthon docstrings.

Another feature that was required is to provide an access to the returned R object via attributes, whcih was done with another attribute.

Docstrings
#. docstrings are fectehd from R pacakges and appened ot the doc.
#. data types are accesible as attributes

.. code-block:: python

    @Rsetdoc
    @Rnames2attributes
    def readSIF(filename):
        return rpack_CNOR.readSIF(filename)

.. code-block:: python

    from cellnopt.wrapper import readSIF
    s = readSIF(cnodata("PKN-ToyMMB.sif"))
    s.interMat
    <Matrix - Python:0x6c0a9e0 / R:0x68f7740>
    [-1.000000, 0.000000, 0.000000, ...

Now, in practice, the wrapping is effective and fast as compared to the original R code. This overhead due to the wrapping seems reasonable. This is true because we are just calling a few functions and the entire optimisation is performed within R.

One issue though is that RPY2 being  higher-level interface has a cost on performance (see RPY2 website). This is fine when we call one R function. However, when we want to perform an optimisation ourself by calling the R obejctive function, this may slow significanlty a python script. THis is something to keep in mind when using RPY2.

The cost of writting a wrapper should be ignored either. What if the original code is changed ? The developer of the wrapper and the developr of the original R code should communicate closely since changing the prototype of a function needs t obe reflected into the wrapper in general.

If a R script is provided and only inputs needs to be provided, it may be wiser to call a subprocess and retrieve the output within Python. In that sense, the **cellnopt.core package** is of great interest: you manipulate, visualsise and save the input data structure beore calling a subprocess that will analyse them.

Althouh R provides a great set of packages, Python is also well armed to provide all the tools required to manipulate data. So, at the end, it also depends on the choice of the developers and community around them.


BioServices
----------------

Context and motivation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the context of CellNOpt, we need to access to web resources
such as signalling pathways or protein identifiers. Actually, there
are numerous web resources required to build applications in life science. Many can be accessed to in a programmatic way thanks to Web
Services. Building applications that combine several of them would benefit from a single framework. This was the reason to develop **BioServices**, which is a comprehensive Python framework that
provides programmatic access to major bioinformatics Web Services (e.g., KEGG, UniProt, BioModels, etc.). BioServices releases and documentation are available on `pypi <http://pypi.python.org/pypi/bioservices>`_


Programmatic access to Web Services relies mostly on (i) REST
(Representational State Transfer) and (ii) SOAP (Simple Object
Access Protocol; \href{www.w3.org/TR/soap}{www.w3.org/TR/soap}). REST has an emphasis on readability: each resource
corresponds to a unique URL. There is no need for any
external dependency since operations are carried out via standard HTTP methods
(e.g. GET, POST). SOAP uses XML-based messaging
protocol to encode request and response messages
using WSDL (Web Services Description Language; \href{www.w3.org/TR/soap}{www.w3.org/TR/wsdl}) to describe the service's capabilities.

In order to build applications that
integrate several Web Services, one needs to have expertise in (i) HTTP
requests, (ii) SOAP protocol, (iii) REST
protocol, (iv) XML parsing to consume the XML messages and
(v) related bioinformatics fields.
Besides, inputs and outputs of the services can be heterogeneous.
Consequently, the composition of workflows or design of external
applications based on several Web Services can be challenging.
s.

BioServices hides the technical aspects giving access to the services quickly and easily thanks to a thorough documentation.


Approach and Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


We first designed a set of classes to encapsulates the technical aspect that allwos an access to the web services. For developers, there is a class dedicated to REST protocol, and a class dedicated to WSDL/SOAP access.

With these classes in place, it is then straightforward to create a class dedicated to web services provided you have the main URL. Let us consider the WikiPathway web service [WP09]., which uses a WSDL protocol:

.. code-block:: python
    :linenos:

    from bioservices import WSDLService
    url ="http://www.wikipathways.org/"
    url += "wpi/webservice/webservice.php?wsdl"
    class WikiPath(WSDLService):
       def __init__(self):
         super(WikiPath, self).__init__("WikiPath", url=url)
    wp = WikiPath()
    wp.methods # or wp.serv.methods

You are now ready to access to this service. All public methods are visible in the wp.methods attribute, which contains a dictionary with all available methods from the service. A developer can then easily access diretcly to those methods or wrap them to add robustness, quality, and documentation. This is what we have done in BioServices in a systematic way by wrapping the methods of 25 web services (version 1.2.6).

The following simple code search for signalling pathways that contains the protein *MTOR*. It then returns an image showing the first pathway that has been found:

.. code-block:: python
    :linenos:

    from bioservices import WikiPathway
    s = WikiPathway()
    pathways = s.findPathwaysByText("MTOR")
    # Get a SVG representation of the pathway
    image = w.getColoredPathway("WP2320")

    # within an ipython notebook:
    from IPython.display import SVG
    SVG(image)


.. figure:: wiki.png
   :align: center

   Pathway image returned by the method getColoredPathway from the wikipathway web resource illustrated example in the text.

Combining BioServices with standard scientific tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BioServices is written in Python and has few dependencies.
Yet, manipulating data means that we want to visualise and apply various data analysis tools. Here below, we show that this is something easy.

Let us solve this very simple example. We will play with another web services from UniProt [UNI14]. What we want is to get the sequence of all human protein, get the distribution of the sequence length, and figure out what distributino it belongs to.

First, we need to download the list of uniprot entries for human, which can be downloaded from the uniprot `website <http://www.uniprot.org>`_

:

.. code-block:: python
    :linenos:

    # we assume you have a list of entries.
    # here are two entries ["ZAP70_HUMAN", "MK01_HUMAN"]
    from bioservices import UniProt
    u = UniProt()
    u.get_df(entries)

Note that the method *get_df* is the only function that requires Pandas; the import being local you do not need Pandas striclty speaking to use BioServices, except for that example.


The dataframe returned contains lots of information. One of the column contains the sequence length.



We can then plot the data distribution together with best fitted parameters of some possible distributions:

.. code-block:: python
    :linenos:

    data = df[df.Length<3000].Length
    import fitter
    f = fitter.Fitter(data, bins=150)
    f.distributions = ['lognorm', 'chi2', 'rayleigh',
        'cauchy', 'invweibull'
    f.fit()
    f.summary()

In this example, it appears that a log normal distribution is a very good guess as shown in Figure :ref:`fig:uniprot`.

.. figure:: sequence_length_fitting.png
    :align: center

    Distribution of the length of 20,000 protein sequence (human).
    Distribution was fitted to 80 distributions using SciPy distribution module.
    A log normal distribution with parameters fits the length distribution.
    shape, location, and scale of 0.71,-15.5, 416.5 respectively.
    See code snippet in the text. :label:`fig:uniprot`

Code to get the entries and regenerate this results is available within the documentation as an IPython [IPYTHON]_ notebook.

Status and future directions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BioServices provides a comprehensive access to
bioinformatics Web Services within a single Python library;
the current release (1.2.6) provides access to 25 Web Services (see Table :ref:`tabbioservices`).


.. table:: Web Services accessible from BioServices :label:`tabbioservices`
    :class: w

    +---------------+------------------------------------------------------+
    | REST          | ArrayExpress, BioMart, ChEMBLdb, KEGG, HGNC, PDB,    |
    |               | PICR, PSICQUIC, QuickGO, Rhea, UniChem, UniProt,     |
    |               | NCBIBlast, PICR, PSICQUIC                            |
    +---------------+------------------------------------------------------+
    | WSDL/SOAP     | BioModel, ChEBI, EUtils,  Miriam, WikiPathway,       |
    |               | WSDbfetch                                            |
    +---------------+------------------------------------------------------+

Do you need BioServices ? The answer depends on your applications.
If you need lots of access to a unique database, then downloading a flat file may be
a better option. However, if you need to access to several resources without frequent access, then BioServices ease the developer and user life. If you need to access to a database that changes regularly then BioServices will also be handy.

The previous example on UniProt was chosen especially because it is a very good case
study. If you want to download the flat files, this is about half a giga bytes of data to be downloaded. You may want to download it but it may be obsolet at a later stage.
If you provide an application, do you wan to provide the flat files as well ? Those
are consideration to take into account.

In the previous example, the request is very long, about 25 minutes but can be reduced
significanly by using the *requests* package instead of *urllib*, by using asynchronous calls and use caching (it would not speed up the first call but later ones).

Another comment about the previous example is that the actual requests is very long: it is the concatenation of 20,000 entry names. The URL had to be split into
several chunks are results combined together. This is transparent for a user.

THere are lots of technical aspects when dealing with REST and WSDL that do not appear when one web service is wrapped. Wrapping 25 web services within BioServices has made it more versatile and useful than doing it for one. A final example is the time out error. Some requests may died unexpectedly simply because it took too long. A simple change the timeout attribute in BioServices classes would solve the problem

Future directions of BioServices is as follows. Depending on requests and interests or simply on contributions, web services may be added but the main aspect that will be updated are

 - to use the requests package, which seems to be currently faster than standard modules (e.g., urllib2)
 - use buffering or caching to save requests and their results. This would signicantly speed up repetitive requests.
 - python3 compatible, which is currently an issue with the SOAP/WSDL protocol
 - asynchronous requests


Conclusions
-------------------------------------

We presented two Python packages related to the CellNOpt software (written in R). The first one called **cellnopt.wrapper** provides to Python users a full access to all CellNOptR functionalities (using RPY2). The second Python package provides tools to manipulate input data structures requires by CellNOptR (e.g., MIDAS data sets and SIF prior knowledge networks). Visualisation tools are also provided and the package is linked to Pandas and Matplotlib librairies.

We also briefly introduced BioServices Python package that allows developers and users to access programmatically to web services used in life sciences. The main interests of BioServices are (i) to hide technical aspects related to web resource access (GET/POST requests) so as to foster the integration of new web services (ii) to put within a single framework many web services (iii) to provide extensive on-line documentation.

The source code of those packages can be found on http://pypi.python.org/pypi where documentation are also provided.



Acknowledgement
---------------

Authors acknowledge support from EU *BioPreDyn* FP7-KBBE grant 289434.



References
----------

.. [UNI14] The UniProt Consortium
    Nucleic Acids Res. 42: D191-D198 (2014).

.. [COK13] T. Cokelaer, D. Pultz, L.M. Harder, J. Serra-Musach and J. Saez-Rodriguez
    *BioServices: a common Python package to access biological Web Services programmatically*
    Bioinformatics, 29 (24) 3241-3242 (2013)


.. [WP09] T. Kelder, AR. Pico, K. Hanspers, MP. van Iersel, C. Evelo, BR. Conklin.
    *Mining Biological Pathways Using WikiPathways Web Services.*
    PLoS ONE 4(7) (2009). doi:10.1371/journal.pone.0006447

.. [CNO12] C. Terfve, T. Cokelaer, A. MacNamara, D. Henriques, E. Goncalves, M.K. Morris, M. van Iersel, D.A. Lauffenburger, J Saez-Rodriguez. CellNOptR: a flexible toolkit to train protein signaling networks to data using multiple logic formalisms.
    *CellNOptR: a flexible toolkit to train protein signaling networks to data using multiple logic formalisms.*
    BMC Systems Biology, 2012, 6:133


.. [CHA13] C. Chaouiya et al.
    *SBML qualitative models: a model representation format and infrastructure to foster interactions between qualitative modelling formalisms and tools*
    BMC Systems Biology 2013, 7:135


.. [IPYTHON] F. Pérez and B. E. Granger. *IPython: A system for interactive scientific computing.*
    Computing in Science & Engineering , 9(3):21-29, 2007. http://ipython.org/


.. [NUMPY] T. E. Oliphant. Python for scientific computing.
    Computing in Science & Engineering , 9(3):10-20, 2007. http://www.numpy.org


.. [HUN07] J. D. Hunter. *Matplotlib: A 2d graphics environment.*
    Computing in Science & Engineering , 9(3):90-95, 2007. http://matplotlib.org


.. [SCIPY] E. Jones, T. E. Oliphant, P. Peterson, et al. *SciPy: Open source
    scientific tools for Python*, 2001-. http://www.scipy.org


.. [MCK10] W. McKinney
    *Data Structures for Statistical Computing in Python* in
    Proceedings of the 9th Python in Science Conference , p 51-56 2010


.. [MIDAS] J. Saez-Rodriguez, A. Goldsipe, J. Muhlich, L. Alexopoulos, B. Millard, D. A.   Lauffenburger, P. K. Sorger**,
   *Flexible Informatics for Linking Experimental Data to Mathematical Models via DataRail*.
   Bioinformatics, 24:6, 840-847 (2008).


.. [SAEZ] J. Saez-Rodriguez et al.
    *Discrete logic modelling as a means to link protein signalling networks with functional analysis of mammalian signal transduction*
    Mol. Syst. Biol. (2009), 5, 331

.. [MAC12] A. MacNamara, C. Terfve, D. Henriques, B. Pe\tilde{n}alver Bernab\acute{e}, and J. Saez-Rodriguez
    *State–time spectrum of signal transduction logic models*
    2012 Phys. Biol. 9 045003

.. [IDE01] T. Ideker, T. Galitski, L. Hood. *A new approach to decoding life: systems biology.*
   Annual Review of Genomics and Human Genetics. 2001;2:343–372. [


.. [KIT02] H. Kitano. *Systems biology: a brief overview.*
   Science. 2002;295(5560):1662–1664.


.. [ARI08] A.A. Hagberg, D.A. Schult and P.J. Swart,
   *Exploring network structure, dynamics, and function using NetworkX*
   in Proceedings of the 7th Python in Science Conference (SciPy2008),
   , pp. 11–15, (2008)
