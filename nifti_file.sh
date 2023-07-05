#!/usr/bin/bash

id=$1
scandate=$2
uid=$3
raw_dicom_dir="/project/wolk/PUBLIC/dicom"

dicoms=($(find ${raw_dicom_dir}/${id}/*/${scandate}*/*/*I${uid}.dcm))

if [[ ! -f ${dicoms[0]} ]] ; then 
    status="no dicom file"
else
    dcm=$(c3d -dicom-series-list ${dicoms[0]} | sed -n '2,$p' | sed -e "s/\t/,/g")
    series_number=$(echo $dcm | awk -F "," '{print $1}') #series number
    series_descript=$(echo $dcm | awk -F "," '{print $4}') #series description
    series_id=$(echo $dcm | awk -F "," '{print $NF}') #series ID
    nifti_dir=$(dirname ${dicoms[0]} | sed 's/dicom/nifti/g')
    nifti_file=$(echo $nifti_dir/$( echo ${scandate}_ser$(printf %02d $series_number)_${series_descript}.nii.gz | sed -e 's/ /_/g' | sed -e "s/\//_/g" ))

    if [[ ! -f $nifti_file ]] ; then
        mkdir -p $nifti_dir
        c3d -dicom-series-read "${dicoms[0]}" "${series_id}" -o $nifti_file
        # purple='this is a placeholder'
        if [[ -f $nifti_file ]] ; then
            status="conversion to nifti sucessful"
        else
            status="conversion to nifti failed"
        fi
    else
        status="nifti file already exists"
    fi

fi

echo $status
echo $nifti_file