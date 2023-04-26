#!/usr/bin/bash
# This code removes straggling PRC/ERC voxels
# formerly a fucntion in cleanup_prc_taupet_adni_....sh

in=$1
out=$2

TMPDIR=$(mktemp -d)
INFO=$(c3d $in -thresh 9 inf 1 0 -dilate 0 1x1x0vox  -o $TMPDIR/temp.nii.gz -info)
NS=$(echo $INFO | sed -e "s/.*dim = .//g" -e "s/.;.*bb.*//g" | awk -F ',' '{print $3}')
slicecmd=$(for((i=1;i<$NS;i++)); do echo "-push X -slice z $i -voxel-sum "; done)
c3d $TMPDIR/temp.nii.gz -popas X $slicecmd | grep Voxel | awk '{print $3}' > $TMPDIR/counts.txt
NNZ=$(cat $TMPDIR/counts.txt | grep -v '^0$' | wc -l)
MEDIAN=$(cat $TMPDIR/counts.txt | grep -v '^0$' | sort -n | tail -n $((NNZ/2)) | head -n 1)
CUTOFF=$((MEDIAN / 4))
RULE=$(cat $TMPDIR/counts.txt | awk "{print NR-1,int(\$1 < $CUTOFF)}")
c3d $in $TMPDIR/temp.nii.gz -copy-transform -cmv -replace $RULE -popas M $in -as X \
-thresh 9 inf 1 0 -push M -times -scale -1 -shift 1 \
-push X -times -o $out
NLEFT=$(cat $TMPDIR/counts.txt | awk "\$1 > $CUTOFF {k++} END {print k}")
