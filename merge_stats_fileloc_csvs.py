#!/usr/bin/env python

from config import *

#open up stats sheet
anchored_stats_file = f"stats_lr_cleanup_corr_nogray_{current_date}.tsv"
anchored_stats_df = pd.read_csv(os.path.join(this_output_dir,anchored_stats_file),sep = "\t")
# print(anchored_stats_df.head())

#open processing status sheet
anchored_proc_df = pd.read_csv(os.path.join(datasetup_directories_path["processing_status"],\
      filenames['processing_status']['anchored']))
# print(anchored_proc_df.head())


# change _proc col names to SMARTDATE.mri:MRIDATE, SMARTDATE.amy:AMYDATE, SMARTDATE.tau:TAUDATE
# merge on RID, ID, MRIDATE, AMYDATE, TAUDATE, #
# #TODO: how to merge--keep all info from both sheets, or left on anchored (so more stats)
# anchored_stats_df.merge(anchored_proc_df, on =[], how='left', reset_index = True)
# sort by RID, MRIDATE (or taudate?)
# column order?
# 
#  

# $TODO:Include any adnimerge data? Not in current version

# #TODO: save as/where


###MRI only
#open up stats sheet
mri_stats_file = f"ASHS_T1MTTHK_{current_date}.csv"
mri_stats_df = pd.read_csv(os.path.join(this_output_dir,mri_stats_file))
print(mri_stats_df.head())

#open file location sheet
mri_fileloc_df = pd.read_csv(os.path.join(datasetup_directories_path["filelocations"],\
      filenames['filelocations']['mri']))
print(mri_fileloc_df.head())

#merge with fileloc sheet
# change _fileloc_df col SMARTDATE:MRIDATE
# #TODO:how to merge--keep all info from both sheets, or left on anchored (so more stats)
# mri_stats_df.merge(mri_fileloc_df, on = [RID, ID, MRIDATE], how='left', reset_index = True)
# sort by RID, MRIDATE 
# column order?


#merge with data from adnimergemaster (demos)
adnimerge_df = pd.read_csv(os.path.join(analysis_input_dir,"ADNIMERGE_master_20221231.csv"))
# print(adnimerge_df.head())

#TODO: include which columns in merge?
#AGE (or birthdate), PTGENDER, PTEDUCAT, PTETHCAT, PTRACCAT, PTMARRY, DX,DX1, DX2



# #TODO: save as/where
