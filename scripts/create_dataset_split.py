# -*- coding: utf-8 -*-
import pandas as pd
from pandas.io.parsers import read_csv
from sklearn.model_selection import GroupShuffleSplit
import numpy as np
import os, re

SEED = 1
to_replace = {
          '&#13;': '', '&#65279;': '', '&#9688;': '', '&#8216;': "'", '&#8217;': "'",
          '&#8364;': 'euro', '&#8211;': '-',       '&#8220;': '"', '&#8221;': '"',
          '&#61616;': '', '&#339;': 'œ', '&#64257;': 'fi', '&#64258;': 'fl', '&#8226;': '',
          '&#923;': 'ê', '&#13': '', '\((non|NON)\)': '', '\((oui|OUI)\)': '', '\/\.': '', '_': ' ',
          r'^ *\/* *(jdf|JDF) *$': '', r'([a-zA-Z])¿([a-zA-Z])': r"\1'\2", r'([0-9])¿(\s)': r"\1€\2",
          '¿uvre': 'œuvre', 'd¿uvre': "d'œuvre", r'([A-zÀ-ú])¿([A-zÀ-ú])': r"\1'\2",
          r'\*': '', r'\s{5,}à$': '', r'\s{2,}': ' '
       }

# expects a list of titres (including the matter)
def clean_titrage_list(titrage_list):
    assert type(titrage_list) == list
    for e in range(len(titrage_list)):
        for r in to_replace:
            titrage_list[e] = re.sub(r, to_replace[r], titrage_list[e])
    return titrage_list

def clean(dataset):
    dataset = dataset.replace(to_replace = to_replace)
       #to_replace = {
       #   '&#13;': '', '&#65279;': '', '&#9688;': '', '&#8216;': "'", '&#8217;': "'",
       #   '&#8364;': 'euro', '&#8211;': '-',       '&#8220;': '"', '&#8221;': '"',
       #   '&#61616;': '', '&#339;': 'œ', '&#64257;': 'fi', '&#64258;': 'fl', '&#8226;': '',
       #   '&#923;': 'ê', '&#13': '', '\((non|NON)\)': '', '\((oui|OUI)\)': '', '\/\.': '', '_': ' ',
       #   r'^ *\/* *(jdf|JDF) *$': '', r'([a-zA-Z])¿([a-zA-Z])': r"\1'\2", r'([0-9])¿(\s)': r"\1€\2",
       #   '¿uvre': 'œuvre', 'd¿uvre': "d'œuvre", r'([A-zÀ-ú])¿([A-zÀ-ú])': r"\1'\2",
       #   r'\*': '', r'\s{5,}à$': '', r'\s{2,}': ' '
        #}, regex=True)
    
    # only replace in titrages
    dataset.loc[:, "PM":"AM12"] = dataset.loc[:, "PM":"AM12"].replace(to_replace = { r';$' : '', }, regex=True)
    return dataset
   
def extract_excluded_arrets(df, df_exclude):
    df_extracted = pd.DataFrame(columns=df.columns)
   
    for row in df_exclude.itertuples():
        row_lst1 = df[df.loc[:, "ID_DOCUMENT"] == row.ID_DOCUMENT]
        row_lst2 = df[df.loc[:, "ID_DOCUMENT"] == row.ID_DOCUMENT2]
        # copy the row to the new dataframe
        if len(row_lst1) > 0:
            df_extracted = df_extracted.append(df.iloc[row_lst1.index])
        if len(row_lst2) > 0:
            df_extracted = df_extracted.append(df.iloc[row_lst2.index])
    # In case we copied duplicated we remove them
    df_extracted = df_extracted.drop_duplicates()
    # remove the row from the original dataframe
    df = df.drop(df_extracted.index)
    return df, df_extracted


def split_train_val_test(dataset, df_annot):
    """
    df_annot is a dataset of annotation used later for similarity
    every arrêt present in this dataframe will be moved to the test set after the initial split
    """
    # Splitting 80/10/10

    columns_ids = ["ID_DOCUMENT", "NUM_ANALYSE"] 
    columns_other = ["ID_CHAMBRE", "DT_DECISION", "ID_SOLUTION", "TEXTE_VISE"]
    columns_variables = ["SOMMAIRE"]
    columns_labels = ["PM", "AM1", "AM2", "AM3", "AM4", "AM5", "AM6", "AM7", "AM8", "AM9", "AM10", "AM11", "AM12"]
    dataset, df_extracted = extract_excluded_arrets(dataset, df_annot)

    def get_X_y(dataset):
        """In the case where the sommaires are used to predict the titrages."""
        X = dataset.loc[:, columns_ids + columns_other + columns_variables]
        y = dataset.loc[:, columns_labels]
        return X, y

    X, y = get_X_y(dataset)
    groups = dataset.loc[:, "ID_DOCUMENT"]

    # group shuffle split allows to keep elements of the same group in the same dataset
    train_idx, inter_idx = next(GroupShuffleSplit(n_splits=1, test_size=17000, random_state=SEED).split(X, y, groups=groups))
    X_test = dataset.iloc[inter_idx, :]
    y_test = dataset.iloc[inter_idx, :]
    test_groups = groups.iloc[inter_idx]

    # splitting again test in 2 : validation and test
    val_idx, test_idx = next(GroupShuffleSplit(n_splits=1, test_size=15500, random_state=SEED).split(X_test, y_test, groups=test_groups))

    # make sure to apply right indexes to right dataset (the one the split was made on) 
    train = dataset.iloc[train_idx, :]
    valid = X_test.iloc[val_idx, :]
    test = X_test.iloc[test_idx, :]

    # add arrêts excluded from train/valid set to test set
    test = test.append(df_extracted)

    return train, valid, test


def extract_last_titres(df):
    cross_df = np.logical_xor(df.loc[:,"PM":"AM11"].notnull().values,
                            df.loc[:,"AM1":"AM12"].notnull().values)
    cross_df_insert = np.insert(cross_df, -1, df.loc[:,"AM12"].notnull().values, axis=1)
    return cross_df_insert


def build_dataset(df_titrages_sommaires, df_meta):

    os.sys.stderr.write("Merging data into a dataset...\n")

    # columns for each type of df
    columns_titrages_sommaires = ["ID_DOCUMENT", "NUM_ANALYSE", "PM", "AM1", "AM2", "AM3", "AM4", "AM5", "AM6", "AM7", "AM8", "AM9", "AM10", "AM11", "AM12", "SOMMAIRE"]
    columns_meta = ["ID_DOCUMENT", "ID_CHAMBRE", "DT_DECISION", "ID_SOLUTION", "TEXTE_VISE"]
    # keep only specified columns
    df_titrages_sommaires = df_titrages_sommaires[columns_titrages_sommaires]
    df_meta = df_meta[columns_meta]

    print('titrages - sommaires')
    print(df_titrages_sommaires.shape)
    print('meta')
    print(df_meta.shape)

    # merge the dataframes on id_document (unique identifier of arrêts)
    dataset = df_titrages_sommaires.merge(df_meta, how='outer', on="ID_DOCUMENT")

    print('merged')
    print(dataset.shape)

    # only keep lines that have at least one sommaire, maitère and titrage
    dataset = dataset.dropna(subset=["PM", "AM1", "SOMMAIRE"])

    print('removed empty sommaire + titrages values')
    print(dataset.shape)

    # final dataset
    dataset = dataset.astype({"ID_DOCUMENT" : "int64", "NUM_ANALYSE" : "int64"})
    # replace any NaNs with empty strings
    dataset.loc[:, "AM1":"AM12"] = dataset.loc[:, "AM1":"AM12"].fillna("") 
    # remove lines with no date
    arret_with_date = len(dataset[dataset["DT_DECISION"].notna()]["ID_DOCUMENT"].unique())
    # convert date format
    dataset['DT_DECISION'] = pd.to_datetime(dataset['DT_DECISION'], format='%Y-%m-%d')
    dataset['ID_DATAPOINT'] = dataset["ID_DOCUMENT"].astype(str).str.cat(dataset["NUM_ANALYSE"].astype(str), sep='-', na_rep='?')
    # move the last column to the beginning
    cols = dataset.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    dataset = dataset[cols]

    assert dataset['ID_DATAPOINT'].shape == dataset['ID_DATAPOINT'].drop_duplicates().shape, 'Each ID must be unique'

    print('before clean')
    print(dataset.shape)
    
    # clean the dataset
    dataset = clean(dataset)
    
    dataset = dataset[dataset["PM"] != ""]
    dataset = dataset[dataset["AM1"] != ""]
    dataset = dataset[dataset["SOMMAIRE"] != ""]

    dataset = dataset.reset_index(drop=True)

    # replace all newlines in sommaires with spaces

    dataset = dataset.replace(to_replace={r'[\r\n\t]+': ' '}, regex=True)
    print('all finished')
    print(dataset.shape)
    return dataset


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('orig_data_folder')
    parser.add_argument('output_dir')
    args = parser.parse_args()

    # load all data
    os.sys.stderr.write("Loading input data...\n")
    df_titrages_sommaires = pd.read_csv(args.orig_data_folder + "/titres_and_sommaires.csv", sep=",")
    df_meta = pd.read_csv(args.orig_data_folder + "/meta_decisions_INRIA.csv", sep=",")
    df_annot = pd.read_csv(args.orig_data_folder + "/compilation_toutes_annotations.csv", sep=';', encoding="utf-8")
    df_annot = df_annot.replace("<à compléter>", np.NaN)
    df_annot = df_annot.dropna(subset=["ANNOT_SIMIL1"]) # only keep lines with at least one annotation

    # build dataset
    dataset = build_dataset(df_titrages_sommaires, df_meta)

    os.sys.stderr.write("Saving dataset to file...\n")
    dataset.to_csv(args.output_dir + "/dataset.tsv", index=False, sep='\t')

    # split into train/valid/test
    os.sys.stderr.write("Splitting dataset into train/valid/test...\n")
    train, valid, test = split_train_val_test(dataset, df_annot)
    os.sys.stderr.write("dataset_train size" + str(train.shape) + "\n")
    os.sys.stderr.write("dataset_validation size" + str(valid.shape) + "\n")
    os.sys.stderr.write("dataset_test size" + str(test.shape) + "\n")


    train.to_csv(args.output_dir + "/train.tsv", index=False, sep='\t')
    valid.to_csv(args.output_dir + "/valid.tsv", index=False, sep='\t')
    test.to_csv(args.output_dir + "/test.tsv", index=False, sep='\t')
