# Similarity-cour-de-cassation


## Requirements

Tested with python3.7
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Data

The data is distributed under the licence specified in XXX. To obtain the data, please contact XXX. 

Once you have obtained the data, unzip the folder and place it at the root of the repository. The current repository contains a partial version of this data, containing just the extracted features and correlation results.

The full data repository should contain the following files:

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
 |     |-- lowercase.sommaire-titrage.joint-sp{8,16,24,32}000/
 |     |-- lowercase.sommaire-titrage.joint-sp{8,16,24,32}000.nojoin/
 |     |-- lowercase.sommaire-titrage.camembert/
 |
 |---- similarity/
 |     |-- dataset/
 |     |-- predicted/
 |     |-- features/
 |     |-- results/
```

`orig/` contains the original files will all raw information, `final/` the cleaned dataset splits, `preproc/` the preprocessed files (lowercasing and sentencepiece segmentation) and `bin/` the binarised files to be used by fairseq. The similarity data is found in the `similarity/` subfolder, with the original (gold) data in `similarity/dataset/`, the predicted keyword sequences in `similarity/predicted/`, the extracted features in `similarity/features/` and select correlation results in `similarity/results/`.

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

### Similarity prediction

The dataset and features are all provided, so there is no need to rerun generation, but for reproducibility purposes, the data and features are prepared as follows:

1. Extract different information from the similarity dataset:
```
bash scripts/prepare_similarity_data.sh
```
The extracted information can be found in `data/similarity/dataset` for the original (gold) information and `data/similarity/predicted/` for the predicted information.

Part of step 1 requires the predicted keyword sequences to have been generated. If they have not been generated, you will receive a warning message. You should run step B (below) and then run step A a second time once the predicted files are present.

2. Generate predicted keyword sequences (make sure to adapt to your own scheduler or working environment):
```
sbatch scripts/predict_titrages.slurm
```
The predicted sequences can be found in `data/similarity/predicted/`

3. Produce the different features that are tested:
```
bash scripts/produce_similarity_features.sh
```
Features are output to `data/similarity/features/`

4. Calculate the main similarity correlations
```
bash scripts/get_sim_results.sh
```
Results are output to `data/similarity/results/`
