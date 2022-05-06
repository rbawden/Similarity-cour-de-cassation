#!/bin/sh
thisdir=`dirname $0`

model_path=$1
data_dir=$2
sp_model=$3
n=${4:-1} # nbest
sampling=$5 # supply a temperature here if sampling to be used (otherwise uses beam)

# expects standard input to be one example per line, with each line formatted as MATTER <t> SOMMAIRE

# check args
if [ "$#" -lt 3 ]; then
    echo "Error: expected at least 3 arguments: model_path data_path sp_model (n) (sampling)"
    echo "Usage: $0 <model_path> <data_path> <sp_model> (<n_for_nbest> (<sampling>)"
    exit
fi

beam_param="--beam $n"

if [ ! -z $sampling ]; then
    #sampling_param="--diverse-beam-groups $n"
    sampling_param="--sampling --temperature $sampling"
fi

output=output.$$ # temporary output file to store intermediate values
# apply preprocesing (lowercase and sentencepiece)
bash $thisdir/preprocess_sommaire.sh $sp_model > $output.preproc

# apply translation
cat $output.preproc | \
    fairseq-interactive $data_dir --path $model_path --batch-size 4 --buffer-size 4 \
    -s sommaire -t titrage --nbest $n $sampling_param $beam_param --truncate-source --max-source-positions 508 \
    > $output

# postprocess translation
cat $output | grep "H-" | perl -pe 's/^H-//' | sort -n | cut -f3 | perl -pe 's/ //g;s/▁/ /g'

#rm $output $output.preproc



