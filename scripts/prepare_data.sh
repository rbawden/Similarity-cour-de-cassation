#!/bin/sh

thisdir=`realpath $(dirname $0)`
maindir=`realpath $thisdir/..`

# Divide into syntheses and keyword sequences
for subfolder in $maindir/data/final $maindir/data/preproc $maindir/data/bin; do
    [ -d $subfolder ] || mkdir -p $subfolder
done

# Get dataset splits
if [ ! -f $maindir/data/final/train.tsv ]; then
    python $thisdir/create_dataset_split.py $maindir/data/orig/ $maindir/data/final
fi

for dset in train valid test; do
    cat $maindir/data/final/$dset.tsv | cut -f 17 | tail -n +2 > $maindir/data/final/$dset.sommaire
    cat $maindir/data/final/$dset.tsv | cut -f 5-16 | tail -n +2 | perl -pe 's/^[\t ]*(.+?)[\t ]*$/\1/' | perl -pe 's/\t/ <t> /g' > $maindir/data/final/$dset.titrage
    cat $maindir/data/final/$dset.tsv | cut -f 4 | tail -n +2 > $maindir/data/final/$dset.matiere
    for suffix in sommaire titrage matiere; do
        cat $maindir/data/final/$dset.$suffix | perl -CS -Mutf8 -Mlocale -ne 'print lc' > $maindir/data/final/$dset.lowercase.$suffix
    done
    # data for titrage
    paste $maindir/data/final/$dset.lowercase.matiere \
	$maindir/data/final/$dset.lowercase.sommaire | perl -pe 's/\t/ <t> /' \
	> $maindir/data/preproc/$dset.lowercase.sommaire-titrage.sommaire
    ln -sf $maindir/data/final/$dset.lowercase.titrage $maindir/data/preproc/$dset.lowercase.sommaire-titrage.titrage
done

# download CamemBERT
if [ ! -d $maindir/camembert-base ]; then
    wget https://dl.fbaipublicfiles.com/fairseq/models/camembert-base.tar.gz
    tar -xzvf $maindir/camembert-base.tar.gz -C $maindir/
    rm $maindir/camembert-base.tar.gz
    # replace last word with <t> token
    mv $maindir/camembert-base/dict.txt $maindir/camembert-base/orig-dict.txt
    cat <(head -n -1 $maindir/camembert-base/orig-dict.txt) <(echo "<t> 999") <(echo "<mask> 999")  > $maindir/camembert-base/dict.txt
fi

# prepare data for semi-supervised prediction
bash $thisdir/prepare_data_semisup.sh

# do BPE + char segmentation
bash $thisdir/preproc.sh
