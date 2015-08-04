:author: Hendrik Heuer
:email: hendrik.heuer@aalto.fi
:institution: Aalto University, Finland

------------------------------------------------------------------------------
Text comparison using word vector representations and dimensionality reduction
------------------------------------------------------------------------------

.. class:: abstract

   This paper describes a novel tool to compare texts using word vector representations (word2vec) and dimensionality reduction (t-SNE). This yields a bird’s-eye view of different text sources, including text summaries and their source material, and enables users to explore a text source like a geographical map.

   The tool uses word2vec word representations from the gensim Python library and t-SNE from scikit-learn to visualize and compare the topics in book summaries and their source material. Word vector representations capture many linguistic properties such as gender, tense, plurality and even semantic concepts like "capital city of". Using dimensionality reduction, a 2D map can be computed where semantically similar words are close to each other.

.. class:: keywords

   terraforming, desert, numerical perspective


Introduction
------------

The main contribution of this poster is a novel way of doing text comparison using word vector representations (word2vec) and dimensionality reduction (t-SNE). This yields a bird’s-eye view of different text sources, including text summaries and their source material, and enables users to explore a text source like a geographical map.
As similar words are close to each other, the user can visually identify clusters of topics that are present in the text. Conceptually, it can be understood as a {\textquotedbl}Fourier transformation for text{\textquotedbl}.
The tool uses word2vec word representations from the gensim Python library and t-SNE from scikit-learn to visualize.


Process
-------

\paragraph{Theory}

As discussed in Section 3.1, word vectors capture many linguistic properties such as gender, tense, plurality and even semantic concepts like \textit{is capital city of}, which we exploit using a combination of dimensionality reduction and data visualization.

\paragraph{Background}

\paragraph{Use Case}

When summarizing a large text, only a subset of the available stories and examples can be taken into account. The decision which topics to cover is largely editorial. The Topic Comparison module assists this editorial process. It enables a user to visually identify agreement and disagreement between two text sources. 

To compare the topics, three different sets of words are computed: a source text topic set, a summary topic set, as well as the intersection set of both topic sets (see Figure 8). These three sets are then visualized similarly to the Topic module. A colour is assigned to each set of words. This enables the user to visually compare the different text sources and to see which topics are covered where. The user can explore the word map and zoom in and out. He or she can also toggle the visibility, i.e. show and hide, certain word sets.


\paragraph{Motivation}

There are a variety of different ways to approach the problem of visualizing the topics in a text. The simplest way would be looking at unique words and their occurrences and visualizing them in a list. The topics could also be visualized using word clouds, where the font size of a word is determined by the frequency of the word. Word clouds have a variety of shortcomings: They can only visualize a small subsets, the focus on the most common words is not helpful for the task at hand and they do not take synonyms and semantically similar words into account.

Therefore, the bird's-eye view approach was developed and favoured. Section 3.7 details why the word2vec implementation \cite{mikolov_efficient_2013, mikolov_word2vec_????} was used instead of Random Indexing \cite{sahlgren_introduction_2005} or the dependency-based word embeddings from Levy and Goldberg \cite{levy_dependency-based_2014}.

\paragraph{Implementation}

The topic module implements the following steps: 

\subparagraph{0. Pre-processing}
In the pre-processing step, all sentences are tokenized to extract single words. The tokenization is done using the Penn Treebank Tokenizer implemented in the Natural Language Processing Toolkit (NLTK) for Python \cite{bird_natural_2009}. Alternatively, this could also be achieved with a regular expression.

Using a hash map, all words are counted. Only unique words, i.e. the keys of the hash map, are taken into account for the dimensionality reduction. Not all unique words are taken into account. The 3000 most frequent English words according to a frequency list collected from Wikipedia are ignored to reduce the amount of data \cite{wiktionary_frequency_????}.

\subparagraph{1. Word representations}

For all unique non-frequent words, the word representation vectors are collected from the word2vec model via the gensim Python library \cite{rehurek_lrec}. Each word is represented by an N-dimensional vector (N=300). 

\subparagraph{2. Dimensionality Reduction}

The results of the word2vec vectors are projected down to 2D using the t-SNE Python implementation in scikit-learn (See Figure 7) \cite{pedregosa_scikit-learn:_2011}.

\begin{figure}[h]
\centering \includegraphics[height=4cm]{thesis-img/tsne_dimensionality_reduction.pdf}
\caption{In the dimensionality reduction step, the 300 dimensional word vectors are projected down to a two--dimensional space, so that they can be easily visualized in a 2D coordinate sytem.}
\end{figure}

\subparagraph{3. Visualization}

After the dimensionality reduction, the vectors are written to a JSON file. The vectors are visualized using the D3.js JavaScript data visualization library \cite{d3js}. Using D3.js, an interactive map was developed. With this map, the user can move around and zoom in and out.


Background
----------

\paragraph{word2vec}
Word vectors encode semantic meaning and capture many different degrees of similarity in a vector space. In this vector space, linear algebra can be used to exploit the encoded dimensions of similarity. Using this, a computer system can complete tasks like the Scholastic Assessment Test (SAT) analogy quizzes, that measure relational similarity. This includes the classical example ($king - man + women = \mathbf{queen}$) \cite{mikolov_efficient_2013}, but it also works for the superlative ($fastest - fast + slow = \mathbf{slowest}$) and the past participle ($woken - wake + be = \mathbf{been}$). It captures analogies between political figures ($Cameron - England + Germany = \mathbf{Merkel}$) as well as national dish ($haggis - Scotland + Germany = \mathbf{Currywurst}$). word2vec captures domain similarity, while other more dependency-based approaches capture functional similarity. 
\paragraph{t-SNE}
t-distributed Stochastic Neighbour Embedding (t-SNE) is a dimensionality reduction technique that retains the local structure of data and that helps to visualize large real-world datasets with limited computational demands \cite{van_der_maaten_visualizing_2008}. Vectors that are similar in a high-dimensional vector space get represented by two-- or three--dimensional vectors that are close to each other in the two-- or three--dimensional vector space and vice versa. Meanwhile, the global structure of the data is revealed. t-SNE minimizes the Kullback-Leibler divergence between the joint probabilities of the high-dimensional data and the low-dimensional representation.

Use case
--------

This approach can be used to compare Wikipedia revisions. 

A convenience sample of the most popular articles in 2013 from the English Wikipedia was used. The list is ranked by view count \cite{johan_gunnarsson_most_????}. For each article, the last revision from the 31st of December 2013 and the most recent revision on the 26th of May 2015 were collected. The assumption was that popular articles will attract sufficient changes to be interesting to compare.


For this, a revsion of the Wikipedia article on Game of Thrones from 2013 and from 2015 was used and compared. Similar words are close to each other in the 2D projection.
Using this, it is e.g. easy to visually compare characters names, i.e. first names, that were removed since 2013 and that were added in 2015. The tool gives an global overview and allows to compare the text sources in regards to the intersection set, i.e. words that are present in the 2013 and the 2015 revision, and each revision separately. In the proceedings, this technique is also applied to the Wikipedia articles on the United States and World War 2. The technique can also be applied to compare the Google searches of an individual.



    includegraphics[width=0.8\linewidth,trim=20mm 10mm 10mm 10mm, clip]facebook_hacking.png}



    includegraphics[width=0.4\linewidth,trim=20mm 10mm 10mm 10mm, clip]game_of_thrones_full_all_glow.png}
    includegraphics[width=0.4\linewidth,trim=20mm 10mm 10mm 10mm, clip]game_of_thrones_full_white_glow.png}


\subsubsection[Topic comparison of Wikipedia revisions]{Topic comparison of Wikipedia revisions}

In the following sections, the Topic Comparison module described in Section 4.1.1 will be applied to different revisions of Wikipedia articles described in Section 5.2.1 to demonstrate how the module exposes regional clusters, global clusters, and how it facilitates topic comparison.

\subsubsection[Regional cluster]{Regional cluster}

Figure 9 shows a regional cluster of words in the Wikipedia article on Game of Thrones related to television and acting.

\begin{figure}[H]
\centering \includegraphics[height=12cm]{thesis-img/game_of_thrones_episodes.png}
\caption{Game of Thrones: Semantically and stylistically similar words end up being close to each other.}
\end{figure}

\newpage

\subsubsection[Global clusters]{Global clusters}

Figure 10 shows the articles of three Wikipedia articles and their revisions from 2013 and 2015 including the article on the United States of America, Game of Thrones and World War 2. 

\begin{figure}[H]
\centering
\begin{subfigure}{.33333333\textwidth}
  \centering
  \includegraphics[width=.95\linewidth]{thesis-img/united_states_full_all_glow.png}
  \caption{United States}
\end{subfigure}%
\begin{subfigure}{.33333333\textwidth}
  \centering
  \includegraphics[width=.95\linewidth]{thesis-img/game_of_thrones_full_all_glow.png}
  \caption{Game of Thrones}
\end{subfigure}%
\begin{subfigure}{.33333333\textwidth}
  \centering
  \includegraphics[width=.95\linewidth]{thesis-img/world_war_two_full_all_glow.png}
  \caption{World War 2}
\end{subfigure}
\caption{Topic Module bird’s-eye view of three Wikipedia articles and their revisions from 2013 and 2015.}
\end{figure}

\newpage

\subsubsection[Topic comparison I]{Topic comparison I}

Figure 11 shows how an editor would view all sets, only the intersection set, the set of words only present in the 2013 revision and the set of words only present in the 2015 revision of the Wikipedia article revision about the United States.

\begin{figure}[H] 
\centering
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/united_states_full_all_glow.png}
  \caption{All words}
\end{subfigure}%
\hfill
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/united_states_full_white_glow.png}
  \caption{Intersection set}
\end{subfigure}%
\vskip\baselineskip
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/united_states_full_orange_glow.png}
  \caption{2013 revision}
\end{subfigure}%
\hfill
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/united_states_full_red_glow.png}
  \caption{2015 revision}
\end{subfigure}%

\caption{Topic Comparison module visualizing the Wikipedia article about the United States.}
\end{figure}

\newpage

\subsubsection[Topic comparison II]{Topic comparison II}

Figure 12 compares the Game of Thrones Wikipedia article revisions in regards to character names. Figure 12a) shows that a few characters were removed from the article and are only present in the 2013 revision. Figure 12b) shows that a variety of character names were added to the article in 2015.

\begin{figure}[H] 
\centering
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/game_of_thrones_characters_orange_glow.png}
  \caption{2013 revision}
\end{subfigure}%
\hfill
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/game_of_thrones_characters_red_glow.png}
  \caption{2015 revision}
\end{subfigure}%

\caption{Comparison of character names in Game of Thrones article.}
\end{figure}

\subsubsection[Intersection sets]{Intersection sets}

The Figures 13-15 compare the intersection sets of words present in both the 2013 and the 2015 revisions of the Wikipedia articles on the United States (Figure 13), Game of Thrones (Figure 14) and World War 2 (Figure 15).

\begin{figure}[H] 
\centering
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/united_states_full_all_glow.png}
  \caption{All words}
\end{subfigure}%
\hfill
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/united_states_full_white_glow.png}
  \caption{Intersection set}
\end{subfigure}%

\caption{United States of America}
\vskip\baselineskip

\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/game_of_thrones_full_all_glow.png}
  \caption{All words}
\end{subfigure}%
\hfill
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/game_of_thrones_full_white_glow.png}
  \caption{Intersection set}
\end{subfigure}%

\caption{Game of Thrones}
\vskip\baselineskip

\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/world_war_two_full_all_glow.png}
  \caption{2013 revision}
\end{subfigure}%
\hfill
\begin{subfigure}[b]{.5\textwidth}
  \centering
  \includegraphics[width=.9\linewidth]{thesis-img/world_war_two_full_white_glow.png}
  \caption{2015 revision}
\end{subfigure}%

\caption{World War 2}
\end{figure}

Conclusion
----------

Word2vec word vector representations and t-SNE dimensionality reduction are used to provide a bird’s-eye view of different text sources, including text summaries and their source material. This enables users to explore a text source like a geographical map. Semantically similar words are close to each other in 2D, which yields a {\textquotedbl}Fourier transformation for text{\textquotedbl}. The tool addresses a complex problem -- comparing two text sources with each other -- using word representations, dimensionality reduction and data visualization.

As many researchers publish their source code under open source licenses and as the Python community embraces these publication, it was possible to integrate the findings from the literature review from my Master's thesis into a useable tool. 

Both the frontend and the backend of the implementation were made available on GitHub under GNU General Public License 3 \cite{heuer_topic_2015}. The repository includes the necessary Python code to collect the word2vec representations using Gensim, to project them down to 2D using t-SNE and to output them as JSON. The repository also includes the frontend code to explore the JSON file as a geographical map.


The open-source word2vec C tool released by Google and the Python bindings available in gensim are used as this opened the possibility to use the freely available word vectors that were trained on a Google data set with 100 billion words.

The major flaw of the thesis is that the introduced text visualization and text comparison approach is not validated empirically.

bibliographystyle{plain}
bibliography{Thesis.bib}

Of course, no paper would be complete without some source code.  Without
highlighting, it would look like this::

   def sum(a, b):
       """Sum two numbers."""

       return a + b

With code-highlighting:

.. code-block:: python

   def sum(a, b):
       """Sum two numbers."""

       return a + b

Maybe also in another language, and with line numbers:

.. code-block:: c
   :linenos:

   int main() {
       for (int i = 0; i < 10; i++) {
           /* do something */
       }
       return 0;
   }

Or a snippet from the above code, starting at the correct line number:

.. code-block:: c
   :linenos:
   :linenostart: 2

   for (int i = 0; i < 10; i++) {
       /* do something */
   }
 
Important Part
--------------

It is well known [Atr03]_ that Spice grows on the planet Dune.  Test
some maths, for example :math:`e^{\pi i} + 3 \delta`.  Or maybe an
equation on a separate line:

.. math::

   g(x) = \int_0^\infty f(x) dx

or on multiple, aligned lines:

.. math::
   :type: eqnarray

   g(x) &=& \int_0^\infty f(x) dx \\
        &=& \ldots


The area of a circle and volume of a sphere are given as

.. math::
   :label: circarea

   A(r) = \pi r^2.

.. math::
   :label: spherevol

   V(r) = \frac{4}{3} \pi r^3

We can then refer back to Equation (:ref:`circarea`) or
(:ref:`spherevol`) later.

Mauris purus enim, volutpat non dapibus et, gravida sit amet sapien. In at
consectetur lacus. Praesent orci nulla, blandit eu egestas nec, facilisis vel
lacus. Fusce non ante vitae justo faucibus facilisis. Nam venenatis lacinia
turpis. Donec eu ultrices mauris. Ut pulvinar viverra rhoncus. Vivamus
adipiscing faucibus ligula, in porta orci vehicula in. Suspendisse quis augue
arcu, sit amet accumsan diam. Vestibulum lacinia luctus dui. Aliquam odio arcu,
faucibus non laoreet ac, condimentum eu quam. Quisque et nunc non diam
consequat iaculis ut quis leo. Integer suscipit accumsan ligula. Sed nec eros a
orci aliquam dictum sed ac felis. Suspendisse sit amet dui ut ligula iaculis
sollicitudin vel id velit. Pellentesque hendrerit sapien ac ante facilisis
lacinia. Nunc sit amet sem sem. In tellus metus, elementum vitae tincidunt ac,
volutpat sit amet mauris. Maecenas diam turpis, placerat at adipiscing ac,
pulvinar id metus.

.. figure:: figure1.png

   This is the caption. :label:`egfig`

.. figure:: figure1.png
   :align: center
   :figclass: w

   This is a wide figure, specified by adding "w" to the figclass.  It is also
   center aligned, by setting the align keyword (can be left, right or center).

.. figure:: figure1.png
   :scale: 20%
   :figclass: bht

   This is the caption on a smaller figure that will be placed by default at the
   bottom of the page, and failing that it will be placed inline or at the top.
   Note that for now, scale is relative to a completely arbitrary original
   reference size which might be the original size of your image - you probably
   have to play with it. :label:`egfig2`

As you can see in Figures :ref:`egfig` and :ref:`egfig2`, this is how you reference auto-numbered
figures.

.. table:: This is the caption for the materials table. :label:`mtable`

   +------------+----------------+
   | Material   | Units          |
   +------------+----------------+
   | Stone      | 3              |
   +------------+----------------+
   | Water      | 12             |
   +------------+----------------+
   | Cement     | :math:`\alpha` |
   +------------+----------------+


We show the different quantities of materials required in Table
:ref:`mtable`.


.. The statement below shows how to adjust the width of a table.

.. raw:: latex

   \setlength{\tablewidth}{0.8\linewidth}


.. table:: This is the caption for the wide table.
   :class: w

   +--------+----+------+------+------+------+--------+
   | This   | is |  a   | very | very | wide | table  |
   +--------+----+------+------+------+------+--------+


Perhaps we want to end off with a quote by Lao Tse:

  *Muddy water, let stand, becomes clear.*


.. Customised LaTeX packages
.. -------------------------

.. Please avoid using this feature, unless agreed upon with the
.. proceedings editors.

.. ::

..   .. latex::
..      :usepackage: somepackage

..      Some custom LaTeX source here.

References
----------
.. [Atr03] P. Atreides. *How to catch a sandworm*,
           Transactions on Terraforming, 21(3):261-300, August 2003.


