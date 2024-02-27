#!/usr/bin/bash

##variables to import:
id=$1
mridate=$2  
stats_output_dir=$3
t1_ashs_seg_prefix=$4
t1_ashs_seg_suffix=$5
thickness_csv_prefix=$6
thickness_csv_suffix=$7
icv_txt=$8

################ICV VOL#############
# icv_txt=/project/wolk/ADNI2018/dataset/067_S_6117/2021-08-04/ASHSICV/final/067_S_6117_left_corr_nogray_volumes.txt
ICV=$(cat $icv_txt | cut -d " " -f 5)
# echo $ICV

################T1 ASHS: Volumes#############
ASHST13TLABELNUMS=(1     2      10  11   12   13) #AHippo PHippo ERC BA35 BA36 PHC
for side in left right; do
    t1_ashs_seg="${t1_ashs_seg_prefix}_${side}_${t1_ashs_seg_suffix}"
    # t1_ashs_seg=/project/wolk/ADNI2018/scripts/pipeline_test_data/114_S_6917/2021-04-16/ASHST1/final/114_S_6917_${side}_lfseg_heur.nii.gz
    STATS=${stats_output_dir}/rawvols_ASHST1_3T.txt
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
    # echo "in for loop this is lmea: $LMEAN" 
    # echo "this is rmea: $RMEAN"
    if [[ $LMEAN != "" && $RMEAN != "" ]]; then    #if both values
        MMEAN=$(echo "scale=10;($LMEAN+$RMEAN)/2" | bc -l)  #get mean value
    else
        MMEAN=""
    fi
    VOL="$VOL,$MMEAN"
done
# echo "volumes: $VOL"


################T1 ASHS: Thickness#############
THK=""
for side in left right; do
    thickness_csv="${thickness_csv_prefix}_${side}_${thickness_csv_suffix}"
    # thickness_csv=/project/wolk/ADNI2018/dataset/067_S_6117/2021-08-04/ASHST1_MTLCORTEX_MSTTHK/067_S_6117_2021-08-04_${side}_thickness.csv
    if [[ -f $thickness_csv ]]; then
        THKTMP=$(cat $thickness_csv | grep MultiTemp | cut -d , -f 5-14)
        len=$(echo $THKTMP | sed 's/[^,]//g'  | awk '{ print length }')
        if [[ $len -ne 9 ]]; then
            THK="$THK,,,,,,,,,,"
        else
            THK="$THK,$THKTMP"
        fi
    else
        THK="$THK,,,,,,,,,,"
    fi
done
THK="${THK:1}"
# compute mean
number_of_labels=10
for ((i=1;i<=$number_of_labels;i++)); do
    LMEAN=$(echo $THK| cut -d, -f $i)
    RMEAN=$(echo $THK | cut -d, -f $((i+number_of_labels)))
    if [[ $LMEAN != "" && $RMEAN != "" ]]; then
        MMEAN=$(echo "scale=10;($LMEAN+$RMEAN)/2" | bc -l)
    else
        MMEAN=""
    fi
    THK="$THK,$MMEAN"
done
# echo "thickness: $THK"

################T1 ASHS: Fit Quality of Thickness#############
THKFITQUALITY=""
for side in left right; do
    thickness_csv="${thickness_csv_prefix}_${side}_${thickness_csv_suffix}"
    # thickness_csv=/project/wolk/ADNI2018/dataset/067_S_6117/2021-08-04/ASHST1_MTLCORTEX_MSTTHK/067_S_6117_2021-08-04_${side}_thickness.csv
    if [[ -f $thickness_csv ]]; then
        THKFITQUALITYTMP=$(cat $thickness_csv | grep MultiTemp | cut -d , -f 15-20)
        len=$(echo $THKFITQUALITYTMP | sed 's/[^,]//g'  | awk '{ print length }')
        if [[ $len -ne 5 ]]; then
            THKFITQUALITY="$THKFITQUALITY,,,,,,"
        else
            THKFITQUALITY="$THKFITQUALITY,$THKFITQUALITYTMP"
        fi
    else
        THKFITQUALITY="$THKFITQUALITY,,,,,,"
    fi
done
THKFITQUALITY="${THKFITQUALITY:1}"
# echo "Thick fit qual: $THKFITQUALITY"

# echo "$ICV,$VOL,$THK,$THKFITQUALITY"
RID=$(echo $id | cut -f 3 -d "_")

# output all values
echo "$RID,$id,$mridate,$ICV,$VOL,$THK,$THKFITQUALITY" | tee ${stats_output_dir}/stats_mri_${mridate}_${id}_ashst1.txt
