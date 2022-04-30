#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('gold_titrage')
parser.add_argument('pred_titrage')
args = parser.parse_args()

def read_file(filename):
    content = []
    with open(filename) as fp:
        for line in fp:
            content.append(line.strip())
    return content

gold_titrages = read_file(args.gold_titrage)
pred_titrages = read_file(args.pred_titrage)

num_titrages = len(gold_titrages)
num_per_titrages = len(pred_titrages) / num_titrages

t = 0
for p, pred_titrage in enumerate(pred_titrages):
    # print the gold titrage every xth predicted titrage (first one)
    if p % num_per_titrages == 0:
        print(gold_titrages[t])
        t += 1
    print(pred_titrage)
    p += 1
