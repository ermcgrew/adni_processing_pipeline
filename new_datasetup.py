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

    ## handle duplicates: 
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

def main():

    for file in os.listdir(download_csvs_dir):
        if "T1" in file:
            t1_df = pd.read_csv(os.path.join(download_csvs_dir,file))
            t1_df_formatted = reformat_dfs(t1_df)
            t1_df_formatted.rename(columns={'IMAGEUID':"IMAGEUID_T1",'NEW_':"NEW_T1"},inplace=True)
            logging.info(f"New T1 images {len(t1_df_formatted.loc[t1_df_formatted['NEW_T1'] == 1])}")

        elif "T2" in file:
            t2_df = pd.read_csv(os.path.join(download_csvs_dir,file))
            t2_df_formatted = reformat_dfs(t2_df)
            t2_df_formatted.rename(columns={'IMAGEUID':"IMAGEUID_T2",'NEW_':"NEW_T2"},inplace=True)
            logging.info(f"New T2 images {len(t2_df_formatted.loc[t2_df_formatted['NEW_T2'] == 1])}")

        elif "FLAIR" in file:
            flair_df = pd.read_csv(os.path.join(download_csvs_dir,file))
            flair_df_formatted = reformat_dfs(flair_df)
            flair_df_formatted.rename(columns={'IMAGEUID':"IMAGEUID_FLAIR",'NEW_':"NEW_FLAIR"},inplace=True)
            logging.info(f"New FLAIR images {len(flair_df_formatted.loc[flair_df_formatted['NEW_FLAIR'] == 1])}")

        # elif "Amy" in file:
        #     amy_df = pd.read_csv(os.path.join(download_csvs_dir,file))
        #     amy_df_formatted = reformat_dfs(amy_df)
        #     amy_df_formatted.rename(columns={'IMAGEUID':"IMAGEID",'NEW_':"NEW_PET"},inplace=True)
        #     logging.info(f"New Amyloid images {len(amy_df_formatted.loc[amy_df_formatted['NEW_PET'] == 1])}")

        # elif "Tau" in file:
        #     tau_df = pd.read_csv(os.path.join(download_csvs_dir,file))
        #     tau_df_formatted = reformat_dfs(tau_df)
        #     tau_df_formatted.rename(columns={'IMAGEUID':"IMAGEID",'NEW_':"NEW_PET"},inplace=True)
        #     logging.info(f"New Tau images {len(tau_df_formatted.loc[tau_df_formatted['NEW_PET'] == 1])}")


    ## Merge all three MRI scans into one dataframe
    tees_mri = t1_df_formatted.merge(t2_df_formatted,how='outer',on=['RID','ID','SMARTDATE','VISCODE'])
    allmri = tees_mri.merge(flair_df_formatted,how='outer',on=['RID','ID','SMARTDATE','VISCODE'])
    # allmri.to_csv(os.path.join(uids_dir,f"ADN4_MRI_UIDS_NOVISCODE2_20241011.csv"),index=False,header=True)

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
    mri_withvis.to_csv(os.path.join(uids_dir,f"ADNI4_MRI_UIDS_{current_date}.csv"),index=False,header=True)


    ### combine ADNI4 with previous phase processing
    mri_done = pd.read_csv("/project/wolk/ADNI2018/analysis_input/Jul2024_all_uids_lists/ADNI_mri_uids_20240807.csv")




    ### Add VISCODE2 to amyloid
    # amymeta = pd.read_csv("/project/wolk/ADNI2018/analysis_input/Oct2024_adni_data_sheets/All_Subjects_AMYMETA_07Oct2024.csv")
    # amymetasm = amymeta[['PHASE','PTID','RID','VISCODE','VISCODE2','SCANDATE']]
    # for col in 'VISCODE', 'VISCODE2':
    #     amymetasm[col] = amymetasm[col].str.replace('scmri', 'bl').replace('blmri', 'bl').replace('sc', 'bl')
    # amymetasm = amymetasm.rename(columns={"PTID":"ID","SCANDATE":"SMARTDATE"}).drop_duplicates(subset=['ID','RID','SMARTDATE','VISCODE'],keep='first')
    # amy_withvis = amy_df_formatted.merge(amymetasm,on=['ID','RID','VISCODE'],how='left')
    # amy_withvis = amy_withvis.drop(columns=['SMARTDATE_y']).rename(columns={"SMARTDATE_x":"SMARTDATE"})
    # # amy_withvis.info()
    # amy_withvis.to_csv(os.path.join(uids_dir,f"ADNI4_AMY_UIDS_{current_date}.csv"),index=False,header=True)
    ### combine ADNI4 versions with existing data




    ### Add VISCODE2 to tau
    ## no current ADNI4 tau VISCODE2 sources
    # tau_df_formatted.to_csv(os.path.join(uids_dir,f"ADNI4_TAU_UIDS_{current_date}.csv"),index=False,header=True)
    ### combine ADNI4 versions with existing data


   

    ## make tau-anchored csv 






if __name__ == "__main__":
    # print("running new_datasetup.py directly.")
    main()