import csv
import datetime
import logging
import os
# Classes:
from processing import MRI, AmyloidPET, TauPET, MRIPetReg


def reformat_dates(date):
    MDYlist=date.split('/')
    if len(MDYlist[0]) == 1:
        month = "0" + MDYlist[0]
    else:
        month = MDYlist[0]
    if  len(MDYlist[1]) == 1:
        day = "0" + MDYlist[1]
    else:
        day=MDYlist[1]
    year="20" + MDYlist[2]
    return year + "-" + month + "-" + day

def open_csv():
    ##would this be the csv directly from adni?
    with open("../pipeline_test_data/MRI3TLIST_testdata.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count+=1
            else:
                line_count+=1
                subject = row[1]
                if "/" in row[6]:
                    mridate = reformat_dates(row[6])
                else:
                    mridate = row[6]


def main(mode):
    #### function: get new scans info from adni, return list of subject,date
    # open_csv()
        #### for each subject, date:
            #### function: download new dicom files from adni & sort into correct locations in cluster

            if mode == "mri" or mode == "both":
                mri_to_process = MRI(subject,mridate)
                logging.info(f"{mri_to_process.id}:{mri_to_process.mridate}: Now processing")
                #### function: dicom to nifti
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

            if mode == "pet" or mode == "both": 
                tau_to_process = TauPET(subject, taudate)
                mri_tau_reg_to_process = MRIPetReg("taupet", mri_to_process, tau_to_process)
                logging.info(f"{mri_tau_reg_to_process.id}:{mri_tau_reg_to_process.mridate}:{mri_tau_reg_to_process.petdate}: Now processing")
                # t1_tau_pet_reg_job = mri_tau_reg_to_process.do_t1_pet_reg()
                # mri_tau_reg_to_process.do_pet_reg_qc(t1_tau_pet_reg_job)
                # mri_tau_reg_to_process.do_t2_pet_reg(t1_tau_pet_reg_job)      

                amy_to_process = AmyloidPET(subject, amydate)
                mri_amy_reg_to_process = MRIPetReg("amypet", mri_to_process, amy_to_process)
                logging.info(f"{mri_amy_reg_to_process.id}:{mri_amy_reg_to_process.mridate}:{mri_amy_reg_to_process.petdate}: Now processing")
                # t1_amy_pet_reg_job = mri_amy_reg_to_process.do_t1_pet_reg()
                # mri_amy_reg_to_process.do_pet_reg_qc(t1_amy_pet_reg_job)
                # mri_amy_reg_to_process.do_t2_pet_reg(t1_amy_pet_reg_job)

            print(f"./stats.sh {mri_to_process.id} {mri_to_process.wbseg} {mri_to_process.thickness} \
                    {mri_tau_reg_to_process.t1_reg_nifti} {mri_tau_reg_to_process.t2_reg_nifti} \
                    {mri_amy_reg_to_process.t1_reg_nifti} {mri_amy_reg_to_process.t2_reg_nifti} \
                    {mri_to_process.t2ahs_cleanup_left} {mri_to_process.t2ahs_cleanup_right} \
                    {mri_to_process.t2ahs_cleanup_both} {mri_to_process.t1trim} {mode}") 
    
    #### once all subject,dates completed:
        #### collate all stats files to make tsv: create_tsv.sh
                

#### Log file
# logging.basicConfig(filename=f"{adni_analysis_dir}/{current_date}.log", filemode='w', format="%(levelname)s:%(message)s", level=logging.INFO)
#### for testing:            
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

#### file takes kwargs 
# mode: mri, pet, both
# options to call only certain processing steps

mode="both"

main(mode)

