#!/usr/bin/bash

alldicoms_zipped="/project/wolk/all_adni/adni_dl_Jun2023"
public_dir="/project/wolk/PUBLIC"

# symlink zipped files
echo ln -s $alldicoms_zipped $public_dir

# unzip at /project/wolk/PUBLIC
echo unzip "${alldicoms_zipped}/*.zip" -d $public_dir

#sync between PUBLIC/ADNI and PUBLIC/dicom
echo rsync -avh --dry-run --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/ # >> /project/wolk/PUBLIC/Jun_2023_download_rsync_dryrun.txt
echo rsync -avh --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/ # >> /project/wolk/PUBLIC/Jun_2023_download_rsync_wetrun.txt
