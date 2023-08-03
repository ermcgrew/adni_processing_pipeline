#!/usr/bin/bash

##variables to import:
# id=$1
# mridate=$2  
#stats_output_dir=$3
#seg=$4
#THICKCSV=$5
#SUBJASHSICVDIR=$6

# seg = ASHST1/final/${id}_${side}_lfseg_heur.nii.gz = self.t1ashs_seg_left
# THICKCSV = ASHST1_MTLCORTEX_MSTTHK/${id}_${date}_${side}_thickness.csv  = self.t1mtthk_left
# SUBJASHSICVDIR = ASHSICV/final/${id}_left_corr_nogray_volumes.txt
##TODO: stats icv made from t2/final/_icv.txt, not icv/final/_icv.txt



################ICV VOL#############
SUBJASHSICVDIR=/project/wolk/ADNI2018/dataset/067_S_6117/2021-08-04/ASHSICV/final/067_S_6117_left_corr_nogray_volumes.txt
ICV=$(cat $SUBJASHSICVDIR | cut -d " " -f 5)


################T1 ASHS: Volumes#############
ASHST13TLABELNUMS=(1     2      10  11   12   13) #AHippo PHippo ERC BA35 BA36 PHC
for side in left right; do
    seg=/project/wolk/ADNI2018/scripts/pipeline_test_data/114_S_6917/2021-04-16/ASHST1/final/114_S_6917_${side}_lfseg_heur.nii.gz
    STATS=rawvols_ASHST1_3T.txt
    c3d $seg -dup -lstat > $STATS
    for i in "${ASHST13TLABELNUMS[@]}" ; do
        VOL="$VOL,$(cat $STATS | awk -v id=$i '$1 == id {print $7}')" #get values for labels we use 
    done
done
VOL="${VOL:1}" #removes leading ,
number_of_labels=${#ASHST13TLABELNUMS[*]} #length of array// number of labels
for ((i=1;i<=$number_of_labels;i++)); do
    LMEAN=$(echo $VOL | cut -d, -f $i)  #grab left volume
    RMEAN=$(echo $VOL | cut -d, -f $((i+number_of_labels))) # grab right volume
    # echo "in for loop this is lmea: $LMEAM" 
    # echo "this is rmea: $RMEAN"
    if [[ $LMEAN != "" && $RMEAN != "" ]]; then    #if both values
        MMEAN=$(echo "scale=10;($LMEAN+$RMEAN)/2" | bc -l)  #get mean value
    else
        MMEAN=""
    fi
    VOL="$VOL,$MMEAN"
done
# echo $VOL


################T1 ASHS: Thickness#############
THK=""
for side in left right; do
THKCSV=/project/wolk/ADNI2018/dataset/067_S_6117/2021-08-04/ASHST1_MTLCORTEX_MSTTHK/067_S_6117_2021-08-04_${side}_thickness.csv
if [[ -f $THKCSV ]]; then
    THKTMP=$(cat $THKCSV | grep MultiTemp | cut -d , -f 5-14)
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
# echo $THK

################T1 ASHS: Fit Quality of Thickness#############
THKFITQUALITY=""
for side in left right; do
THKCSV=/project/wolk/ADNI2018/dataset/067_S_6117/2021-08-04/ASHST1_MTLCORTEX_MSTTHK/067_S_6117_2021-08-04_${side}_thickness.csv
if [[ -f $THKCSV ]]; then
    THKFITQUALITYTMP=$(cat $THKCSV | grep MultiTemp | cut -d , -f 15-20)
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
# echo $THKFITQUALITY


echo "$ICV,$VOL,$THK,$THKFITQUALITY"

# output all values
#echo "$ICV,$VOL,$THK,$THKFITQUALITY" >>  ${stats_output_dir}/stats_mri_{mridate}_{id}_mrionly.txt

#
# $ROW,$ICV,$RATERS,$QCINFO,$T1VOL,$THK3TT1,$THKFITQUALITY,$blscandate,$date_diff,$AnalysisType,$DEMOGROW,-1
##TODO: raters& qc info ; baseline scan info; demographic info; Row--info from where?
