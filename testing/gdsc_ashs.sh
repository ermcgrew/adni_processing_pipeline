#!/usr/bin/bash

mridata="/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230731_processing_status/mri_processing_status.csv"
testloc="/project/wolk/ADNI2018/scripts/pipeline_test_data"
dataset="/project/wolk/ADNI2018/dataset"

resultfile=ashst1_gdsc.csv
rm $resultfile
touch $resultfile
echo "ID,DATE,ASHSROOT,SIDE,MEAN_DICE,DATASET_SEG,TEST_SEG" >> $resultfile

cat $mridata | while read line ; do 
    id=$( echo $line | cut -d "," -f 3 )
    date=$( echo $line | cut -d "," -f 2)
    echo $id, $date
    if [[ $id == "ID" || $date == "2022-06-23" || $date == "2022-07-01" || $date == "2022-11-21" || $date == "2022-10-17" || $date == "2020-03-12" ]] ; then
        continue 
    else
        for root in pauly lxie ; do
            for side in left right ; do
                test_seg=$testloc/necktrim_trimtestants_ashsroot_${root}/$id/$date/ASHST1/final/${id}_${side}_lfseg_corr_nogray.nii.gz
                originalseg=$dataset/$id/$date/ASHST1/final/${id}_${side}_lfseg_corr_nogray.nii.gz
                # echo c3d $originalseg $test_seg -label-overlap
                # c3d $test_seg $originalseg -interp NN -reslice-identity $test_seg -label-overlap
                meandice=$( c3d $test_seg $originalseg -interp NN -reslice-identity $test_seg -label-overlap | grep -A2 "All" | awk '{print $3}' | tail -n 1)
                echo "$id,$date,$root,$side,$meandice,$originalseg,$test_seg" >> $resultfile
            done
        done
    fi
done