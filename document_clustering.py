from __future__ import print_function

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD


from optparse import OptionParser
import sys

import numpy as np
from pandas import read_csv

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
op.add_option("--n-features", type=int, default=10000,
              help="Maximum number of features (dimensions)"
                   "to extract from text.")
op.add_option("--verbose",
              action="store_true", dest="verbose", default=False,
              help="Print progress reports inside k-means algorithm.")

(opts, args) = op.parse_args()
if len(args) > 0:
    op.error("this script takes no arguments.")
    sys.exit(1)

###############################################################################

#load data (will already be done when scripts are combined)
all_data = read_csv('./Data/all_data.csv')
#uncomment the following to only analyze articles about candidates
#all_data = all_data[(all_data['candidate'] == 'Romney') | (all_data['candidate'] == 'Obama')]

#turn list of sources into np array
labels = np.array(all_data[['source']].to_dict('list').values()[0])
#turn list of abstracts into a list
abstracts = all_data[['abstract']].to_dict('list').values()[0]
#source_num is number of unique sources
source_num = np.unique(labels).shape[0]

#print number of abstracts and sources
print("%d abstracts" % len(abstracts))
print("%d sources" % source_num)

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
                                 stop_words='english', use_idf=opts.use_idf)
X = vectorizer.fit_transform(abstracts)

print("n_samples: %d, n_features: %d" % X.shape)
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

print("Clustering sparse data with %s" % km)
km.fit(X)
print()

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

#Code modified from http://scikit-learn.org/stable/auto_examples/document_clustering.html
#Statistical definitions from http://scikit-learn.org/stable/modules/clustering.html