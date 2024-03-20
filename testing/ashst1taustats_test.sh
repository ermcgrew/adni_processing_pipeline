#!/usr/bin/bash
t1_ashs_seg_prefix=$1
t1tausuvr=$2

#### ASHST1-tau measures
ASHST13TTAULABELIDS=(AHippo PHippo ERC BA35 BA36 PHC ERCBA35 WholeHippo MTLCortex     All)
ASHST13TTAULABELNUMS=(1     2      10  11   12   13  "10 11" "1 2"      "10 11 12 13" "1 2 10 11 12 13")

TAU=""

# t1ashs_seg_prefix= through id
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

echo $TAU