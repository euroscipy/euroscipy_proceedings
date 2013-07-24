EuroSciPy Proceedings
=====================

This repository is a fork from scipy/scipy_proceedings.

Paper Format
------------
Papers are formatted using reStructuredText and the compiled version should be
no longer than 7 pages, including figures.  Here are the steps to produce a
paper:

- Fork the [scipy_proceedings](https://github.com/euroscipy/scipy_proceedings)
  repository on GitHub.

- An example paper is provided in ``papers/00_vanderwalt``.  Create a new
  directory ``papers/firstname_surname``, copy the example paper into it, and
  modify to your liking.

- Run ``./make_paper.sh papers/firstname_surname`` to compile your paper to PDF
  (requires LaTeX, docutils, Python--see below).  The output appears in
  ``output/firstname_surname/paper.pdf``.

- Once you are ready to submit your paper, file a pull request on GitHub.
  **Please ensure that you file against the correct branch**--your branch should
  be named master, and the pull-request should be against our master branch.

- Please do not modify any files outside of your paper directory.

Pull requests are to be submitted by **September 30th**, but modifications are
allowed during the review period.

General Guidelines
------------------
- All figures and tables should have captions.
- License conditions on images and figures must be respected (Creative Commons,
  etc.).
- Code snippets should be formatted to fit inside a single column without
  overflow.
- Avoid custom LaTeX markup where possible.

Other markup
------------
Please refer to the example paper in ``papers/00_vanderwalt`` for
examples of how to:

 - Label figures, equations and tables
 - Use math markup
 - Include code snippets

Requirements
------------

 - IEEETran (often packaged as ``texlive-publishers``, or download from
   [CTAN](http://www.ctan.org/tex-archive/macros/latex/contrib/IEEEtran/) LaTeX
   class
 - AMSmath LaTeX classes (included in most LaTeX distributions)
 - `docutils` 0.8 or later (``easy_install docutils``)
 - `pygments` for code highlighting (``easy_install pygments``)
