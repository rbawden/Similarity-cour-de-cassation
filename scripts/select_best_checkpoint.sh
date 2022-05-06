#!/bin/sh

thisdir=`dirname $0`
maindir=`realpath $thisdir/..`

valid_outputs_dir=$1

# check args
if [ "$#" -ne 1 ]; then
    echo "Error: expected 2 arguments: valid_outputs_folder"
    echo "Usage: $0 <valid_outputs_folder>"
    exit
fi

echo "Selecting best checkpoint based on the outputs in $valid_outputs_dir"

#criterion=weighted_acc
criterion=weighted_acc # change to weighted_acc or micro_acc
best_score=-1
best_checkpoint=None
if [ -f $valid_outputs_dir/../valid.$criterion.eval ]; then
    rm $valid_outputs_dir/../valid.$criterion.eval
fi

for checkpoint in `ls -tr $valid_outputs_dir/*postproc`; do
    score=`python $thisdir/evaluate.py $checkpoint $maindir/data/final/valid.lowercase.titrage $criterion`
    number=`echo $checkpoint | perl -pe 's/^.*?checkpoint(.+?).pt.*$/\1/'`
    if [[ $number == "_best" ]] || [[ $number == "_last" ]]; then
	continue
    fi
    echo "Checkpoint $number = $score"
    if (( $(echo "$score > $best_score" | bc -l) )); then
	best_score=$score
	best_checkpoint=$number
	echo ">> New best score!"
	echo "$number = $score = best" >> $valid_outputs_dir/../valid.$criterion.eval
    else
	echo "$number = $score" >> $valid_outputs_dir/../valid.$criterion.eval
    fi
done

# copy model of best score (assuming models are found in the parent directory of valid_outputs/)
cp $valid_outputs_dir/../checkpoint$best_checkpoint.pt $valid_outputs_dir/../checkpoint_best_$criterion.pt
echo "Best checkpoint = $num with a $criterion score of $score"

echo "$best_checkpoint = $best_score" > $valid_outputs_dir/../checkpoint_best_$criterion.eval
