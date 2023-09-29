#!/usr/bin/bash
# adapted from cleanup_prc_taupet_adni_unified_flexible.sh

# Usage:
# ./stats.sh id wholebrainseg corticalthickness t1taureg t2taureg t1amyreg t2amyreg \
# cleanup/seg_left cleanup/seg_right cleanup/seg_both t1trim icv.txt mode wblabelfile \ 
# pmtau_template_dir stats_output_dir mridate taudate amydate


export DOERODE=true
TMPDIR=$(mktemp -d)
export TMPDIR

id=$1  
wholebrainseg=$2 
thickness=$3 
t1tau=$4 
t2tau=$5 
t1amy=$6 
t2amy=$7 
cleanup_left=$8
cleanup_right=$9
cleanup_both=${10}
t1trim=${11}
icvfile=${12}
mode=${13}
wblabelfile=${14}
pmtau_template_dir=${15}
stats_output_dir=${16}
mridate=${17}
taudate=${18}
amydate=${19}

# for file in $@ ; do
#   # echo $file
#   if [[ ! -f $file ]] ; then
#     echo "Not a file $file"
#   fi
# done

#determine first values to be added to stats
RID=$(echo $id | cut -f 3 -d "_")
ICV=$( printf %10.2f $(cat $icvfile | awk '{print $5}'))
thick=$(c3d $cleanup_left -info-full | grep Spacing | \
  sed -e "s/[a-zA-Z:,]//g" -e "s/\]//" -e "s/\[//" | awk '{print $3}')
statline="$RID\t$id\t$mridate\t$amydate\t$taudate\t$ICV\t$thick"
# echo $statline
#do stats for each hemisphere:
for side in left right; do
  if [ "$side" == "left" ] ; then
    cleanup_seg=$cleanup_left
  elif [ "$side" == "right" ] ; then
    cleanup_seg=$cleanup_right
  fi

  if [ "$mode" == "mri" ] ; then 
    c3d $t1trim -scale 0 -shift 1 -o $TMPDIR/faket1.nii.gz
    t1tau=$TMPDIR/faket1.nii.gz
    t1amy=$TMPDIR/faket1.nii.gz

    c3d $cleanup_seg -scale 0 -shift 1 $TMPDIR/faket2.nii.gz
    t2tau=$TMPDIR/faket2.nii.gz
    t2amy=$TMPDIR/faket2.nii.gz

  fi

  echo "cleanup & t2 pet reg"
  c3d $cleanup_seg $t2tau -interp NN -reslice-identity $cleanup_seg -lstat > $TMPDIR/stattau.txt
  c3d $cleanup_seg $t2amy -interp NN -reslice-identity $cleanup_seg -lstat > $TMPDIR/statamy.txt
  
  echo "wholebrain seg and t1 pet reg"
  # Get T1 segmentation and get cerebellar GM
  c3d $wholebrainseg -as SEG -thresh 38 38 1 0 -erode 1 2x2x2vox -popas A \
    -push SEG -thresh 39 39 1 0 -erode 1 2x2x2vox -popas B \
    -push SEG -thresh 71 71 1 0 -erode 1 2x2x2vox -popas C \
    -push SEG -thresh 72 72 1 0 -erode 1 2x2x2vox -popas D \
    -push SEG -thresh 73 73 1 0 -erode 1 2x2x2vox -popas E \
    -push A -push B -add -push C -add -push D -add -push E -add -as CEREB \
    $t1tau -interp NN -reslice-identity -push CEREB  -lstat > $TMPDIR/stattaump.txt
  c3d $wholebrainseg -as SEG -thresh 38 38 1 0 -popas A \
    -push SEG -thresh 39 39 1 0 -popas B \
    -push SEG -thresh 71 71 1 0 -popas C \
    -push SEG -thresh 72 72 1 0 -popas D \
    -push SEG -thresh 73 73 1 0 -popas E \
    -push SEG -thresh 40 40 1 0 -popas F \
    -push SEG -thresh 41 41 1 0 -popas G \
    -push A -push B -add -push C -add -push D -add -push E -add -push F -add -push G -add \
    -erode 1 2x2x2vox -as CEREB \
    $t1amy -interp NN -reslice-identity -push CEREB  -lstat > $TMPDIR/statamymp.txt

  # Occipital ROIs
  c3d $wholebrainseg -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000\
  -thresh 1000 1000 1 0 -as A $t1tau -interp NN -reslice-identity -push A  -lstat > $TMPDIR/stattauocc.txt
  c3d $wholebrainseg -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000 \
  -thresh 1000 1000 1 0 -as A $t1amy -interp NN -reslice-identity -push A  -lstat > $TMPDIR/statamyocc.txt
  
  # Posterior Cingulate ROIs
  c3d $wholebrainseg -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $t1tau -interp NN \
  -reslice-identity -push A  -lstat > $TMPDIR/stattaupc.txt
  c3d $wholebrainseg -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $t1amy -interp NN \
  -reslice-identity -push A  -lstat > $TMPDIR/statamypc.txt
  
  # Other ROIs suitable for looking at subtypes: 
  # inf temporal gyrus (132 133) middle temporal (154 right 155 left) superior temporal 200 201 \
  # superior parietal 198 199 calcarine 108 109 angular gyrus 106 107 190 191 superior frontal
  c3d $wholebrainseg -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; \
  do echo "-push A -thresh $roi $roi $roi 0" ; done) \
    -accum -add -endaccum -as SUM  $t1tau -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/varioustaurois.txt
  c3d $wholebrainseg -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; \
  do echo "-push A -thresh $roi $roi $roi 0" ; done) \
    -accum -add -endaccum -as SUM  $t1amy -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/variousamyrois.txt

  # Mask with GM
  tissueseg=$(echo $thickness | sed -e 's/CorticalThickness/BrainSegmentation/g')
  jacobian=$(echo $tissueseg | sed -e 's/BrainSegmentation/SubjectToTemplateLogJacobian/g' )
  tempgmmask=$pmtau_template_dir/adninormalgmmask.nii.gz

  # All ROIs tau
  c3d $wholebrainseg -as A $t1tau -interp NN -reslice-identity -push A  -lstat > $TMPDIR/alltau.txt
  c3d $wholebrainseg -as A $t1amy -interp NN -reslice-identity -push A  -lstat > $TMPDIR/allamy.txt
  
  # All ROIs thickness
  MASKCOMM="$tissueseg -interp NN -reslice-identity -thresh 2 2 1 0 -times"
  TEMPMASKCOMM="$tempgmmask -interp NN -reslice-identity -thresh 1 1 1 0 -times"
  c3d $wholebrainseg -dup $MASKCOMM -as A $thickness -interp NN -reslice-identity -push A  -lstat > $TMPDIR/allthick.txt


  #list is label numbers in stattau.txt file: CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus 
  list=$(echo 1 2 4 3 7 8 10 11 12 13 14)
  #cerebellem reference region to compare radiotracer uptake to
  CEREBTAU=$(cat $TMPDIR/stattaump.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
  CEREBAMY=$(cat $TMPDIR/statamymp.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
  for i in $list; do
    THISVOL=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
    THISNSLICE=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
    THISTAU=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline\t $THISVOL\t $THISNSLICE\t$(echo $THISTAU/${CEREBTAU} | bc -l )\t$(echo $THISAMY/${CEREBAMY} | bc -l )"  
  done

  #remove leading tab
  # statline=$( echo -e "$statline" | sed -e "s/^\t//g")

  # CA (CA1 + CA2 + CA3)
  c3d $cleanup_seg -replace 2 1 4 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/stattau.txt
  c3d $cleanup_seg -replace 2 1 4 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statamy.txt
  for i in 1; do
    THISVOL=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
    THISNSLICE=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
    THISTAU=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline\t $THISVOL\t  $THISNSLICE\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  # HIPP
  c3d $cleanup_seg -replace 2 1 3 1 4 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathipptau.txt
  c3d $cleanup_seg -replace 2 1 3 1 4 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippamy.txt
  for i in 1; do
    THISVOL=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
    THISNSLICE=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
    THISTAU=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/stathippamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline\t $THISVOL\t  $THISNSLICE\t  $(echo $THISTAU/${CEREBTAU} | bc -l )\t  $(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  # EXTHIPPO
  c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 12 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthipptau.txt
  c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 12 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippamy.txt
  for i in 1; do
    THISVOL=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
    THISNSLICE=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
    THISTAU=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statexthippamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline\t $THISVOL\t  $THISNSLICE\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  # EXTHIPPO NO BA36
  c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36tau.txt
  c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36amy.txt
  for i in 1; do
    THISVOL=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
    THISNSLICE=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
    THISTAU=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statexthippno36amy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline\t $THISVOL\t  $THISNSLICE\t  $(echo $THISTAU/${CEREBTAU} | bc -l )\t  $(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  # MTL NO BA36
  c3d $cleanup_seg -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36tau.txt
  c3d $cleanup_seg -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36amy.txt
  for i in 1; do
    THISVOL=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
    THISNSLICE=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
    THISTAU=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statmtlno36amy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline\t $THISVOL\t  $THISNSLICE\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
  done
 
  if [ "${side}" == "right" ]; then
    # BOTH HIPP
    c3d $cleanup_both -replace 2 1 3 1 4 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippbothtau.txt
    c3d $cleanup_both -replace 2 1 3 1 4 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippbothamy.txt
    THISTAU=$(cat $TMPDIR/stathippbothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/stathippbothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"

    # BOTH EXTHIPPO NO BA36
    c3d $cleanup_both -replace 1 2 -replace 10 1 11 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36bothtau.txt
    c3d $cleanup_both -replace 1 2 -replace 10 1 11 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36bothamy.txt
    THISTAU=$(cat $TMPDIR/statexthippno36bothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statexthippno36bothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"

    # BOTH MTL NO BA36
    c3d $cleanup_both -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36bothtau.txt
    c3d $cleanup_both -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36bothamy.txt
    THISTAU=$(cat $TMPDIR/statmtlno36bothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statmtlno36bothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"

    # T1 ROIs
    # Cerebellum
    THISTAU=$(cat $TMPDIR/stattaump.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamymp.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline\t $THISTAU\t $THISAMY"
    # Occipital lobe
    THISTAU=$(cat $TMPDIR/stattauocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamyocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    # Posterior cingulate
    THISTAU=$(cat $TMPDIR/stattaupc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamypc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    
    # Various ROIs inf temp, mid temp, sup temp, sup pariet, calc cortex
    for i in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; do
      THISTAU=$(cat $TMPDIR/varioustaurois.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/variousamyrois.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      statline="$statline\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )"
    done
    for i in $(cat $wblabelfile | grep -v '#' | sed -n '9,$p' | \
    grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' | awk '{print $1}' ); do
      THISTAU=$(cat $TMPDIR/alltau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/allamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISTHICK=$(cat $TMPDIR/allthick.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      statline="$statline\t $(echo $THISTAU/${CEREBTAU} | bc -l )\t $(echo $THISAMY/${CEREBAMY} | bc -l )\t $THISTHICK"
    done

    # PMTAU Anterior and Posterior ROI
    pmtau=$(dirname $thickness)/template_avg_density_cutoff_mild_Tau_tangles_to_t1.nii.gz
    pmfreq=$(dirname $thickness)/template_avg_density_Tau_tangles_to_t1.nii.gz
    apmask=$(dirname $thickness)/ap.nii.gz
    # PMTAU Anterior and Posterior ROI template space
    pmtautemp=$pmtau_template_dir/template_avg_density_cutoff_mild_Tau_tangles_to_ADNINormal.nii.gz
    pmfreqtemp=$pmtau_template_dir/template_avg_density_Tau_tangles_to_ADNINormal.nii.gz
    apmasktemp=$pmtau_template_dir/ap.nii.gz
    # Thresholded PMTAU mask
    PMTAUTHRESH=0.2
    c3d $apmask -dup $pmtau -interp NN -reslice-identity -thresh $PMTAUTHRESH 1 1 0 -times \
      -dup $MASKCOMM -as APMASKED -dup $thickness -interp NN -reslice-identity -push APMASKED  \
      -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauthick.txt
    c3d $apmasktemp -dup $pmtautemp -interp NN -reslice-identity -thresh $PMTAUTHRESH 1 1 0 -times \
      -dup $TEMPMASKCOMM -as APMASKED -dup $jacobian -interp NN -reslice-identity -push APMASKED  \
      -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtaujac.txt
    # Weighted PMTAU thickness
    c3d $apmask -dup $pmfreq -interp NN -reslice-identity -as PMTAU -thresh $PMTAUTHRESH 1 1 0 -times \
      -dup $MASKCOMM -as APMASKED $thickness -interp NN -reslice-identity -push PMTAU -times -push APMASKED \
      -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauweightedthick.txt
    c3d $apmasktemp -dup $pmfreqtemp -interp NN -reslice-identity -as PMTAU -thresh $PMTAUTHRESH 1 1 0 -times \
      -dup $TEMPMASKCOMM -as APMASKED $jacobian -interp NN -reslice-identity -push PMTAU -times -push APMASKED \
      -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauweightedjac.txt

    # PMTAU thresholded thickness ANT and POST
    ANT=1
    POST=2
    for i in $ANT $POST; do
      THISTHICK=$(cat $TMPDIR/pmtauthick.txt | grep "^${i}," | cut -f 2 -d "," ) 
      statline="$statline\t 0$THISTHICK"
      THISTHICK=$(cat $TMPDIR/pmtauweightedthick.txt | grep "^${i}," | cut -f 2 -d "," ) 
      statline="$statline\t 0$THISTHICK"
      THISJAC=$(cat $TMPDIR/pmtaujac.txt | grep "^${i}," | cut -f 2 -d "," ) 
      statline="$statline\t $THISJAC"
      THISJAC=$(cat $TMPDIR/pmtauweightedjac.txt | grep "^${i}," | cut -f 2 -d "," ) 
      statline="$statline\t $THISJAC"
   done
  fi
done

echo $statline
if [[ $mode == "mri" ]] ; then
  echo -e $statline >> ${stats_output_dir}/stats_mri_${mridate}_${id}_structonly.txt
else
  echo -e $statline >> ${stats_output_dir}/stats_tau_${taudate}_amy_${amydate}_mri_${mridate}_${id}_whole.txt
fi 