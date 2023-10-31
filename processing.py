#!/usr/bin/env python3

import logging
import os
import time
import pandas as pd
from config import *

##processing class functions only return job name if it's outputs are the inputs for another function

###when doing job submission, use subprocess.run instead of os.system, parse stdout result
    #if message is "no parent job matching wait code", try to run anyway? 
    ##that would work for cleanup_both

#common functions
def ready_to_process(processing_step, id, date, input_files = [], output_files = [], parent_job = ""):
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


def set_submit_options(this_job_name, output_dir, parent_job_name):
    jobname = f"-J {this_job_name}"
    output = f"-o {output_dir}/{this_job_name}_{current_date_time}.txt"
    if parent_job_name:
        if len(parent_job_name) == 2: #for t2 pet reg, needs input from t1petreg and t2ashs
            wait = f'-w "done({parent_job_name[0]}) && done({parent_job_name[1]})"'
        elif "stats" in this_job_name:  ##for stats to run after all image processing 
            wait = f'-w "ended({parent_job_name})"'
        else:
            wait = f'-w "done({parent_job_name})"'
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


#Class definitions
class MRI:
    #strings for MRI filepaths and functions for MRI processing
    def __init__(self, subject, mridate):
        self.id = subject
        self.mridate = mridate
        self.scandate = mridate
        self.filepath=f"{adni_data_dir}/{self.id}/{self.mridate}"
        self.date_id_prefix = f"{self.mridate}_{self.id}"
        
        self.t1nifti = f"{self.filepath}/{self.date_id_prefix}_T1w.nii.gz"
        self.t1trim_thickness_dir = f"{self.filepath}/thickness/{self.id}PreprocessedInput.nii.gz"
        self.t1trim = f"{self.filepath}/{self.date_id_prefix}_T1w_trim.nii.gz"
        ####for testing--trim created from ANTS neckmask
        # self.t1trim = f"{self.filepath}/{self.date_id_prefix}_T1w_trimtestants.nii.gz"

        self.thickness = f"{self.filepath}/thickness/{self.id}CorticalThickness.nii.gz"
        self.pmtau_output = f"{self.filepath}/thickness/ap.nii.gz"

        self.brainx_thickness_dir = f"{self.filepath}/thickness/{self.id}ExtractedBrain0N4.nii.gz"
        self.brainx = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain.nii.gz"
        self.wbseg_nifti = f"{self.filepath}/{self.date_id_prefix}_wholebrainseg/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz"
        self.wbsegqc_image = f"{self.filepath}/{self.date_id_prefix}_wbseg_qa.png"
        
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
        self.t2ashs_qc_left = f"{self.filepath}/sfsegnibtend/qa/qa_seg_bootstrap_corr_nogray_left_qa.png"
        self.t2ashs_qc_right = f"{self.filepath}/sfsegnibtend/qa/qa_seg_bootstrap_corr_nogray_right_qa.png"


        self.t2ashs_tse = f"{self.filepath}/sfsegnibtend/tse.nii.gz"
        self.t2ashs_flirt_reg = f"{self.filepath}/sfsegnibtend/flirt_t2_to_t1/flirt_t2_to_t1.mat"

        self.t2ahs_cleanup_left = f"{cleanup_dir}/{self.id}_{self.mridate}_seg_left.nii.gz"
        self.t2ahs_cleanup_right = f"{cleanup_dir}/{self.id}_{self.mridate}_seg_right.nii.gz"
        self.t2ahs_cleanup_both = f"{cleanup_dir}/{self.id}_{self.mridate}_seg_both.nii.gz"

        self.flair = f"{self.filepath}/{self.date_id_prefix}_flair.nii.gz"
        self.wmh = f"{self.filepath}/{self.date_id_prefix}_wmh.nii.gz"
        self.wmh_mask = f"{self.filepath}/{self.date_id_prefix}_wmh_mask.nii.gz"

        self.log_output_dir = f"{self.filepath}/logs_{current_date}"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir -p {self.log_output_dir}")


    # def neck_trim(self, parent_job_name = ""):
    #     this_job_name=f"{self.date_id_prefix}_necktrim"
    #     if ready_to_process("necktrim", self.id, self.mridate, input_files=[self.t1nifti], 
    #                         output_files=[self.t1trim], parent_job = parent_job_name):
    #         submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)    
    #         os.system(f"bsub {submit_options} /home/lxie/pkg/trim_neck_rf.sh \
    #              {self.t1nifti} {self.t1trim}")
    #     return(this_job_name)
        #  sandy's script: /project/hippogang_1/srdas/homebin/ashsharpicvscripts/trim_neck.sh -w $(mktemp -d)

    def ants(self, parent_job_name = ""):
        this_function = MRI.ants.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        brainx_job_name = f"{self.date_id_prefix}_copybrainx"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1nifti], output_files=[self.t1trim]):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)    
            os.system(f"bsub {submit_options} -n 2 {ants_script} {self.t1nifti} {self.filepath}/thickness/{self.id}")
            os.system(f"bsub -o {self.log_output_dir}/{brainx_job_name}.txt -J {brainx_job_name} -w 'done({this_job_name})' cp {self.brainx_thickness_dir} {self.brainx}")
        # T1 trim file created in about 30 seconds, wait for it, 
        # then copy it to main folder so other processing steps can start using it while the rest of ants is still running.
        status = wait_for_file(self.t1trim_thickness_dir)
        if status == "Success":
            os.system(f"cp {self.t1trim_thickness_dir} {self.t1trim}")
            return brainx_job_name
        else:
            return

    def wbseg(self, parent_job_name = ""):
        this_function = MRI.wbseg.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.brainx], 
                            output_files = [self.wbseg_nifti], parent_job = parent_job_name):
            submit_options =  set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            os.system(f"bsub {submit_options} -M 12G -q bsc_long \
                    {wbseg_script} \
                    {self.filepath} \
                    {self.filepath}/{self.date_id_prefix}_wholebrainseg \
                    {self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain \
                    {wbseg_atlas_dir} 1")
            return this_job_name          
        else:
            return

    def wbsegqc(self, parent_job_name = ""):
        this_function = MRI.wbsegqc.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim,self.wbseg_nifti], 
                            output_files = [self.wbsegqc_image], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)        
            os.system(f"bsub {submit_options} ./wrapper_scripts/segmented_image_qc.sh \
                {self.t1trim} {self.wbseg_nifti} {wblabel_file} {self.wbsegqc_image}")
        return         

    def wbseg_to_ants(self, parent_job_name = ""):
        print(f"bsub ./wrapper_scripts/wbseg_to_ants.sh")
        return


    def t1icv(self, parent_job_name = ""):
        this_function = MRI.t1icv.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim], \
                            output_files=[self.t1icv_seg]):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            # print("submit T1icv")
            # print(f"bsub {submit_options} \
            #     ./wrapper_scripts/run_ashs_testcopy.sh run_ashs {ashs_root} {icv_atlas} {self.t1trim} {self.t1trim}\
            #         {self.filepath}/ASHSICV {self.id} {ashs_mopt_mat_file}")
            os.system(f"mkdir {self.filepath}/ASHSICV")
            os.system(f"bsub {submit_options} \
                  ./wrapper_scripts/run_ashs.sh {ashs_root} {icv_atlas} {self.t1trim} {self.t1trim}\
                      {self.filepath}/ASHSICV {self.id} {ashs_mopt_mat_file}")
           
            # os.system(f"bsub {submit_options} \
            #       ./wrapper_scripts/run_ashs_testcopy.sh run_ashs {ashs_root} {icv_atlas} {self.t1trim} {self.t1trim}\
            #           {self.filepath}/ASHSICV {self.id} {ashs_mopt_mat_file}")
            # return 


    def superres(self, parent_job_name = ""):
        this_function = MRI.superres.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim], output_files=[self.superres_nifti]):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            os.system(f"bsub {submit_options} -M 4G -n 1 ./wrapper_scripts/super_resolution.sh \
                    {self.filepath} {self.t1trim} {self.superres_nifti}")
            return this_job_name
        else:
            return

    def t1ashs(self, parent_job_name = ""):
        this_function = MRI.t1ashs.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t1trim, self.superres_nifti], 
                            output_files=[self.t1ashs_seg_left, self.t1ashs_seg_right], parent_job = parent_job_name):
            # print("T1 ashs running")
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            os.system(f"mkdir {self.filepath}/ASHST1")
            os.system(f"bsub {submit_options} \
                      ./wrapper_scripts/run_ashs_testcopy.sh run_ashs {ashs_root} {ashs_t1_atlas} {self.t1trim} {self.superres_nifti}\
                      {self.filepath}/ASHST1 {self.id} {ashs_mopt_mat_file}")
            return this_job_name
        else:
            return
    
    def t1mtthk(self, parent_job_name = ""):
        this_function = MRI.t1mtthk.__name__
        for side in sides:
            if side == "left":
                ashs_thick = self.t1mtthk_left
                ashs_seg = self.t1ashs_seg_left
                this_job_name=f"{self.date_id_prefix}_{this_function}_left"
            elif side == "right":
                ashs_thick = self.t1mtthk_right
                ashs_seg = self.t1ashs_seg_right
                this_job_name=f"{self.date_id_prefix}_{this_function}_right"
            if ready_to_process(f"{this_function}_{side}", self.id, self.mridate, input_files=[ashs_seg], output_files=[ashs_thick], 
                                parent_job = parent_job_name):
                # print(f"t1mtthk for {side} running")
                submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
                os.system(f"bsub {submit_options} -M 12G -n 1 \
                            ./wrapper_scripts/multitemplate_thickness.sh {self.id} {self.mridate}\
                            {side} {ashs_seg} {self.filepath}/ASHST1_MTLCORTEX_MSTTHK")  
        
        return 
              

    def t2ashs(self, parent_job_name = ""):
        this_function = MRI.t2ashs.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t2nifti, self.t1trim], \
                            output_files=[self.t2ashs_seg_left, self.t2ashs_seg_right]):
            # print(f"bsub submit t2ashs")
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            os.system(f"mkdir {self.filepath}/sfsegnibtend")
            os.system(f"bsub {submit_options} ./wrapper_scripts/run_ashs_testcopy.sh run_ashs \
                      {ashs_root} {ashs_t2_atlas} {self.t1trim} {self.t2nifti}\
                      {self.filepath}/sfsegnibtend {self.id}")
            return this_job_name
        else: 
            return

    def t2ashs_qconly(self,parent_job_name = ""):
        this_function = MRI.t2ashs_qconly.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.t2nifti, self.t1trim], \
                            output_files=[self.t2ashs_qc_left, self.t2ashs_qc_right]):
            # print(f"bsub submit t2ashs")
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            os.system(f"bsub {submit_options} ./wrapper_scripts/temp_run_ashs_t2_qconly.sh run_ashs \
                      {ashs_root} {ashs_t2_atlas} {self.t1trim} {self.t2nifti}\
                      {self.filepath}/sfsegnibtend {self.id}")
            return this_job_name
        else:
            return


    def prc_cleanup(self, parent_job_name = ""):
        this_function = MRI.prc_cleanup.__name__
        for side in sides:
            this_job_name = f"{self.date_id_prefix}_{this_function}_{side}"

            if side == "left":
                seg=self.t2ashs_seg_left
                output=self.t2ahs_cleanup_left
            elif side == "right":
                seg=self.t2ashs_seg_right
                output=self.t2ahs_cleanup_right
            
            if ready_to_process(f"{this_function}_{side}", self.id, self.mridate, input_files=[seg], \
                                output_files=[output], parent_job = parent_job_name):
                submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
                os.system(f"bsub {submit_options} ./wrapper_scripts/cleanup_prc.sh {seg} {output}")

        this_job_name = f"{self.date_id_prefix}{this_function}_both"
        parent_job_name = f"{self.date_id_prefix}_{this_function}_right"
        if ready_to_process(f"{this_function}_both", self.id, self.mridate, \
                            input_files=[self.t2ahs_cleanup_left, self.t2ahs_cleanup_right], \
                            output_files=[self.t2ahs_cleanup_both], parent_job = parent_job_name):
                submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
                os.system(f"bsub {submit_options} c3d {self.t2ashs_tse} -as A {self.t2ahs_cleanup_left} \
                          -interp NN -reslice-identity -push A {self.t2ahs_cleanup_right} \
                          -interp NN -reslice-identity -add -o {self.t2ahs_cleanup_both}")
                return


    def wmh_prep(self, parent_job_name = ""):
        this_function = MRI.wmh_prep.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.flair], output_files=[self.wmh]):
            if not os.path.exists(f"{analysis_input_dir}/{current_date}"):
                logging.info(f"making directory {current_date} in analysis_input for WMH analysis.")               
                os.system(f"mkdir {analysis_input_dir}/{current_date}")
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)        
            os.system(f"bsub {submit_options} cp {self.flair} {analysis_input_dir}/{current_date}/{self.mridate}_{self.id}_flair_0000.nii.gz")
            return

    def pmtau(self, parent_job_name = ""):
        this_function = MRI.pmtau.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"
        if ready_to_process(this_function, self.id, self.mridate, input_files=[self.thickness], \
                            output_files=[self.pmtau_output], parent_job=parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            os.system(f"bsub {submit_options} ./wrapper_scripts/pmtau.sh {self.id} {self.mridate} {self.filepath}/thickness")
            return

    def ashst1_stats(self, wait_code = ""):
        this_function = MRI.ashst1_stats.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"             
        if ready_to_process(this_function, self.id, self.mridate, \
                            input_files=[self.t1ashs_seg_left,self.t1ashs_seg_right,\
                                         self.t1mtthk_left,self.t1mtthk_right,self.icv_volumes_file], \
                            output_files=[f"{stats_output_dir}/stats_mri_{self.mridate}_{self.id}_mrionly.txt"],\
                            parent_job=wait_code):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, wait_code)
            os.system(f"bsub {submit_options} ./wrapper_scripts/mri_ashs_stats.sh \
                    {self.id} {self.mridate} {stats_output_dir} {self.t1ashs_seg_prefix} \
                    {self.t1ashs_seg_suffix} {self.t1mtthk_prefix} {self.t1mtthk_suffix} {self.icv_volumes_file}") 
            # print("ASHS T1 stats running")
            return

    def ashst2_stats(self, wait_code = ""):
        this_function = MRI.ashst2_stats.__name__
        this_job_name=f"{self.date_id_prefix}_{this_function}"  
        if ready_to_process(this_function, self.id, self.mridate, \
                            input_files=[self.t2nifti,self.t2ahs_cleanup_left,self.t2ahs_cleanup_right], \
                            output_files=[f"{stats_output_dir}/stats_mri_{self.mridate}_{self.id}_ashst2.txt"],\
                            parent_job=wait_code):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, wait_code)
            os.system(f"bsub {submit_options} ./testing/t2statsonly.sh \
                    {self.id} {self.mridate} {stats_output_dir} {self.t2nifti} \
                    {self.t2ahs_cleanup_left} {self.t2ahs_cleanup_right}") 
            # print("ASHS T2 stats running")
            return


    def structpetstats(self, wait_code="",t1tau="null",t2tau="null",t1amy="null",t2amy="null",taudate="null",amydate="null"):
        this_function = MRI.structpetstats.__name__
        ##if t1t1/pets are null, set mode to mri, else mode pet
        if t1tau == "null":
            mode = "mri"
        else:
            mode="pet"
        
        this_job_name=f"{this_function}_{mode}_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.log_output_dir, wait_code)
        logging.info(f"{self.id}:{self.mridate}: Submitting structpetstats to queue with mode {mode},\
                     will run when parent jobs matching wait code {wait_code} are complete.")
        os.system(f"bsub {submit_options } ./stats.sh {self.id} {self.wbseg_nifti} {self.thickness} \
                {t1tau} {t2tau} {t1amy} {t2amy} \
                {self.t2ahs_cleanup_left} {self.t2ahs_cleanup_right} \
                {self.t2ahs_cleanup_both} {self.t1trim} {self.icv_volumes_file} \
                {mode} {wblabel_file} {pmtau_template_dir} {stats_output_dir} \
                {self.mridate} {taudate} {amydate} {self.flair} {self.wmh_mask}")
        # print(f"pet_stats {mode}")
        # print(f"bsub {submit_options } ./stats.sh {self.id} {self.wbseg_nifti} {self.thickness} \
        #         {t1tau} {t2tau} {t1amy} {t2amy} \
        #         {self.t2ahs_cleanup_left} {self.t2ahs_cleanup_right} \
        #         {self.t2ahs_cleanup_both} {self.t1trim} {self.icv_volumes_file} \
        #         {mode} {wblabel_file} {pmtau_template_dir} {stats_output_dir} \
        #         {self.mridate} {taudate} {amydate} {self.flair} {self.wmh_mask}")
        return


class AmyloidPET:
    # strings for Amyloid PET filepaths
    def __init__(self, subject, amydate):
        self.id = subject
        self.scandate = amydate
        self.filepath=f"{adni_data_dir}/{self.id}/{self.scandate}"
        self.date_id_prefix = f"{self.scandate}_{self.id}"
        self.amy_nifti = f"{self.filepath}/{self.date_id_prefix}_amypet.nii.gz"        

        self.log_output_dir = f"{self.filepath}/logs_{current_date}"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir -p {self.log_output_dir}")

class TauPET:
    # strings for Tau PET filepaths
    def __init__(self, subject, taudate):
        self.id = subject
        self.scandate = taudate
        self.filepath = f"{adni_data_dir}/{self.id}/{self.scandate}"
        self.date_id_prefix = f"{self.scandate}_{self.id}"
        self.tau_nifti = f"{self.filepath}/{self.date_id_prefix}_taupet.nii.gz"
        
        self.log_output_dir = f"{self.filepath}/logs_{current_date}"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir -p {self.log_output_dir}")

class MRIPetReg:
    #strings for filepaths from MRI and PET class instances and function to do MRI-PET registrations and QC
    def __init__(self, pet_type, MRI, PET):
        self.id = MRI.id
        self.mridate = MRI.mridate
        self.t1trim = MRI.t1trim
        self.t2nifti = MRI.t2nifti
        self.t2ashs_flirt_reg = MRI.t2ashs_flirt_reg
        self.pet_type = pet_type
        self.reg_type = f"{self.pet_type}reg"

        if self.pet_type == "AmyloidPET":
            self.petdate = PET.scandate
            self.pet_nifti = PET.amy_nifti
            self.pettype_filename = "amypet"
        elif self.pet_type == "TauPET":
            self.petdate = PET.scandate
            self.pet_nifti = PET.tau_nifti            
            self.pettype_filename = "taupet"

        self.filepath = f"{adni_data_dir}/{self.id}/{self.petdate}"
        self.reg_prefix = f"{self.petdate}_{self.id}_{self.pettype_filename}_to_{self.mridate}"

        self.t1_reg_RAS = f"{self.filepath}/{self.reg_prefix}_T10GenericAffine_RAS.mat"
        self.t1_reg_nifti = f"{self.filepath}/{self.reg_prefix}_T1.nii.gz"
        self.t1_reg_qc = f"{self.filepath}/{self.reg_prefix}_T1_qa.png"

        self.t2_reg_nifti = f"{self.filepath}/{self.reg_prefix}_T2.nii.gz"

        self.log_output_dir = f"{self.filepath}/logs_{current_date}"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir -p {self.log_output_dir}")


    def t1_pet_reg(self, parent_job_name = ""):
        this_function = f"{self.pet_type}_{MRIPetReg.t1_pet_reg.__name__}"
        this_job_name=f"{self.mridate}_{self.id}_{this_function}"
        if ready_to_process(this_function, self.id, f"{self.mridate}:{self.petdate}", \
                            input_files = [self.t1trim, self.pet_nifti], \
                            output_files = [self.t1_reg_RAS]):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            os.system(f"bsub {submit_options} \
                       {t1petreg_script} \
                       {self.id} {self.t1trim} {self.pet_nifti} {self.mridate} {self.filepath}")
            # print(f"bsub {submit_options} \
            #            {t1petreg_script} \
            #            {self.id} {self.t1trim} {self.pet_nifti} {self.mridate} {self.filepath}")
            # print(this_job_name)
            return (this_job_name)    
        else:
            return     
        

    def t2_pet_reg(self, parent_job_name = ""):
        this_function = f"{self.pet_type}_{MRIPetReg.t2_pet_reg.__name__}"
        this_job_name=f"{self.mridate}_{self.id}_{this_function}"
        if ready_to_process(this_function, self.id, f"{self.mridate}:{self.petdate}", \
                            input_files = [self.t2nifti, self.pet_nifti, self.t2ashs_flirt_reg, self.t1_reg_RAS], \
                            output_files = [self.t2_reg_nifti], parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)        
            os.system(f"bsub {submit_options} ./wrapper_scripts/t2_pet_registration.sh {self.t2nifti} \
                  {self.pet_nifti} {self.t2_reg_nifti} {self.t2ashs_flirt_reg} {self.t1_reg_RAS}")
            # print(f"bsub {submit_options} ./wrapper_scripts/t2_pet_registration.sh {self.t2nifti} \
            #       {self.pet_nifti} {self.t2_reg_nifti} {self.t2ashs_flirt_reg} {self.t1_reg_RAS}")
            # print(this_job_name)
            return

 
    def pet_reg_qc(self, parent_job_name = ""):
        this_function = f"{self.pet_type}_{MRIPetReg.pet_reg_qc.__name__}"
        this_job_name=f"{self.mridate}_{self.id}_{this_function}" 
        if ready_to_process(this_function, self.id, f"{self.mridate}:{self.petdate}", 
                            input_files = [self.t1trim, self.t1_reg_nifti], 
                            output_files = [self.t1_reg_qc],
                            parent_job = parent_job_name):
            submit_options = set_submit_options(this_job_name, self.log_output_dir, parent_job_name)
            os.system(f"bsub {submit_options} ./wrapper_scripts/registered_image_qc.sh \
                  {self.t1trim} {self.t1_reg_nifti} {self.t1_reg_qc}")
            # print(f"bsub {submit_options} \
            #       {t1petregqc_script} \
            #       {self.t1trim} {self.t1_reg_nifti} {self.t1_reg_qc}")
            # print(this_job_name)
            return

 

if __name__ == "__main__":
    print("Running processing.py directly.")

    # mri_to_process = MRI("033_S_1016","2017-12-06") 
    # mri_to_process = MRI('141_S_6779','2020-10-27')
    # mri_to_process = MRI("033_S_7088", "2022-06-27")
    # mri_to_process = MRI("137_S_6826", "2019-10-17")
    # mri_to_process = MRI("099_S_6175", "2020-06-03")
    # mri_to_process = MRI("033_S_0734", "2018-10-10")
    mri_to_process = MRI("018_S_2133", "2019-02-11")
    mri_to_process.t2ashs_qconly()

    # amy_to_process = AmyloidPET("114_S_6917","2021-06-02")
    # amy_to_process = AmyloidPET("141_S_6779", "2021-06-02")
    # amy_to_process = AmyloidPET("033_S_7088", "2022-07-27")

    # tau_to_process = TauPET("114_S_6917", "2021-08-11")
    # tau_to_process = TauPET("099_S_6175", "2020-07-09")

    # mri_amy_reg_to_process = MRIPetReg('amypet', mri_to_process, amy_to_process)
    # mri_tau_reg_to_process = MRIPetReg('taupet', mri_to_process, tau_to_process)


    # ##MRI processing
    # mri_to_process.t2ashs_qconly()
    # mri_to_process.superres() 
    # mri_to_process.structpetstats(t1tau = mri_tau_reg_to_process.t1_reg_nifti, t2tau = mri_tau_reg_to_process.t2_reg_nifti,
    #                 t1amy = mri_amy_reg_to_process.t1_reg_nifti, t2amy = mri_amy_reg_to_process.t2_reg_nifti)

    # mri_to_process.wbsegqc()


    # mri_to_process.structpetstats(wait_code = f"{mri_to_process.mridate}_{mri_to_process.id}*",
    #                 t1tau = mri_tau_reg_to_process.t1_reg_nifti, t2tau = mri_tau_reg_to_process.t2_reg_nifti,
    #                 t1amy = mri_amy_reg_to_process.t1_reg_nifti, t2amy = mri_amy_reg_to_process.t2_reg_nifti)

    # mri_to_process.t1icv()
    # t1ashs_job_name = mri_to_process.do_t1ashs()
    # mri_to_process.do_ashs_stats(t1ashs_job_name)
    # mri_to_process.do_t1mtthk()
    # mri_to_process.do_t1mtthk(t1ashs_job_name) 
    # mri_to_process.do_ashs_stats(f"*{mri_to_process.id}")

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
    # mri_to_process.do_pmtau()


    ##PET processing
    # mri_tau_reg_to_process.pet_reg_qc()

    # t1_pet_reg_job = mri_tau_reg_to_process.do_t1_pet_reg()
    # mri_tau_reg_to_process.do_pet_reg_qc(t1_pet_reg_job)
    # mri_tau_reg_to_process.do_t2_pet_reg(t1_pet_reg_job)
    # mri_tau_reg_to_process.do_t2_pet_reg()
    # mri_tau_reg_to_process.do_t2_pet_reg(f"{mri_to_process.mridate}_{mri_to_process.id}_t1taupetreg")
    # mri_tau_reg_to_process.do_t2_pet_reg([f"{mri_to_process.mridate}_{mri_to_process.id}_t1taupetreg",f"{mri_to_process.mridate}_{mri_to_process.id}_t2ashs"])