#!/bin/bash
#SBATCH --job-name=bpe-multitok    # create a short name for your job
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --cpus-per-task=10       # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --partition=gpu          # Name of the partition
#SBATCH --gres=gpu:rtx6000:1     # GPU nodes are only available in gpu partition
#SBATCH --mem=20G                # Total memory allocated
#SBATCH --hint=multithread       # we get physical cores not logical
#SBATCH --time=20:00:00          # total run time limit (HH:MM:SS)
#SBATCH --output=gpu_gen%j.out   # output file name
#SBATCH --error=gpu_gen%j.out    # error file name
##SBATCH --array=0-10%1

#echo "### Running $SLURM_JOB_NAME ###"

#set -x
cd ${SLURM_SUBMIT_DIR}

if [ -n $SLURM_JOB_ID ];  then
    # check the original location through scontrol and $SLURM_JOB_ID
    thisscript=$(scontrol show job $SLURM_JOBID | awk -F= '/Command=/{print $2}')
    thisdir=`dirname $thisscript`
else
    # otherwise: started with bash. Get the real location.
    thisdir=`realpath $(dirname $0)`
fi

module purge
module load gnu8 cuda

# translate each of the sommaires (with matiere at the start separated by <t>)
for sommaire_num in 1 2; do
    # first with beam search
    if [ ! -f $thisdir/../data/similarity/predicted/titrages$sommaire_num.lower.joint-8000.20.beam.pred ]; then
	paste $thisdir/../data/similarity/dataset/matiere$sommaire_num.lower.gold \
	    $thisdir/../data/similarity/dataset/sommaire$sommaire_num.lower.gold | perl -pe 's/\t/ <t> /' | \
	    bash $thisdir/translate-interactive.sh \
	    $thisdir/../models/sommaire2titrage/joint/8000/model-1/checkpoint_best_weighted_acc.pt \
	    $thisdir/../data/bin/lowercase.sommaire-titrage.joint-sp8000 \
	    $thisdir/../data/preproc/spm.8000.lowercase.joint-sommaire-titrage.model 20 \
	    > $thisdir/../data/similarity/predicted/titrages$sommaire_num.lower.joint-8000.20.beam.pred
    fi
    # now with sampling
    for temp in 0.5 0.6 0.7 0.8 0.9 0.95; do
	if [ ! -f $thisdir/../data/similarity/predicted/titrages$sommaire_num.lower.joint-8000.20.sampling.$temp.pred ]; then
	    paste $thisdir/../data/similarity/dataset/matiere$sommaire_num.lower.gold \
		$thisdir/../data/similarity/dataset/sommaire$sommaire_num.lower.gold | perl -pe 's/\t/ <t> /' | \
		bash $thisdir/translate-interactive.sh \
		$thisdir/../models/sommaire2titrage/joint/8000/model-1/checkpoint_best_weighted_acc.pt \
		$thisdir/../data/bin/lowercase.sommaire-titrage.joint-sp8000 \
		$thisdir/../data/preproc/spm.8000.lowercase.joint-sommaire-titrage.model 20 $temp \
		> $thisdir/../data/similarity/predicted/titrages$sommaire_num.lower.joint-8000.20.sampling.$temp.pred
	fi
    done
done
