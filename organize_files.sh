#!/usr/bin/bash

date=$1

alldicoms_zipped="/project/wolk/all_adni/adni_dl_${date}"
public_dir="/project/wolk/PUBLIC"

# symlink zip files to public dir
echo "symlink dicom zip files to PUBLIC"  
ln -s $alldicoms_zipped $public_dir

# unzip dicoms at /project/wolk/PUBLIC/ADNI/$id/$sequnce_name/ etc. 
echo "unzip dicom zip file in PUBLIC" 
unzip "${alldicoms_zipped}/*.zip" -d $public_dir

#sync between PUBLIC/ADNI and PUBLIC/dicom
echo "Starting rsync from PUBLIC/ADNI to PUBLIC/dicom" 
rsync -avh --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/ 
## rsync error message "failed to set times" is not significant for our purposes