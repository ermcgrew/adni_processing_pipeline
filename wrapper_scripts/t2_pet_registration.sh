#!/usr/bin/bash
module load greedy

t2=$1
pet_nifti=$2
pet_t2_reg=$3
t2ashs_reg=$4
pet_t1_reg_ras=$5

greedy -d 3 -rf $t2 -rm $pet_nifti $pet_t2_reg -r $t2ashs_reg $pet_t1_reg_ras