import pdb
import numpy
import time

import pprint as pp

from pandas                          import DataFrame
from itertools                       import izip
from sklearn.pipeline                import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model            import SGDClassifier
from sklearn.naive_bayes             import GaussianNB
from sklearn.model_selection         import KFold
from sklearn                         import svm
from sklearn.model_selection         import GridSearchCV

rows = []
with open('../training_data/tlc_items') as text, open('../training_data/top_level_category') as labels:
    for string, label in izip(text, labels):
        if label.rstrip() in ['Beer', 'Wine', 'Liquor']:
            rows.append({
                'text': string.rstrip(),
                'labels': 'alcohol'
            })
        elif label.rstrip() in ['Extra', 'Extras']:
            rows.append({
                'text': string.rstrip(),
                'labels': 'non-alcohol'
            })

data = DataFrame(rows)
data = data.reindex(numpy.random.permutation(data.index))

###########################
#
# Build the pipelines
#
###########################

# uncommenting more parameters will give better exploring power but will
# increase processing time in a combinatorial way
parameters = {
    'vectorizer__max_df': (0.5, 0.75, 1.0),
    #'vectorizer__max_features': (None, 5000, 10000, 50000),
    'vectorizer__ngram_range': ((1, 1), (1, 2)),  # unigrams or bigrams
    #'tfidf_transformer__use_idf': (True, False),
    #'tfidf_transformer__norm': ('l1', 'l2'),
    'classifier__alpha': (0.00001, 0.000001),
    'classifier__penalty': ('l2', 'elasticnet'),
    #'classifier__n_iter': (10, 50, 80),
}

pipeline = Pipeline([
    ('vectorizer', CountVectorizer(ngram_range=(1,2), max_df=0.75)),
    ('tfidf_transformer', TfidfTransformer()),
    ('classifier', SGDClassifier(alpha=1e-06))
])

###########################
#
# Grid Search to find best parameters
#
###########################

# grid_search = GridSearchCV(pipeline, {}, n_jobs=-1, verbose=1)

# print("Performing grid search...")
# print("pipeline:", [name for name, _ in pipeline.steps])
# print("parameters:")
# pp.pprint(parameters)
# t0 = time.time()
# grid_search.fit(data['text'].values, data['labels'].values)
# print("done in %0.3fs" % (time.time() - t0))
# print()

# print("Best score: %0.3f" % grid_search.best_score_)
# print("Best parameters set:")
# best_parameters = grid_search.best_estimator_.get_params()
# for param_name in sorted(parameters.keys()):
#     print("\t%s: %r" % (param_name, best_parameters[param_name]))

# best results from first run
# classifier__alpha: 1e-06
# classifier__penalty: 'l2'
# vectorizer__max_df: 0.75
# vectorizer__ngram_range: (1, 2)

###########################
#
# Validate the model
#
###########################
kf = KFold(n_splits=6)
for train_indices, test_indices in kf.split(data):
    train_text   = data.iloc[train_indices]['text'].values
    train_labels = data.iloc[train_indices]['labels'].values

    test_text   = data.iloc[test_indices]['text'].values
    test_labels = data.iloc[test_indices]['labels'].values

    pipeline.fit(train_text, train_labels)
    predictions = pipeline.predict(test_text)

    count_correct = 0
    for i, prediction in enumerate(predictions):
        if prediction == test_labels[i]:
            count_correct += 1
        # else:
        #     print('wrong: ', test_text[i], prediction)
        #     print("\n")

    print('Correct:', count_correct)
    print('Total:', len(predictions))
    print('Percentage:', (float(count_correct) / len(predictions)) * 100)
    print("\n")