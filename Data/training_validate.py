'''
Classifer Training functions plus cross-validation
'''

# functions to load classifier training data
def load_positivity():
    '''
    Loads positivity data from Stanford IMDB dataset into memory as two lists: one text and the other
    binary 1 = positive, 0 = negative.
    
    This function concatenates the presorted testing and training data into one group.
    
    Output:
        quotes (text data), positivity (binary data)
    
    '''
    
    quotes, positivity = [], []
    
    for path in ['./Data/Training_Data/positivity/train/', './Data/Training_Data/positivity/test/']:
        # load all positive quotes
        for filename in os.listdir(path + 'pos/'):
            if(re.search(u'.txt', filename) is not None):
                with open(path + 'pos/' + filename) as f:
                    data="".join(line.rstrip() for line in f)
                quotes.append(plaintext(data))
                positivity.append(1)
        
        # load all negative quotes
        for filename in os.listdir(path + 'neg/'):
            if(re.search(u'.txt', filename) is not None):
                with open(path + 'neg/' + filename) as f:
                    data="".join(line.rstrip() for line in f)
                quotes.append(plaintext(data))
                positivity.append(0)
    
    return quotes, np.array(positivity)

def load_support():
    '''
    Loads support / oppose data from political speeches dataset into memory as two lists: one text and the other
    binary 1 = support, 0 = no oppose.
    
    This function groups the presorted testing and training groups into one set.
    
    Output:
        quotes (text data), support (binary data)
    
    '''
    
    quotes, support = [], []
    
    for path in ['./Data/Training_Data/support_oppose/data_stage_one/training_set/', 
                 './Data/Training_Data/support_oppose/data_stage_one/test_set/']:
        # load all quotes
        for filename in os.listdir(path):
            if(re.search(u'.txt', filename) is not None):
                with open(path+filename) as f:
                    data="".join(line.rstrip() for line in f)
                quotes.append(plaintext(data))
                
                # determine if last letter is a Y or N for support binary data
                if filename.split('.txt')[0][-1] == 'Y':
                    support.append(1)
                else:
                    support.append(0)
    
    return quotes, np.array(support)

def load_subjectivity():
    '''
    Loads subjectivity data from IMDB summary / Rotten Tomatoes review dataset into memory as two lists: one text and the other
    binary 1 = subjective, 0 = objective.
    
    Output:
        quotes (text data), support (binary data)
        
    There is no automatic split between testing and training data for this dataset.
    
    '''
    
    # load all subjective quotes
    subj = open('./Data/Training_Data/subjectivity/subj')
    subj_quotes, subjectivity = [], []
    
    for line in subj:
        subj_quotes.append(line.rstrip('\n'))
        subjectivity.append(1)
    subj.close()
    
    # load all objective quotes
    obj = open('./Data/Training_Data/subjectivity/obj')
    obj_quotes = []
    
    for line in obj:
        obj_quotes.append(line.rstrip('\n'))
        subjectivity.append(0)
    obj.close
    
    quotes = subj_quotes + obj_quotes
    
    # tranform subjective data into UTF-8
    for idx, item in enumerate(quotes):
        quotes[idx] = item.decode('latin1').encode('utf8')
    
    return quotes, np.array(subjectivity)

# Fit a vectorizer to given data
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

def vectorize_data(quote_list, vectorizer = None, Tfidf = True, min_df = 1, 
                   ngram_range = (1,2), token_pattern = r'\b\w\w+\b'):
    '''
    Vectorizes given data using desired vectorizer object.
    
    Input:
        quote_list: list of data to vectorize
        vectorizer : CountVectorizer object (optional)
            A CountVectorizer object to use. If None,
            then create and fit a new CountVectorizer.
            Otherwise, re-fit the provided CountVectorizer
            using the provided data data
    
    Output:
        numpy array (dims: nreview, nwords)
            Bag-of-words representation for each quote.
    '''
    
    # if no vectorizer was passed, declare a vectorizer object
    if(vectorizer is None): 
        if(Tfidf == False):
            vectorizer = CountVectorizer(min_df = min_df, ngram_range = ngram_range, token_pattern = token_pattern)
        else:
            vectorizer = TfidfVectorizer(min_df = min_df, ngram_range = ngram_range, token_pattern = token_pattern)
    
    # build the vectorizer vocabulary
    vectorizer.fit(quote_list)

    # transform into bag of words
    X = vectorizer.transform(quote_list)
    
    return X.tocsc()

from sklearn.cross_validation import cross_val_score
from sklearn.decomposition import sparse_encode

def log_likelihood(clf, x_vals, y_vals):
    '''
    Computes the log liklihood of a dataset according to a Bayseian classifier
    '''
    
    # generate log liklihood scores
    logP_pos_neg = clf.predict_log_proba(x_vals)
    
    # separate logP(fresh) and logP(rotten) into two lists
    logP_neg = logP_pos_neg[:,0]
    logP_pos = logP_pos_neg[:,1]
    
    # place both lists into a DataFrame
    logP_scores_df = pd.DataFrame({'logP_neg': logP_neg, 'logP_pos': logP_pos, 'actual': y_vals})
    
    # calculate the sums of freshness log scores and rotten log scores
    sum_neg = logP_scores_df[logP_scores_df.actual == 0].logP_neg.sum()
    sum_pos = logP_scores_df[logP_scores_df.actual == 1].logP_pos.sum()
    
    return sum_pos + sum_neg

def testing_score(clf, x_vals, y_vals):
    '''
    Returns the CLF score of a dataset
    '''
    
    return clf.score(x_vals, y_vals)

def cross_validate(X, Y, vectorizers = [CountVectorizer, TfidfVectorizer], ngrams = [(1,1), (1,2)], 
                   alphas = [0, 0.1, 1, 5, 10, 50], min_dfs = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1], 
                   score_methods = [log_likelihood, testing_score]):
    '''
    Performs cross validation of a Naive Bayes classifier's fit.
    
    Inputs:
        X: an unvectorized list of input data
        Y: a numpy array of categories
        vectorizers: list of vectorizing functions
        ngrams: list of ngram tuples to compare
        alphas: list of alpha values to compare
        min_dfs: list of min_df values to compare
        score_methods: list of scoring functions
        
    Outputs:
        Average scores for each condition as a DataFrame
    '''
    # Find the best value for alpha and min_df, and the best classifier
    
    results = []
    
    for score_method in score_methods:
        for vectorizer_func in vectorizers:
            for ngram in ngrams:
                for min_df in min_dfs:
                    for alpha_val in alphas:
                        # declare vectorizer with desired parameters
                        vectorizer = vectorizer_func(min_df = min_df, ngram_range = ngram)       
                        X_vec = vectorize_data(X, vectorizer)
                        
                        # declare the clf object and calculate the score
                        clf = MultinomialNB(alpha = alpha_val)
                        score_array = cross_val_score(clf, X_vec, Y, score_method)
                        
                        # add to DataFrame
                        results.append({'avg_score': np.mean(score_array), 
                                        'scores': score_array,
                                        'vectorizer': vectorizer_func.__name__,
                                        'scoring_method': score_method.__name__,
                                        'ngram': ngram,
                                        'min_df': min_df,
                                        'alpha': alpha_val})
    
    return pd.DataFrame(results)

# pos_X, pos_Y = load_positivity()
# sup_X, sup_Y = load_support()
subj_X, subj_Y = load_subjectivity()

# cv_pos = cross_validate(pos_X, pos_Y)
# cv_sup = cross_validate(sup_X, sup_Y)
cv_subj = cross_validate(subj_X, subj_Y)

cv_subj.to_csv("./cv_subj.csv", encoding = "UTF-8")