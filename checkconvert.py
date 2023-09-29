#!/usr/bin/env python

from processing import MRI
import pandas as pd
import os

csv="/project/wolk/ADNI2018/analysis_output/2023_09_29/convert_failed_2023_09_29.txt"
df = pd.read_csv(csv, sep=":")
df.head()

for index,row in df.iterrows():
    id = row['ID']
    scandate = row['DATE']
    session = MRI(id,scandate)
    mod = str(row['MOD']).split("_")[0]
    # print(mod)
    if mod == 't1':
        # print(session.t1nifti)
        if os.path.exists(session.t1nifti):
            print("T1 acutally there")
        else:
            print("CONVERT DID FAIL")
    else:
        # print(session.t2nifti)
        if os.path.exists(session.t2nifti):
            print("T2 acutally there")
        else:
            print(f"CONVERT DID FAIL for {session.id}/{session.scandate} {session.t2nifti}")
