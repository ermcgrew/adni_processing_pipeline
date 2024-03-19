#!/usr/bin/bash

# Usage:
# ./pet_stats.sh id mridate taudate amydate  
# wholebrainseg wbsegtoants wblabelfile
# icv.txt 
# cleanup/seg_left cleanup/seg_right cleanup/seg_both
# t1tau t1tausuvr t1tausuvrpvc t2taureg t1amyreg t2amyreg 
# stats_output_file 
# ASHST1dir/final/${id}  


export DOERODE=true
TMPDIR=$(mktemp -d)
export TMPDIR

id=$1  
mridate=$2
taudate=$3
amydate=$4

wholebrainseg=$5
wbsegtoants=$6
wblabelfile=$7

icvfile=$8

cleanup_left=$9
cleanup_right=${10}
cleanup_both=${11}

t1tau=${12}
t1tausuvr=${13}
t1tausuvrpvc=${14}
t2tau=${15} 
t1amy=${16} 
t2amy=${17} 

stats_output_file=${18}

t1_ashs_seg_prefix=${19}


#ID, ICV vol and thickness to stat variable
RID=$(echo $id | cut -f 3 -d "_")
ICV=$( printf %10.2f $(cat $icvfile | awk '{print $5}'))
thick=$(c3d $cleanup_left -info-full | grep Spacing | \
  sed -e "s/[a-zA-Z:,]//g" -e "s/\]//" -e "s/\[//" | awk '{print $3}')
statline="$RID,$id,$mridate,$amydate,$taudate,$ICV,$thick"
# echo $statline

#do stats for each hemisphere:
for side in left right; do
  if [ "$side" == "left" ] ; then
    cleanup_seg=$cleanup_left
  elif [ "$side" == "right" ] ; then
    cleanup_seg=$cleanup_right
  fi
  
  ### Get cerebellar reference region to compare radiotracer uptake to
  ### wholebrain seg + t1-pet reg
  wbdir=$( dirname $wholebrainseg )
  inf_cereb_mask="${wbdir}/inferior_cerebellum.nii.gz"
  CEREBTAU=$(c3d $wholebrainseg $inf_cereb_mask -times -as SEG -thresh 38 38 1 0 -erode 1 2x2x2vox -popas A \
    -push SEG -thresh 39 39 1 0 -erode 1 2x2x2vox -popas B \
    -push SEG -thresh 71 71 1 0 -erode 1 2x2x2vox -popas C \
    -push SEG -thresh 72 72 1 0 -erode 1 2x2x2vox -popas D \
    -push SEG -thresh 73 73 1 0 -erode 1 2x2x2vox -popas E \
    -push A -push B -add -push C -add -push D -add -push E -add -as CEREB \
    $t1tau -interp NN -reslice-identity -push CEREB  -lstat | \
    sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
  
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
  CEREBAMY=$(cat $TMPDIR/statamymp.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')



  ###ASHST2 regions: tau and amy measures 
  # cleanupt2 + t2-pet reg
  c3d $cleanup_seg $t2tau -interp NN -reslice-identity $cleanup_seg -lstat > $TMPDIR/stattau.txt
  c3d $cleanup_seg $t2amy -interp NN -reslice-identity $cleanup_seg -lstat > $TMPDIR/statamy.txt
  #list is label numbers in stattau.txt file: CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus 
  list=$(echo 1 2 4 3 7 8 10 11 12 13 14)
  for i in $list; do
    THISTAU=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"  
  done


  # Combine CA regions (CA1 + CA2 + CA3) to get total CA values
  c3d $cleanup_seg -replace 2 1 4 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/stattau.txt
  c3d $cleanup_seg -replace 2 1 4 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statamy.txt
  for i in 1; do
    THISTAU=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  # Combine hippocampal regions to get total HIPP values 
  c3d $cleanup_seg -replace 2 1 3 1 4 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathipptau.txt
  c3d $cleanup_seg -replace 2 1 3 1 4 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippamy.txt
  for i in 1; do
    THISTAU=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/stathippamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  # Combine EXTHIPPO regions to get total EXTHIPPO values 
  c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 12 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthipptau.txt
  c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 12 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippamy.txt
  for i in 1; do
    THISTAU=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statexthippamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  # Combine EXTHIPPO NO BA36 regions to get total EXTHIPPO NO BA36 values 
  c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36tau.txt
  c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36amy.txt
  for i in 1; do
    THISTAU=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statexthippno36amy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"
  done

  # Combine MTL NO BA36 regions to get total MTL NO BA36 values 
  c3d $cleanup_seg -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36tau.txt
  c3d $cleanup_seg -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36amy.txt
  for i in 1; do
    THISTAU=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statmtlno36amy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"
  done


  if [ "${side}" == "right" ]; then
    ####tau & amy values for combined hemispheres MTL regions (from T2 seg)
    # BOTH HIPP
    c3d $cleanup_both -replace 2 1 3 1 4 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippbothtau.txt
    c3d $cleanup_both -replace 2 1 3 1 4 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippbothamy.txt
    THISTAU=$(cat $TMPDIR/stathippbothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/stathippbothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"

    # BOTH EXTHIPPO NO BA36
    c3d $cleanup_both -replace 1 2 -replace 10 1 11 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36bothtau.txt
    c3d $cleanup_both -replace 1 2 -replace 10 1 11 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36bothamy.txt
    THISTAU=$(cat $TMPDIR/statexthippno36bothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statexthippno36bothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"

    # BOTH MTL NO BA36
    c3d $cleanup_both -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2tau -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36bothtau.txt
    c3d $cleanup_both -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2amy -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36bothamy.txt
    THISTAU=$(cat $TMPDIR/statmtlno36bothtau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statmtlno36bothamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline,$(echo $THISTAU/${CEREBTAU} | bc -l ),$(echo $THISAMY/${CEREBAMY} | bc -l )"


    ####tau & amy values for ROIs from T1 whole brain seg
    # Add Cerebellum values used above
    statline="$statline,$CEREBTAU,$CEREBAMY"

    # Occipital lobe ROIs
    c3d $wbsegtoants -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000\
    -thresh 1000 1000 1 0 -as A $t1tausuvr -interp NN -reslice-identity -push A  -lstat > $TMPDIR/stattauocc.txt
    c3d $wbsegtoants -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000\
    -thresh 1000 1000 1 0 -as A $t1tausuvrpvc -interp NN -reslice-identity -push A  -lstat > $TMPDIR/stattaupvcocc.txt
    c3d $wbsegtoants -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000 \
    -thresh 1000 1000 1 0 -as A $t1amy -interp NN -reslice-identity -push A  -lstat > $TMPDIR/statamyocc.txt
    THISTAU=$(cat $TMPDIR/stattauocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISTAUPVC=$(cat $TMPDIR/stattaupvcocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamyocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline,$THISTAU,$THISTAUPVC,$(echo $THISAMY/${CEREBAMY} | bc -l )"
        
    # Posterior cingulate ROIs
    c3d $wbsegtoants -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $t1tausuvr -interp NN \
    -reslice-identity -push A  -lstat > $TMPDIR/stattaupc.txt
    c3d $wbsegtoants -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $t1tausuvrpvc -interp NN \
    -reslice-identity -push A  -lstat > $TMPDIR/stattaupvcpc.txt
    c3d $wbsegtoants -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $t1amy -interp NN \
    -reslice-identity -push A  -lstat > $TMPDIR/statamypc.txt
    THISTAU=$(cat $TMPDIR/stattaupc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISTAUPVC=$(cat $TMPDIR/stattaupvcpc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    THISAMY=$(cat $TMPDIR/statamypc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline,$THISTAU,$THISTAUPVC,$(echo $THISAMY/${CEREBAMY} | bc -l )"
  
    # Other ROIs suitable for looking at subtypes: 
    # inf temporal gyrus (132 133) middle temporal (154 right 155 left) superior temporal 200 201 \
    # superior parietal 198 199 calcarine 108 109 angular gyrus 106 107 190 191 superior frontal
    c3d $wbsegtoants -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; \
    do echo "-push A -thresh $roi $roi $roi 0" ; done) \
      -accum -add -endaccum -as SUM  $t1tausuvr -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/varioustaurois.txt
    c3d $wbsegtoants -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; \
    do echo "-push A -thresh $roi $roi $roi 0" ; done) \
      -accum -add -endaccum -as SUM  $t1tausuvrpvc -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/varioustauroispvc.txt
    c3d $wbsegtoants -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; \
    do echo "-push A -thresh $roi $roi $roi 0" ; done) \
      -accum -add -endaccum -as SUM  $t1amy -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/variousamyrois.txt
    for i in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; do
      THISTAU=$(cat $TMPDIR/varioustaurois.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISTAUPVC=$(cat $TMPDIR/varioustauroispvc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/variousamyrois.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      statline="$statline,$THISTAU,$THISTAUPVC,$(echo $THISAMY/${CEREBAMY} | bc -l )"
    done


    #### All ROIs tau, taupvc, amy
    c3d $wbsegtoants -as A $t1tausuvr -interp NN -reslice-identity -push A  -lstat > $TMPDIR/alltau.txt
    c3d $wbsegtoants -as A $t1tausuvrpvc -interp NN -reslice-identity -push A  -lstat > $TMPDIR/alltaupvc.txt
    c3d $wbsegtoants -as A $t1amy -interp NN -reslice-identity -push A  -lstat > $TMPDIR/allamy.txt

    for i in $(cat $wblabelfile | grep -v '#' | sed -n '9,$p' | \
    grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF|Thalamus|Forebrain' | awk '{print $1}' ); do
      THISTAU=$(cat $TMPDIR/alltau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISTAUPVC=$(cat $TMPDIR/alltaupvc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      THISAMY=$(cat $TMPDIR/allamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      statline="$statline,$THISTAU,$THISTAUPVC,$(echo $THISAMY/${CEREBAMY} | bc -l )"
    done

    ### comp SUVR 
    # Left_MFG_middle_frontal_gyrus,Right_MFG_middle_frontal_gyrus,Left_ACgG_anterior_cingulate_gyrus,
    # Right_ACgG_anterior_cingulate_gyrus,Left_PCgG_posterior_cingulate_gyrus,Right_PCgG_posterior_cingulate_gyrus,
    # Left_AnG_angular_gyrus,Right_AnG_angular_gyrus,Left_PCu_precuneus,Right_PCu_precuneus,
    # Left_SMG_supramarginal_gyrus,Right_SMG_supramarginal_gyrus,Left_MTG_middle_temporal_gyrus,
    # Right_MTG_middle_temporal_gyrus,Left_ITG_inferior_temporal_gyrus,Right_ITG_inferior_temporal_gyrus
    sum=0
    for i in 142 143 100 101 166 167 106 107 168 169 194 195 154 155 132 133; do
      THISPET=$(cat $TMPDIR/allamy.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
      sum=$(echo $sum + $(echo $THISPET/${CEREBAMY} | bc -l ) | bc -l )
    done
    compsuvr="0$(echo $sum/16 | bc -l)"
    statline="$statline,$compsuvr"

  fi
done


##### Whole brain Tau measures BRAAK stages 3-6
WBTAULABELIDS=(BRAAK3 BRAAK4 BRAAK5 BRAAK6)
WBTAULABELLEFTNUMS=("32 34 171 123 135" "173 103 133 155 167" "125 201 127 163 165 205 115 169 101 195 145 169 199 153 191 141 143" "109 115 149 151 177 183")
WBTAULABELRIGHTNUMS=("31 33 170 122 134" "172 102 132 154 166" "124 200 126 162 164 204 114 168 100 194 144 168 198 152 190 140 142" "108 114 148 150 176 182")

WBTAU=""
# extract measurements
for tautype in $t1tausuvr $t1tausuvrpvc ; do 
  for side in left right; do
    for ((i=0;i<${#WBTAULABELIDS[*]}; i++)); do
      if [[ -f $wbsegtoants && -f $tautype ]]; then
        if [[ $side == "left" ]]; then
          REPRULE=$(for lab in ${WBTAULABELLEFTNUMS[i]}; do echo $lab 999; done)
        else
          REPRULE=$(for lab in ${WBTAULABELRIGHTNUMS[i]}; do echo $lab 999; done)
        fi
        WBTAU="$WBTAU,$(c3d $wbsegtoants -replace $REPRULE -thresh 999 999 1 0 -as SEG \
          $tautype -int 0 -reslice-identity \
          -push SEG -lstat | awk '{print $2}' | tail -n 1)"
      else
        WBTAU="$WBTAU,"
      fi
    done
  done
done

statline="$statline$WBTAU" ##WBTAU variable starts with comma


#### ASHST1-tau measures
ASHST13TTAULABELIDS=(AHippo PHippo ERC BA35 BA36 PHC ERCBA35 WholeHippo MTLCortex     All)
ASHST13TTAULABELNUMS=(1     2      10  11   12   13  "10 11" "1 2"      "10 11 12 13" "1 2 10 11 12 13")
TAU=""
for side in left right; do
  SEG=${t1_ashs_seg_prefix}_${side}_lfseg_heur_LW.nii.gz
  if [[ ! -f $SEG ]]; then
    SEG=${t1_ashs_seg_prefix}_${side}_lfseg_heur.nii.gz
  fi
  # extract measurements
  for ((i=0;i<${#ASHST13TTAULABELIDS[*]}; i++)); do
    REPRULE=$(for lab in ${ASHST13TTAULABELNUMS[i]}; do echo $lab 99; done)
    TAU="$TAU,$(c3d $SEG -replace $REPRULE -thresh 99 99 1 0 -as SEG \
      $t1tausuvr -int 0 -reslice-identity -push SEG -lstat | awk '{print $2}' | tail -n 1)"
  done 
done
TAU="${TAU:1}"

# compute mean
MEA=$TAU
NMEA=${#ASHST13TTAULABELIDS[*]}
for ((i=1;i<=$NMEA;i++)); do
  LMEA=$(echo $MEA | cut -d, -f $i)
  RMEA=$(echo $MEA | cut -d, -f $((i+NMEA)))
  if [[ $LMEA != "" && $RMEA != "" ]]; then
    MMEA=$(echo "scale=10;($LMEA+$RMEA)/2" | bc -l)
  else
    MMEA=""
  fi
  MEA="$MEA,$MMEA"
done

TAU=$MEA

statline="$statline,$TAU"



echo -e $statline | tee $stats_output_file
