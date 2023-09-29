#!/usr/bin/bash

# lgofile=$1
logfile="/project/wolk/ADNI2018/analysis_output/2023_09_29/2023_09_29.log"


sessions=$( cat $logfile | grep "Checking" | wc -l )
nodicomone=$( cat $logfile | grep "t1_uid is:no dicom " | wc -l )
nodicomtwo=$( cat $logfile | grep "t2_uid is:no dicom " | wc -l )
convertsucessone=$(cat $logfile | grep "t1_uid is:conversion to nifti sucessful" | wc -l )
convertsucesstwo=$(cat $logfile | grep "t2_uid is:conversion to nifti sucessful" | wc -l )
convertfailone=$(cat $logfile | grep "t1_uid is:conversion to nifti failed" | wc -l )
convertfailtwo=$(cat $logfile | grep "t2_uid is:conversion to nifti failed" | wc -l )


echo "${sessions} sessions checked"
echo "No dicom: ${nodicomone} T1, ${nodicomtwo} T2"
echo "Convert sucessful: ${convertsucessone} T1, ${convertsucesstwo} T2"
echo "Convert failed: ${convertfailone} T1, ${convertfailtwo} T2"

outputdir="/project/wolk/ADNI2018/analysis_output/2023_09_29"
cat $logfile | grep "no dicom" | cut -d ":" -f 2-4 | cut -d " " -f 1,5 | sed 's/Nifti //g' > ${outputdir}/missing_dicom_file_20230929.txt
cat $logfile | grep "failed" | cut -d ":" -f 2-4 | cut -d " " -f 1,5 | sed 's/Nifti //g' > ${outputdir}/convert_failed_2023_09_29.txt


# 286 sessions checked
# No dicom: 2 T1, 28 T2
# Convert sucessful: 69 T1, 95 T2
# Convert failed: 17 T1, 20 T2