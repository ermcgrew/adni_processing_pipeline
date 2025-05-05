#!/usr/bin/env python3

import pandas as pd

oldlistcsv="/project/wolk/ADNI2018/analysis_input/20241104_processing/20241104_uids/allADNI_tauanchored_2024_11_06T16_02_36.csv"
olddf=pd.read_csv(oldlistcsv)
# print(olddf.info())

newlistcsv="/project/wolk/ADNI2018/analysis_input/20250204_processing/20250204_uids/allADNI_tauanchored_2025_02_17T11_33_41.csv"
newdf=pd.read_csv(newlistcsv)
# print(newdf.info())

olddf['SOURCE'] = 'old'
newdf['SOURCE'] = 'new'

colstokeep=[col for col in newdf.columns if "SCANDATE" in col or col == 'ID' or col == 'SOURCE']
olddfsm=olddf[colstokeep]
olddfsm.info()
newdfsm=newdf[colstokeep]
newdfsm.info()

combo = pd.concat([olddfsm,newdfsm])
diffpairs = combo.drop_duplicates(subset=[col for col in colstokeep if col != "SOURCE"],keep=False)
diffpairs.info()
print(diffpairs['SOURCE'].value_counts())

newpairs = diffpairs.loc[diffpairs['SOURCE'] == "new"].reset_index(drop=True).drop(columns=['SOURCE'])
newpairs.info()
newpairs.to_csv("/project/wolk/ADNI2018/analysis_input/20250204_processing/20250204_uids/new_tauanchored_pairs_20250313.csv",index=False,header=True)