#!/bin/sh
thisdir=`dirname $0`
datadir=$thisdir/../data/similarity/dataset/
pred_datadir=$thisdir/../data/similarity/predicted
annots=$datadir/similarity_annotations.tsv

# work from the finalised annotations file
cat $annots | cut -f 1 | tail -n +2 > $datadir/datapoint1
cat $annots | cut -f 2 | tail -n +2 > $datadir/datapoint2
cat $annots | cut -f 3 | tail -n +2 > $datadir/doc1
cat $annots | cut -f 4 | tail -n +2 > $datadir/doc2

cat $annots | cut -f 17 | tail -n +2 > $datadir/sommaire1.lower.gold
cat $annots | cut -f 18 | tail -n +2 > $datadir/sommaire2.lower.gold

cat $annots | cut -f 13 | tail -n +2 > $datadir/matiere+titrage1.lower.pipe-sep.gold
cat $annots | cut -f 14 | tail -n +2 > $datadir/matiere+titrage2.lower.pipe-sep.gold

cat $annots | cut -f 13 | tail -n +2 | cut -d"|" -f2- | perl -pe 's/^ *//' | \
    perl -pe 's/ \| / <t> /g' > $datadir/titrage1.lower.gold
cat $annots | cut -f 14 | tail -n +2 | cut -d"|" -f2- | perl -pe 's/^ *//' | \
    perl -pe 's/ \| / <t> /g' > $datadir/titrage2.lower.gold

cat $annots | cut -f 13 | tail -n +2 | cut -d"|" -f1 | perl -pe 's/^ *//' \
    > $datadir/matiere1.lower.gold
cat $annots | cut -f 14 | tail -n +2 | cut -d"|" -f1 | perl -pe 's/^ *//'  \
    > $datadir/matiere2.lower.gold

cat $annots | cut -f 7 | tail -n +2 > $datadir/sim1
cat $annots | cut -f 8 | tail -n +2 > $datadir/sim2
paste $datadir/sim1 $datadir/sim2 | \
    python $thisdir/avg_columns.py > $datadir/ave-sim

python $thisdir/associate_arrets_to_sim_data.py \
    $thisdir/../data/orig/arrets.csv $annots $datadir/arrets
mv $datadir/arrets1 $datadir/arret1.lower.gold
mv $datadir/arrets2 $datadir/arret2.lower.gold

# Now insert gold titrage into predicted files to be produce a version with pred+gold
# Prediction must have already been run for this step.

# sampling
for num in 1 2; do
    for temp in 0.5 0.6 0.7 0.8 0.9 0.95; do
	if [ ! -f $pred_datadir/titrages$num.lower.joint-8000.20.sampling.$temp.pred ]; then
	    echo "Missing file: $pred_datadir/titrages$num.lower.joint-8000.20.sampling.$temp.pred"
	    echo "You must first run the generation of predicted keyword sequences."
	    echo "Run 'sbatch scripts/predict_titrages.slurm' and then rerun this script"
	    echo "Exiting now."
	    exit
	fi
	python $thisdir/concatenate_gold_pred_titrages.py \
	    $datadir/titrage$num.lower.gold $pred_datadir/titrages1.lower.joint-8000.20.sampling.$temp.pred \
	    > $pred_datadir/titrages$num.lower.joint-8000.1+20.sampling.$temp.gold+pred
    done
    
    # beam search
    if [ ! -f $pred_datadir/titrages$num.lower.joint-8000.20.beam.pred ]; then
	echo "Missing file: $pred_datadir/titrages$num.lower.joint-8000.20.beam.pred"
	echo "You must first run the generation of predicted keyword sequences."
	echo "Run 'sbatch scripts/predict_titrages.slurm' and then rerun this script"
	echo "Exiting now."
	exit
    fi
    python $thisdir/concatenate_gold_pred_titrages.py \
	$datadir/titrage$num.lower.gold \
	$pred_datadir/titrages$num.lower.joint-8000.20.beam.pred \
	> $pred_datadir/titrages$num.lower.joint-8000.1+20.beam.gold+pred
done
