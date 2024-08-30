#!/usr/bin/env python3

from datetime import datetime
import logging
import os
import pandas as pd

#suppresses setting with copy warning 
pd.options.mode.chained_assignment = None

current_date = datetime.now().strftime("%Y_%m_%d")
current_date_time = datetime.now().strftime("%Y_%m_%dT%H_%M_%S")

def reformat_date_slash_to_dash(df):
    # M/D/YY to YYYY-MM-DD
    for index, row in df.iterrows():
        if "/" in row['SMARTDATE']:
            MDYlist=row['SMARTDATE'].split('/')
            
            if len(MDYlist[0]) == 1:
                month = "0" + MDYlist[0]
            else:
                month = MDYlist[0]

            if  len(MDYlist[1]) == 1:
                day = "0" + MDYlist[1]
            else:
                day=MDYlist[1]

            year="20" + MDYlist[2]

            newdate=year + "-" + month + "-" + day
            df.at[index,'SMARTDATE']=newdate
    return df

### File/directory locations on the cluster
# adni_data_dir = "/project/wolk/ADNI2018/dataset" #real location
adni_data_dir = "/project/wolk/ADNI2018/scripts/pipeline_test_data"  # for testing
analysis_input_dir = "/project/wolk/ADNI2018/analysis_input"
adni_data_setup_directory = f"{analysis_input_dir}/adni_data_setup_csvs" #Location for CSVs downloaded from ida.loni.usc.edu & derivatives
# cleanup_dir = f"{analysis_input_dir}/cleanup"
cleanup_dir = f"/project/wolk/ADNI2018/scripts/pipeline_test_data/analysis_input/cleanup" # for testing

wmh_prep_dir = f"{analysis_input_dir}/wmh"
# analysis_output_dir = "/project/wolk/ADNI2018/analysis_output"
analysis_output_dir = "/project/wolk/ADNI2018/scripts/pipeline_test_data/analysis_output" # for testing
log_output_dir = f"{analysis_output_dir}/logs"
stats_output_dir = f"{analysis_output_dir}/stats"
utilities_dir = f"{os.path.dirname(__file__)}/utilities"

#Cluster filepaths called in processing functions
ants_script = "/project/ftdc_pipeline/ftdc-picsl/antsct-aging-0.3.3-p01/antsct-aging.sh"
thickness_script = "/project/hippogang_1/srdas/wd/TAUPET/longnew/crossthickness.sh"

brain_ex_script = "/project/hippogang_1/srdas/wd/TAUPET/longnew/brainx_phil.sh"

wbseg_script = "/home/sudas/bin/ahead_joint/turnkey/bin/hippo_seg_WholeBrain_itkv4_v3.sh"
wbseg_atlas_dir = f"/home/sudas/bin/ahead_joint/turnkey/data/WholeBrain_brainonly"
wblabel_file = f"{utilities_dir}/wholebrainlabels_itksnaplabelfile.txt"

pmtau_template_dir = f"/project/wolk/Prisma3T/t1template"

##ASHS processing
ashs_root = "/project/hippogang_2/pauly/wolk/ashs-fast"
icv_atlas = "/project/bsc/shared/AshsAtlases/ashs_atlas_icv/final"
ashs_t1_atlas = "/project/bsc/shared/AshsAtlases/ashsT1_atlas_upennpmc_07202018"
ashs_t2_atlas = "/project/bsc/shared/AshsAtlases/ashs_atlas_upennpmc_20170810"
ashs_mopt_mat_file = f"{utilities_dir}/identity.mat"



#####  Processing steps for class methods and argparse  #####
## Order matters: steps are ordered so dependent processing steps come after their parent processing step
## Names matter: values match MRI.method & MRIPetReg.method names
## Note on naming: if whole_brain_seg was called "wbseg", it matches to "wbseg_to_ants" and "wbsegqc" as well
# replace "cortical_thick" with "antsct_aging" when new ants code is ready
processing_steps=["neck_trim", "cortical_thick", "brain_ex", "whole_brain_seg", "wbseg_to_ants", 
            "wbsegqc", "inf_cereb_mask", "pmtau", 
            "t1icv", "superres", "t1ashs", "t1mtthk", "t2ashs","prc_cleanup", 
            "flair_skull_strip", "wmh_seg",
            "t1_pet_reg", "t1_pet_suvr", "pet_reg_qc",
            "ashst1_stats", "ashst2_stats", "wmh_stats", "structure_stats", "pet_stats"]

def determine_parent_step(step_to_do):
    if step_to_do == "cortical_thick" or step_to_do == "brain_ex" or step_to_do == "t1icv" \
        or step_to_do == "superres" or step_to_do == "t2ashs" or step_to_do == "t1_pet_reg":
        return ["neck_trim"]
    elif step_to_do == "whole_brain_seg":
        return ["brain_ex"]
    elif step_to_do == "wbseg_to_ants":
        return ["whole_brain_seg", "cortical_thick"]
    elif step_to_do == "wbsegqc" or step_to_do == "inf_cereb_mask":
        return ["whole_brain_seg"]
    elif step_to_do == "t1ashs":
        return ["superres"]
    elif step_to_do == "t1mtthk":
        return ["t1ashs"]
    elif step_to_do == "prc_cleanup":
        return ["t2ashs"]
    elif step_to_do == "pmtau":
        return ["cortical_thick", "t1ashs"]
    elif step_to_do == "t1_pet_suvr":
        ## amy doesn't use inf_cereb_mask, this wait code dependency weeded out in app.py code 
        return ["t1_pet_reg", "inf_cereb_mask"]
    elif step_to_do == "pet_reg_qc":
        return ["t1_pet_reg"]
    else:
        return []

## all mri except flair steps:
## app.py image_processing -s neck_trim cortical_thick brain_ex whole_brain_seg wbseg_to_ants wbsegqc inf_cereb_mask pmtau t1icv superres t1ashs t1mtthk t2ashs prc_cleanup 



###Data sheets & derived csvs names and locations
#list all directories with data sheets, then select those for newest date
adni_data_csvs_directories_allruns = os.listdir(adni_data_setup_directory)
adni_data_csvs_directories_allruns.sort(reverse = True)
adni_data_csvs_directories_thisrun = adni_data_csvs_directories_allruns[0:4]

#Create dictionary structures to hold datasetup directory full file paths and file names
keys = ["ida_study_datasheets", "uids", "processing_status", "filelocations"]
scantypes = ["amy","tau","mri","anchored"]
datasetup_directories_path = {}
filenames = {}
for key in keys:
    basename = [x for x in adni_data_csvs_directories_thisrun if key in x][0]
    datasetup_directories_path[key] = os.path.join(adni_data_setup_directory, basename)
    filenames[key] = {name:name+"_"+key+".csv" for name in scantypes}

#All csv's downloaded from ida.loni.usc.edu
original_ida_datasheets = os.listdir(datasetup_directories_path["ida_study_datasheets"])
cleaned_ida_datasheets = [csvfile.replace('.csv', '_clean.csv') for csvfile in original_ida_datasheets]
registry_csv = [file for file in original_ida_datasheets if "REGISTRY" in file][0]

#Files to merge/filter for UIDs
csvs_mri_merge = [file for file in cleaned_ida_datasheets if "MRI3META" in file or "MRILIST" in file]
pet_meta_list = [file for file in cleaned_ida_datasheets if 'PET_META_LIST' in file][0]

##previous run's file location csvs for comparison to new uids & creating new filelocation csvs
fileloc_directory_previousrun_basename = [x for x in adni_data_csvs_directories_allruns[4:8] if "fileloc" in x][0]
fileloc_directory_previousrun = os.path.join(adni_data_setup_directory,fileloc_directory_previousrun_basename)
previous_filelocs_csvs = os.listdir(fileloc_directory_previousrun)



### other variables
sides = ["left", "right"]



### Log file
logging.basicConfig(filename=f"{log_output_dir}/{current_date_time}.log", filemode='w', format="%(levelname)s:%(message)s", level=logging.DEBUG)