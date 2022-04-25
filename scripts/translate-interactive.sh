#!/bin/sh
thisdir=`dirname $0`

model_path=$1
data_dir=$2
sp_model=$3
# expects standard input to be one example per line, with each line formatted as MATTER <t> SOMMAIRE

output=output.$$

# check args
if [ "$#" -ne 3 ]; then
    echo "Error: expected 2 argument: model_path data_path sp_model"
    echo "Usage: $0 <model_path> <data_path> <sp_model>"
    exit
fi

# apply sentencepiece
python $thisdir/spm_encode.py --model $sp_model > $output.preproc

cat $output.preproc

# apply translation
cat $output.preproc | fairseq-interactive $data_dir --path $model_path --batch-size 4 --buffer-size 4 -s sommaire -t titrage > $output

# postprocess translation
cat $output | grep "H-" | perl -pe 's/^H-//' | sort -n | cut -f3 | perl -pe 's/ //g;s/▁/ /g'


rm $output $output.preproc



