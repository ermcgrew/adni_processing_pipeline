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


def main():
    #### already have new scans downloaded to cluster
    # os.system(bash organize_files.sh) 
    print(f"bash organize_files.sh --symlink, unzip, rsync")

    #### already have adni spreadsheets saved in clustr
    # os.system(python datasetup.py) #to get UID & processing status lists 
    print(f"python datasetup.py --cleans ADNI csvs, merges data and selects correct UIDs")

    ## Do dicom-nifti conversion for new amy, fdg, tau, mri scans & do mri image processing
    # for scantype in scantypes:
    #     if scantype == "anchored":
    #         continue
    #     else:
    #         logging.info(f"Now processing csv for {scantype}")
    #         df=pd.read_csv(os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status'][scantype]))
    #         # print(df.head())

    #         if scantype == 'mri':
    #             df_newscans = df.loc[(df['NEW_T1'] == 1) | (df['NEW_T2'] == 1)] # | df['NEW_FLAIR'] == 1
    #         else:
    #             df_newscans = df.loc[(df['NEW_PET'] == 1)]

    #         ##Start converting dicom to nifti, line by line    
    #         for index,row in df_newscans.iterrows():
    #             subject = str(row['ID'])
    #             scandate = str(row['SMARTDATE'])
    #             if scantype == 'mri':
    #                 scan_to_process = MRI(subject,scandate)
    #                 ##TODO: Flair dicom to nifti processing--add flair dicom to uid csvs
    #                 uids={"t1_uid": str(row['IMAGEUID_T1']).split(".")[0],"t2_uid": str(row['IMAGEUID_T2']).split('.')[0]} #'flair_uid': str(row['IMAGEUID_FLAIR'])
    #             elif scantype == "amy":
    #                 scan_to_process = AmyloidPET(subject,scandate)
    #                 uids = {'amy_uid':str(row["IMAGEID"])}
    #             elif scantype == 'tau':
    #                 scan_to_process = TauPET(subject,scandate)
    #                 uids = {'tau_uid':str(row["IMAGEID"])}

    #             logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:{scantype}: Checking for nifti file.")

    #             for key in uids:
    #                 result = subprocess.run(
    #                         ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/dicom_to_nifti.sh",\
    #                         scan_to_process.id,scan_to_process.scandate,uids[key],\
    #                             scan_to_process.__class__.__name__,scan_to_process.log_output_dir], 
    #                         capture_output=True, text=True)
    #                 if result.returncode != 0:
    #                     logging.warning(f"{scan_to_process.id}:{scan_to_process.scandate}:\
    #                                     dicom_to_nifti.sh error {result.returncode}:{result.stderr}")
    #                     continue

    #                 result_list = result.stdout.split("\n")
    #                 if len(result_list) > 3:
    #                     #first item is "Job <###> submitted to queue..."
    #                     status = result_list[1]
    #                 else:
    #                     status = result_list[0]
                    
    #                 logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Nifti conversion status for {key} is:{status}")

    #                 if status == "conversion to nifti sucessful":
    #                     nifti_file_loc_public = result_list[2]
    #                     # print(f"Nifti filepath: {nifti_file_loc_public}")
    #                     if key == "t1_uid":
    #                         nifti_file_loc_dataset = scan_to_process.t1nifti
    #                         df_newscans.at[index,'FINALT1NIFTI'] = nifti_file_loc_public
    #                         df_newscans.at[index,'T1_CONVERT_STATUS'] = 1
    #                     elif key == "t2_uid":
    #                         nifti_file_loc_dataset = scan_to_process.t2nifti
    #                         df_newscans.at[index,'FINALT2NIFTI'] = nifti_file_loc_public
    #                         df_newscans.at[index,'T2_CONVERT_STATUS'] = 1
    #                     #elif key == "flair_uid":
    #                         # nifti_file_loc_dataset = scan_to_process.flair
    #                         # df_newscans.at[index,'FINALFLAIRNIFTI'] = nifti_file_loc_public
    #                         # df_newscans.at[index,'FLAIR_CONVERT_STATUS'] = 1
    #                     elif key == "amy_uid":
    #                         nifti_file_loc_dataset = scan_to_process.amy_nifti
    #                         df_newscans.at[index,'FILELOC'] = nifti_file_loc_public
    #                         df_newscans.at[index,'AMYNIFTI'] = nifti_file_loc_dataset
    #                         df_newscans.at[index,'AMY_CONVERT_STATUS'] = 1
    #                     elif key == "tau_uid":
    #                         nifti_file_loc_dataset = scan_to_process.tau_nifti
    #                         df_newscans.at[index,'FILELOC'] = nifti_file_loc_public
    #                         df_newscans.at[index,'TAUNIFTI'] = nifti_file_loc_dataset
    #                         df_newscans.at[index,'TAU_CONVERT_STATUS'] = 1

    #                     # make symlink for nifti file between /PUBLIC and /dataset
    #                     # print(f"ln -sf {nifti_file_loc_public} {nifti_file_loc_dataset}") 
    #                     os.system(f"ln -sf {nifti_file_loc_public} {nifti_file_loc_dataset}")
                        
    #             ##MRI only steps:
    #             if scantype == "mri":
    #                 logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Finding additional information for mri filelocation csv.")
    #                 #site's vendor & model info
    #                 site = scan_to_process.id.split("_")[0]
    #                 siteinfo_result = subprocess.run(
    #                     ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/get_site_scanner_info.sh",site],
    #                     capture_output=True, text=True)
    #                 siteinfo_result_list = siteinfo_result.stdout.split("\n")[:-1] # remove extra newline at end
    #                 siteinfo_headers = ["Model2","Model3","Vendor2","Vendor3"]
    #                 for i in range(0,len(siteinfo_result_list)):
    #                     df_newscans.at[index,siteinfo_headers[i]] = siteinfo_result_list[i]

    #                 #baseline scan date
    #                 alldates = df_newscans.loc[df_newscans['ID'] == scan_to_process.id]['SMARTDATE'].values.tolist()
    #                 alldates.sort()
    #                 df_newscans.at[index,"BLSCANDATE"] = alldates[0]

    #                 ###MRI Image processing (ANTS, ASHS, etc.)
    #                 if os.path.exists(scan_to_process.t1nifti):
    #                     logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Doing MRI T1 image processing.")
    #                     # ants_job_name = scan_to_process.do_ants()
    #                     # scan_to_process.do_pmtau(ants_job_name)
    #                     # wbseg_job_name = scan_to_process.do_wbseg(ants_job_name) 
    #                     # scan_to_process.do_wbsegqc(wbseg_job_name)
    #                     # scan_to_process.do_t1icv() 
    #                     # superres_job_name = scan_to_process.do_superres() 
    #                     # t1ashs_job_name = scan_to_process.do_t1ashs(superres_job_name) 
    #                     # t1mtthk_job_name = scan_to_process.do_t1mtthk(t1ashs_job_name) 
    #                     # scan_to_process.do_ashs_stats(f"*{scan_to_process.id}") 
    #                         #so stats only runs once all the other image processing for this subject is done

    #                 if os.path.exists(scan_to_process.t2nifti):
    #                     logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Doing MRI T2 image processing.")
    #                     t2_ashs_job_name = scan_to_process.do_t2ashs() 
    #                     scan_to_process.prc_cleanup(t2_ashs_job_name)
                    
    #                 scan_to_process.testallstats(f"*{scan_to_process.id}")

    #                 if os.path.exists(scan_to_process.flair):
    #                     scan_to_process.do_t1flair() 
    #                     scan_to_process.do_wmh_prep() 

    #             # testwaitcode=f"*{scan_to_process.id}"
    #         ##after all rows in iterrows
    #         logging.info(f"{scantype}:Saving file location csv with new data")
    #         old_fileloc_path = [os.path.join(fileloc_directory_previousrun,x) for x in \
    #                             os.listdir(fileloc_directory_previousrun) if scantype in x][0]
    #         old_filelocs = pd.read_csv(old_fileloc_path)
    #         all_filelocs = pd.concat([df_newscans, old_filelocs], ignore_index=True)
    #         #keep most recent (e.g. updated) if any duplicates
    #         all_filelocs.drop_duplicates(subset=['RID','SMARTDATE'],keep='last', inplace=True) 
    #         all_filelocs.sort_values(by=["RID","SMARTDATE"], ignore_index=True, inplace=True)
    #         all_filelocs.to_csv(os.path.join(datasetup_directories_path["filelocations"],\
    #                                             filenames['filelocations'][scantype]),index=False,header=True)

    # print(testwaitcode)
    logging.info(f"Starting anchored processing for PET & MRI matches.")
    anchored_df=pd.read_csv(os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status']["anchored"]))
    # print(anchored_df.head())

    for index,row in anchored_df.iterrows():
        subject = str(row['ID'])
        mridate = str(row['SMARTDATE.mri'])
        taudate = str(row['SMARTDATE.tau'])
        amydate = str(row['SMARTDATE.amy'])
    
        mri_to_process = MRI(subject,mridate)
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

        job_wait_code = f"*{mri_to_process.id}_*_to_{mri_to_process.mridate}"
        mri_to_process.testallstats(wait_code=job_wait_code,
                t1tau = mri_tau_reg_to_process.t1_reg_nifti, 
                t2tau = mri_tau_reg_to_process.t2_reg_nifti,
                t1amy = mri_amy_reg_to_process.t1_reg_nifti,
                t2amy = mri_amy_reg_to_process.t2_reg_nifti) 
    ########end of dfiterrows for loop 

    logging.info(f"Collecting data from analysis_output/stats/ for data sheets.")
    print(f"bsub -J '{current_date}_datasheets' -w 'done()' -o {this_output_dir} create_stats_sheets.sh {wblabel_file} {stats_output_dir} {this_output_dir}")
    # os.system(f"bsub -J '{current_date}_datasheets' -o {this_output_dir} -w 'done()' \
    #           bash create_stats_sheets.sh {wblabel_file} {stats_output_dir} {this_output_dir}")
    ##TODO: what's the wait code--last subject processed?
        #bsub a job before this that just watches the queue: 
        #while $(bjobs | grep "emcgrew RUN" | wc -l) > 0:
            #sleep 8
        #hang the stats collection off the completion of that job?

    ##TODO: pandas merge stats with fileloc csvs, demographic data, baseline scan date & date diff


#Arguments
# ap = argparse.ArgumentParser()
# ap.add_argument('-m', '--mode', required=False,  action='store', help='Options: mri, pet, or both')
# ap.add_argument('-s', '--steps', required=False,  action='store', help='only run particular processing step')
# args = ap.parse_args()
# mode=args.mode
# main(mode)

main()