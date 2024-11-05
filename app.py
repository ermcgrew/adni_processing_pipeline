#!/usr/bin/env python3

import argparse
import logging
import os
import pandas as pd
import subprocess
## Classes
from processing import MRI, AmyloidPET, TauPET, MRIPetReg
## variables
from config import *

## for raising argument errors
class ArgumentError(Exception):
    pass

## Symlinks zip files to /PUBLIC, unpack dicoms to /PUBLIC/ADNI, rsync /PUBLIC/ADNI with /PUBLIC/dicoms
def unpack_dicoms(date):
    #### zip files of new dicoms must already be added to cluster
    logging.info(f"Running organize_files.sh on zip file adni_dl_{date}")
    os.system(f"bsub -J '{current_date}_unzip_rsync' -o {log_output_dir}/{current_date_time}_unzip_rsync.txt \
        bash organize_files.sh {date}") 


## get UID & processing status lists for new batches of scans to process
def data_setup(date):
    #### adni spreadsheets must already be added to cluster
    os.system(f"bsub -J '{current_date}_datasteup' -o {log_output_dir}/{current_date_time}_datasetup.txt \
        python ./testing/new_datasetup.py -d {date}") 


## Convert dicom to nifti and symlink nifti to /dataset
def convert_symlink(single_type="", all_types=False, inputcsv="", outputcsv=""):
    for scantype in scantypes:
        if single_type == scantype or all_types == True and scantype != "anchored":
            if inputcsv:
                csv_to_read = inputcsv
            else:
                csv_to_read = os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status'][scantype])
        
            logging.info(f"Running dicom to nifti conversion and nifti symlink for scantype {scantype} sessions in csv {csv_to_read}")

            df=pd.read_csv(csv_to_read,index_col=False)

            if scantype == 'mri':
                df_newscans = df.loc[(df['NEW_T1'] == 1) | (df['NEW_T2'] == 1) | (df['NEW_FLAIR'] == 1 )].reset_index(drop = True)
            else:
                df_newscans = df.loc[(df['NEW_PET'] == 1)].reset_index(drop = True)

            ##Start converting dicom to nifti, line by line    
            for index,row in df_newscans.iterrows():
                print(f"Processing line {index + 1} of {len(df_newscans)}")
                subject = str(row['ID'])
                scandate = str(row['SMARTDATE'])
                if scantype == 'mri':
                    scan_to_process = MRI(subject,scandate)
                    uids={"T1": [str(row['IMAGEUID_T1']).split(".")[0], scan_to_process.t1nifti],
                          "T2": [str(row['IMAGEUID_T2']).split('.')[0], scan_to_process.t2nifti], 
                          "FLAIR": [str(row['IMAGEUID_FLAIR']).split('.')[0], scan_to_process.flair]}
                elif scantype == "amy":
                    scan_to_process = AmyloidPET(subject,scandate)
                    uids = {'AMY':[str(row["IMAGEID"]).split(".")[0], scan_to_process.amy_nifti]}
                elif scantype == 'tau':
                    scan_to_process = TauPET(subject,scandate)
                    uids = {'TAU':[str(row["IMAGEID"]).split(".")[0], scan_to_process.tau_nifti]}

                logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:{scantype}: Checking convert to nifti status.")

                for key in uids:
                    if uids[key][0] == "nan":
                        status="No dicom UID"
                        df_newscans.at[index,f'{key}_CONVERT_STATUS'] = -1 
                        df_newscans.at[index,f"{key}_DATASET_NIFTI"] = "dicom does not exist"
                    elif os.path.exists(uids[key][1]):
                        status="nifti file already exists in ADNI2018/dataset"
                        df_newscans.at[index,f'{key}_CONVERT_STATUS'] = 1 
                        df_newscans.at[index,f"{key}_DATASET_NIFTI"] = uids[key][1]
                    else:
                        ### DO CONVERSION
                        result = subprocess.run(
                                ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/dicom_to_nifti.sh",\
                                scan_to_process.id,scan_to_process.scandate,uids[key][0],\
                                    scan_to_process.__class__.__name__,scan_to_process.log_output_dir], 
                                capture_output=True, text=True)
                        if result.returncode != 0:
                            logging.warning(f"{scan_to_process.id}:{scan_to_process.scandate}:\
                                            dicom_to_nifti.sh error {result.returncode}:{result.stderr}")
                            continue

                        result_list = result.stdout.split("\n")
                        if len(result_list) > 3:
                            #first item is "Job <###> submitted to queue..."
                            status = result_list[1]
                            nifti_file_loc_public = result_list[2]
                        else:
                            status = result_list[0]
                            nifti_file_loc_public = result_list[1]

                        ## Record conversion status to dataframe
                        if status == "conversion to nifti sucessful" or status == "nifti file already exists in PUBLIC/nifti":
                            df_newscans.at[index,f"{key}_CONVERT_STATUS"] = 1
                            df_newscans.at[index,f"{key}_DATASET_NIFTI"] = uids[key][1]
                        elif status == "conversion to nifti failed":
                            df_newscans.at[index,f"{key}_CONVERT_STATUS"] = 0
                        else:
                            df_newscans.at[index,f"{key}_CONVERT_STATUS"] = -1
                            df_newscans.at[index,f"{key}_DATASET_NIFTI"] = "dicom does not exist"

                        #Symlink PUBLIC/nifti file to ADNI2018/dataset version:
                        if not os.path.exists(uids[key][1]) and nifti_file_loc_public:
                            os.system(f"ln -sf {nifti_file_loc_public} {uids[key][1]}")

                    ##Report status of each key (t1, t2, flair, amy, tau)
                    logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Nifti conversion status for {key} is:{status}")

                ##MRI only step:
                if scantype == "mri":
                    logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Finding additional information for mri filelocation csv.")
                    #site's vendor & model info
                    site = scan_to_process.id.split("_")[0]
                    siteinfo_result = subprocess.run(
                        ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/get_site_scanner_info.sh",site],
                        capture_output=True, text=True)
                    siteinfo_result_list = siteinfo_result.stdout.split("\n")[:-1] # remove extra newline at end
                    siteinfo_headers = ["Model2","Model3","Vendor2","Vendor3"]
                    for i in range(0,len(siteinfo_result_list)):
                        df_newscans.at[index,siteinfo_headers[i]] = siteinfo_result_list[i]

            ### after all rows in iterrows, log conversion stats
            logging.info(f"{scantype}:Conversion status records (1=successful conversion, 0=failed conversion, -1=no dicom UID/dicom not found in cluster):")
            for column in [col for col in df_newscans.columns if "CONVERT_STATUS" in col]:
                logging.info(f"{df_newscans[column].value_counts()}")

            ### Save conversion status dataframe to csv
            if outputcsv:
                logging.info(f"Saving conversion status dataframe to csv: {outputcsv}")
                df_newscans.to_csv(outputcsv,index=False,header=True)
            else:
                new_fileloc_path = os.path.join(datasetup_directories_path["filelocations"],filenames['filelocations'][scantype])
                logging.info(f"Saving conversion status dataframe to csv: {new_fileloc_path}")
                
                # old_fileloc_path = [os.path.join(fileloc_directory_previousrun,x) for x in \
                #                     os.listdir(fileloc_directory_previousrun) if scantype in x][0]
                # old_filelocs_df = pd.read_csv(old_fileloc_path)
                # all_filelocs = pd.concat([df_newscans, old_filelocs_df], ignore_index=True)
                # #keep most recent (e.g. updated) if any duplicates
                # all_filelocs.drop_duplicates(subset=['RID','SMARTDATE'],keep='last', inplace=True) 
                # all_filelocs.sort_values(by=["RID","SMARTDATE"], ignore_index=True, inplace=True)
                # all_filelocs.to_csv(new_fileloc_path,index=False,header=True)
 

def image_processing(steps = [], all_steps = False, csv = "", dry_run = False):
    if all_steps:
        steps_ordered = processing_steps
    else:
        if len(steps) == 1:
            steps_ordered = steps
        else:
            ##variable processing_steps from config.py is ordered so steps with inputs that depend on other steps' outputs are listed after the other steps.
            steps_ordered = [method for method in processing_steps for step in steps if step in method]
    
    pet_check = [x for x in steps_ordered if "pet" in x]
    if len(pet_check) > 0:
        pet_steps=True
    else:
        pet_steps=False

    if csv:
        csv_to_read = csv
        df = pd.read_csv(csv_to_read)
    else:
        csv_to_read = os.path.join(datasetup_directories_path["processing_status"],"mri_processing_status.csv")
        df_full = pd.read_csv(csv_to_read)
        df = df_full.loc[(df_full['NEW_T1'] == 1) | (df_full['NEW_T2'] == 1) | (df_full['NEW_FLAIR'] == 1)]
    
    logging.info(f"DRY_RUN={dry_run}: Doing image processing steps {steps_ordered} for sessions in csv {csv_to_read}")

    #### For each session
    for index,row in df.iterrows():
        print(f"Processing line {index + 1} of {len(df)}")

        jobs_running = []
        subject = str(row['ID'])
        scandate = str(row['SMARTDATE.mri'])
        mri_to_process = MRI(subject,scandate)

        if pet_steps == True: 
            if 'SMARTDATE.tau' in df.columns:
                taudate = str(row['SMARTDATE.tau'])
                tau_to_process = TauPET(subject, taudate)
                mri_tau_reg_to_process = MRIPetReg(tau_to_process.__class__.__name__, mri_to_process, tau_to_process) 

            if "SMARTDATE.amy" in df.columns:
                amydate = str(row['SMARTDATE.amy'])
                amy_to_process = AmyloidPET(subject, amydate)
                mri_amy_reg_to_process = MRIPetReg(amy_to_process.__class__.__name__, mri_to_process, amy_to_process)

        for step in steps_ordered:
            if step == "wmh_seg": 
                continue
            elif (step == "flair_skull_strip" or step == "wmh_stats") and not os.path.exists(mri_to_process.flair):
                logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}: Cannot run {step}: No FLAIR file.")
                continue
            elif (step == "t2ashs" or step == "prc_cleanup" or step == "ashst2_stats") and not os.path.exists(mri_to_process.t2nifti):
                logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}: Cannot run {step}: No T2 file.")
                continue              
            elif (step != "flair_skull_strip" and step != "wmh_stats") and not os.path.exists(mri_to_process.t1nifti):
                logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}: Cannot run {step}: No T1 file.")
                ## Every other processing step uses T1 trim at least, including pet steps and all other stats steps
                continue
            elif "stats" in step:

                ## if only doing stats steps, no wait code from image processing jobs OR
                ## if no other jobs running, no wait code needed
                if len(steps_ordered) == len([x for x in steps_ordered if "stats" in x]) or len(jobs_running) == 0:
                    stats_wait_code = ""
                else:
                    stats_wait_code = [f"{mri_to_process.mridate}_{mri_to_process.id}*"]

                if step == "pet_stats":
                    mri_to_process.pet_stats(parent_job_name = stats_wait_code,
                                            t1tausuvr = mri_tau_reg_to_process.t1_SUVR,
                                            t1amysuvr = mri_amy_reg_to_process.t1_SUVR,
                                            taudate = mri_tau_reg_to_process.petdate,
                                            amydate = mri_amy_reg_to_process.petdate,
                                            dry_run = dry_run) 
                else:
                    getattr(mri_to_process,step)(parent_job_name = stats_wait_code, dry_run = dry_run)
            else:
                parent_step = determine_parent_step(step)
                wait_code = [job for job in jobs_running for pstep in parent_step if pstep in job]

                if "pet" in step: 
                    for pet_reg_class in [mri_tau_reg_to_process, mri_amy_reg_to_process]:
                        ## check files exist
                        if not os.path.exists(pet_reg_class.pet_nifti):
                            logging.info(f"{pet_reg_class.id}:{pet_reg_class.petdate}: Cannot run {step}: No {pet_reg_class.pet_type} file.")            
                            continue

                        ## Filter wait codes by pet_reg_class.pet_type as needed
                        if step == "t1_pet_reg":
                            ## only depends on neck_trim, not matched to pet_reg_class
                            pet_wait_code = wait_code
                        elif step == "t1_pet_suvr" and pet_reg_class.pet_type == "TauPET":
                            ## t1-tau suvr needs both mri infcereb and t1-tau reg
                            pet_wait_code = [code for code in wait_code if "Amyloid" not in code]
                        else:
                            ## wait code needs to match pet_reg_class as well as pstep in jobs running
                            pet_wait_code = [code for code in wait_code if pet_reg_class.pet_type in code]

                        job_name = getattr(pet_reg_class,step)(parent_job_name = pet_wait_code, dry_run = dry_run)
                        if job_name:
                            jobs_running.append(job_name)
                else:
                    job_name = getattr(mri_to_process,step)(parent_job_name = wait_code, dry_run = dry_run)
                    if job_name:
                        jobs_running.append(job_name)

    # For all sessions in csv, run WMH container--only spin up container once
    if "wmh_seg" in steps_ordered:
        if dry_run:
            print(f"run wmh singularity container")
        else:
            sing_output = f"{log_output_dir}/{current_date_time}_wmh_singularity_%J.txt"
            logging.info(f"Running WMH singularity for all files, check results at {sing_output}.")
            if "flair_skull_strip" in steps_ordered:
                os.system(f'bsub -o {sing_output} -w "done(*_flair_skull_strip)" bash ./wrapper_scripts/run_wmh_singularity.sh {wmh_prep_dir}/{current_date}')
            else: 
                os.system(f"bsub -o {sing_output} bash ./wrapper_scripts/run_wmh_singularity.sh {wmh_prep_dir}/{current_date} ")
        

## Make csvs of stats
def final_data_sheets(mode,wait):
    for stats_type in mode:
        logging.info(f"With wait == {wait}: Compiling individual session stats data from analysis_output/stats/ for stats type {stats_type}.")
        if wait: 
            # job to watch queue, only releases final_data_sheets job when all other jobs complete
            os.system(f'bsub -J "{current_date}_queuewatch" -o {log_output_dir}/{current_date_time}_queuewatch_%J.txt ./queue_watch.sh')
            os.system(f'bsub -J "{current_date}_datasheets" -w "done({current_date}_queuewatch)" \
                -o {log_output_dir}/{current_date_time}_createstatssheets_{stats_type}_%J.txt \
                ./create_stats_sheets.sh {wblabel_file} {analysis_output_dir} {stats_type}')
        else:
            os.system(f'bsub -J "{current_date}_datasheets" -o {log_output_dir}/{current_date_time}_createstatssheets_{stats_type}_%J.txt \
                ./create_stats_sheets.sh {wblabel_file} {analysis_output_dir} {stats_type}')
    

## Run longitudinal antsct-aging
def longitudinal_processing(csv = "" ,dry_run = False):
    csv_to_read = csv
    df = pd.read_csv(csv_to_read)
    subjects = df['ID'].unique().tolist()
    logging.info(f"Reading from csv: {csv}.")
    logging.info(f"Running ants_longitudinal_t1_processing for {len(subjects)} subjects")
    for subject in subjects:
        print(f"Processing subject {(subjects.index(subject)) + 1} of {len(subjects)}")
        output_dir = f'{adni_data_dir}/{subject}/longitudinal_ants'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        id_allrows=df.loc[df['ID'] == subject]
        alldates=id_allrows['SMARTDATE.mri'].values.tolist()
        mri_list=[]
        for i in range(0,len(alldates)):
            mri_list.append(MRI(subject,alldates[i]))
        t1images=" ".join([x.t1trim for x in mri_list])

        ## only checks if long_ants has been run, not if it's been run on the same subset of dates for the subject
        # existing_output = f"{output_dir}/antsLongitudinalCorticalThicknessOutput.txt"
        # if os.path.exists(existing_output):
        #     logging.info(f"{subject}:long ants already run.")
        #     continue
        # el
        if len(mri_list) == 1:
            logging.info(f"{subject}:skipping, only one timepoint available.")
            continue
        elif len(mri_list) >= 4: 
            logging.info(f"{subject}: skipping for now, 4 or more timepoints.")
            # logging.info(f"{subject}:passing {len(mri_list)} images to wrapper script.")
            continue
        else:
            logging.info(f"{subject}: passing {len(mri_list)} images to wrapper script.")
            # logging.info(f"{subject}:skipping, already did 2 and 3 timepoint subs.")
            # continue

        if dry_run == True: 
            print(f"{output_dir} {t1images}")
        else:
            result = subprocess.run(["bsub", "-o", f"{output_dir}/antsct-aging_longitudinal_%J.txt", "-q", "bsc_long", \
                "-n", "4", "-R", "rusage[mem=16000]", \
                "/project/wolk/ADNI2018/scripts/adni_processing_pipeline/wrapper_scripts/long_ants.sh",\
                output_dir, t1images], capture_output=True, text=True)
            if result.returncode != 0:
                logging.warning(f"{subject}:long_ants.sh error:{result.returncode}:{result.stderr}")
                continue
            result_list = result.stdout.split("\n") ## strips new line out of result.stdout
            logging.info(result_list[0]) 


''' Arguments/Parameters for each function '''
#Arguments
global_parser = argparse.ArgumentParser()
subparsers = global_parser.add_subparsers(title="Subcommands", help="Sections of ADNI processing pipeline.", dest='subparser_name')


###unpack_dicoms
unpack_dicoms_parser = subparsers.add_parser("unpack_dicoms", help="Unzip dicom files and rsync to /dataset.")
unpack_dicoms_parser.add_argument("-d", "--date", help="Date in format three-letter abbreviationYYYY, matching the zip file name.")
unpack_dicoms_parser.set_defaults(func=unpack_dicoms)


###data_setup
datasetup_parser = subparsers.add_parser("data_setup", help="Run datasetup.py.")
datasetup_parser.add_argument("-d", "--date",help="")
datasetup_parser.set_defaults(func=data_setup)


###convert_symlink
convert_parser = subparsers.add_parser("convert_symlink", help="Convert dicoms to nifti, symlink, create csv with filelocations.")
convert_type_group = convert_parser.add_mutually_exclusive_group(required=True)
convert_type_group.add_argument("-t","--single_type", choices=["amy","tau","mri"], help="Run conversion to nifti for tau, amy, OR mri dicoms.")
convert_type_group.add_argument("-a", "--all_types", action = "store_true", help="Run conversion to nifti for tau, amy, AND mri dicoms.")
convert_parser.add_argument("-i", "--inputcsv", required=False, help="If not using default csv for single type conversion, \
    filepath of a csv with format:\
    column 'ID' in format 999_S_9999, \
    column 'SMARTDATE' in format YYYY-MM-DD, \
    column 'NEW_T1|T2|FLAIR|PET' in format 1 if true, 0 if false, and \
    column 'IMAGEUID_T1|T2|FLAIR' (mri) or 'IMAGEID' (pet) in format '999999'")
convert_parser.add_argument("-o","--outputcsv", required=False, help="If not using default csv for single type conversion,\
     filepath for output csv with conversion status.")
convert_parser.set_defaults(func=convert_symlink)


###image_processing
image_proc_parser = subparsers.add_parser("image_processing", help="process mri images")
which_steps = image_proc_parser.add_mutually_exclusive_group(required=True)
which_steps.add_argument("-s", '--steps', nargs="+", choices=processing_steps, help="Processing step(s) to run.")
which_steps.add_argument("-a", "--all_steps", action="store_true", help=f"Run all processing steps: {processing_steps}")
image_proc_parser.add_argument("-c", "--csv", required=False, help="Optional csv of sessions to run if not using default csv produced by datasetup.py. \
    Format must be column 'ID' as 999_S_9999 and column 'SMARTDATE.mri' as YYYY-MM-DD. \
    If processing pet scans, include columns 'SMARTDATE.tau' and 'SMARTDATE.amy', both as YYYY-MM-DD")
image_proc_parser.add_argument("-d", "--dry_run", action = "store_true", required=False, help = "Run program but don't submit any jobs.")
image_proc_parser.set_defaults(func=image_processing)


###final_data_sheets
final_data_sheet_parser = subparsers.add_parser("final_data_sheets", help = "Collect individual stats into final sheets.")
final_data_sheet_parser.add_argument("-m", "--mode", nargs = "+", choices = ["pet", "structure", "ashst1", "ashst2","wmh"], help="Select which type(s) of stats to compile into a final sheet")
final_data_sheet_parser.add_argument("-w", "--wait", action="store_true", help = "Run with queuewatch to wait for all image processing to complete")
final_data_sheet_parser.set_defaults(func=final_data_sheets)


###longitudinal processing
long_process_parser = subparsers.add_parser("longitudinal_processing", help = "Longitudinal processing")
long_process_parser.add_argument("-c", "--csv", help="Required csv of sessions to run. \
    Format must be column 'ID' as 999_S_9999 and column 'SMARTDATE.mri' as YYYY-MM-DD.")
long_process_parser.add_argument("-d", "--dry_run", action = "store_true", required=False, help = "Run program but don't submit any jobs.")
long_process_parser.set_defaults(func=longitudinal_processing)


### Parse args
args = global_parser.parse_args()

## Raise exceptions for convert_symlink arguments that don't go together
if args.subparser_name == "convert_symlink":
    if args.all_types and args.inputcsv:
        raise ArgumentError("Cannot pass -i or -o for option --all_types, must use default csvs.")

    if args.inputcsv and not args.outputcsv:
        raise ArgumentError("--outputcsv option must be used with the --inputcsv option.")

## remove any non-kwargs values to pass to args.func()
args_ = vars(args).copy()
args_.pop('func', None) 
args_.pop('subparser_name', None) 
args.func(**args_)
