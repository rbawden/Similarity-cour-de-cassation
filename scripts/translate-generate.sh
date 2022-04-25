#!/bin/sh

model_path=$1
dataset=$2
data=$3
output=$4

# check args
if [ "$#" -ne 4 ]; then
    echo "Error: expected 4 arguments: model_path dataset data output"
    echo "Usage: $0 <model_path> <dataset> <data> <output>"
    exit
fi

if [ ! -f $output.output ]; then
    fairseq-generate $data --gen-subset $dataset --path $model_path > $output.output
fi

if [ ! -f $output.postproc ]; then
    cat $output.output | grep "H-" | perl -pe 's/^H-//' | sort -n | cut -f3 | perl -pe 's/ //g;s/▁/ /g' > $output.postproc
fi




