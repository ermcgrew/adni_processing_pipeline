#!/usr/bin/bash

mridata="/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230731_processing_status/mri_processing_status.csv"
testloc="/project/wolk/ADNI2018/scripts/pipeline_test_data"
dataset="/project/wolk/ADNI2018/dataset"


cat $mridata | while read line ; do 
    id=$( echo $line | cut -d "," -f 3 )
    date=$( echo $line | cut -d "," -f 2)
    if [[ $id == "ID" || $date == "2022-11-21" || $date == "2022-10-17" || $date == "2022-06-23" || $date == "2022-07-01" ]] ; then
        continue 
    else
        echo $id, $date

        oldthick=$dataset/${id}/${date}/thickness/${id}CorticalThickness.nii.gz
        newthick=$testloc/${id}/${date}/thickness/${id}CorticalThickness.nii.gz
        output=$testloc/${id}/${date}/thickness/${id}compare_old_new.nii.gz

        c3d $oldthick $newthick -interp NN -reslice-identity -o $output
        c3d $oldthick $output -scale -1 -add -info 
    fi
done


# 114_S_6917, 2021-04-16
# Image #1: dim = [240, 190, 176];  bb = {[93.1659 -116.852 83.707], [333.166 73.1477 259.707]};  vox = [1, 1, 1];  range = [-7.36126, 8.01049];  orient = ASL

# 033_S_0734, 2018-10-10
# Image #1: dim = [240, 190, 176];  bb = {[82.1024 -127.422 72.1928], [322.102 62.5783 248.193]};  vox = [1, 1, 1];  range = [-5.86829, 6.91041];  orient = ASL

# 024_S_2239, 2019-06-03
# Image #1: dim = [240, 190, 208];  bb = {[103.5 -150.373 65.0847], [343.5 39.6271 273.085]};  vox = [1, 1, 1];  range = [-8.10754, 6.60476];  orient = ASL

# 100_S_0069, 2020-01-23
# Image #1: dim = [256, 190, 211];  bb = {[105.527 -136.74 124.821], [361.527 53.2602 335.821]};  vox = [1, 1, 1];  range = [-8.0487, 9.685];  orient = ASL

# 068_S_0127, 2020-03-12
# Image #1: dim = [230, 230, 175];  bb = {[-117.289 -126.42 -138.811], [112.711 103.58 36.1877]};  vox = [1, 1, 0.999992];  range = [-8.40908, 8.43078];  orient = Oblique, closest to RAI