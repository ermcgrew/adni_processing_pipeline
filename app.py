import csv
import datetime
import logging
import os
## Classes:
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


def main():
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

                ##would this be the csv directly from adni?
                ##call to download dicom file from adni
                ## run dicom to nifti --this should be a general function for all scans
                ##then create t1 instance
                ##dicom location is saved in t1 class to add to final spreadsheet
                ##do we need to create the intermediate spreadsheets with nifti paths if we're not using db anymore?

                # print(subject, mridate)
                mri_to_process = MRI(subject,mridate)
                logging.info(f"{mri_to_process.id}:{mri_to_process.mridate}: Now processing")

                # ants_job_name = mri_to_process.do_ants()

                # wbseg_job_name = mri_to_process.do_wbseg(ants_job_name) 
                # mri_to_process.do_wbsegqc(wbseg_job_name)

                # mri_to_process.do_t1icv() 
                # mri_to_process.do_t2ashs() 
                # mri_to_process.do_t1flair() 
                # mri_to_process.do_wmh_prep() 

                # superres_job_name = mri_to_process.do_superres() 
                # t1ashs_job_name = mri_to_process.do_t1ashs(superres_job_name) 
                # mri_to_process.do_t1mtthk(t1ashs_job_name) 

                ##how to id mri-pet date pairings

                ##do mri-tau reg
                tau_to_process = TauPET(subject, "9999-99-99")
                logging.info(f"{tau_to_process.id}:{tau_to_process.taudate}: Now processing")

                mri_tau_reg_to_process = MRIPetReg("taupet", mri_to_process, tau_to_process)
                logging.info(f"{mri_tau_reg_to_process.id}:{mri_tau_reg_to_process.mridate}:{mri_tau_reg_to_process.petdate}: Now processing")
                # t1_pet_reg_job = mri_tau_reg_to_process.do_t1_pet_reg()
                # mri_tau_reg_to_process.do_pet_reg_qc(t1_pet_reg_job)
                # mri_tau_reg_to_process.do_t2_pet_reg(t1_pet_reg_job)      


                ##do mri-amy reg
                amy_to_process = AmyloidPET(subject, "9999-99-99")
                logging.info(f"{amy_to_process.id}:{amy_to_process.amydate}: Now processing")

                mri_amy_reg_to_process = MRIPetReg("amypet", mri_to_process, amy_to_process)
                logging.info(f"{mri_amy_reg_to_process.id}:{mri_amy_reg_to_process.mridate}:{mri_amy_reg_to_process.petdate}: Now processing")
                # t1_pet_reg_job = mri_amy_reg_to_process.do_t1_pet_reg()
                # mri_amy_reg_to_process.do_pet_reg_qc(t1_pet_reg_job)
                # mri_amy_reg_to_process.do_t2_pet_reg(t1_pet_reg_job)

                ##once reg done, call stats.sh
                ##capture t2_pet_reg job name as -w option for stats bsub?
                ##set mode for stats:
                stats_mri_only_mode=False

                print(f"./stats.sh {mri_to_process.id} {mri_to_process.wbseg} {mri_to_process.thickness} \
                      {mri_tau_reg_to_process.t1_reg_nifti} {mri_tau_reg_to_process.t2_reg_nifti} \
                      {mri_amy_reg_to_process.t1_reg_nifti} {mri_amy_reg_to_process.t2_reg_nifti} \
                      {mri_to_process.filepath}/sfsegnibtend/tse.nii.gz {mri_to_process.t1trim}\
                      {mri_to_process.t2ashs_seg_left} {stats_mri_only_mode}")


#Log file
# logging.basicConfig(filename=f"{adni_analysis_dir}/{current_date}.log", filemode='w', format="%(levelname)s:%(message)s", level=logging.INFO)
#for testing:            
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# csvlist=['MRI.csv','amy.csv','tau.csv']

main()
    