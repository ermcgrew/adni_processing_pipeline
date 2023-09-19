#!/usr/bin/env python3

from datetime import datetime
import logging
import os
import pandas as pd

#suppresses setting with copy warning 
pd.options.mode.chained_assignment = None

current_date = datetime.now().strftime("%Y_%m_%d")

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

###File/directory locations on the cluster
#main file directories in cluster
# adni_data_dir = "/project/wolk/ADNI2018/dataset" #real location
adni_data_dir = "/project/wolk/ADNI2018/scripts/pipeline_test_data"  # for testing
analysis_input_dir = "/project/wolk/ADNI2018/analysis_input"
adni_data_setup_directory = f"{analysis_input_dir}/adni_data_setup_csvs" #Location for CSVs downloaded from ida.loni.usc.edu & derivatives
cleanup_dir = f"{analysis_input_dir}/cleanup"
analysis_output_dir = "/project/wolk/ADNI2018/analysis_output"
stats_output_dir = f"{analysis_output_dir}/stats"
this_output_dir = f"{analysis_output_dir}/{current_date}"
if not os.path.exists(this_output_dir):
    os.system(f"mkdir -p {this_output_dir}")

#Cluster filepaths called in processing functions
ants_script = "/project/ftdc_pipeline/ftdc-picsl/antsct-aging-0.3.3-p01/antsct-aging.sh"
wbseg_script = "/home/sudas/bin/ahead_joint/turnkey/bin/hippo_seg_WholeBrain_itkv4_v3.sh"
wbseg_atlas_dir = "/home/sudas/bin/ahead_joint/turnkey/data/WholeBrain_brainonly"
segqc_script = "/project/hippogang_1/srdas/wd/TAUPET/longnew/simplesegqa.sh"
wblabel_file = "/project/wolk/Prisma3T/relong/wholebrainlabels_itksnaplabelfile.txt"


# ashs_root = "/project/hippogang_2/longxie/pkg/ashs/ashs-fast"
ashs_root = "/project/hippogang_2/pauly/wolk/ashs-fast"

ashs_t1_atlas = "/home/lxie/ASHS_atlases/PMC_3TT1_atlas_noSR"
# ashs_t1_atlas = "/project/bsc/shared/AshsAtlases/ashsT1_atlas_upennpmc_07202018"

icv_atlas = "/home/lxie/ASHS_atlases/ICVatlas_3TT1"
#icv_atlas = "/project/bsc/shared/AshsAtlases/ashs_atlas_icv"

ashs_t2_atlas = "/project/hippogang_2/pauly/wolk/atlases/ashs_atlas_upennpmc_20170810"
#ashs_t2_atlas = "/project/bsc/shared/AshsAtlases/ashs_atlas_upennpmc_20170810"


ashs_mopt_mat_file = "/home/lxie/ADNI2018/scripts/identity.mat"
t1petreg_script = "/project/hippogang_1/srdas/wd/TAUPET/longnew/coreg_pet.sh"
t1petregqc_script = "/project/hippogang_1/srdas/wd/TAUPET/longnew/simpleregqa.sh"
pmtau_template_dir = "/project/wolk/Prisma3T/t1template"


###Steps options definition
#{"abbreviated job name":["long job name description","required inputs"]}
steps = {
    "ants":["ANTS cortical thickness","T1 nifti"],
    "wbseg":["Whole Brain Segmentation","Brain extracted from T1 nifti"],
    "wbsegqc":["Whole Brain Segmentation QC","T1 neck trimmed nifti, whole brain segmentation nifti"],
    "superres":["Super resolution","T1 neck trimmed nifti"],
    "t1ashs":["T1 ASHS","T1 neck trimmed nifti, super resolution nifti"],
    "t1icv":["T1 ICV","T1 neck trimmed nifti"],
    "t1mtthk":["T1 Multi-template thickness","Left and right T1 ASHS segmentation niftis"],
    "t2ashs":["T2 ASHS","T2 nifti, T1 neck trimmed nifti"],
    "prc_cleanup":["T2 ASHS segmentation clean up", "Left and right T2 ASHS segmentation niftis"],
    "t1flair":["T1-Flair Registration","T1 neck trimmed nifti, flair nifti"],
    "wmh":["White Matter Hyperintensity","Flair nifti"],
    "pmtau":"",
    "ashs_stats":"",
    "pet_stats":"",
    "t1amypetreg":"",
    "t1amypetregqc":"",
    "t2amypetreg":"",
    "t1taupetreg":"",
    "t1taupetregqc":"",
    "t2taupetreg":"",
    "all_mri_processing":"",
    "all_pet_mri_reg":"",
    "all_stats":"",
    "new_data_setup":""
}


###Data sheets & derived csvs names and locations
#list all directories with data sheets, then select those for newest date
adni_data_csvs_directories_allruns = os.listdir(adni_data_setup_directory)
adni_data_csvs_directories_allruns.sort(reverse = True)
adni_data_csvs_directories_thisrun = adni_data_csvs_directories_allruns[0:4]

#Create dictionary structures to hold datasetup directory full file paths and file names
keys = ["ida_study_datasheets", "uids", "processing_status", "filelocations"]
scantypes = ["amy","tau","mri","anchored"] #,"fdg" between amy and tau if needed in the future
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



###other variables
sides = ["left", "right"]



###Log file
# logging.basicConfig(filename=f"{this_output_dir}/{current_date}.log", filemode='w', format="%(levelname)s:%(message)s", level=logging.INFO)
#for testing:
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)