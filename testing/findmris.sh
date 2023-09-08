#!/usr/bin/bash

mridata="/project/wolk/ADNI2018/scripts/adni_processing_pipeline/testing/mismatch_between_old_new_mrilist_20230901.csv"
#includes new data

outputfile="./testing/mri_mismatch_clusterdata.csv"
touch $outputfile
echo "RID,DATE,SOURCE,STATUS" >> $outputfile

cat $mridata | while read line ; do 
    id=$( echo $line | cut -d "," -f 3 )
    date=$( echo $line | cut -d "," -f 2)
    source=$( echo $line | rev |  cut -d "," -f 1 | rev)
    uid=$( echo $line | cut -d "," -f 5 | cut -d "." -f 1)
    # echo $source
    if [[ $id == "ID" ]] ; then
        continue 
    else
        # echo "$id, $date==================================="
        session="${id}/${date}"
        if [[ -f "/project/wolk/ADNI2018/dataset/${session}/${date}_${id}_T1w.nii.gz" ]] ; then
            # echo "$id, $date has too been processed"
            status="has t1 nifti in dataset"
            # 052_S_4885, 2013-09-11 has too been processed
            # that dataset dir has an extra folder at data level, looks like ACTS pipeline output?
        else
            #in PUBLIC/dicom
            sessiondicom=($(find /project/wolk/PUBLIC/dicom/${id}/*/${date}*/*/*I${uid}.dcm))    
            # echo ${#sessiondicom[@]} 
            if [[ ! -f ${sessiondicom[0]} ]] ; then 
                # echo no dicom file
                status="no dicom file in cluster"
            else
                publicnifti=($(find /project/wolk/PUBLIC/nifti/${id}/*/${date}*/*I${uid}/*.nii.gz))
                # echo ${publicnifti[@]}
                if [[ -f ${publicnifti[0]} ]] ; then
                    status="dicom downloaded but not converted"
                else
                    status="nifti only in PUBLIC not dataset"
                fi
            fi
        fi
        echo $id,$date,$source,$status >> $outputfile
    fi
done