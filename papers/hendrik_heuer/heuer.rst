:author: Hendrik Heuer
:email: hendrik.heuer@aalto.fi
:institution: Aalto University, Finland

------------------------------------------------------------------------------
Text comparison using word vector representations and dimensionality reduction
------------------------------------------------------------------------------

.. class:: abstract

   This paper describes a technique to compare large text sources using word vector representations (word2vec) and dimensionality reduction (t-SNE) and how it can be implemented using Python. The technique provides a bird’s-eye view of different text sources, including text summaries and their source material and enables users to explore a text source like a geographical map. The technique uses the word2vec model from the gensim Python library and t-SNE from scikit-learn. Word vector representations capture many linguistic properties such as gender, tense, plurality and even semantic concepts like "capital city of". Using dimensionality reduction, a 2D map can be computed where semantically similar words are close to each other.

.. class:: keywords

   Text Comparison, Topic Comparison, word2vec, t-SNE,

Introduction
------------

When summarizing a large text, only a subset of the available topics and stories can be taken into account. The decision which topics to cover is largely editorial. This paper introduces a tool that assists this editorial process using word vector representations and dimensionality reduction. It enables a user to visually identify agreement and disagreement between two text sources. 

There is a variety of different ways to approach the problem of visualizing the topics present in a text. The simplest approach is to look at unique words and their occurrences and visualize the words in a list. Topics could also be visualized using word clouds, where the font size of a word is determined by the frequency of the word. Word clouds have a variety of shortcomings: They can only visualize small subsets, they focus on the most frequent words and they do not take synonyms and semantically similar words into account.

This paper describes a human-computer interaction-inspired approach of comparing two text sources. The approach yields a bird’s-eye view of different text sources, including text summaries and their source material and enables users to explore a text source like a geographical map.
As similar words are close to each other, the user can visually identify clusters of topics that are present in the text. Conceptually, it can be understood as a "Fourier transformation for text".

This paper describes a tool, which can be used to visualize the topics in a single text source as well as to compare different text sources. To compare the topics in source A and source B, three different sets of words can be computed: a set of unique words in source A, a set of unique words in source B as well as the intersection set of words both in source A and B. These three sets are then plotted at the same time. For this, a colour is assigned to each set of words. This enables the user to visually compare the different text sources and enables them to see which topics are covered where. The user can explore the word map and zoom in and out. He or she can also toggle the visibility, i.e. show and hide, certain word sets.

The comparison can be used to visualize the difference between a text summary and its source material. It can also help to compare Wikipedia revisions in regards to the topics they cover. Another possible implementation is visualize heterogeneous like a list of search keywords. 

The Github repository of the tool includes an online demo [Heu15]. The tool can be used to explore the precomputed topic sets of the Game of Thrones Wikipedia article revisions from 2013 and 2015. The repository also includes the precomputed topic sets for the Wikipedia article revisions for the articles on World War 2, Facebook, and the United States of America.

Distributional semantic models
------------------------------

The distributional hypothesis by Harris states that words with similar meaning occur in similar contexts [Sah05]. This implies that the meaning of words can be inferred from its distribution across contexts. The goal of Distributional Semantics is to find a representation, e.g. a vector, that approximates the meaning of a word [Bru14]. The traditional approach to statistical modeling of language is based on counting frequencies of occurrences of short symbol sequences of length up to N and did not exploit distributed representations [Cun15]. 

The general idea behind word space models is to use distributional statistics to generate high-dimensional vector spaces, where a word is represented by a context vector that encodes semantic similarity [Sah05]. There is a variety of computational models that implement the Distributional Hypothesis, including word2vec [Mik13], GloVe [Pen14], Dependency-based word embeddings [Lev14] and Random Indexing [Sah05]. For all of the techniques, Python implementations exist. Word2vec is available in gensim [Řeh10]. For GloVe, the C source code was ported to Python [Gau2015, Kul2015]. The dependency-based word embeddings by Levy and Goldberg are implemented in spaCy [Hon15]. Random Indexing is available on Github in an implementation by Joseph Turian [Tur15].

word2vec
~~~~~~~~

word2vec word vectors can capture many linguistic properties such as gender, tense, plurality and even semantic concepts such as is capital city of.

word2vec was developed by Mikolov, Sutskever, Chen, Corrado and Dean at Google. The two model architectures were made available as an open-source toolkit written in C [Mik13]. The open-source word2vec C tool released by Google and the Python bindings available in gensim were used [Řeh10] as this opened the possibility to use the freely available word vectors that were trained on a Google data set with 100 billion words.

word2vec captures domain similarity while other more dependency-based approaches capture functional similarity. Word vectors encode semantic meaning and capture many different degrees of similarity [Lev14]. In this vector space, linear algebra can be used to exploit the encoded dimensions of similarity. Using this, a computer system can complete tasks like the Scholastic Assessment Test (SAT) analogy quizzes, that measure relational similarity. 

.. math::

   king - man + women = queen

It works for the superlative:

.. math::

   fastest - fast + slow = slowest

As well as the past participle}:

.. math::

   woken - wake + be = been

It can infer the Finnish national sport from the German national sport.

.. math::

   football - Germany + Finland = hockey

Based on the last name of the current Prime Minister of the United Kingdom, it identifies the last name of the German Bundeskanzlerin:

.. math::

   Cameron - England + Germany = Merkel

The analogies can also be applied to the national dish of a country:

.. math::

   haggis - Scotland + Germany = Currywurst

Fig. 1 shows the clusters of semantically similar words and how they for visual units, which can be easily interpreted by humans.

.. figure:: word_clusters.png

   Clusters of semantically similar words emerge when the word2vec vectors are projected down to 2D using t-SNE :label:`egfig`

Dimensionality reduction with t-SNE
-----------------------------------

t-distributed Stochastic Neighbour Embedding (t-SNE) is a dimensionality reduction technique that retains the local structure of data and that helps to visualize large real-world datasets with limited computational demands [Maa08]. Vectors that are similar in a high-dimensional vector space get represented by two- or three-dimensional vectors that are close to each other in the two- or three-dimensional vector space. Dissimilar high-dimensional vectors are distant in the two- or three-dimensional vector space. Meanwhile, the global structure of the data and the presence of clusters at several scales is revealed. t-SNE is well-suited for high-dimensional data that lies on several different, but related, low-dimensional manifolds [Maa08].

t-SNE achieves this by minimizing the Kullback-Leibler divergence between the joint probabilities of the high-dimensional data and the low-dimensional representation. The Kullback-Leibler divergence measures the faithfulness with which a probability distribution q represents a probability distribution p by a discrete scalar and equals zero if the distributions are the same [Maa08]. The Kullback-Leibler divergence is minimized using the gradient descent method. In contrast to other Stochastic Neighbor Embedding methods that use Gaussian distributions, it uses a Student t-distribution.


Implementation
--------------

The tool implements a workflow that consists of a Python tool for the back end and a Javascript tool for the front end. With the Python tool, a text is converted into a collection of two-dimensional word vectors. These are visualized using the Javascript front end. With the Javascript front end, the user can explore the word map and zoom in and out to investigated both the local and the global structure of the text source. The Javascript front end can be published online.

The workflow of the tool includes the following four steps: 

Pre-processing
~~~~~~~~~~~~~~

In the pre-processing step, all sentences are tokenized to extract single words. The tokenization is done using the Penn Treebank Tokenizer implemented in the Natural Language Processing Toolkit (NLTK) for Python [Bir09]. Alternatively, this could also be achieved with a regular expression.

Using a hash map, all words are counted. Only unique words, i.e. the keys of the hash map, are taken into account for the dimensionality reduction. Not all unique words are taken into account. The 3000 most frequent English words according to a frequency list collected from Wikipedia are ignored to reduce the amount of data.

Word representations
~~~~~~~~~~~~~~~~~~~~

For all unique non-frequent words, the word representation vectors are collected from the word2vec model from the gensim Python library [Řeh10]. Each word is represented by an N-dimensional vector (N=300). 

.. code-block:: python

   from gensim.models import Word2Vec

   model = Word2Vec.load_word2vec_format( \
    word_vectors_filename, binary=True )

   for word in words:
     if word in model:
       print model[ word ]


Dimensionality Reduction
~~~~~~~~~~~~~~~~~~~~~~~~

The resulting 300-dimensional word2vec vectors are projected down to 2D using the t-SNE Python implementation in scikit-learn [Ped11].

In the dimensionality reduction step, the 300-dimensional word vectors are projected down to a two-dimensional space so that they can be easily visualized in a 2D coordinate system (see Fig. 2).

.. figure:: tsne_dimensionality_reduction.png

   In the dimensionality reduction step, the word vectors are projected down to 2D :label:`egfig`

For the implementation, the t-SNE implementation in scikit-learn is used:


.. code-block:: python

   from sklearn.manifold import TSNE

   tsne = TSNE(n_components=2)
   tsne.fit_transform( word_vectors )

Visualization
~~~~~~~~~~~~~

After the dimensionality reduction, the vectors are exported to a JSON file. The vectors are visualized using the D3.js JavaScript data visualization library [Bos12]. Using D3.js, an interactive map was developed. With this map, the user can move around and zoom in and out.

Results
--------------

The flow described in the previous section is applied to different revisions of Wikipedia articles. For this, a convenience sample of the most popular articles in 2013 from the English Wikipedia was used.  For each article, the last revision from the 31st of December 2013 and the most recent revision on the 26th of May 2015 were collected. The assumption was that popular articles will attract sufficient changes to be interesting to compare. The list of the most popular Wikipedia articles includes Facebook, Game of Thrones, the United States, and World War 2.

The article on Game of Thrones was deemed especially illustrative for the task of comparing the topics in a text, as the storyline of the TV show developed between the two different snapshot dates as new characters were introduced. Other characters became less relevant and were removed from the article. The article on World War 2 was especially interesting as one of the motivations for the topic tool is to find subtle changes in data.

Fig. 3 shows how different the global cluster, i.e. the full group of words on the maximum zoom setting, of the Wikipedia articles on the United States, Game of Thrones and World War 2 are.

.. figure:: global_clusters.png

   Global clusters of the Wikipedia articles on the United States (left), Game of Thrones (middle), and World War 2 (right). :label:`egfig`

Fig. 4 shows four screenshots of the visualization of the Wikipedia articles on the United States, including everything enabled and detail views that only show the intersection set of words, words only present in the 2013 revision of the article and words only present in the 2015 revision of the article. 

When applied to Game of Thrones, it is e.g. easy to visually compare characters names, i.e. first names, that were removed since 2013 and that were added in 2015. Using the online demo available [Heu15], this technique can be applied to the Wikipedia articles on the United States and World War 2. The technique can also be applied to compare the Google searches of an individual.

.. figure:: topic_comparison_usa.png

   Topic Comparison of the Wikipedia article on the United States. In the top left, all words in both texts are plotted. On the top right, only the intersection set of words is shown. On the bottom left, only words present in the 2013 revision and in the bottom right, only words present in the 2015 revision are shown. :label:`egfig`

Conclusion
----------

Word2vec word vector representations and t-SNE dimensionality reduction can be used to provide a bird’s-eye view of different text sources, including text summaries and their source material. This enables users to explore a text source like a geographical map. 

The paper gives an overview of an ongoing investigation of the usefulness of word vector representations and dimensionality reduction in the text and topic comparison context. The major flaw of this paper is that the introduced text visualization and text comparison approach are not validated empirically.

As many researchers publish their source code under open source licenses and as the Python community embraces and supports these publications, it was possible to integrate the findings from the literature review of my Master's thesis into a useable tool. 

Both the front end and the back end of the implementation were made available on GitHub under GNU General Public License 3 [Heu15]. The repository includes the necessary Python code to collect the word2vec representations using Gensim, to project them down to 2D using t-SNE and to output them as JSON. The repository also includes the front end code to explore the JSON file as a geographical map.

References
----------
.. [Sah05] M. Sahlgren, “An introduction to random indexing,” in Methods and applications of semantic indexing workshop at the 7th international conference on terminology and knowledge engineering, TKE, 2005, vol. 5.

.. [Bos12] M. Bostock, D3.js - Data-Driven Documents. 2012.

.. [Cun15] Y. LeCun, Y. Bengio, and G. Hinton, “Deep learning,” Nature, vol. 521, no. 7553, pp. 436–444, May 2015.

.. [Lev14] O. Levy and Y. Goldberg, “Dependency-Based Word Embeddings,” in Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), Baltimore, Maryland, 2014, pp. 302–308.

.. [Mik13] T. Mikolov, K. Chen, G. Corrado, and J. Dean, “Efficient Estimation of Word Representations in Vector Space,” CoRR, vol. abs/1301.3781, 2013.

.. [Pen14] J. Pennington, R. Socher, and C. D. Manning, “GloVe: Global Vectors for Word Representation,” in Proceedings of EMNLP, 2014.

.. [Bru14] E. Bruni, N. K. Tran, and M. Baroni, “Multimodal Distributional Semantics,” J. Artif. Int. Res., vol. 49, no. 1, pp. 1–47, Jan. 2014.

.. [Bir09] S. Bird, E. Klein, and E. Loper, Natural Language Processing with Python, 1st ed. O’Reilly Media, Inc., 2009.

.. [Ped11] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, M. Brucher, and E. Duchesnay, “Scikit-learn: Machine Learning in Python,” Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.

.. [Řeh10] Radim Řehůřek and P. Sojka, “Software Framework for Topic Modelling with Large Corpora,” in Proceedings of the LREC 2010 Workshop on New Challenges for NLP Frameworks, Valletta, Malta, 2010, pp. 45–50.

.. [Hon15] M. Honnibal, spaCy. 2015. Available: https://honnibal.github.io/spaCy/. [Accessed: 06-Aug-2015].

.. [Heu15] H. Heuer, Topic Comparison Tool. GitHub, 2015. Available: https://github.com/h10r/topic_comparison_tool. [Accessed: 06-Aug-2015].

.. [Tur15] Joseph Turian, Random Indexing Word Representations. Github, 2015. [Online]. Available: https://github.com/turian/random-indexing-wordrepresentations. [Accessed: 06-Aug-2015].

.. [Maa08] L. Van der Maaten and G. Hinton, “Visualizing data using t-SNE,” Journal of Machine Learning Research, vol. 9, no. 2579–2605, p. 85, 2008.

.. [Gau2015] J. Gauthier, glove.py. GitHub, 2015. Available: https://github.com/hans/glove.py. [Accessed: 06-Aug-2015].

.. [Kul2015] M. Kula, glove-python. GitHub, 2015. Available: https://github.com/maciejkula/glove-python. [Accessed: 06-Aug-2015].
