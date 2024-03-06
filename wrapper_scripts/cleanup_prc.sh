#!/usr/bin/bash
# This code removes straggling PRC/ERC voxels
# formerly a fucntion in cleanup_prc_taupet_adni_....sh

ashst2_left=$1
cleanup_left=$2
ashst2_right=$3
cleanup_right=$4
ashst2_tse=$5
cleanup_both=$6

for side in left right ; do 
    if [ "$side" == "left" ] ; then
        input=$ashst2_left
        out=$cleanup_left
    elif [ "$side" == "right" ] ; then
        input=$ashst2_right
        out=$cleanup_right
    fi
    
    TMPDIR=$(mktemp -d)

    INFO=$(c3d $input -thresh 9 inf 1 0 -dilate 0 1x1x0vox  -o $TMPDIR/temp.nii.gz -info)
    NS=$(echo $INFO | sed -e "s/.*dim = .//g" -e "s/.;.*bb.*//g" | awk -F ',' '{print $3}')
    slicecmd=$(for((i=1;i<$NS;i++)); do echo "-push X -slice z $i -voxel-sum "; done)
    c3d $TMPDIR/temp.nii.gz -popas X $slicecmd | grep Voxel | awk '{print $3}' > $TMPDIR/counts.txt

    NNZ=$(cat $TMPDIR/counts.txt | grep -v '^0$' | wc -l)
    MEDIAN=$(cat $TMPDIR/counts.txt | grep -v '^0$' | sort -n | tail -n $((NNZ/2)) | head -n 1)
    CUTOFF=$((MEDIAN / 4))
    RULE=$(cat $TMPDIR/counts.txt | awk "{print NR-1,int(\$1 < $CUTOFF)}")
    c3d $input $TMPDIR/temp.nii.gz -copy-transform -cmv -replace $RULE -popas M $input -as X \
    -thresh 9 inf 1 0 -push M -times -scale -1 -shift 1 \
    -push X -times -o $out

    NLEFT=$(cat $TMPDIR/counts.txt | awk "\$1 > $CUTOFF {k++} END {print k}")
    rm -rf $TMPDIR
done

c3d $ashst2_tse -as A ${cleanup_left} -interp NN -reslice-identity -push A ${cleanup_right} -interp NN -reslice-identity -add -o ${cleanup_both}