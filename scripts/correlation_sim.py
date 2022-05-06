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

def train_model_folds(xs, ys, model_type='linear', name=''):

    print(name + '\tmodel type\t' + model_type)
    print(name + '\t#features\t' + str(xs.shape[-1]))
    if xs.shape[-1] == 1:
        print(name + '\tnon-trained r\t', pearsonr(xs.squeeze(-1), ys)[0])        
    
    splitter = ShuffleSplit(n_splits=20, test_size=0.5, random_state=0)
    scores_det, scores_r2, scores_corr = [], [], []
    slopes, inter = [], []
    for train_idx, test_idx in splitter.split(xs, ys):
        X_train = xs[train_idx]
        X_test = xs[test_idx]
        y_train = ys[train_idx]
        y_test = ys[test_idx]

        if model_type == 'linear':
            model = LinearRegression().fit(X_train, y_train)
        else:
            model = MLPRegressor(max_iter=2000, hidden_layer_sizes=(48,48,48)).fit(X_train, y_train)

        preds = model.predict(X_test)
            
        # correlations
        r2 = r2_score(y_test, preds)
        pearsons = pearsonr(preds, y_test)[0]
        scores_r2.append(r2)
        scores_corr.append(pearsons)

    scores_r2_ave = sum(scores_r2) / len(scores_r2)
    scores_corr_ave = sum(scores_corr) / len(scores_corr)
    print(name + '\ttrained r\t' + str(scores_corr_ave))
        

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gold', required=True)
    parser.add_argument('-m', '--model_type', choices=('linear', 'mlp'), default='linear')
    parser.add_argument('-n', '--name', default = '')
    args = parser.parse_args()

    # read gold and features
    gold = read_gold(args.gold)
    xs, ys = read_input_data(gold)
    assert len(gold) == xs.shape[0], 'There should be the same number of gold labels as examples'

    # train models
    model = train_model_folds(xs, ys, model_type=args.model_type, name=args.name)
