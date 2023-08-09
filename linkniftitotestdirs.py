#!/usr/bin/env python3
import pandas as pd
import subprocess
import os

from processing import MRI, AmyloidPET, TauPET, MRIPetReg
#variables
from config import *

##adding nifti symlinks to testing folders for existing niftis
for scantype in scantypes:
        if scantype == "anchored":
            continue
        else:
            df=pd.read_csv(os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status'][scantype]))
            # print(df.head())

            ##Start converting dicom to nifti, line by line    
            for index,row in df.iterrows():
                subject = str(row['ID'])
                scandate = str(row['SMARTDATE'])
                if scantype == 'mri':
                    scan_to_process = MRI(subject,scandate)
                    uids={"t1_uid": str(row['IMAGEUID_T1']).split(".")[0],"t2_uid": str(row['IMAGEUID_T2']).split('.')[0]}
                elif scantype == "amy":
                    scan_to_process = AmyloidPET(subject,scandate)
                    uids = {'amy_uid':str(row["IMAGEID"])}
                elif scantype == 'tau':
                    scan_to_process = TauPET(subject,scandate)
                    uids = {'tau_uid':str(row["IMAGEID"])}

                for key in uids:
                    result = subprocess.run(
                        [f"/project/wolk/ADNI2018/scripts/adni_processing_pipeline/getniftipublic.sh", subject,scandate], 
                        capture_output=True, text=True)
                    # print(result)
                    if result.stderr != "":
                        continue
                    else:    
                        result_list = result.stdout.split("\n")
                        # print(result_list[0])
                        nifti_file_loc_public = result_list[0]

                    if key == "t1_uid":
                        nifti_file_loc_dataset = scan_to_process.t1nifti
                    
                    elif key == "t2_uid":
                        nifti_file_loc_dataset = scan_to_process.t2nifti
                       
                    elif key == "amy_uid":
                        nifti_file_loc_dataset = scan_to_process.amy_nifti
                       
                    elif key == "tau_uid":
                        nifti_file_loc_dataset = scan_to_process.tau_nifti
                       
                    if not os.path.exists(nifti_file_loc_dataset):
                        print(f"link {nifti_file_loc_public} :: {nifti_file_loc_dataset}")
                        # print(scan_to_process.id,scan_to_process.scandate,uids[key],\
                                # scan_to_process.__class__.__name__,scan_to_process.log_output_dir)
                        os.system(f"ln -sf {nifti_file_loc_public} {nifti_file_loc_dataset}")
                        # pass
                    # else:
                    #     print(f"this one already there: {nifti_file_loc_dataset}")
