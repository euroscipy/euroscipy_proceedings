:author: Bastian Venthur
:email: bastian.venthur@tu-berlin.de
:institution: Berlin Institute of Technology

:author: Benjamin Blankertz
:email: benjamin.blankertz@tu-berlin.de
:institution: Berlin Institute of Technology


--------------------------------------------------
Wyrm: A Brain-Computer Interface Toolbox in Python
--------------------------------------------------

.. class:: abstract

    In the last years Python has gained more and more traction in the scientific
    community. Projects like `Numpy <http://numpy.org>`__, `SciPy
    <http://scipy.org>`__, and `Matplotlib <http://matplotlib.org>`__ have
    created a strong foundation for scientific computing in Python and machine
    learning packages like `Scikit-learn <http://scikit-learn.org>`__ or
    packages for data analysis like `Pandas <http://pandas.pydata.org>`__ are
    building on top of it. Yet, in the brain-computer interfacing (BCI)
    community Matlab is still the dominant programming language.

    We present `Wyrm <http://github.com/venthur/wyrm>`__, an open source BCI
    toolbox in Python. Wyrm is applicable to a wide range of neuroscientific
    problems. It can be used as a toolbox for analysis and visualization of
    neurophysiological data (e.g. EEG, ECoG, fMRI, or NIRS) and it is suitable
    for real-time online experiments. In Wyrm we implemented dozens of methods,
    covering a broad range of aspects for off-line analysis and online
    experiments. The list of algorithms includes: channel selection, IIR
    filters, sub-sampling, spectrograms, spectra, baseline removal for signal
    processing; Common Spatial Patterns (CSP), Source Power Co-modulation
    (SPoC), classwise average, jumping means, signed :math:`r^2`-values for
    feature extraction; Linear Discriminant Analyis (LDA) with and without
    shrinkage for machine learning; various plotting methods and many more. It
    is worth mentioning that with scikit-learn you have a wide range of machine
    learning algorithms readily at your disposal. Our data format is very
    compatible with scikit-learn and one can usually apply the algorithms
    without any data conversion step at all.

    Since the correctness of its methods is crucial for a toolbox, we used unit
    testing to ensure all methods work as intended. In our toolbox *each* method
    is tested respectively by at least a handful of test cases to ensure that
    the methods calculate the correct results, throw the expected errors if
    necessary, etc. The total amount of code for all tests is roughly 2-3 times
    bigger than the amount code for the toolbox methods.

    As a software toolbox would be hard to use without proper documentation, we
    provide documentation that consists of readable prose and extensive `API
    documentation <http://venthur.github.io/wyrm/>`__. Each method of the
    toolbox is thoroughly documented and has usually a short summary, a detailed
    description of the algorithm, a list of expected inputs, return values and
    exceptions, as well as cross references to related methods in- or outside
    the toolbox and example code to demonstrate how to use the method.

    The ongoing transition from Python 2 to Python 3 was also considered and we
    decided to support *both* Python versions. Wyrm is mainly developed under
    Python 2.7, but written in a *forward compatible* way to support Python 3 as
    well. Our unit tests ensure that the methods provide the expected results in
    Python 2 and Python 3.

    To show how to use the toolbox realistic scenarios we provide two off-line
    analysis scripts, where we demonstrate how to use the toolbox to complete
    two tasks from the `BCI Competition III
    <https://www.bbci.de/competition/iii/>`__. The data sets from the
    competition are freely available and one can reproduce our results using the
    scripts and the data. We also provide a simulated online BCI experiment
    using a data set from the same competition.

    Together with `Mushu <http://github.com/venthur/mushu>`__ our signal
    acquisition library and `Pyff <http://github.com/venthur/pyff>`__ our
    Framework for Feedback and Stimulus Presentation, Wyrm adds the final piece
    to our ongoing effort to provide a complete, free and open source BCI system
    in Python.

.. class:: keywords

    Brain-Computer Interfacing, BCI, Toolbox


Introduction
------------

In the last years Python has gained more and more traction in the scientific
community. Projects like Numpy [Numpy]_, SciPy [SciPy]_, and Matplotlib
[Matplotlib]_ have created a strong foundation for scientific computing in
Python and machine learning packages like Scikit-learn [Scikit-learn]_ or
packages for data analysis like Pandas [Pandas]_ are building on top of it. Yet,
in the brain-computer interfacing (BCI) community Matlab is still the dominant
programming language.

We present `Wyrm <http://github.com/venthur/wyrm>`__, an open source BCI toolbox
in Python. Wyrm is applicable to a wide range of neuroscientific problems. It
can be used as a toolbox for analysis and visualization of neurophysiological
data (e.g. EEG, ECoG, fMRI, or NIRS) and it is suitable for real-time online
experiments. In Wyrm we implemented dozens of methods, covering a broad range of
aspects for off-line analysis and online experiments. The list of algorithms
includes: channel selection, IIR filters, sub-sampling, spectrograms, spectra,
baseline removal for signal processing; Common Spatial Patterns (CSP), Source
Power Co-modulation (SPoC), classwise average, jumping means, signed
:math:`r^2`-values for feature extraction; Linear Discriminant Analyis (LDA)
with and without shrinkage for machine learning; various plotting methods and
many more. It is worth mentioning that with scikit-learn you have a wide range
of machine learning algorithms readily at your disposal. Our data format is very
compatible with scikit-learn and one can usually apply the algorithms without
any data conversion step at all.


Design
------

Toolbox Methods
---------------

Plotting Facilities
-------------------



Unit Testing
------------

Since the correctness of its methods is crucial for a toolbox, we used unit
testing to ensure all methods work as intended. In our toolbox *each* method is
tested respectively by at least a handful of test cases to ensure that the
methods calculate the correct results, throw the expected errors if necessary,
etc. The total amount of code for all tests is roughly 2-3 times bigger than the
amount code for the toolbox methods.


Documentation
-------------

As a software toolbox would be hard to use without proper documentation, we
provide documentation that consists of readable prose and extensive API
documentation (http://venthur.github.io/wyrm/). Each method of the toolbox is
thoroughly documented and has usually a short summary, a detailed description of
the algorithm, a list of expected inputs, return values and exceptions, as well
as cross references to related methods in- or outside the toolbox and example
code to demonstrate how to use the method.


Examples
--------

To show how to use the toolbox realistic scenarios we provide two off-line
analysis scripts, where we demonstrate how to use the toolbox to complete two
tasks from the BCI Competition III [BCIComp3]_. The data sets from the
competition are freely available and one can reproduce our results using the
scripts and the data. We also provide a simulated online BCI experiment using a
data set from the same competition.


Python 2 vs Python 3
--------------------

The ongoing transition from Python 2 to Python 3 was also considered and we
decided to support *both* Python versions. Wyrm is mainly developed under Python
2.7, but written in a *forward compatible* way to support Python 3 as well. Our
unit tests ensure that the methods provide the expected results in Python 2 and
Python 3.


Summary and Conclusion
----------------------

In this paper we presented Mushu, a free and open source BCI toolbox in Python.
We showed XXX

Mushu is available under the terms of the MIT license, its repository can be
found at http://github.com/venthur/mushu.

Together with `Mushu <http://github.com/venthur/mushu>`__ [Mushu]_ our signal
acquisition library and `Pyff <http://github.com/venthur/pyff>`__ [Pyff]_ our
Framework for Feedback and Stimulus Presentation, Wyrm adds the final piece to
our ongoing effort to provide a complete, free and open source BCI system in
Python.


Acknowledgements
----------------
This work was supported in part by grants of the BMBF: 01GQ0850 and 16SV5839.
The research leading to this results has received funding from the European
Union Seventh Framework Programme (FP7/2007-2013) under grant agreements 611570
and 609593.


References
----------
.. [Pyff] Bastian Venthur, Simon Scholler, John Williamson, Sven Dähne, Matthias
          S Treder, Maria T Kramarek, Klaus-Robert Müller and Benjamin
          Blankertz. *Pyff---A Pythonic Framework for Feedback Applications and
          Stimulus Presentation in Neuroscience.* Frontiers in Neuroscience.
          2010. http://dx.doi.org/10.3389/fnins.2010.00179.
.. [Mushu] Bastian Venthur and Benjamin Blankertz. *Mushu, a Free and Open
           Source BCI Signal Acquisition, Written in Python.* Engineering in
           Medicine and Biology Society (EMBC). doi:
           http://dx.doi.org/10.1109/EMBC.2012.6346296 San Diego, 2012.

.. [Numpy] http://numpy.org
.. [SciPy] http://scipy.org
.. [Matplotlib] http://matplotlib.org
.. [Scikit-learn] http://scikit-learn.org
.. [Pandas] http://pandas.pydata.org
.. [BCIComp3] https://www.bbci.de/competition/iii/

