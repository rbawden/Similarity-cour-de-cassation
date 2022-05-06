#!/usr/bin/python
import editdistance, re
import unicodedata

def calculate_norm_edit_distance_similarity(list_t1, list_t2):
    return 1 - (editdistance.eval(list_t1, list_t2) / max(len(list_t1), len(list_t2)))

def create_list_from_titrage(t):
    return re.split(' *<t> *', t)

def create_list_from_sommaire(s):
    return s.split()

def remove_accents(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")

def read_sfile(filename, n=1):
    sommaires = []
    examples = []
    with open(filename) as fp:
        for l, line in enumerate(fp):
            examples.append(create_list_from_sommaire(remove_accents(line.strip().lower())))
            if len(examples) == n:
                sommaires.append(examples)
                examples = []
    assert len(examples) == 0, 'There is a strange number of lines given the value n=' + str(n)
    return sommaires

def read_tfile(filename, n=1):
    titrages = []
    examples = []
    with open(filename) as fp:
        for l, line in enumerate(fp):
            examples.append(create_list_from_titrage(remove_accents(line.strip().lower())))
            if len(examples) == n:
                titrages.append(examples)
                examples = []
    assert len(examples) == 0, 'There is a strange number of lines given the value n=' + str(n)
    return titrages

def calculate_sims(t1s, t2s, k=1, type_calc='max'):
    assert type_calc in ['max', 'avg']
    final_scores = []
    for t1, t2 in zip(t1s, t2s):
        # get all the examples to be compared
        exs_t1, exs_t2 = t1[:k], t2[:k]
        all_scores = []
        for ex1 in exs_t1:
            for ex2 in exs_t2:
                score = calculate_norm_edit_distance_similarity(ex1, ex2)
                all_scores.append(score)

        if type_calc == 'max':
            final_score = max(all_scores)
        elif type_calc == 'avg':
            final_score = sum(all_scores)/len(all_scores)
        final_scores.append(final_score)
            
    return final_scores
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('t1_file')
    parser.add_argument('t2_file')
    parser.add_argument('type_calc', choices=('max', 'avg'))
    parser.add_argument('-s', '--sommaire', action='store_true', help='These are summaries and not titrages')
    parser.add_argument('-n', '--number_titrages_per_example', type=int, default=1, help='the number of titrages provided per example')
    parser.add_argument('-k', '--number_titrages_to_use', type=int, default=1, help='the number of titrages to look at per example')
    args = parser.parse_args()

    assert args.number_titrages_to_use <= args.number_titrages_per_example, 'k must be smaller than or equal to n'
    
    if args.sommaire:
        t1s = read_sfile(args.t1_file, args.number_titrages_per_example)
        t2s = read_sfile(args.t2_file, args.number_titrages_per_example)
    else:
        t1s = read_tfile(args.t1_file, args.number_titrages_per_example)
        t2s = read_tfile(args.t2_file, args.number_titrages_per_example)

    final_scores = calculate_sims(t1s, t2s, args.number_titrages_to_use, args.type_calc)
    for score in final_scores:
        print(score)
