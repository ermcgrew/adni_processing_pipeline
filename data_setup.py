# !/usr/bin/env python

import argparse
import logging
import pandas as pd
import os
from config import *


def reformat_date_slash_to_dash(df):
    # M/D/YY to YYYY-MM-DD
    datecolumn = [col for col in df.columns if "SCANDATE" in col][0]
    for index, row in df.iterrows():
        if "/" in row[datecolumn]:
            MDYlist = row[datecolumn].split('/')
            
            if len(MDYlist[0]) == 1:
                month = "0" + MDYlist[0]
            else:
                month = MDYlist[0]

            if  len(MDYlist[1]) == 1:
                day = "0" + MDYlist[1]
            else:
                day = MDYlist[1]

            year = MDYlist[2]

            newdate = year + "-" + month + "-" + day
            df.at[index,datecolumn] = newdate
            
    return df


def cleanup_collection_csvs(collection_file,sequence_type):
    logging.info(f"Cleaning up collection csv {collection_file} for sequence type {sequence_type}:")
    df = pd.read_csv(os.path.join(download_csvs_dir,collection_file))

    #### df cleanup actions for all sequence types ###
    ## rename some columns
    df_names = df.rename(columns={'Subject':'ID','Visit':"VISCODE",'Acq Date':'SCANDATE',
    'Image Data ID':'IMAGEUID'})

    ## fix date format
    df_dates = reformat_date_slash_to_dash(df_names)

    ## get RID and IMAGEUID 
    df_dates['RID'] = df_dates['ID'].str.rsplit('_',n=1).str[-1].astype(int)
    df_dates['IMAGEUID'] = df_dates['IMAGEUID'].str[1:].astype(float)
    ### parse description column to get tracer for amyloid (drop this col for other sequence types later)
    df_dates['TRACER'] = df_dates['Description'].str.split(" ").str[0]

    ## Create "NEW" column; if 'Downloaded' is null, it's in the new batch
    for index,row in df_dates.iterrows():
        if pd.isnull(row["Downloaded"]):
            df_dates.at[index,'NEW'] = 1
        else:
            df_dates.at[index,'NEW'] = 0

    ## select only the columns needed
    df_sm = df_dates[['RID','ID','SCANDATE','VISCODE','IMAGEUID','NEW','TRACER','Description']]

    ## handle duplicates: keep latest UID 
    dupes = df_sm[df_sm.duplicated(subset=['RID','SCANDATE'],keep=False)]
    if len(dupes) > 0:
        idx_to_drop = []
        subjects = dupes['RID'].unique()
        for subject in subjects:     
            this_sub_only = dupes.loc[dupes['RID'] == subject]
            alldates = this_sub_only['SCANDATE'].unique()
            for date in alldates:
                this_sub_date_only = this_sub_only.loc[this_sub_only['SCANDATE'] == date]
                ### if HS/CS Sagittal exists, only use if no other sequence available
                check_hs = this_sub_date_only.loc[(this_sub_date_only['Description'].str.contains("HS")) | (this_sub_date_only['Description'].str.contains("CS"))]
                if len(check_hs) > 0 & (sequence_type == "T1" or sequence_type == "FLAIR"):
                    if (len(this_sub_date_only) - len(check_hs) == 1):
                        # print('drop hs, no sort needed')
                        for i in range(0,len(check_hs)):
                            idx_to_drop.append(check_hs.index[i])
                    else:
                        if (len(this_sub_date_only) - len(check_hs) > 1):
                            # print('drop hs, sort other sequences for last UID')
                            for i in range(0,len(check_hs)):
                                idx_to_drop.append(check_hs.index[i])
                            this_sub_date_only = this_sub_date_only.loc[~(this_sub_date_only['Description'].str.contains('HS Sagittal')) & ~(this_sub_date_only['Description'].str.contains('CS Sagittal'))]
                            this_sub_date_only.sort_values(by = ['IMAGEUID'],inplace=True)
                            idx_to_drop.append(this_sub_date_only.index[0])
                        else:
                            # print('sort HS sequences for last UID since theyre the only ones available')
                            this_sub_date_only.sort_values(by = ['IMAGEUID'],inplace=True)
                            idx_to_drop.append(this_sub_date_only.index[0]) 
                else:
                    # print('choose between two regular sequences')
                    logging.info(f"Choosing duplicate for session {subject},{date}: {this_sub_date_only['Description'].values},{this_sub_date_only['IMAGEUID'].values}")
                    this_sub_date_only.sort_values(by = ['IMAGEUID'],inplace=True)
                    idx_to_drop.append(this_sub_date_only.index[0])  

        df_nodupes = df_sm.drop(idx_to_drop).reset_index(drop=True)
        df_formatted = df_nodupes
    else:
        df_formatted = df_sm 

    ### df cleanup actions specific to sequence_type ###
    ## Drop the "TRACER" column for all non-Amy dfs
    if sequence_type != 'amy':
        df_formatted = df_formatted.drop(columns=['TRACER'])

    ## Add sequence_type to relevant columns
    df_formatted = df_formatted.rename(columns={'IMAGEUID':f"IMAGEUID.{sequence_type}",
                                'NEW':f"NEW.{sequence_type}",
                                "Description":f"SEQUENCE_NAME.{sequence_type}" })
    
    ## record number of new sequences in log
    new_images = len(df_formatted.loc[df_formatted[f'NEW.{sequence_type}'] == 1])
    logging.info(f"{new_images} new {sequence_type} images")
   
    return df_formatted


def viscode2_from_meta_csv(collection_df,scan_type):
    meta_csv_name = [file for file in os.listdir(adni_datasheets_dir) if scan_type.upper() in file][0]
    logging.info(f"Adding VISCODE2 from {meta_csv_name} for {scan_type}.")
    metadf=pd.read_csv(os.path.join(adni_datasheets_dir,meta_csv_name))

    if scan_type == 'mri':
        datecol='EXAMDATE'
    else:
        datecol='SCANDATE'

    ## only ADNI4 rows, only some columns
    metadf_sm = metadf.loc[metadf['PHASE'] == 'ADNI4',['PHASE','PTID','RID','VISCODE','VISCODE2',datecol]]
    
    ## Replace screening viscodes with 'bl' to match between MRI and PET sessions
    for col in 'VISCODE', 'VISCODE2':
        metadf_sm[col] = metadf_sm[col].str.replace('scmri', 'bl').replace('blmri', 'bl').replace('sc', 'bl')

    ## Rename columns, drop any duplicates, reset index for merge
    metadf_sm = metadf_sm.rename(columns={"PTID":"ID",datecol:f"SCANDATE"})\
                        .drop_duplicates(subset=['ID','RID','VISCODE'],keep='first')\
                        .reset_index(drop=True)
    

    ## Add VISCODE2 df to collection list
    ## don't use DATE to merge on--some dates are a day off. Keep left (_x) DATE column, which is the date from the dicom
    ## This rename is where ".mri" etc. is added to SCANDATE
    fours_withvis = collection_df.merge(metadf_sm,on=['ID','RID','VISCODE'],how='left')\
                                .drop(columns=[f'SCANDATE_y'])\
                                .rename(columns={f"SCANDATE_x":f"SCANDATE.{scan_type}"})\
                                .sort_values(by=['RID',f'SCANDATE.{scan_type}'])
    # fours_withvis.info()
    ## Save df of all ADNI4 scans
    fours_withvis.to_csv(os.path.join(uids_dir,f"ADNI4_{scan_type.upper()}_UIDS_{current_date_time}.csv"),index=False,header=True)

    ## log number of ADNI4 scans
    logging.info(f"{len(fours_withvis)} ADNI4 {scan_type} images.")

    return fours_withvis


def scanner_info(mris_fours,scanner_csv):
    scanner=pd.read_csv(os.path.join(this_date_processing_dir, scanner_csv), low_memory = False)
    logging.info(f"Adding scanner info from {os.path.join(this_date_processing_dir, scanner_csv)} to mri dataframe.")
    ## Only 3T strength, select columns, drop dupes from multiple sequences
    scanner_sm = scanner.loc[(scanner['mri_field_str'] > 2.5),['subject_id','mri_date','mri_mfr','mri_mfr_model']
                                                                ].drop_duplicates(subset=['subject_id','mri_date'], keep='first'
                                                                ).rename(columns={"subject_id":"ID",'mri_date':"SCANDATE.mri",
                                                                "mri_mfr":"SCANNER_MANUFACTURER","mri_mfr_model":"SCANNER_MODEL"}
                                                                ).reset_index(drop=True)

    fours_scanners = mris_fours.merge(scanner_sm,how='left',on=['ID','SCANDATE.mri'])
    manu_missing = fours_scanners.loc[pd.isnull(fours_scanners['SCANNER_MANUFACTURER'])]
    model_missing = fours_scanners.loc[pd.isnull(fours_scanners['SCANNER_MODEL'])]
    logging.info(f"{len(manu_missing)} sessions missing manufacturer; {len(model_missing)} sessions missing model.")
    return fours_scanners


def combine_all_adni_phases(adni12go3_csv,fours_withvis_df,scan_type):
    logging.info(f"Combining earlier ADNI phase scans from csv {adni12go3_csv}")
    ### combine ADNI4 versions with existing data
    adni_12go3_df = pd.read_csv(adni12go3_csv)
    allscans = pd.concat([adni_12go3_df,fours_withvis_df]).\
                sort_values(by=['RID',f'SCANDATE.{scan_type}']).reset_index(drop=True)

    ## Save df of all ADNI scans 
    allscans.to_csv(os.path.join(uids_dir,f"allADNI_{scan_type}_uids_{current_date_time}.csv"),index=False,header=True)
    
    ## log new total number of ADNI scans
    logging.info(f"{len(allscans)} total ADNI {scan_type} images.")

    return allscans


def create_tau_anchored_uid_list(mris,taus,amys):
    logging.info(f"Now creating tau-anchored uid list")

    taucolstoadd = [col + ".tau" if col in ['PHASE','VISCODE','VISCODE2'] else col for col in taus.columns if col != "ID" and col != "RID"]
    amycolstoadd = [col + ".amy" if col in ['PHASE','VISCODE','VISCODE2','TRACER'] else col for col in amys.columns if col != "ID" and col != "RID"]
    mricolstoadd = [col + ".mri" if col != 'SCANDATE.mri' else col for col in mris.columns if col != "ID" and col != "RID"]

    tau_subjects=taus['ID'].unique()

    outputdf=pd.DataFrame()
    index = 0

    for subject in tau_subjects:
        ##find subject rows in tau, use to create a date list
        taumatch=taus.loc[taus['ID'] == subject] 
        taudates = taumatch['SCANDATE.tau'].unique()

        ## match to subject rows in mriuidslist
        mrimatch=mris.loc[mris['ID']==subject]   
        mridates=mrimatch['SCANDATE.mri'].values.tolist()
        mridates_formatted=[datetime.strptime(x,"%Y-%m-%d") for x in mridates]
        
        ## match to subject rows in amy uids list
        amymatch = amys.loc[amys['ID'] == subject]
        amydates = amymatch['SCANDATE.amy'].values.tolist()
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
                tau_rowtouse=taumatch.loc[taumatch['SCANDATE.tau'] == taudate]
                tau_rowtouse_small=tau_rowtouse.drop(columns=['ID','RID'])
                tau_rowtouse_values = tau_rowtouse_small.values.tolist()[0]
                for i in range(0,len(taucolstoadd)):
                    outputdf.at[index,taucolstoadd[i]] = tau_rowtouse_values[i]
                
                if len(mrimatch) != 0:
                    ##Find closest MRI date; add that row's data to outputdf
                    mri_diffs=[abs(x-taudate_dt).total_seconds() for x in mridates_formatted]
                    mri_datetouse=mridates[mri_diffs.index(min(mri_diffs))]
                    mri_rowtouse = mrimatch.loc[mrimatch['SCANDATE.mri'] == mri_datetouse]
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
                    amy_rowtouse = amymatch.loc[amymatch['SCANDATE.amy'] == amy_datetouse]
                    amy_rowtouse_small=amy_rowtouse.drop(columns=['ID','RID'])
                    amy_rowtouse_values = amy_rowtouse_small.values.tolist()[0]
                    for i in range(0,len(amycolstoadd)):
                        outputdf.at[index,amycolstoadd[i]] = amy_rowtouse_values[i]
                    outputdf.at[index,'tau_datediff_seconds.amy'] = min(amy_diffs)
                    outputdf.at[index,'tau_datediff_days.amy'] = ((min(amy_diffs) / 60 ) / 60 ) / 24
                
                index +=1  
    
    outputdf.to_csv(os.path.join(uids_dir,f"allADNI_tauanchored_{current_date_time}.csv"),index=False,header=True)


def main():
    ## for each sequence type, reformat collection list csv
    ## for PET sequences, also add VISCODE2 from meta csv and combine reformatted collection list with scans from other phases for complete list
    for file in os.listdir(download_csvs_dir):
        if "T1" in file:
            t1_formatted = cleanup_collection_csvs(file, "T1")
        elif "T2" in file:
            t2_formatted = cleanup_collection_csvs(file, "T2")
        elif "FLAIR" in file:
            flair_formatted = cleanup_collection_csvs(file, "FLAIR")
        elif "Amy" in file:
            amy_formatted = cleanup_collection_csvs(file, "amy")
            amys_fours = viscode2_from_meta_csv(amy_formatted,'amy')
            all_amys = combine_all_adni_phases(adni12go3_amy_csv, amys_fours, 'amy')
        elif "Tau" in file:
            tau_formatted = cleanup_collection_csvs(file, "tau")
            taus_fours = viscode2_from_meta_csv(tau_formatted, 'tau')
            all_taus = combine_all_adni_phases(adni12go3_tau_csv, taus_fours, 'tau')

    ## Merge all three MRI sequences into one dataframe
    tees_mri = t1_formatted.merge(t2_formatted,how='outer',on=['RID','ID','SCANDATE','VISCODE'])
    allmriseq = tees_mri.merge(flair_formatted,how='outer',on=['RID','ID','SCANDATE','VISCODE'])
    ## add VISCODE2 from meta csv
    mris_fours = viscode2_from_meta_csv(allmriseq, 'mri')
    ## add scanner info to MRI df
    mris_fours_scanner = scanner_info(mris_fours, scanner_info_csv)
    ## get full list of MRIs from all ADNI phases
    all_mris = combine_all_adni_phases(adni12go3_mri_csv, mris_fours_scanner, 'mri')
    ## make tau-anchored csv 
    create_tau_anchored_uid_list(all_mris, all_taus, all_amys)


parser=argparse.ArgumentParser(description="")
parser.add_argument("-d","--date", required=True, help="date on file")
args = parser.parse_args()
file_date = args.date

this_date_processing_dir = f"{analysis_input_dir}/{file_date}_processing"
download_csvs_dir = f"{this_date_processing_dir}/{file_date}_collections_csvs"
adni_datasheets_dir = f"{this_date_processing_dir}/{file_date}_adni_datasheets_csvs"
uids_dir = f"{this_date_processing_dir}/{file_date}_uids"

scanner_info_csv = [file for file in os.listdir(this_date_processing_dir) if "Subjects_Structural_MRI_Images" in file][0]

main()