#!/usr/bin/bash

session_filepath=$1
date_id_prefix=$2


module load singularity
SINGULARITYENV_TMPDIR=/tmp

singularity run -B ${session_filepath}:/data/input -B ${session_filepath}:/data/output /project/wolk/hd-bet/hd-bet-latest.sif \
                -i /data/input/${date_id_prefix}_flair.nii.gz -o /data/output/${date_id_prefix}_flair_skullstrip.nii.gz \
                -device cpu -tta 0 -mode fast
 