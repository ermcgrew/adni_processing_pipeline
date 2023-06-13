#!/usr/bin/bash python3

import pandas as pd
import os
import csv
from processing import adni_data_dir

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


def preprocess_new(csvfilename, source_directory, registry=None):
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
    df = pd.read_csv(os.path.join(source_directory, csvfilename))

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
    df.to_csv(os.path.join(source_directory, csvfilename.replace('.csv', '_clean.csv')),
                index=False, quoting=csv.QUOTE_ALL,
                date_format='%Y-%m-%d')


def merge_for_mri(clean_csvlist, source_directory):
    mrimeta_df = pd.read_csv(os.path.join(source_directory,clean_csvlist[0]))
    mrilist_df = pd.read_csv(os.path.join(source_directory,clean_csvlist[1]))
    print(mrimeta_df.head())
    print(mrilist_df.head())




    return


##programmatic way to get csvs--grab names from specific directory on cluster
registry_csv = "REGISTRY_12Jun2023.csv"
registry_df = pd.read_csv(os.path.join(adni_data_dir,registry_csv))

csvlist = ["MRI3META_12Jun2023.csv","MRILIST_12Jun2023.csv"]
clean_csvlist = [csvfile.replace('.csv', '_clean.csv') for csvfile in csvlist]

for csvfile in csvlist:
    preprocess_new(csvfile, adni_data_dir, registry=registry_df)

merge_for_mri(clean_csvlist, adni_data_dir)



