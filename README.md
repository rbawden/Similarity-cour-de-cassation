# Complex Labelling and Similarity Prediction in Legal Texts: Automatic Analysis of France’s Court of Cassation Rulings

(repository under construction)

This code accompanies the LREC 2022 article of the above name. With the long-term goal of automatising the detection of divergence in the application of the law, we propose tools to (i) automatically generate keyword sequences for rulings from syntheses to improve coverage of these keyword sequence annotations (used for indexing) and (ii) calcualte the similarity of a given pair of rulings based on manually provided documents (the text of the rulings, syntheses and keyword sequences) as well as on the predicted keyword sequences from step (i).

## Citation

If you use this work, please cite the following article:

Thibault Charmet, Inès Cherichi, Matthieu Allain, Urszula Czerwinska, Amaury Fouret, Benoît Sagot and Rachel Bawden, 2022. **Complex Labelling and Similarity Prediction in Legal Texts: Automatic Analysis of France’s Court of Cassation Rulings**. In Proceedings of the 13th Language Resources and Evaluation Conference, Marseille, France.

```
@inproceedings{charmet-et-al-2022-complex,
  tite = {Complex Labelling and Similarity Prediction in Legal Texts: Automatic Analysis of France’s Court of Cassation Rulings},
  author = {Charmet, Thibault and Cherichi, Inès and Allain, Matthieu and Czerwinska, Urszula and Fouret, Amaury, and Sagot, Benoît and Bawden, Rachel},
  booktitle = {Proceedings of the 13th Language Resources and Evaluation Conference},
  year = {2022},
  address = {Marseille, France}
```

## Easily usable models released

The original experiments are run using Fairseq and you can find instructions to reproduce these experiments and run the Fairseq models. For ease of use, we also make some models available on HuggingFace.

### Automatic keyword sequence prediction 

The model can be found [here](https://huggingface.co/rbawden/CCASS-auto-titrages-base).

Model input is the *matière* (matter) concatenated to the text from the sommaire separated by the token `<t>`. Each example should be on a single line. E.g. `bail <t> La recommendation du tribunal selon l'article...` (fictive example for illustrative purposes. The maximum input length of the model is 1024 input tokens (after tokenisation).

```
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokeniser = AutoTokenizer.from_pretrained("rbawden/CCASS-auto-titrages-base", use_auth_token=True)
model = AutoModelForSeq2SeqLM.from_pretrained("rbawden/CCASS-auto-titrages-base", use_auth_token=True)

matiere = "matter"
sommaire = "full text from the sommaire on a single line"
inputs = tokeniser([matiere + " <t> " + sommaire], return_tensors='pt')
outputs = model.generate(inputs['input_ids'])
tokeniser.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenisation_spaces=True)
```

The model is the 8k joint BPE vocabulary Fairseq model, converted to HuggingFace and then fine-tuned to remove incoherences in the original and converted model.

### Semi-automatic keyword sequence prediction

We also make a second model available to enable semi-automatic keyword sequence prediction (predict a keyword from the synthesis, matter and the beginning of the keyword sequence. The input should be formatted as follows: the matter, the keyword sequence prefix and the synthesis should be concatenated, each separated by the `<t>` token, which should also be used to separated individual keywords within the sequence. E.g. If the matter is "contrat" and the prefix sequence is "resiliation <t> travail <t> légal" (keywords chosen randomly for illustrative purposes), the input will be "contrat <t> resiliation <t> travail <t> légal <t> " followed by the content of the synthesis.

```
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokeniser = AutoTokenizer.from_pretrained("rbawden/CCASS-semi-auto-titrages-base", use_auth_token=True)
model = AutoModelForSeq2SeqLM.from_pretrained("rbawden/CCASS-semi-auto-titrages-base", use_auth_token=True)

matiere_and_titrage_prefix = "matter <t> titre"
sommaire = "full text from the sommaire on a single line"
inputs = tokeniser([matiere_and_titrage_prefix + " <t> " + sommaire], return_tensors='pt')
outputs = model.generate(inputs['input_ids'])
tokeniser.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenisation_spaces=True)
```

### Similarity prediction

To predict the similarity of two cases, use `scripts/predict_similarity.py` as follows:
  
```
python scripts/predidct_similarity.py \
      -g GOLD_KEYWORD_SEQ_1 GOLD_KEYWORD_SEQ_2 \
      -p PRED_KEYWORD_SEQ_1 PRED_KEYWORD_SEQ_2 \
      -s GOLD_SYNTHESIS_1 GOLD_SYNTHESIS_2 \  -m models/edsim.sommaire-gold.titrage-gold.titrage-pred-3.pickle \
      -n NUM_PRED_TITRAGES_TO_USE \
      -m SIM_PRED_MODEL_PATH
  
python scripts/predidct_similarity.py \
      -g data/similarity/dataset/titrage1.lower.gold data/similarity/dataset/titrage2.lower.gold \
      -p data/similarity/predicted/titrages1.lower.joint-8000.20.beam.pred.tab-sep data/similarity/predicted/titrages2.lower.joint-8000.20.beam.pred.tab-sep \
      -s data/similarity/dataset/sommaire1.lower.gold data/similarity/dataset/sommaire2.lower.gold  -m models/edsim.sommaire-gold.titrage-gold.titrage-pred-3.pickle -n 3
```
where the two arguments to `-g` are the two files containing gold keyword sequences, the two arguments to `-p` are the two files containing predicted keyword sequences and the two arguments to `-s` are the two files containing gold syntheses.
  
In each file, there should be one example per line. When there are multiple syntheses/sequences for one example, these should be written on the same line, separated by tabs. Neither keyword sequences nor syntheses should contain tabs or newlines (these should be replaced with spaces beforehand). No additional processing needs to be applied (other than removing non-printing characters or cleaning encoding problems if they occur).

## Reproducing the results in the article

### Requirements

Tested with python3.7
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Data

The data is distributed under the licence specified in XXX. To obtain the data, please contact XXX. (Access to data to be added very soon!)

Once you have obtained the data, unzip the folder and place it at the root of the repository. The current repository contains a partial version of this data, containing just the extracted features and correlation results.

The full data repository should contain the following files:

```
data/
 |
 |---- orig/
 |     |-- arrets.csv
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

### Prepare the data

The prepared data is provided in the zip folder, so there is no need to rerun data preparation. For reproducibility purposes, the script to prepare the data from the original files found in `data/orig/` is provided:

`bash scripts/prepare_data.sh`

### Models

#### Automatic keyword sequence prediction ('titrage' in French)

##### Download models

TODO

##### Generation
Take examples consisting of the matter (first title; 'matière') concatenated to the synthesis ('sommaire') and predict the rest of the keyword sequence 'titrage'.

```
echo "MATIERE <t> SOMMAIRE" | bash scripts/translate-interactive.sh <model_path> <data_dir> <sp_model>

echo "contrat <t> la convention collective du batiment doit être calculée en fonction ..." | \
    bash scripts/translate-interactive.sh \
        models/sommaire2titrage/mini-joint/8000/model-1/checkpoint_best_weighted_acc.pt \
        data/bin/lowercase.sommaire-titrage.joint-sp8000 \
        data/preproc/spm.8000.lowercase.joint-sommaire-titrage.model
```

Preprocessing is applied before translation:
- lowercase
- sentencepiece subword segmentation

##### Evaluation
Evaluation is run as follows, by comparing the hypothesis and reference file according to a specific criterion:
```
python scripts/evaluate.py <hyp_file> <ref_file> {global_acc,acc_per_level,weighted_acc,micro_acc}
```
E.g.

TODO

#### Similarity prediction

##### Reproducing results

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





