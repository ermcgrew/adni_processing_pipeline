
# global var
adni_data_dir = "/project/wolk_2/ADNI2018/dataset/"

class T1:
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
        self.T1_wb_seg_QC = f"{self.filepath}{self.date_id_prefix}_wbseg.qa.png"
        self.T2_nifti = f"{self.filepath}{self.date_id_prefix}_T2w.nii.gz"
        self.flair = f"{self.filepath}{self.date_id_prefix}_flair.nii.gz"

    def ants_thick(self):
        print(f"Use FTDC's ANTS gear code")

    def extract_brain(self):
        print(f"os.system(f'bsub < brainx_phil.sh {self.T1_trim}')")
        print(f"record job ID, action >> to log")
    
    def wb_seg(self):
        print(f"bsub < wbseg script")

    def wb_seg_QC(self):
        print(f"call QC script: simplesegqa.sh {self.T1_trim} {self.T1_wb_seg} wholebrainlabels_itksnaplabelfile.txt {self.T1_wb_seg_QC}")        
    
    def ashst1(self):
        print('ASHST1')
    
    def ashst2(self, atlas):
        print(f"If not {self.filepath}sfsegnibtend/final/${self.id}_right_lfseg_corr_nogray.nii.gz")
        print(f"bsub < ashs_and_cleanup.sh {atlas} {self.T1_trim} {self.T2_nifti}")


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





# T1processing=T1('035_S_6788','2020-03-27')
# print(T1processing.T1_nifti)
# print(T1processing.T1_trim)
# print(T1processing.T1_extract_brain)
# T1processing.extract_brain()
# T1processing.wb_seg_QC()

# Amyloidprocessing = AmyloidPET("035_S_6788","2019-06-13")

# testreg = T1PetReg('amyloid',T1processing, Amyloidprocessing)
# print(f"Now doing {testreg.pet_type} PET")
# testreg.pet_registration()