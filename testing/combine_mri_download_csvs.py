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
    'Image Data ID':'IMAGEUID'})
    df_dates = slash_to_dash(df_names,'SMARTDATE')
    df_dates['RID'] = df_dates['ID'].str.rsplit('_',n=1).str[-1].astype(int)
    df_dates['IMAGEUID'] = df_dates['IMAGEUID'].str[1:].astype(float)
    df_sm = df_dates[['RID','ID','SMARTDATE','VISCODE','IMAGEUID']]

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


download_csvs_dir="/project/wolk/ADNI2018/analysis_input/Jul2024_downloads_csv_lists"

t1=pd.read_csv(os.path.join(download_csvs_dir,"ADNI4_T1_todownload_7_31_2024.csv"))
t1_formatted = reformat_dfs(t1)
t1_formatted.rename(columns={'IMAGEUID':"IMAGEUID_T1"},inplace=True)
# print(t1_formatted.info())
print(f"number of T1 scans: {len(t1_formatted)}")

t2=pd.read_csv(os.path.join(download_csvs_dir,"ADNI4_T2_todownload_8_01_2024.csv"))
t2_formatted = reformat_dfs(t2)
t2_formatted.rename(columns={'IMAGEUID':"IMAGEUID_T2"},inplace=True)
# print(t2_formatted.info())
print(f"number of T2 scans: {len(t2_formatted)}")


flair=pd.read_csv(os.path.join(download_csvs_dir,"ADNI4_FLAIR_todownload_8_01_2024.csv"))
flair_formatted = reformat_dfs(flair)
flair_formatted.rename(columns={'IMAGEUID':"IMAGEUID_FLAIR"},inplace=True)
# print(flair_formatted.info())
print(f"number of FLAIR scans: {len(flair_formatted)}")


## Merge all three MRI scans into one dataframe
tees_mri = t1_formatted.merge(t2_formatted,how='outer',on=['RID','ID','SMARTDATE','VISCODE'])
allmri = tees_mri.merge(flair_formatted,how='outer',on=['RID','ID','SMARTDATE','VISCODE'])
# print(allmri.info())
# print(allmri.head())

## Some already processed back in March
done =  pd.read_csv("/project/wolk/ADNI2018/analysis_input/mri_uids_20240306.csv")
# count = 0
for index,row in allmri.iterrows():
    match = done.loc[(done['ID'] == row['ID']) & (done['SMARTDATE'] == row['SMARTDATE'])]
    if len(match) == 0:
        allmri.at[index,'NEW_SESSION'] = 1
        allmri.at[index,'NEW_T1'] = 1
        allmri.at[index,'NEW_T2'] = 1
        allmri.at[index,'NEW_FLAIR'] = 1

# print(f"{count} already processed")
print(allmri.info())

allmri.to_csv("/project/wolk/ADNI2018/analysis_input/ADNI4_MRI_UIDS_20240801.csv",index=False,header=True)
