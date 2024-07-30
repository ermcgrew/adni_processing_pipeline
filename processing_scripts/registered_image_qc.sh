#!/bin/bash
# Create screenshot for registered images
# copy with module modifications of:
# /project/hippogang_1/srdas/wd/TAUPET/longnew/simpleregqa.sh
if [ $# != 3 ]; then
  echo Usage: $0 im1.nii.gz im2.nii.gz output.png
  exit 1
fi

IM1=$1
IM2=$2
OUT=$3

module unload matlab/2023a 
module load ImageMagick
module load c3d

if [[ ! $TMPDIR ]]; then
  TMPDIR=$(mktemp -d)
fi
# Resample to IM1 resolution
res=$(c3d $IM1 -info | cut -f 3 -d ";" | cut -f 2 -d "[" |  cut -f 1 -d "]" | sed -e "s/, /x/g")mm
echo $res
c3d -verbose  $IM2 -stretch 1% 99% 0 255 -clip 0 255 -resample-mm $res -as IM2  \
  $IM1 -stretch 1% 99% 0 255 -clip 0 255 -reslice-identity -as IM1 \
  -slice z 50% -type uchar -o $TMPDIR/im1z.png \
  -push IM1 -slice y 50% -type uchar -o $TMPDIR/im1y.png \
  -push IM1 -slice x 50% -type uchar -o $TMPDIR/im1x.png \
  -clear \
  -push IM2 -slice z 50% -type uchar -o $TMPDIR/im2z.png \
  -push IM2 -slice y 50% -type uchar -o $TMPDIR/im2y.png \
  -push IM2 -slice x 50% -type uchar -o $TMPDIR/im2x.png 

for fn in $TMPDIR/im??.png; do
  /project/wolk/ADNI2018/scripts/adni_processing_pipeline/wrapper_scripts/ashs_grid.sh -o 0.25 -s 25 -c white $fn $fn
done

montage -tile 3x -geometry +3+3 -mode Concatenate $TMPDIR/im1?.png $TMPDIR/im2?.png $OUT
convert $OUT -bordercolor Black -border 1x1 $OUT
