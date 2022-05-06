#!/usr/bin/python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np
import os

def read_file(filename, n=1):
    contents = []
    example = []
    with open(filename) as fp:
        for l, line in enumerate(fp):
            example.append(line.strip())
            if len(example) == n:
                contents.append(example)
                example = []
    assert len(example) == 0, 'The number of examples is not correct'
    return contents


def train_tfidf(texts, model_output_path, gram=1, max_vocab=None):
    texts = [x for y in texts for x in y]
    if max_vocab == -1:
        max_vocab = None
    # tf-idf based vectors (add stop words?)
    if os.path.exists(model_output_path):
        os.sys.stderr.write('Model already exists. Delete to retrain.\n')
        fit_model = pickle.load(open(model_output_path, 'rb'))
    else:
        os.sys.stderr.write('Training new TFIDF model on the texts provided.\n')
        model = TfidfVectorizer(analyzer='word', strip_accents='unicode', 
                                ngram_range=(1, gram), lowercase=True, max_features=max_vocab)
        fit_model = model.fit(texts) # Fit the model
        pickle.dump(fit_model, open(model_output_path, "wb"))

    return fit_model


def predict(texts1, texts2, fit_model, calc='avg', k=1):
    assert calc in ['max', 'avg'], 'Function should be one of "max", "avg"'
    all_scores = []
    for i in range(len(texts1)):
        x1s = fit_model.transform(texts1[i][:k])
        x2s = fit_model.transform(texts2[i][:k])
        scores = []
        for i in range(x1s.shape[0]):
            score = cosine_similarity(x1s[i], x2s[i])[0][0]
            scores.append(score)
        if calc == 'avg':
            all_scores.append(max(scores))
        elif calc == 'max':
            all_scores.append(sum(scores)/len(scores))
    return all_scores


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+', required=True)
    parser.add_argument('-o', '--output_model', required=True)
    parser.add_argument('-g', '--gram', default=1, type=int)
    parser.add_argument('-m', '--max_vocab', default=None, type=int)
    parser.add_argument('-p', '--predict', default=False, help='do predict as well as training', action='store_true')

    # prediction parameters
    parser.add_argument('-t', '--type_calc', choices=('max', 'avg'), default='max')
    parser.add_argument('-n', '--number_texts_per_example', type=int, default=1, help='the number of texts provided per example')
    parser.add_argument('-k', '--number_texts_to_use', type=int, default=1, help='the number of texts to look at per example')
    args = parser.parse_args()

    # get trained model
    text_files = []
    for filename in args.files:
        text_files.append(read_file(filename, args.number_texts_per_example))
    # use all texts to train (if not already trained)
    model = train_tfidf([y for x in text_files for y in x], args.output_model, 
                        max_vocab=args.max_vocab, gram=args.gram)

    # apply model to texts
    if args.predict:
        assert len(text_files) == 2 and len(text_files[0]) == len(text_files[1]), \
            'There should be 2 files of equal length to do predictions'
        corrs = predict(text_files[0], text_files[1], model, calc=args.type_calc, k=args.number_texts_to_use)
        for corr in corrs:
            print(corr)
