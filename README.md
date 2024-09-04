# PICSL's MRI and PET processing pipeline for ADNI data

## Key files
- `config.py`: filepaths for data storage locations and some scripts. 
- `processing.py`: Defines MRI, PET, and MRI-PET reg classes, with attributes for storing strings of standard image filepaths and methods for individual steps of processing. 
- `app.py`: run script for all steps. See the 'Arguments/Parameters' section for options for each function in app.py.

## Instructions for use
### Get dicoms
1. Follow instructions in `/download_dicoms/download_dicoms_procedure.txt` to gather new scans from ida.loni.usc.edu database and get download links.
2. Download a csv of the "not downloaded" files in each collection.
3. Add download https strings to a copy of `/download_dicoms/download_adni_dicoms.py` on your personal computer (cannot download directly to the bscsub cluster) to download dicoms from ida.loni.usc.edu. 
4. Use scp or rsync to move files from personal computer to cluster.
5. Run command `python app.py unpack_dicoms <options>` to unzip dicoms and rsync between cluster locations.

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
- `unpack_dicoms`: 
  - d, --date, required, Date in format three-letter abbreviationYYYY, matching the zip file name.
- `convert_symlink`
  - t,--single_type, choices=["amy","tau","mri"], mutually exclusive with -a option, run conversion to nifti for tau, amy, OR mri dicoms.
  - a, --all_types, mutually exclusive with -t option, run conversion to nifti for tau, amy, AND mri dicoms.
  - i, --inputcsv, if not using default csv with -t option, filepath of a csv with format: column 'ID' in format 999_S_9999, column 'SMARTDATE' in format YYYY-MM-DD, column 'NEW_T1|T2|FLAIR|PET' in format 1 if true, 0 if false, and column 'IMAGEUID_T1|T2|FLAIR' (mri) or 'IMAGEID' (pet) in format '999999'
  - o,--outputcsv, if not using default csv with -t option, filepath for output csv with conversion status.
- `image_processing`
  - -s, --steps, choices listed in variable processing_steps in config.py, mutually exclusive with -a option, set which processing step(s) to run.
  - a, --all_steps, mutually exclusive with -s option, run all processing steps.
  - c, --csv, optional csv of sessions to run if not using default csv produced by datasetup.py. Format must be column 'ID' as 999_S_9999 and column 'SMARTDATE.mri' as YYYY-MM-DD. If processing pet scans, include columns 'SMARTDATE.tau' and 'SMARTDATE.amy', both as YYYY-MM-DD.
  - d, --dry_run, run program but don't submit any jobs.
- `final_data_sheets`
  - m, --mode, required, choices = ["pet", "structure", "ashst1", "ashst2","wmh"], select which type(s) of stats to compile into a final sheet.
  - w, --wait, run with queuewatch to wait for all image processing to complete.
- `longitudinal_processing`
  - c, --csv, Required csv of sessions to run. Format must be column 'ID' as 999_S_9999 and column 'SMARTDATE.mri' as YYYY-MM-DD.
  - d, --dry_run, Run program but don't submit any jobs.