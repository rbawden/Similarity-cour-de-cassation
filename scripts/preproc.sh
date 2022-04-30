#!/bin/sh
thisdir=`realpath $(dirname $0)`
maindir=`realpath $thisdir/..`
datadir=$maindir/data


function train_spm_bpe() {
    inputs=$1; bpesize=$2; model_prefix=$3
    if [ ! -f $model_prefix.model ]; then
	python $thisdir/spm_train.py \
            --input=$inputs \
	    --model_prefix=$model_prefix \
	    --vocab_size=$bpesize \
            --character_coverage=1.0 \
            --model_type=bpe \
            --num_threads=8 \
	    --user_defined_symbols="<t>"
    else
	echo "$model_prefix.model already exists. Not redoing training"
    fi
}

function train_spm_char() {
    inputs=$1; model_prefix=$2
    if [ ! -f $model_prefix.model ]; then
	python $thisdir/spm_train.py \
            --input=$inputs \
            --model_prefix=$model_prefix \
            --character_coverage=1.0 \
            --model_type=char \
            --num_threads=8 \
	    --user_defined_symbols="<t>"
    fi
}

function apply_spm() {
    model_path=$1; input=$2; output=$3
    if [ ! -f $output ]; then
	python $thisdir/spm_encode.py \
            --model=$model_path \
            --output_format=piece \
            --inputs=$input \
            --outputs=$output
    fi
}


function preprocess() {
    train_prefix=$1; valid_prefix=$2; test_prefix=$3; src=$4; trg=$5; output_dir=$6; joined=$7 \
	src_dict=$8; trg_dict=$9
    if [ ! -d $output_dir ]; then
	fairseq-preprocess --source-lang $src --target-lang $trg \
            --trainpref $train_prefix \
            --validpref $valid_prefix \
            --testpref $test_prefix \
            --destdir $output_dir \
            --workers 10 $joined $src_dict $trg_dict 
    fi
}

# camembert model
if [ ! -f $datadir/preproc/spm_camembert.model ]; then
    cp $maindir/camembert-base/sentencepiece.bpe.model $datadir/preproc/spm_camembert.model
    echo "Copying camembert sentencepiece model"
fi
for preproc in .lowercase; do
    for dset in train valid test; do
	for lang in sommaire titrage; do
	    apply_spm $datadir/preproc/spm_camembert.model \
		$datadir/preproc/$dset$preproc.sommaire-titrage.$lang \
		$datadir/preproc/$dset$preproc.sommaire-titrage.camembert.$lang
	    # correct <t> symbols
	    cat $datadir/preproc/$dset$preproc.sommaire-titrage.camembert.$lang | perl -pe 's/< t >/ <t>/g' \
		> $datadir/preproc/$dset$preproc.sommaire-titrage.camembert.$lang.tmp
	    mv $datadir/preproc/$dset$preproc.sommaire-titrage.camembert.$lang.tmp \
		$datadir/preproc/$dset$preproc.sommaire-titrage.camembert.$lang
	done
    done
    preprocess $datadir/preproc/train$preproc.sommaire-titrage.camembert \
        $datadir/preproc/valid$preproc.sommaire-titrage.camembert \
        $datadir/preproc/test$preproc.sommaire-titrage.camembert sommaire titrage \
        $datadir/bin/${preproc/.}.sommaire-titrage.camembert --joined-dictionary \
	--srcdict=$maindir/camembert-base/dict.txt 

    # manually copy over dictionaries because flags are not correctly copied over
    cp $maindir/camembert-base/dict.txt \
	$datadir/bin/${preproc/.}.sommaire-titrage.camembert/dict.sommaire.txt
    cp $maindir/camembert-base/dict.txt \
	$datadir/bin/${preproc/.}.sommaire-titrage.camembert/dict.titrage.txt
done

# train and apply bpe for different segmentation sizes
for bpesize in 8000 16000 24000 32000; do
    # for differently preprocessed versions
    for preproc in .lowercase ; do
	# train and apply a joint model between sommaires and titrages
	inputs="$datadir/preproc/train$preproc.sommaire-titrage.sommaire,$datadir/preproc/train$preproc.sommaire-titrage.titrage"
	model=$datadir/preproc/spm.$bpesize$preproc.joint-sommaire-titrage

	if [ $bpesize == char ]; then
	    echo "Training $model on $inputs w/ segmenation size char"
	    train_spm_char "$inputs" $model
	else
	    echo "Training $model in $inputs w/ segmentation size $bpesize"
            train_spm_bpe "$inputs" $bpesize $model
	fi

	# apply sentence piece
	for tmp_preproc in $preproc $preproc.semisup; do
	    for dset in train valid test; do
		for lang in sommaire titrage; do
		    echo "Applying $model.model to $datadir/preproc/$dset$tmp_preproc.sommaire-titrage.$lang"
		    apply_spm $model.model \
			$datadir/preproc/$dset$tmp_preproc.sommaire-titrage.$lang \
			$datadir/preproc/$dset$tmp_preproc.sommaire-titrage.joint-sp$bpesize.$lang
		done
            done
	    
	    # binarise with joint vocab
	    preprocess $datadir/preproc/train$tmp_preproc.sommaire-titrage.joint-sp$bpesize \
		$datadir/preproc/valid$tmp_preproc.sommaire-titrage.joint-sp$bpesize \
		$datadir/preproc/test$tmp_preproc.sommaire-titrage.joint-sp$bpesize sommaire titrage \
		$datadir/bin/${tmp_preproc/.}.sommaire-titrage.joint-sp$bpesize --joined-dictionary
	    # binarise without joint vocab (although bpe was calculated jointly)
	    preprocess $datadir/preproc/train$tmp_preproc.sommaire-titrage.joint-sp$bpesize \
		$datadir/preproc/valid$tmp_preproc.sommaire-titrage.joint-sp$bpesize \
		$datadir/preproc/test$tmp_preproc.sommaire-titrage.joint-sp$bpesize sommaire titrage \
            $datadir/bin/${tmp_preproc/.}.sommaire-titrage.joint-sp$bpesize.nojoin
	done

	# train a separate model for each of sommaires and titrages
	for lang in sommaire titrage; do
	    input=$datadir/preproc/train$preproc.sommaire-titrage.$lang
	    model=$datadir/preproc/spm.$bpesize$preproc.sep-$lang
	    if [ $bpesize == char ]; then
		train_spm_char $input $model
	    else
		train_spm_bpe $input $bpesize $model
	    fi
	    for dset in train valid test; do
		apply_spm $model.model \
		    $datadir/preproc/$dset$preproc.sommaire-titrage.$lang \
		    $datadir/preproc/$dset$preproc.sommaire-titrage.sep-sp$bpesize.$lang
	    done
	done
    done
done
