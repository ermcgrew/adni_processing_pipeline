#!/usr/bin/bash

session_filepath=$1
date_id_prefix=$2
current_wmh_prep_dir=$3

module load singularity
SINGULARITYENV_TMPDIR=/tmp

dataset_flair="${session_filepath}/${date_id_prefix}_flair.nii.gz"

if [[ -h $dataset_flair ]] ; then 
    realoc=$(readlink $dataset_flair )
    path_tobind=$(dirname $realoc )
    inputfile=$( basename $realoc)
else
    path_tobind=$session_filepath
    inputfile=${date_id_prefix}_flair.nii.gz
fi

singularity run -B ${path_tobind}:/data/input -B ${session_filepath}:/data/output /project/wolk/hd-bet/hd-bet-latest.sif \
                -i /data/input/$inputfile -o /data/output/${date_id_prefix}_flair_skullstrip.nii.gz \
                -device cpu -tta 0 -mode fast


# singularity run -B ${session_filepath}:/data/input -B ${session_filepath}:/data/output /project/wolk/hd-bet/hd-bet-latest.sif \
#                 -i /data/input/${date_id_prefix}_flair.nii.gz -o /data/output/${date_id_prefix}_flair_skullstrip.nii.gz \
#                 -device cpu -tta 0 -mode fast


if [[ ! -d ${current_wmh_prep_dir} ]] ; then
    mkdir -p ${current_wmh_prep_dir}/data_for_inference/
fi

cp ${session_filepath}/${date_id_prefix}_flair_skullstrip.nii.gz ${current_wmh_prep_dir}/data_for_inference/${date_id_prefix}_flair_wmh_0000.nii.gz