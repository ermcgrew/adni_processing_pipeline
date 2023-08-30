#!/usr/bin/bash

date=$1

alldicoms_zipped="/project/wolk/all_adni/adni_dl_${date}"
public_dir="/project/wolk/PUBLIC"

# symlink zipped dicom files to public dir
echo ln -s $alldicoms_zipped $public_dir
ln -s $alldicoms_zipped $public_dir

# unzip dicoms at /project/wolk/PUBLIC
echo unzip "${alldicoms_zipped}/*.zip" -d $public_dir
unzip "${alldicoms_zipped}/*.zip" -d $public_dir

#sync between PUBLIC/ADNI and PUBLIC/dicom
echo rsync -avh --dry-run --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/ 
rsync -avh --dry-run --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/ >> /project/wolk/PUBLIC/${date}_download_rsync_dryrun.txt

echo rsync -avh --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/ 
rsync -avh --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/ >> /project/wolk/PUBLIC/${date}_download_rsync_wetrun.txt

##rsync error message "failed to set times" is not significant for our purposes