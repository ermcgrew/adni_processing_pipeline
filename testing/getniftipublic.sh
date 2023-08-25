#!/usr/bin/bash

id=$1
scandate=$2
# uid=$3

niftis=($( find /project/wolk/PUBLIC/nifti/${id}/*/${scandate}*/*/*.nii.gz ))
echo $niftis 