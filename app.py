#!/usr/bin/env python3

import argparse
import logging
import csv
import os
import pandas as pd
import subprocess
## Classes
from processing import MRI, AmyloidPET, TauPET, MRIPetReg
## variables
from config import *


## Symlinks zip files to /PUBLIC, unpack dicoms to /PUBLIC/ADNI, rsync /PUBLIC/ADNI with /PUBLIC/dicoms
def unpack_dicoms(date):
    #### zip files of new dicoms must already be added to cluster
    logging.info(f"Running organize_files.sh on zip file adni_dl_{date}")
    os.system(f"bsub -J '{current_date}_unzip_rsync' -q bsc_long -o {log_output_dir}/{current_date_time}_unzip_rsync.txt \
        bash organize_files.sh {date}") 


## get UID & processing status lists for new batches of scans to process
def data_setup(date):
    #### adni spreadsheets must already be added to cluster
    logging.info(f"Running data_setup.py for files in {analysis_input_dir}/{date}_processing.")
    os.system(f"bsub -J '{current_date}_data_setup' -o {log_output_dir}/{current_date_time}_data_setup.txt \
        python data_setup.py -d {date}") 


## Convert dicom to nifti and symlink nifti to /dataset
def convert_symlink(scantype="", inputcsv="", outputcsv=""):      
    logging.info(f"Running dicom to nifti conversion and nifti symlink for scantype {scantype} sessions in csv {inputcsv}")

    df=pd.read_csv(inputcsv,index_col=False)

    if scantype == 'mri':
        df_newscans = df.loc[(df['NEW.T1'] == 1) | (df['NEW.T2'] == 1) | (df['NEW.FLAIR'] == 1 )].reset_index(drop = True)
        datecol = "SCANDATE.mri"
    elif scantype == "amy":
        df_newscans = df.loc[(df['NEW.amy'] == 1)].reset_index(drop = True)
        datecol = "SCANDATE.amy"
    elif scantype == "tau":
        df_newscans = df.loc[(df['NEW.tau'] == 1)].reset_index(drop = True)
        datecol = "SCANDATE.tau"
    
    ##Start converting dicom to nifti, line by line    
    for index,row in df_newscans.iterrows():
        print(f"Processing line {index + 1} of {len(df_newscans)}")
        subject = str(row['ID'])
        scandate = str(row[datecol])
        if scantype == 'mri':
            scan_to_process = MRI(subject,scandate)
            uids={"T1": [str(row['IMAGEUID.T1']).split(".")[0], scan_to_process.t1nifti],
                    "T2": [str(row['IMAGEUID.T2']).split('.')[0], scan_to_process.t2nifti], 
                    "FLAIR": [str(row['IMAGEUID.FLAIR']).split('.')[0], scan_to_process.flair]}
        elif scantype == "amy":
            scan_to_process = AmyloidPET(subject,scandate)
            uids = {'AMY':[str(row["IMAGEUID.amy"]).split(".")[0], scan_to_process.amy_nifti]}
        elif scantype == 'tau':
            scan_to_process = TauPET(subject,scandate)
            uids = {'TAU':[str(row["IMAGEUID.tau"]).split(".")[0], scan_to_process.tau_nifti]}

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

    ### after all rows in iterrows, log conversion stats
    logging.info(f"{scantype}:Conversion status records (1=successful conversion, 0=failed conversion, -1=no dicom UID/dicom not found in cluster):")
    for column in [col for col in df_newscans.columns if "CONVERT_STATUS" in col]:
        print(df_newscans[column].value_counts())
        logging.info(df_newscans[column].value_counts())

    ### Save conversion status dataframe to csv
    if outputcsv:
        logging.info(f"Saving conversion status dataframe to csv: {outputcsv}")
        df_newscans.to_csv(outputcsv,index=False,header=True)
    else:
        new_fileloc_path = inputcsv.split(".")[0] + "_converted.csv"
        logging.info(f"Saving conversion status dataframe to csv: {new_fileloc_path}")
        df_newscans.to_csv(new_fileloc_path,index=False,header=True)


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

    df = pd.read_csv(csv)
    logging.info(f"DRY_RUN={dry_run}: Doing image processing steps {steps_ordered} for sessions in csv {csv}")

    #### For each session
    for index,row in df.iterrows():
        print(f"Processing line {index + 1} of {len(df)}")

        jobs_running = []
        subject = str(row['ID'])
        scandate = str(row['SCANDATE.mri'])
        mri_to_process = MRI(subject,scandate)

        if pet_steps == True: 
            if 'SCANDATE.tau' in df.columns:
                taudate = str(row['SCANDATE.tau'])
                tau_to_process = TauPET(subject, taudate)
                mri_tau_reg_to_process = MRIPetReg(tau_to_process.__class__.__name__, mri_to_process, tau_to_process) 

            if "SCANDATE.amy" in df.columns:
                amydate = str(row['SCANDATE.amy'])
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
                                            # t1tausuvr = mri_tau_reg_to_process.t1_8mm_SUVR,
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
                os.system(f'bsub -q bsc_long -o {sing_output} -w "done(*_flair_skull_strip)" bash ./wrapper_scripts/run_wmh_singularity.sh {wmh_prep_dir}/{current_date}')
            else: 
                os.system(f"bsub -q bsc_long -o {sing_output} bash ./wrapper_scripts/run_wmh_singularity.sh {wmh_prep_dir}/{current_date} ")

    ## Print some stats to the console
    print()
    logfile=logging.getLoggerClass().root.handlers[0].baseFilename 
    result = subprocess.run(["cat", logfile], capture_output=True, text=True)
    result_list = result.stdout.split("\n")
    for step in steps:
        print(f"{step} session counts")
        print(f"{len([i for i in result_list if 'already' in i and step in i])} already done")
        print(f"{len([i for i in result_list if 'Cannot' in i and step in i])} missing input file(s)")
        print(f"{len([i for i in result_list if f'Running {step}' in i or f'Submitting {step}' in i])} ready to submit job to run")
        # print(f"{len([i for i in result_list if ('Running' in i and f'{step}' in i) or ('Submitting' in i and f'{step}' in i)])} ready to submit job to run")
        print()

    print(f"{len([i for i in result_list if 'Running' in i or 'Submitting' in i])} total jobs submitted")


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
        alldates=id_allrows['SCANDATE.mri'].values.tolist()
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


def collect_qc(csv = "", dry_run = False, qc_type = ""):
    df = pd.read_csv(csv)

    ### Add filter for only new scans if using ADNI4_MRI_UIDS..._converted.csv??
    ## if a session had just one sequence type added later, will be adding existing files to qc, would have to break it down by seq type
    # if (qc_type == "ASHST1" or qc_type == "ASHST2" or qc_type == "wbseg" or qc_type == "thickness" ) and ("NEW"* in df.columns) :
        # df_newscans = df.loc[(df['NEW.T1'] == 1) | (df['NEW.T2'] == 1) | (df['NEW.FLAIR'] == 1 )].reset_index(drop = True)
  
    logging.info(f"DRY_RUN={dry_run}: collect {qc_type} QC for sessions in csv {csv}")

    ## make dir for this batch of QC files
    this_batch_qc_name = f"{qc_type}_{current_date}_QCToDo"
    this_batch_qc_dir = f"{qc_base_dir}/{this_batch_qc_name}"
    if not os.path.exists(this_batch_qc_dir) and not dry_run:
        os.system(f"mkdir {this_batch_qc_dir}")

    ## Create ratings files and add appropriate header from config.py
    ratings_file=f"{this_batch_qc_dir}/{this_batch_qc_name}_ratings.csv"
    if not dry_run:
        f = open(ratings_file, "a")
        f.write(qc_headers[qc_type])

    filecount = 0
    #### For each session, check for files 
    for index,row in df.iterrows():
        print(f"Processing line {index + 1} of {len(df)}")
        subject = str(row['ID'])

        if 'SCANDATE.mri' in df.columns:
            mridate = str(row['SCANDATE.mri'])
            mri_to_process = MRI(subject,mridate)
            line_to_write = f"\n{subject},{mridate}"

            if qc_type == "ASHST1":
                # qc_files = [mri_to_process.t1icv_qc, mri_to_process.t1ashs_qc_left, mri_to_process.t1ashs_qc_right]
                qc_files = [mri_to_process.t1icv_qc, mri_to_process.t1ashsext_qc_left, mri_to_process.t1ashsext_qc_right]
            elif qc_type == "ASHST2":
                qc_files = [mri_to_process.t2ashs_qc_left, mri_to_process.t2ashs_qc_right, mri_to_process.t2nifti]
            elif qc_type == "wbseg":
                qc_files = [mri_to_process.wbsegqc_image]
            elif qc_type == "thickness":
                qc_files = [mri_to_process.brainseg_mosaic_qc, mri_to_process.corticalthick_mosaic_qc]

        if qc_type == "Amy_MRI_reg": 
            amydate = str(row['SCANDATE.amy'])
            amy_to_process = AmyloidPET(subject, amydate)
            mri_amy_reg_to_process = MRIPetReg(amy_to_process.__class__.__name__, mri_to_process, amy_to_process)
            qc_files = [mri_amy_reg_to_process.t1_reg_qc]
            line_to_write = f"{line_to_write},{amydate}"
        elif qc_type == "Tau_MRI_reg":
            taudate = str(row['SCANDATE.tau'])
            tau_to_process = TauPET(subject, taudate)
            mri_tau_reg_to_process = MRIPetReg(tau_to_process.__class__.__name__, mri_to_process, tau_to_process) 
            qc_files = [mri_tau_reg_to_process.t1_reg_qc]
            # qc_files = [mri_tau_reg_to_process.t1_8mm_reg_qc]
            line_to_write = f"{line_to_write},{taudate}"

        ## Check if QC files exist:
        if len([file for file in qc_files if os.path.isfile(file)]) == len(qc_files):
            ## Directory to copy QC files to
            if "ASHS" in qc_type:
                dir_to_copy_to = f"{this_batch_qc_dir}/{subject}_{mridate}"  
            else:
                dir_to_copy_to = this_batch_qc_dir
            
            ## Make directory to copy to 
            if not os.path.exists(dir_to_copy_to) and not dry_run:
                os.mkdir(dir_to_copy_to)

            ## log and do copy and write to ratings file
            logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}:copying QC files to {dir_to_copy_to}.")
            filecount += 1
            if not dry_run:
                f.write(line_to_write)
                if "ASHS" in qc_type:
                    ## ASHS qc files don't have subject or date in file name, and T1 ASHS needs to be distinguished from ICV ASHS in same dir
                    [os.system(f"cp {file} {dir_to_copy_to}/{subject}_{mridate}_{os.path.dirname(file).split('/')[-2]}_{os.path.basename(file)}") for file in qc_files]
                elif "thickness" in qc_type:
                    [os.system(f"cp {file} {dir_to_copy_to}/{mridate}_{os.path.basename(file)}") for file in qc_files]
                    #### add date to file name
                    # print("")
                else:
                    [os.system(f"cp {file} {dir_to_copy_to}") for file in qc_files]

        ## if qc file not found
        else:
            logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}:QC files do not exist.")
            if not dry_run:
                f.write(f"{line_to_write},-1")

    ## zip directory of all QC files for download to Box
    if not dry_run:
        f.close()
        os.system(f"cd {this_batch_qc_dir}; zip -r {this_batch_qc_name}.zip .")
        logging.info(f"scp <username>@bscsub.pmacs.upenn.edu:{this_batch_qc_dir}/{this_batch_qc_name}.zip .")
    
    print(f"{filecount} {qc_type} files added to be QC'ed.")
    return


def file_exist(inputcsv = "", check_type = ""):
    df = pd.read_csv(inputcsv)
    logging.info(f"Check if {check_type} derived files exist for sessions in csv:{inputcsv}")
    record_file = f"{analysis_output_dir}/file_exist_record_{check_type}_{current_date_time}.csv"

    with open(record_file, 'w', newline='') as csvfile:
        fieldnames = ['ID', 'MRIDATE', 't1nifti', 't1trim', 'thickness', 'pmtau_output', 'brainx', 'wbseg_nifti', \
                    'wbsegqc_image', 'wbseg_propagated', 'inferior_cereb_mask', 'superres_nifti', 't1ashsext_seg_left', \
                    't1ashsext_seg_right', 't1ashsext_qc_left', 't1ashsext_qc_right', 't1mtthk_left', 't1mtthk_right', \
                    't1icv_seg', 't1icv_qc', 'icv_volumes_file', 't2nifti', 't2ashs_seg_left', 't2ashs_seg_right', \
                    't2ashs_tse', 't2ashs_flirt_reg', 't1_to_t2_transform', 't2ashs_qc_left', 't2ashs_qc_right', \
                    't2ashs_cleanup_left', 't2ashs_cleanup_right', 't2ashs_cleanup_both', 'flair', \
                    'flair_noskull', 'wmh', 't1ashs_stats_txt', 't2ashs_stats_txt', 'structure_stats_txt', 'wmh_stats_txt', 'brainseg_mosaic_qc','corticalthick_mosaic_qc']
        if check_type == "pet":
            pet_fieldnames = ['TAUDATE', 'AMYDATE', 'TauPET_pet_nifti', 'TauPET_t1_reg_nifti', 'TauPET_t1_SUVR', 'TauPET_t1_reg_qc', \
                                'AmyloidPET_pet_nifti', 'AmyloidPET_t1_reg_nifti', 'AmyloidPET_t1_SUVR', 'AmyloidPET_t1_reg_qc']
            fieldnames.extend(pet_fieldnames)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        #### For each session, check for files 
        for index,row in df.iterrows():
            print(f"Processing line {index + 1} of {len(df)}")
            subject = str(row['ID'])

            if 'SCANDATE.mri' in df.columns:
                mridate = str(row['SCANDATE.mri'])
                mri_to_process = MRI(subject,mridate)
                dict_to_write = {"ID":subject, "MRIDATE":mridate}     

                ones_to_remove = ["id", "mridate", "scandate", "filepath", "date_id_prefix", "thick_dir", "t1trim_thickness_dir", 
                "ants_brainseg","brainx_thickness_dir","wbseg_dir", "t1ashsext_dir", "t1ashsext_seg_prefix","t1ashsext_seg_suffix",
                "t1ashs_seg_left", "t1ashs_seg_right", "t1mtthk_prefix","t1mtthk_suffix","log_output_dir"]
                ## list of all class attributes, drop the ones that aren't important files, then give dict value of 1 if file exists
                file_check = {item:1 if os.path.exists(value) else 0 for item,value in vars(mri_to_process).items() if item not in ones_to_remove}
                dict_to_write.update(file_check)

            if check_type == "pet":
                taudate = str(row['SCANDATE.tau'])
                tau_to_process = TauPET(subject, taudate)
                mri_tau_reg_to_process = MRIPetReg(tau_to_process.__class__.__name__, mri_to_process, tau_to_process) 
                amydate = str(row['SCANDATE.amy'])
                amy_to_process = AmyloidPET(subject, amydate)
                mri_amy_reg_to_process = MRIPetReg(amy_to_process.__class__.__name__, mri_to_process, amy_to_process)
                pet_dates = {"TAUDATE":taudate, "AMYDATE":amydate}     
                dict_to_write.update(pet_dates)

                ## checking for 4 files for amy and tau: pet_nifti, t1_reg_nifti, t1_SUVR, t1_reg_qc
                ones_to_keep = ["pet_nifti", "t1_reg_nifti", "t1_SUVR", "t1_reg_qc"]
                for pet_reg in mri_tau_reg_to_process, mri_amy_reg_to_process:
                    pet_file_check = {f"{pet_reg.pet_type}_{item}":1 if os.path.exists(value) else 0 for item,value in vars(pet_reg).items() if item in ones_to_keep}
                    dict_to_write.update(pet_file_check)
            
            ## write all file exist values for this row to file
            writer.writerow(dict_to_write)

    return


''' Arguments/Parameters for each function '''
#Arguments
global_parser = argparse.ArgumentParser()
subparsers = global_parser.add_subparsers(title="Subcommands", help="Sections of ADNI processing pipeline.", dest='subparser_name')


###unpack_dicoms
unpack_dicoms_parser = subparsers.add_parser("unpack_dicoms", help="Unzip dicom files and rsync to /dataset.")
unpack_dicoms_parser.add_argument("-d", "--date", help="Date in format \{three_letter_abbreviationYYYY\}, \
    matching the directory containing the zip files, e.g. Jan2025.")
unpack_dicoms_parser.set_defaults(func=unpack_dicoms)


###data_setup
datasetup_parser = subparsers.add_parser("data_setup", help="Run datasetup.py.")
datasetup_parser.add_argument("-d", "--date",help="Date in format YYYYMMDD that matches date on processing folders in /project/wolk/ADNI2018/analysis_input/.")
datasetup_parser.set_defaults(func=data_setup)


###convert_symlink
convert_parser = subparsers.add_parser("convert_symlink", help="Convert dicoms to nifti, symlink, create csv with filelocations.")
convert_parser.add_argument("-t","--scantype", choices=["amy","tau","mri"], help="Run conversion to nifti for tau, amy, or mri dicoms.")
convert_parser.add_argument("-i", "--inputcsv", help="Required csv for single type conversion, \
    filepath of a csv with format:\
    column 'ID' in format 999_S_9999, \
    column 'SCANDATE.(mri|tau|amy)' in format YYYY-MM-DD, \
    column 'NEW.T1|T2|FLAIR|tau|amy' in format 1 if true, 0 if false, and \
    column 'IMAGEUID.T1|T2|FLAIR|amy|tau' in format '999999'")
convert_parser.add_argument("-o","--outputcsv", required=False, help="If not saving to default location of \
    inputcsv_filname + 'converted' for single type conversion,\
    filepath for output csv with conversion status.")
convert_parser.set_defaults(func=convert_symlink)


###image_processing
image_proc_parser = subparsers.add_parser("image_processing", help="process mri images")
which_steps = image_proc_parser.add_mutually_exclusive_group(required=True)
which_steps.add_argument("-s", '--steps', nargs="+", choices=processing_steps, help="Processing step(s) to run.")
which_steps.add_argument("-a", "--all_steps", action="store_true", help=f"Run all processing steps: {processing_steps}")
image_proc_parser.add_argument("-c", "--csv", help="Required csv of sessions to run. \
    Format must be column 'ID' as 999_S_9999 and column 'SCANDATE.mri' as YYYY-MM-DD. \
    If processing pet scans, include columns 'SCANDATE.tau' and 'SCANDATE.amy', both as YYYY-MM-DD")
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
    Format must be column 'ID' as 999_S_9999 and column 'SCANDATE.mri' as YYYY-MM-DD.")
long_process_parser.add_argument("-d", "--dry_run", action = "store_true", required=False, help = "Run program but don't submit any jobs.")
long_process_parser.set_defaults(func=longitudinal_processing)


## Collect qc files 
collectqc_parser = subparsers.add_parser("collect_qc", help = "collect qc files")
collectqc_parser.add_argument("-t", "--qc_type", choices = qc_types, help="Which kind of qc to do")
collectqc_parser.add_argument("-c", "--csv", help="Required csv of sessions to run. \
    Format must be column 'ID' as 999_S_9999 and column 'SCANDATE.mri' as YYYY-MM-DD.\
    If qc_type is Amy_MRI_reg or Tau_MRI_reg, include column 'SCANDATE.tau|amy' as YYYY-MM-DD")
collectqc_parser.add_argument("-d", "--dry_run", action = "store_true", required=False, 
    help = "Run program to get log file with expected files to be copied but does not create \
    any QC folders or files or copy any files.")
collectqc_parser.set_defaults(func=collect_qc)


## check if all processing files exist
fileexist_parser = subparsers.add_parser("file_exist", help = "check if processed files exist")
fileexist_parser.add_argument("-t", "--check_type", choices = ["mri", "pet"], help="check for only mri-derived files \
    or mri-derived files and mri-pet registration derived files.")
fileexist_parser.add_argument("-c", "--inputcsv", help="Required csv of sessions to run. \
    Format must be column 'ID' as 999_S_9999 and column 'SCANDATE.mri' as YYYY-MM-DD.\
    If check_type is pet, include columns 'SCANDATE.tau' and 'SCANDATE.amy' as YYYY-MM-DD")
fileexist_parser.set_defaults(func=file_exist)


### Parse args
args = global_parser.parse_args()
## remove any non-kwargs values to pass to args.func()
args_ = vars(args).copy()
args_.pop('func', None) 
args_.pop('subparser_name', None) 
args.func(**args_)
