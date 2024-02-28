#!/usr/bin/env python3

import argparse
import logging
import os
import pandas as pd
import subprocess
# Classes
from processing import MRI, AmyloidPET, TauPET, MRIPetReg
#variables
from config import *
# from convert_symlink import convert_symlink_function

def unpack_dicoms(date):
    #### zip files of new dicoms must already be added to cluster
    ### Symlinks zip files to /PUBLIC, unpack dicoms to /PUBLIC/ADNI, 
    ### rsync /PUBLIC/ADNI with /PUBLIC/dicoms
    os.system(f"bsub -J '{current_date}_unzip_rsync' -o {this_output_dir}/unzip_rsync_{current_date_time}.txt \
        bash organize_files.sh {date} {this_output_dir}") 

def data_setup():
    #### adni spreadsheets must already be added to cluster
    ### get UID & processing status lists for new batches of scans to process
    os.system(f"bsub -J '{current_date}_datasteup' -o {this_output_dir}/datasetup_{current_date_time}.txt \
        python datasetup.py") 

def convert_symlink(types="", all_types=False, inputcsv="", outputcsv=""):
    # print("run dicom to nifti conversion")

    ##TODO: modify this function so it runs via bsub
    # os.system(f'python -c "from convert_symlink import convert_symlink_function;\
    #     convert_symlink_function(types={types})"')
        #works when \'mri\' is passed, but not the variable

    for scantype in scantypes:
        if types == scantype or all_types == True and scantype != "anchored":
            if inputcsv:
                csv_to_read = inputcsv
            else:
                csv_to_read = os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status'][scantype])
        
            logging.info(f"Running dicom to nifti conversion and nifti symlink for scantype {scantype} sessions in csv {csv_to_read}")

            df=pd.read_csv(csv_to_read)

            if scantype == 'mri':
                df_newscans = df.loc[(df['NEW_T1'] == 1) | (df['NEW_T2'] == 1)] # | df['NEW_FLAIR'] == 1
            else:
                df_newscans = df.loc[(df['NEW_PET'] == 1)]

            ##Start converting dicom to nifti, line by line    
            for index,row in df_newscans.iterrows():
                subject = str(row['ID'])
                scandate = str(row['SMARTDATE'])
                if scantype == 'mri':
                    scan_to_process = MRI(subject,scandate)
                    ##TODO: Flair dicom to nifti processing--add flair dicom to uid csvs
                    uids={"t1_uid": [str(row['IMAGEUID_T1']).split(".")[0], scan_to_process.t1nifti],
                          "t2_uid": [str(row['IMAGEUID_T2']).split('.')[0], scan_to_process.t2nifti]} 
                        #'flair_uid': str(row['IMAGEUID_FLAIR'])
                elif scantype == "amy":
                    scan_to_process = AmyloidPET(subject,scandate)
                    uids = {'amy_uid':[str(row["IMAGEID"]).split(".")[0], scan_to_process.amy_nifti]}
                elif scantype == 'tau':
                    scan_to_process = TauPET(subject,scandate)
                    uids = {'tau_uid':[str(row["IMAGEID"]).split(".")[0], scan_to_process.tau_nifti]}

                logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:{scantype}: Checking convert to nifti status.")

                for key in uids:
                    if uids[key][0] == "nan":
                        status="No dicom UID"
                        ##TODO: record convert status to dataframe
                        ##df_newscans.at[index,'{key}_CONVERT_STATUS'] = 0 
                        #if/else for col name
                    elif os.path.exists(uids[key][1]):
                        status="nifti file already exists in ADNI2018/dataset"
                    else:
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

                        if status == "conversion to nifti sucessful" or status == "nifti file already exists in PUBLIC/nifti":
                            if key == "t1_uid":
                                df_newscans.at[index,'FINALT1NIFTI'] = nifti_file_loc_public
                                df_newscans.at[index,'T1_CONVERT_STATUS'] = 1
                            elif key == "t2_uid":
                                df_newscans.at[index,'FINALT2NIFTI'] = nifti_file_loc_public
                                df_newscans.at[index,'T2_CONVERT_STATUS'] = 1
                            #elif key == "flair_uid":
                                # df_newscans.at[index,'FINALFLAIRNIFTI'] = nifti_file_loc_public
                                # df_newscans.at[index,'FLAIR_CONVERT_STATUS'] = 1
                            elif key == "amy_uid":
                                df_newscans.at[index,'FILELOC'] = nifti_file_loc_public
                                df_newscans.at[index,'AMYNIFTI'] = uids[key][1]
                                df_newscans.at[index,'AMY_CONVERT_STATUS'] = 1
                            elif key == "tau_uid":
                                df_newscans.at[index,'FILELOC'] = nifti_file_loc_public
                                df_newscans.at[index,'TAUNIFTI'] = uids[key][1]
                                df_newscans.at[index,'TAU_CONVERT_STATUS'] = 1

                            # make symlink for nifti file between /PUBLIC and /dataset
                            # print(f'symlink if sucess')
                                ##TODO: delete this--next if statement will still be evaluated for truthiness even if link is already made
                            os.system(f"ln -sf {nifti_file_loc_public} {uids[key][1]}")

                        ##if dicom has been converted but nifti not symlinked:
                        if not os.path.exists(uids[key][1]) and nifti_file_loc_public:
                            # print("symlink if other than success")
                            os.system(f"ln -sf {nifti_file_loc_public} {uids[key][1]}")

                    ##Report status of each key (t1/t2, amy, tau)
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

            ##after all rows in iterrows
            ###TODO: Missing dicoms record:
            # no_t1 = all_filelocs.loc[pd.isnull(all_filelocs['FINALT1NIFTI'])]
            # no_t2 = all_filelocs.loc[pd.isnull(all_filelocs['FINALT2NIFTI'])]

            ## Save record of file locations
            # logging.info(f"{scantype}:Saving file location csv after conversion")
            # if outputcsv:
            #     df_newscans.to_csv(outputcsv,index=False,header=True)
            # else:
            #     old_fileloc_path = [os.path.join(fileloc_directory_previousrun,x) for x in \
            #                         os.listdir(fileloc_directory_previousrun) if scantype in x][0]
            #     old_filelocs_df = pd.read_csv(old_fileloc_path)
            #     all_filelocs = pd.concat([df_newscans, old_filelocs_df], ignore_index=True)
            #     #keep most recent (e.g. updated) if any duplicates
            #     all_filelocs.drop_duplicates(subset=['RID','SMARTDATE'],keep='last', inplace=True) 
            #     all_filelocs.sort_values(by=["RID","SMARTDATE"], ignore_index=True, inplace=True)
                
            #     print(all_filelocs.info())
            
            #     all_filelocs.to_csv(os.path.join(datasetup_directories_path["filelocations"],\
            #                         filenames['filelocations'][scantype]),index=False,header=True)
 

def mri_image_processing(steps=[], all_steps=False, csv="", dry_run=False):
    if all_steps:
        steps_ordered = mri_processing_steps
    else:
        if len(steps) == 1:
            steps_ordered = steps
        else:
            ##variable mri_processing_steps from config.py is ordered so steps with inputs that depend on other steps' outputs are listed after the other steps.
            steps_ordered = [method for method in mri_processing_steps for step in steps if step in method]
    print(f"Run image processing steps: {steps_ordered}")

    if csv:
        csv_to_read = csv
        df = pd.read_csv(csv_to_read)
    else:
        csv_to_read = os.path.join(datasetup_directories_path["processing_status"],"mri_processing_status.csv")
        df_full = pd.read_csv(csv_to_read)
        df = df_full.loc[(df_full['NEW_T1'] == 1) | (df_full['NEW_T2'] == 1)] # | df['NEW_FLAIR'] == 1
    
    logging.info(f"With DRY_RUN={dry_run}: Running MRI image processing steps {steps_ordered} for sessions in csv {csv_to_read}")
    # print(df.head())

    # dry_run = True

    for index,row in df.iterrows():
        subject = str(row['ID'])
        scandate = str(row['SMARTDATE'])
        scan_to_process = MRI(subject,scandate)
        ##first processing step will always run without a parent job.
        ##processing steps will return either a job name if needed for subsequent steps, or 'None' if no other steps depend on its output
        parent_job=''
        for step in steps_ordered:
            # print(f"{scan_to_process.id}:{scan_to_process.scandate}:Doing image processing:{step}.")
            if (step == "t2ashs" or step == "prc_cleanup") and not os.path.exists(scan_to_process.t2nifti):
                logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:No T2 file.")
                continue              
            elif "stats" not in step and not os.path.exists(scan_to_process.t1nifti):
                logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:No T1 file.")
                continue
            elif "stats" in step:
                # print(f"doing stats step {step}")
                ##if only doing stats, no need to wait for image processing jobs to complete
                if len(steps_ordered) == len([x for x in steps_ordered if "stats" in x]):
                    getattr(scan_to_process,step)(dry_run = dry_run) 
                else:
                    getattr(scan_to_process,step)(wait_code=f"{scan_to_process.mridate}_{scan_to_process.id}*", dry_run = dry_run)
            else:
                if parent_job: 
                    ##Call processing step function on class instance with the parent job name
                    parent_job = getattr(scan_to_process,step)(parent_job_name = parent_job, dry_run = dry_run)
                else:
                    ##Call processing step function on class instance with no parent job 
                    parent_job = getattr(scan_to_process,step)(dry_run = dry_run)
                    

def mri_pet_registration(steps=[], all_steps=False, csv="", dry_run=False):
    if all_steps==True:
        steps_ordered = registration_steps
    else:
        if len(steps) == 1:
            steps_ordered = steps
        else:
            ##variable registration_steps from config.py is ordered so steps with inputs that depend on other steps' outputs are listed after the other steps.
            steps_ordered = [method for method in registration_steps for step in steps if step in method]
    # print(f"Run pet-mri registration steps: {steps_ordered}")

    if csv:
        csv_to_read = csv
        df = pd.read_csv(csv_to_read)
    else:
        csv_to_read = os.path.join(datasetup_directories_path["processing_status"],"anchored_processing_status.csv")
        df_newscans = pd.read_csv(csv_to_read)
        df = df_newscans.loc[(df_newscans['NEW_anchored'] == 1)]

    logging.info(f"With DRY_RUN={dry_run}: Running MRI-PET registration steps {steps_ordered} for sessions in csv {csv_to_read}")
    
    # print(df.head())
    for index,row in df.iterrows():
        subject = str(row['ID'])
        mridate = str(row['SMARTDATE.mri'])
        taudate = str(row['SMARTDATE.tau'])
        amydate = str(row['SMARTDATE.amy'])
    
        mri_to_process = MRI(subject,mridate)
        tau_to_process = TauPET(subject, taudate)
        mri_tau_reg_to_process = MRIPetReg(tau_to_process.__class__.__name__, mri_to_process, tau_to_process) 
        amy_to_process = AmyloidPET(subject, amydate)
        mri_amy_reg_to_process = MRIPetReg(amy_to_process.__class__.__name__, mri_to_process, amy_to_process)

        if "structpetstats" in steps_ordered and len(steps_ordered) == 1:
            ##if only doing stats, no wait code from image processing funcations
            logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}:{mri_tau_reg_to_process.petdate}:{mri_amy_reg_to_process.petdate}:Running pet stats.")
            # print(f"submit without wait code")
            mri_to_process.structpetstats(t1tau = mri_tau_reg_to_process.t1_reg_nifti, 
                                        t2tau = mri_tau_reg_to_process.t2_reg_nifti,
                                        t1amy = mri_amy_reg_to_process.t1_reg_nifti,
                                        t2amy = mri_amy_reg_to_process.t2_reg_nifti, 
                                        taudate = mri_tau_reg_to_process.petdate,
                                        amydate = mri_amy_reg_to_process.petdate, dry_run = dry_run) 
        else:
            ##first processing step will always run without a parent job.
            ##processing steps will return either a job name if needed for subsequent steps, or 'None' if no other steps depend on its output
            parent_job=''
            for pet_reg_class in [mri_tau_reg_to_process, mri_amy_reg_to_process]:
                logging.info(f"{pet_reg_class.id}:{pet_reg_class.mridate}:{pet_reg_class.petdate}:{pet_reg_class.pet_type}:Now processing")
                for step in steps_ordered:
                    if step != "structpetstats":
                        if (step == "t1_pet_reg" or step == "pet_reg_qc") and not os.path.exists(mri_to_process.t1nifti):
                            logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}:No T1 file.")
                            continue              
                        elif "t2" in step and not os.path.exists(mri_to_process.t2nifti):
                            logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}:No T2 file.")
                            continue
                        else:
                            if parent_job: 
                                ##Call processing step function on class instance with the parent job name
                                parent_job = getattr(pet_reg_class,step)(parent_job_name = parent_job, dry_run = dry_run)
                            else:
                                ##Call processing step function on class instance with no parent job 
                                parent_job = getattr(pet_reg_class,step)(dry_run = dry_run)

                    elif step == "structpetstats" and pet_reg_class.pet_type == "amypet":
                        ###only run once, don't need for both tau and amy petreg classes
                        # print(f'submit with id date wait code')
                        logging.info(f"{mri_to_process.id}:{mri_to_process.scandate}:{mri_tau_reg_to_process.petdate}:{mri_amy_reg_to_process.petdate}:Running pet stats.")
                        jobname_prefix_this_subject = f"{mri_to_process.mridate}_{mri_to_process.id}*"
                        mri_to_process.structpetstats(wait_code=jobname_prefix_this_subject,
                                                    t1tau = mri_tau_reg_to_process.t1_reg_nifti, 
                                                    t2tau = mri_tau_reg_to_process.t2_reg_nifti,
                                                    t1amy = mri_amy_reg_to_process.t1_reg_nifti,
                                                    t2amy = mri_amy_reg_to_process.t2_reg_nifti, 
                                                    taudate = mri_tau_reg_to_process.petdate,
                                                    amydate = mri_amy_reg_to_process.petdate, dry_run = dry_run) 
        

def final_data_sheets(mode):
    #job to watch queue for status of all image processing & individual stats collection
    # print(f'bsub -J "{current_date}_queuewatch" -o {this_output_dir} ./queue_watch.sh')
    os.system(f'bsub -J "{current_date}_queuewatch" -o {this_output_dir} ./queue_watch.sh')
    
    logging.info(f"Collecting data from analysis_output/stats/ for data sheets.")
    # print(f'bsub -J "{current_date}_datasheets" -w "done({current_date}_queuewatch)" -o {this_output_dir} \
    #       ./create_stats_sheets.sh {wblabel_file} {stats_output_dir} {this_output_dir}')
    os.system(f'bsub -J "{current_date}_datasheets" -w "done({current_date}_queuewatch)" -o {this_output_dir} \
              ./create_stats_sheets.sh {wblabel_file} {analysis_output_dir} {mode}')

 
#Arguments
global_parser = argparse.ArgumentParser()
subparsers = global_parser.add_subparsers(title="Subcommands", help="Sections of ADNI processing pipeline.")


###unpack_dicoms
unpack_dicoms_parser = subparsers.add_parser("unpack_dicoms", help="Unzip dicom files and rsync to /dataset.")
unpack_dicoms_parser.add_argument("-d", "--date", help="Date in format three-letter abbreviationYYYY, matching the zip file name.")
unpack_dicoms_parser.set_defaults(func=unpack_dicoms)


###data_setup
datasetup_parser = subparsers.add_parser("data_setup", help="Run datasetup.py.")
datasetup_parser.set_defaults(func=data_setup)


###convert_symlink
convert_parser = subparsers.add_parser("convert_symlink", help="Convert dicoms to nifti, symlink, create csv with filelocations.")
convert_type_group = convert_parser.add_mutually_exclusive_group(required=True)
convert_type_group.add_argument("-t","--types", choices=["amy","tau","mri"], help="Run conversion to nifti for tau, amy, OR mri dicoms.")
convert_type_group.add_argument("-a", "--all_types", action = "store_true", help="Run conversion to nifti for tau, amy, AND mri dicoms.")
##can only use input and output csv args if doing single type
convert_parser.add_argument("-i", "--inputcsv", required=False, help="csv with column 'ID' in format 999_S_9999, \
    column 'SMARTDATE' in format YYYY-MM-DD, column 'NEW_' in format 1 if true, 0 if false, and column 'IMAGEUID_T1' \
        in format '999999' \
        of sessions to process if not using default.")
        ##TODO: complete help for pet vs mri csv parameters
convert_parser.add_argument("-o","--outputcsv", required=False, help="Full filepath and filename to save csv of filelocation information.")
##TODO: if input, then output and vice versa (if using one, the other is also required)
convert_parser.set_defaults(func=convert_symlink)


###mri_image_processing
mri_image_proc_parser = subparsers.add_parser("mri_image_processing", help="process mri images")
mristep_or_all_group = mri_image_proc_parser.add_mutually_exclusive_group(required=True)
mristep_or_all_group.add_argument("-s", '--steps', nargs="+", choices=mri_processing_steps, help="Processing step(s) to run.")
mristep_or_all_group.add_argument("-a", "--all_steps", action="store_true", help=f"Run all processing steps: {mri_processing_steps}")
mri_image_proc_parser.add_argument("-c", "--csv", required=False, help="csv with column 'ID' in format 999_S_9999 and \
    column 'SMARTDATE' in format YYYY-MM-DD of sessions to process if not using default.")
mri_image_proc_parser.add_argument("-d", "--dry_run", action = "store_true", required=False, help = "Run program but don't submit any jobs.")
mri_image_proc_parser.set_defaults(func=mri_image_processing)


###mri_pet_registration
mri_pet_reg_parser = subparsers.add_parser("mri_pet_registration", help="Do mri-pet registration and stats.")
reg_step_or_all_group = mri_pet_reg_parser.add_mutually_exclusive_group(required=True)
reg_step_or_all_group.add_argument("-s", '--steps', nargs="+", choices=registration_steps, help="Select processing step(s) to run.")
reg_step_or_all_group.add_argument("-a", "--all_steps", action="store_true", help=f"Run all processing steps: {registration_steps}")
mri_pet_reg_parser.add_argument("-c", "--csv", required=False, help="csv with column 'ID' in format 999_S_9999, columns \
    'SMARTDATE.tau', 'SMARTDATE.mri', 'SMARTDATE.amy', all in format YYY-MM-DD of sessions to process if not using default.")
mri_pet_reg_parser.add_argument("-d", "--dry_run", action = "store_true", required=False, help = "Run program but don't submit any jobs.")
mri_pet_reg_parser.set_defaults(func=mri_pet_registration)


###final_data_sheets
final_data_sheet_parser = subparsers.add_parser("final_data_sheets", help = "Collect individual stats into final sheets.")
final_data_sheet_parser.add_argument("-m", "--mode", nargs = "+", choices = stats_steps, help="Select which type of stats to collect into final sheet")
final_data_sheet_parser.set_defaults(func=final_data_sheets)


###Parse args
args = global_parser.parse_args()
##removes any non-kwargs values to pass to args.func()
args_ = vars(args).copy()
args_.pop('func', None) 
args.func(**args_)
