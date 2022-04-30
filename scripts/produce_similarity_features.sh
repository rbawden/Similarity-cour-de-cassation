#!/bin/sh
thisdir=`dirname $0`
simdir=$thisdir/../data/similarity

# gold information
gold_titrage1=$simdir/dataset/titrage1.lower.gold
gold_titrage2=$simdir/dataset/titrage2.lower.gold
gold_sommaire1=$simdir/dataset/sommaire1.lower.gold
gold_sommaire2=$simdir/dataset/sommaire2.lower.gold
gold_arret1=$simdir/dataset/arret1.lower.gold
gold_arret2=$simdir/dataset/arret1.lower.gold

# predicted information
pred_titrage1_prefix=$simdir/predicted/titrages1.lower 
pred_titrage2_prefix=$simdir/predicted/titrages2.lower

titrages1.lower.joint-8000.1+20.sampling.0.9.gold+pred   titrages2.lower.joint-8000.20.sampling.0.7.pred
titrages1.lower.joint-8000.20.beam.pred 

# different beam and sampling strategies
for strategy in beam sampling.0.95 sampling.0.9 sampling.0.8 sampling.0.7 sampling.0.6 sampling.0.5; do
    echo "Beam/samling strategy = $strategy"
    model=joint-8000 # model to be used
    pred_suffix=$model.20.$strategy.pred
    gold_pred_suffix=$model.1+20.$strategy.gold+pred

    # calculate features for pred and gold+pred
    for type_calc in avg max; do
	echo " --> function type = $type_calc"
	for k in $(seq 20); do
	    echo "    --> number to use = $k"
	    # produce features for the predicted files
	    if [ ! -f $simdir/features/edsim.titrages.$pred_suffix.$type_calc.$k ]; then
		python $thisdir/edsim_files.py \
		    $pred_titrage1_prefix.$pred_suffix \
		    $pred_titrage2_prefix.$pred_suffix $type_calc -n 20 -k $k \
		    > $simdir/features/edsim.titrages.$pred_suffix.$type_calc.$k
	    fi
	    
	    # produce features for the gold+predicted files
	    total=$((k+1))
	    if [ ! -f $simdir/features/edsim.titrages.$gold_pred_suffix.$type_calc.$k+1 ]; then
		python $thisdir/edsim_files.py \
		    $pred_titrage1_prefix.$gold_pred_suffix \
		    $pred_titrage2_prefix.$gold_pred_suffix $type_calc -n 21 -k $total \
                    > $simdir/features/edsim.titrages.$gold_pred_suffix.$type_calc.$k+1
	    fi
	done
    done
done

# calculate feature for gold titrages
python $thisdir/edsim_files.py $gold_titrage1 $gold_titrage2 max -n 1 -k 1 \
    > $simdir/features/edsim.titrages.gold

# calculate features for gold sommaires
python $thisdir/edsim_files.py $gold_sommaire1 $gold_sommaire2 max -n 1 -k 1 -s \
    > $simdir/features/edsim.sommaires.gold

# calculate features for arrêts (1-3gram, max 1M features, trained on all arrets except those in data/final/test.tsv set)
if [ ! -f $simdir/features/tf_idf_model.pickle ]; then
    if [ ! -f $simdir/dataset/arrets.no_test_docs.lower.gold ]; then
	echo "Extracting non-test-set arrêt text"
	python $thisdir/get_text_arrets.py $thisdir/../data/orig/arrets.csv \
	    -e $thsidir/../data/final/test.id_document \
	    > $simdir/dataset/arrets.no_test_docs.lower.gold
    fi
    echo "Training TF.IDF model"
    python $thisdir/tfidf_arrets.py -f $simdir/dataset/arrets.no_test_docs.lower.gold \
	--output_model $simdir/features/tf_idf_model.pickle
fi

# predict features based on gold arrets (given model already exists, only does prediction)
python $thisdir/tfidf_arrets.py -f $gold_arret1 $gold_arret2 -p \
    --output_model $simdir/features/tf_idf_model.pickle \
    > $simdir/features/tf_idf.arrets.gold

