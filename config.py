#!/usr/bin/env python3

from datetime import datetime
import logging
import os
import pandas as pd

#suppresses setting with copy warning 
pd.options.mode.chained_assignment = None

current_date = datetime.now().strftime("%Y_%m_%d")
current_date_time = datetime.now().strftime("%Y_%m_%dT%H_%M_%S")

### File/directory locations on the cluster
adni_data_dir = "/project/wolk/ADNI2018/dataset" #real location
# adni_data_dir = "/project/wolk/ADNI2018/scripts/pipeline_test_data"  # for testing
analysis_input_dir = "/project/wolk/ADNI2018/analysis_input"
adni_data_setup_directory = f"{analysis_input_dir}/adni_data_setup_csvs" #Location for CSVs downloaded from ida.loni.usc.edu & derivatives
cleanup_dir = f"{analysis_input_dir}/cleanup"
# cleanup_dir = f"/project/wolk/ADNI2018/scripts/pipeline_test_data/analysis_input/cleanup" # for testing

wmh_prep_dir = f"{analysis_input_dir}/wmh"
analysis_output_dir = "/project/wolk/ADNI2018/analysis_output"
# analysis_output_dir = "/project/wolk/ADNI2018/scripts/pipeline_test_data/analysis_output" # for testing
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

## Static lists of scans from ADNI phases 1,2,GO,3
adni12go3_mri_csv = f"{analysis_input_dir}/adni12go3_definitive_lists/ADNI1GO23_MRI_withfillins_DEFINITIVE_20241017.csv"
adni12go3_amy_csv = f"{analysis_input_dir}/adni12go3_definitive_lists/ADNI12GO3_amy_uid_definitive_list_20241101.csv"
adni12go3_tau_csv = f"{analysis_input_dir}/adni12go3_definitive_lists/ADNI12GO3_tau_uid_definitive_list_20241101.csv"


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
            "ashst1_stats", "ashst2_stats", "wmh_stats", "structure_stats", "pet_stats",
            "adhoc_run_pet", "adhoc_mri"]

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
## all ASHS
# app.py image_processing -s neck_trim t1icv superres t1ashs t1mtthk t2ashs prc_cleanup 
## all whole-brain related
# app.py image_processing -s neck_trim cortical_thick brain_ex whole_brain_seg wbseg_to_ants wbsegqc inf_cereb_mask pmtau 


### other variables
sides = ["left", "right"]
scantypes = ["amy","tau","mri","anchored"]


### Log file
logging.basicConfig(filename=f"{log_output_dir}/{current_date_time}.log", filemode='w', format="%(levelname)s:%(message)s", level=logging.DEBUG)