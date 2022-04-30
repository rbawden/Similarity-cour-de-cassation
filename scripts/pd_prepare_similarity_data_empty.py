#!/usr/bin/python
import pandas as pd
import argparse
import re
import numpy as np
from create_dataset_split import clean_titrage_list

parser = argparse.ArgumentParser()
parser.add_argument('orig_similarity_file')
parser.add_argument('titres_sommaires_orig')
args = parser.parse_args()

df_annot = pd.read_csv(args.orig_similarity_file, sep=",", encoding="utf-8")

# remove examples with no annotations
df_annot = df_annot.replace("<à compléter>", 1)
#df_annot = df_annot.dropna(subset=["ANNOT_SIMIL1"])[:]
#df_annot = df_annot.astype({"ANNOT_SIMIL1" : "float", "ANNOT_SIMIL2" : "float"})
#df_annot = df_annot.astype({"ID_DOCUMENT" : "int", "ID_DOCUMENT2" : "int"})


#ID_CHAMBRE 1,ID_CHAMBRE 2,similarité annotée 1,annotateur 1,similarité annotée 2,annotateur 2,ID_DOCUMENT,N° POURVOI,N° POURVOI,N° POURVOI,ID_CHAMBRE,TITRAGE,SOMMAIRE
# output basic information
subset_df = df_annot[['ID_CHAMBRE', 'ID_DOCUMENT', 'TITRAGE', 'SOMMAIRE']]

data = df_annot.to_dict('records')


# clean up entries
# 1. Titrage
# 2. Some of the lines are split in 2 (where no second document id present) so merge these
new_data, pair = [], []
for e, example in enumerate(data):
    if str(example['TITRAGE']) == 'nan':
        continue
    example['TITRAGE'] = example['TITRAGE'].strip(' \|')
                 
    pair.append(example)
    
    if len(pair) == 2:
        new_data.append(pair)
        pair = []

assert len(pair) != 1, 'must not have one odd one'
if len(pair) == 2:
    new_data.append(pair)

print('Number of examples = ', len(new_data))

for pair in new_data:
    assert str(pair[0]['ID_DOCUMENT']) != 'nan' and str(pair[1]['ID_DOCUMENT']) != 'nan', 'docid must be specified'

longer = 0
# associate titrages, sommaires and arrêts and id numbers
df_tiso = pd.read_csv(args.titres_sommaires_orig, sep="\t")

for p, pair in enumerate(new_data):
    doc1 = df_tiso[df_tiso['ID_DOCUMENT'] == int(pair[0]['ID_DOCUMENT'])]
    doc2 = df_tiso[df_tiso['ID_DOCUMENT'] == int(pair[1]['ID_DOCUMENT'])]

    if len(doc1) == 0 or len(doc2) == 0:
        continue

    assert len(doc1) >= 1, 'There should be a single row possible doc1'
    assert len(doc2) >= 1, 'There should be a single row possible doc2'

    # get titrage from test set
    orig_titrages1 = doc1[['PM', 'AM1', 'AM2', 'AM3', 'AM4', 'AM5', 'AM6', 'AM7', 'AM8', 'AM9', 'AM10', 'AM11', 'AM12']].values
    orig_titrages1 = [list(x) for x in orig_titrages1]
    orig_titrages2 = doc2[['PM', 'AM1', 'AM2', 'AM3', 'AM4', 'AM5', 'AM6', 'AM7', 'AM8', 'AM9', 'AM10', 'AM11', 'AM12']].values
    orig_titrages2 = [list(x) for x in orig_titrages2]
    
    str_titrages1 = [' | '.join([x.strip() for x in orig_titrage1 if str(x) != 'nan']).lower() for orig_titrage1 in orig_titrages1]
    str_titrages2 = [' | '.join([x.strip() for x in orig_titrage2 if str(x) != 'nan']).lower() for orig_titrage2 in orig_titrages2]

    # compare to titrage in the similarities file to make sure it is the right one
    sim_titrage1 = ' | '.join(clean_titrage_list(re.sub(' +', ' ', pair[0]['TITRAGE']).split(' | '))).lower().strip()
    sim_titrage2 = ' | '.join(clean_titrage_list(re.sub(' +', ' ', pair[1]['TITRAGE']).split(' | '))).lower().strip()

    # find matching titrage for 1st document
    for t, titrage in enumerate(str_titrages1):
        if sim_titrage1 == titrage:
            doc1_idx = t

    # find matching titrage for 1st document
    for t, titrage in enumerate(str_titrages2):
        if sim_titrage2 == titrage:
            doc2_idx = t

    if len(doc2) > 1:
        print(sim_titrage2)
        print(str_titrages2[0])
        input()

    if doc2_idx != 0:
        print(doc2_idx)
        input()
exit()

# final integrity checks
assert all([str(ex['ID_DOCUMENT']) != 'nan' for ex in new_data])
assert all([str(ex['ID_DOCUMENT2']) != 'nan' for ex in new_data])

# typing
for e in range(len(new_data)):
    new_data[e]['ID_DOCUMENT'] = str(int(new_data[e]['ID_DOCUMENT']))
    new_data[e]['ID_DOCUMENT2'] = str(int(new_data[e]['ID_DOCUMENT2']))

# print out final dataframex
print('\t'.join(['id_chamber1', 'id_chamber2', 'similarity1', 'similarity2', 'annotator1', 'annotator2', 'id_document1', 'id_document2']))
def applytab(row):
    print('\t'.join(map(str, row.values)))
subset_df.apply(applytab, axis=1)

longer += 1
