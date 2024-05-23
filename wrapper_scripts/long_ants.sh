#!/usr/bin/bash 
module load singularity

t1_images=$1
output_dir=$2
dry_run=$3

if [[ $dry_run == "True" ]] ; then 
    echo Run these images: $t1_images
    echo Store output in dir: $output_dir
else
    singularity run --containall /project/picsl/cookpa/antsct-aging/antsct-aging-0.5.0.sif --anatomical-images $t1_images --longitudinal --output-dir $output_dir
fi