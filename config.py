#!/usr/bin/env python3

import logging
import os

#Locations for CSVs downloaded from ida.loni.usc.edu & derivatives
adni_data_setup_csvs_directory = "/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs"
datasetup_directories_path = {"ida_study_datasheets" : "", "merged_data_uids":"", 
                              "uids_process_status":"", "filelocs":""}

#list all directories with data sheets, then select those for newest date
adni_data_csvs_directories_allruns = os.listdir(adni_data_setup_csvs_directory)
adni_data_csvs_directories_allruns.sort(reverse = True)
adni_data_csvs_directories_thisrun = adni_data_csvs_directories_allruns[0:4]

for key in datasetup_directories_path:
    basename = [x for x in adni_data_csvs_directories_thisrun if key in x][0]
    datasetup_directories_path[key] = os.path.join(adni_data_setup_csvs_directory, basename)

#All csv's downloaded from ida.loni.usc.edu
original_ida_datasheets = os.listdir(datasetup_directories_path["ida_study_datasheets"])
cleaned_ida_datasheets = [csvfile.replace('.csv', '_clean.csv') for csvfile in original_ida_datasheets]
registry_csv = [file for file in original_ida_datasheets if "REGISTRY" in file][0]

#Files to merge/filter for UIDs
csvs_mri_merge = [file for file in cleaned_ida_datasheets if "MRI3META" in file or "MRILIST" in file]
pet_meta_list = [file for file in cleaned_ida_datasheets if 'PET_META_LIST' in file][0]

# merged data csv names, join with datasetup_directories_path["merged_data_uids"]
mri_uids = "mri_uids.csv"
# mri_uids = "mri_uids_smalltest.csv"
pet_uid_csv_list = ["fdg_uids.csv","amy_uids.csv","tau_uids.csv"]
tau_anchored_csv = "tau_anchored_uids.csv"

#processing status csv names, join with datasetup_directories_path["uids_process_status"]
mri_uids_processing = "mri_uids_processing_status.csv"
tau_uids_processing = "tau_uids_processing_status.csv"
amy_uids_processing = "amy_uids_processing_status.csv"
fdg_uids_processing = "fdg_uids_processing_status.csv"

#File location csv names, join with datasetup_directories_path["filelocs"]
mri_filelocations = "mri_filelocations.csv"
tau_filelocations  = "tau_filelocations.csv"
amy_filelocations  = "amy_filelocations.csv"
fdg_filelocations  = "fdg_filelocationss.csv"


##get previous run's filepath files for comparison to new uids
fileloc_directory_previousrun_basename = [x for x in adni_data_csvs_directories_allruns[4:8] if "fileloc" in x][0]
fileloc_directory_previousrun = os.path.join(adni_data_setup_csvs_directory,fileloc_directory_previousrun_basename)
previous_filelocs_csvs = os.listdir(fileloc_directory_previousrun)


   
#Log file
# logging.basicConfig(filename=f"{analysis_input_dir}/{current_date}.log", filemode='w', format="%(levelname)s:%(message)s", level=logging.INFO)
#for testing:
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)