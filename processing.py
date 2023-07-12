#!/usr/bin/env python3

import datetime
import logging
import os
import time
import pandas as pd
import subprocess

#Cluster filepaths called in processing functions
ants_script = "/project/ftdc_pipeline/ftdc-picsl/antsct-aging-0.3.3-p01/antsct-aging.sh"
wbseg_script = "/home/sudas/bin/ahead_joint/turnkey/bin/hippo_seg_WholeBrain_itkv4_v3.sh"
wbseg_atlas_dir = "/home/sudas/bin/ahead_joint/turnkey/data/WholeBrain_brainonly"
segqc_script = "/project/hippogang_1/srdas/wd/TAUPET/longnew/simplesegqa.sh"
wblabel_file = "/project/wolk/Prisma3T/relong/wholebrainlabels_itksnaplabelfile.txt"
ashs_root = "/project/hippogang_2/longxie/pkg/ashs/ashs-fast"
ashs_t1_atlas = "/home/lxie/ASHS_atlases/PMC_3TT1_atlas_noSR"
long_scripts = "/home/lxie/ADNI2018/scripts"
icv_atlas = "/home/lxie/ASHS_atlases/ICVatlas_3TT1"
ashs_t2_atlas = "/project/hippogang_2/pauly/wolk/atlases/ashs_atlas_upennpmc_20170810"
t1petreg_script = "/project/hippogang_1/srdas/wd/TAUPET/longnew/coreg_pet.sh"
t1petregqc_script = "/project/hippogang_1/srdas/wd/TAUPET/longnew/simpleregqa.sh"
pmtau_template_dir = "/project/wolk/Prisma3T/t1template"


#main file directories in cluster
analysis_input_dir = "/project/wolk/ADNI2018/analysis_input"
analysis_output_dir = "/project/wolk/ADNI2018/analysis_output"
cleanup_dir = f"{analysis_input_dir}/cleanup"
csvs_dir = f"{analysis_input_dir}/adni_data_setup_csvs"
csvs_dirs_dict = {"ida_study_datasheets" : "", "merged_data_uids":"", "uids_process_status":"", "filelocs":""}

# adni_data_dir = "/project/wolk/ADNI2018/dataset" #real location
adni_data_dir = "/project/wolk/ADNI2018/scripts/pipeline_test_data"  # for testing


#other variables
sides = ["left", "right"]
current_date = datetime.datetime.now().strftime("%Y_%m_%d")


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
            logging.info(f"{id}:{date}: One or more input files missing, cannot run {processing_step}")
            return False


def set_submit_options(this_job_name, output_dir, parent_job_name):
    jobname = f"-J {this_job_name}"
    output = output_dir
    if parent_job_name:
        wait = f'-w "done({parent_job_name})"'
    else:
        wait = ""
    return f"{jobname} {output} {wait}"


def wait_for_file(file):
    print(f"waiting for file {file} to be created.")
    while not os.path.exists(file):
        time.sleep(5)
    if os.path.exists(file):
        while os.stat(file).st_size <= 10000:
            time.sleep(1)
        return
    else:
        return 


def convert_to_nifti(scanclass,uids):
    # uid_df = pd.read_csv(uid_csv)
    # print(uid_df.head())
    # for index,row in uid_df.iterrows():
        # id = str(row['ID'])
        # scandate = str(row['SMARTDATE'])
        # nifti_file_loc_dataset_prefix = f"{adni_data_dir}/{id}/{scandate}/{scandate}_{id}"
        # uids={"t1_uid": str(row['IMAGUID_T1']),"t2_uid": str(row['IMAGUID_T2']).split('.')[0]}
        print("In convert_to_nifti function")
        id = scanclass.id
        scandate = scanclass.mridate
        # print(id)
        # print(scandate)
        for key in uids:
            # print(uids[key])
            result = subprocess.run(
                ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/nifti_file.sh",id,scandate,uids[key]],  
                capture_output=True, text=True)
            ##handle any errors 
            result_list = result.stdout.split("\n")
            status = result_list[0]
            logging.info(f"{id}:{scandate}:Nifti conversion status is:{status}")

            if status == "conversion to nifti sucessful":
                nifti_file_loc_public = result_list[1]
                # print(f"Nifti filepath: {nifti_file_loc_public}")
                # if key == "t1_uid":
                    # uid_df.at[index,'FINALT1NIFTI'] = nifti_file_loc_public
                    # uid_df.at[index,'T1_PROCESS_STATUS'] = 1
                    # nifti_file_loc_dataset = f"{nifti_file_loc_dataset_prefix}_T1w.nii.gz"
                # elif key == "t2_uid":
                    # uid_df.at[index,'FINALT2NIFTI'] = nifti_file_loc_public
                    # uid_df.at[index,'T2_PROCESS_STATUS'] = 1
                    # nifti_file_loc_dataset = f"{nifti_file_loc_dataset_prefix}_T2w.nii.gz"
                
                # make sym link between /PUBLIC and /dataset
                print(f"ln -sf {nifti_file_loc_public} {scanclass.t1nifti}") 
                # os.system(f"ln -sf {nifti_file_loc_public} {nifti_file_loc_dataset}")




    #     #fill in site vendor & model info
    #     site = id.split("_")[0]
    #     siteinfo_result = subprocess.run(
    #         ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/get_site_scanner_info.sh",site],
    #          capture_output=True, text=True)
    #     siteinfo_result_list = siteinfo_result.stdout.split("\n")[:-1] # remove extra newline at end
    #     siteinfo_headers = ["Model2","Model3","Vendor2","Vendor3"]
    #     for i in range(0,len(siteinfo_result_list)):
    #         uid_df.at[index,siteinfo_headers[i]] = siteinfo_result_list[i]

    #     #baseline scan date
    #     alldates = uid_df.loc[uid_df['ID'] == id]['SMARTDATE'].values.tolist()
    #     alldates.sort()
    #     uid_df.at[index,"BLSCANDATE"] = alldates[0]

    # print(uid_df.head())
    # uid_df.to_csv(os.path.join(adni_data_dir,mri_uids_filelocs),index=False,header=True)




#Class definitions
class MRI:
    #strings for MRI filepaths and functions for MRI processing
    def __init__(self, subject, mridate):
        self.id = subject
        self.mridate = mridate
        self.T1_dicom_filepath = f"/project/wolk/PUBLIC/Dicoms/{self.id}/MRI3T/{self.mridate}/"
        self.filepath=f"{adni_data_dir}/{self.id}/{self.mridate}"
        self.date_id_prefix = f"{self.mridate}_{self.id}"
        
        self.t1nifti = f"{self.filepath}/{self.date_id_prefix}_T1w.nii.gz"
        self.t1trim_thickness_dir = f"{self.filepath}/thickness/{self.id}PreprocessedInput.nii.gz"
        self.t1trim = f"{self.filepath}/{self.date_id_prefix}_T1w_trim.nii.gz"
        
        self.thickness = f"{self.filepath}/thickness/{self.id}CorticalThickness.nii.gz"
        self.pmtau_output = f"{self.filepath}/thickness/ap.nii.gz"

        self.brainx_thickness_dir = f"{self.filepath}/thickness/{self.id}ExtractedBrain0N4.nii.gz"
        self.brainx = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain.nii.gz"
        self.wbseg= f"{self.filepath}/{self.date_id_prefix}_wholebrainseg/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz"
        self.wbsegqc = f"{self.filepath}/{self.date_id_prefix}_wbseg_qa.png"
        
        self.superres = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_denoised_SR.nii.gz"
        
        self.t1ashs_seg_left = f"{self.filepath}/ASHST1/final/{self.id}_left_lfseg_heur.nii.gz"
        self.t1ashs_seg_right = f"{self.filepath}/ASHST1/final/{self.id}_right_lfseg_heur.nii.gz"
        
        self.t1mtthk_left = f"{self.filepath}/ASHST1_MTLCORTEX_MSTTHK/{self.id}_{self.mridate}_left_thickness.csv"
        self.t1mtthk_right = f"{self.filepath}/ASHST1_MTLCORTEX_MSTTHK/{self.id}_{self.mridate}_right_thickness.csv"   
        
        self.t1icv_seg = f"{self.filepath}/ASHSICV/final/{self.id}_left_lfseg_corr_nogray.nii.gz"

        self.t2nifti = f"{self.filepath}/{self.date_id_prefix}_T2w.nii.gz"
        self.t2ashs_seg_left = f"{self.filepath}/sfsegnibtend/final/{self.id}_left_lfseg_corr_nogray.nii.gz"
        self.t2ashs_seg_right = f"{self.filepath}/sfsegnibtend/final/{self.id}_right_lfseg_corr_nogray.nii.gz"
        self.t2ashs_tse = f"{self.filepath}/sfsegnibtend/tse.nii.gz"
        self.t2ashs_flirt_reg = f"{self.filepath}/sfsegnibtend/flirt_t2_to_t1/flirt_t2_to_t1.mat"
        self.icv_file = f"{self.filepath}/sfsegnibtend/final/{self.id}_icv.txt"

        self.t2ahs_cleanup_left=f"{cleanup_dir}/{self.id}_{self.mridate}_seg_left.nii.gz"
        self.t2ahs_cleanup_right=f"{cleanup_dir}/{self.id}_{self.mridate}_seg_right.nii.gz"
        self.t2ahs_cleanup_both=f"{cleanup_dir}/{self.id}_{self.mridate}_seg_both.nii.gz"

        self.flair = f"{self.filepath}/{self.date_id_prefix}_flair.nii.gz"
        self.wmh = f"{self.filepath}/{self.date_id_prefix}_wmh.nii.gz"
        self.t1flair = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_to_flair.mat"


        self.log_output_dir = f"{self.filepath}/logs_{current_date}"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir {self.log_output_dir}")
        self.bsub_output = f"-o {self.log_output_dir}"


    def neck_trim(self, parent_job_name = ""):
        this_job_name=f"necktrim_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process("necktrim", self.id, self.mridate, input_files=[self.t1nifti], 
                            output_files=[self.t1trim], parent_job = parent_job_name):
            os.system(f"bsub {submit_options} /home/lxie/pkg/trim_neck_rf.sh \
                 {self.t1nifti} {self.t1trim}")
        return(this_job_name)
                    #  sandy's script: /project/hippogang_1/srdas/homebin/ashsharpicvscripts/trim_neck.sh -w $(mktemp -d)

    def do_ants(self, parent_job_name = ""):
        this_job_name=f"ants_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process('ants', self.id, self.mridate, input_files=[self.t1nifti], output_files=[self.t1trim]):
            os.system(f"bsub {submit_options} -n 2 {ants_script} {self.t1nifti} {self.filepath}/thickness/{self.id}")
            os.system(f"bsub {self.bsub_output} -w 'done({this_job_name})' cp {self.brainx_thickness_dir} {self.brainx}")
        # T1 trim file created in about 30 seconds, wait for it, 
        # then copy it to main folder so other processing steps can start using it while the rest of ants is still running.
        wait_for_file(self.t1trim_thickness_dir)
        os.system(f"cp {self.t1trim_thickness_dir} {self.t1trim}")
        return this_job_name

    def do_wbseg(self, parent_job_name = ""):
        this_job_name=f"wbseg_{self.date_id_prefix}"
        submit_options =  set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process('wbseg', self.id, self.mridate, input_files=[self.brainx], 
                            output_files = [self.wbseg], parent_job = parent_job_name):
            os.system(f"bsub {submit_options} -M 12G -q bsc_long \
                    {wbseg_script} \
                    {self.filepath} \
                    {self.filepath}/{self.date_id_prefix}_wholebrainseg \
                    {self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain \
                    {wbseg_atlas_dir} 1")
        return this_job_name          
     
    def do_wbsegqc(self, parent_job_name = ""):
        this_job_name=f"wbsegqc_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process('wbsegqc', self.id, self.mridate, input_files=[self.t1trim,self.wbseg], 
                            output_files = [self.wbsegqc], parent_job = parent_job_name):
            os.system(f"bsub {submit_options} {segqc_script} \
                {self.t1trim} {self.wbseg} {wblabel_file} {self.wbsegqc}")
        return         

    def do_superres(self, parent_job_name = ""):
        this_job_name=f"superres_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process('superres', self.id, self.mridate, input_files=[self.t1trim], output_files=[self.superres]):
            os.system(f"bsub {submit_options} -M 4G -n 1 ./wrapper_scripts/super_resolution.sh \
                    {self.filepath} {self.t1trim} {self.superres}")
        return this_job_name

    def do_t1ashs(self, parent_job_name = ""):
        this_job_name=f"t1ashs_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process("t1ashs", self.id, self.mridate, input_files=[self.t1trim, self.superres], 
                            output_files=[self.t1ashs_seg_left, self.t1ashs_seg_right], parent_job = parent_job_name):
            os.system(f"mkdir {self.filepath}/ASHST1")
            os.system(f"bsub {submit_options} \
                      ./wrapper_scripts/run_ashs.sh {ashs_root} {ashs_t1_atlas} {self.t1trim} {self.superres}\
                      {self.filepath}/ASHST1 {self.id} {long_scripts}/ashs-fast-z.sh {long_scripts}/identity.mat")
        return(this_job_name)
    
    def do_t1mtthk(self, parent_job_name = ""):
        for side in sides:
            if side == "left":
                ashs_thick = self.t1mtthk_left
                ashs_seg = self.t1ashs_seg_left
                this_job_name=f"t1mtthk_left_{self.date_id_prefix}"
            elif side == "right":
                ashs_thick = self.t1mtthk_right
                ashs_seg = self.t1ashs_seg_right
                this_job_name=f"t1mtthk_right_{self.date_id_prefix}"
            
            submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
            if ready_to_process(f"t1mtthk_{side}", self.id, self.mridate, input_files=[ashs_seg], output_files=[ashs_thick], 
                                parent_job = parent_job_name):
                os.system(f"bsub {submit_options} -M 12G -n 1 \
                            ./wrapper_scripts/multitemplate_thickness.sh {self.id} {self.mridate}\
                            {side} {ashs_seg} {self.filepath}/ASHST1_MTLCORTEX_MSTTHK")  
        return
            
    def do_t1icv(self, parent_job_name = ""):
        this_job_name=f"t1icv_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process("t1icv", self.id, self.mridate, input_files=[self.t1trim], \
                            output_files=[self.t1icv_seg]):
            os.system(f"mkdir {self.filepath}/ASHSICV")
            os.system(f"bsub {submit_options} \
                  ./wrapper_scripts/run_ashs.sh {ashs_root} {icv_atlas} {self.t1trim} {self.t1trim}\
                      {self.filepath}/ASHSICV {self.id} {long_scripts}/ashs-fast-z.sh {long_scripts}/identity.mat")
            return   

    def do_t2ashs(self, parent_job_name = ""):
        this_job_name=f"t2ashs_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process("t2ashs", self.id, self.mridate, input_files=[self.t2nifti, self.t1trim], \
                            output_files=[self.t2ashs_seg_left, self.t2ashs_seg_right]):
            os.system(f"mkdir {self.filepath}/sfsegnibtend")
            os.system(f"bsub {submit_options} ./wrapper_scripts/run_ashs.sh \
                      {ashs_root} {ashs_t2_atlas} {self.t1trim} {self.t2nifti}\
                      {self.filepath}/sfsegnibtend {self.id}")
            return

    def prc_cleanup(self, parent_job_name = ""):
        for side in sides:
            this_job_name = f"prc_cleanup_{side}_{self.date_id_prefix}"

            if side == "left":
                seg=self.t2ashs_seg_left
                output=self.t2ahs_cleanup_left
            elif side == "right":
                seg=self.t2ashs_seg_right
                output=self.t2ahs_cleanup_right
            
            submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
            if ready_to_process(f"prc_cleanup_{side}", self.id, self.mridate, input_files=[seg], \
                                output_files=[output], parent_job = parent_job_name):
                os.system(f"bsub {submit_options} ./wrapper_scripts/cleanup_prc.sh {seg} {output}")

        this_job_name = f"prc_cleanup_both_{self.date_id_prefix}"
        parent_job_name = f"prc_cleanup_right_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process(f"prc_cleanup_both", self.id, self.mridate, \
                            input_files=[self.t2ahs_cleanup_left, self.t2ahs_cleanup_right], \
                            output_files=[self.t2ahs_cleanup_both], parent_job = parent_job_name):
                os.system(f"bsub {submit_options} c3d {self.t2ashs_tse} -as A {self.t2ahs_cleanup_left} \
                          -interp NN -reslice-identity -push A {self.t2ahs_cleanup_right} \
                          -interp NN -reslice-identity -add -o {self.t2ahs_cleanup_both}")


    def do_t1flair(self, parent_job_name = ""):
        this_job_name=f"t1flair_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process("t1flair", self.id, self.mridate, input_files=[self.flair,self.t1trim], output_files=[self.t1flair]):
            os.system(f"bsub {submit_options} \
                      ./wrapper_scripts/t1_flair_reg.sh {self.t1trim} {self.flair} {self.t1flair}")
            return(this_job_name)

    def do_wmh_prep(self, parent_job_name = ""):
        this_job_name=f"wmhprep_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process("wmhprep", self.id, self.mridate, input_files=[self.flair], output_files=[self.wmh]):
            if not os.path.exists(f"{analysis_input_dir}/{current_date}"):
                logging.info(f"making directory {current_date} in analysis_input for WMH analysis.")               
                os.system(f"mkdir {analysis_input_dir}/{current_date}")
            os.system(f"bsub {submit_options} cp {self.flair} {analysis_input_dir}/{current_date}/{self.mridate}_{self.id}_flair_0000.nii.gz")
            return

    def do_pmtau(self, parent_job_name = ""):
        this_job_name=f"pmtau_{self.date_id_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process("pmtau", self.id, self.mridate, input_files=[self.thickness], \
                            output_files=[self.pmtau_output]):
            os.system(f"bsub {submit_options} ./wrapper_scripts/pmtau.sh {self.id} {self.mridate} {self.filepath}/thickness")
            return

class AmyloidPET:
    # strings for Amyloid PET filepaths
    def __init__(self, subject, amydate):
        self.id = subject
        self.amydate = amydate
        self.filepath=f"{adni_data_dir}/{self.id}/{self.amydate}"
        self.date_id_prefix = f"{self.amydate}_{self.id}"
        self.amy_nifti = f"{self.filepath}/{self.date_id_prefix}_amypet.nii.gz"        


class TauPET:
    # strings for Tau PET filepaths
    def __init__(self, subject, taudate):
        self.id = subject
        self.taudate = taudate
        self.filepath = f"{adni_data_dir}/{self.id}/{self.taudate}"
        self.date_id_prefix = f"{self.taudate}_{self.id}"
        self.tau_nifti = f"{self.filepath}/{self.date_id_prefix}_taupet.nii.gz"
        

class MRIPetReg:
    #strings for filepaths from MRI and PET class instances and function to do MRI-PET registrations and QC
    def __init__(self, pet_type, MRI, PET):
        self.id = MRI.id
        self.mridate = MRI.mridate
        self.t1trim = MRI.t1trim
        self.t2nifti = MRI.t2nifti
        self.t2ashs_flirt_reg = MRI.t2ashs_flirt_reg
        self.pet_type = pet_type
        self.processing_step = f"{self.pet_type}reg"

        if self.pet_type == "amypet":
            self.petdate = PET.amydate
            self.pet_nifti = PET.amy_nifti
        elif self.pet_type == "taupet":
            self.petdate = PET.taudate
            self.pet_nifti = PET.tau_nifti

        self.filepath = f"{adni_data_dir}/{self.id}/{self.petdate}"
        self.reg_prefix = f"{self.petdate}_{self.id}_{self.pet_type}_to_{self.mridate}"

        self.t1_reg_RAS = f"{self.filepath}/{self.reg_prefix}_T10GenericAffine_RAS.mat"
        self.t1_reg_nifti = f"{self.filepath}/{self.reg_prefix}_T1.nii.gz"
        self.t1_reg_qc = f"{self.filepath}/{self.reg_prefix}_T1_qa.png"

        self.t2_reg_nifti = f"{self.filepath}/{self.reg_prefix}_T2.nii.gz"

        self.log_output_dir = f"{self.filepath}/logs_{current_date}"
        if not os.path.exists(self.log_output_dir):
            os.system(f"mkdir {self.log_output_dir}")
        self.bsub_output = f"-o {self.log_output_dir}"


    def do_t1_pet_reg(self, parent_job_name = ""):
        this_job_name=f"t1{self.processing_step}_{self.reg_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process(f"t1{self.processing_step}", self.id, f"{self.mridate}:{self.petdate}", \
                            input_files = [self.t1trim, self.pet_nifti], \
                            output_files = [self.t1_reg_RAS]):
            os.system(f"bsub {submit_options} \
                       {t1petreg_script} \
                       {self.id} {self.t1trim} {self.pet_nifti} {self.mridate} {self.filepath}")
            return (this_job_name)         
        

    def do_t2_pet_reg(self, parent_job_name = ""):
        this_job_name=f"t2{self.processing_step}_{self.reg_prefix}"
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)        
        if ready_to_process(f"t2{self.processing_step}", self.id, f"{self.mridate}:{self.petdate}", \
                            input_files = [self.t2nifti, self.pet_nifti, self.t2ashs_flirt_reg, self.t1_reg_RAS], \
                            output_files = [self.t2_reg_nifti], parent_job = parent_job_name):
            os.system(f"bsub {submit_options} ./wrapper_scripts/t2_pet_registration.sh {self.t2nifti} \
                  {self.pet_nifti} {self.t2_reg_nifti} {self.t2ashs_flirt_reg} {self.t1_reg_RAS}")
            return(this_job_name)

 
    def do_pet_reg_qc(self, parent_job_name = ""):
        processing_step = f"t1{self.processing_step}qc"
        this_job_name=f"{processing_step}_{self.reg_prefix}" 
        submit_options = set_submit_options(this_job_name, self.bsub_output, parent_job_name)
        if ready_to_process(processing_step, self.id, f"{self.mridate}:{self.petdate}", 
                            input_files = [self.t1trim, self.t1_reg_nifti], 
                            output_files = [self.t1_reg_qc],
                            parent_job = parent_job_name):
            os.system(f"bsub {submit_options} \
                  {t1petregqc_script} \
                  {self.t1trim} {self.t1_reg_nifti} {self.t1_reg_qc}")
            return

    
#Log file
# logging.basicConfig(filename=f"{analysis_input_dir}/{current_date}.log", filemode='w', format="%(levelname)s:%(message)s", level=logging.INFO)
#for testing:
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


# Test runs
# mri_to_process = MRI('141_S_6779','2020-10-27')
# mri_to_process = MRI("033_S_7088", "2022-06-27")
# mri_to_process = MRI("114_S_6917", "2021-04-16") 
# mri_to_process = MRI("137_S_6826", "2019-10-17")
# mri_to_process = MRI("099_S_6175", "2020-06-03")
mri_to_process = MRI("126_S_6721", "2021-05-05")

# amy_to_process = AmyloidPET("141_S_6779", "2020-11-11")
# amy_to_process = AmyloidPET("033_S_7088", "2022-07-27")

# tau_to_process = TauPET("114_S_6917", "2021-08-11")
# tau_to_process = TauPET("099_S_6175", "2020-07-09")

# mri_amy_reg_to_process = MRIPetReg('amypet', mri_to_process, amy_to_process)
# mri_tau_reg_to_process = MRIPetReg('taupet', mri_to_process, tau_to_process)


##MRI processing
# ants_job_name = mri_to_process.do_ants()
 
# wbseg_job_name = mri_to_process.do_wbseg(ants_job_name) 
# mri_to_process.do_wbsegqc(wbseg_job_name)

# mri_to_process.do_t1icv() 
# mri_to_process.do_t2ashs() 
# mri_to_process.do_t1flair() 
# mri_to_process.do_wmh_prep() 

# mri_to_process.neck_trim()
# superres_job_name = mri_to_process.do_superres() 
# t1ashs_job_name = mri_to_process.do_t1ashs(superres_job_name) 
# mri_to_process.do_t1mtthk(t1ashs_job_name) 

# mri_to_process.do_pmtau()


##PET processing
# t1_pet_reg_job = mri_tau_reg_to_process.do_t1_pet_reg()
# mri_tau_reg_to_process.do_pet_reg_qc(t1_pet_reg_job)
# mri_tau_reg_to_process.do_t2_pet_reg(t1_pet_reg_job)


