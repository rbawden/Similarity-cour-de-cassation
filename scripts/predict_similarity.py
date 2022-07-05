#!/usr/bin/python
import editdistance, re
import unicodedata
import pickle

def read_sfile(filename, n=1):
    '''
    Read a file containing sommaires (one example per line, but there may be multiple titrages                                     
    per line and in this case they should be tab-separated).
    - Filename: the path to the file containing the sommaires
    - n:        (default=None) the maximum number of sommaires that should be kept for each example. If None,
                then all titrages will be used.
    Returns sommaires: a list of examples where each example is a list of sommaires
    '''
    sommaires = []
    with open(filename) as fp:
        for l, line in enumerate(fp):
            sommaires.append(create_list_from_sommaire(remove_accents(line.strip().lower()), n))
    return sommaires

def read_tfile(filename, n=None):
    '''
    Read the file containing titrages (one example per line, but there may be multiple titrages
    per line and in this case they should be tab-separated).
    - Filename: the path to the file containing the titrages
    - n:        (default=None) the maximum number of titrages that should be kept for each example. If None,
                then all titrages will be used.
    Returns titrages: a list of examples where each example is a list of titrages
    '''
    titrages = []
    with open(filename) as fp:
        for l, line in enumerate(fp):
            titrages.append(create_list_from_titrage(remove_accents(line.strip().lower()), n))
    return titrages


def create_list_from_titrage(t, n=None):
    '''
    Convert a string containing one or several (tab-separated) titrages and return a list of titrages, 
    where each titrage is a list of titres.
    - t: the string containing one or several titrages
    - n: the maximum number of titrages to keep for this example. Defaults to None (=keep them all)
    '''
    if n is None:
        return [re.split(' *<t> *', tx) for tx in t.split('\t')]
    else:
        return [re.split(' *<t> *', tx) for tx in t.split('\t')][:n]

def create_list_from_sommaire(s, n=None):
    '''                                                                                                                           
    Convert a string containing one or several (tab-separated) sommaires and return a list of sommaires,
    where each sommaires is a list of tokens.
    - t: the string containing one or several sommaires
    - n: the maximum number of sommaires to keep for this example. Defaults to None (=keep them all)
    '''
    if n is None:
        return [x.split() for x in s.split('\t')]
    else:
        return [x.split() for x in s.split('\t')][:n]

def remove_accents(text):
    '''
    Returns a modified version of the text without accents
    '''
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")

def calculate_norm_edit_distance_similarity(list_t1, list_t2):
    '''
    Returns the edit-distance-based similarity score given two examples each containing a 
    list of titres (for titrages) or a list of words (for somaires).
    '''
    return 1 - (editdistance.eval(list_t1, list_t2) / max(len(list_t1), len(list_t2)))


def calculate_sim_features(gold_titrage1=None, gold_titrage2=None, 
                           pred_titrages1=None, pred_titrages2=None, 
                           sommaires1=None, sommaires2=None):
    '''
    Returns unsupervised similarity features for (i) gold sommaires, (ii) gold titrages
    and (iii) predicted titrages using the edit-distance similarity measure.
    '''
    assert (pred_titrages1 is not None or (pred_titrages1 == pred_titrages2)) and \
        (pred_titrages2 is not None or (pred_titrages1 == pred_titrages2)), \
        'Either predicted titrages must be specified for both cases or for neither of them'
    assert (gold_titrage1 is not None or (gold_titrage1 == gold_titrage2)) and \
        (gold_titrage2 is not None or (gold_titrage1 == gold_titrage2)), \
        'Either gold titrages must be specified for both cases of for neither of them'
    assert (sommaires1 is not None or (sommaires1 == sommaires2)) and (sommaires2 is not None or (sommaires1 == sommaires2)), \
        'Either both sommaires must be specified or neither of them'
    assert pred_titrages1 is not None or gold_titrage1 is not None or sommaires1 is not None, 'You must specify titrages and/or sommaires'

    num_examples = []
    # gold syntheses
    s_scores = None
    if sommaires1 is not None:
        s_scores = []
        for s1, s2 in zip(sommaires1, sommaires2):
            all_scores = []
            for ex_s1 in s1:
                for ex_s2 in s2:
                    all_scores.append(calculate_norm_edit_distance_similarity(ex_s1, ex_s2))
            s_scores.append(max(all_scores))
        num_examples.append(len(s_scores))        

    # gold titrages
    g_scores = None
    if gold_titrage1 is not None:
        g_scores = []
        for g1, g2 in zip(gold_titrage1, gold_titrage2):
            all_scores = []
            for ex_g1 in g1:
                for ex_g2 in g2:
                    all_scores.append(calculate_norm_edit_distance_similarity(ex_g1, ex_g2))
            g_scores.append(max(all_scores))
        num_examples.append(len(g_scores))

    # predicted titrages
    t_scores = None
    if pred_titrages1 is not None:
        t_scores = []
        for t1, t2 in zip(pred_titrages1, pred_titrages2):
            all_scores = []
            for ex_t1 in t1:
                for ex_t2 in t2:
                    all_scores.append(calculate_norm_edit_distance_similarity(ex_t1, ex_t2))
            t_scores.append(max(all_scores))
        num_examples.append(len(t_scores))


    

    assert all([x == num_examples[0] for x in num_examples]), 'Each feature type should have the same number of examples. This is not the case. Check the number of lines in each of the files you pass to this script. There are currently this number of examples per feature:' + str(num_examples)
    return s_scores, g_scores, t_scores


def mlp_predict(model_path, s_scores, g_scores, t_scores):
    '''
    Apply the learned multi-layer perceptron model to the specified features and return the
    predicted similarity scores for each example.
    '''
    model = pickle.load(open(model_path, 'rb'))
    non_null_features=[]
    for feature in s_scores, g_scores, t_scores:
        if feature is not None:
            non_null_features.append(feature)
    input_features = list(zip(*non_null_features))
    preds = model.predict(input_features)
    return preds


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model_path', required=True, 
                        help='Path to pickled model. Make sure it corresponds to the similarity features you specify')
    parser.add_argument('-g', '--gold_titrages', default=None, nargs=2,
                        help='The two files containing the gold titrages, one example per line. If there are multiple gold titrages, they should be tab-separated.')
    parser.add_argument('-p', '--pred_titrages', default=None, nargs=2,
                        help='The two files containing predicted titrages, one example per line. If there are multiple pred titrages, they should be tab-separated.')
    parser.add_argument('-s', '--sommaires', default=None, nargs=2,
                        help='The two files containing gold sommaires, one example per line. If there are multiple gold sommaires, they should be tab-separated. Sommaires should not contain any tabs or newlines (these should be replaced beforehand by spaces).')
    parser.add_argument('-n', '--num_titrages', type=int, default=None, help='The maximum number of predicted titrages to use per example. Defaults to None=all those present in the file will be used.')
    args = parser.parse_args()

    g1, g2 = None, None
    s1, s2 = None, None
    t1, t2 = None, None
    if args.sommaires is not None:
        s1 = read_sfile(args.sommaires[0])
        s2 = read_sfile(args.sommaires[1])
    if args.pred_titrages is not None:
        t1 = read_tfile(args.pred_titrages[0], n=args.num_titrages)
        t2 = read_tfile(args.pred_titrages[1], n=args.num_titrages)
    if args.gold_titrages is not None:
        g1 = read_tfile(args.gold_titrages[0])
        g2 = read_tfile(args.gold_titrages[1])

    s_scores, g_scores, t_scores = calculate_sim_features(g1, g2, t1, t2, s1, s2)
    sim_scores = mlp_predict(args.model_path, s_scores, g_scores, t_scores)
    for score in sim_scores:
        print(score)
