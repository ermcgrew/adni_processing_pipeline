#!/usr/bin/bash

raw_dicom_dir="/project/wolk/PUBLIC/dicom"

id=$1
scandate=$2
t1uid=$3
echo "this is the nifti_files.sh script" 
t1dicoms=($(find ${raw_dicom_dir}/${id}/*/${scandate}*/*/*I${t1uid}.dcm))

if [[ ! -f ${t1dicoms[0]} ]] ; then 
    # echo no dicom file, skip the rest of this iteration
else
    dcm=$(c3d -dicom-series-list ${t1dicoms[0]} | sed -n '2,$p' | sed -e "s/\t/,/g")
    ser=$(echo $dcm | awk -F "," '{print $1}') #series number
    descr=$(echo $dcm | awk -F "," '{print $4}') #series Description
    t1_nifti_dir=$(dirname ${t1dicoms[0]} | sed 's/dicom/nifti/g')
    t1_nifti_file=$(echo $t1_nifti_dir/$( echo ${scandate}_ser$(printf %02d $ser)_${descr}.nii.gz | sed -e 's/ /_/g' | sed -e "s/\//_/g" ))

    if [[ ! -f $t1_nifti_file ]] ; then
        echo do dicom to nifti conversion
        echo add $t1_nifti_file fileloc to csv
    else
        echo this file already converted
    fi

fi




# function ReFormateDate()
# {
#   indate=$1

#   if [[ $indate == "" || $indate == " " ]]; then
#     outdate=$indate
#   else
#     DD=$(date -d "$indate" '+%d')
#     MM=$(date -d "$indate" '+%m')
#     YYYY=$(date -d "$indate" '+%Y')
#     outdate="${YYYY}-${MM}-${DD}"
#   fi

#   echo $outdate
# }


# filetoread="/project/wolk/ADNI2018/scripts/pipeline_test_data/mrilist_with_uids_smalltest.csv"

# cat $filetoread | sed -n '2,$p' |  grep -v ADNI1 | while read line; do
#     # echo $line
#     rid=$(echo $line | cut -f 1 -d ",")
#     id=$(echo $line | cut -f 3 -d ",")
#     scandate=$(echo $line | cut -f 2 -d ",")
#     scandate=$(ReFormateDate $scandate)
#     t1uid=$(echo $line | cut -f 5 -d ",")

#     echo $id,$scandate
#     # echo $t1uid

#     t1dicoms=($(find ${raw_dicom_dir}/${id}/*/${scandate}*/*/*I${t1uid}.dcm))

#     if [[ ! -f ${t1dicoms[0]} ]] ; then 
#         echo no dicom file, skip the rest of this iteration
#     else
#         dcm=$(c3d -dicom-series-list ${t1dicoms[0]} | sed -n '2,$p' | sed -e "s/\t/,/g")
#         ser=$(echo $dcm | awk -F "," '{print $1}') #series number
#         descr=$(echo $dcm | awk -F "," '{print $4}') #series Description
#         t1_nifti_dir=$(dirname ${t1dicoms[0]} | sed 's/dicom/nifti/g')
#         t1_nifti_file=$(echo $t1_nifti_dir/$( echo ${scandate}_ser$(printf %02d $ser)_${descr}.nii.gz | sed -e 's/ /_/g' | sed -e "s/\//_/g" ))

#         if [[ ! -f $t1_nifti_file ]] ; then
#             echo do dicom to nifti conversion
#             echo add fileloc to csv
#         else
#             echo this file already converted
#         fi
#     fi

# done