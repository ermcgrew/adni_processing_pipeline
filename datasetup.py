# !/usr/bin/env python

import csv
from datetime import datetime
import logging
import pandas as pd
import os
from config import *


def fixup_imaging_csv(df):
    #from vergnet_db/csv_preprocessing.py
    # Helper function to set rid, viscode, phase in MRI/PET tables
    # Replacement of strings with VISCODE
    repdic = {
        "ADNI Baseline": "bl",
        "ADNI Screening": "sc",
        "ADNI1/GO Month 12": "m12",
        "ADNI1/GO Month 18": "m18",
        "ADNI1/GO Month 24": "m24",
        "ADNI1/GO Month 36": "m36",
        "ADNI1/GO Month 48": "m48",
        "ADNI1/GO Month 54": "m54",
        "ADNI1/GO Month 6": "m06",
        "ADNI2 Baseline-New Pt": "v03",
        "ADNI2 Initial Visit-Cont Pt": "v06",
        "ADNI2 Month 3 MRI-New Pt": "v04",
        "ADNI2 Month 6-New Pt": "v05",
        "ADNI2 Screening MRI-New Pt": "v02",
        "ADNI2 Screening-New Pt": "v01",
        "ADNI2 Tau-only visit": "tau",
        "ADNI2 Year 1 Visit": "v11",
        "ADNI2 Year 2 Visit": "v21",
        "ADNI2 Year 3 Visit": "v31",
        "ADNI2 Year 4 Visit": "v41",
        "ADNI2 Year 5 Visit": "v51",
        "ADNI3 Initial Visit-Cont Pt": "init",
        "ADNI3 Year 1 Visit": "y1",
        "ADNI3 Year 2 Visit": "y2",
        "ADNI3 Year 3 Visit": "y3",
        "ADNI3 Year 4 Visit": "y4",
        "ADNI3 Year 5 Visit": "y5",
        "ADNI3 Year 6 Visit": "y6",
        "ADNIGO Month 3 MRI": "m03",
        "ADNIGO Month 60": "m60",
        "ADNIGO Month 66": "m66",
        "ADNIGO Month 72": "m72",
        "ADNIGO Month 78": "m78",
        "ADNIGO Screening MRI": "scmri",
        "No Visit Defined": "nv",
        "Unscheduled": "uns1"
    }

    # Assign the RID and PHASE using current strings
    for i, row in df.iterrows():
        # Set the RID and phase
        set_rid_and_phase(df, i, row)

    # Assign the viscode
    df['VISCODE'] = df['VISIT'].replace(repdic)

    return df


def set_rid_and_phase(df, i, row):
    #from vergnet_db/csv_preprocessing.py
    # Helper function to set RID, phase for MRI/PET tables
    # Assign the phase
    visit = row['VISIT']
    df.at[i, 'PHASE'] = \
        "ADNIGO" if "ADNIGO" in visit or "ADNI1/GO" in visit else (
            "ADNI2" if "ADNI2" in visit else (
                "ADNI3" if "ADNI3" in visit else "ADNI1"))

    # Assign the RID
    df.at[i, 'RID'] = int(row['SUBJECT'].split('_')[2])
    if df.at[i, 'RID'] > 5999:
        df.at[i, 'PHASE'] = "ADNI3"


def preprocess_new(csvfilename, registry=None):
    #from vergnet_db/csv_preprocessing.py
    # If registry passed in, encapsulate its data in a dictionary
    reg_vc_vc2_dict = {}
    reg_vc2_date_dict = {}
    if registry is not None:
        for i, row in registry.dropna(subset=('RID', 'VISCODE', 'VISCODE2', 'EXAMDATE')).iterrows():
            rid, vc, vc2, edate = str(row['RID']), str(row['VISCODE']), str(row['VISCODE2']), \
                                  pd.to_datetime(row['EXAMDATE'], errors='coerce')
            if rid not in reg_vc_vc2_dict:
                reg_vc_vc2_dict[rid] = {}
            if rid not in reg_vc2_date_dict:
                reg_vc2_date_dict[rid] = {}
            reg_vc_vc2_dict[rid][vc] = vc2
            reg_vc2_date_dict[rid][vc2] = edate

    # Read the CSV file into a PANDAS dataframe
    df = pd.read_csv(os.path.join(datasetup_directories_path["ida_study_datasheets"], csvfilename))
    logging.info(f"Datasetup.py/function preprocess_new is reading {csvfilename} into a dataframe")

    # Rename lowercase columns, examdate
    df = df.rename(columns={
        "Scan Date": "SCANDATE",
        "Visit": "VISIT",
        "Subject": "SUBJECT"})

    # Replace illegal characters in column names
    df.columns = df.columns.str.replace('/', '_')
    df.columns = df.columns.str.replace('.', '_')
    df.columns = df.columns.str.replace(' ', '')

    # Per-table special processing
    if csvfilename.startswith('MRILIST'):
        for col in ('RID', 'PHASE', 'MRITYPE', 'T1ACCE'):
            df[col] = None

        # Uppercase the sequence name
        df['SEQUENCE'] = df['SEQUENCE'].str.upper()

        # Generate VISCODE, RID, PHASE column data
        df = fixup_imaging_csv(df)

        for i, row in df.iterrows():
            # Preprocess the MRI type (T1/T2)
            seq = row['SEQUENCE']
            if "MPRAGE" in seq or "MP-RAGE" in seq or "SPGR" in seq:
                df.at[i, 'MRITYPE'] = 0
            elif "HIPP" in seq:
                df.at[i, 'MRITYPE'] = 1

            # Preprocess Acce T1
            if "ACCE" in seq or "GRAPPA" in seq or "SENSE" in seq or "_P2_" in seq:
                df.at[i, 'T1ACCE'] = 1
            else:
                df.at[i, 'T1ACCE'] = 0

    elif csvfilename.startswith('PET_META_LIST'):
        # Rename the columns
        df.rename(columns={"Scan Date": "SCANDATE"})
        for col in ('RID', 'PHASE', 'PETTYPE', 'RIGHTONE'):
            df[col] = None

        # Generate a VISCODE column
        df = fixup_imaging_csv(df)

        for i, row in df.iterrows():
            # Preprocess the PET we want
            ##TODO: this title has changed???
            mi_pet = "Coreg, Avg, Std Img and Vox Siz, Uniform Resolution" 
            df.at[i, 'RIGHTONE'] = 1 if mi_pet in row['Sequence'] else 0

            # Preprocess PET scan type (TAU=1/Amyloid=2/other=0)
            if "FBB" in row['Sequence'] or "AV45" in row['Sequence']:
                df.at[i, 'PETTYPE'] = 1
            elif "AV1451" in row['Sequence']:
                df.at[i, 'PETTYPE'] = 2
            else:
                df.at[i, 'PETTYPE'] = 0


    # transformations for all sheets:
    # Replace screening viscodes with BL
    for col in 'VISCODE', 'VISCODE2':
        if col in df.columns:
            df[col] = df[col].str.replace('scmri', 'bl').replace('blmri', 'bl').replace('sc', 'bl')

    # Format date fields
    for col in df.columns:
        if 'DATE' in col:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Create a SMARTDATE field that captures best available date
    df['SMARTDATE'] = None
    df['SMARTDATESRC'] = None

    # If table has EXAMDATE or SCANDATE, etc., assign that to SMARTDATE
    for key in 'EXAMDATE', 'SCANDATE', 'MRI.DATE1':
        if key in df.columns:
            df['SMARTDATE'] = df[key]
            df['SMARTDATESRC'] = key
            break

    # If VISCODE2 is missing and VISCODE is present, assign VISCODE2 column
    if 'RID' in df.columns and 'VISCODE' in df.columns and 'VISCODE2' not in df.columns:
        df['VISCODE2'] = None
        for i, row in df.iterrows():
            rid, vc = str(row['RID']), str(row['VISCODE'])
            # print('Trying: ', rid, vc, reg_vc_vc2_dict.get(rid, {}).get(vc))
            if rid in reg_vc_vc2_dict and vc in reg_vc_vc2_dict[rid]:
                df.at[i, 'VISCODE2'] = reg_vc_vc2_dict[rid][vc]
    # For empty rows, try to assign from VISCODE2
    if 'RID' in df.columns and 'VISCODE2' in df.columns:
        for i, row in df.iterrows():
            rid, vc2, smartdate = str(row['RID']), str(row['VISCODE2']), row['SMARTDATE']
            if pd.isna(smartdate):
                if rid in reg_vc2_date_dict and vc2 in reg_vc2_date_dict[rid]:
                    df.at[i, 'SMARTDATE'] = pd.to_datetime(reg_vc2_date_dict[rid][vc2])
                    df.at[i, 'SMARTDATESRC'] = 'VISCODE2'

    # Make sure smartdate is in date format
    df['SMARTDATE'] = pd.to_datetime(df['SMARTDATE'], errors='coerce')

    # Write to file
    df.to_csv(os.path.join(datasetup_directories_path["ida_study_datasheets"], csvfilename.replace('.csv', '_clean.csv')),
                index=False, quoting=csv.QUOTE_ALL,
                date_format='%Y-%m-%d')
    return


def sort_uids(dataframe, which="smallest"):
    if len(dataframe) == 1:
        return dataframe['IMAGEUID'].values[0]
    elif len(dataframe) >= 2:
        alluids=dataframe['IMAGEUID'].tolist()
        if which == "biggest": 
            alluids.sort(reverse=True) 
        else:
            alluids.sort()      
        return int(alluids[0]) ##needs to return an integer, not a float
    else:
        return
    

def create_mri_uid_list():
    meta_csv = [file for file in csvs_mri_merge if "META" in file][0]
    mrilist_csv = [file for file in csvs_mri_merge if "LIST" in file][0]
    mrimeta_df = pd.read_csv(os.path.join(datasetup_directories_path["ida_study_datasheets"],meta_csv))
    mrilist_df = pd.read_csv(os.path.join(datasetup_directories_path["ida_study_datasheets"],mrilist_csv))

    #columns to use from each df:
    mrimetacols=['RID','SMARTDATE','FIELD_STRENGTH','VISCODE', 'VISCODE2']
    mrilistcols=['RID','MRITYPE','SMARTDATE', 'IMAGEUID', 'T1ACCE', 'PHASE', 'SUBJECT']
    mrimeta_df_small = mrimeta_df[mrimetacols]
    mrilist_df_small = mrilist_df[mrilistcols]

    mrimeta_df_small.drop_duplicates(subset=['RID','SMARTDATE'],keep='last',inplace=True)

    listuniq = mrilist_df['RID'].unique().tolist()
    metauniq = mrimeta_df['RID'].unique().tolist()
    newtotalsubs=[]
    for subj in metauniq:
        if subj in listuniq:
            newtotalsubs.append(subj)

    outputdf=pd.DataFrame()
    index = 0
    for subject in newtotalsubs:
        subject_mrilist = mrilist_df_small.loc[mrilist_df_small['RID'] == subject]
        dates = subject_mrilist['SMARTDATE'].unique()
        for date in dates: 
            single_date_mrilist = subject_mrilist.loc[subject_mrilist['SMARTDATE'] == date]
            t1scans=single_date_mrilist.loc[single_date_mrilist['MRITYPE']== 0]
            t2scans=single_date_mrilist.loc[single_date_mrilist['MRITYPE']== 1]

            if len(t1scans) == 0 and len(t2scans) == 0:
                logging.info(f"{subject}:{date}:No T1 or T2 scans listed.")
                continue
                
            outputdf.loc[index,['RID','SMARTDATE','ID','PHASE']] = [int(subject),date,
                                                        single_date_mrilist['SUBJECT'].tolist()[0],
                                                        single_date_mrilist['PHASE'].tolist()[0]]
            index +=1            

    ###T1#################################################################################################        
            if len(t1scans) > 0:
                notacce = t1scans.loc[t1scans['T1ACCE'] == 0]
                yesacce = t1scans.loc[t1scans['T1ACCE'] == 1]

                if len(notacce) == 0:
                    t1uid=sort_uids(yesacce, "biggest") #return biggest UID
                    ist1acce='Y'
                else: 
                    t1uid = sort_uids(notacce) #return smallest UID is default in function
                    ist1acce='N'

                notacce_t1_uids = ";".join(map(str, notacce['IMAGEUID'].tolist()))
                yesacce_t1_uids = ";".join(map(str, yesacce['IMAGEUID'].tolist()))
            else:
                #There aren't currently any sessions with a missing T1 but present T2, so this else clause is never triggered. 
                t1uid, ist1acce, notacce, notacce_t1_uids, yesacce, yesacce_t1_uids = [None,None,None,None,None,None]
                
    ###T2#################################################################################################  
            if len(t2scans) > 0:
                t2uid = sort_uids(t2scans, "biggest")
                allt2uids = ";".join(map(str, t2scans['IMAGEUID'].tolist()))
            else: 
                t2uid, allt2uids = [None,None]
                
    ###Add to new dataframe###############################################################################
            datalisttoadd=[t1uid,ist1acce,t2uid,len(notacce),notacce_t1_uids,
                        len(yesacce),yesacce_t1_uids,len(t2scans),allt2uids]

            outputdf.loc[
                (outputdf['RID'] == subject) & (outputdf['SMARTDATE'] == date),
                    ['IMAGEUID_T1','T1ISACCE', 'IMAGEUID_T2', 'NT1NONEACCE','IMAGEUID_T1NONEACCE', 
                    'NT1ACCE', 'IMAGEUID_T1ACCE', 'NT2','IMAGEUID_T2ALL']
                        ] = datalisttoadd

    alloutput = outputdf.merge(mrimeta_df_small, how='left',on=['RID','SMARTDATE'])
    alloutput['RID'] = alloutput['RID'].astype(int)
    alloutput.info()

    alloutput.to_csv(os.path.join(datasetup_directories_path["uids"],filenames['uids']['mri']),header=True,index=False)
    return


def create_pet_uid_list():
    petmeta_df = pd.read_csv(os.path.join(datasetup_directories_path["ida_study_datasheets"],pet_meta_list))
    # print(petmeta_df.head())
    pettype_column_dict = {0:'fdg', 1:'amy', 2:'tau'}
    for key in pettype_column_dict:
        logging.info(f"Datasetup.py/function create_pet_uid_list is collating data for {pettype_column_dict[key]}")
        outputdf=pd.DataFrame()
        petmeta_one_scantype = petmeta_df.loc[petmeta_df['PETTYPE'] == key]

        for subject in petmeta_one_scantype['RID'].unique():
            this_subject = petmeta_one_scantype.loc[petmeta_one_scantype['RID'] == subject]
            dates = this_subject['SMARTDATE'].unique()
            for date in dates: 
                match = petmeta_one_scantype.loc[(petmeta_one_scantype['RID']== subject) & (petmeta_one_scantype['SMARTDATE'] == date) & (petmeta_one_scantype['RIGHTONE'] == 1)]
                if len(match) == 0:
                    continue
                else:
                    outputdf = pd.concat([outputdf,match],ignore_index = True)

        outputdf.drop(columns=['Orig_Proc','VISIT', 'SCANDATE','SMARTDATESRC','PETTYPE','RIGHTONE'],inplace=True)
        outputdf.rename(columns={"SUBJECT":'ID'},inplace=True)
        outputdf.columns = outputdf.columns.str.upper()
        querymergedf = outputdf[['RID', 'ID', 'VISCODE', 'VISCODE2', 'PHASE', 'SMARTDATE', 'SEQUENCE',
                                'STUDYID', 'SERIESID', 'IMAGEID']]
        # print(querymergedf.info())
        # print(querymergedf.head())
        querymergedf.to_csv(os.path.join(datasetup_directories_path["uids"],filenames["uids"][pettype_column_dict[key]]),header=True,index=False)

    return


def create_tau_anchored_uid_list():
    #need tau, amy, mri uid csvs
    mris = pd.read_csv("/project/wolk/ADNI2018/analysis_input/20230731_processing_status/mri_processing_status.csv")
    amys = pd.read_csv("/project/wolk/ADNI2018/analysis_input/20230731_processing_status/amy_processing_status.csv")
    taus = pd.read_csv("/project/wolk/ADNI2018/analysis_input/20230731_processing_status/tau_processing_status.csv")
    
    # mris = pd.read_csv(os.path.join(datasetup_directories_path['uids'],filenames["uids"]["mri"]))
    # amys = pd.read_csv(os.path.join(datasetup_directories_path['uids'],filenames["uids"]["amy"]))
    # taus = pd.read_csv(os.path.join(datasetup_directories_path['uids'],filenames["uids"]["tau"]))
    
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
    
    outputdf.to_csv("/project/wolk/ADNI2018/analysis_input/20230731_processing_status/anchored_uids.csv",index=False,header=True)
    # outputdf.to_csv(os.path.join(datasetup_directories_path["uids"],filenames["uids"]["anchored"]),index=False,header=True)


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


def reformat_date_datetime_to_dash(df):
    # YYYY-MM-DDTHH:MM:SSZ to M/D/YY
    datecols = [col for col in df.columns if 'DATE.' in col]
    for index, row in df.iterrows():
        for column in datecols:
            YMDlist=row[column].split('-')
            df.at[index,column]=YMDlist[0] + "-" + YMDlist[1] + "-" + YMDlist[2][0:2]
    return df


def identify_new_scans(new_uids_csv,old_filelocs_csv,scantype):
    #compare output of create_{scantype}_uid_list function to previous fileloc list
    new_uids_df = pd.read_csv(os.path.join(datasetup_directories_path['uids'],new_uids_csv))
    old_filelocs_df = pd.read_csv(os.path.join(fileloc_directory_previousrun,old_filelocs_csv),sep="\t")
    # print(new_uids_df.info())
    # print(new_uids_df.head())
    # print(old_filelocs_df.info())
    # print(old_filelocs_df.head())

    #pet fileloc tsv's made by Long & Sandy use M/D/YY dates, convert to dash
    if scantype == 'amy' or scantype == 'fdg' or scantype == 'tau':
        old_filelocs_df = reformat_date_slash_to_dash(old_filelocs_df)

    if scantype == 'anchored':
        old_filelocs_df = reformat_date_datetime_to_dash(old_filelocs_df)

    #fix MRI uid col data types
    if scantype == 'mri':
        old_filelocs_df['IMAGEUID_T1'] =  old_filelocs_df['IMAGEUID_T1'].astype(str)
        old_filelocs_df['IMAGEUID_T2'] =  old_filelocs_df['IMAGEUID_T2'].astype(str)
    
    if scantype == 'anchored':
        for index,row in new_uids_df.iterrows():
            id = row['ID']
            taudate_new = row['SMARTDATE.tau']
            amydate_new = row['SMARTDATE.amy']
            mridate_new = row['SMARTDATE.mri']

            match_in_old = old_filelocs_df.loc[(old_filelocs_df['ID'] == id) 
                                                & (old_filelocs_df['SMARTDATE.tau'] == taudate_new)
                                                & (old_filelocs_df['SMARTDATE.amy'] == amydate_new)
                                                & (old_filelocs_df['SMARTDATE.mri'] == mridate_new)]
            # print(len(match_in_old))

            if len(match_in_old) == 1:
                # print("One match")
                tauuid_new = str(row['IMAGEID.tau']).split('.')[0]
                tauuid_old = str(match_in_old['IMAGEID.tau'].values.tolist()[0])
                amyuid_new = str(row['IMAGEID.amy']).split('.')[0]
                amyuid_old = str(match_in_old['IMAGEID.amy'].values.tolist()[0])
                mriuid_new = str(row['IMAGEUID_T1.mri']).split('.')[0]
                mriuid_old = str(match_in_old['IMAGEUID_T1.mri'].values.tolist()[0])

                if tauuid_new == tauuid_old and amyuid_new == amyuid_old and mriuid_new == mriuid_old:
                    new_uids_df.at[index,f"NEW_{scantype}"] = 0 
                    # print("already processed")
                else:
                    logging.debug(f"{id}:{taudate_new}:{scantype}:Different uid selected from adni csv data")
                    new_uids_df.at[index,f"NEW_{scantype}"] = 3

            elif len(match_in_old) < 1:
                logging.info(f"{id}:{taudate_new}:{scantype}:New scan to process")
                new_uids_df.at[index,f"NEW_{scantype}"] = 1
            else:
                logging.debug(f"{id}:{taudate_new}:{scantype}:Duplicate entries in previous uid.csv")
                new_uids_df.at[index,f"NEW_{scantype}"] = 4
    
    else:
        for index,row in new_uids_df.iterrows():
            id = row['ID']
            scandate = row['SMARTDATE']
            # if "FIELD_STRENGTH" in columns:
            #     if row['FIELD_STRENGTH'] != "3T":
            #         continue
            # else:
                # print(f"ID: {id}, date: {scandate}")
                #find each row from newuid.csv in olduid.csv
            match_in_old = old_filelocs_df.loc[(old_filelocs_df['ID'] == id) & (old_filelocs_df['SMARTDATE'] == scandate)]
            
            if scantype == 'mri': #MRI csvs
                uid_comparison_data = {"T1":[],"T2":[]}    
            else: #PET csvs
                uid_comparison_data = {"PET":[]}
            
            for key in uid_comparison_data:
                if len(match_in_old) == 1: 
                #this id,scandate already has processing record, double-check the UIDs are the same in old & new 
                    if key == "T1":
                        newuid = str(row['IMAGEUID_T1']).split('.')[0]
                        olduid = match_in_old['IMAGEUID_T1'].values.tolist()[0].split(".")[0]
                        filepath_from_old = match_in_old['FINALT1NIFTI'].values.tolist()[0]
                        uid_comparison_data['T1'] = [newuid,olduid,filepath_from_old]
                    elif key == "T2":
                        newuid = str(row['IMAGEUID_T2']).split('.')[0]
                        olduid = match_in_old['IMAGEUID_T2'].values.tolist()[0].split(".")[0]
                        filepath_from_old = match_in_old['FINALT2NIFTI'].values.tolist()[0]
                        uid_comparison_data['T2'] = [newuid,olduid,filepath_from_old]
                    elif key == "PET":
                        newuid = str(row['IMAGEID']).split('.')[0]
                        olduid = str(match_in_old['IMAGEID'].values.tolist()[0])
                        filepath_from_old = match_in_old["FILELOC"].values.tolist()[0]
                        uid_comparison_data['PET'] = [newuid,olduid,filepath_from_old]

                    # print(uid_comparison_data)
                    if uid_comparison_data[key][0] == uid_comparison_data[key][1]:
                        if uid_comparison_data[key][2]:
                            new_uids_df.at[index,f"NEW_{key}"] = 0 
                            # print("already processed")
                        else:
                            logging.debug(f"{id}:{scandate}:{key}:Previous nifti conversion failed")
                            new_uids_df.at[index,f"NEW_{key}"] = 2
                    else:
                        logging.debug(f"{id}:{scandate}:{key}:Different uid selected from adni csv data")
                        new_uids_df.at[index,f"NEW_{key}"] = 3

                elif len(match_in_old) < 1:# and scandate > "2022-01-01": 
                    ##TODO:check for dicom? scandate clause holding for now;; some dicoms aren't downloaded?
                    logging.info(f"{id}:{scandate}:{key}:New scan to process")
                    new_uids_df.at[index,f"NEW_{key}"] = 1
                else:
                    logging.debug(f"{id}:{scandate}:{key}:Duplicate entries in previous uid.csv")
                    new_uids_df.at[index,f"NEW_{key}"] = 4
        
    # print(new_uids_df.head())
    # print(new_uids_df.info())
    new_uids_df.to_csv(os.path.join(datasetup_directories_path["processing_status"], filenames['processing_status'][scantype]), index=False, header=True)


def main():
    registry_df = pd.read_csv(os.path.join(datasetup_directories_path["ida_study_datasheets"],registry_csv))

    # for csvfile in original_ida_datasheets:
    #     preprocess_new(csvfile, registry=registry_df)

    ##TODO:fix IMAGEUID_ spelling error in old mri sheets
    # create_mri_uid_list()
    # create_pet_uid_list() 
    create_tau_anchored_uid_list()

    # for key in filenames["uids"]:
    #     if "smalltest" in filenames["uids"][key]:
    #         continue ##skipping test data csv for now
    #     else:
    #         previous_fileloc_csv = [x for x in previous_filelocs_csvs if key in x]
    #         if previous_fileloc_csv: #in case of no match
    #             identify_new_scans(filenames['uids'][key], previous_fileloc_csv[0], key)

    # identify_new_scans("/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230628_uids/mri_uids.csv",\
    #     "/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20221017_filelocs/mri3TListWithNIFTIPath_10172022.tsv")


main()