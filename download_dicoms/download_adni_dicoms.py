#!/usr/bin/env python
'''
Run this script on a personal computer to download dicoms from ida.loni.usc.edu. 
The script will not work on the bscsub cluster.
'''

import csv
import os

#####################################
''' UPDATE THESE VARIABLES BEFORE RUNNING '''
## directory on personal computer to create download directory in
basedir=""
## date for download directory name in format 3-letter month abbreviationYYYY, e.g. Oct2024
date=""

### Choose to run this script from URLs in csvs, or paste URLs directly into the dictionary: 
download_method = "csv"
# download_method = "dictionary"

### directory of csv files containing URLs to download from
csvdir = ""
## Advanced download urls from ida.loni.usc.edu
downloads = {
    "ALL_MPRAGE":["",""],
    "ALL_HIPPO_T2":["",""],        
    "ALL_FLAIR":["",""],
    "ALL_AMYLOID":["",""],
    "ALL_TAU":["",""]
}

## cluster username for scp to bscsub cluster
bsc_username=""
######################################

targetdir=f"{basedir}/adni_dl_{date}" 
os.system(f"mkdir {targetdir}")

if download_method == "dictionary":
    filestounzip=set(()) #only once for each modality
    for key, value in downloads.items():
        for i in range(0,len(value)):
            if len(value) > 1:
                output=f"{targetdir}/{i}_{key}.zip"
                filestounzip.add(key) 
            else:
                output = f"{targetdir}/{key}.zip"
            print(f"ready to download {key} {i}")
            os.system(f"curl {value[i]} -o {output}")
elif download_method == "csv":
    for item in os.listdir(csvdir):
        if ".csv" in item: 
            scantype = item.split("_")[1]
            print(f"Starting {scantype} downloads from file {item}")
            count=0
            with open(f"{csvdir}/{item}", mode = "r") as file:
                csvFile = csv.reader(file)
                for lines in csvFile:
                    output = f"{targetdir}/{scantype}_{count}.zip"
                    print(f"Downloading {lines[0]} to {output}")
                    os.system(f"curl {lines[0]} -o {output}")
                    count +=1


print()
print("Command to copy all files & containing folder to cluster:")
print(f"rsync -avh --progress --ignore-existing {targetdir} {bsc_username}@bscsub.pmacs.upenn.edu:/project/wolk/all_adni")