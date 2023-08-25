#!/usr/bin/env python

import pandas as pd

mrilist=pd.read_csv("/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230731_ida_study_datasheets/MRILIST_12Jun2023.csv")
print(mrilist.info())

#just the rows with "FLAIR" in seq
flairs_df = mrilist.loc[mrilist['SEQUENCE'].str.contains("FLAIR")] 
print(flairs_df.info())
print(flairs_df.head())

#only one FLAIR for each subject + scandate

checkdupes = flairs_df[flairs_df.duplicated(subset=['SUBJECT','SCANDATE'],keep = False)]
print(checkdupes.info())