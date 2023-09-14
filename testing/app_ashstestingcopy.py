#!/usr/bin/env python3

import argparse
import logging
import os
import pandas as pd
import subprocess
# Classes
from processing_ashstestingcopy import MRI
#variables
from config_ashstestingcopy import *

def main():
    df=pd.read_csv(os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status']["mri"]))
    df_newscans = df.loc[(df['NEW_T1'] == 1) | (df['NEW_T2'] == 1)] 
    for index,row in df_newscans.iterrows():
        subject = str(row['ID'])
        scandate = str(row['SMARTDATE'])
        print(scandate)
        if scandate == "2022-06-23" or scandate == "2022-07-01" or scandate == "2022-11-21" or scandate == "2022-10-17":
                continue 
        else:
            scan_to_process = MRI(subject,scandate)
            if os.path.exists(scan_to_process.t1nifti):
                logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Doing MRI T1 image processing.")
                scan_to_process.do_t1icv() 
                superres_job_name = scan_to_process.do_superres() 
                t1ashs_job_name = scan_to_process.do_t1ashs(superres_job_name) 
                t1mtthk_job_name = scan_to_process.do_t1mtthk(t1ashs_job_name) 
                scan_to_process.do_ashs_stats(f"{scan_to_process.mridate}_{scan_to_process.id}*")  

    #job to watch queue for status of all image processing & individual stats collection
    os.system(f'bsub -J "{current_date}_queuewatch" -o {this_output_dir} ./queue_watch.sh')
    
    logging.info(f"Collecting data from analysis_output/stats/ for data sheets.")
    os.system(f'bsub -J "{current_date}_datasheets" -w "done({current_date}_queuewatch)" -o {this_output_dir} \
              ./create_stats_sheets.sh {wblabel_file} {stats_output_dir} {this_output_dir}')


main()