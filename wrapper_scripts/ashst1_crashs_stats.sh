#!/usr/bin/bash


# example inputs 
# B10081264 20140212x004 /project/wolk_4/A4/bids_dataset/derivatives/ASHST1/code \
# /project/wolk_4/A4/bids_dataset/derivatives/ASHST1/sub-B10081264/ses-20140212x004/anat/ASHST1_anteriorMTL/ashs/final/B10081264_left_lfseg_heur.nii.gz \
# /project/wolk_4/A4/bids_dataset/derivatives/ASHST1/sub-B10081264/ses-20140212x004/anat/ASHST1_anteriorMTL/crashs/crashs_left/thickness/B10081264_20140212x004_left_thickness_roi_summary.csv \
# /project/wolk_4/A4/bids_dataset/derivatives/ASHST1/sub-B10081264/ses-20140212x004/anat/ASHST1_anteriorMTL/crashs/crashs_left/fitting/B10081264_20140212x004_left_fitted_dist_stat.json \
# /project/wolk_4/A4/bids_dataset/derivatives/ASHST1/sub-B10081264/ses-20140212x004/anat/ASHSICV/final/B10081264_left_multiatlas_corr_nogray_volumes.txt

## input files
id=$1
mridate=$2  
stats_output_dir=$3
left_t1_ashs_seg=$4    # ./ASHST1_anteriorMTL/ashs/final/${id}_left_lfseg_heur.nii.gz
left_thickness_roi=$5   # ./ASHST1_anteriorMTL/crashs/crashs_left/thickness/${id}_${ses}_left_thickness_roi_summary.csv
left_fitting_json=$6    # ./ASHST1_anteriorMTL/crashs/crashs_left/fitting/${id}_${ses}_left_fitted_dist_stat.json
icv_txt=$7              # ./ASHSICV/final/${id}_left_corr_nogray_volumes.txt


ASHST13TLABELNUMS=(1 2 10 11 12 13 18 20) #AHippo PHippo ERC BA35 BA36 PHC Amygdala WhiteMatter

TMPDIR=$( mktemp -d )

################ RID from ADNI ID #############
RID=$(echo $id | cut -f 3 -d "_")

################ ICV VOL #############
ICV=$(cat $icv_txt | cut -d " " -f 5)

################ T1 ASHS: Volumes #############
for side in left right; do
    if [[ $side == "left" ]] ; then 
        t1_ashs_seg=$left_t1_ashs_seg
    else 
        t1_ashs_seg=$( echo $left_t1_ashs_seg | sed 's/left/right/g' )
    fi
    # echo $t1_ashs_seg
    STATS=$TMPDIR/rawvols_ASHST1_3T.txt
    c3d $t1_ashs_seg -dup -lstat > $STATS
    for i in "${ASHST13TLABELNUMS[@]}" ; do
        VOL="$VOL,$(cat $STATS | awk -v id=$i '$1 == id {print $7}')" #get values for labels we use 
    done
done
VOL="${VOL:1}" #removes leading ,
number_of_labels=${#ASHST13TLABELNUMS[*]} #length of array// number of labels
for ((i=1;i<=$number_of_labels;i++)); do
    LMEAN=$(echo $VOL | cut -d, -f $i)  #grab left volume
    RMEAN=$(echo $VOL | cut -d, -f $((i+number_of_labels))) # grab right volume
    if [[ $LMEAN != "" && $RMEAN != "" ]]; then    #if both values
        MMEAN=$(echo "scale=10;($LMEAN+$RMEAN)/2" | bc -l)  #get mean value
    else
        MMEAN=""
    fi
    VOL="$VOL,$MMEAN"
done


################ Thickness from CRASHS #############
THK=""
for side in left right; do
    if [[ $side == "left" ]] ; then 
        csvtoread=$left_thickness_roi
    else 
        csvtoread=$( echo $left_thickness_roi | sed 's/left/right/g' )
    fi
    # echo $csvtoread
    if [[ -f $csvtoread ]] ; then 
        for i in "${ASHST13TLABELNUMS[@]}" ; do
            ### exclude 18 amygdala
            if [[ $i != 18 ]] ; then 
                THK="$THK,$( cat $csvtoread | grep "$side,$i," | awk -F',' '{print $5 }' )"
            fi
        done
    fi
done
THK="${THK:1}"


################ CRASHS QC #############
THKQC=""
for side in left right; do
    if [[ $side == "left" ]] ; then 
        csvtoread=$left_fitting_json
    else 
        csvtoread=$( echo $left_fitting_json | sed 's/left/right/g' )
    fi
    # echo $csvtoread
    if [[ -f $csvtoread ]] ; then 
        THKQC="$THKQC,$( cat $csvtoread | jq '.q95' )"
    fi
done
THKQC="${THKQC:1}"

### output all values
echo "$RID,$id,$mridate,$ICV,$VOL,$THK,$THKQC" | tee ${stats_output_dir}/stats_mri_${mridate}_${id}_ashst1_crashs.txt

rm -rf $TMPDIR


