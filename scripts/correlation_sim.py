# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor, MLPClassifier
from scipy.stats import pearsonr
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import r2_score
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import StandardScaler
import pickle
import numpy as np
import os, sys, random

# assume input has the gold as the first features
def read_input_data(gold):
    xs, ys = [], []
    g = 0
    for line in sys.stdin:
        tabline = [float(x) for x in line.strip().split()]
        #tabline = [random.randint(0, 5), random.randint(0, 5)] # random for testing purposes
        xs.append(tabline)
        ys.append(gold[g])
        g += 1
    return np.array(xs), np.array(ys)

def read_docids(filename):
    docids = []
    with open(filename) as fp:
        for line in fp:
            docids.append(int(line.strip()))
    return docids

def read_gold(filename):
    gold = []
    with open(filename) as fp:
        for line in fp:
            gold.append(float(line.strip()))
    return gold

def train_model_folds(xs, ys):

    print('Number of features detected = ', xs.shape[-1])
    # single feature, just calculate score
    if xs.shape[-1] == 1:
        print('r2 = ', r2_score(xs.squeeze(-1), ys))
        print('pearsons = ', pearsonr(xs.squeeze(-1), ys)[0])        
        
    if True:

        splitter = ShuffleSplit(n_splits=5, test_size=0.5, random_state=0)
        scores_det, scores_r2, scores_corr = [], [], []
        slopes, inter = [], []
        for train_idx, test_idx in splitter.split(xs, ys):
            X_train = xs[train_idx]
            X_test = xs[test_idx]
            y_train = ys[train_idx]
            y_test = ys[test_idx]

            #sc_X = StandardScaler()
            #X_trainscaled=sc_X.fit_transform(X_train)
            #X_testscaled=sc_X.transform(X_test)
            
            #model = MLPClassifier(max_iter=2000, hidden_layer_sizes=(64,64,64)).fit(X_train, y_train)
            #model = MLPRegressor(max_iter=2000, hidden_layer_sizes=(64,64,64)).fit(X_train, y_train)
            #model = LinearRegression().fit(X_train, y_train)
            preds = model.predict(X_test)
            
            # correlations
            r2 = r2_score(y_test, preds)
            pearsons = pearsonr(preds, y_test)[0]
            scores_r2.append(r2)
            scores_corr.append(pearsons)
            #print('-----')
            #print('det coeff = ', det_coeff, ', r2 = ', r2, 'pearsons r = ', pearsons)
            #print('fit params = ', model.coef_, model.intercept_)
            #slopes.append(model.coef_)
            #inter.append(model.intercept_)

        scores_r2_ave = sum(scores_r2) / len(scores_r2)
        scores_corr_ave = sum(scores_corr) / len(scores_corr)
        print('------')
        print('averages = ')
        print('r2 = ', scores_r2_ave, 'pearsons r = ', scores_corr_ave)
        #print('slope = ', sum(slopes)/len(slopes), 'intercept = ', sum(inter)/len(inter))


    

# OLD
def train_model(xs, ys, model_output_path):
    if os.path.exists(model_output_path):
        os.sys.stderr.write('Model already exists. Delete to retrain.\n')
        fit_model = pickle.load(open(model_output_path, 'rb'))
    else:
        os.sys.stderr.write('Training new model on the texts provided.\n')
        fit_model = LinearRegression().fit(xs, ys)
        pickle.dump(fit_model, open(model_output_path, "wb"))    
        print(fit_model.coef_, fit_model.intercept_, fit_model.score(xs, ys))
    return fit_model

# OLD
def predict(xs, ys, fit_model):
    preds = fit_model.score(x1s)
    x2s = fit_model.transform(texts2)

    preds = fit_model.predict(xs)
    det = fit_model.score(xs, ys) # coefficient of determination
    det2 = r2score(ys, preds)

    print('det = ', det)
    print('det2 = ', det2)
                                 
    

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    #xparser.add_argument('-f', '--feature_file', required=True)
    #parser.add_argument('-d', '--docids', required=True)
    parser.add_argument('-g', '--gold', required=True)
    #parser.add_argument('-o', '--output_model', required=True)
    #parser.add_argument('-p', '--predict', default=False, help='do predictions', action='store_true')
    args = parser.parse_args()

    # features
    #docids = read_docids(args.docids)
    gold = read_gold(args.gold)
    xs, ys = read_input_data(gold)
    assert len(gold) == xs.shape[0], 'There should be the same number of gold labels as examples'

    # train models
    model = train_model_folds(xs, ys)
