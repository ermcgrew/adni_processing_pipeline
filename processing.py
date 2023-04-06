import datetime
import logging
import os

#Filepaths for scripts called in processing functions
ashs_t1_atlas = "/home/lxie/ASHS_atlases/PMC_3TT1_atlas_noSR"
ashs_root = "/project/hippogang_2/longxie/pkg/ashs/ashs-fast"
long_scripts = "/home/lxie/ADNI2018/scripts"
icv_atlas = "/home/lxie/ASHS_atlases/ICVatlas_3TT1"
ashs_t2_atlas = "/project/hippogang_2/pauly/wolk/atlases/ashs_atlas_upennpmc_20170810"




#main file directories
adni_analysis_dir = "/project/wolk_2/ADNI2018/analysis_input"
# adni_data_dir = "/project/wolk_2/ADNI2018/dataset"
# for testing
adni_data_dir = "/project/wolk_2/ADNI2018/scripts/pipeline_test_data"

#other variables
sides = ["left", "right"]
current_date = datetime.datetime.now().strftime("%Y_%m_%d")


def wait_value(parent_job_name):
    if parent_job_name:
        return f"-w done({parent_job_name})"
    else:
        return ""

def ready_to_process(processing_step, id, date, input_files = ['', True], output_files = ['', False]):
#output files all "OR" comparisons: {file} or False == True, unless {file} is not there
#input files all "AND" comparisons: {file} and True == True, unless {file} is not there
    if [file for file in output_files if os.path.exists(file)]:
        logging.info(f"{id}:{date}: {processing_step} already run.")
        return False
    else:
        if [file for file in input_files if os.path.exists(file)]:
            logging.info(f"{id}:{date}: Running {processing_step}")
            return True
        else:
            logging.info(f"{id}:{date}: One or more input files missing, cannot run {processing_step}")
            return False


class MRI:
    #strings for MRI filepaths and functions for MRI processing

    def __init__(self, subject, mridate):
        self.id = subject
        self.mridate = mridate
        # self.T1_dicom_filepath = f"/project/wolk/PUBLIC/Dicoms/{self.id}/MRI3T/{self.mridate}/...dcm"
        self.filepath=f"{adni_data_dir}/{self.id}/{self.mridate}"
        self.date_id_prefix = f"{self.mridate}_{self.id}"
        
        self.t1nifti = f"{self.filepath}/{self.date_id_prefix}_T1w.nii.gz"
        self.t1trim = f"{self.filepath}/{self.date_id_prefix}_T1w_trim.nii.gz"
        
        self.brainx = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain.nii.gz"
        self.wbseg= f"{self.filepath}/{self.date_id_prefix}_wholebrainseg/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz"
        self.wbsegqc = f"{self.filepath}/{self.date_id_prefix}_wbseg_qa.png"
        
        self.superres = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_denoised_SR.nii.gz"
        
        self.t1ashs_seg_left = f"{self.filepath}/ASHST1/final/{self.id}_left_lfseg_heur.nii.gz"
        self.t1ashs_seg_right = f"{self.filepath}/ASHST1/final/{self.id}_right_lfseg_heur.nii.gz"
        self.t1ashs_qc_left = f"{self.filepath}/ASHST1/qa/qa_seg_bootstrap_heur_left_qa.png"
        self.t1ashs_qc_right = f"{self.filepath}/ASHST1/qa/qa_seg_bootstrap_heur_right_qa.png"
    
        #t1ashs producing these names as of 4/5/2023:
        # self.t1ashs_qc_left = f"{self.filepath}/ASHST1/qa/final_left.png"
        # self.t1ashs_qc_right = f"{self.filepath}/ASHST1/qa/final_right.png"    

        self.t1mtthk_left = f"{self.filepath}/ASHST1_MTLCORTEX_MSTTHK/{self.date_id_prefix}_left_thickness.csv"
        self.t1mtthk_right = f"{self.filepath}/ASHST1_MTLCORTEX_MSTTHK/{self.date_id_prefix}_right_thickness.csv"
        self.t1icv_qc_left = f"{self.filepath}/ASHSICV/qa/qa_seg_multiatlas_corr_nogray_left_qa.png"
        self.t1icv_qc_right = f"{self.filepath}/ASHSICV/qa/qa_seg_multiatlas_corr_nogray_right_qa.png"

        self.t2nifti = f"{self.filepath}/{self.date_id_prefix}_T2w.nii.gz"
        self.t2ashs_seg_left = f"{self.filepath}/sfsegnibtend/final/${self.id}_left_lfseg_corr_nogray.nii.gz"
        self.t2ashs_seg_right = f"{self.filepath}/sfsegnibtend/final/${self.id}_right_lfseg_corr_nogray.nii.gz"
        self.t2ashs_qc_left = f"{self.filepath}/sfsegnibtend/qa/"
        self.t2ashs_qc_right = f"{self.filepath}/sfsegnibtend/qa/"

        self.flair = f"{self.filepath}/{self.date_id_prefix}_flair.nii.gz"
        self.wmh = f"{self.filepath}/{self.date_id_prefix}_wmh.nii.gz"
        self.t1flair = f"{self.filepath}/{self.date_id_prefix}_T1w_trim_to_flair.mat"

    def do_ants(self):
        this_job_name=f"ants_{self.date_id_prefix}"
        if ready_to_process('ants', self.id, self.mridate, input_files=[self.t1nifti], output_files=[self.t1trim]):
            print(f"Use FTDC's ANTS gear code")
            return this_job_name

    def do_brainx(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"brainx_{self.date_id_prefix}"
        if ready_to_process('brainx',self.id,self.mridate, input_files=[self.t1trim], output_files = [self.brainx]):
            # os.system(f'bsub -o {self.filepath} ./wrapper_scripts/brain_extract.sh {self.t1trim}')
            return this_job_name

    def do_wbseg(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"wbseg_{self.date_id_prefix}"
        if ready_to_process('wbseg', self.id, self.mridate, input_files=[self.brainx], output_files = [self.wbseg]):
            # os.system(f"bsub -o {self.filepath} -M 12G -q bsc_long \
            #       /home/sudas/bin/ahead_joint/turnkey/bin/hippo_seg_WholeBrain_itkv4_v3.sh \
            #       {self.filepath} \
            #       {self.filepath}{self.date_id_prefix}_wholebrainseg \
            #       {self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain \
            #       /home/sudas/bin/ahead_joint/turnkey/data/WholeBrain_brainonly 1")
            return this_job_name          
     
    def do_wbsegqc(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"wbsegqc_{self.date_id_prefix}"
        if ready_to_process('wbsegqc', self.id, self.mridate, input_files=[self.t1trim,self.wbseg], output_files = [self.wbsegqc]):
            # os.system(f"bsub -o {self.filepath} /project/hippogang_1/srdas/wd/TAUPET/longnew/simplesegqa.sh \
            #   {self.t1trim} {self.wbseg} \
            #   /project/hippogang_1/srdas/wd/TAUPET/longnew/wholebrainlabels_itksnaplabelfile.txt  \
            #   {self.wbsegqc}")
            return         

    def do_superres(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"superres_{self.date_id_prefix}"
        if ready_to_process('superres', self.id, self.mridate, input_files=[self.t1trim], output_files=[self.superres]):
            # os.system(f"bsub -o {self.filepath} -M 4G -n 1 ./wrapper_scripts/super_resolution.sh \
            #           {self.filepath} {self.t1trim} {self.superres}")
            return this_job_name

    def do_t1ashs(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"t1ashs_{self.date_id_prefix}"
        if ready_to_process("t1ashs", self.id, self.mridate, input_files=[self.t1trim, self.superres], output_files=[self.t1ashs_qc_left, self.t1ashs_qc_right]):
            # os.system(f"mkdir {self.filepath}/ASHST1")
            ## set ASHS_ROOT before running
            # os.system(f"bsub -J {this_job_name} {wait} -o {self.filepath} \
            #       {ashs_root}/bin/ashs_main.sh \
            #       -a {ashs_t1_atlas} -d -T -I {self.id} -g {self.t1trim} -f {self.superres} \
            #       -l -s 1-7 \
            #       -z {long_scripts}/ashs-fast-z.sh \
            #       -m {long_scripts}/identity.mat -M \
            #       -w {self.filepath}/ASHST1")
            return(this_job_name)
    
    def do_t1mtthk(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        for side in sides:
            if side == "left":
                ashs_thick = self.t1mtthk_left
                ashs_seg = self.t1ashs_seg_left
                this_job_name=f"t1mtthk_left_{self.date_id_prefix}"
            elif side == "right":
                ashs_thick = self.t1mtthk_right
                ashs_seg = self.t1ashs_seg_right
                this_job_name=f"t1mtthk_right_{self.date_id_prefix}"

            if ready_to_process("t1mtthk", self.id, self.mridate, input_files=[ashs_seg], output_files=[ashs_thick]):
                # os.system(f"bsub -o {self.filepath} -J {this_job_name} {wait} -M 12G -n 1 \
                #            ./wrapper_scripts/multitemplate_thickness.sh {self.id} {self.mridate}\
                #            {side} {ashs_seg} {self.filepath}/ASHST1_MTLCORTEX_MSTTHK")  
                return

    def do_t1icv(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"t1icv_{self.date_id_prefix}"
        if ready_to_process("t1icv", self.id, self.mridate, input_files=[self.t1trim], output_files=[self.t1icv_qc_left, self.t1icv_qc_right]):
            # os.system(f"mkdir {self.filepath}ASHSICV")
            # os.system(f"{ashs_root}/bin/ashs_main.sh \
            #     -a $ICVATLAS -d -T -I {self.id} -g {self.t1trim} -f {self.t1trim} \
            #     -l -s 1-7 \
            #     -z {long_scripts}/ashs-fast-z.sh \
            #     -m {long_scripts}/identity.mat -M \
            #     -B \
            #     -w {self.filepath} &")
            return   

    def do_t2ashs(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"t2ashs_{self.date_id_prefix}"
        if ready_to_process("t2ashs", self.id, self.mridate, input_files=[self.t2nifti], output_files=[self.t2ashs_seg_left, self.t2ashs_seg_right]):
            # export ashs_root in shell first
            # export ASHS_ROOT=/project/hippogang_2/longxie/pkg/ashs/ashs-fast
            # os.system(f"mkdir {self.filepath}sfsegnibtend")
            # os.system(f"{ashs_root}/bin/ashs_main.sh \
            #       -a {ashs_t2_atlas} -g {self.t1trim} -f {self.t2nifti} \
            #       -d -T -I {self.id} -w {self.filepath}sfsegnibtend")
            return

    def do_t1flair(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"t1flair_{self.date_id_prefix}"
        if ready_to_process("t1flair", self.id, self.mridate, input_files=[self.flair,self.t1trim], output_files=[self.t1flair]):
            # os.system(f"bsub -o {self.filepath} -J {this_job_name} {wait} \
            #           ./wrapper_scripts/t1_flair_reg.sh {self.t1trim} {self.flair} {self.t1flair}")
            return(this_job_name)

    def do_wmh_prep(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        if ready_to_process("wmh", self.id, self.mridate, input_files=[self.flair], output_files=[self.wmh]):
            if not os.path.exists(f"{adni_analysis_dir}/{current_date}"):
                logging.info(f"making directory {current_date} in analysis_input for WMH analysis.")               
                # os.system(f"mkdir {adni_analysis_dir}/{current_date}")
            # os.system(f"cp {self.flair} {adni_analysis_dir}/{current_date}/{self.mridate}_{self.id}_flair_0000.nii.gz")
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
        

class T1PetReg:
    #strings for filepaths from MRI and PET class instances and function to do T1-PET registration
    def __init__(self, pet_type, T1, PET):
        self.id = T1.id
        self.mridate = T1.mridate
        self.t1trim = T1.t1trim
        self.pet_type = pet_type
        self.processing_step = f"t1{self.pet_type}reg"

        if self.pet_type == "amypet":
            self.petdate = PET.amydate
            self.pet_nifti = PET.amy_nifti
        elif self.pet_type == "taupet":
            self.petdate = PET.taudate
            self.pet_nifti = PET.tau_nifti

        self.filepath = f"{adni_data_dir}/{self.id}/{self.petdate}"
        self.reg_prefix = f"{self.petdate}_{self.id}_{self.pet_type}_to_{self.mridate}"
        self.reg_RAS = f"{self.filepath}/{self.reg_prefix}_T10GenericAffine_RAS.mat"
        self.reg_nifti = f"{self.filepath}/{self.reg_prefix}_T1.nii.gz"
        self.reg_qc = f"{self.filepath}/{self.reg_prefix}_T1_qa.png"


    def do_pet_reg(self):
        this_job_name=f"{self.processing_step}_{self.reg_prefix}"
        if ready_to_process(self.processing_step, self.id, f"{self.mridate}:{self.petdate}", input_files = [self.t1trim, self.pet_nifti], output_files = [self.reg_RAS]):
            # os.system(f"bsub -o {self.filepath}/{self.reg_prefix}.log \
                #       /project/hippogang_1/srdas/wd/TAUPET/longnew/coreg_pet.sh \
                #       {self.id} {self.t1trim} {self.pet_nifti} {self.mridate} {self.filepath}")
            return (this_job_name)         
 
    def do_pet_reg_qc(self, parent_job_name = ""):
        wait = wait_value(parent_job_name)
        this_job_name=f"{self.processing_step}_{self.reg_id_prefix}"
        if ready_to_process(self.processing_step, self.id, f"{self.mridate}:{self.petdate}", input_files = [self.t1trim, self.reg_nifti], output_files = [self.reg_qc]):
            # os.system(f"bsub -o {self.filepath}/{self.reg_prefix}_{self.pet_type}regqa.log \
            #       /project/hippogang_1/srdas/wd/TAUPET/longnew/simpleregqa.sh \
            #       {self.t1trim} {self.reg_nifti} {self.reg_qc}")
            return


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

MRIprocessing=MRI('141_S_6779','2020-10-27')
# print(MRIprocessing.t1nifti)
# print(MRIprocessing.t1trim)
# print(MRIprocessing.brainx)
MRIprocessing.do_wbseg()

Amyloidprocessing = AmyloidPET("141_S_6779","2020-11-11")
testreg = T1PetReg('amypet', MRIprocessing, Amyloidprocessing)
testreg.do_pet_reg()