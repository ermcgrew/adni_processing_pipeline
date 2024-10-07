#!/usr/bin/bash

module load PETPVC/1.2.10

t1amysuvr=$1

## name of t1_pvc image
t1_pet_pvc=$( echo $t1amysuvr | sed 's/SUVR.nii.gz/pvc.nii.gz/')

echo Make PVC version $t1_pet_pvc
pvc_vc $t1amysuvr $t1_pet_pvc -x 8.0 -y 8.0 -z 8.0

