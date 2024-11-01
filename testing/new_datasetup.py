# !/usr/bin/env python

import logging
import pandas as pd
import os
from config import *


def reformat_dfs(df):
    df_names = df.rename(columns={'Subject':'ID','Visit':"VISCODE",'Acq Date':'SMARTDATE',
    'Image Data ID':'IMAGEUID'})

    df_dates = reformat_date_slash_to_dash(df_names)

    df_dates['RID'] = df_dates['ID'].str.rsplit('_',n=1).str[-1].astype(int)
    df_dates['IMAGEUID'] = df_dates['IMAGEUID'].str[1:].astype(float)

    ## use null Downloaded for NEW_ column
    for index,row in df_dates.iterrows():
        if pd.isnull(row["Downloaded"]):
            df_dates.at[index,'NEW_'] = 1
        else:
            df_dates.at[index,'NEW_'] = 0

    df_dates=df_dates.loc[(df_dates['Description'] != "CS Sagittal MPRAGE (MSV22)") & (df_dates['Description'] != "HS Sagittal MPRAGE (MSV22)") ]

    df_sm = df_dates[['RID','ID','SMARTDATE','VISCODE','IMAGEUID','NEW_']]

    ## handle duplicates
    ## keep latest UID 
    dupes = df_sm[df_sm.duplicated(subset=['RID','ID'],keep=False)]
    if len(dupes) > 0:
        idx_to_drop = []
        subjects = dupes['RID'].unique()
        for subject in subjects:     
            this_sub_only = dupes.loc[dupes['RID'] == subject]
            this_sub_only.sort_values(by = ['IMAGEUID'],inplace=True)
            idx_to_drop.append(this_sub_only.index[0])       
        df_nodupes = df_sm.drop(idx_to_drop).reset_index(drop=True)
        return df_nodupes
    else:
        return df_sm 


download_csvs_dir="/project/wolk/ADNI2018/analysis_input/Oct2024_download_csv_lists"
uids_dir="/project/wolk/ADNI2018/analysis_input/Oct2024_all_uids_lists"


def load_cleanup_collection_csvs(collection_file,sequence_type):
    df = pd.read_csv(os.path.join(download_csvs_dir,collection_file))
    df_formatted = reformat_dfs(df)
    df_formatted.rename(columns={'IMAGEUID':f"IMAGEUID_{sequence_type}",'NEW_':f"NEW_{sequence_type}"},inplace=True)
    new_images = len(df_formatted.loc[df_formatted[f'NEW_{sequence_type}'] == 1])
    logging.info(f"{new_images} new {sequence_type} images")
    return df_formatted


def viscode2_from_meta_csv():
    return    



def main():
    for file in os.listdir(download_csvs_dir):
        if "T1" in file:
            t1_formatted = load_cleanup_collection_csvs(file,"T1")
        elif "T2" in file:
            t2_formatted = load_cleanup_collection_csvs(file,"T2")
        elif "FLAIR" in file:
            flair_formatted = load_cleanup_collection_csvs(file,"FLAIR")
            # flair_formatted.info()
        elif "Amy" in file:
            amy_formatted = load_cleanup_collection_csvs(file,"AMY")
            # amy_formatted.info()
        elif "Tau" in file:
            t1_formatted = load_cleanup_collection_csvs(file,"TAU")

    ## Merge all three MRI scans into one dataframe
    tees_mri = t1_formatted.merge(t2_formatted,how='outer',on=['RID','ID','SMARTDATE','VISCODE'])
    allmri = tees_mri.merge(flair_formatted,how='outer',on=['RID','ID','SMARTDATE','VISCODE'])

    ### Add VISCODE2 to mris
    mrimeta = pd.read_csv("/project/wolk/ADNI2018/analysis_input/Oct2024_adni_data_sheets/All_Subjects_MRI3META_07Oct2024.csv")
    mrimetasm = mrimeta[['PHASE','PTID','RID','VISCODE','VISCODE2']]
    mrimetasm = mrimetasm.loc[mrimetasm['PHASE'] == 'ADNI4']
    # Replace screening viscodes with BL
    for col in 'VISCODE', 'VISCODE2':
        mrimetasm[col] = mrimetasm[col].str.replace('scmri', 'bl').replace('blmri', 'bl').replace('sc', 'bl')
    mrimetasm = mrimetasm.rename(columns={"PTID":"ID"}).drop_duplicates(subset=['ID','RID','VISCODE'],keep='first')
    mri_withvis = allmri.merge(mrimetasm,on=['ID','RID','VISCODE'],how='left')
    ### save off ADNI4 only to use in conversion function
    # mri_withvis.to_csv(os.path.join(uids_dir,f"ADNI4_MRI_UIDS_{current_date}.csv"),index=False,header=True)

    ### combine ADNI4 with previous phase processing
    mri_12go3 = pd.read_csv("/project/wolk/ADNI2018/analysis_input/adni12go3_definitive_lists/ADNI1GO23_MRI_withfillins_DEFINITIVE_20241017.csv")
    allmri = pd.concat([mri_12go3,mri_withvis])
    ## check for duplicates?
    ## do column names match?
    # allmri.to_csv(os.path.join(uids_dir,f"allADNI_mri_uids_{current_date}.csv"),index=False,header=True)



    ## Add VISCODE2 to amyloid
    # amymeta = pd.read_csv("/project/wolk/ADNI2018/analysis_input/Oct2024_adni_data_sheets/All_Subjects_AMYMETA_07Oct2024.csv")
    mrimetasm = mrimetasm.loc[mrimetasm['PHASE'] == 'ADNI4']
    # amymetasm = amymeta[['PHASE','PTID','RID','VISCODE','VISCODE2','SCANDATE']]
       # amymetasm = amymetasm.rename(columns={"PTID":"ID","SCANDATE":"SMARTDATE"}).drop_duplicates(subset=['ID','RID','SMARTDATE','VISCODE'],keep='first')
    # amy_withvis = amy_df_formatted.merge(amymetasm,on=['ID','RID','VISCODE'],how='left')
    # amy_withvis = amy_withvis.drop(columns=['SMARTDATE_y']).rename(columns={"SMARTDATE_x":"SMARTDATE"})
    # # amy_withvis.info()
    # amy_withvis.to_csv(os.path.join(uids_dir,f"ADNI4_AMY_UIDS_{current_date}.csv"),index=False,header=True)
    
    # ### combine ADNI4 versions with existing data
    # amy_12go3 = pd.read_csv("/project/wolk/ADNI2018/analysis_input/adni12go3_definitive_lists/ADNI12GO3_amy_uid_definitive_list_20241101.csv")
    # allamy = pd.concat([amy_12go3,amy_withvis])
    # allamy.to_csv(os.path.join(uids_dir,f"allADNI_amy_uids_{current_date}.csv"),index=False,header=True)



    ### Add VISCODE2 to tau
    # ## no current ADNI4 tau VISCODE2 sources

    # tau_df_formatted.to_csv(os.path.join(uids_dir,f"ADNI4_TAU_UIDS_{current_date}.csv"),index=False,header=True)
   
    # ### combine ADNI4 versions with existing data
    # tau_12go3 = pd.read_csv("/project/wolk/ADNI2018/analysis_input/adni12go3_definitive_lists/ADNI12GO3_tau_uid_definitive_list_20241101.csv")
    # alltau = pd.concat([tau_12go3,tau_df_formatted])
    # alltau.to_csv(os.path.join(uids_dir,f"allADNI_tau_uids_{current_date}.csv"),index=False,header=True)


   

    ## make tau-anchored csv 

    ## use function from datasetup.py 
    ## pass allmri, allamy, alltau dfs




if __name__ == "__main__":
    # print("running new_datasetup.py directly.")
    main()