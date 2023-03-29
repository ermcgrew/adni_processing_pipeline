import csv
import logging
import os
from processing import T1, T1PetReg, AmyloidPET, TauPET


def reformat_dates(date):
    MDYlist=date.split('/')
    if len(MDYlist[0]) == 1:
        month = "0" + MDYlist[0]
    else:
        month = MDYlist[0]
    if  len(MDYlist[1]) == 1:
        day = "0" + MDYlist[1]
    else:
        day=MDYlist[1]
    year="20" + MDYlist[2]
    return year + "-" + month + "-" + day


def file_exists(filepath):
    return os.path.isfile(filepath) 
    # works for files and symlinks
    # to check for directories too, use os.path.exists


def main():
    with open("../MRI3TLIST_testdata.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count+=1
            else:
                line_count+=1
                subject = row[1]
                if "/" in row[6]:
                    mridate = reformat_dates(row[6])
                else:
                    mridate = row[6]

                ##would this be the csv directly from adni?
                ##call to download dicom file from adni
                ## run dicom to nifti --this should be a general function for all scans
                ##then create t1 instance
                ##dicom location is saved in t1 class to add to final spreadsheet
                ##do we need to create the intermediate spreadsheets with nifti paths if we're not using db anymore?

                # print(subject, mridate)
                t1_to_process=T1(subject,mridate)
                logging.info(f"Now processing: {t1_to_process.T1_nifti}")

                t1_to_process.ants_thick()

                if file_exists(t1_to_process.T1_extract_brain):
                    logging.info(f"Whole Brain Segmentation already done for {t1_to_process.T1_nifti}")
                else:
                    if file_exists(t1_to_process.T1_trim):
                        t1_to_process.wb_seg()
                    else:
                        logging.info(f"No T1 trim file for {t1_to_process.T1_nifti}, cannot run whole brain segmentation")
                t1_to_process.t1_ashs()
                t1_to_process.t2_ashs('purple')
                t1_to_process.t1_flair_reg()
                t1_to_process.wmh()

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
# csvlist=['MRI.csv','amy.csv','tau.csv']
    