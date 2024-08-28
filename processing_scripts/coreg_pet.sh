#!/bin/bash 
### copied and cleaned up from /project/hippogang_1/srdas/wd/TAUPET/longnew/coreg_pet.sh"
set -x

if [ $# -lt 4 ]; then
  echo Usage: $0 T1 PET MRIDATE WDIR
  exit 1
else
  T1=$1
  PET=$2
  MRIDATE=$3
  WDIR=$4
fi

if [ ! -z $WDIR ]; then
  cd $WDIR
else
  echo Must define a directory for output
  exit 1
fi

f=$T1
m=$PET
OUT=${PET%.nii.gz}_to_${MRIDATE}_T1

/project/wolk/ADNI2018/scripts/adni_processing_pipeline/utilities/antsRegistration -d 3 \
  -m Mattes[  $f, $m , 1 , 32, random , 0.1 ] \
  -t Rigid[ 0.2 ] \
  -c [1000x1000x1000,1.e-7,20]  \
  -s 4x2x0  \
  -r [ $f, $m, 1 ] \
  -f 4x2x1 -l 1 \
  -a 0 \
  -o [ $OUT, ${OUT}.nii.gz, ${OUT}_inverse.nii.gz ] -v 

/project/wolk/ADNI2018/scripts/adni_processing_pipeline/utilities/ConvertTransformFile 3 ${OUT}0GenericAffine.mat \
  ${OUT}0GenericAffine_RAS.mat --hm --ras

c3d ${OUT}.nii.gz -type float -o ${OUT}.nii.gz

rm -f ${OUT}_inverse.nii.gz
