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

def unpack_dicoms():
    print('this should run organize_files.sh --symlink zip folders, unzip, rsync')
     

def data_setup():
    print("Run datasetup.py to create new uids, processing status csvs")


def convert_symlink(type, csv=""):
    print("run dicom to nifti conversion")


def mri_image_processing(steps, csv=""):
    # print(f"Run image processing steps: {steps}")

    if len(steps) == 1:
        if steps[0] == "all_mri":
            steps_ordered = mri_processing_steps[:-1]
        else:
            steps_ordered = steps
    else:
        ##variable mri_processing_steps from config.py is ordered so steps with inputs that depend on other steps' outputs are listed after the other steps.
        steps_ordered = [method for method in mri_processing_steps for step in steps if step in method]

    if csv:
        csv_to_read = csv
    else:
        csv_to_read = os.path.join(datasetup_directories_path["processing_status"],"mri_processing_status.csv")

    df=pd.read_csv(csv_to_read)
    for index,row in df.iterrows():
        subject = str(row['ID'])
        scandate = str(row['SMARTDATE'])
        scan_to_process = MRI(subject,scandate)
        ##first processing step will always run without a parent job.
        ##processing steps will return either a job name if needed for subsequent steps, or 'None' if no other steps depend on its output
        parent_job=''
        for step in steps_ordered:
            logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Doing image processing:{step}.")
            # if step == "t2ashs" or step == "prc_cleanup" and not os.path.exists(scan_to_process.t2nifti):
            #     logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:No T2 file.")
            #     continue              
            # elif 'stats' not in step and not os.path.exists(scan_to_process.t1nifti):
            #     logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:No T1 file.")
            #     continue
            # else:
            #     if parent_job: 
            #         ##Call processing step function on class instance with the parent job name
            #         parent_job = getattr(scan_to_process,step)(parent_job)
            #     else:
            #         ##Call processing step function on class instance with no parent job 
            #         parent_job = getattr(scan_to_process,step)()

                    

def mri_pet_registration(step, csv=""):
    print(f"Run pet-mri registration steps: {step}")

    if len(steps) == 1:
        if steps[0] == "all_reg":
            steps_ordered = registration_steps[:-1]
        else:
            steps_ordered = steps
    else:
        ##variable registration_steps from config.py is ordered so steps with inputs that depend on other steps' outputs are listed after the other steps.
        steps_ordered = [method for method in registration_steps for step in steps if step in method]

    if csv:
        csv_to_read = csv
    else:
        csv_to_read = os.path.join(datasetup_directories_path["processing_status"],"anchored_processing_status.csv")

    df=pd.read_csv(csv_to_read)
    # print(df.head())
    for index,row in df.iterrows():
        subject = str(row['ID'])
        mridate = str(row['SMARTDATE.mri'])
        taudate = str(row['SMARTDATE.tau'])
        amydate = str(row['SMARTDATE.amy'])
    
        mri_to_process = MRI(subject,mridate)

        tau_to_process = TauPET(subject, taudate)
        mri_tau_reg_to_process = MRIPetReg("taupet", mri_to_process, tau_to_process) 

        ##first processing step will always run without a parent job.
        ##processing steps will return either a job name if needed for subsequent steps, or 'None' if no other steps depend on its output
        parent_job=''
        for step in steps_ordered:
            logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Doing image processing:{step}.")
            # if step == "t2ashs" or step == "prc_cleanup" and not os.path.exists(scan_to_process.t2nifti):
            #     logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:No T2 file.")
            #     continue              
            # elif 'stats' not in step and not os.path.exists(scan_to_process.t1nifti):
            #     logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:No T1 file.")
            #     continue
            # else:
            #     if parent_job: 
            #         ##Call processing step function on class instance with the parent job name
            #         parent_job = getattr(scan_to_process,step)(parent_job)
            #     else:
            #         ##Call processing step function on class instance with no parent job 
            #         parent_job = getattr(scan_to_process,step)()



        logging.info(f"{mri_tau_reg_to_process.id}:{mri_tau_reg_to_process.mridate}:{mri_tau_reg_to_process.petdate}: Now processing")
        t1_tau_pet_reg_job = mri_tau_reg_to_process.do_t1_pet_reg()
        # mri_tau_reg_to_process.do_pet_reg_qc(t1_tau_pet_reg_job)
        mri_tau_reg_to_process.do_t2_pet_reg([t1_tau_pet_reg_job,f"{mri_to_process.mridate}_{mri_to_process.id}_t2ashs"])
 
        amy_to_process = AmyloidPET(subject, amydate)
        mri_amy_reg_to_process = MRIPetReg("amypet", mri_to_process, amy_to_process)
        
        logging.info(f"{mri_amy_reg_to_process.id}:{mri_amy_reg_to_process.mridate}:{mri_amy_reg_to_process.petdate}: Now processing")
        t1_amy_pet_reg_job = mri_amy_reg_to_process.do_t1_pet_reg()
        # mri_amy_reg_to_process.do_pet_reg_qc(t1_amy_pet_reg_job)
        mri_amy_reg_to_process.do_t2_pet_reg([t1_amy_pet_reg_job,f"{mri_to_process.mridate}_{mri_to_process.id}_t2ashs"])

        jobname_prefix_this_subject = f"{mri_to_process.mridate}_{mri_to_process.id}*"
        mri_to_process.mripetstats(wait_code=jobname_prefix_this_subject,
                t1tau = mri_tau_reg_to_process.t1_reg_nifti, 
                t2tau = mri_tau_reg_to_process.t2_reg_nifti,
                t1amy = mri_amy_reg_to_process.t1_reg_nifti,
                t2amy = mri_amy_reg_to_process.t2_reg_nifti, 
                taudate = mri_tau_reg_to_process.petdate,
                amydate = mri_amy_reg_to_process.petdate) 


def final_data_sheets():
    print(f"this is the final data sheet collation.")

def main():
    #### already have new scans downloaded to cluster
    ##TODO: date for dl folder as argument to this script
    # os.system(bash organize_files.sh "Sep2023") 
    print(f"bash organize_files.sh --symlink, unzip, rsync")

    #### already have adni spreadsheets saved in clustr
    # os.system(python datasetup.py) #to get UID & processing status lists 
    print(f"python datasetup.py --cleans ADNI csvs, merges data and selects correct UIDs")

    ## Do dicom-nifti conversion for new amy, tau, mri scans & do mri image processing
    for scantype in scantypes:
        if scantype == "anchored":
            continue
        else:
            logging.info(f"Now processing csv for {scantype}")
            df=pd.read_csv(os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status'][scantype]))
            # print(df.head())

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
                    uids={"t1_uid": str(row['IMAGEUID_T1']).split(".")[0],"t2_uid": str(row['IMAGEUID_T2']).split('.')[0]} #'flair_uid': str(row['IMAGEUID_FLAIR'])
                elif scantype == "amy":
                    scan_to_process = AmyloidPET(subject,scandate)
                    uids = {'amy_uid':str(row["IMAGEID"]).split(".")[0]}
                elif scantype == 'tau':
                    scan_to_process = TauPET(subject,scandate)
                    uids = {'tau_uid':str(row["IMAGEID"]).split(".")[0]}

                logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:{scantype}: Checking for nifti file.")

                for key in uids:
                    result = subprocess.run(
                            ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/dicom_to_nifti.sh",\
                            scan_to_process.id,scan_to_process.scandate,uids[key],\
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
                    else:
                        status = result_list[0]
                    
                    logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Nifti conversion status for {key} is:{status}")

                    if status == "conversion to nifti sucessful":
                        nifti_file_loc_public = result_list[2]
                        # print(f"Nifti filepath: {nifti_file_loc_public}")
                        if key == "t1_uid":
                            nifti_file_loc_dataset = scan_to_process.t1nifti
                            df_newscans.at[index,'FINALT1NIFTI'] = nifti_file_loc_public
                            df_newscans.at[index,'T1_CONVERT_STATUS'] = 1
                        elif key == "t2_uid":
                            nifti_file_loc_dataset = scan_to_process.t2nifti
                            df_newscans.at[index,'FINALT2NIFTI'] = nifti_file_loc_public
                            df_newscans.at[index,'T2_CONVERT_STATUS'] = 1
                        #elif key == "flair_uid":
                            # nifti_file_loc_dataset = scan_to_process.flair
                            # df_newscans.at[index,'FINALFLAIRNIFTI'] = nifti_file_loc_public
                            # df_newscans.at[index,'FLAIR_CONVERT_STATUS'] = 1
                        elif key == "amy_uid":
                            nifti_file_loc_dataset = scan_to_process.amy_nifti
                            df_newscans.at[index,'FILELOC'] = nifti_file_loc_public
                            df_newscans.at[index,'AMYNIFTI'] = nifti_file_loc_dataset
                            df_newscans.at[index,'AMY_CONVERT_STATUS'] = 1
                        elif key == "tau_uid":
                            nifti_file_loc_dataset = scan_to_process.tau_nifti
                            df_newscans.at[index,'FILELOC'] = nifti_file_loc_public
                            df_newscans.at[index,'TAUNIFTI'] = nifti_file_loc_dataset
                            df_newscans.at[index,'TAU_CONVERT_STATUS'] = 1

                        # make symlink for nifti file between /PUBLIC and /dataset
                        # print(f"ln -sf {nifti_file_loc_public} {nifti_file_loc_dataset}") 
                        os.system(f"ln -sf {nifti_file_loc_public} {nifti_file_loc_dataset}")
                        
                ##MRI only steps:
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

                    #baseline scan date
                    alldates = df_newscans.loc[df_newscans['ID'] == scan_to_process.id]['SMARTDATE'].values.tolist()
                    alldates.sort()
                    df_newscans.at[index,"BLSCANDATE"] = alldates[0]

                    ###MRI Image processing (ANTS, ASHS, etc.)
                    if os.path.exists(scan_to_process.t1nifti):
                        logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Doing MRI T1 image processing.")
                        # ants_job_name = scan_to_process.do_ants()
                        # scan_to_process.do_pmtau(ants_job_name)
                        # wbseg_job_name = scan_to_process.do_wbseg(ants_job_name) 
                        # scan_to_process.do_wbsegqc(wbseg_job_name)
                        scan_to_process.do_t1icv() 
                        superres_job_name = scan_to_process.do_superres() 
                        t1ashs_job_name = scan_to_process.do_t1ashs(superres_job_name) 
                        t1mtthk_job_name = scan_to_process.do_t1mtthk(t1ashs_job_name) 
                        scan_to_process.do_ashs_stats(f"{scan_to_process.mridate}_{scan_to_process.id}*")  
                            #ashs T1 stats only runs once all the other image processing for this subject is done

                    if os.path.exists(scan_to_process.t2nifti):
                        logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Doing MRI T2 image processing.")
                        t2_ashs_job_name = scan_to_process.do_t2ashs() 
                        scan_to_process.prc_cleanup(t2_ashs_job_name)
                    
                    if os.path.exists(scan_to_process.flair):
                        scan_to_process.do_t1flair() 
                        scan_to_process.do_wmh_prep() 

                    scan_to_process.mripetstats(wait_code=f"{scan_to_process.mridate}_{scan_to_process.id}*")

            ##after all rows in iterrows
            logging.info(f"{scantype}:Saving file location csv with new data")
            old_fileloc_path = [os.path.join(fileloc_directory_previousrun,x) for x in \
                                os.listdir(fileloc_directory_previousrun) if scantype in x][0]
            old_filelocs_df = pd.read_csv(old_fileloc_path)

            # ##for transition from old sheets to versions produced by this pipeline
            # if "SCANDATE" in [col for col in old_filelocs_df.columns]:
            #     old_filelocs_df.rename(columns={'SCANDATE':"SMARTDATE"},inplace=True) 
            # reformat_date_slash_to_dash(old_filelocs_df)
            
            all_filelocs = pd.concat([df_newscans, old_filelocs_df], ignore_index=True)
            #keep most recent (e.g. updated) if any duplicates
            all_filelocs.drop_duplicates(subset=['RID','SMARTDATE'],keep='last', inplace=True) 
            all_filelocs.sort_values(by=["RID","SMARTDATE"], ignore_index=True, inplace=True)
            all_filelocs.to_csv(os.path.join(datasetup_directories_path["filelocations"],\
                                                filenames['filelocations'][scantype]),index=False,header=True)


    # logging.info(f"Starting PET/MRI image registration processing based on anchored processing_status csv.")
    # anchored_df=pd.read_csv(os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status']["anchored"]))
    # print(anchored_df.head())
    # for index,row in anchored_df.iterrows():
    #     subject = str(row['ID'])
    #     mridate = str(row['SMARTDATE.mri'])
    #     taudate = str(row['SMARTDATE.tau'])
    #     amydate = str(row['SMARTDATE.amy'])
    
    #     mri_to_process = MRI(subject,mridate)

    #     tau_to_process = TauPET(subject, taudate)
    #     mri_tau_reg_to_process = MRIPetReg("taupet", mri_to_process, tau_to_process)
        
    #     logging.info(f"{mri_tau_reg_to_process.id}:{mri_tau_reg_to_process.mridate}:{mri_tau_reg_to_process.petdate}: Now processing")
    #     t1_tau_pet_reg_job = mri_tau_reg_to_process.do_t1_pet_reg()
    #     # mri_tau_reg_to_process.do_pet_reg_qc(t1_tau_pet_reg_job)
    #     mri_tau_reg_to_process.do_t2_pet_reg([t1_tau_pet_reg_job,f"{mri_to_process.mridate}_{mri_to_process.id}_t2ashs"])
 
    #     amy_to_process = AmyloidPET(subject, amydate)
    #     mri_amy_reg_to_process = MRIPetReg("amypet", mri_to_process, amy_to_process)
        
    #     logging.info(f"{mri_amy_reg_to_process.id}:{mri_amy_reg_to_process.mridate}:{mri_amy_reg_to_process.petdate}: Now processing")
    #     t1_amy_pet_reg_job = mri_amy_reg_to_process.do_t1_pet_reg()
    #     # mri_amy_reg_to_process.do_pet_reg_qc(t1_amy_pet_reg_job)
    #     mri_amy_reg_to_process.do_t2_pet_reg([t1_amy_pet_reg_job,f"{mri_to_process.mridate}_{mri_to_process.id}_t2ashs"])

    #     jobname_prefix_this_subject = f"{mri_to_process.mridate}_{mri_to_process.id}*"
    #     mri_to_process.mripetstats(wait_code=jobname_prefix_this_subject,
    #             t1tau = mri_tau_reg_to_process.t1_reg_nifti, 
    #             t2tau = mri_tau_reg_to_process.t2_reg_nifti,
    #             t1amy = mri_amy_reg_to_process.t1_reg_nifti,
    #             t2amy = mri_amy_reg_to_process.t2_reg_nifti, 
    #             taudate = mri_tau_reg_to_process.petdate,
    #             amydate = mri_amy_reg_to_process.petdate) 
    # ########end of anchored_df.iterrows for loop 

   
    #job to watch queue for status of all image processing & individual stats collection
    # print(f'bsub -J "{current_date}_queuewatch" -o {this_output_dir} ./queue_watch.sh')
    os.system(f'bsub -J "{current_date}_queuewatch" -o {this_output_dir} ./queue_watch.sh')
    
    logging.info(f"Collecting data from analysis_output/stats/ for data sheets.")
    # print(f'bsub -J "{current_date}_datasheets" -w "done({current_date}_queuewatch)" -o {this_output_dir} \
    #       ./create_stats_sheets.sh {wblabel_file} {stats_output_dir} {this_output_dir}')
    os.system(f'bsub -J "{current_date}_datasheets" -w "done({current_date}_queuewatch)" -o {this_output_dir} \
              ./create_stats_sheets.sh {wblabel_file} {stats_output_dir} {this_output_dir}')
    

    ##This step not needed as part of this code (additional data merges done separately or as needed)
    # logging.info(f"Performing final merge between datasheets and fileloc csvs.")
    # # print(f'bsub -J "{current_date}_finalmerge" -o {this_output_dir} \
    # #           -w "done({current_date}_datasheets)" ./merge_stats_fileloc_csvs.py')
    # os.system(f'bsub -J "{current_date}_finalmerge" -o {this_output_dir} \ 
    #           -w "done({current_date}_datasheets)" python merge_stats_fileloc_csvs.py')


#Arguments
global_parser = argparse.ArgumentParser()
subparsers = global_parser.add_subparsers(title="Subcommands", help="Sections of ADNI processing pipeline.")

unpack_dicoms_parser = subparsers.add_parser("unpack_dicoms", help="Unzip dicom files and rsync to /dataset.")
unpack_dicoms_parser.set_defaults(func=unpack_dicoms)

datasetup_parser = subparsers.add_parser("data_setup", help="Run datasetup.py.")
datasetup_parser.set_defaults(func=data_setup)

convert_parser = subparsers.add_parser("convert_symlink", help="Convert dicoms to nifti, symlink, create csv with filelocations.")
convert_parser.add_argument("-c", "--csv", required=False, help="csv with ID and Date, UID of images of sessions to process if not using default")
###TODO: multiple csvs
convert_parser.add_argument("-t","--type", choices=["amy","tau","mri","all"], help="Run conversion for tau, amy, or mri dicoms; or run for all three.")
convert_parser.set_defaults(func=convert_symlink)


mri_image_proc_parser = subparsers.add_parser("mri_image_processing", help="process mri images")
##TODO:mutually exclusive options: select steps or run all (here & convert & reg)
#mristep_or_all_group = mri_image_proc_parser.add_mutually_exclusive_group(required=True)
mri_image_proc_parser.add_argument("-s", '--steps', nargs="+", choices=mri_processing_steps, help="Processing step(s) to run.")
mri_image_proc_parser.add_argument("-c", "--csv", required=False, help="csv with column 'ID' in format 999_S_9999 and \
    column 'SMARTDATE' in format YYYY-MM-DD of sessions to process if not using default.")
mri_image_proc_parser.set_defaults(func=mri_image_processing)


mri_pet_reg_parser = subparsers.add_parser("mri_pet_registration", help="Do mri-pet registration and stats.")
mri_pet_reg_parser.add_argument("-s", '--steps', nargs="+", choices=registration_steps, help="Processing step(s) to run.")
mri_pet_reg_parser.add_argument("-c", "--csv", required=False, help="csv with column 'ID' in format 999_S_9999, columns \
    'SMARTDATE.tau', 'SMARTDATE.mri', 'SMARTDATE.amy', all in format YYY-MM-DD of sessions to process if not using default.")
mri_pet_reg_parser.set_defaults(func=mri_pet_registration)


final_data_sheet_parser = subparsers.add_parser("final_data_sheets", help="Collect individual stats into final sheets.")
final_data_sheet_parser.set_defaults(func=final_data_sheets)


args = global_parser.parse_args()

##removes any non-kwargs values to pass to args.func()
args_ = vars(args).copy()
args_.pop('func', None) 

args.func(**args_)


# main()