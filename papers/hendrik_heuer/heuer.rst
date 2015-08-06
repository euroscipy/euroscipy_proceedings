:author: Hendrik Heuer
:email: hendrik.heuer@aalto.fi
:institution: Aalto University, Finland

------------------------------------------------------------------------------
Text comparison using word vector representations and dimensionality reduction
------------------------------------------------------------------------------

.. class:: abstract

   This paper describes a technique to compare large text sources using word vector representations (word2vec) and dimensionality reduction (t-SNE) and how it can be implemented using Python. The technique provides a bird’s-eye view of different text sources, including text summaries and their source material, and enables users to explore a text source like a geographical map. The technique uses the word2vec model from the gensim Python library and t-SNE from scikit-learn. Word vector representations capture many linguistic properties such as gender, tense, plurality and even semantic concepts like "capital city of". Using dimensionality reduction, a 2D map can be computed where semantically similar words are close to each other.

.. class:: keywords

   Text Comparison, Topic Comparison, word2vec, t-SNE,

Introduction
------------

When summarizing a large text, only a subset of the available stories and examples can be taken into account. The decision which topics to cover is largely editorial. The Topic Comparison module assists this editorial process. It enables a user to visually identify agreement and disagreement between two text sources. 


The main contribution of this poster is a novel way of doing text comparison using word vector representations (word2vec) and dimensionality reduction (t-SNE). This yields a bird’s-eye view of different text sources, including text summaries and their source material, and enables users to explore a text source like a geographical map.
As similar words are close to each other, the user can visually identify clusters of topics that are present in the text. Conceptually, it can be understood as a "Fourier transformation for text"

There are a variety of different ways to approach the problem of visualizing the topics in a text. The simplest way would be looking at unique words and their occurrences and visualizing them in a list. The topics could also be visualized using word clouds, where the font size of a word is determined by the frequency of the word. Word clouds have a variety of shortcomings: They can only visualize a small subsets, the focus on the most common words is not helpful for the task at hand and they do not take synonyms and semantically similar words into account.


Example Use Case
~~~~~~~~~~~~~~~~


To compare the topics, three different sets of words are computed: a source text topic set, a summary topic set, as well as the intersection set of both topic sets (see Figure 8). These three sets are then visualized similarly to the Topic module. A colour is assigned to each set of words. This enables the user to visually compare the different text sources and to see which topics are covered where. The user can explore the word map and zoom in and out. He or she can also toggle the visibility, i.e. show and hide, certain word sets.



Background
----------

The distributional hypothesis by Harris states that words with similar meaning occur in similar contexts \cite{sahlgren_introduction_2005}. This implies that the meaning of words can be inferred from its distribution across contexts. The goal of Distributional Semantics is to find a representation, e.g. a vector, that approximates the meaning of a word (see Figure 2) \cite{bruni_multimodal_2014}. The traditional approach to statistical modelling of language is based on counting frequencies of occurrences of short symbol sequences of length up to N and did not exploit distributed representations \cite{lecun_deep_2015}. The general idea behind word space models is to use distributional statistics to generate high-dimensional vector spaces, where a word is represented by a context vector that encodes semantic similarity \cite{sahlgren_introduction_2005}.


There are a variety of computational models that implement the Distributional Hypothesis, including word2vec \cite{mikolov_efficient_2013}, GloVe \cite{pennington_glove:_2014}, Dependency-based word embeddings \cite{levy_dependency-based_2014} and Random Indexing \cite{sahlgren_introduction_2005}. For all of the techniques, Python implementations exist. Word2vec is available in gensim. The dependency-based word embeddings by Levy and Goldberg (2014) are implemented in spaCy. Random Indexing is available 

word2vec word vectors can capture many linguistic properties such as gender, tense, plurality and even semantic concepts like "is capital city of", which we exploit using a combination of dimensionality reduction and data visualization.





word2vec
~~~~~~~~

word2vec word vectors can capture many linguistic properties such as gender, tense, plurality and even semantic concepts such as is capital city of.

word2vec was developed by Mikolov, Sutskever, Chen, Corrado and Dean at Google. The two model architectures were made available as an open-source toolkit written in C CITATION MIKOLOV. The open-source word2vec C tool released by Google and the Python bindings available in gensim were used CITATION MIKOLOV as this opened the possibility to use the freely available word vectors that were trained on a Google data set with 100 billion words.

word2vec captures domain similarity, while other more dependency-based approaches capture functional similarity. Word vectors encode semantic meaning and capture many different degrees of similarity. In this vector space, linear algebra can be used to exploit the encoded dimensions of similarity. Using this, a computer system can complete tasks like the Scholastic Assessment Test (SAT) analogy quizzes, that measure relational similarity. 

.. math::

   king - man + women = **queen**

It works for the superlative:

.. math::

   fastest - fast + slow = **slowest**

As well as the past participle}:

.. math::

   woken - wake + be = **been**

It can infer the Finnish national sport from the German national sport.

.. math::

   football - Germany + Finland = **hockey**

Based on the last name of the current Prime Minister of the United Kingdom, it identifies the last name of the German Bundeskanzlerin:

.. math::

   Cameron - England + Germany = **Merkel**

The analogies can also be applied to the national dish of a country:

.. math::

   haggis - Scotland + Germany = **Currywurst**

.. figure:: word_clusters.png

   Clusters of semantically similar words emerge when the word2vec vectors are projected down to 2D using t-SNE :label:`egfig`

t-SNE
~~~~~

t-distributed Stochastic Neighbour Embedding (t-SNE) is a dimensionality reduction technique that retains the local structure of data and that helps to visualize large real-world datasets with limited computational demands CITATION van_der_maaten_visualizing_2008. Vectors that are similar in a high-dimensional vector space get represented by two-- or three--dimensional vectors that are close to each other in the two-- or three--dimensional vector space. Dissimilar high-dimensional vectors are distant in the two-- or three--dimensional vector space. Meanwhile, the global structure of the data is revealed.

t-SNE achieves this by minimizing the Kullback-Leibler divergence between the joint probabilities of the high-dimensional data and the low-dimensional representation. The Kullback-Leibler divergence measures the dissimilarity ("distance") of two probability distributions by a discrete scalar and equals zero if they are the same CITATION van_der_maaten_visualizing_2008.

Visualization
~~~~~~~~~~~~~

The Topic Comparison tool uses a variety of different JavaScript toolkits to visualize the data including D3.js and Google’s Graph API. For most of these toolkits, data is exchanged using the JSON format.

Implementation
--------------

The topic module implements the following steps: 

Pre-processing
~~~~~~~~~~~~~~

In the pre-processing step, all sentences are tokenized to extract single words. The tokenization is done using the Penn Treebank Tokenizer implemented in the Natural Language Processing Toolkit (NLTK) for Python CITATION bird_natural_2009. Alternatively, this could also be achieved with a regular expression.

Using a hash map, all words are counted. Only unique words, i.e. the keys of the hash map, are taken into account for the dimensionality reduction. Not all unique words are taken into account. The 3000 most frequent English words according to a frequency list collected from Wikipedia are ignored to reduce the amount of data CITATION wiktionary _frequency ????.

Word representations
~~~~~~~~~~~~~~~~~~~~

For all unique non-frequent words, the word representation vectors are collected from the word2vec model via the gensim Python library CITATION rehurek_lrec. Each word is represented by an N-dimensional vector (N=300). 

The 

.. code-block:: python

   from gensim.models import Word2Vec

   model = Word2Vec.load_word2vec_format( word_vectors_filename, binary=True )

   for word in words:
    if word in model:
      print model[ word ]


Dimensionality Reduction
~~~~~~~~~~~~~~~~~~~~~~~~

The results of the word2vec vectors are projected down to 2D using the t-SNE Python implementation in scikit-learn (See Figure 7) CITATION pedregosa_scikit-learn:_2011.

In the dimensionality reduction step, the 300 dimensional word vectors are projected down to a two--dimensional space, so that they can be easily visualized in a 2D coordinate sytem.


.. figure:: tsne_dimensionality_reduction.png

   In the dimensionality reduction step, the word vectors are projected down to 2D :label:`egfig`

For the implementation, the t-SNE implementation in scikit-learn is used:


.. code-block:: python

   from sklearn.manifold import TSNE

   tsne = TSNE(n_components=2)
   tsne.fit_transform( word_vectors )

Visualization
~~~~~~~~~~~~~

After the dimensionality reduction, the vectors are written to a JSON file. The vectors are visualized using the D3.js JavaScript data visualization library CITATION d3js. Using D3.js, an interactive map was developed. With this map, the user can move around and zoom in and out.

Results
--------------

This approach can be used to compare Wikipedia revisions. 

For this, a revsion of the Wikipedia article on Game of Thrones from 2013 and from 2015 was used and compared. Similar words are close to each other in the 2D projection.
Using this, it is e.g. easy to visually compare characters names, i.e. first names, that were removed since 2013 and that were added in 2015. The tool gives an global overview and allows to compare the text sources in regards to the intersection set, i.e. words that are present in the 2013 and the 2015 revision, and each revision separately. In the proceedings, this technique is also applied to the Wikipedia articles on the United States and World War 2. The technique can also be applied to compare the Google searches of an individual.

.. figure:: topic_comparison_usa.png

   Topic Comparison of the Wikipedia article on the United States. In the top left, all words in present in the 2013 (orange) and 2015 (red) revisions and the intersection set (white) of the Wikipedia article are plotted. :label:`egfig`

.. figure:: global_clusters.png

   Global clusters of the Wikipedia articles on the United States (left), Game of Thrones (middle), and World War 2 (right). :label:`egfig`

Conclusion
----------

Word2vec word vector representations and t-SNE dimensionality reduction are used to provide a bird’s-eye view of different text sources, including text summaries and their source material. This enables users to explore a text source like a geographical map. Semantically similar words are close to each other in 2D, which yields a "Fourier transformation for text" The tool addresses a complex problem -- comparing two text sources with each other -- using word representations, dimensionality reduction and data visualization.

As many researchers publish their source code under open source licenses and as the Python community embraces these publication, it was possible to integrate the findings from the literature review from my Master's thesis into a useable tool. 

Both the frontend and the backend of the implementation were made available on GitHub under GNU General Public License 3 CITATION heuer_topic_2015. The repository includes the necessary Python code to collect the word2vec representations using Gensim, to project them down to 2D using t-SNE and to output them as JSON. The repository also includes the frontend code to explore the JSON file as a geographical map.


The open-source word2vec C tool released by Google and the Python bindings available in gensim are used as this opened the possibility to use the freely available word vectors that were trained on a Google data set with 100 billion words.

The major flaw of the thesis is that the introduced text visualization and text comparison approach is not validated empirically.

References
----------
.. [Atr03] P. Atreides. *How to catch a sandworm*,
           Transactions on Terraforming, 21(3):261-300, August 2003.


.. [1] M. Sahlgren, “An introduction to random indexing,” in Methods and applications of semantic indexing workshop at the 7th international conference on terminology and knowledge engineering, TKE, 2005, vol. 5.
.. [2] M. Bostock, D3.js - Data-Driven Documents. 2012.
.. [3] Y. LeCun, Y. Bengio, and G. Hinton, “Deep learning,” Nature, vol. 521, no. 7553, pp. 436–444, May 2015.
.. [4] O. Levy and Y. Goldberg, “Dependency-Based Word Embeddings,” in Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), Baltimore, Maryland, 2014, pp. 302–308.
.. [5] T. Mikolov, K. Chen, G. Corrado, and J. Dean, “Efficient Estimation of Word Representations in Vector Space,” CoRR, vol. abs/1301.3781, 2013.
.. [6] J. Pennington, R. Socher, and C. D. Manning, “GloVe: Global Vectors for Word Representation,” in Proceedings of EMNLP, 2014.
.. [7] E. Bruni, N. K. Tran, and M. Baroni, “Multimodal Distributional Semantics,” J. Artif. Int. Res., vol. 49, no. 1, pp. 1–47, Jan. 2014.
.. [8] S. Bird, E. Klein, and E. Loper, Natural Language Processing with Python, 1st ed. O’Reilly Media, Inc., 2009.
.. [9] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, M. Brucher, and E. Duchesnay, “Scikit-learn: Machine Learning in Python,” Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.
.. [10] Radim Řehůřek and P. Sojka, “Software Framework for Topic Modelling with Large Corpora,” in Proceedings of the LREC 2010 Workshop on New Challenges for NLP Frameworks, Valletta, Malta, 2010, pp. 45–50.
.. [11] M. Honnibal, spaCy. 2015.
.. [12] H. Heuer, Topic Comparison Tool. GitHub, 2015.
.. [13] “turian/random-indexing-wordrepresentations,” GitHub. [Online]. Available: https://github.com/turian/random-indexing-wordrepresentations. [Accessed: 06-Aug-2015].
.. [14] L. Van der Maaten and G. Hinton, “Visualizing data using t-SNE,” Journal of Machine Learning Research, vol. 9, no. 2579–2605, p. 85, 2008.
.. [15] T. Mikolov, K. Chen, G. Corrado, and J. Dean, word2vec. Google, 2013.


