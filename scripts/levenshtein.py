#!/usr/bin/python
import editdistance, re

def calculate_norm_edit_distance_similarity(t1, t2):
    return 1 - (editdistance.eval(list_t1, list_t2) / max(len(list_t1), len(list_t2)))

def create_list_from_titrage(t):
    list_t = re.split(' *<t> *', t)
    return list_t

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('titrage1', help='First titrage, of the form "renonciation <t> correspondence entre les trucs <t> peuple ...')
    parser.add_argument('titrage2', help='Second titrage, of the form "renonciation <t> correspondence entre les trucs <t> peuple ...')
    args = parser.parse_args()

    t1 = create_list_from_titrage(args.titrage1)
    t2 = create_list_from_titrage(args.titrage2)
    dist = calculate_norm_edit_distance_similarity(t1, t2)
    print(dist)
