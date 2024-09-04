#!/usr/bin/env python3

import logging
import os
import time
import pandas as pd
from config import *
import subprocess


''' Shared functions '''
def ready_to_process(processing_step, id, date, input_files = [], output_files = [], parent_job = []):
    #output files all "OR" comparisons, as long as 1 is true, output is present
    if [file for file in output_files if os.path.exists(file)]:
        logging.info(f"{id}:{date}: {processing_step} already run.")
        return False
    else:
        #assumes parent job will complete so all input files will be present 
        if parent_job:
            logging.info(f"{id}:{date}: Submitting {processing_step} to queue, will run when {parent_job} is complete")
            return True
        #input files all "AND" comparisons--all must be present to run
        elif len([file for file in input_files if os.path.exists(file)]) == len(input_files):
            logging.info(f"{id}:{date}: Running {processing_step}")
            return True
        else:
            missingfiles=[file for file in input_files if not os.path.exists(file)]
            logging.info(f"{id}:{date}: Cannot run {processing_step}, missing these input file(s) {missingfiles}")
            return False

### -w argument has to be in double quotes
def set_submit_options(this_job_name, output_dir, parent_job_name):
    jobname = f"-J {this_job_name}"
    output = f"-o {output_dir}/{this_job_name}_{current_date_time}.txt"
    if parent_job_name:
        if len(parent_job_name) == 2: 
            wait = f'-w "done({parent_job_name[0]}) && done({parent_job_name[1]})"'
        elif "stats" in this_job_name:  
            wait = f'-w "ended({parent_job_name[0]})"'
        else:
            wait = f'-w "done({parent_job_name[0]})"'
    else:   
        wait = ""
    return f"{jobname} {output} {wait}"


def wait_for_file(file):
    print(f"waiting for file {file} to be created.")
    counter = 0
    while not os.path.exists(file) and counter < 25:
        time.sleep(5)
        counter += 1
    
    if os.path.exists(file):
        while os.stat(file).st_size <= 10000:
            time.sleep(1)
        return "Success"
    else:
        return "Error"


''' Class definitions '''
class MRI:
    #strings for MRI filepaths and functions for MRI processing
    def __init__(self, subject, mridate):
        self.id = subject
        self.mridate = mridate
        self.scandate = mridate
        self.filepath=f"{adni_data_dir}/{self.id}/{self.mridate}"
        self.date_id_prefix = f"{self.mridate}_{self.id}"
        
        self.t1nifti = f"{self.filepath}/{self.date_id_prefix}_T1w.nii.gz"
        self.t1trim = f"{self.filepath}/{self.date_id_prefix}_T1w_trim.nii.gz"

        self.thick_dir = f"{self.filepath}/thickness"
        self.t1trim_thickness_dir = f"{self.filepath}/thickness/{self.id}PreprocessedInput.nii.gz"
        self.ants_brainseg = f"{self.filepath}/thickness/{self.id}BrainSegmentation.nii.gz"
        self.thickness = f"{self.filepath}/thickness/{self.id}CorticalThickness.nii.gz"
        self.pmtau_output = f"{self.filepath}/thickness/ap.nii.gz"
        self.brainx_thickness_dir = f"{self.filepath}/thickness/{self.id}ExtractedBrain0N4.nii.gz"
        
        self.brainx = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain.nii.gz"
        self.wbseg_dir = f"{self.date_id_prefix}_wholebrainseg/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain"
        self.wbseg_nifti = f"{self.filepath}/{self.wbseg_dir}/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz"
        self.wbsegqc_image = f"{self.filepath}/{self.date_id_prefix}_wbseg_qa.png"
        self.wbseg_propagated = f"{self.filepath}/{self.wbseg_dir}/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain_wholebrainseg_cortical_propagate.nii.gz"
        self.inferior_cereb_mask = f"{self.filepath}/{self.wbseg_dir}/inferior_cerebellum.nii.gz"
        
        self.superres_nifti = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_denoised_SR.nii.gz"
        
        self.t1ashs_seg_left = f"{self.filepath}/ASHST1/final/{self.id}_left_lfseg_heur.nii.gz"
        self.t1ashs_seg_right = f"{self.filepath}/ASHST1/final/{self.id}_right_lfseg_heur.nii.gz"
        self.t1ashs_seg_prefix = f"{self.filepath}/ASHST1/final/{self.id}"
        self.t1ashs_seg_suffix = "lfseg_heur.nii.gz"
        
        self.t1mtthk_left = f"{self.filepath}/ASHST1_MTLCORTEX_MSTTHK/{self.id}_{self.mridate}_left_thickness.csv"
        self.t1mtthk_right = f"{self.filepath}/ASHST1_MTLCORTEX_MSTTHK/{self.id}_{self.mridate}_right_thickness.csv"   
        self.t1mtthk_prefix = f"{self.filepath}/ASHST1_MTLCORTEX_MSTTHK/{self.id}_{self.mridate}"
        self.t1mtthk_suffix = "thickness.csv"   
        
        self.t1icv_seg = f"{self.filepath}/ASHSICV/final/{self.id}_left_lfseg_corr_nogray.nii.gz"
        ##ICV volume txt file name from older ASHS version
        self.icv_volumes_file = f"{self.filepath}/ASHSICV/final/{self.id}_left_corr_nogray_volumes.txt" 
        if not os.path.exists(self.icv_volumes_file):
            ##ICV volume txt file name from newer ASHS versions:
            self.icv_volumes_file = f"{self.filepath}/ASHSICV/final/{self.id}_left_multiatlas_corr_nogray_volumes.txt"

        self.t2nifti = f"{self.filepath}/{self.date_id_prefix}_T2w.nii.gz"
        self.t2ashs_seg_left = f"{self.filepath}/sfsegnibtend/final/{self.id}_left_lfseg_corr_nogray.nii.gz"
        self.t2ashs_seg_right = f"{self.filepath}/sfsegnibtend/final/{self.id}_right_lfseg_corr_nogray.nii.gz"
        self.t2ashs_tse = f"{self.filepath}/sfsegnibtend/tse.nii.gz"

        self.t2ashs_flirt_reg = f"{self.filepath}/sfsegnibtend/flirt_t2_to_t1/flirt_t2_to_t1.mat"
        self.t1_to_t2_transform = f"{self.filepath}/sfsegnibtend/flirt_t2_to_t1/flirt_t2_to_t1_inv.mat"
        self.t2ashs_qc_left = f"{self.filepath}/sfsegnibtend/qa/qa_seg_bootstrap_corr_nogray_left_qa.png"
        self.t2ashs_qc_right = f"{self.filepath}/sfsegnibtend/qa/qa_seg_bootstrap_corr_nogray_right_qa.png"

        self.t2ashs_cleanup_left = f"{cleanup_dir}/{self.id}_{self.mridate}_seg_left.nii.gz"
        self.t2ashs_cleanup_right = f"{cleanup_dir}/{self.id}_{self.mridate}_seg_right.nii.gz"
        self.t2ashs_cleanup_both = f"{cleanup_dir}/{self.id}_{self.mridate}_seg_both.nii.gz"

        self.flair = f"{self.filepath}/{self.date_id_prefix}_flair.nii.gz"
        self.flair_noskull = f"{self.filepath}/{self.date_id_prefix}_flair_skullstrip.nii.gz"
        self.wmh = f"{self.filepath}/{self.date_id_prefix}_flair_wmh.nii.gz"

        self.log_output_dir = f"{self.filepath}/logs"
        if not os.path.exists(self.log_output_dir):
            os.makedirs(self.log_output_dir)

        self.t1ashs_stats_txt = f"{stats_output_dir}/stats_mri_{self.mridate}_{self.id}_ashst1.txt"
        self.t2ashs_stats_txt = f"{stats_output_dir}/stats_mri_{self.mridate}_{self.id}_ashst2.txt"
        self.structure_stats_txt = f"{stats_output_dir}/stats_mri_{self.mridate}_{self.id}_structure.txt"
        self.wmh_stats_txt = f"{stats_output_dir}/stats_mri_{self.mridate}_{self.id}_wmh.txt"


    def neck_trim(self, parent_job_name = [], dry_run = False):
        this_function = MRI.neck_trim.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1nifti], 
                            output_files=[self.t1trim], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)    
            if dry_run:
                print('run neck trim')
            else:      
                os.system(f"bsub {submit_options} ./processing_scripts/trim_neck.sh \
                            {self.t1nifti} {self.t1trim}")
            return this_job_name
        else: 
            return


    ## old version of getting thickness
    def cortical_thick(self, parent_job_name = [], dry_run = False):
        this_function = MRI.cortical_thick.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim], 
                            output_files = [self.thickness], parent_job = parent_job_name):
            submit_options =  set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print(f'run crossthick.sh')
            else:
                os.system(f"bsub {submit_options} -M 8G {thickness_script} {self.id} {self.t1trim} {self.thick_dir}")
            return this_job_name          
        else:
            return


    def brain_ex(self, parent_job_name = [], dry_run = False):
        this_function = MRI.brain_ex.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim], 
                            output_files = [self.brainx], parent_job = parent_job_name):
            submit_options =  set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print(f'run brainx')
            else:
                os.system(f"bsub {submit_options} {brain_ex_script} {self.t1trim} ")
            return this_job_name          
        else:
            return


    ## New version of getting thickness
    def antsct_aging(self, parent_job_name = [], dry_run = False):
        this_function = MRI.ants.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        brainx_job_name = f"{self.date_id_prefix}_copybrainx"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1nifti], output_files=[self.t1trim]):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)    
            if dry_run: 
                print("doing ants")
            else:
                os.system(f"bsub {submit_options} -n 2 {ants_script} {self.t1nifti} {self.filepath}/thickness/{self.id}")
                os.system(f"bsub -o {self.log_output_dir}/{brainx_job_name}.txt -J {brainx_job_name} -w 'done({this_job_name})' cp {self.brainx_thickness_dir} {self.brainx}")
        # T1 trim file created in about 30 seconds, wait for it, 
        # then copy it to main folder so other processing steps can start using it while the rest of ants is still running.
        if dry_run:
            print("would wait for trim file")
            return
        else:
            status = wait_for_file(self.t1trim_thickness_dir)
            if status == "Success":
                os.system(f"cp {self.t1trim_thickness_dir} {self.t1trim}")
                return brainx_job_name
            else:
                return


    def whole_brain_seg(self, parent_job_name = [], dry_run = False):
        this_function = MRI.whole_brain_seg.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.brainx], 
                            output_files = [self.wbseg_nifti], parent_job = parent_job_name):
            submit_options =  set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print(f'run wbseg')
            else:
                os.system(f"bsub {submit_options} -M 12G -q bsc_long \
                        {wbseg_script} {self.filepath} \
                        {self.filepath}/{self.date_id_prefix}_wholebrainseg \
                        {self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain \
                        {wbseg_atlas_dir} 1")
            return this_job_name          
        else:
            return


    def wbsegqc(self, parent_job_name = [], dry_run = False):
        this_function = MRI.wbsegqc.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim,self.wbseg_nifti], 
                            output_files = [self.wbsegqc_image], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)        
            if dry_run:
                print("run WBSEG QC")
            else:
                os.system(f"bsub {submit_options} ./processing_scripts/segmented_image_qc.sh \
                    {self.t1trim} {self.wbseg_nifti} {wblabel_file} {self.wbsegqc_image}")
            return this_job_name          
        else:
            return       


    def wbseg_to_ants(self, parent_job_name = [], dry_run = False):
        this_function = MRI.wbseg_to_ants.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.ants_brainseg,self.wbseg_nifti], 
                            output_files = [self.wbseg_propagated], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)       
            if dry_run:
                print(f"propagate wbseg to ants space")
            else:
                os.system(f"bsub {submit_options} ./processing_scripts/wbseg_to_ants.sh {self.ants_brainseg} {self.wbseg_nifti}")
            return this_job_name          
        else:
            return
    

    def inf_cereb_mask(self, parent_job_name = [], dry_run = False):
        this_function = MRI.inf_cereb_mask.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.wbseg_nifti], 
                            output_files = [self.inferior_cereb_mask], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)       
            if dry_run:
                print(f" ./processing_scripts/make_inferior_cereb_mask.sh")
            else:
                os.system(f"bsub {submit_options} ./processing_scripts/make_inferior_cereb_mask.sh {self.wbseg_nifti} {self.inferior_cereb_mask}")
            return this_job_name
        else:
            return


    def t1icv(self, parent_job_name = [], dry_run = False):
        this_function = MRI.t1icv.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim], \
                            output_files=[self.t1icv_seg], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print("submit T1icv")
            else:
                os.system(f"bsub {submit_options} \
                  ./wrapper_scripts/run_ashs.sh {ashs_root} {icv_atlas} {self.t1trim} {self.t1trim}\
                      {self.filepath}/ASHSICV {self.id} {ashs_mopt_mat_file}")
            return this_job_name          
        else:
            return


    def superres(self, parent_job_name = [], dry_run = False):
        this_function = MRI.superres.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim], \
                            output_files=[self.superres_nifti], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print("run superres")
            else:
                os.system(f"bsub {submit_options} -M 4G -n 1 ./processing_scripts/super_resolution.sh \
                    {self.filepath} {self.t1trim} {self.superres_nifti} {utilities_dir}/build_release")
            return this_job_name
        else:
            return


    def superres_test(self, parent_job_name = [], dry_run = False):
        this_function = MRI.superres.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim], \
                            output_files=[self.superres_nifti], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print("run superres")
            else:
                try:
                    # "bsub", submit_options, "-M 4G -n 1 ./wrapper_scripts/super_resolution.sh", \
                        # self.filepath, self.t1trim, self.superres_nifti
                        #bsub separate
                        # each bsub option must be separate from others
                            ### modify submit_options return
                        # flag and arg go together for bsbu options "-o filepath/log.txt"
                        # script, args as separate strings
                    result=subprocess.run(["bsub","-N", "-o testlog.txt", "./wrapper_scripts/super_resolution.sh", self.filepath, self.t1trim, self.superres_nifti], capture_output=True, text=True, timeout=10,check=True)
                    result_list = result.stdout.split("\n")
                    print(result_list)
                except FileNotFoundError as exc:
                    print(f"Process failed because the executable could not be found.\n{exc}")
                except subprocess.CalledProcessError as exc:
                    print(f"Process failed because did not return a successful return code. "
                        f"Returned {exc.returncode}\n{exc}")
                except subprocess.TimeoutExpired as exc:
                    print(f"Process timed out.\n{exc}")
                # return this_job_name
        else:
            return


    def t1ashs(self, parent_job_name = [], dry_run = False):
        this_function = MRI.t1ashs.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim, self.superres_nifti], 
                            output_files=[self.t1ashs_seg_left, self.t1ashs_seg_right], parent_job = parent_job_name):
           
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run: 
                print("T1 ashs running")
                # print(f"bsub {submit_options} \
                #         ./wrapper_scripts/run_ashs.sh {ashs_root} {ashs_t1_atlas} {self.t1trim} {self.superres_nifti} \
                #         {self.filepath}/ASHST1 {self.id} {ashs_mopt_mat_file}")
            else:
                os.system(f"bsub {submit_options} \
                        ./wrapper_scripts/run_ashs.sh {ashs_root} {ashs_t1_atlas} {self.t1trim} {self.superres_nifti}\
                        {self.filepath}/ASHST1 {self.id} {ashs_mopt_mat_file}")
            return this_job_name
        else:
            return
    

    def t1mtthk(self, parent_job_name = [], dry_run = False):
        this_function = MRI.t1mtthk.__name__
        this_job_name = f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(f"{this_function}", self.id, self.mridate, input_files=[self.t1ashs_seg_left,self.t1ashs_seg_right], output_files=[self.t1mtthk_left,self.t1mtthk_right], 
                                parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run: 
                print(f"do MTTHK")
            else:
                os.system(f"bsub {submit_options} -M 12G -n 1 \
                            ./wrapper_scripts/multitemplate_thickness.sh {self.id} {self.mridate}\
                            {self.t1ashs_seg_left} {self.t1ashs_seg_right} {self.filepath}/ASHST1_MTLCORTEX_MSTTHK")  
            return this_job_name
        else:
            return  


    def t2ashs(self, parent_job_name = [], dry_run = False):
        this_function = MRI.t2ashs.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t2nifti, self.t1trim], \
                            output_files=[self.t2ashs_seg_left, self.t2ashs_seg_right], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print(f"bsub submit t2ashs")
            else:
                os.system(f"bsub {submit_options} ./wrapper_scripts/run_ashs.sh \
                        {ashs_root} {ashs_t2_atlas} {self.t1trim} {self.t2nifti}\
                        {self.filepath}/sfsegnibtend {self.id}")
            return this_job_name
        else: 
            return


    def prc_cleanup(self, parent_job_name = [], dry_run = False):
        this_function = MRI.prc_cleanup.__name__
        this_job_name = f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, \
                            input_files=[self.t2ashs_seg_left, self.t2ashs_seg_right, self.t2ashs_tse], \
                            output_files=[self.t2ashs_cleanup_both], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print(f"running prc_cleanup")
            else:
                os.system(f"bsub {submit_options} ./processing_scripts/cleanup_prc.sh {self.t2ashs_seg_left} \
                    {self.t2ashs_cleanup_left} {self.t2ashs_seg_right} {self.t2ashs_cleanup_right} {self.t2ashs_tse} {self.t2ashs_cleanup_both}")
            return this_job_name          
        else:
            return

    
    def flair_skull_strip(self, parent_job_name = [], dry_run = False):
        this_function = MRI.flair_skull_strip.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.flair], \
                            output_files=[self.flair_noskull], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)        
            if dry_run:
                print('do skull stripping')
            else:
                os.system(f"bsub {submit_options} bash ./wrapper_scripts/flair_skull_strip_hdbet.sh \
                    {self.filepath} {self.date_id_prefix} {wmh_prep_dir}/{current_date}")
            return this_job_name
        else:
            return


    def pmtau(self, parent_job_name = [], dry_run = False):
        this_function = MRI.pmtau.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.thickness, self.t1ashs_seg_left], \
                            output_files=[self.pmtau_output], parent_job=parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print('run pmtau')
            else:
                os.system(f"bsub {submit_options} ./processing_scripts/pmtau.sh {self.id} \
                    {self.filepath}/thickness {self.t1ashs_seg_left}")
            return this_job_name          
        else:
            return


    def ashst1_stats(self, wait_code = "", dry_run = False):
        this_function = MRI.ashst1_stats.__name__
        this_job_name=f"{this_function}_{self.date_id_prefix}"             
        if ready_to_process(this_function, self.id, self.mridate, \
                            input_files=[self.t1ashs_seg_left,self.t1ashs_seg_right,\
                                         self.t1mtthk_left,self.t1mtthk_right,self.icv_volumes_file], \
                            output_files=[self.t1ashs_stats_txt],\
                            parent_job=wait_code):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, wait_code)
            if dry_run:
                print("ASHS T1 stats running")
            else:
                os.system(f"bsub {submit_options} ./wrapper_scripts/ashst1_stats.sh \
                    {self.id} {self.mridate} {stats_output_dir} {self.t1ashs_seg_prefix} \
                    {self.t1ashs_seg_suffix} {self.t1mtthk_prefix} {self.t1mtthk_suffix} \
                    {self.icv_volumes_file}") 
            return this_job_name          
        else:
            return


    def ashst2_stats(self, wait_code = "", dry_run = False):
        this_function = MRI.ashst2_stats.__name__
        this_job_name=f"{this_function}_{self.date_id_prefix}"  
        if ready_to_process(this_function, self.id, self.mridate, \
                            input_files=[self.t2nifti,self.t2ashs_cleanup_left,self.t2ashs_cleanup_right], \
                            output_files=[self.t2ashs_stats_txt],\
                            parent_job=wait_code):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, wait_code)
            if dry_run:
                print("ASHS T2 stats running")
            else:
                os.system(f"bsub {submit_options} ./wrapper_scripts/ashst2_stats.sh \
                        {self.id} {self.mridate} {stats_output_dir} {self.t2nifti} \
                        {self.t2ashs_cleanup_left} {self.t2ashs_cleanup_right}") 
            return this_job_name          
        else:
            return

   
    def structure_stats(self, wait_code = "", dry_run = False):
        this_function = MRI.structure_stats.__name__
        this_job_name=f"{this_function}_{self.date_id_prefix}"
        if ready_to_process(this_function, self.id, self.mridate, \
                            input_files=[self.wbseg_propagated, self.thickness], \
                            output_files=[self.structure_stats_txt], parent_job=wait_code):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, wait_code)
            if dry_run:
                print("Running structure stats")
            else:
                os.system(f"bsub {submit_options} ./wrapper_scripts/structure_stats.sh \
                    {self.wbseg_propagated} {self.thickness} {wblabel_file} {self.structure_stats_txt} \
                    {self.id} {self.mridate} {pmtau_template_dir}")
            return this_job_name          
        else:
            return


    def wmh_stats(self, wait_code = "", dry_run = False):
        this_function = MRI.wmh_stats.__name__
        this_job_name=f"{this_function}_{self.date_id_prefix}"
        if ready_to_process(this_function, self.id, self.mridate, \
                            input_files=[self.flair, self.wmh], \
                            output_files=[self.wmh_stats_txt], parent_job=wait_code):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, wait_code)
            if dry_run:
                print("Running wmh stats")
            else:
                os.system(f"bsub {submit_options} ./wrapper_scripts/wmh_stats.sh \
                  {self.id} {self.mridate} {self.flair} {self.wmh} {self.wmh_stats_txt}")
            return this_job_name          
        else:
            return 

    ## function pet_stats has to be in mri class, since it takes two instances of class MRIPETReg
    def pet_stats(self, wait_code = "", t1tausuvr="null", t1amysuvr="null",\
                        taudate="null", amydate="null", dry_run = False):
        this_function = MRI.pet_stats.__name__
        this_job_name=f"{this_function}_{self.date_id_prefix}"
        pet_stats_txt = f"{stats_output_dir}/stats_tau_{taudate}_amy_{amydate}_mri_{self.mridate}_{self.id}_pet.txt"
        ## too many input files, so pass blank list to get stats related to any existing images & prevent overwriting stats output
        if ready_to_process(this_function, self.id, self.mridate, input_files = [], \
                            output_files = [pet_stats_txt], parent_job = wait_code):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, wait_code)
            if dry_run:
                print(f"running pet stats")
            else:
                os.system(f"bsub {submit_options} ./wrapper_scripts/pet_stats.sh \
                    {self.id} {self.mridate} {taudate} {amydate} \
                    {self.wbseg_nifti} {self.wbseg_propagated} {wblabel_file} \
                    {self.icv_volumes_file} {self.t2ashs_cleanup_left} \
                    {self.t2ashs_cleanup_right} {self.t2ashs_cleanup_both}  \
                    {t1tausuvr} {t1amysuvr} \
                    {pet_stats_txt} {self.t1ashs_seg_prefix} \
                    {self.t1_to_t2_transform} {self.t2nifti} {self.t1trim}")
            return this_job_name          
        else:
            return


class AmyloidPET:
    # strings for Amyloid PET filepaths
    def __init__(self, subject, amydate):
        self.id = subject
        self.scandate = amydate
        self.filepath=f"{adni_data_dir}/{self.id}/{self.scandate}"
        self.date_id_prefix = f"{self.scandate}_{self.id}"
        self.eightmm_amy_nifti = f"{self.filepath}/{self.date_id_prefix}_amypet.nii.gz"        
        self.amy_nifti = f"{self.filepath}/{self.date_id_prefix}_amypet6mm.nii.gz"        

        self.log_output_dir = f"{self.filepath}/logs"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir -p {self.log_output_dir}")

class TauPET:
    # strings for Tau PET filepaths
    def __init__(self, subject, taudate):
        self.id = subject
        self.scandate = taudate
        self.filepath = f"{adni_data_dir}/{self.id}/{self.scandate}"
        self.date_id_prefix = f"{self.scandate}_{self.id}"
        self.eightmm_tau_nifti = f"{self.filepath}/{self.date_id_prefix}_taupet.nii.gz"
        self.tau_nifti = f"{self.filepath}/{self.date_id_prefix}_taupet6mm.nii.gz"

        self.log_output_dir = f"{self.filepath}/logs"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir -p {self.log_output_dir}")

class MRIPetReg:
    #strings for filepaths from MRI and PET class instances and function to do MRI-PET registrations and QC
    def __init__(self, pet_type, MRI, PET):
        self.id = MRI.id
        self.mridate = MRI.mridate
        self.t1trim = MRI.t1trim
        self.mriwbseg = MRI.wbseg_nifti
        self.mri_infcereb = MRI.inferior_cereb_mask
        self.pet_type = pet_type
        self.reg_type = f"{self.pet_type}reg"

        if self.pet_type == "AmyloidPET":
            self.petdate = PET.scandate
            self.pet_nifti = PET.amy_nifti
            self.eightmm_pettype_filename = "amypet"
            self.pettype_filename = "amypet6mm"
        elif self.pet_type == "TauPET":
            self.petdate = PET.scandate
            self.pet_nifti = PET.tau_nifti
            self.eightmm_pettype_filename = "taupet"            
            self.pettype_filename = "taupet6mm"

        self.filepath = f"{adni_data_dir}/{self.id}/{self.petdate}"
        self.reg_prefix = f"{self.petdate}_{self.id}_{self.pettype_filename}_to_{self.mridate}"

        self.t1_reg_RAS = f"{self.filepath}/{self.reg_prefix}_T10GenericAffine_RAS.mat"
        self.t1_reg_nifti = f"{self.filepath}/{self.reg_prefix}_T1.nii.gz"
        self.t1_SUVR = f"{self.filepath}/{self.reg_prefix}_T1_SUVR.nii.gz"
        self.t1_reg_qc = f"{self.filepath}/{self.reg_prefix}_T1_qa.png"

        self.log_output_dir = f"{self.filepath}/logs"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir -p {self.log_output_dir}")


    def t1_pet_reg(self, parent_job_name = [], dry_run = False):
        this_function = f"{self.pet_type}_{MRIPetReg.t1_pet_reg.__name__}"
        this_job_name=f"{self.mridate}_{self.id}_{this_function}"
        if ready_to_process(this_function, self.id, f"{self.mridate}:{self.petdate}", \
                            input_files = [self.t1trim, self.pet_nifti], \
                            output_files = [self.t1_reg_RAS], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print(f"do t1 to pet registration")    
            else:
                os.system(f"bsub {submit_options} ./processing_scripts/coreg_pet.sh \
                    {self.t1trim} {self.pet_nifti} {self.mridate} {self.filepath}")
            return this_job_name
        else:
            return     

 
    def pet_reg_qc(self, parent_job_name = [], dry_run = False):
        this_function = f"{self.pet_type}_{MRIPetReg.pet_reg_qc.__name__}"
        this_job_name=f"{self.mridate}_{self.id}_{this_function}" 
        if ready_to_process(this_function, self.id, f"{self.mridate}:{self.petdate}", 
                            input_files = [self.t1trim, self.t1_reg_nifti], 
                            output_files = [self.t1_reg_qc],
                            parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print(f"qc pet registration")
            else:
                os.system(f"bsub {submit_options} ./processing_scripts/registered_image_qc.sh \
                    {self.t1trim} {self.t1_reg_nifti} {self.t1_reg_qc}")
            return this_job_name          
        else:
            return 


    def t1_pet_suvr(self, parent_job_name = [], dry_run = False):
        this_function = f"{self.pet_type}_{MRIPetReg.t1_pet_suvr.__name__}"
        this_job_name=f"{self.mridate}_{self.id}_{this_function}" 
        if ready_to_process(this_function, self.id, f"{self.mridate}:{self.petdate}", 
                            input_files = [self.t1_reg_nifti, self.mriwbseg], 
                            output_files = [self.t1_SUVR],
                            parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            if dry_run:
                print(f"make t1-pet suvr")
            else:
                os.system(f"bsub {submit_options} ./processing_scripts/suvr.sh {self.mriwbseg} \
                    {self.t1_reg_nifti} {self.t1_SUVR} {self.mri_infcereb}")
            return this_job_name          
        else:
            return 

 

if __name__ == "__main__":
    print("Running processing.py directly.")

    ### Define class instance
    # mri_to_process = MRI("018_S_2155", "2022-11-21")    
    # mri_to_process = MRI("033_S_0734", "2018-10-10")
    mri_to_process = MRI("114_S_6917","2021-04-16") 
    # mri_to_process = MRI("135_S_4722","2017-06-22") 
    # mri_to_process = MRI("033_S_7088", "2022-06-27")
    # mri_to_process = MRI("099_S_6175", "2020-06-03")
    # mri_to_process = MRI('141_S_6779','2020-10-27')
    # mri_to_process = MRI('007_S_2394','2023-10-26')
    # mri_to_process = MRI("022_S_6796","2020-09-09")
    # mri_to_process = MRI("024_S_6846",'2021-05-20')
    # mri_to_process = MRI("135_S_6703",'2021-04-20')

    # amy_to_process = AmyloidPET("033_S_7088", "2022-07-27")
    # amy_to_process = AmyloidPET("114_S_6917","2021-06-02")
    # amy_to_process = AmyloidPET("141_S_6779", "2021-06-02")
    # amy_to_process = AmyloidPET("135_S_4722","2017-06-20")
    # amy_to_process = AmyloidPET("022_S_6796","2021-08-24")
    # amy_to_process = AmyloidPET("135_S_6703","2021-04-20")

    # tau_to_process = TauPET("099_S_6175", "2020-07-09")
    # tau_to_process = TauPET("114_S_6917", "2021-08-11")
    # tau_to_process = TauPET("135_S_4722", "2017-06-22")
    # tau_to_process = TauPET("022_S_6796","2020-09-23")


    # mri_amy_reg_to_process = MRIPetReg(amy_to_process.__class__.__name__, mri_to_process, amy_to_process)
    # mri_tau_reg_to_process = MRIPetReg(tau_to_process.__class__.__name__, mri_to_process, tau_to_process)


    ### MRI processing
    # mri_to_process.neck_trim()
    # mri_to_process.cortical_thick()

    # mri_to_process.t1icv()

    # mri_to_process.superres() 
    # mri_to_process.superres_test()
    # mri_to_process.t1ashs()
    mri_to_process.testmultitemp()

    # mri_to_process.brain_ex(dry_run=True)
    # mri_to_process.whole_brain_seg
    # mri_to_process.wbsegqc()
    # mri_to_process.wbseg_to_ants()
    # mri_to_process.pmtau()

    # mri_to_process.t2ashs()
    # mri_to_process.prc_cleanup()

    # mri_to_process.flair_skull_strip()

    # mri_to_process.structure_stats()
    # mri_to_process.ashst2_stats()
    # mri_to_process.ashst1_stats()
    
    # mri_to_process.pet_stats(t1tausuvr=mri_tau_reg_to_process.t1_SUVR,
    #                             t1amysuvr=mri_amy_reg_to_process.t1_SUVR,
    #                             taudate=mri_tau_reg_to_process.petdate,
    #                             amydate=mri_amy_reg_to_process.petdate)


    ### PET processing
    # mri_tau_reg_to_process.t1_pet_reg()
    # mri_tau_reg_to_process.pet_reg_qc()
    # mri_tau_reg_to_process.t1_pet_suvr()

    # mri_amy_reg_to_process.t1_pet_reg()
    # mri_amy_reg_to_process.pet_reg_qc()
    # mri_amy_reg_to_process.t1_pet_suvr()
