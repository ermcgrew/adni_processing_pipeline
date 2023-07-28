# adni_processing_pipeline

1. Run download_adni_dicoms.py from local machine to get dicoms from ida.loni.usc.edu and copy to cluster.
2. Manually download these csvs from ida.loni.usc.edu:
- Download/StudyData/Imaging/MR Image Acquisition/
  - 3T MRI Scan Information [ADNI1,GO,2,3] (MRI3META.csv)
  - MRI Scan Metadata Listing [ADNI1,GO,2,3] (MRILIST.csv)
- Download/StudyData/Imaging/PET Image Acquisition/
  - PET Metadata Listing [ADNI1,GO,2] (PET_META_LIST.csv)
- Download/StudyData/Enrollment/
  - Registry [ADNI1,GO,2,3] (REGISTRY.csv)
3. On cluster, run command from directory /ADNI2018/analysis_input/adni_data_setup_csvs/: 
`mkdir YYYYMMDD_ida_study_datasheets YYYYMMDD_merged_data_uids YYYYMMDD_uids_process_status YYYYMMDD_filelocs` 
4. copy downloaded data csvs to YYYYMMDD_ida_study_datasheets
5. run app.py on cluster