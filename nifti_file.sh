#!/usr/bin/bash

raw_dicom_dir="/project/wolk/PUBLIC/dicom"

id=$1
scandate=$2
t1uid=$3
###works the same for t2?
t1dicoms=($(find ${raw_dicom_dir}/${id}/*/${scandate}*/*/*I${t1uid}.dcm))

if [[ ! -f ${t1dicoms[0]} ]] ; then 
    status="no dicom file"
else
    dcm=$(c3d -dicom-series-list ${t1dicoms[0]} | sed -n '2,$p' | sed -e "s/\t/,/g")
    series_number=$(echo $dcm | awk -F "," '{print $1}') #series number
    series_descript=$(echo $dcm | awk -F "," '{print $4}') #series description
    series_id=$(echo $dcm | awk -F "," '{print $NF}') #series ID
    t1_nifti_dir=$(dirname ${t1dicoms[0]} | sed 's/dicom/nifti/g')
    t1_nifti_file=$(echo $t1_nifti_dir/$( echo ${scandate}_ser$(printf %02d $series_number)_${series_descript}.nii.gz | sed -e 's/ /_/g' | sed -e "s/\//_/g" ))

    if [[ ! -f $t1_nifti_file ]] ; then
        # mkdir -p $t1_nifti_dir
        # c3d -dicom-series-read "${t1dicoms[0]}" "${series_id}" \
            -o $t1_nifti_file
        purple='this is a placeholder'
        if [[ -f $t1_nifti_file ]] ; then
            status="conversion to nifti sucessful"
        else
            status="conversion to nifti failed"
        fi
    else
        status="nifti file already exists"
    fi

fi

echo $status
echo $t1_nifti_file