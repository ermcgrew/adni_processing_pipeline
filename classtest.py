class T1:
    def __init__(self, subject, mridate):
        self.id = subject
        self.mridate = mridate
        # self.T1_dicom_filepath = f"/project/wolk/PUBLIC/Dicoms/{self.id}/MRI3T/{self.mridate}/...dcm"
        self.base_filepath=f"/project/wolk_2/ADNI2018/dataset/{self.id}/{self.mridate}"
        
        self.T1_nifti = f"{self.base_filepath}/{self.mridate}_{self.id}_T1w.nii.gz"
        self.T1_trim = f"{self.base_filepath}/{self.mridate}_{self.id}_T1w_trim.nii.gz"
        self.T1_extract_brain = f"{self.base_filepath}/{self.mridate}_{self.id}_T1w_trim_brainx_ExtractedBrain.nii.gz"
        self.T1_wb_seg= f"{self.base_filepath}/{self.mridate}_{self.id}_wholebrainseg/{self.mridate}_{self.id}_T1w_trim_brainx_ExtractedBrain/{self.mridate}_{self.id}_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz"
        self.T1_wb_seg_QC = f"{self.base_filepath}/{self.mridate}_{self.id}_wbseg.qa.png"

    def extract_brain(self):
        print(f" bsub ./brainx_phil.sh {self.T1_trim}")
        print(f"record job ID, action >> to log")
    
    def wb_seg(self):
        print(f"bsub wbseg script")

    def wb_seg_QC(self):
        print(f"call QC script: ./simplesegqa.sh {self.T1_trim} {self.T1_wb_seg} wholebrainlabels_itksnaplabelfile.txt {self.T1_wb_seg_QC}")        

    def t1AmyRegistration(self,amyloid):
        print(f"bsub ./coreg_pet.sh {self.T1_trim} {amyloid}")


class AmyloidPET:
    def __init__(self, subject, amydate):
        self.id = subject
        self.amydate = amydate
        self.base_filepath=f"/project/wolk_2/ADNI2018/dataset/{self.id}/{self.amydate}/{self.amydate}_{self.id}_"
        self.amypet = f"{self.base_filepath}amypet.nii.gz"



T1processing=T1('035_S_6788','2020-03-27')
print(T1processing.T1_nifti)
print(T1processing.T1_trim)
print(T1processing.T1_extract_brain)
T1processing.extract_brain()
T1processing.wb_seg_QC()

Amyloidprocessing = AmyloidPET("035_S_6788","2019-06-13")
T1processing.t1AmyRegistration(Amyloidprocessing.amypet)
