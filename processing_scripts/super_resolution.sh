#!/usr/bin/bash
#Usage: super_resolution.sh output_directory input_file output_file_name
#code adapted from /home/lxie/ADNI2018/scripts/RunT1BaselineLongitudianl_09092022.sh

module load c3d

output_directory=$1
T1TRIM=$2
T1SR=$3
SRPATH=$4

$SRPATH/NLMDenoise \
    -i $T1TRIM \
    -o $output_directory/T1w_trim_denoised.nii.gz

orient_code=$(c3d $T1TRIM -info | cut -d ';' -f 5 | cut -d ' ' -f 5)
if [[ $orient_code == "Oblique," ]]; then
    orient_code=$(c3d $T1TRIM -info | cut -d ';' -f 5 | cut -d ' ' -f 8)
fi

c3d $output_directory/T1w_trim_denoised.nii.gz \
    -swapdim RPI \
    -o $output_directory/T1w_trim_denoised.nii.gz

$SRPATH/NLMUpsample \
    -i $output_directory/T1w_trim_denoised.nii.gz \
    -o $output_directory/T1w_trim_denoised_SR.nii.gz \
    -lf 2 1 2

c3d $output_directory/T1w_trim_denoised_SR.nii.gz\
    -swapdim $orient_code \
    -clip 0 inf \
    -type short \
    -o $T1SR

echo "Using SRPATH=${SRPATH} to perform denoising and superresolution." > $output_directory/super_resolution_version.txt

rm $output_directory/*_short.nii.gz 