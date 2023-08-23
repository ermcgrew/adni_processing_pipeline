#!/usr/bin/bash

mridata="/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230731_processing_status/mri_processing_status.csv"
testloc="/project/wolk/ADNI2018/scripts/pipeline_test_data"
dataset="/project/wolk/ADNI2018/dataset"

resultfile=testtrimresults.txt
touch $resultfile

echo "ID,DATE,ORIGINAL,TEST" >> $resultfile

cat $mridata | while read line ; do 
    id=$( echo $line | cut -d "," -f 3 )
    date=$( echo $line | cut -d "," -f 2)
    echo $id, $date
    if [[ $id == "ID" || $date == "2022-11-21" || $date == "2022-10-17" ]] ; then # 2022-06-23 2022-07-01
        continue 
    else
        t1=$testloc/${id}/${date}/${date}_${id}_T1w.nii.gz
        neckmask=$testloc/${id}/${date}/thickness/${id}NeckTrimMask.nii.gz
        originaltrim=$dataset/${id}/${date}/${date}_${id}_T1w_trim.nii.gz
        trimtest=$testloc/${id}/${date}/${date}_${id}_T1w_trimtest.nii.gz
    
        c3d $t1 $neckmask -times -o $trimtest
        original=$( c3d $originaltrim -info | cut -d ";" -f 4 | cut -d "," -f 2 | sed "s/]//g")
        test=$( c3d $trimtest -info | cut -d ";" -f 4 | cut -d "," -f 2 | sed "s/]//g")
        echo $id,$date,$original,$test >> $resultfile
    fi

done