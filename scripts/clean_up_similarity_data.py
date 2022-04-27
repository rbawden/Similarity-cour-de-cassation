#!/usr/bin/python
import pandas as pd
import argparse
import re, os
import numpy as np
from create_dataset_split import clean_titrage_list

parser = argparse.ArgumentParser()
parser.add_argument('orig_similarity_file')
parser.add_argument('blank_similarity_file')
parser.add_argument('titres_sommaires_orig')
args = parser.parse_args()

def prepare_empty_df(df_blank):
    #subset_df = df_blank[['ID_CHAMBRE', 'ID_DOCUMENT', 'TITRAGE', 'SOMMAIRE']]
    data = df_blank.to_dict('records')
    # clean up entries
    # 1. Titrage
    # 2. Some of the lines are split in 2 (where no second document id present) so merge these
    new_data, pair = {}, []
    for e, example in enumerate(data):
        if str(example['TITRAGE']) == 'nan':
            continue
        example['TITRAGE'] = example['TITRAGE'].strip(' \|')
        pair.append(example)
        if len(pair) == 2:
            docs = (pair[0]['ID_DOCUMENT'], pair[1]['ID_DOCUMENT'])
            if docs in new_data:
                for idx in range(0, 1):
                    for key in pair[idx]:
                        assert str(pair[idx][key]) == str(new_data[docs][idx][key])
                        #print('duplicate but same values')
            new_data[docs] = pair # it is round the wrong way in the similarity file
            pair = []

    assert len(pair) != 1, 'must not have one odd one'
    if len(pair) == 2:
        new_data.append(pair)

    return new_data

def prepare_sim_df(df_annot):
    # remove examples with no annotations
    df_annot = df_annot.replace("<à compléter>", np.NaN)
    df_annot = df_annot.dropna(subset=["ANNOT_SIMIL1"])[:]

    # output basic information
    subset_df = df_annot[['ID_CHAMBRE1', 'ID_CHAMBRE2', 'ANNOT_SIMIL1', 'Annotateur1', 
                          'ANNOT_SIMIL2', 'Annotateur2', 'ID_DOCUMENT', 'ID_DOCUMENT2']]

    data = df_annot.to_dict('records')

    # clean up entries
    # 1. Titrage
    # 2. Some of the lines are split in 2 (where no second document id present) so merge these
    new_data = []
    partial = False
    for e, example in enumerate(data):
        example['TITRAGE'] = example['TITRAGE'].strip(' \|')
        if partial:
            # switch these round because second entry looks more complete
            #tmp = new_data[-1]
            #new_data[-1] = example
            #example = tmp
            #print(new_data[-1])
            # find the most complete of the two annotations
            #if str(example['ID_DOCUMENT']) != 'nan' and str(example['ID_DOCUMENT2']) != 'nan':
            #example['TITRAGE1'] = example['TITRAGE']
            #example['SOMMAIRE1'] = example['SOMMAIRE']
            new_data[-1] = example

            # check non-empty infos
            assert str(example['ID_CHAMBRE1']) != 'nan', 'id_chambre1 must be specified'
            assert str(example['ID_CHAMBRE2']) != 'nan', 'id_chambre2 must be specified'
            assert str(example['TITRAGE']) != 'nan', 'titrage must be specified'
            assert str(example['SOMMAIRE']) != 'nan', 'sommaire must be specified'
            assert str(example['SOMMAIRE']) != 'nan', 'sommaire must be specified'
            assert str(example['ANNOT_SIMIL2']) != 'nan', 'sim2 must be specified'
            assert str(example['ANNOT_SIMIL1']) != 'nan', 'sim1 must be specified'
            assert str(example['Annotateur1']) != 'nan', 'annot1 must be specified'
            assert str(example['Annotateur2']) != 'nan', 'annot2 must be specified'
        else:
            assert str(example['TITRAGE']) != 'nan', 'titrage must be specified'
            new_data.append(example)

        if str(example['ID_DOCUMENT2']) in ["NaN", "nan"]:
            partial = True
        else:
            partial = False

    return new_data

# read the similarity file with annotations
df_annot = pd.read_csv(args.orig_similarity_file, sep=";", encoding="utf-8")
annot_data = prepare_sim_df(df_annot)
os.sys.stderr.write('Number of annotated examples = ' + str(len(annot_data)) + '\n')

# read the blank similarity file (with no annotations)
df_blank = pd.read_csv(args.blank_similarity_file, sep=",", encoding="utf-8")
df_blank = df_blank.replace("<à compléter>", np.nan) # keep all examples
blank_data = prepare_empty_df(df_blank)

# read titres and sommaires dataset
df_tiso = pd.read_csv(args.titres_sommaires_orig, sep="\t")

# go through annotated examples and associate with the correct ids from the other files
wrong, wrong1, wrong2 = 0, 0, 0
new_annot_data = []
for e, example in enumerate(annot_data):

    # get potential matches from the titres-sommaires file
    doc1 = df_tiso[df_tiso['ID_DOCUMENT'] == int(example['ID_DOCUMENT'])]
    doc2 = df_tiso[df_tiso['ID_DOCUMENT'] == int(example['ID_DOCUMENT2'])]
    # check that there is at least one matching document (not necessarily matching titrage)
    assert len(doc1) >= 1, 'There should be a single row possible doc1'
    assert len(doc2) >= 1, 'There should be a single row possible doc2'

    # get matching entry in the empty file
    try:
        blank_example = blank_data[(example['ID_DOCUMENT'], example['ID_DOCUMENT2'])]
    except KeyError:
        blank_example = blank_data[(example['ID_DOCUMENT2'], example['ID_DOCUMENT'])]
        blank_example = blank_example[1], blank_example[0]

    assert example['ID_CHAMBRE1'] == blank_example[0]['ID_CHAMBRE']
    assert example['ID_CHAMBRE2'] == blank_example[1]['ID_CHAMBRE']
    assert example['TITRAGE'] == blank_example[0]['TITRAGE']

    if str(blank_example[0]['SOMMAIRE']) != 'nan' and str(example['SOMMAIRE']) != 'nan':
        assert example['SOMMAIRE'] == blank_example[0]['SOMMAIRE']

    # get titrage from test set - always corresponds to first document (checked this)
    tiso_titrages1 = doc1[['PM', 'AM1', 'AM2', 'AM3', 'AM4', 'AM5', 'AM6', 'AM7', 'AM8', 'AM9', 'AM10', 'AM11', 'AM12']].values[0:1]
    tiso_titrages1 = [list(x) for x in tiso_titrages1]
    tiso_titrages2 = doc2[['PM', 'AM1', 'AM2', 'AM3', 'AM4', 'AM5', 'AM6', 'AM7', 'AM8', 'AM9', 'AM10', 'AM11', 'AM12']].values[0:1]
    tiso_titrages2 = [list(x) for x in tiso_titrages2]
    
    str_tiso_titrages1 = [' | '.join([x.strip() for x in tiso_titrage1 if str(x) != 'nan']).lower() for tiso_titrage1 in tiso_titrages1]
    str_tiso_titrages2 = [' | '.join([x.strip() for x in tiso_titrage2 if str(x) != 'nan']).lower() for tiso_titrage2 in tiso_titrages2]

    # compare to titrage in the similarities file to make sure it is the right one
    sim_titrage1 = ' | '.join(clean_titrage_list(re.sub(' +', ' ', example['TITRAGE']).split(' | '))).lower().strip()
    blank_sim_titrage1 = ' | '.join(clean_titrage_list(re.sub(' +', ' ', blank_example[0]['TITRAGE']).split(' | '))).lower().strip()
    blank_sim_titrage2 = ' | '.join(clean_titrage_list(re.sub(' +', ' ', blank_example[1]['TITRAGE']).split(' | '))).lower().strip()

    # check that these are all coherent    
    assert sim_titrage1 == blank_sim_titrage1, 'sim_titrage1 == blank_sim_titrage1'

    # find matching titrage for 1st document
    doc1_idx = None
    for t, titrage in enumerate(str_tiso_titrages1):
        if blank_sim_titrage1 == titrage:
            doc1_idx = t

    doc2_idx = None
    for t, titrage in enumerate(str_tiso_titrages2):
        if blank_sim_titrage2 == titrage:
            doc2_idx = t

    if doc1_idx is None or doc2_idx is None:
        wrong += 1
        if doc1_idx is None:
            wrong1 += 1
        if doc2_idx is None:
            wrong2 += 1
        continue

    example['DATAPOINT1'] = doc1['ID_DATAPOINT'].values[doc1_idx]
    example['DATAPOINT2'] = doc2['ID_DATAPOINT'].values[doc2_idx]
    example['CLEAN_TITRAGE1'] = blank_sim_titrage1
    example['CLEAN_TITRAGE2'] = blank_sim_titrage2
    example['ORIG_TITRAGE1'] = ' | '.join([x.strip() for x in tiso_titrages1[doc1_idx] if str(x) != 'nan'])
    example['ORIG_TITRAGE2'] = ' | '.join([x.strip() for x in tiso_titrages2[doc2_idx] if str(x) != 'nan'])
    example['ORIG_SOMMAIRE1'] = doc1['SOMMAIRE'].values[doc1_idx]
    example['ORIG_SOMMAIRE2'] = doc2['SOMMAIRE'].values[doc2_idx]
    example['SOMMAIRE1'] = doc1['SOMMAIRE'].values[doc1_idx].lower()
    example['SOMMAIRE2'] = doc2['SOMMAIRE'].values[doc2_idx].lower()
    
    new_annot_data.append(example) # set in new dict

    assert str_tiso_titrages1[doc1_idx] == blank_sim_titrage1, 'str_tiso_titrages1[i] == blank_sim_titrage1'
    assert str_tiso_titrages2[doc2_idx] == blank_sim_titrage2, 'str_tiso_titrages2[i] == blank_sim_titrage2'

os.sys.stderr.write('Number of examples not found = ' + str(wrong) + '\n')
os.sys.stderr.write('Number of titrage1 not found = ' + str(wrong1) + '\n')
os.sys.stderr.write('Number of titrage2 not found = ' + str(wrong2) + '\n')

# final integrity checks
for ex in new_annot_data:
    for info in ['ID_DOCUMENT', 'ID_DOCUMENT2', 'ID_CHAMBRE1', 'ID_CHAMBRE2',
                 'ORIG_TITRAGE1', 'ORIG_TITRAGE2', 'ORIG_SOMMAIRE1', 'ORIG_SOMMAIRE2', 'ANNOT_SIMIL1',
                 'Annotateur1', 'DATAPOINT1', 'DATAPOINT2']:
        assert str(ex[info]) != 'nan', info + ' must not be nan'
    assert '\n' not in ex['ORIG_SOMMAIRE1'], 'no newline in sommaire1'
    assert '\n' not in ex['ORIG_SOMMAIRE2'], 'no newline in sommaire2'
    assert '\n' not in ex['ORIG_TITRAGE1'], 'no newline in titrage1'
    assert '\n' not in ex['ORIG_TITRAGE2'], 'no newline in titrage2'

# typing
for e in range(len(new_annot_data)):
    new_annot_data[e]['ID_DOCUMENT'] = str(int(annot_data[e]['ID_DOCUMENT']))
    new_annot_data[e]['ID_DOCUMENT2'] = str(int(annot_data[e]['ID_DOCUMENT2']))

# print out final dataframex
print('\t'.join(['id_datapoint1', 'id_datapoint2', 'id_document1', 'id_document2', 'id_chamber1', 'id_chamber2', 'similarity1', 'similarity2', 'annotator1', 'annotator2', 'orig_titrage1', 'orig_titrage2', 'clean_lc_titrage1', 'clean_lc_titrage2', 'orig_sommaire1', 'orig_sommaire2', 'lc_sommaire1', 'lc_sommaire2']))

seen_docs = []
for ex in new_annot_data:
    if (ex['DATAPOINT1'], ex['DATAPOINT2']) in seen_docs:
        continue
    prepare_str = [str(ex[info]).strip() for info in ['DATAPOINT1','DATAPOINT2', 
                                                      'ID_DOCUMENT', 'ID_DOCUMENT2', 
                                                      'ID_CHAMBRE1', 'ID_CHAMBRE2',
                                                      'ANNOT_SIMIL1', 'ANNOT_SIMIL2', 
                                                      'Annotateur1', 'Annotateur2',
                                                      'ORIG_TITRAGE1', 'ORIG_TITRAGE2', 
                                                      'CLEAN_TITRAGE1', 'CLEAN_TITRAGE2',
                                                      'ORIG_SOMMAIRE1', 'ORIG_SOMMAIRE2', 
                                                      'SOMMAIRE1', 'SOMMAIRE2']]
    print('\t'.join(prepare_str))
    seen_docs.append((ex['DATAPOINT1'], ex['DATAPOINT2']))
