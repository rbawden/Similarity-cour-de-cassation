#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

def remove_accents(text):
    """Remove accents from a text."""
    replace_from = "ǎắāǽǣáàâäąãăåĉćčçďέĕēếệéèêëęěġğĝĥὶǐιίīìíîĩĭıïĵĺľłῆήṇṅńñňŏởộǒōòóôõöøŗŕřŝśšşṭťţύŭủūùúûũüǔỳýŷÿźẑżžÁ\
ÀÂÄĄÃĂÅĆČÇĎÉÈÊËĘĚĞÌÍÎĨĬİÏĹĽŁŃÑŇÒÓÔÕÖØŔŘŚŠŞŤŢÙÚÛŨÜǓỲÝŶŸŹẐŻŽ"
    replace_into = "aaaææaaaaaaaaccccdεeeeeeeeeeeggghiiiiiiiiiiiijlllηηnnnnnooooooooooorrrsssstttυuuuuuuuuuyyyyzzzzA\
AAAAAAACCCDEEEEEEGIIIIIIILLLNNNOOOOOORRSSSTTUUUUUUYYYYZZZZ"
    table = text.maketrans(replace_from, replace_into)
    text = text.replace("œ", "oe").replace("Œ", "OE") # RB: switched round                                           
    return text.translate(table)

def read_titrage_file(filename, no_accents=False):
    titrages = []
    with open(filename) as fp:
        for line in fp:
            if no_accents:
                titrages.append(re.split(' *<t> *', remove_accents(line.strip())))
            else:
                titrages.append(re.split(' *<t> *', line.strip()))
    return titrages


def global_accuracy(hyps, refs):
    return sum([1 for i in range(len(hyps)) if hyps[i] == refs[i]])/len(hyps)

def micro_accuracy(hyps, refs):
    correct = 0
    total = 0
    for hyp, ref in zip(hyps, refs):
        maxlen = max(len(hyp), len(ref))
        for i in range(maxlen):
            total += 1
            if i >= len(hyp) or i>= len(ref):
                continue
            elif hyp[i] == ref[i]:
                correct += 1
    return correct/total


def accuracy_per_level(hyps, refs):
    level2count = {}
    for hyp, ref in zip(hyps, refs):
        maxlen = max(len(hyp), len(ref))
        for i in range(maxlen):
            if i not in level2count:
                level2count[i] = {'correct': 0, 'total': 0}
            level2count[i]['total'] += 1
            if i >= len(hyp) or i>= len(ref):
                continue
            elif hyp[i] == ref[i]:
                level2count[i]['correct'] += 1

    return [level2count[level]['correct']/level2count[level]['total'] for level in sorted(level2count)]

def weighted_from_level_acc(accuracies):
    weights = [1 / (3.85 * (n**0.8)) for n in range(1, len(accuracies) + 1)]
    return sum([acc * weights[a] for a, acc in enumerate(accuracies)])

# macro-averge of accuracies per level                
def weighted_accuracy(hyps, refs):
    accuracies = accuracy_per_level(hyps, refs)
    weights = [1 / (3.85 * (n**0.8)) for n in range(1, len(accuracies) + 1)]
    return sum([acc * weights[a] for a, acc in enumerate(accuracies)])


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('hyp_file')
    parser.add_argument('ref_file')
    parser.add_argument('eval_type', choices=('global_acc', 'acc_per_level', 'weighted_acc', 'micro_acc'))
    parser.add_argument('-n', '--no_accents', help='remove accents when evaluating', action='store_true', default=False)
    args = parser.parse_args()
    
    hyps = read_titrage_file(args.hyp_file, args.no_accents)
    refs = read_titrage_file(args.ref_file, args.no_accents)

    assert len(hyps) == len(refs), 'Ref and hyp must be of the same length'
    
    if args.eval_type == 'global_acc':
        score = global_accuracy(hyps, refs)
    elif args.eval_type == 'acc_per_level':
        score = accuracy_per_level(hyps, refs)
    elif args.eval_type == 'weighted_acc':
        score = weighted_accuracy(hyps, refs)
    else:
        score = micro_accuracy(hyps, refs)

    if type(score) == float:
        print(round(score * 100, 3))
    elif type(score) == list:
        print([round(s * 100) for s in score])







