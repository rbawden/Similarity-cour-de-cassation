#!/bin/sh

thisdir=`dirname $0`
feature_dir=$thisdir/../data/similarity/features
datadir=$thisdir/../data/similarity/dataset
results=$thisdir/../sim-results

# gold labels
labels=$datadir/ave-sim

# features based on gold
tfidf_arrets_gold=$feature_dir/tf_idf.arret.sommaire-model.1,2,3,g.2000000.gold
tfidf_sommaires_gold=$feature_dir/tf_idf.sommaire.sommaire-model.1,2,g.250000.gold
tfidf_titrages_gold=$feature_dir/tf_idf.titrage.titrage-model.1,g.250000.gold

edsim_arrets_gold=$feature_dir/edsim.arrets.gold
edsim_sommaires_gold=$feature_dir/edsim.sommaires.gold
edsim_titrages_gold=$feature_dir/edsim.titrages.gold


# features based on pred
mt_model=joint-8000


# potentially add models here
for model in mlp; do
    # make a separate folder for this model
    resdir=$thisdir/../data/similarity/results/mlp
    [ -d $resdir ] || mkdir $resdir

    # ------ start off with individual gold features ------
    [ -d $resdir/gold ] || mkdir $resdir/gold

    echo $resdir/gold/tfidf.arrets.gold.correl
    if [ ! -s $resdir/gold/tfidf.arrets.gold.correl ]; then
	paste $tfidf_arrets_gold | OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py \
	    -g $labels -m $model -n "$model.tfidf.arrets.gold" > $resdir/gold/tfidf.arrets.gold.correl
    fi
    echo $resdir/gold/tfidf.sommaires.gold.correl
    if [ ! -s $resdir/gold/tfidf.sommaires.gold.correl ]; then
	paste $tfidf_sommaires_gold | OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py \
	-g $labels -m $model -n "$model.tfidf.sommaires.gold" > $resdir/gold/tfidf.sommaires.gold.correl
    fi

    echo $resdir/gold/tfidf.titrages.gold.correl
    if [ ! -s $resdir/gold/tfidf.titrages.gold.correl ]; then
	paste $tfidf_titrages_gold | OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py \
	-g $labels -m $model -n "$model.tfidf.titrages.gold" > $resdir/gold/tfidf.titrages.gold.correl
    fi

    echo $resdir/gold/edsim.arrets.gold.correl
    if [ ! -s $resdir/gold/edsim.arrets.gold.correl ]; then
	paste $edsim_arrets_gold | OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py \
	-g $labels -m $model -n "$model.edsim.arrets.gold" > $resdir/gold/edsim.arrets.gold.correl
    fi

    echo $resdir/gold/edsim.sommaires.gold.correl
    if [ ! -s $resdir/gold/edsim.sommaires.gold.correl ]; then
	paste $edsim_sommaires_gold | OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py \
	    -g $labels -m $model -n "$model.edsim.sommaires.gold" > $resdir/gold/edsim.sommaires.gold.correl
    fi

    echo $resdir/gold/edsim.titrages.gold.correl
    if [ ! -s $resdir/gold/edsim.titrages.gold.correl ]; then
	paste $edsim_titrages_gold | OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py \
	    -g $labels -m $model -n "$model.edsim.titrages.gold" > $resdir/gold/edsim.titrages.gold.correl
    fi


    # ------ combine gold features -----
    echo $resdir/gold/tfidf.titrages.gold__tfidf.sommaire.gold.correl
    if [ ! -s $resdir/gold/tfidf.titrages.gold__tfidf.sommaires.gold.correl ]; then
	paste $tfidf_titrages_gold $tfidf_sommaires_gold | \
        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
        $model -n "$model.tfidf.titrages.gold__tfidf.sommaires.gold" \
	> $resdir/gold/tfidf.titrages.gold__tfidf.sommaire.gold.correl
    fi
    
    echo $resdir/gold/edsim.titrages.gold__edsim.sommaires.gold.correl
    if [ ! -s $resdir/gold/edsim.titrages.gold__edsim.sommaires.gold.correl ]; then
	paste $edsim_titrages_gold $edsim_sommaires_gold | \
        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
        $model -n "$model.edsim.titrages.gold__edsim.sommaires.gold" \
        > $resdir/gold/edsim.titrages.gold__edsim.sommaires.gold.correl
    fi

    echo $resdir/gold/edsim.titrages.gold__tfidf.sommaires.gold.correl
    if [  ! -s $resdir/gold/edsim.titrages.gold__tfidf.sommaires.gold.correl ]; then
	paste $edsim_titrages_gold $tfidf_sommaires_gold | \
	OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
	$model -n "$model.edsim.titrages.gold__tfidf.sommaires.gold" \
        > $resdir/gold/edsim.titrages.gold__tfidf.sommaires.gold.correl
    fi

    echo $resdir/gold/tfidf.titrages.gold__edsim.sommaires.gold.correl
    if [ ! -s $resdir/gold/tfidf.titrages.gold__edsim.sommaires.gold.correl ]; then
	paste $tfidf_titrages_gold $edsim_sommaires_gold | \
	OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
	$model -n "$model.tfidf.titrages.gold__edsim.sommaires.gold" \
        > $resdir/gold/tfidf.titrages.gold__edsim.sommaires.gold.correl
    fi

    echo $resdir/gold/tfidf.sommaires.gold__edsim.sommaires.gold.correl
    if [ ! -s $resdir/gold/tfidf.sommaires.gold__edsim.sommaires.gold.correl ]; then
	paste $tfidf_sommaires_gold $edsim_sommaires_gold | \
	OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
	$model -n "$model.tfidf.sommaires.gold__edsim.sommaires.gold" \
        > $resdir/gold/tfidf.sommaires.gold__edsim.sommaires.gold.correl
    fi
    
    # ------ then produce individual and combined features for predicted titrages
    # add different strategies here (for example sampling, diverse beam)
    for subfolder in pred gold+pred combo; do
	[ -d $resdir/$subfolder ] || mkdir $resdir/$subfolder
    done
    # add other MT model types here
    for mt_model in camembert joint-8000; do
	for subfolder in pred gold+pred combo; do
	    [ -d $resdir/$subfolder/$mt_model ] || mkdir $resdir/$subfolder/$mt_model
	done
	
	# shortcut to the features
	edsim_titrages_pred=$feature_dir/edsim.titrages.$mt_model.20
	tfidf_titrages_pred=$feature_dir/tf_idf.titrages.$mt_model.20
	edsim_titrages_gold_pred=$feature_dir/edsim.titrages.$mt_model.1+20
	tfidf_titrages_gold_pred=$feature_dir/tf_idf.titrages.$mt_model.1+20
	
	for strategy in beam ; do 
	    for subfolder in pred gold+pred combo; do
		[ -d $resdir/$subfolder/$mt_model/$strategy ] || mkdir $resdir/$subfolder/$mt_model/$strategy
	    done
	    for calc in max avg; do
		for subfolder in pred gold+pred combo; do
		    [ -d $resdir/$subfolder/$mt_model/$strategy/$calc ] || mkdir $resdir/$subfolder/$mt_model/$strategy/$calc
		done
		predresdir=$resdir/pred/$mt_model/$strategy/$calc
		goldpredresdir=$resdir/gold+pred/$mt_model/$strategy/$calc
		combodir=$resdir/combo/$mt_model/$strategy/$calc
		
		# for different numbers of predicted titrages
		for k in $(seq 20); do
		    
		    # individual features
		    
		    # predicted
		    echo $predresdir/edsim.titrages.$k.correl
		    echo "paste $edsim_titrages_pred.$strategy.pred.$calc.$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.edsim.titrages.pred.$mt_model.$strategy.$calc.$k" > $predresdir/edsim.titrages.$k.correl"
		    if [ ! -s $predresdir/edsim.titrages.$k.correl ]; then
			paste $edsim_titrages_pred.$strategy.pred.$calc.$k | \
			OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
			$model -n "$model.edsim.titrages.pred.$mt_model.$strategy.$calc.$k" > $predresdir/edsim.titrages.$k.correl
		    fi
		    read 

		    echo $predresdir/tfidf.titrages.$k.correl
		    if [ ! -s $predresdir/tfidf.titrages.$k.correl ]; then
			paste $tfidf_titrages_pred.$strategy.pred.$calc.$k | \
			OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
			$model -n "$model.tfidf.titrages.pred.$mt_model.$strategy.$calc.$k" > $predresdir/tfidf.titrages.$k.correl
		    fi

		    # gold+predicted
		    echo $goldpredresdir/edsim.titrages.1+$k.correl
		    if [ ! -s $goldpredresdir/edsim.titrages.1+$k.correl ]; then
			paste $edsim_titrages_gold_pred.$strategy.gold+pred.$calc.1+$k | \
			OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
			$model -n "$model.edsim.titrages.gold+pred.$mt_model.$strategy.$calc.1+$k" > $goldpredresdir/edsim.titrages.1+$k.correl
		    fi

		    echo $goldpredresdir/tfidf.titrages.1+$k.correl
		    if [ ! -s $goldpredresdir/tfidf.titrages.1+$k.correl ]; then
			paste $tfidf_titrages_gold_pred.$strategy.gold+pred.$calc.1+$k | \
			OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
			$model -n "$model.tfidf.titrages.gold+pred.$mt_model.$strategy.$calc.1+$k" > $goldpredresdir/tfidf.titrages.1+$k.correl
		    fi

		    # combined features
		    # -- adding gold titrage --

		    # predicted
                    if [ ! -s $combodir/tfidf.titrages.gold__tfidf.titrages.pred.$k.correl ]; then
                        paste $tfidf_titrages_gold $tfidf_titrages_pred.$strategy.pred.$calc.$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.tfidf.titrages.gold__tfidf.titrages.pred.$mt_model.$strategy.$calc.$k" > \
                        $combodir/tfidf.titrages.gold__tfidf.titrages.pred.$k.correl
		    fi

                    if [ ! -s $combodir/edsim.titrages.gold__edsim.titrages.pred.$k.correl ]; then
                        paste $edsim_titrages_gold $edsim_titrages_pred.$strategy.pred.$calc.$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.edsim.titrages.gold__edsim.titrages.pred.$mt_model.$strategy.$calc.$k" > \
                        $combodir/edsim.titrages.gold__edsim.titrages.pred.$k.correl
		    fi

		    # gold+predicted
                    if [ ! -s $combodir/tfidf.titrages.gold__tfidf.titrages.gold+pred.1+$k.correl ]; then
                        paste $tfidf_titrages_gold $tfidf_titrages_gold_pred.$strategy.gold+pred.$calc.1+$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.tfidf.titrages.gold__tfidf.titrages.pred.$mt_model.$strategy.$calc.$k" > \
                        $combodir/tfidf.titrages.gold__tfidf.titrages.gold+pred.1+$k.correl
		    fi

                    if [ ! -s $combodir/edsim.titrages.gold__edsim.titrages.gold+pred.1+$k.correl ]; then
                        paste $edsim_titrages_gold $edsim_titrages_gold_pred.$strategy.gold+pred.$calc.1+$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.edsim.titrages.gold__edsim.titrages.gold+pred.$mt_model.$strategy.$calc.1+$k" > \
                        $combodir/edsim.titrages.gold__edsim.titrages.gold+pred.1+$k.correl
		    fi


		    # -- adding gold sommaire --
		    # predicted
                    if [ ! -s $predresdir/tfidf.sommaires.gold__tfidf.titrages.pred.$k.correl ]; then
                        paste $tfidf_sommaires_gold $tfidf_titrages_pred.$strategy.pred.$calc.$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.tfidf.sommaires.gold__tfidf.titrages.pred.$mt_model.$strategy.$calc.$k" > \
                        $combodir/tfidf.sommaires.gold__tfidf.titrages.pred.$k.correl
		    fi

                    if [ ! -s $combodir/edsim.sommaires.gold__edsim.titrages.pred.$k.correl ]; then
                        paste $edsim_sommaires_gold $edsim_titrages_pred.$strategy.pred.$calc.$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.edsim.sommaires.gold__edsim.titrages.pred.$mt_model.$strategy.$calc.$k" > \
                        $combodir/edsim.sommaires.gold__edsim.titrages.pred.$k.correl
		    fi

		    # gold+predicted
                    if [ ! -s $combodir/tfidf.sommaires.gold__tfidf.titrages.gold+pred.1+$k.correl ]; then
                        paste $tfidf_sommaires_gold $tfidf_titrages_gold_pred.$strategy.gold+pred.$calc.1+$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.tfidf.sommaires.gold__tfidf.titrages.gold+pred.$mt_model.$strategy.$calc.1+$k" > \
                        $combodir/tfidf.sommaires.gold__tfidf.titrages.gold+pred.1+$k.correl
		    fi

                    if [ ! -s $combodir/edsim.sommaires.gold__edsim.titrages.gold+pred.1+$k.correl ]; then
                        paste $edsim_titrages_gold $edsim_titrages_gold_pred.$strategy.gold+pred.$calc.1+$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.edsim.sommaires.gold__edsim.titrages.gold+pred.$mt_model.$strategy.$calc.1+$k" > \
                        $combodir/edsim.sommaires.gold__edsim.titrages.gold+pred.1+$k.correl
		    fi

		    # -- adding gold titrage + sommaire --
		    # predicted
                    if [ ! -s $combodir/tfidf.titrages.gold__tfidf.sommaires.gold__tfidf.titrages.pred.$k.correl ]; then
                        paste $tfidf_titrages_gold $tfidf_sommaires_gold $tfidf_titrages_pred.$strategy.pred.$calc.$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.tfidf.titrages.gold__tfidf.sommaires.gold__tfidf.titrages.pred.$mt_model.$strategy.$calc.$k" > \
                        $combodir/tfidf.titrages.gold__tfidf.sommaires.gold__tfidf.titrages.pred.$k.correl
		    fi

                    if [ ! -s $combodir/edsim.titrages.gold__edsim.sommaires.gold__edsim.titrages.pred.$k.correl ]; then
                        paste $edsim_titrages_gold $edsim_sommaires_gold $edsim_titrages_pred.$strategy.pred.$calc.$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.edsim.titrages.gold__edsim.sommaires.gold__edsim.titrages.pred.$mt_model.$strategy.$calc.$k" > \
                        $combodir/edsim.titrages.gold__edsim.sommaires.gold__edsim.titrages.pred.$k.correl
		    fi

		    # gold+predicted
                    if [ ! -s $combodir/tfidf.titrages.gold__tfidf.sommaires.gold__tfidf.titrages.gold+pred.1+$k.correl ]; then
                        paste $tfidf_titrages_gold $tfidf_sommaires_gold $tfidf_titrages_gold_pred.$strategy.gold+pred.$calc.1+$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.tfidf.titrages.gold__tfidf.sommaires.gold__tfidf.titrages.gold+pred.$mt_model.$strategy.$calc.1+$k" > \
                        $combodir/tfidf.titrages.gold__tfidf.sommaires.gold__tfidf.titrages.gold+pred.1+$k.correl
		    fi

                    if [ ! -s $combodir/edsim.titrages.gold__edsim.sommaires.gold__edsim.titrages.gold+pred.1+$k.correl ]; then
                        paste $edsim_titrages_gold $edsim_titrages_gold $edsim_titrages_gold_pred.$strategy.gold+pred.$calc.1+$k | \
                        OPENBLAS_NUM_THREADS=1 python $thisdir/correlation_sim.py -g $labels -m \
                        $model -n "$model.edsim.titrages.gold__edsim.sommaires.gold__edsim.titrages.gold+pred.$mt_model.$strategy.$calc.1+$k" > \
                        $combodir/edsim.titrages.gold__edsim.sommaires.gold__edsim.titrages.gold+pred.1+$k.correl
		    fi
		done
	    done
	done
    done
done



