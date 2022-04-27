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
 |     |-- {train,valid,test}.lowercase.sommaitre-titrage.{sommaire,titrage} (original lowercased files)
 |     |-- spm.{8,16,24,32}000.joint-sommaire-titrage.{model,vocab} (sentencepiece models)
 |     |-- spm_camembert.{model,vocab} (CamemBERT sentencepiece model)
 |     |-- {train,valid,test}.lowercase.sommaitre-titrage.joint-sp{8,16,24,32}.{sommaire,titrage} (segmented text)
 |     |-- {train,valid,test}.lowercase.sommaitre-titrage.camembert.{sommaire,titrage} (segmented text)
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

```
echo "MATIERE <t> SOMMAIRE" | bash scripts/translate-interactive.sh <model_path> <data_dir> <sp_model>

echo "contrat <t> la convention collective du batiment doit être calculée en fonction ..." | \
    bash scripts/translate-interactive.sh \
        models/sommaire2titrage/mini-joint/8000/model-1/checkpoint_best_micro_acc.pt \
        data/bin/lowercase.sommaire-titrage.joint-sp8000 \
        data/preproc/spm.8000.lowercase.joint-sommaire-titrage.model
```

TODO: check other types of preprocessing that must be applied for this model to work (e.g. apostrophes, lowercasing, accents?)

