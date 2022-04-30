#!/usr/bin/python
import pandas as pd
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('arrets_file')
parser.add_argument('sim_dataset')
parser.add_argument('output_prefix')
args = parser.parse_args()

df_arrets = pd.read_csv(args.arrets_file, sep='∞')
df_arrets = df_arrets.replace('\n',' ', regex=True) # replace all newlines with spaces


with open(args.sim_dataset) as fp, \
     open(args.output_prefix + '1', 'w') as ofp1, \
     open(args.output_prefix + '2', 'w') as ofp2:
    fp.readline() # eat up header line
    for line in fp:
        tabline = line.split('\t')
        doc1, doc2 = tabline[2], tabline[3]

        arret1 = df_arrets[df_arrets['ID_DOCUMENT']==int(doc1)].values.tolist()[0][-1]
        arret2 = df_arrets[df_arrets['ID_DOCUMENT']==int(doc2)].values.tolist()[0][-1]

        arret1.replace('\n', ' ')
        arret1.replace('\t', ' ')
        arret2.replace('\n', ' ')
        arret2.replace('\t', ' ')

        ofp1.write(arret1.lower() + '\n')
        ofp2.write(arret2.lower() + '\n')
        
        
