#!/usr/bin/bash

result_file="ashst1_randomness_test.csv"
touch $result_file
basedir="/project/wolk/ADNI2018/scripts/pipeline_test_data"

dir_prefix_long="necktrim_trimtestants_ashsroot_lxie_"
dir_prefix_paul="necktrim_trimtestants_ashsroot_pauly_"

for root in $dir_prefix_long $dir_prefix_paul ; do 
    for i in {1..5} ; do 
        cat ${basedir}/${root}$i/2023_09_*/ASHS_T1MTTHK_pipeline_test_data.csv | while read line ; do
            # echo $line
            id=$( echo $line | cut -d "," -f 2 )
            date=$( echo $line | cut -d "," -f 3)
            if [[ $id == "ID" ]] ; then
                echo ${root}$i,$line >> $result_file 
            else
                # echo $id, $date
                echo ${root}$i,$line >> $result_file
            fi
        done
    done
done