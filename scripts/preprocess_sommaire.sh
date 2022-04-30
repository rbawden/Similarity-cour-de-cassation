#!/bin/sh
thisdir=`dirname $0`

sp_model=$1

# check args
if [ "$#" -ne 1 ]; then
    echo "Error: expected 1 argument: sp_model"
    echo "Usage: $0  <sp_model>"
    exit
fi

# apply sentencepiece
perl -CS -Mutf8 -Mlocale -ne 'print lc' | python $thisdir/spm_encode.py --model $sp_model
