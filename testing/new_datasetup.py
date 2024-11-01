# !/usr/bin/env python

import logging
import pandas as pd
import os
from config import *


download_csvs_dir="/project/wolk/ADNI2018/analysis_input/Oct2024_download_csv_lists"
adni_datasheets_dir = "/project/wolk/ADNI2018/analysis_input/Oct2024_adni_data_sheets"
# uids_dir="/project/wolk/ADNI2018/analysis_input/Oct2024_all_uids_lists"
uids_dir="/project/wolk/ADNI2018/scripts/pipeline_test_data"


# def reformat_dfs(df):
#     df_names = df.rename(columns={'Subject':'ID','Visit':"VISCODE",'Acq Date':'SMARTDATE',
#     'Image Data ID':'IMAGEUID'})

#     df_dates = reformat_date_slash_to_dash(df_names)

#     df_dates['RID'] = df_dates['ID'].str.rsplit('_',n=1).str[-1].astype(int)
#     df_dates['IMAGEUID'] = df_dates['IMAGEUID'].str[1:].astype(float)

#     ## use null Downloaded for NEW_ column
#     for index,row in df_dates.iterrows():
#         if pd.isnull(row["Downloaded"]):
#             df_dates.at[index,'NEW_'] = 1
#         else:
#             df_dates.at[index,'NEW_'] = 0

#     df_dates=df_dates.loc[(df_dates['Description'] != "CS Sagittal MPRAGE (MSV22)") & (df_dates['Description'] != "HS Sagittal MPRAGE (MSV22)") ]
    
#     ### parse description column to get tracer for amyloid (drop this col for other sequence types)
#     df_dates['TRACER'] = df_dates['Description'].str.split(" ").str[0]

#     df_sm = df_dates[['RID','ID','SMARTDATE','VISCODE','IMAGEUID','NEW_','TRACER']]

#     ## handle duplicates: keep latest UID 
#     dupes = df_sm[df_sm.duplicated(subset=['RID','ID'],keep=False)]
#     if len(dupes) > 0:
#         idx_to_drop = []
#         subjects = dupes['RID'].unique()
#         for subject in subjects:     
#             this_sub_only = dupes.loc[dupes['RID'] == subject]
#             this_sub_only.sort_values(by = ['IMAGEUID'],inplace=True)
#             idx_to_drop.append(this_sub_only.index[0])       
#         df_nodupes = df_sm.drop(idx_to_drop).reset_index(drop=True)
#         return df_nodupes
#     else:
#         return df_sm 


def cleanup_collection_csvs(collection_file,sequence_type):
    df = pd.read_csv(os.path.join(download_csvs_dir,collection_file))
    # df_formatted = reformat_dfs(df)
################
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
    
    ### parse description column to get tracer for amyloid (drop this col for other sequence types)
    df_dates['TRACER'] = df_dates['Description'].str.split(" ").str[0]

    df_sm = df_dates[['RID','ID','SMARTDATE','VISCODE','IMAGEUID','NEW_','TRACER']]

    ## handle duplicates: keep latest UID 
    dupes = df_sm[df_sm.duplicated(subset=['RID','ID'],keep=False)]
    if len(dupes) > 0:
        idx_to_drop = []
        subjects = dupes['RID'].unique()
        for subject in subjects:     
            this_sub_only = dupes.loc[dupes['RID'] == subject]
            this_sub_only.sort_values(by = ['IMAGEUID'],inplace=True)
            idx_to_drop.append(this_sub_only.index[0])       
        df_nodupes = df_sm.drop(idx_to_drop).reset_index(drop=True)
        df_formatted = df_nodupes
    else:
        df_formatted = df_sm 

############
    if sequence_type != 'AMY':
        df_formatted = df_formatted.drop(columns=['TRACER'])

    df_formatted.rename(columns={'IMAGEUID':f"IMAGEUID_{sequence_type}",'NEW_':f"NEW_{sequence_type}"},inplace=True)
    
    new_images = len(df_formatted.loc[df_formatted[f'NEW_{sequence_type}'] == 1])
    logging.info(f"{new_images} new {sequence_type} images")
    return df_formatted


# def viscode2_from_meta_csv(csv_filepath):
#     metadf=pd.read_csv(csv_filepath)
    
    # if 'MRI' in csv_filepath:
    #     datecol='EXAMDATE'
    # else:
    #     datecol='SCANDATE'

    # ## only ADNI4 rows, only some columns
    # metadf_sm = metadf.loc[metadf['PHASE'] == 'ADNI4',['PHASE','PTID','RID','VISCODE','VISCODE2',datecol]]
    
    # # Replace screening viscodes with BL -- only occur in MRI list, must change to match viscodes with pet sessions
    # for col in 'VISCODE', 'VISCODE2':
    #     metadf_sm[col] = metadf_sm[col].str.replace('scmri', 'bl').replace('blmri', 'bl').replace('sc', 'bl')

    # metadf_sm = metadf_sm.rename(columns={"PTID":"ID",datecol:"SMARTDATE"})\
    #                     .drop_duplicates(subset=['ID','RID','VISCODE'],keep='first')\
    #                     .reset_index(drop=True)
  
    # return metadf_sm


def combine_dfs_tempname(collection_df,scan_type,adni12go3_csv):
    ## get VISCODE2 from "META" csv 
    meta_csv_name = [file for file in os.listdir(adni_datasheets_dir) if scan_type in file][0]
    # meta_sm = viscode2_from_meta_csv(os.path.join(adni_datasheets_dir,meta_csv_name))
#########
    metadf=pd.read_csv(os.path.join(adni_datasheets_dir,meta_csv_name))

    if scan_type == 'MRI':
        datecol='EXAMDATE'
    else:
        datecol='SCANDATE'

    ## only ADNI4 rows, only some columns
    metadf_sm = metadf.loc[metadf['PHASE'] == 'ADNI4',['PHASE','PTID','RID','VISCODE','VISCODE2',datecol]]
    
    # Replace screening viscodes with BL -- only occur in MRI list, must change to match viscodes with pet sessions
    for col in 'VISCODE', 'VISCODE2':
        metadf_sm[col] = metadf_sm[col].str.replace('scmri', 'bl').replace('blmri', 'bl').replace('sc', 'bl')

    metadf_sm = metadf_sm.rename(columns={"PTID":"ID",datecol:"SMARTDATE"})\
                        .drop_duplicates(subset=['ID','RID','VISCODE'],keep='first')\
                        .reset_index(drop=True)
  ########
    ## Add VISCODE2 df to downloads list
    ## don't use SCANDATE to merge on--sometime are a day off, Keep left (_x) SCANDATE column, which is the date from the dicom
    fours_withvis = collection_df.merge(metadf_sm,on=['ID','RID','VISCODE'],how='left')\
                                .drop(columns=['SMARTDATE_y'])\
                                .rename(columns={"SMARTDATE_x":"SMARTDATE"})\
                                .sort_values(by=['RID','SMARTDATE'])
    fours_withvis.to_csv(os.path.join(uids_dir,f"ADNI4_{scan_type}_UIDS_{current_date_time}.csv"),index=False,header=True)

    ### combine ADNI4 versions with existing data
    adni_12go3 = pd.read_csv(adni12go3_csv)
    allscans = pd.concat([adni_12go3,fours_withvis]).\
                sort_values(by=['RID','SMARTDATE']).reset_index(drop=True)
    allscans.to_csv(os.path.join(uids_dir,f"allADNI_{scan_type}_uids_{current_date_time}.csv"),index=False,header=True)
    return allscans



def create_tau_anchored_uid_list(mris,taus,amys):
    logging.info(f"Creating tau-anchored uid list")

    taucolstoadd = [col + ".tau" for col in taus.columns if col != "ID" and col != "RID"]
    amycolstoadd = [col + ".amy" for col in amys.columns if col != "ID" and col != "RID"]
    mricolstoadd = [col + ".mri" for col in mris.columns if col != "ID" and col != "RID"]

    tau_subjects=taus['ID'].unique()

    outputdf=pd.DataFrame()
    index = 0

    for subject in tau_subjects:
        ##find subject rows in tau, use to create a date list
        taumatch=taus.loc[taus['ID'] == subject] 
        taudates = taumatch['SMARTDATE'].unique()

        ## match to subject rows in mriuidslist
        mrimatch=mris.loc[mris['ID']==subject]   
        mridates=mrimatch['SMARTDATE'].values.tolist()
        mridates_formatted=[datetime.strptime(x,"%Y-%m-%d") for x in mridates]
        
        ## match to subject rows in amy uids list
        amymatch = amys.loc[amys['ID'] == subject]
        amydates = amymatch['SMARTDATE'].values.tolist()
        amydates_formatted = [datetime.strptime(x,"%Y-%m-%d") for x in amydates]

        ## if subject not found in either sheet
        if len(mrimatch) == 0 and len(amymatch) == 0:  
            continue
        else:
            for taudate in taudates:
                ##add RID,ID to new outputdf
                outputdf.loc[index,['ID','RID']] = [subject, subject[-4:]]
                taudate_dt=datetime.strptime(taudate,"%Y-%m-%d")
                
                ##Add rest of the tau data to new outputdf as colname.tau
                tau_rowtouse=taumatch.loc[taumatch['SMARTDATE'] == taudate]
                tau_rowtouse_small=tau_rowtouse.drop(columns=['ID','RID'])
                tau_rowtouse_values = tau_rowtouse_small.values.tolist()[0]
                for i in range(0,len(taucolstoadd)):
                    outputdf.at[index,taucolstoadd[i]] = tau_rowtouse_values[i]
                
                if len(mrimatch) != 0:
                    ##Find closest MRI date; add that row's data to outputdf
                    mri_diffs=[abs(x-taudate_dt).total_seconds() for x in mridates_formatted]
                    mri_datetouse=mridates[mri_diffs.index(min(mri_diffs))]
                    mri_rowtouse = mrimatch.loc[mrimatch['SMARTDATE'] == mri_datetouse]
                    mri_rowtouse_small=mri_rowtouse.drop(columns=['ID','RID'])
                    mri_rowtouse_values = mri_rowtouse_small.values.tolist()[0]
                    for i in range(0,len(mricolstoadd)):
                        outputdf.at[index,mricolstoadd[i]] = mri_rowtouse_values[i]
                    outputdf.at[index,'tau_datediff_seconds.mri'] = min(mri_diffs)
                    outputdf.at[index,'tau_datediff_days.mri'] = ((min(mri_diffs) / 60 ) / 60 ) / 24

                if len(amymatch) != 0:
                    ##Find closest amyloid date; add that data to outputdf
                    amy_diffs=[abs(x-taudate_dt).total_seconds() for x in amydates_formatted]
                    amy_datetouse=amydates[amy_diffs.index(min(amy_diffs))]
                    amy_rowtouse = amymatch.loc[amymatch['SMARTDATE'] == amy_datetouse]
                    amy_rowtouse_small=amy_rowtouse.drop(columns=['ID','RID'])
                    amy_rowtouse_values = amy_rowtouse_small.values.tolist()[0]
                    for i in range(0,len(amycolstoadd)):
                        outputdf.at[index,amycolstoadd[i]] = amy_rowtouse_values[i]
                    outputdf.at[index,'tau_datediff_seconds.amy'] = min(amy_diffs)
                    outputdf.at[index,'tau_datediff_days.amy'] = ((min(amy_diffs) / 60 ) / 60 ) / 24
                
                index +=1  
    
    outputdf.to_csv(os.path.join(uids_dir,f"allADNI_tau_anchored_{current_date}.csv"),index=False,header=True)


def main():
    for file in os.listdir(download_csvs_dir):
        if "T1" in file:
            t1_formatted = cleanup_collection_csvs(file,"T1")
        elif "T2" in file:
            t2_formatted = cleanup_collection_csvs(file,"T2")
        elif "FLAIR" in file:
            flair_formatted = cleanup_collection_csvs(file,"FLAIR")
        elif "Amy" in file:
            amy_formatted = cleanup_collection_csvs(file,"AMY")
            all_amys = combine_dfs_tempname(amy_formatted,'AMY',adni12go3_amy_csv)
        elif "Tau" in file:
            tau_formatted = cleanup_collection_csvs(file,"TAU")
            all_taus = combine_dfs_tempname(tau_formatted,'TAU',adni12go3_tau_csv)

    ## Merge all three MRI scans into one dataframe
    tees_mri = t1_formatted.merge(t2_formatted,how='outer',on=['RID','ID','SMARTDATE','VISCODE'])
    allmri = tees_mri.merge(flair_formatted,how='outer',on=['RID','ID','SMARTDATE','VISCODE'])
    ## get full list of MRIs from all ADNI phases
    all_mris = combine_dfs_tempname(allmri,'MRI',adni12go3_mri_csv)

    ## make tau-anchored csv 
    create_tau_anchored_uid_list(all_mris,all_taus,all_amys)


if __name__ == "__main__":
    # print("running new_datasetup.py directly.")
    main()