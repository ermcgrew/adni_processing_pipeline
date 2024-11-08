# PICSL's MRI and PET processing pipeline for ADNI data

## Key files
- `config.py`: filepaths for data storage locations and some scripts. 
- `processing.py`: Defines MRI, PET, and MRI-PET reg classes, with attributes for storing strings of standard image filepaths and methods for individual steps of processing. 
- `app.py`: run script for all steps. See the 'Arguments/Parameters' section for options for each function in app.py.

## Instructions for use
### Get dicoms
1. Follow instructions in `/download_dicoms/download_dicoms_procedure.txt` to gather new scans from ida.loni.usc.edu database and get download links.
2. Download a csv of in each collection BEFORE running any dicom downloads. The 'null' value in the 'Downloaded' column is used to identify new scans in `data_setup.py`. 
3. Add download https strings to a copy of `/download_dicoms/download_adni_dicoms.py` on your personal computer (cannot download directly to the bscsub cluster) to download dicoms from ida.loni.usc.edu. 
4. Use scp or rsync to move files from personal computer to cluster.
5. Run command `python app.py unpack_dicoms <options>` to unzip dicoms and rsync between cluster locations.

### Get data sheets
1. Manually download these csvs from ida.loni.usc.edu:
- Search/Image Metadata/MR Image Acquisition/MRI3META (MRI3META.csv)
- Search/Image Metadata/PET Image Acquisition/AMYMETA (AMYMETA.csv)
- Downloads/Imaging/PET Image Acquisition/Tau PET Scan Information (TAUMETA.csv)
2. On cluster, run script `dir_setup.py -d YYYYMMDD` to create folders for all ADNI data sheets and uid lists for this round of processing.  
3. Copy downloaded data sheet csvs to `/YYYYMMDD_ida_study_datasheets` and downloaded collection csvs to `/YYYYMMDD_collections_csvs`
4. Get csvs of all mri and pet files and a csv of tau-anchored dates using command: `python app.py data_setup -d YYYYMMDD`

### Processing
1. Convert all new images to nifti using command: `python app.py convert_symlink <options>`
- Can use either 'ADNI4' or 'allADNI' csv outputs from data_setup as input to convert_symlink, both have new sessions marked.
2. Run image processing and statistics steps using command: `python app.py image_processing <options>`
- Recommend using the csv output of convert_symlink as input to image_processing, it will contain all new sessions that need to be processed.
3. Compile all statistics using command `python app.py final_data_sheets <options>`
4. Collect QC files for reviewers using command `python app.py collect_qc <options>`

## Arguments/Parameters for app.py functions
- `unpack_dicoms`: 
  - d, --date, required, Date in format three-letter abbreviationYYYY, matching the zip file name.
- `data_setup`:
  - d, --date, required, Date in format YYYYMMDD that matches date on processing folders in `/project/wolk/ADNI2018/analysis_input/`.
- `convert_symlink`
  - t, --scantype, choices=["amy","tau","mri"], run conversion to nifti for tau, amy, or mri dicoms.
  - i, --inputcsv, required csv with format: column 'ID' in format 999_S_9999, column 'SMARTDATE.(mri|amy|tau)' in format YYYY-MM-DD, column 'NEW.T1|T2|FLAIR|amy|tau' in format 1 if true, 0 if false, and column 'IMAGEUID.T1|T2|FLAIR|amy|tau' in format '999999'
  - o, --outputcsv, optional filepath for output csv with conversion status. Default csv save location is inputcsv filename + 
  'processed'.
- `image_processing`
  - -s, --steps, choices listed in variable processing_steps in config.py, mutually exclusive with -a option, set which processing step(s) to run.
  - a, --all_steps, mutually exclusive with -s option, run all processing steps.
  - c, --csv, required csv of sessions to process. Format must be column 'ID' as 999_S_9999 and column 'SMARTDATE.mri' as YYYY-MM-DD. If processing pet scans, include columns 'SMARTDATE.tau' and 'SMARTDATE.amy', both as YYYY-MM-DD.
  - d, --dry_run, run program but don't submit any jobs.
- `final_data_sheets`
  - m, --mode, required, choices = ["pet", "structure", "ashst1", "ashst2","wmh"], select which type(s) of stats to compile into a final sheet.
  - w, --wait, run with queuewatch to wait for all image processing to complete.
- `longitudinal_processing`
  - c, --csv, required csv of sessions to run. Format must be column 'ID' as 999_S_9999 and column 'SMARTDATE.mri' as YYYY-MM-DD.
  - d, --dry_run, Run program but don't submit any jobs.
- `collect_qc`
  - c, --csv, required csv of sessions to gather files from. Format must be column 'ID' as 999_S_9999 and column 'SMARTDATE.mri' as YYYY-MM-DD. If qc_type is Amy_MRI_reg or Tau_MRI_reg, include column 'SCANDATE.tau|amy' as YYYY-MM-DD.
  - d, --dry_run, run program to get log file with expected files to be copied but does not create any QC folders or files or copy any files.
  - t, --qc_type, required, choices = ["ASHST1", "ASHST2", "Amy_MRI_reg", "Tau_MRI_reg", "wbseg", "thickness"], select which type of QC to collect files for.
