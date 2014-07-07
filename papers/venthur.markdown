# Wyrm: A Brain-Computer Interface Toolbox in Python

## Abstract

In the last years Python has gained more and more traction in the scientific
community. Projects like [Numpy](http://numpy.org), [SciPy](http://scipy.org),
and [Matplotlib](http://matplotlib.org) have created a strong foundation for
scientific computing in Python and machine learning packages like
[Scikit-learn](http://scikit-learn.org) or packages for data analysis like
[Pandas](http://pandas.pydata.org) are building on top of it. Yet, in the
brain-computer interfacing (BCI) community Matlab is still the dominant
programming language.

We present [Wyrm](http://github.com/venthur/wyrm), an open source BCI toolbox in
Python. Wyrm is applicable to a wide range of neuroscientific problems. It can
be used as a toolbox for analysis and visualization of neurophysiological data
(e.g. EEG, ECoG, fMRI, or NIRS) and it is suitable for real-time online
experiments. In Wyrm we implemented dozens of methods, covering a broad range of
aspects for off-line analysis and online experiments. The list of algorithms
includes: channel selection, IIR filters, sub-sampling, spectrograms, spectra,
baseline removal for signal processing; Common Spatial Patterns (CSP), Source
Power Co-modulation (SPoC), classwise average, jumping means, signed
$r^2$-values for feature extraction; Linear Discriminant Analyis (LDA) with and
without shrinkage for machine learning; various plotting methods and many more.
It is worth mentioning that with scikit-learn you have a wide range of machine
learning algorithms readily at your disposal. Our data format is very compatible
with scikit-learn and one can usually apply the algorithms without any data
conversion step at all.

Since the correctness of its methods is crucial for a toolbox, we used unit
testing to ensure all methods work as intended. In our toolbox *each* method is
tested respectively by at least a handful of test cases to ensure that the
methods calculate the correct results, throw the expected errors if necessary,
etc. The total amount of code for all tests is roughly 2-3 times bigger than the
amount code for the toolbox methods.

As a software toolbox would be hard to use without proper documentation, we
provide documentation that consists of readable prose and extensive [API
documentation](http://venthur.github.io/wyrm/). Each method of the toolbox is
thoroughly documented and has usually a short summary, a detailed description of
the algorithm, a list of expected inputs, return values and exceptions, as well
as cross references to related methods in- or outside the toolbox and example
code to demonstrate how to use the method.

The ongoing transition from Python 2 to Python 3 was also considered and we
decided to support *both* Python versions. Wyrm is mainly developed under Python
2.7, but written in a *forward compatible* way to support Python 3 as well. Our
unit tests ensure that the methods provide the expected results in Python 2 and
Python 3.

To show how to use the toolbox realistic scenarios we provide two off-line
analysis scripts, where we demonstrate how to use the toolbox to complete two
tasks from the [BCI Competition III](https://www.bbci.de/competition/iii/). The
data sets from the competition are freely available and one can reproduce our
results using the scripts and the data. We also provide a simulated online BCI
experiment using a data set from the same competition.

Together with [Mushu](http://github.com/venthur/mushu) our signal acquisition
library and [Pyff](http://github.com/venthur/pyff) our Framework for Feedback
and Stimulus Presentation, Wyrm adds the final piece to our ongoing effort to
provide a complete, free and open source BCI system in Python.

