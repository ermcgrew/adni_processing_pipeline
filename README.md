# adni_processing_pipeline

Run download_adni_dicoms.py from local machine to get dicoms from ida.loni.usc.edu and copy to cluster.
Manually download all necessary data csvs from ida.loni.usc.edu. (**make list)
On cluster, run command from directory /ADNI2018/analysis_input/adni_data_setup_csvs/: 
`mkdir YYYYMMDD_ida_study_datasheets YYYYMMDD_merged_data_uids YYYYMMDD_uids_process_status YYYYMMDD_filelocs` 
copy downloaded data csvs to YYYYMMDD_ida_study_datasheets