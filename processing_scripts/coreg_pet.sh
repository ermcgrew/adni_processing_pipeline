#!/bin/bash 
### copied and cleaned up from /project/hippogang_1/srdas/wd/TAUPET/longnew/coreg_pet.sh"
set -x

# ROOT=~srdas/wd/ADNI23

# if [ -z $ROOT ]; then
#   echo "Please define ROOT to point to the top level image analysis directory"
#   exit 1
# fi

if [ $# -lt 4 ]; then
  echo Usage: $0 SubjectID T1 PET MRIDATE WDIR
  exit 1
else
  ID=$1
  T1=$2
  PET=$3
  MRIDATE=$4
  WDIR=$5
fi

if [ ! -z $WDIR ]; then
  cd $WDIR
else
  # cd $ROOT/{$ID}
  echo Must define a directory for output
  exit 1
fi

# export ANTSPATH=~sudas/bin/ants_cook_Sep012015/
# reg=${ANTSPATH}antsRegistration

# dim=3

f=$T1
m=$PET
OUT=${PET%.nii.gz}_to_${MRIDATE}_T1

~sudas/bin/ants_cook_Sep012015/antsRegistration -d 3  \
  -m Mattes[  $f, $m , 1 , 32, random , 0.1 ] \
  -t Rigid[ 0.2 ] \
  -c [1000x1000x1000,1.e-7,20]  \
  -s 4x2x0  \
  -r [ $f, $m, 1 ] \
  -f 4x2x1 -l 1 \
  -a 0 \
  -o [ $OUT, ${OUT}.nii.gz, ${OUT}_inverse.nii.gz ] -v 

~sudas/bin/ConvertTransformFile 3 ${OUT}0GenericAffine.mat \
  ${OUT}0GenericAffine_RAS.mat --hm --ras

c3d ${OUT}.nii.gz -type float -o ${OUT}.nii.gz

rm -f ${OUT}_inverse.nii.gz
