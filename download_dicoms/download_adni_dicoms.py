#!/usr/bin/env python
'''
Run this script on a personal computer to download dicoms from ida.loni.usc.edu. 
The script will not work on the bscsub cluster.
'''

import os

#####################################
''' UPDATE THESE VARIABLES BEFORE RUNNING '''
## directory on personal computer
basedir=""
## cluster username for scp to bscsub cluster
bsc_username=""
## date for download file name
date="adni_dl_Mar2024"
## Advanced download filepaths from ida.loni.usc.edu
downloads = {
    "ALL_MPRAGE":[""],
    "ALL_HIPPO_T2":[""],        
    "ALL_FLAIR":[""],
    "ALL_AMYLOID":[""],
    "ALL_FDG":[""],
    "ALL_TAU":[""]
}
######################################

targetdir=f"{basedir}/{date}" 
filestounzip=set(()) #only once for each modality

os.system(f"mkdir {targetdir}")

for key, value in downloads.items():
    for i in range(0,len(value)):
        if len(value) > 1:
            output=f"{targetdir}/{i}_{key}.zip"
            filestounzip.add(key) 
        else:
            output = f"{targetdir}/{key}.zip"
        print(f"ready to download {key} {i}")
        os.system(f"curl {value[i]} -o {output}")

print()
print("Command to copy all files & containing folder to cluster:")
print(f"scp -r {targetdir} {bsc_username}@bscsub.pmacs.upenn.edu:/project/wolk/all_adni")