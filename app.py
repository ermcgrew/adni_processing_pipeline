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
    # os.system(bash organize_files.sh) #run once overall
    print(f"bash organize_files.sh --symlink, unzip, rsync")

    #### already have adni spreadsheets saved in clustr
    # os.system(python datasetup.py) to get UID & fileloc lists 
    print(f"python datasetup.py --cleans ADNI csvs, merges data and selects correct UIDs")

    ## Do dicom-nifti conversion for new amy, fdg, tau, mri scans & do additional mri processing
    for scantype in scantypes:
        if scantype == "anchored":
            continue
        else:
            logging.info(f"Now processing csv for {scantype}")
            df=pd.read_csv(os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status'][scantype]))
            # print(df.head())

            if scantype == 'mri':
                df_newscans = df.loc[(df['NEW_T1'] == 1) | (df['NEW_T2'] == 1)]
            else:
                df_newscans = df.loc[(df['NEW_PET'] == 1)]

            for index,row in df_newscans.iterrows():
                subject = str(row['ID'])
                scandate = str(row['SMARTDATE'])
                if scantype == 'tau':
                    scan_to_process = TauPET(subject,scandate)
                    uids = {'tau_uid':str(row["IMAGEID"])}
                elif scantype == "amy":
                    scan_to_process = AmyloidPET(subject,scandate)
                    uids = {'amy_uid':str(row["IMAGEID"])}
                elif scantype == 'mri':
                    scan_to_process = MRI(subject,scandate)
                    uids={"t1_uid": str(row['IMAGUID_T1']),"t2_uid": str(row['IMAGUID_T2']).split('.')[0]}
                
                # logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}: Now processing")
                df_newscans.loc[index,'TESTCOLUMN'] ='testdata'

                # for key in uids:
                #     result = subprocess.run(
                #             ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/dicom_to_nifti.sh",\
                #             scan_to_process.id,scan_to_process.scandate,uids[key],scan_to_process.__class__.__name__], 
                #             capture_output=True, text=True)
                #     ##TODO: handle any errors 
                #     result_list = result.stdout.split("\n")
                #     status = result_list[0]
                #     logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Nifti conversion status for {key} is:{status}")

                #     if status == "conversion to nifti sucessful":
                #         nifti_file_loc_public = result_list[1]
                #         print(f"Nifti filepath: {nifti_file_loc_public}")
                #         if key == "t1_uid":
                #             df_newscans.at[index,'FINALT1NIFTI'] = nifti_file_loc_public
                #             df_newscans.at[index,'T1_PROCESS_STATUS'] = 1
                #         elif key == "t2_uid":
                #             df_newscans.at[index,'FINALT2NIFTI'] = nifti_file_loc_public
                #             df_newscans.at[index,'T2_PROCESS_STATUS'] = 1
                #         ##TODO: add PET fileloc data to df
                    
                #         ##TODO: create var for each scantype for dataset location of nifti file--use class.
                #         dataset_nifti = ''
                #         # make sym link between /PUBLIC and /dataset
                #         print(f"ln -sf {nifti_file_loc_public} {dataset_nifti}") 
                #         # os.system(f"ln -sf {nifti_file_loc_public} {dataset_nifti}")

                # ##Additional information for MRI fileloc csv
                # if scantype == "mri":
                #     #fill in site vendor & model info
                #     site = id.split("_")[0]
                #     siteinfo_result = subprocess.run(
                #         ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/get_site_scanner_info.sh",site],
                #         capture_output=True, text=True)
                #     siteinfo_result_list = siteinfo_result.stdout.split("\n")[:-1] # remove extra newline at end
                #     siteinfo_headers = ["Model2","Model3","Vendor2","Vendor3"]
                #     for i in range(0,len(siteinfo_result_list)):
                #         df_newscans.at[index,siteinfo_headers[i]] = siteinfo_result_list[i]

                #     #baseline scan date
                #     alldates = df_newscans.loc[df_newscans['ID'] == id]['SMARTDATE'].values.tolist()
                #     alldates.sort()
                #     df_newscans.at[index,"BLSCANDATE"] = alldates[0]

            if scantype == 'mri':
                print('do mri processing if MRI')
                 ##TODO: make sure this doesn't break if t1 or t2 is missing
        #             # ants_job_name = mri_to_process.do_ants()
        #             # wbseg_job_name = mri_to_process.do_wbseg(ants_job_name) 
        #             # mri_to_process.do_wbsegqc(wbseg_job_name)
        #             # mri_to_process.do_t1icv() 
        #             # t2_ashs_job_name = mri_to_process.do_t2ashs() 
        #             # mri_to_process.prc_cleanup(t2_ashs_job_name)
        #             # mri_to_process.do_t1flair() 
        #             # mri_to_process.do_wmh_prep() 
        #             # superres_job_name = mri_to_process.do_superres() 
        #             # t1ashs_job_name = mri_to_process.do_t1ashs(superres_job_name) 
        #             # mri_to_process.do_t1mtthk(t1ashs_job_name) 
        #             # mri_to_process.do_pmtau(ants_job_name)
            
        print(f"Save off all fileloc data for sheet {scantype}")
        #match scantype to fileloc_directory_previousrun file with same scantype
        old_fileloc_path = [os.path.join(fileloc_directory_previousrun,x) for x in os.listdir(fileloc_directory_previousrun) if scantype in x][0]
        # old_filelocs = pd.read_csv(old_fileloc_path)
        # all_filelocs = pd.concat([df_newscans, old_filelocs], on=['RID','SMARTDATE'])
        # all_filelocs.drop_duplicates(subset=['RID','SMARTDATE'],keep='last',inplace=True) #keep most recent (updated) if any duplicates
        # print(all_filelocs.to_csv(os.path.join(datasetup_directories_path["filelocations"],filenames['filelocations'][scantype]),index=False,header=True))


    print("Do MRI-only stats here")
    ##TODO: write this

    print("Doing tau-anchored processing:")
    # ##TODO: grab tau-anchored csv
    # tau_anchored_csv = ""
    # tau_anchored_df = pd.read_csv(tau_anchored_csv)
    # for index,row in tau_anchored_df.iterrows():
    #     subject = str(row['ID'])
    #     mridate = str(row['MRIDATE']) ##TODO: make sure column names are correct
    #     taudate = str(row['TAUDATE'])
    #     amydate = str(row['AMYDATE'])
    #     mri_to_process = MRI(subject,scandate)
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


    ##TODO: bsub this so it runs after all processing steps
    print(f"run stats.sh")
    # print(f"./stats.sh {mri_to_process.id} {mri_to_process.wbseg} {mri_to_process.thickness} \
    #         {mri_tau_reg_to_process.t1_reg_nifti} {mri_tau_reg_to_process.t2_reg_nifti} \
    #         {mri_amy_reg_to_process.t1_reg_nifti} {mri_amy_reg_to_process.t2_reg_nifti} \
    #         {mri_to_process.t2ahs_cleanup_left} {mri_to_process.t2ahs_cleanup_right} \
    #         {mri_to_process.t2ahs_cleanup_both} {mri_to_process.t1trim} {mri_to_process.icv_file} \
    #         {wblabel_file} {pmtau_template_dir}") 
            ##TODO: remove mode from stats.sh file (2nd from last)


    
    print(f"now running create_tsv.sh with all info from completed processing")
    # os.system(f"mkdir {this_output_dir}")
    # os.system(f"bash create_tsv.sh {wblabel_file} {cleanup_dir} {this_output_dir}")


#Arguments
# ap = argparse.ArgumentParser()
# ap.add_argument('-m', '--mode', required=False,  action='store', help='Options: mri, pet, or both')
# ap.add_argument('-s', '--steps', required=False,  action='store', help='only run particular processing step')
# args = ap.parse_args()
# mode=args.mode
# main(mode)

main()