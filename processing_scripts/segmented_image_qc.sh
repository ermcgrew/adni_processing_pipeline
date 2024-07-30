#!/bin/bash
# Create screenshot for single label file
# copy with module modifications of:
# /project/hippogang_1/srdas/wd/TAUPET/longnew/simplesegqa.sh
if [ $# != 4 ]; then
  echo Usage: $0 gray.nii.gz seg.nii.gz itksnaplabelfile output.png
  exit 1
fi

GRAY=$1
SEG=$2
LFILE=$3
OUT=$4

module unload matlab/2023a 
module load ImageMagick

if [[ ! $TMPDIR ]]; then
  TMPDIR=$(mktemp -d)
fi
c3d -verbose  $SEG -int 0 -resample-mm 1x1x1mm -as SEG  \
  $GRAY -stretch 1% 99% 0 255 -clip 0 255 -reslice-identity -as GRAY \
  -slice z 50% -type uchar -o $TMPDIR/grayz.png \
  -popas GRAYZ -push GRAY -slice y 50% -type uchar -o $TMPDIR/grayy.png \
  -popas GRAYY -push GRAY -slice x 50% -type uchar -o $TMPDIR/grayx.png \
  -popas GRAYX -push SEG \
  -slice z 50% -popas SEGZ -push SEG -slice y 50% -popas SEGY -push SEG -slice x 50% -popas SEGX \
  -push GRAYZ -push SEGZ -oli $LFILE 0.5 -omc 3 $TMPDIR/segz.png \
  -push GRAYY -push SEGY -oli $LFILE 0.5 -omc 3 $TMPDIR/segy.png \
  -push GRAYX -push SEGX -oli $LFILE 0.5 -omc 3 $TMPDIR/segx.png 

montage -tile 3x -geometry +3+3 -mode Concatenate $TMPDIR/gray?.png $TMPDIR/seg?.png $OUT
convert $OUT -bordercolor Black -border 1x1 $OUT
