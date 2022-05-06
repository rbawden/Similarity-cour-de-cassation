#!/bin/sh
thisdir=`dirname $0`
simdir=$thisdir/../data/similarity

# gold information
gold_titrage1=$simdir/dataset/titrage1.lower.gold
gold_titrage2=$simdir/dataset/titrage2.lower.gold
gold_sommaire1=$simdir/dataset/sommaire1.lower.gold
gold_sommaire2=$simdir/dataset/sommaire2.lower.gold
gold_arret1=$simdir/dataset/arret1.lower.gold
gold_arret2=$simdir/dataset/arret2.lower.gold

# predicted information
pred_titrage1_prefix=$simdir/predicted/titrages1.lower 
pred_titrage2_prefix=$simdir/predicted/titrages2.lower

# different beam and sampling strategies
for strategy in beam; do # sampling.0.95 sampling.0.9 sampling.0.8 sampling.0.7 sampling.0.6 sampling.0.5; do
    echo "Beam/samling strategy = $strategy"
    model=camembert #joint-8000 # model to be used
    pred_suffix=$model.20.$strategy.pred
    gold_pred_suffix=$model.1+20.$strategy.gold+pred

    # calculate features for pred and gold+pred
    for type_calc in avg max; do
	echo " --> function type = $type_calc"
	for k in $(seq 20); do
	    echo "    --> number to use = $k"
	    # produce features for the predicted files
	    if [ ! -f $simdir/features/edsim.titrages.$pred_suffix.$type_calc.$k ]; then
		OPENBLAS_NUM_THREADS=1 python $thisdir/edsim_files.py \
		    $pred_titrage1_prefix.$pred_suffix \
		    $pred_titrage2_prefix.$pred_suffix $type_calc -n 20 -k $k \
		    > $simdir/features/edsim.titrages.$pred_suffix.$type_calc.$k
	    fi
	    
	    # produce features for the gold+predicted files
	    total=$((k+1))
	    if [ ! -s $simdir/features/edsim.titrages.$gold_pred_suffix.$type_calc.1+$k ]; then
		OPENBLAS_NUM_THREADS=1 python $thisdir/edsim_files.py \
		    $pred_titrage1_prefix.$gold_pred_suffix \
		    $pred_titrage2_prefix.$gold_pred_suffix $type_calc -n 21 -k $total \
                    > $simdir/features/edsim.titrages.$gold_pred_suffix.$type_calc.1+$k
	    fi
	done
    done
done

# calculate feature for gold titrages
OPENBLAS_NUM_THREADS=1 python $thisdir/edsim_files.py $gold_titrage1 $gold_titrage2 max -n 1 -k 1 \
    > $simdir/features/edsim.titrages.gold

# calculate features for gold sommaires
OPENBLAS_NUM_THREADS=1 python $thisdir/edsim_files.py $gold_sommaire1 $gold_sommaire2 max -n 1 -k 1 -s \
    > $simdir/features/edsim.sommaires.gold

# calculate features for gold sommaires
OPENBLAS_NUM_THREADS=1 python $thisdir/edsim_files.py $gold_arret1 $gold_arret2 max -n 1 -k 1 -s \
    > $simdir/features/edsim.arrets.gold

# calculate features for TD-IDF models

# for arrêts (trained on sommaires, max 3gram, max 1M features)
if [ ! -f $simdir/features/tf_idf_model.sommaires.1,2,3,g.2000000.pickle ]; then
    echo "Training TF.IDF model for arrêts"
    OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py -f $thisdir/../data/final/train.sommaire -g 3 -m 2000000 \
	--output_model $simdir/features/tf_idf_model.sommaires.1,2,3,g.2000000.pickle
fi

# predict features based on gold arrets (given model already exists, only does prediction)
if [ ! -f $simdir/features/tf_idf.arret.sommaire-model.1,2,3,g.2000000.gold ]; then
    OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py -f $gold_arret1 $gold_arret2 -p \
	--output_model $simdir/features/tf_idf_model.sommaires.1,2,g.2000000.pickle \
	> $simdir/features/tf_idf.arret.sommaire-model.1,2,3,g.2000000.gold
fi

# for sommaires (trained on sommaires, max 2gram, max 250k features)
if [ ! -f $simdir/features/tf_idf_model.sommaires.1,2,g.250000.pickle ]; then
    echo "Training TF.IDF model for sommaires"
    OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py -f $thisdir/../data/final/train.sommaire -g 3 -m 250000 \
        --output_model $simdir/features/tf_idf_model.sommaires.1,2,g.250000.pickle
fi

# predict features based on gold sommaires (given model already exists, only does prediction)
if [ ! -f $simdir/features/tf_idf.sommaire.sommaire-model.1,2,g.250000.gold ]; then
    OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py -f $gold_sommaire1 $gold_sommaire2 -p \
	--output_model $simdir/features/tf_idf_model.sommaires.1,2,g.250000.pickle \
	> $simdir/features/tf_idf.sommaire.sommaire-model.1,2,g.250000.gold
fi

# for titrages (trained on sommaires, max 1gram, max 250k features)
if [ ! -f $simdir/features/tf_idf_model.titrages.1,g.250000.pickle ]; then
    echo "Training TF.IDF model for titrages"
    OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py -f $thisdir/../data/final/train.titrage -g 3 -m 250000 \
	--output_model $simdir/features/tf_idf_model.titrages.1,g.250000.pickle
fi

# predict features based on gold titrages (given model already exists, only does prediction)
if [ ! -f $simdir/features/tf_idf.titrage.titrage-model.1,g.250000.gold ]; then
    OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py -f $gold_titrage1 $gold_titrage2 -p \
    --output_model $simdir/features/tf_idf_model.titrages.1,2,g.250000.pickle \
    > $simdir/features/tf_idf.titrage.titrage-model.1,g.250000.gold
fi


# TFIDF features for predicted titrages
for strategy in beam; do 
    echo "Beam/samling strategy = $strategy"
    model=camembert  #joint-8000 # model to be used                                                                                          
    pred_suffix=$model.20.$strategy.pred
    gold_pred_suffix=$model.1+20.$strategy.gold+pred

    # calculate features for pred and gold+pred
    for type_calc in avg max; do
	echo " --> function type = $type_calc"
        for k in $(seq 20); do
            echo "    --> number to use = $k"
	    echo "OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py \
                    -f $pred_titrage1_prefix.$pred_suffix $pred_titrage2_prefix.$pred_suffix -p -n 20 -k $k -t $type_calc \
                    --output_model $simdir/features/tf_idf_model.titrages.1,2,g.250000.pickle \
                    > $simdir/features/tf_idf.titrages.$pred_suffix.$type_calc.$k"
	    # predicted titrages
	    if [ ! -s $simdir/features/tf_idf.titrages.$pred_suffix.$type_calc.$k ]; then
		OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py \
		    -f $pred_titrage1_prefix.$pred_suffix $pred_titrage2_prefix.$pred_suffix -p -n 20 -k $k -t $type_calc \
		    --output_model $simdir/features/tf_idf_model.titrages.1,2,g.250000.pickle \
		    > $simdir/features/tf_idf.titrages.$pred_suffix.$type_calc.$k
	    fi
	    # predicted+gold titrages
	    total=$((k+1))
	    if [ ! -s $simdir/features/tf_idf.titrages.$gold_pred_suffix.$type_calc.1+$k ]; then
		OPENBLAS_NUM_THREADS=1 python $thisdir/tfidf_train_predict.py \
		    -f $pred_titrage1_prefix.$gold_pred_suffix $pred_titrage2_prefix.$gold_pred_suffix -p -n 21 -k $total -t $type_calc \
		    --output_model $simdir/features/tf_idf_model.titrages.1,2,g.250000.pickle \
		    > $simdir/features/tf_idf.titrages.$gold_pred_suffix.$type_calc.1+$k
	    fi
	done
    done
done
