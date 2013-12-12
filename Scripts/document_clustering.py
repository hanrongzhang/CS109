from __future__ import print_function

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans

from optparse import OptionParser
import sys

import numpy as np
from pandas import read_csv
import pylab as pl
from sklearn.decomposition import PCA

# parse commandline arguments
op = OptionParser()
op.add_option("--lsa",
              dest="n_components", type="int",
              help="Preprocess documents with latent semantic analysis.")
op.add_option("--no-minibatch",
              action="store_false", dest="minibatch", default=True,
              help="Use ordinary k-means algorithm (in batch mode).")
op.add_option("--no-idf",
              action="store_false", dest="use_idf", default=True,
              help="Disable Inverse Document Frequency feature weighting.")
op.add_option("--use-hashing",
              action="store_true", default=False,
              help="Use a hashing feature vectorizer")
op.add_option("--n-features", type=int, default=100000,
              help="Maximum number of features (dimensions)"
                   "to extract from text.")
op.add_option("--min_df",
              dest="min_df", default=.0001)
op.add_option("--verbose",
              action="store_true", dest="verbose", default=False,
              help="Print progress reports inside k-means algorithm.")
op.add_option("--start_date",
              dest="start_date", default='2011-01-01')
op.add_option("--end_date",
              dest="end_date", default='2012-12-31')
op.add_option("--text_source",
              dest="text_source", default='both')
op.add_option("--print_visualization", action="store_false",
              dest="print_visualization", default=True)

			  
(opts, args) = op.parse_args()

###############################################################################
# Set up data and vectorizer

#load data
data = read_csv('./Data/all_data_classified_both.csv')
data = data[(data['date'] >= opts.start_date) & (data['date'] <= opts.end_date)]

#turn list of sources into np array
labels = np.array(data[['source']].to_dict('list').values()[0])
#turn list of abstracts into a list
if (opts.text_source == 'headlines'):
  text = data[['headline']].to_dict('list').values()[0]
elif (opts.text_source == 'abstracts'):
  text = data[['abstract']].to_dict('list').values()[0]
else:
  text = (data[['abstract']] + data[['headline']]).to_dict('list').values()[0]

#source_num is number of unique sources
source_num = np.unique(labels).shape[0]

if opts.use_hashing:
    if opts.use_idf:
        # Perform an IDF normalization on the output of HashingVectorizer
        hasher = HashingVectorizer(n_features=opts.n_features,
                                   stop_words='english', non_negative=True,
                                   norm=None, binary=False)
        vectorizer = Pipeline((
            ('hasher', hasher),
            ('tf_idf', TfidfTransformer())
        ))
    else:
        vectorizer = HashingVectorizer(n_features=opts.n_features,
                                       stop_words='english',
                                       non_negative=False, norm='l2',
                                       binary=False)
else:
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=opts.n_features,
                                 stop_words='english', use_idf=opts.use_idf, min_df = float(opts.min_df))

X = vectorizer.fit_transform(text)

print("n_samples: %d, n_features: %d," % X.shape, "n_sources: %d" % source_num)
print()

if opts.n_components:
    print("Performing dimensionality reduction using LSA")
    lsa = TruncatedSVD(opts.n_components)
    X = lsa.fit_transform(X)
    # Vectorizer results are normalized, which makes KMeans behave as
    # spherical k-means for better results. Since LSA/SVD results are
    # not normalized, we have to redo the normalization.
    X = Normalizer(copy=False).fit_transform(X)

    print()


###############################################################################
# Do the actual clustering

if opts.minibatch:
    km = MiniBatchKMeans(n_clusters=source_num, init='k-means++', n_init=1,
                         init_size=1000, batch_size=1000, verbose=opts.verbose)
else:
    km = KMeans(n_clusters=source_num, init='k-means++', max_iter=100, n_init=1,
                verbose=opts.verbose)

km.fit(X)

#homogeneity: each cluster contains only members of a single class
print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels, km.labels_))

#completeness: all members of a given class are assigned to the same cluster
print("Completeness: %0.3f" % metrics.completeness_score(labels, km.labels_))

#v-measure: harmonic mean of homogeneity and completeness
print("V-measure: %0.3f" % metrics.v_measure_score(labels, km.labels_))

#adjusted rand-index: function that measures the similarity of the two assignments, ignoring permutations
print("Adjusted Rand-Index: %.3f" % metrics.adjusted_rand_score(labels, km.labels_))

#silhouette coefficient: a higher score relates to a model with better defined clusters
print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels, sample_size=1000))

###############################################################################
# Visualize the results on PCA-reduced data

if(opts.print_visualization):
    np.random.seed(42)
    sample_size = 300

    data = X.toarray()
    n_digits = source_num
    n_samples, n_features = data.shape

    reduced_data = PCA(n_components=2).fit_transform(data)
    kmeans = KMeans(init='k-means++', n_clusters=n_digits, n_init=10)
    kmeans.fit(reduced_data)

    # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .02     # point in the mesh [x_min, m_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min(), reduced_data[:, 0].max()
    y_min, y_max = reduced_data[:, 1].min(), reduced_data[:, 1].max()
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    pl.figure(1)
    pl.clf()
    pl.imshow(Z, interpolation='nearest',
              extent=(xx.min(), xx.max(), yy.min(), yy.max()),
              cmap=pl.cm.Paired,
              aspect='auto', origin='lower')

    pl.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    pl.scatter(centroids[:, 0], centroids[:, 1],
               marker='x', s=169, linewidths=3,
               color='w', zorder=10)

    pl.title('K-means clustering on ' + opts.text_source + ' (PCA-reduced data)\n'
             'Centroids are marked with white cross')
    pl.xlim(x_min, x_max)
    pl.ylim(y_min, y_max)
    pl.xticks(())
    pl.yticks(())
    pl.savefig('clustering.png')

#Kmeans code modified from http://scikit-learn.org/stable/auto_examples/document_clustering.html
#PCA code modified from http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_digits.html
#Statistical definitions from http://scikit-learn.org/stable/modules/clustering.html