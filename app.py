import argparse
import csv
import datetime
import logging
import os
import pandas as pd
import subprocess
# Classes
from processing import MRI, AmyloidPET, TauPET, MRIPetReg
#variables
from processing import convert_to_nifti, wblabel_file, cleanup_dir, analysis_output_dir, current_date, pmtau_template_dir
from config import *

this_output_dir = f"{analysis_output_dir}/{current_date}"


def main():
    #### already have new scans downloaded to cluster
    # os.system(bash organize_files.sh) #run once overall
    print(f"bash organize_files.sh --symlink, unzip, rsync")

    #### already have adni spreadsheets saved in clustr
    # os.system(python datasetup.py) to get UID & fileloc lists 
    print(f"python datasetup.py --cleans ADNI csvs, merges data and selects correct UIDs")


    for file in os.listdir(datasetup_directories_path["uids_process_status"]):
        print(f"do this file: {file}")
        #except for tau-anchored file
        ##do nifti conversion for T1, T2, tau, amy
            #pd.read_csv(file)
            
            # bash dicom_to_nifti.sh id scandate uids class.name
            # return nifti fileloc, status

         #   uids={"t1_uid": str(row['IMAGUID_T1']),"t2_uid": str(row['IMAGUID_T2']).split('.')[0]}
    #         for key in uids:
    #             result = subprocess.run(
    #                 ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/dicom_to_nifti.sh",\
    #                 mri_to_process.id,mri_to_process.mridate,uids[key],mri_to_process.__class__.__name__], 
    #                 capture_output=True, text=True)
    #             ##TODO: handle any errors 
    #             result_list = result.stdout.split("\n")
    #             status = result_list[0]
    #             logging.info(f"{mri_to_process.id}:{mri_to_process.mridate}:Nifti conversion status is:{status}")




    #do mri processing

    #do tau-mri processing
    #do amy-mri processing



    # "/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230628_uids_process_status/mri_uids_processing_status.csv"
    # uid_df = pd.read_csv("/project/wolk/ADNI2018/scripts/pipeline_test_data/mri_uids_new.csv")
    # scans_to_process = uid_df.loc[uid_df["NEW_currentdate"] == 1]
    # for index, row in scans_to_process.iterrows():
    #     subject = str(row['ID'])
    #     mridate = str(row['SMARTDATE'])

    #     # subject = "099_S_6175"
    #     # mridate = "2020-06-03"
    #     taudate = "2020-07-09"
    #     amydate = "2020-07-08"
        
    #     if mode == "mri" or mode == "both":
    #         mri_to_process = MRI(subject,mridate)
    #         logging.info(f"{mri_to_process.id}:{mri_to_process.mridate}: Now processing")

    #         uids={"t1_uid": str(row['IMAGUID_T1']),"t2_uid": str(row['IMAGUID_T2']).split('.')[0]}
    #         for key in uids:
    #             result = subprocess.run(
    #                 ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/dicom_to_nifti.sh",\
    #                 mri_to_process.id,mri_to_process.mridate,uids[key],mri_to_process.__class__.__name__], 
    #                 capture_output=True, text=True)
    #             ##TODO: handle any errors 
    #             result_list = result.stdout.split("\n")
    #             status = result_list[0]
    #             logging.info(f"{mri_to_process.id}:{mri_to_process.mridate}:Nifti conversion status is:{status}")


            # ants_job_name = mri_to_process.do_ants()
            # wbseg_job_name = mri_to_process.do_wbseg(ants_job_name) 
            # mri_to_process.do_wbsegqc(wbseg_job_name)
            # mri_to_process.do_t1icv() 
            # t2_ashs_job_name = mri_to_process.do_t2ashs() 
            # mri_to_process.prc_cleanup(t2_ashs_job_name)
            # mri_to_process.do_t1flair() 
            # mri_to_process.do_wmh_prep() 
            # superres_job_name = mri_to_process.do_superres() 
            # t1ashs_job_name = mri_to_process.do_t1ashs(superres_job_name) 
            # mri_to_process.do_t1mtthk(t1ashs_job_name) 
            # mri_to_process.do_pmtau(ants_job_name)

        # if mode == "pet" or mode == "both": 
        #     tau_to_process = TauPET(subject, taudate)
        #     mri_tau_reg_to_process = MRIPetReg("taupet", mri_to_process, tau_to_process)
        #     logging.info(f"{mri_tau_reg_to_process.id}:{mri_tau_reg_to_process.mridate}:{mri_tau_reg_to_process.petdate}: Now processing")
            # t1_tau_pet_reg_job = mri_tau_reg_to_process.do_t1_pet_reg()
            # mri_tau_reg_to_process.do_pet_reg_qc(t1_tau_pet_reg_job)
            # mri_tau_reg_to_process.do_t2_pet_reg(t1_tau_pet_reg_job)      

            # amy_to_process = AmyloidPET(subject, amydate)
            # mri_amy_reg_to_process = MRIPetReg("amypet", mri_to_process, amy_to_process)
            # logging.info(f"{mri_amy_reg_to_process.id}:{mri_amy_reg_to_process.mridate}:{mri_amy_reg_to_process.petdate}: Now processing")
            # t1_amy_pet_reg_job = mri_amy_reg_to_process.do_t1_pet_reg()
            # mri_amy_reg_to_process.do_pet_reg_qc(t1_amy_pet_reg_job)
            # mri_amy_reg_to_process.do_t2_pet_reg(t1_amy_pet_reg_job)

        #bsub this so it runs after all processing steps
        #for mri mode, t1& t2 -pet reg need to be assigned
        # print(f"run stats.sh")
        # print(f"./stats.sh {mri_to_process.id} {mri_to_process.wbseg} {mri_to_process.thickness} \
        #         {mri_tau_reg_to_process.t1_reg_nifti} {mri_tau_reg_to_process.t2_reg_nifti} \
        #         {mri_amy_reg_to_process.t1_reg_nifti} {mri_amy_reg_to_process.t2_reg_nifti} \
        #         {mri_to_process.t2ahs_cleanup_left} {mri_to_process.t2ahs_cleanup_right} \
        #         {mri_to_process.t2ahs_cleanup_both} {mri_to_process.t1trim} {mri_to_process.icv_file} \
        #         {mode} {wblabel_file} {pmtau_template_dir}") 

    #### once all subject,dates completed:
    # os.system(f"mkdir {this_output_dir}")
    # if mode == both, do once for mri, once for pet; otherwise, just do once 
    # os.system(f"bash create_tsv.sh {wblabel_file} {cleanup_dir} {this_output_dir}")




#Logging
#### Log file
# logging.basicConfig(filename=f"{adni_analysis_dir}/{current_date}.log", filemode='w', format="%(levelname)s:%(message)s", level=logging.INFO)
#### for testing:            
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

#Arguments
ap = argparse.ArgumentParser()
ap.add_argument('-m', '--mode', required=False,  action='store', help='Options: mri, pet, or both')
ap.add_argument('-s', '--steps', required=False,  action='store', help='only run particular processing step')
args = ap.parse_args()
# mode=args.mode
# main(mode)

main()