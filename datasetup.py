# !/usr/bin/env python

import pandas as pd
import os
import csv
import logging
import subprocess
from processing import adni_data_dir, csvs_dir, csvs_dirs_dict

#from vergnet_db/csv_preprocessing.py
# Helper function to set rid, viscode, phase in MRI/PET tables
def fixup_imaging_csv(df):
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

#from vergnet_db/csv_preprocessing.py
# Helper function to set RID, phase for MRI/PET tables
def set_rid_and_phase(df, i, row):
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

#from vergnet_db/csv_preprocessing.py
def preprocess_new(csvfilename, registry=None):
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
    df = pd.read_csv(os.path.join(csvs_dirs_dict["ida_study_datasheets"], csvfilename))
    print(f"Reading dataframe: {csvfilename}")

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
            ###################
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

    print(f"writing {csvfilename} to file")
    # Write to file
    df.to_csv(os.path.join(csvs_dirs_dict["ida_study_datasheets"], csvfilename.replace('.csv', '_clean.csv')),
                index=False, quoting=csv.QUOTE_ALL,
                date_format='%Y-%m-%d')


def get_uids(dataframe, which="smallest"):
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
    

def merge_for_mri(mri_csvs):
    meta_csv = [file for file in mri_csvs if "META" in file][0]
    mrilist_csv = [file for file in mri_csvs if "LIST" in file][0]
    mrimeta_df = pd.read_csv(os.path.join(csvs_dirs_dict["ida_study_datasheets"],meta_csv))
    mrilist_df = pd.read_csv(os.path.join(csvs_dirs_dict["ida_study_datasheets"],mrilist_csv))
    
    print(mrimeta_df.head())
    print(mrilist_df.head())
    # return

    ## columns to use from each df:
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

    print(f"total number of subjects is {len(newtotalsubs)}")

    outputdf=pd.DataFrame()
    index = 0
    for subject in newtotalsubs:
        subject_mrilist = mrilist_df_small.loc[mrilist_df_small['RID'] == subject]
    #     print(f"Subject {subject} has {matches} rows in mrilist")
        dates = subject_mrilist['SMARTDATE'].unique()
    #     print(f"Subject {subject} has {dates} scans in mrilist")
        for date in dates: 
            single_date_mrilist = subject_mrilist.loc[subject_mrilist['SMARTDATE'] == date]
            t1scans=single_date_mrilist.loc[single_date_mrilist['MRITYPE']== 0]
            t2scans=single_date_mrilist.loc[single_date_mrilist['MRITYPE']== 1]

            if len(t1scans) == 0 and len(t2scans) == 0:
                print(f"No scans for {subject} {date} with index {index} Loop should do continue")
                continue
                
    #         print(f"Index to outputdf {index} {subject} {date}")
            outputdf.loc[index,['RID','SMARTDATE','ID','PHASE']] = [int(subject),date,
                                                        single_date_mrilist['SUBJECT'].tolist()[0],
                                                        single_date_mrilist['PHASE'].tolist()[0]]
            index +=1            

    ###T1#################################################################################################        
            if len(t1scans) > 0:
                print(f"Finding t1 scans for {subject} {date}")
                notacce = t1scans.loc[t1scans['T1ACCE'] == 0]
                yesacce = t1scans.loc[t1scans['T1ACCE'] == 1]

                if len(notacce) == 0:
    #                 print(f"No un-accelerated T1 scans, use an accel t1 as main")
                    t1uid=get_uids(yesacce, "biggest") #return biggest UID
                    ist1acce='Y'
                else: 
                    t1uid = get_uids(notacce) #return smallest UID is default in function
                    ist1acce='N'

                notacce_t1_uids = ";".join(map(str, notacce['IMAGEUID'].tolist()))
                yesacce_t1_uids = ";".join(map(str, yesacce['IMAGEUID'].tolist()))
            else:
                #There aren't currently any sessions with a missing T1 but present T2, 
                #so this else clause is never triggered. 
                t1uid, ist1acce, notacce, notacce_t1_uids, yesacce, yesacce_t1_uids = [None,None,None,None,None,None]
                
    ###T2#################################################################################################  
            if len(t2scans) > 0:
                print(f"There is a T2 scan for {subject} {date}")
                t2uid = get_uids(t2scans, "biggest")
                allt2uids = ";".join(map(str, t2scans['IMAGEUID'].tolist()))
            else: 
                t2uid, allt2uids = [None,None]
                
    ###Add to new dataframe###############################################################################
            datalisttoadd=[t1uid,ist1acce,t2uid,len(notacce),notacce_t1_uids,
                        len(yesacce),yesacce_t1_uids,len(t2scans),allt2uids]

            outputdf.loc[
                (outputdf['RID'] == subject) & (outputdf['SMARTDATE'] == date),
                    ['IMAGUID_T1','T1ISACCE', 'IMAGUID_T2', 'NT1NONEACCE','IMAGEUID_T1NONEACCE', 
                    'NT1ACCE', 'IMAGEUID_T1ACCE', 'NT2','IMAGEUID_T2ALL']
                        ] = datalisttoadd

    outputdf.info()

    alloutput = outputdf.merge(mrimeta_df_small, how='left',on=['RID','SMARTDATE'])
    alloutput.info()
    
    alloutput.to_csv(os.path.join(csvs_dirs_dict["merged_data_uids"],mri_uids),header=True,index=False)
    return


def identify_new_scans(new_uids_csv,old_uid_csv):
    #compare output of merge_for_mri function to previous mri_uid list
    old_uids_df = pd.read_csv(os.path.join(previous_fileloc_dir_fullpath,old_uid_csv),sep="\t")
    old_uids_df['IMAGEUID_T1'] =  old_uids_df['IMAGEUID_T1'].astype(str)
    old_uids_df['IMAGEUID_T2'] =  old_uids_df['IMAGEUID_T2'].astype(str)

    new_uids_df = pd.read_csv(os.path.join(csvs_dirs_dict["merged_data_uids"],new_uids_csv))
    for index,row in new_uids_df.iterrows():
        id = str(row['ID'])
        scandate = str(row['SMARTDATE'])

        #find each row from newuid.csv in olduid.csv
        match_in_old = old_uids_df.loc[(old_uids_df['ID'] == id) & (old_uids_df['SCANDATE'] == scandate)]
        if len(match_in_old) == 1:
            # check uids: T1
            if str(row['IMAGUID_T1']) == match_in_old['IMAGEUID_T1'].values.tolist()[0].split(".")[0]:
                new_uids_df.at[index,'NEW_currentdate'] = 0            
            else:
                logging.debug(f"{id}:{scandate}:New uid selected from adni csv data")
                new_uids_df.at[index,'NEW_currentdate'] = 2
            # check uids: T2
            if str(row['IMAGUID_T2']).split('.')[0] == match_in_old['IMAGEUID_T2'].values.tolist()[0].split(".")[0]:
                new_uids_df.at[index,'NEW_currentdate'] = 0            
            else:
                logging.debug(f"{id}:{scandate}:New uid selected from adni csv data")
                new_uids_df.at[index,'NEW_currentdate'] = 2
        elif len(match_in_old) < 1:
            logging.info(f"{id}:{scandate}:New scan to process")
            new_uids_df.at[index,'NEW_currentdate'] = 1
        else:
            logging.debug(f"{id}:{scandate}:Duplicate entries in previous uid.csv")
            new_uids_df.at[index,'NEW_currentdate'] = 2

    new_uids_df.to_csv(os.path.join(csvs_dirs_dict["uids_process_status"], mri_uids_processing), index=False, header=True)


### Set up variables for data locations
#list all directories with adni data setup sheets, get only those for newest date
all_csvs_dirs = os.listdir(csvs_dir)
all_csvs_dirs.sort(reverse = True)
csvs_dirs_list = all_csvs_dirs[0:4]

for key in csvs_dirs_dict:
    basename = [x for x in csvs_dirs_list if key in x][0]
    csvs_dirs_dict[key] = os.path.join(csvs_dir, basename)

#All csv's downloaded from ida.loni.usc.edu
csvlist = os.listdir(csvs_dirs_dict["ida_study_datasheets"])
clean_csvlist = [csvfile.replace('.csv', '_clean.csv') for csvfile in csvlist]

#registry file
registry_csv = [file for file in csvlist if "REGISTRY" in file][0]
registry_df = pd.read_csv(os.path.join(csvs_dirs_dict["ida_study_datasheets"],registry_csv))

#mri files to merge
csvs_mri_merge = [file for file in clean_csvlist if "MRI3META" in file or "MRILIST" in file]

#merged data csv names, join with csvs_dirs_dict["merged_data_uids"]
mri_uids = "mri_uids.csv"
tau_uids = "tau_uids.csv"
amy_uids = "amy_uids.csv"

##get previous filepath file for comparison to new uids
##TODO: use uids csv instead of filepath one?
previous_fileloc_dir_basename = [x for x in all_csvs_dirs[4:8] if "fileloc" in x][0]
previous_fileloc_dir_fullpath = os.path.join(csvs_dir,previous_fileloc_dir_basename)
previous_filelocs_csvs = os.listdir(previous_fileloc_dir_fullpath)
previous_mri_filelocs = [x for x in previous_filelocs_csvs if "MRI" in x][0]

#uids + processing status csv names, join with csvs_dirs_dict["uids_process_status"]
mri_uids_processing = "mri_uids_processing_status.csv"
tau_uids_processing = "tau_uids_processing_status.csv"
amy_uids_processing = "amy_uids_processing_status.csv"


def main():
    pass
    # for csvfile in csvlist:
    #     preprocess_new(csvfile, registry=registry_df)

    # merge_for_mri(csvs_mri_merge)

    # identify_new_scans(mriuids, previous_mri_filelocs)