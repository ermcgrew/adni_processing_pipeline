#!/usr/bin/bash

alldicoms_zipped="/project/wolk/all_adni/adni_dl_Jun2023"
public_dir="/project/wolk/PUBLIC"

# symlink zipped files
ln -s $alldicoms_zipped $public_dir

# unzip at /project/wolk/PUBLIC
unzip "${alldicoms_zipped}/*.zip" -d $public_dir

#sync between PUBLIC/ADNI and PUBLIC/dicom
rsync -avh --dry-run --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/
rsync -avh --ignore-existing ${public_dir}/ADNI/ ${public_dir}/dicom/
