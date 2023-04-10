#!/usr/bin/bash
#adapted from cleanup_prc_.sh

# Find out which atlas was used
function getatlas()
{
  fn=$1
  range=$(c3d $fn  -info | cut -f 4 -d ";" | cut -f 2 -d "=")
  if [ "$range" == " [0, 13]" ]; then
    echo NOPHG
  fi
  if [ "$range" == " [0, 14]" ]; then
    echo PHG
  fi
  if [ "$range" == " [0, 8]" ]; then
    echo UTR
  fi
}


# This code removes straggling PRC/ERC voxels
function cleanup_prc()
{
  in=$1
  out=$2
  atype=$3

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
  echo $NLEFT
}



SDROOT='/project/wolk_2/ADNI2018/scripts/pipeline_test_data'

# mkdir -p cleanup/dump
# mkdir -p cleanup/png
# mkdir -p cleanup/stats


id="126_S_6721"
tp="2021-05-05"
# id=$1
# tp=$2
# t1tp=$3
# tautp=$4
# amytp=$5
# t2qa=$6
# t1qa=$7
# tauqa=$8
# amyqa=${9}
# line="${10}"
for side in left right; do
    # seg=$SDROOT/$id/$tp/sfsegnibtend/bootstrap/fusion/lfseg_corr_nogray_${side}.nii.gz
    seg=$SDROOT/$id/$tp/sfsegnibtend/final/126_S_6721_${side}_lfseg_corr_nogray.nii.gz
    # echo $seg
    # atlastype=$(getatlas $seg)
    # if [ -z "$atlastype" ]; then atlastype=PHG; fi;
    # if [ "$atlastype" == "PHG" ]; then
    # :
    # if [ ! -f cleanup/${id}_${tp}_seg_${side}.nii.gz ]; then
    #     cleanup_prc $seg \
    #     cleanup/${id}_${tp}_seg_${side}.nii.gz $atlastype
    # fi
    # fi

    tse=$SDROOT/$id/$tp/sfsegnibtend/tse.nii.gz
    if [ ! -f cleanup/${id}_${tp}_seg_both.nii.gz ]; then
    c3d $tse -as A cleanup/${id}_${tp}_seg_left.nii.gz -interp NN -reslice-identity \
        -push A cleanup/${id}_${tp}_seg_right.nii.gz -interp NN -reslice-identity -add \
        -o cleanup/${id}_${tp}_seg_both.nii.gz
    fi
done



#/project/wolk_2/ADNI2018/scripts/pipeline_test_data/126_S_6721/2021-05-05
