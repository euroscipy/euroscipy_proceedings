EuroSciPy Proceedings
=====================


Paper Format
------------
Papers are formatted using reStructuredText and the compiled version should be
no longer than 7 pages, including figures.  Here are the steps to produce a
paper:

- Fork the [euroscipy_proceedings](https://github.com/euroscipy/euroscipy_proceedings)
  repository on GitHub.

- An example paper is provided in ``papers/00_vanderwalt``.  Create a new
  directory ``papers/firstname_surname``, copy the example paper into it, and
  modify to your liking.

- Run ``./make_paper.sh papers/firstname_surname`` to compile your paper to PDF
  (requires LaTeX, docutils, Python--see below).  The output appears in
  ``output/firstname_surname/paper.pdf``.

- Once you are ready to submit your paper, file a pull request on GitHub.
  The pull request title must include the paper title and the name of the
  first author.

- Please do not modify any files outside of your paper directory.

Pull requests are to be submitted by **2015, September 15th**, but modifications are
allowed during the review period.

The articles in the Proceedings remain copyrighted and owned by their original
authors. By submitting, the authors agree to publish their contribution under
the terms of the Creative Commons Attribution License, which permits
unrestricted use, distribution, and reproduction in any medium, provided the
original author and source are credited. For more information, please see:
http://creativecommons.org/licenses/by/3.0/

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

Acknowledgments
---------------

This repository is a fork from scipy/scipy_proceedings, the proceedings
repository of the US SciPy conference.
