# Similarity-cour-de-cassation


## Requirements

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Data

The data is distributed under the licence specified in XXX. To obtain the data, please contact XXX. Once you have obtained the data, unzip the folder and place it at the root of the repository.

Your data repository should contain the following files:

TODO: structure of files

```
data/
 |
 |---- orig/
 |     |-- titres_and_sommaires.csv
 |     |-- meta_decisions_INRIA.csv
 |
 |---- final/
 |     |-- dataset.tsv
 |     |-- {train,valid,test}.tsv
 |     |-- {train,valid,test}.{matiere,sommaire,titrage}
 |     |-- {train,valid,test}.lowercase.{matiere,sommaire,titrage}
 |
 |---- preproc/
 |     |-- {train,valid,test}.lowercase.sommaitre-titrage.{sommaire,titrage}
 |     |-- spm.{8,16,24,32}000.joint-sommaire-titrage.{model,vocab}
 |     |-- spm_camembert.{model,vocab}
 |     |-- {train,valid,test}.lowercase.sommaitre-titrage.joint-sp{8,16,24,32}.{sommaire,titrage}
 |     |-- {train,valid,test}.lowercase.sommaitre-titrage.camembert.{sommaire,titrage}
 |
 |---- bin/
 |     |-- 
```

`orig/` contains the original files will all raw information, `final/` the cleaned dataset splits, `preproc/` the preprocessed files (lowercasing and sentencepiece segmentation) and `bin/` the binarised files to be used by fairseq.

## Prepare the data

The prepared data is provided in the zip folder, so there is no need to rerun data preparation. For reproducibility purposes, the script to prepare the data from the original files found in `data/orig/` is provided:

`bash scripts/prepare_data.sh`

## Models

### Automatic keyword sequence prediction ('titrage' in French)

Take examples consisting of the matter (first title; 'matière') concatenated to the synthesis ('sommaire') and predict the rest of the keyword sequence 'titrage'.


