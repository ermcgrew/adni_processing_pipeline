#!/usr/bin/env python3

import logging
import pandas as pd
import os

pd.options.mode.chained_assignment = None

df = pd.read_csv("/project/wolk/ADNI2018/analysis_input/ADNI4_MRI_UIDS_CONVERSION_FILEPATHS_20240801.csv")

missing = df.loc[(pd.notnull(df['IMAGEUID_T2'])) & (df['T2_CONVERT_STATUS'] == -1)]
# print(missing.info())
# print(missing.head())
missing.to_csv("temp_missedT2s_toconvert.csv", index=False,header=True)