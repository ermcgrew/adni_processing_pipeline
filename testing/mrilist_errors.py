import pandas as pd

mriuid = pd.read_csv("/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230731_uids/mri_uids.csv")
# print(mriuid.head())
# print(mriuid.info()) #len 8910

oldmrilist = pd.read_csv('/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20221017_merged_data_uids/MRILIST_T1T2_10172022.csv')
# print(oldmrilist.head())
# print(oldmrilist.info()) #len 7392

# print(oldmrilist.columns)

oldmrilist.rename(columns={"IMAGUID_T1":"IMAGEUID_T1", "IMAGUID_T2":"IMAGEUID_T2"},inplace=True)
#Null viscodes comparison
# print(mriuid.loc[pd.isnull(mriuid['VISCODE'])])
    #1366 rows
# print(oldmrilist.loc[pd.isnull(oldmrilist['VISCODE'])])
    #0 rows


newtest = mriuid.loc[mriuid['RID'] == 30]
# print(newtest)
# print(newtest.iloc[0])
# print(newtest.iloc[1])
oldtest = oldmrilist.loc[oldmrilist['RID'] ==30]
# print(oldtest)
# print(oldtest['SMARTDATE'])
    #old version doesn't include dates with NaN viscode/viscode2

# print(len(oldmrilist)) #7392
new_nonulls = mriuid.loc[pd.notnull(mriuid['VISCODE'])]
# print(new_nonulls)
# print(len(new_nonulls)) #7544
new_nonulls2 = mriuid.loc[pd.notnull(mriuid['FIELD_STRENGTH'])]
# print(new_nonulls2)
# print(len(new_nonulls2)) #7544



olddates = sorted(oldmrilist['SMARTDATE'].unique().tolist())
# print(olddates[-1:]) #['2022-09-06']


newdates=sorted(new_nonulls2['SMARTDATE'].unique().tolist())
# print(newdates[-1:])


new_nonulls_datefilter = new_nonulls2.loc[new_nonulls2['SMARTDATE'] <= '2022-09-06'] 
# print(new_nonulls_datefilter)
# print(len(new_nonulls_datefilter)) #7477

# new_nonulls_datefilter['SOURCE'] = "NEW"
oldmrilist['SOURCE'] = "OLD"

checking = pd.concat([oldmrilist,new_nonulls_datefilter],ignore_index=True)
# print(checking.head())
# print(checking[checking.duplicated(subset=['RID','SMARTDATE'],keep=False)])
nooverlap = checking.drop_duplicates(subset=['RID','SMARTDATE'],keep=False)
# print(nooverlap['SOURCE'].value_counts())
# nooverlap.to_csv("testing.csv",index=False,header=True)



adnimri = pd.read_csv("/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230731_ida_study_datasheets/MRILIST_12Jun2023_clean.csv")
# print(adnimri.head())
# print(adnimri.info())

adnimri = adnimri.loc[adnimri['MAGSTRENGTH'] != 1.5]
# print(adnimri)




testlist = pd.read_csv("/project/wolk/ADNI2018/scripts/adni_processing_pipeline/testing/new_create_mri_list_output.csv")
# print(testlist.info())


date_filtered = testlist.loc[testlist['SMARTDATE'] <= '2022-09-06']
date_filtered['SOURCE'] = 'NEW'
print(len(date_filtered.columns))
print(len(oldmrilist.columns))
combo = pd.concat([date_filtered,oldmrilist],ignore_index=True)
# print(combo.info())

# print(combo[combo.duplicated(subset=['RID','SMARTDATE'],keep=False)])
mismatch = combo.drop_duplicates(subset=['RID','SMARTDATE'],keep=False)
# print(mismatch['SOURCE'].value_counts())
# mismatch.to_csv("testing2.csv",index=False,header=True)

onlynew=mismatch.loc[mismatch['SOURCE'] == "NEW"]
onlyold =mismatch.loc[mismatch['SOURCE'] == "OLD"]
onlyoldsubs = onlyold['RID'].unique().tolist()
# for index, row in onlynew.iterrows():
#     if row['RID'] in onlyoldsubs:
#         print('subject match')
#         print(row)
#         print(onlyold.loc[onlyold['RID'] == row['RID']])

missinguid=pd.read_csv("/project/wolk/ADNI2018/scripts/adni_processing_pipeline/testing/UID_not_in_mrilist_fromPenn.csv")
# print(missinguid.head())
missingsubs = missinguid['RID'].unique().tolist()
# for index, row in onlynew.iterrows():
    # if row['RID'] in missingsubs:
    #     print(row['RID'])
    #     print(row['SMARTDATE'])
    #     print(missinguid.loc[missinguid['RID'] == row['RID']])