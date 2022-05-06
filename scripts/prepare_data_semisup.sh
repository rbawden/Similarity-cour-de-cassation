#!/bin/sh

thisdir=`realpath $(dirname $0)`
maindir=`realpath $thisdir/..`

for dset in train valid test; do
    for preproc in .lowercase; do
	if [ ! -f $maindir/data/preproc/$dset$preproc.semisup.sommaire-titrage.sommaire-titrag ]; then
	    python $thisdir/prepare_semisupervised_data.py \
		$maindir/data/preproc/$dset$preproc.sommaire-titrage.sommaire \
		$maindir/data/preproc/$dset$preproc.sommaire-titrage.titrage \
		> $maindir/data/preproc/$dset$preproc.semisup.sommaire-titrage.sommaire-titrage
	fi
	if [ ! -f $maindir/data/preproc/$dset$preproc.semisup.sommaire-titrage.sommaire ]; then
	    cut -f 1 $maindir/data/preproc/$dset$preproc.semisup.sommaire-titrage.sommaire-titrage \
		> $maindir/data/preproc/$dset$preproc.semisup.sommaire-titrage.sommaire
	fi
	if [ ! -f $maindir/data/preproc/$dset$preproc.semisup.sommaire-titrage.titrage ]; then
	    cut -f 2 $maindir/data/preproc/$dset$preproc.semisup.sommaire-titrage.sommaire-titrage \
		> $maindir/data/preproc/$dset$preproc.semisup.sommaire-titrage.titrage
	fi
    done
done
