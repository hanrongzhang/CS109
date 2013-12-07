from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.naive_bayes import MultinomialNB
import numpy as np

import pandas as pd

# import training data
training_set = pd.read_csv('training_set.csv')

# take only snippets where the two independent sentiment tags agree
training_set = training_set[training_set['Agreement'] == 'TRUE']

# sort and tag sets
tagged = []
for index, snippet  in training_set.iterrows():
	if any([snippet['Ann1'] == 'POS', snippet['Ann2'] == 'POS', snippet['Ann3'] == 'POS', snippet['Ann4'] == 'POS']):
		tagged.append((snippet['Quote'], 'pos'))

	elif any([snippet['Ann1'] == 'NEG',snippet['Ann2'] == 'NEG',snippet['Ann3'] == 'NEG',snippet['Ann4'] == 'NEG']):
		text_filtered = [s.lower() for s in snippet['Quote'].split() if len(s) > 2]
		tagged.append((snippet['Quote'], 'neg'))

# prepare feature extractor



def vectorize_trainer(training_data, vectorizer = None):
	if vectorizer == None:
		vec = CountVectorizer(charset_error='ignore', min_df=0)
	else:
		vec = vectorizer

	Y = np.empty(len(training_data))

	words = []
	for index,(quote,sentiment) in enumerate(training_data):
		words.append(quote)
		Y[index] = 1 if sentiment == 'pos' else 0

	vec.fit(words)

	bag = vec.transform(words)
	bag = bag.toarray()

	X = np.array(bag)

	return X,Y,vec

# running classifer on randomly split test/train data
X,Y,vec = vectorize_trainer(tagged)
X_train, X_test, Y_train, Y_test = train_test_split(X,Y)
clf = MultinomialNB()
clf = clf.fit(X_train, Y_train)
# print clf.score(X_test, Y_test)
# print clf.score(X_train, Y_train)

# TODO implement cross-validation and model refinement

def classify_data(data_csv, vectorizer=vec):
	df = pd.read_csv(data_csv, encoding = 'UTF-8')

	s_list = []
	neg_list = []
	pos_list = []
	for index,item in df.iterrows():
		bag = vectorizer.transform([item['headline'] + item['abstract']])
		classified = np.array(bag.toarray())
		sentiment = clf.predict(classified)
		probs = clf.predict_proba(classified)
		s_list.append(sentiment)
		neg_list.append(probs[0][0])
		pos_list.append(probs[0][1])

	df['sentiment'] = s_list
	df['neg'] = neg_list
	df['pos'] = pos_list
	return df

classify_data('all_data.csv').drop('Unnamed: 0',1).to_csv("./all_data_sentiment.csv", encoding = "UTF-8")
