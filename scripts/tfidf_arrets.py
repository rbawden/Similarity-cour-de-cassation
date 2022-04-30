# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np
import os

def read_file(filename):
    contents = []
    with open(filename) as fp:
        for line in fp:
            contents.append(line.strip())
    return contents

def train_tfidf(texts, model_output_path):
    # tf-idf based vectors (add stop words?)
    if os.path.exists(model_output_path):
        os.sys.stderr.write('Model already exists. Delete to retrain.\n')
        fit_model = pickle.load(open(model_output_path, 'rb'))
    else:
        os.sys.stderr.write('Training new TFIDF model on the texts provided.\n')
        model = TfidfVectorizer(analyzer='word', ngram_range=(1,3), lowercase = True, max_features = 1000000)
        fit_model = model.fit(texts) # Fit the model
        pickle.dump(fit_model, open(model_output_path, "wb"))    
    return fit_model

def predict(texts1, texts2, fit_model):
    # Create new tfidfVectorizer with old vocabulary
    # = TfidfVectorizer(analyzer='word', ngram_range=(1,4), lowercase = True,
    #                          max_features = 500000, vocabulary = fit_model.vocabulary_)
    
    x1s = fit_model.transform(texts1)
    x2s = fit_model.transform(texts2)

    corrs = []
    for i in range(x1s.shape[0]):
        corr = cosine_similarity(x1s[i], x2s[i])[0][0]
        corrs.append(corr)
    return corrs
                                 
    

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+', required=True)
    parser.add_argument('-o', '--output_model', required=True)
    parser.add_argument('-p', '--predict', default=False, help='do predict as well as training', action='store_true')
    args = parser.parse_args()

    # get trained model
    arret_files = []
    for filename in args.files:
        arret_files.append(read_file(filename))
    # use all texts to train (if not already trained)
    model = train_tfidf([y for x in arret_files for y in x], args.output_model)

    # apply model to texts
    if args.predict:
        assert len(arret_files) == 2 and len(arret_files[0]) == len(arret_files[1]), \
            'There should be 2 files of equal length to do predictions'
        corrs = predict(arret_files[0], arret_files[1], model)
        for corr in corrs:
            print(corr)
