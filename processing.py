import logging
import os

ashs_atlas = "/home/lxie/ASHS_atlases/PMC_3TT1_atlas_noSR"
ashs_root = "/project/hippogang_2/longxie/pkg/ashs/ashs-fast"
long_scripts = "/home/lxie/ADNI2018/scripts"
icv_atlas = "/home/lxie/ASHS_atlases/ICVatlas_3TT1"
# adni_data_dir = "/project/wolk_2/ADNI2018/dataset/"
# for testing
adni_data_dir = "/project/wolk_2/ADNI2018/scripts/pipeline_test_data/"

def file_exists(filepath):
    return os.path.isfile(filepath) 
    # works for files and symlinks
    # to check for directories too, use os.path.exists


class MRI:
    def __init__(self, subject, mridate):
        self.id = subject
        self.mridate = mridate
        # self.T1_dicom_filepath = f"/project/wolk/PUBLIC/Dicoms/{self.id}/MRI3T/{self.mridate}/...dcm"
        self.filepath=f"{adni_data_dir}{self.id}/{self.mridate}/"
        self.date_id_prefix = f"{self.mridate}_{self.id}"
        
        self.T1_nifti = f"{self.filepath}{self.date_id_prefix}_T1w.nii.gz"
        self.T1_trim = f"{self.filepath}{self.date_id_prefix}_T1w_trim.nii.gz"
        
        self.T1_extract_brain = f"{self.filepath}{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain.nii.gz"
        self.T1_wb_seg= f"{self.filepath}{self.date_id_prefix}_wholebrainseg/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain/{self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz"
        self.T1_wb_seg_QC = f"{self.filepath}{self.date_id_prefix}_wbseg_qa.png"
        
        self.T1_SR = f"{self.filepath}{self.date_id_prefix}_T1w_trim_denoised_SR.nii.gz"
        self.T1_ashs_qc_left = f"{self.filepath}ASHST1/qa/qa_seg_bootstrap_heur_left_qa.png"
        self.T1_ashs_qc_right = f"{self.filepath}ASHST1/qa/qa_seg_bootstrap_heur_right_qa.png"

        self.T1_ashs_icv_qc_left = f"{self.filepath}ASHSICV/qa/qa_seg_multiatlas_corr_nogray_left_qa.png"
        self.T1_ashs_icv_qc_right = f"{self.filepath}ASHSICV/qa/qa_seg_multiatlas_corr_nogray_right_qa.png"

        self.T2_nifti = f"{self.filepath}{self.date_id_prefix}_T2w.nii.gz"
        
        self.flair = f"{self.filepath}{self.date_id_prefix}_flair.nii.gz"
        self.T1_flair = f"{self.filepath}{self.date_id_prefix}_T1w_trim_to_flair.mat"

    def ants_thick(self):
        print(f"Use FTDC's ANTS gear code")        
    
    def wb_seg(self):
        if file_exists(self.T1_wb_seg):
            logging.info(f"Whole Brain Segmentation already done for {self.T1_nifti}")
            return
        else:
            if file_exists(self.T1_trim):
                logging.info(f"{self.id}:{self.mridate}: Running whole brain extraction")
                # os.system(f'bsub -o {self.filepath} ./wrapper_scripts/brain_extract.sh {self.T1_trim}')
                logging.info(f"{self.id}:{self.mridate}: Running whole brain segmentation")
                # os.system(f"bsub -o {self.filepath} -M 12G -q bsc_long \
                #       /home/sudas/bin/ahead_joint/turnkey/bin/hippo_seg_WholeBrain_itkv4_v3.sh \
                #       {self.filepath} \
                #       {self.filepath}{self.date_id_prefix}_wholebrainseg \
                #       {self.date_id_prefix}_T1w_trim_brainx_ExtractedBrain \
                #       /home/sudas/bin/ahead_joint/turnkey/data/WholeBrain_brainonly 1")
                if os.path.isfile(self.T1_wb_seg_QC):
                    logging.info(f"{self.id}:{self.mridate}: Whole brain segmentation QC file already generated")
                    return
                else:
                    logging.info(f"{self.id}:{self.mridate}: Generating QC files for whole brain segmentation")
                    # os.system(f"bsub -o {self.filepath} /project/hippogang_1/srdas/wd/TAUPET/longnew/simplesegqa.sh \
                    #       {self.T1_trim} {self.T1_wb_seg} \
                    #       /project/hippogang_1/srdas/wd/TAUPET/longnew/wholebrainlabels_itksnaplabelfile.txt  \
                    #       {self.T1_wb_seg_QC}")        
            else:
                logging.info(f"{self.id}:{self.mridate}: No T1 trim file, cannot run whole brain segmentation")
                return
    
    def t1_super_res(self):
        if file_exists(self.T1_SR):
            logging.info(f"{self.id}:{self.mridate}: Super Resolution already created")
            return
        else:
            if file_exists(self.T1_trim):
                logging.info(f"{self.id}:{self.mridate}: Running super resolution")
                # os.system(f"bsub -o {self.filepath} -M 4G -n 1 ./wrapper_scripts/super_resolution.sh \
                #           {self.filepath} {self.T1_trim} {self.T1_SR}")
            else:
                logging.info(f"{self.id}:{self.mridate}: No T1 trim file, cannot run super resolution")
                return

    def t1_ashs(self):
        if file_exists(self.T1_ashs_qc_left) and file_exists(self.T1_ashs_qc_right):
            logging.info(f"{self.id}:{self.mridate}: ASHST1 already run")
            return
        else:
            if file_exists(self.T1_trim) and file_exists(self.T1_SR):
                logging.info(f"{self.id}:{self.mridate}: Running ASHST1")
                # os.system(f"mkdir {self.filepath}ASHST1")
                # os.system(f"{ashs_root}/bin/ashs_main.sh \
                #     -a {ashs_atlas} -d -T -I {self.id} -g {self.T1_trim} -f {self.T1_SR} \
                #     -l -s 1-7 \
                #     -z {long_scripts}/ashs-fast-z.sh \
                #     -m {long_scripts}/identity.mat -M \
                #     -w {self.filepath}ASHST1")
            else:
                logging.info(f"{self.id}:{self.mridate}: No T1 trim file or no T1_denoised_SR file, cannot run ASHST1")
                return
    
    def t1_ashs_icv(self):
        if file_exists(self.T1_ashs_icv_qc_left) and file_exists(self.T1_ashs_icv_qc_right):
            logging.info(f"{self.id}:{self.mridate}: ASHSICV already run")
            return
        else:
            if file_exists(self.T1_trim):
                logging.info(f"{self.id}:{self.mridate}: Running ASHSICV")
                # os.system(f"mkdir {self.filepath}ASHSICV")
                # os.system(f"{ashs_root}/bin/ashs_main.sh \
                #     -a $ICVATLAS -d -T -I {self.id} -g {self.T1_trim} -f {self.T1_trim} \
                #     -l -s 1-7 \
                #     -z {long_scripts}/ashs-fast-z.sh \
                #     -m {long_scripts}/identity.mat -M \
                #     -B \
                #     -w {self.filepath} &")
            else:
                logging.info(f"{self.id}:{self.mridate}: No T1 trim file, cannot run ASHSICV")
                return


    def t2_ashs(self, atlas):
        print(f"If not {self.filepath}sfsegnibtend/final/${self.id}_right_lfseg_corr_nogray.nii.gz")
        print(f"bsub ashs_and_cleanup.sh {atlas} {self.T1_trim} {self.T2_nifti}")

    def t1_flair_reg(self):
        print(f"bsub flirt {self.T1_trim} {self.flair}")

    def wmh(self):
        print(f"collect files to send to lambda-picsl {self.flair}")


class AmyloidPET:
    def __init__(self, subject, amydate):
        self.id = subject
        self.amydate = amydate
        self.filepath=f"/project/wolk_2/ADNI2018/dataset/{self.id}/{self.amydate}/"
        self.date_id_prefix = f"{self.amydate}_{self.id}"
        self.amy_nifti = f"{self.filepath}{self.date_id_prefix}_amypet.nii.gz"        


class TauPET:
    def __init__(self, subject, taudate):
        self.id = subject
        self.taudate = taudate
        self.filepath = f"/project/wolk_2/ADNI2018/dataset/{self.id}/{self.taudate}/"
        self.date_id_prefix = f"{self.taudate}_{self.id}"
        self.tau_nifti = f"{self.filepath}{self.date_id_prefix}_taupet.nii.gz"
        

class T1PetReg:
    def __init__(self, pet_type, T1, PET):
        self.subject = T1.id
        self.mridate = T1.mridate
        self.T1_trim = T1.T1_trim
        self.pet_type = pet_type
        if self.pet_type == 'amyloid':
            self.petdate = PET.amydate
            self.pet_nifti = PET.amy_nifti
        elif self.pet_type == "tau":
            self.petdate = PET.taudate
            self.pet_nifti = PET.tau_nifti

    def pet_registration(self):
        registration_filepath = f"{adni_data_dir}{self.subject}/{self.petdate}/{self.petdate}_{self.subject}_{self.pet_type}_to_{self.mridate}"
        print(f"If not {registration_filepath}_T10GenericAffine_RAS.mat")
        print(f"Run: coreg_pet.sh {self.T1_trim} {self.pet_nifti}")
        print("time to create QC files")
        print(f"if not {registration_filepath}_T1_qa.png")
        print(f"Run: simpleregqa.sh {self.T1_trim}")


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

MRIprocessing=MRI('141_S_6779','2020-10-27')

# print(MRIprocessing.T1_nifti)
# print(MRIprocessing.T1_trim)
# print(MRIprocessing.T1_extract_brain)
print(MRIprocessing.T1_SR)

# MRIprocessing.wb_seg()
# MRIprocessing.t1_super_res()
MRIprocessing.t1_ashs()

# Amyloidprocessing = AmyloidPET("035_S_6788","2019-06-13")
# testreg = T1PetReg('amyloid',MRIprocessing, Amyloidprocessing)
# print(f"Now doing {testreg.pet_type} PET")
# testreg.pet_registration()