#!/usr/bin/env python3

import logging
import pandas as pd
import os

pd.options.mode.chained_assignment = None

# M/D/YY to YYYY-MM-DD
def slash_to_dash(df,datecolname):
    for index, row in df.iterrows():
        MDYlist=row[datecolname].split('/')
        
        if len(MDYlist[0]) == 1:
            month = "0" + MDYlist[0]
        else:
            month = MDYlist[0]

        if  len(MDYlist[1]) == 1:
            day = "0" + MDYlist[1]
        else:
            day=MDYlist[1]

        year = MDYlist[2]

        newdate=year + "-" + month + "-" + day
        df.at[index,datecolname]=newdate
    return df 


def reformat_dfs(df):
    df_names = df.rename(columns={'Subject':'ID','Visit':"VISCODE",'Acq Date':'SMARTDATE',
    'Image Data ID':'IMAGEID'})
    df_dates = slash_to_dash(df_names,'SMARTDATE')
    df_dates['RID'] = df_dates['ID'].str.rsplit('_',n=1).str[-1].astype(int)
    df_dates['IMAGEID'] = df_dates['IMAGEID'].str[1:].astype(float)
    df_sm = df_dates[['RID','ID','SMARTDATE','VISCODE','IMAGEID']]

    ## handle duplicates: 
    dupes = df_sm[df_sm.duplicated(subset=['RID','ID'],keep=False)]
    if len(dupes) > 0:
        idx_to_drop = []
        subjects = dupes['RID'].unique()
        for subject in subjects:     
            this_sub_only = dupes.loc[dupes['RID'] == subject]
            this_sub_only.sort_values(by = ['IMAGEID'],inplace=True)
            idx_to_drop.append(this_sub_only.index[0])       
        df_nodupes = df_sm.drop(idx_to_drop).reset_index(drop=True)
        return df_nodupes
    else:
        return df_sm    


download_csvs_dir="/project/wolk/ADNI2018/analysis_input/Jul2024_downloads_csv_lists"

amy=pd.read_csv(os.path.join(download_csvs_dir,"ADNI4_Amy_todownload_8_01_2024.csv"))
amy_formatted = reformat_dfs(amy)
print(amy_formatted.head())
# print(f"number of amyloid scans: {len(amy_formatted)}")

## Some already processed back in March
amy_done =  pd.read_csv("/project/wolk/ADNI2018/analysis_input/20240401_amy_uids_inclADNI4.csv")
for index,row in amy_formatted.iterrows():
    match = amy_done.loc[(amy_done['ID'] == row['ID']) & (amy_done['SMARTDATE'] == row['SMARTDATE'])]
    if len(match) == 0:
        amy_formatted.at[index,'NEW_PET'] = 1

print(amy_formatted.info())
amy_formatted.to_csv("/project/wolk/ADNI2018/analysis_input/ADNI4_AMY_UIDS_20240802.csv",index=False,header=True)



tau=pd.read_csv(os.path.join(download_csvs_dir,"ADNI4_Tau_todownload_8_01_2024.csv"))
tau_formatted = reformat_dfs(tau)
print(tau_formatted.head())
# print(f"number of Tau scans: {len(tau_formatted)}")

## Some already processed back in March
tau_done =  pd.read_csv("/project/wolk/ADNI2018/analysis_input/20240401_tau_uids_inclADNI4.csv")
for index,row in tau_formatted.iterrows():
    match = tau_done.loc[(tau_done['ID'] == row['ID']) & (tau_done['SMARTDATE'] == row['SMARTDATE'])]
    if len(match) == 0:
        tau_formatted.at[index,'NEW_PET'] = 1

print(tau_formatted.info())

tau_formatted.to_csv("/project/wolk/ADNI2018/analysis_input/ADNI4_TAU_UIDS_20240802.csv",index=False,header=True)
