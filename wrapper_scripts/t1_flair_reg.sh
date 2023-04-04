#!/usr/bin/bash

module load fsl
export FSLOUTPUTTYPE=NIFTI_GZ

t1_trim=$1
flair=$2
output_filename=$3

flirt -in $t1_trim -ref $flair -omat $output_filename