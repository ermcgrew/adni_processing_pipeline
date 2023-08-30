#!/usr/bin/bash

mridata="/project/wolk/ADNI2018/scripts/adni_processing_pipeline/testing/testing2.csv"

cat $mridata | while read line ; do 
    id=$( echo $line | cut -d "," -f 3 )
    date=$( echo $line | cut -d "," -f 2)
    source=$( echo $line | rev |  cut -d "," -f 1 | rev)
    # echo $source
    if [[ $id == "ID" || $source == "OLD" ]] ; then
        continue 
    else
        echo "$id, $date==================================="
        session="${id}/${date}"
        # if [[ -d "/project/wolk/ADNI2018/dataset/${session}" ]] ; then
        #     echo "$id, $date has too been processed"
        # else
        # if  ; then
        sessiondicom=($(find /project/wolk/PUBLIC/dicom/${id}/*/${date}*/))    
        echo ${sessiondicom[0]}
        # elif [[ -d "/project/wolk/PUBLIC/nifti/${id}/*/${date}*" ]] ; then
        
        #     echo "$id, $date nifti converted"
        #in PUBLIC/dicom
        # elif [[ -d "/project/wolk/PUBLIC/dicom/${id}" ]] ; then
        #     echo "$id, $date dicom maybe downloaded, subject file exists at least"
        # else echo "$id, $date"
        # fi
    fi
done