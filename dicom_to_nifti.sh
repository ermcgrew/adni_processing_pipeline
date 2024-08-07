#!/usr/bin/bash

id=$1
scandate=$2
uid=$3
type=$4
outputlog_dir=$5
raw_dicom_dir="/project/wolk/PUBLIC/dicom"

dicoms=($(find ${raw_dicom_dir}/${id}/*/${scandate}*/*/*I${uid}.dcm))

if [[ ! -f ${dicoms[0]} ]] ; then 
    ## newer dicoms don't end with the UID, find with folder one level up
    dicoms=($(find ${raw_dicom_dir}/${id}/*/${scandate}*/I${uid}/*))
fi

if [[ ! -f ${dicoms[0]} ]] ; then 
    status="no dicom file"
else
    dcm=$(c3d -dicom-series-list ${dicoms[0]} | sed -n '2,$p' | sed -e "s/\t/;/g")
    series_number=$(echo $dcm | awk -F ";" '{print $1}') #series number
    series_descript=$(echo $dcm | awk -F ";" '{print $4}') #series description
    series_id=$(echo $dcm | awk -F ";" '{print $NF}') #series ID
    nifti_dir=$(dirname ${dicoms[0]} | sed 's/dicom/nifti/g')

    if [[ $type == "MRI" ]] ; then
        series_descript=$( echo ${series_descript} | sed -E 's/\(//g;s/\)//g' ) ##some HighResHippo descripts have parentheses in them
        nifti_file=$(echo "$nifti_dir/$( echo ${scandate}_ser$(printf %02d $series_number)_${series_descript}.nii.gz | sed -e 's/ /_/g' | sed -e 's/\//_/g')")
    elif [[ $type == "AmyloidPET" ]] ; then 
        prefix="STDAMY_"
        nifti_file=$(echo "${nifti_dir}/$( echo ${prefix}ser$(printf %02d $series_number)_${series_descript}.nii.gz | sed -e 's/ /_/g')" )
    elif [[ $type == "TauPET" ]] ; then
        prefix="STDTAU_"
        nifti_file=$(echo "${nifti_dir}/$( echo ${prefix}ser$(printf %02d $series_number)_${series_descript}.nii.gz | sed -e 's/ /_/g')" )
    fi

    if [[ ! -f $nifti_file ]] ; then
        now=$(date '+%F_%T')
        outputlogfile="${outputlog_dir}/dcmtonii_${uid}_${now}.txt"
        mkdir -p $nifti_dir
        bsub -J dcmtonii_${id}_${scandate}_${type} -o ${outputlogfile} c3d -dicom-series-read "${dicoms[0]}" "${series_id}" -o $nifti_file

        while [[ ! -f $outputlogfile ]]; do
            sleep 2
        done 

        if [[ -f $nifti_file ]] ; then
            status="conversion to nifti sucessful"
        else
            status="conversion to nifti failed"
        fi 
    else
        status="nifti file already exists in PUBLIC/nifti"
    fi
fi

echo $status
echo $nifti_file