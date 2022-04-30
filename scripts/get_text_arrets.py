#!/usr/bin/python
import pandas as pd
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('arrets_file')
parser.add_argument('-e', '--exclude_file', help='file containing document_ids to exclude in first tab-separated column')
args = parser.parse_args()

df_arrets = pd.read_csv(args.arrets_file, sep='∞')
df_arrets = df_arrets.replace('\n',' ', regex=True) # replace all newlines with spaces

exclude = []
if args.exclude_file:
    with open(args.exclude_file) as fp:
        for line in fp:
            exclude.append(line.strip().split('\t')[0])

for index, row in df_arrets.iterrows():
    id_arret = row.values.tolist()
    if id_arret[0] in exclude:
        continue
    arret = id_arret[-1]
    if str(arret) == 'nan':
        continue
    arret = arret.replace('\n', ' ')
    arret = arret.replace('\t', ' ')
    arret = re.sub(' +', ' ', arret)

    print(arret.lower())
