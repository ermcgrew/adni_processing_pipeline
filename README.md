# PICSL's MRI and PET processing pipeline for ADNI data

## Key files
- `config.py`: filepaths for data storage locations and some scripts. 
- `processing.py`: Defines MRI, PET, and MRI-PET reg classes, with attributes for storing strings of standard image filepaths and methods for individual steps of processing. 
- `app.py`: run script for all steps. See the 'Arguments/Parameters' section for options for each function in app.py.

## Instructions for use
### Get dicoms
1. Follow instructions in `/download_dicoms/download_dicoms_procedure.txt` to gather new scans from ida.loni.usc.edu database and get download links.
2. Add download https strings to a copy of `/download_dicoms/download_adni_dicoms.py` on your personal computer (cannot download directly to the bscsub cluster) to download dicoms from ida.loni.usc.edu. 
3. Use scp or rsync to move files from personal computer to cluster.
4. Run command `python app.py unpack_dicoms <options>` to unzip dicoms and rsync between cluster locations.

### Get data sheets
1. Manually download these csvs from ida.loni.usc.edu:
- Download/StudyData/Imaging/MR Image Acquisition/
  - 3T MRI Scan Information [ADNI1,GO,2,3] (MRI3META.csv)
  - MRI Scan Metadata Listing [ADNI1,GO,2,3] (MRILIST.csv)
- Download/StudyData/Imaging/PET Image Acquisition/
  - PET Metadata Listing [ADNI1,GO,2] (PET_META_LIST.csv)
- Download/StudyData/Enrollment/
  - Registry [ADNI1,GO,2,3] (REGISTRY.csv)
2. On cluster, run command from directory /ADNI2018/analysis_input/adni_data_setup_csvs/: 
`mkdir YYYYMMDD_ida_study_datasheets YYYYMMDD_merged_data_uids YYYYMMDD_uids_process_status YYYYMMDD_filelocs` 
3. Copy downloaded csvs to YYYYMMDD_ida_study_datasheets
4. Get csvs of all mri and pet files and a csv of tau-anchored dates using command: `python app.py data_setup`

### Processing
1. Convert all new images to nifti using command: `python app.py convert_symlink <options>`
2. Run image processing and statistics steps using command: `python app.py image_processing <options>`
3. Compile all statistics using command `python app.py final_data_sheets <options>`


## Arguments/Parameters for app.py functions


## test change
this is a test change to make sure 