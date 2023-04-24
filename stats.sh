#!/usr/bin/bash
# adapted from cleanup_prc_taupet_adni_unified_flexible.sh

# Usage:
# ./stats.sh id wholebrainseg corticalthickness t1taureg t2taureg t1amyreg t2amyreg \
# sfsegnibtend/tse.nii.gz t1trim t2ashs_left_seg mri_only_mode_boolean

# 067_S_7094
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/2022-07-12/2022-07-12_067_S_7094_wholebrainseg/2022-07-12_067_S_7094_T1w_trim_brainx_ExtractedBrain/2022-07-12_067_S_7094_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/2022-07-12/thickness/067_S_7094CorticalThickness.nii.gz 
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/9999-99-99/9999-99-99_067_S_7094_taupet_to_2022-07-12_T1.nii.gz 
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/9999-99-99/9999-99-99_067_S_7094_taupet_to_2022-07-12_T2.nii.gz
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/9999-99-99/9999-99-99_067_S_7094_amypet_to_2022-07-12_T1.nii.gz
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/9999-99-99/9999-99-99_067_S_7094_amypet_to_2022-07-12_T2.nii.gz
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/2022-07-12/sfsegnibtend/tse.nii.gz 
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/2022-07-12/2022-07-12_067_S_7094_T1w_trim.nii.gz
# /project/wolk_2/ADNI2018/scripts/pipeline_test_data/067_S_7094/2022-07-12/sfsegnibtend/final/067_S_7094_left_lfseg_corr_nogray.nii.gz 
# false


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

# Generate the statistics for the subject
function genstats()
{
  in=$1
  inmp=$2
  taupet=$3
  taupetmp=$4
  amypet=$5
  amypetmp=$6
  atype=$7
  inboth=$8
  thickmp=${11}

  c3d $in $taupet -interp NN -reslice-identity $in -lstat > $TMPDIR/stattau.txt
  c3d $in $amypet -interp NN -reslice-identity $in -lstat > $TMPDIR/statamy.txt
  
  # Get T1 segmentation and get cerebellar GM
  c3d $inmp -as SEG -thresh 38 38 1 0 -erode 1 2x2x2vox -popas A \
    -push SEG -thresh 39 39 1 0 -erode 1 2x2x2vox -popas B \
    -push SEG -thresh 71 71 1 0 -erode 1 2x2x2vox -popas C \
    -push SEG -thresh 72 72 1 0 -erode 1 2x2x2vox -popas D \
    -push SEG -thresh 73 73 1 0 -erode 1 2x2x2vox -popas E \
    -push A -push B -add -push C -add -push D -add -push E -add -as CEREB \
    $taupetmp -interp NN -reslice-identity -push CEREB  -lstat > $TMPDIR/stattaump.txt
  c3d $inmp -as SEG -thresh 38 38 1 0 -popas A \
    -push SEG -thresh 39 39 1 0 -popas B \
    -push SEG -thresh 71 71 1 0 -popas C \
    -push SEG -thresh 72 72 1 0 -popas D \
    -push SEG -thresh 73 73 1 0 -popas E \
    -push SEG -thresh 40 40 1 0 -popas F \
    -push SEG -thresh 41 41 1 0 -popas G \
    -push A -push B -add -push C -add -push D -add -push E -add -push F -add -push G -add -erode 1 2x2x2vox -as CEREB \
    $amypetmp -interp NN -reslice-identity -push CEREB  -lstat > $TMPDIR/statamymp.txt

  # Occipital ROIs
  c3d $inmp -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000 -thresh 1000 1000 1 0 -as A $taupetmp -interp NN -reslice-identity -push A  -lstat > $TMPDIR/stattauocc.txt
  c3d $inmp -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000 -thresh 1000 1000 1 0 -as A $amypetmp -interp NN -reslice-identity -push A  -lstat > $TMPDIR/statamyocc.txt
  # Posterior Cingulate ROIs
  c3d $inmp -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $taupetmp -interp NN -reslice-identity -push A  -lstat > $TMPDIR/stattaupc.txt
  c3d $inmp -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $amypetmp -interp NN -reslice-identity -push A  -lstat > $TMPDIR/statamypc.txt
  
  # Other ROIs suitable for looking at subtypes: 
  # inf temporal gyrus (132 133) middle temporal (154 right 155 left) superior temporal 200 201 superior parietal 198 199 calcarine 108 109 angular gyrus 106 107 190 191 superior frontal
  c3d $inmp -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; do echo "-push A -thresh $roi $roi $roi 0" ; done) \
    -accum -add -endaccum -as SUM  $taupetmp -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/varioustaurois.txt
  c3d $inmp -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; do echo "-push A -thresh $roi $roi $roi 0" ; done) \
    -accum -add -endaccum -as SUM  $amypetmp -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/variousamyrois.txt
  
  # Mask with GM
  tissueseg=$(echo $thickmp | sed -e 's/CorticalThickness/BrainSegmentation/g')
  jacobian=$(echo $tissueseg | sed -e 's/BrainSegmentation/SubjectToTemplateLogJacobian/g' )
  tempgmmask=$TDIR/adninormalgmmask.nii.gz

  # All ROIs tau
  c3d $inmp -as A $taupetmp -interp NN -reslice-identity -push A  -lstat > $TMPDIR/alltau.txt
  c3d $inmp -as A $amypetmp -interp NN -reslice-identity -push A  -lstat > $TMPDIR/allamy.txt
  
  # All ROIs thickness
  MASKCOMM="$tissueseg -interp NN -reslice-identity -thresh 2 2 1 0 -times"
  TEMPMASKCOMM="$tempgmmask -interp NN -reslice-identity -thresh 1 1 1 0 -times"
  c3d $inmp -dup $MASKCOMM -as A $thickmp -interp NN -reslice-identity -push A  -lstat > $TMPDIR/allthick.txt

  # PMTAU Anterior and Posterior ROI
  pmtau=$(dirname $thickmp)/template_avg_density_cutoff_mild_Tau_tangles_to_t1.nii.gz
  pmfreq=$(dirname $thickmp)/template_avg_density_Tau_tangles_to_t1.nii.gz
  apmask=$(dirname $thickmp)/ap.nii.gz
  # PMTAU Anterior and Posterior ROI template space
  pmtautemp=$TDIR/template_avg_density_cutoff_mild_Tau_tangles_to_ADNINormal.nii.gz
  pmfreqtemp=$TDIR/template_avg_density_Tau_tangles_to_ADNINormal.nii.gz
  apmasktemp=$TDIR/ap.nii.gz
  # Thresholded PMTAU mask
  PMTAUTHRESH=0.2
  PMFREQTHRESH=0.1
  c3d $apmask -dup $pmtau -interp NN -reslice-identity -thresh $PMTAUTHRESH 1 1 0 -times \
    -dup $MASKCOMM -as APMASKED -dup $thickmp -interp NN -reslice-identity -push APMASKED  -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauthick.txt
  c3d $apmasktemp -dup $pmtautemp -interp NN -reslice-identity -thresh $PMTAUTHRESH 1 1 0 -times \
    -dup $TEMPMASKCOMM -as APMASKED -dup $jacobian -interp NN -reslice-identity -push APMASKED  -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtaujac.txt
  # Weighted PMTAU thickness
  c3d $apmask -dup $pmfreq -interp NN -reslice-identity -as PMTAU -thresh $PMTAUTHRESH 1 1 0 -times \
    -dup $MASKCOMM -as APMASKED $thickmp -interp NN -reslice-identity -push PMTAU -times -push APMASKED -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauweightedthick.txt
  c3d $apmasktemp -dup $pmfreqtemp -interp NN -reslice-identity -as PMTAU -thresh $PMTAUTHRESH 1 1 0 -times \
    -dup $TEMPMASKCOMM -as APMASKED $jacobian -interp NN -reslice-identity -push PMTAU -times -push APMASKED -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauweightedjac.txt
  
  list=$(echo 1 2 4 3 7 8 10 11 12 13 14)
  VOLS=""

  CEREBTAU=$(cat $TMPDIR/stattaump.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
  CEREBAMY=$(cat $TMPDIR/statamymp.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')

  for i in $list; do
    THISVOL=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
    THISNSLICE=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
    THISTAU=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    VOLS="$VOLS\t $THISVOL\t $THISNSLICE\t$(echo $THISTAU/${CEREBTAU} | bc -l )\t$(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  #remove leading tab
  VOLS=$(  echo -e "$VOLS" | sed -e "s/^\t//g")
  
  # Add CA1/2/3
  if [ "$atype" == "NOPHG" ] || [ "$atype" == "PHG" ]; then
    # CA
    c3d $in -replace 2 1 4 1 -as A $taupet -interp NN -reslice-identity -push A -lstat > $TMPDIR/stattau.txt
    c3d $in -replace 2 1 4 1 -as A $amypet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statamy.txt

    for i in 1; do
      THISVOL=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
      THISNSLICE=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
      THISTAU=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/statamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      VOLS="$VOLS\t $THISVOL\t  $THISNSLICE\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    done
    # HIPP
    c3d $in -replace 2 1 3 1 4 1 -as A $taupet -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathipptau.txt
    c3d $in -replace 2 1 3 1 4 1 -as A $amypet -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippamy.txt
    for i in 1; do
      THISVOL=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
      THISNSLICE=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
      THISTAU=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/stathippamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      VOLS="$VOLS\t $THISVOL\t  $THISNSLICE\t  $(echo $THISTAU/${CEREBTAU} | bc -l )\t  $(echo $THISAMY/${CEREBAMY} | bc -l )"
    done
    # EXTHIPPO
    c3d $in -replace 1 2 -replace 10 1 11 1 12 1 -as A $taupet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthipptau.txt
    c3d $in -replace 1 2 -replace 10 1 11 1 12 1 -as A $amypet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippamy.txt
    for i in 1; do
      THISVOL=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
      THISNSLICE=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
      THISTAU=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/statexthippamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      VOLS="$VOLS\t $THISVOL\t  $THISNSLICE\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    done
    # EXTHIPPO NO BA36
    c3d $in -replace 1 2 -replace 10 1 11 1 -as A $taupet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36tau.txt
    c3d $in -replace 1 2 -replace 10 1 11 1 -as A $amypet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36amy.txt
    for i in 1; do
      THISVOL=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
      THISNSLICE=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
      THISTAU=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/statexthippno36amy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      VOLS="$VOLS\t $THISVOL\t  $THISNSLICE\t  $(echo $THISTAU/${CEREBTAU} | bc -l )\t  $(echo $THISAMY/${CEREBAMY} | bc -l )"
    done
    # MTL NO BA36
    c3d $in -replace 2 1 3 1 4 1 10 1 11 1 -as A $taupet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36tau.txt
    c3d $in -replace 2 1 3 1 4 1 10 1 11 1 -as A $amypet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36amy.txt
    for i in 1; do
      THISVOL=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
      THISNSLICE=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
      THISTAU=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/statmtlno36amy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      VOLS="$VOLS\t $THISVOL\t  $THISNSLICE\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    done

  fi

  if [ "${side}" == "right" ]; then

    # BOTH HIPP
    c3d $inboth -replace 2 1 3 1 4 1 -as A $taupet -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippbothtau.txt
    c3d $inboth -replace 2 1 3 1 4 1 -as A $amypet -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippbothamy.txt
    THISTAU=$(cat $TMPDIR/stathippbothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/stathippbothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    VOLS="$VOLS\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"

    # BOTH EXTHIPPO NO BA36
    c3d $inboth -replace 1 2 -replace 10 1 11 1 -as A $taupet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36bothtau.txt
    c3d $inboth -replace 1 2 -replace 10 1 11 1 -as A $amypet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36bothamy.txt
    THISTAU=$(cat $TMPDIR/statexthippno36bothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statexthippno36bothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    VOLS="$VOLS\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"

    # BOTH MTL NO BA36
    c3d $inboth -replace 2 1 3 1 4 1 10 1 11 1 -as A $taupet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36bothtau.txt
    c3d $inboth -replace 2 1 3 1 4 1 10 1 11 1 -as A $amypet -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36bothamy.txt
    THISTAU=$(cat $TMPDIR/statmtlno36bothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statmtlno36bothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    VOLS="$VOLS\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"

    # T1 ROIs
    # Cerebellum
    THISTAU=$(cat $TMPDIR/stattaump.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamymp.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    VOLS="$VOLS\t $THISTAU\t $THISAMY"
    # Occipital lobe
    THISTAU=$(cat $TMPDIR/stattauocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamyocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    VOLS="$VOLS\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    # Posterior cingulate
    THISTAU=$(cat $TMPDIR/stattaupc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamypc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    VOLS="$VOLS\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    # Various ROIs inf temp, mid temp, sup temp, sup pariet, calc cortex
    for i in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; do
      THISTAU=$(cat $TMPDIR/varioustaurois.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/variousamyrois.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      VOLS="$VOLS\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    done
    for i in $(cat $SDROOT/wholebrainlabels_itksnaplabelfile.txt | grep -v '#' | sed -n '9,$p' | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' | awk '{print $1}' ); do
      THISTAU=$(cat $TMPDIR/alltau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/allamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISTHICK=$(cat $TMPDIR/allthick.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      VOLS="$VOLS\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )\t $THISTHICK"
    done

    # PMTAU thresholded thickness ANT and POST
    ANT=1
    POST=2
    for i in $ANT $POST; do
      THISTHICK=$(cat $TMPDIR/pmtauthick.txt | grep "^${i}," | cut -f 2 -d "," ) 
      VOLS="$VOLS\t 0$THISTHICK"
      THISTHICK=$(cat $TMPDIR/pmtauweightedthick.txt | grep "^${i}," | cut -f 2 -d "," ) 
      VOLS="$VOLS\t 0$THISTHICK"
      THISJAC=$(cat $TMPDIR/pmtaujac.txt | grep "^${i}," | cut -f 2 -d "," ) 
      VOLS="$VOLS\t $THISJAC"
      THISJAC=$(cat $TMPDIR/pmtauweightedjac.txt | grep "^${i}," | cut -f 2 -d "," ) 
      VOLS="$VOLS\t $THISJAC"
   done
  
  fi

  echo -e "$VOLS"
}

function create_tsv_header()
{
  HEADER="RID\tID\tICV\tSlice_Thickness"
  list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
  for side in left right; do
    for sf in $list; do
      HEADER="${HEADER}\t${side}_${sf}_vol\t${side}_${sf}_ns\t${side}_${sf}_tau\t${side}_${sf}_amy"
    done
  done

  HEADER="$HEADER\tHIPPboth_tau\tHIPPboth_amy\tEXTHIPPno36both_tau\tEXTHIPPno36both_amy\tMTLno36both_tau\tMTLno36both_amy\tcereb_tau\tcereb_amy\tocc_tau\tocc_amy\tpostcing_tau\tpostcing_amy\tinftemp_tau_R\tinftemp_amy_R\tinftemp_tau_L\tinftemp_amy_L\tmidtemp_tau_R\tmidtemp_amy_R\tmidtemp_tau_L\tmidtemp_amy_L\tsuptemp_tau_R\tsuptemp_amy_R\tsuptemp_tau_L\tsuptemp_amy_L\tsuppariet_tau_R\tsuppariet_amy_R\tsuppariet_tau_L\tsuppariet_amy_L\tcalc_tau_R\tcalc_amy_R\tcalc_tau_L\tcalc_amy_L\tangular_tau_R\tangular_amy_R\tangular_tau_L\tangular_amy_L\tsupfront_tau_R\tsupfront_amy_R\tsupfront_tau_L\tsupfront_amy_L"
  
  for roi in $(cat $SDROOT/wholebrainlabels_itksnaplabelfile.txt | grep -v '#' | sed -n '9,$p' | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
    HEADER="$HEADER\t${roi}_tau\t${roi}_amy\t${roi}_thickness"
  done

  echo -e "${HEADER}\t$(cat $PETFILE | sed -n "1p")" > stats_lr_cleanup_corr_nogray.tsv
}
function collate_new_data ()
{
  for fn in $(ls cleanup/stats/*whole.txt | cut -f 3 -d "/"); do

    id=$(cat cleanup/stats/$fn | head -n 1 | awk -F ' ' '{print $1}')
    RID=$(echo $id | cut -f 3 -d "_")
    tp=$(echo $fn | cut -f 7 -d "_")

    ICV=$(cat $SDROOT/${id}/$tp/${SFSEG}/final/${id}_icv.txt | awk '{print $2}')
    ICV=$(printf %10.2f $ICV)

    newline="$RID\t$id\t0$ICV"

    cat cleanup/stats/$fn | sed -e "s/^$id/$newline/g" | tee -a stats_lr_cleanup_corr_nogray.tsv

  done
}



TMPDIR=$(mktemp -d)
export TMPDIR
# mkdir -p cleanup/dump
# mkdir -p cleanup/png
# mkdir -p cleanup/stats

id=$1  ##genstats
wholebrainseg=$2 ##genstats
thickness=$3 ##genstats
t1tau=$4 ##genstats and mrionly
t2tau=$5 ##genstats and mrionly
t1amy=$6 ##genstats and mrionly
t2amy=$7 ##genstats and mrionly
tse=$8  ##cleanup
t1trim=$9  ##mrionly
t2segleft=$10  ##cleanup
mri_only_mode=$11   #mrionly

statline="$id"

atlastype=$(getatlas $t2segleft) 

for side in left right; do
  echo "doing cleanup prc for $side"
  if [ $side == "right" ] ; then
    seg=$(echo $seg | sed "s/left/$side/") 
  else 
    seg=$t2segleft
  fi

  if [ ! -f cleanup/${id}_${tp}_seg_${side}.nii.gz ]; then
      cleanup_prc $seg cleanup/${id}_${tp}_seg_${side}.nii.gz $atlastype
  fi
done

echo "making seg_both"
if [ ! -f cleanup/${id}_${tp}_seg_both.nii.gz ]; then
  c3d $tse -as A cleanup/${id}_${tp}_seg_left.nii.gz -interp NN -reslice-identity \
      -push A cleanup/${id}_${tp}_seg_right.nii.gz -interp NN -reslice-identity -add \
      -o cleanup/${id}_${tp}_seg_both.nii.gz
fi

for side in left right; do
  if [ "$mri_only_mode" == true ] ; then 
    echo "making fake t1"
    c3d $t1trim -scale 0 -shift 1 -o $TMPDIR/faket1.nii.gz
    t1tau=$TMPDIR/faket1.nii.gz
    t1amy=$TMPDIR/faket1.nii.gz

    echo "making fake t2 for $side"
    c3d cleanup/${id}_${tp}_seg_${side}.nii.gz -scale 0 -shift 1 $TMPDIR/faket2.nii.gz
    t2tau=$TMPDIR/faket2.nii.gz
    t2amy=$TMPDIR/faket2.nii.gz
  fi

  if [ "$side" == "left" ]; then
    thick=$(c3d cleanup/${id}_${tp}_seg_left.nii.gz -info-full | grep Spacing | sed -e "s/[a-zA-Z:,]//g" -e "s/\]//" -e "s/\[//" | awk '{print $3}')
    statline="$statline\t$thick"
  fi

  echo "call genstats"   
  genstats cleanup/${id}_${tp}_seg_${side}.nii.gz \
  $wholebrainseg $t2tau $t1tau $t2amy $t1amy $atlastype \
  cleanup/${id}_${tp}_seg_both.nii.gz $thickness

# statline="${statline}\t$(genstats cleanup/${id}_${tp}_seg_${side}.nii.gz \
#   $wholebrainseg $t2tau $t1tau $t2amy $t1amy $atlastype \
#   cleanup/${id}_${tp}_seg_both.nii.gz $thickness)"
done

# echo -e "$statline\t${MRIDATE}\t${VISCODE}\t${VISCODE2}\t${PHASE}"  >> cleanup/stats/stats_${tp}_${id}_whole.txt


#create_tsv_header
#collate_new_data