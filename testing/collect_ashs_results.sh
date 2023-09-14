#!/usr/bin/bash

result_file_stats="ashst1_randomness_test_stats.csv"
result_file_gdsc="ashst1_randomness_test_gdsc.csv"
touch $result_file_stats
touch $result_file_gdsc
echo "ID,DATE,ROOT,SIDE,MEANDICE" >> $result_file_gdsc

basedir="/project/wolk/ADNI2018/scripts/pipeline_test_data"
dataset="/project/wolk/ADNI2018/dataset"

dir_prefix_long="necktrim_trimtestants_ashsroot_lxie_"
dir_prefix_paul="necktrim_trimtestants_ashsroot_pauly_"

for root in $dir_prefix_long $dir_prefix_paul ; do 
    for i in {1..5} ; do 
        cat ${basedir}/${root}$i/2023_09_*/ASHS_T1MTTHK_pipeline_test_data.csv | while read line ; do
            # echo $line
            id=$( echo $line | cut -d "," -f 2 )
            date=$( echo $line | cut -d "," -f 3)
            if [[ $id == "ID" && $i == 1 && $root == "necktrim_trimtestants_ashsroot_lxie_" ]] ; then
                echo ${root}$i,$line >> $result_file_stats 
                # echo ${root}$i,$line
            elif [[ $id == "ID" ]] ; then   
                continue
            else
                # echo $id, $date
                echo ${root}$i,$line >> $result_file_stats
                for side in left right ; do
                    test_seg=$basedir/${root}${i}/$id/$date/ASHST1/final/${id}_${side}_lfseg_corr_nogray.nii.gz
                    originalseg=$dataset/$id/$date/ASHST1/final/${id}_${side}_lfseg_corr_nogray.nii.gz
                    # echo c3d $originalseg $test_seg -label-overlap
                    # c3d $test_seg $originalseg -interp NN -reslice-identity $test_seg -label-overlap
                    meandice=$( c3d $test_seg $originalseg -interp NN -reslice-identity $test_seg -label-overlap | grep -A2 "All" | awk '{print $3}' | tail -n 1)
                    echo "$id,$date,${root}${i},$side,$meandice" >> $result_file_gdsc
                done
            fi
        done
    done
done