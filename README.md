# PICSL's ADNI MRI and PET processing pipeline

## Key files
- `config.py`: filepaths for data storage locations and some scripts. 
- `processing.py`: Use class attributes for storing image filepaths. Use class methods for individual steps of processing. 
- `app.py`: run script for all steps. See the 'Arguments/Parameters' section for options for each function in app.py.

## Instructions for use
### Get dicoms
1. Run `download_adni_dicoms.py` from local machine to get dicoms from ida.loni.usc.edu and scp to cluster.
2. Unzip dicoms & rsync using command: `python app.py unpack_dicoms <options>`

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
