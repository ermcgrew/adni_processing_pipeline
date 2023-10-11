#!/usr/bin/env python

from config import *
from processing import MRI, AmyloidPET, TauPET, MRIPetReg


def convert_symlink_function(types="", all_types=False, inputcsv="", outputcsv=""):
    print(f"run dicom to nifti conversion for {types}")
    # for scantype in scantypes:
    #     if types == scantype or all_types == True and scantype != "anchored":
    #         if inputcsv:
    #             csv_to_read = inputcsv
    #         else:
    #             csv_to_read = os.path.join(datasetup_directories_path["processing_status"],filenames['processing_status'][scantype])
            
    #         logging.info(f"Running dicom to nifti conversion and nifti symlink for scantype {scantype} sessions in csv {csv_to_read}")

    #         df=pd.read_csv(csv_to_read)
    #         # print(df.head())

    #         if scantype == 'mri':
    #             df_newscans = df.loc[(df['NEW_T1'] == 1) | (df['NEW_T2'] == 1)] # | df['NEW_FLAIR'] == 1
    #         else:
    #             df_newscans = df.loc[(df['NEW_PET'] == 1)]

    #         ##Start converting dicom to nifti, line by line    
    #         for index,row in df_newscans.iterrows():
    #             subject = str(row['ID'])
    #             scandate = str(row['SMARTDATE'])
    #             if scantype == 'mri':
    #                 scan_to_process = MRI(subject,scandate)
    #                 ##TODO: Flair dicom to nifti processing--add flair dicom to uid csvs
    #                 uids={"t1_uid": [str(row['IMAGEUID_T1']).split(".")[0], scan_to_process.t1nifti],
    #                       "t2_uid": [str(row['IMAGEUID_T2']).split('.')[0], scan_to_process.t2nifti]} 
    #                     #'flair_uid': str(row['IMAGEUID_FLAIR'])
    #             elif scantype == "amy":
    #                 scan_to_process = AmyloidPET(subject,scandate)
    #                 uids = {'amy_uid':[str(row["IMAGEID"]).split(".")[0], scan_to_process.amy_nifti]}
    #             elif scantype == 'tau':
    #                 scan_to_process = TauPET(subject,scandate)
    #                 uids = {'tau_uid':[str(row["IMAGEID"]).split(".")[0], scan_to_process.tau_nifti]}

    #             logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:{scantype}: Checking for nifti file.")
    #             # print(f"{scan_to_process.id}:{scan_to_process.scandate}:{scantype}: Checking for nifti file.")

    #             for key in uids:
    #                 if uids[key][0] == "nan":
    #                     # TODO:record as no dicom, 
    #                     continue
                   
    #                 if os.path.exists(uids[key][1]):
    #                     status="nifti file already exists in dataset"
    #                 else:
    #                     result = subprocess.run(
    #                             ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/dicom_to_nifti.sh",\
    #                             scan_to_process.id,scan_to_process.scandate,uids[key][0],\
    #                                 scan_to_process.__class__.__name__,scan_to_process.log_output_dir], 
    #                             capture_output=True, text=True)
    #                     if result.returncode != 0:
    #                         logging.warning(f"{scan_to_process.id}:{scan_to_process.scandate}:\
    #                                         dicom_to_nifti.sh error {result.returncode}:{result.stderr}")
    #                         continue

    #                     result_list = result.stdout.split("\n")
    #                     if len(result_list) > 3:
    #                         #first item is "Job <###> submitted to queue..."
    #                         status = result_list[1]
    #                         nifti_file_loc_public = result_list[2]
    #                     else:
    #                         status = result_list[0]
    #                         nifti_file_loc_public = result_list[1]
                        
    #                 logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Nifti conversion status for {key} is:{status}")
    #                 ##TODO: record no dicom exists status 

    #                 if status == "conversion to nifti sucessful":
    #                     if key == "t1_uid":
    #                         df_newscans.at[index,'FINALT1NIFTI'] = nifti_file_loc_public
    #                         df_newscans.at[index,'T1_CONVERT_STATUS'] = 1
    #                     elif key == "t2_uid":
    #                         df_newscans.at[index,'FINALT2NIFTI'] = nifti_file_loc_public
    #                         df_newscans.at[index,'T2_CONVERT_STATUS'] = 1
    #                     #elif key == "flair_uid":
    #                         # df_newscans.at[index,'FINALFLAIRNIFTI'] = nifti_file_loc_public
    #                         # df_newscans.at[index,'FLAIR_CONVERT_STATUS'] = 1
    #                     elif key == "amy_uid":
    #                         df_newscans.at[index,'FILELOC'] = nifti_file_loc_public
    #                         df_newscans.at[index,'AMYNIFTI'] = uids[key][1]
    #                         df_newscans.at[index,'AMY_CONVERT_STATUS'] = 1
    #                     elif key == "tau_uid":
    #                         df_newscans.at[index,'FILELOC'] = nifti_file_loc_public
    #                         df_newscans.at[index,'TAUNIFTI'] = uids[key][1]
    #                         df_newscans.at[index,'TAU_CONVERT_STATUS'] = 1

    #                     # make symlink for nifti file between /PUBLIC and /dataset
    #                     # print(f"ln -sf {nifti_file_loc_public} {uids[key][1]}") 
    #                     os.system(f"ln -sf {nifti_file_loc_public} {uids[key][1]}")

    #                 ##check for any misses (status isn't always correct):
    #                 if not os.path.exists(uids[key][1]) and nifti_file_loc_public:
    #                     # print(f"ln -sf {nifti_file_loc_public} {uids[key][1]}") 
    #                     os.system(f"ln -sf {nifti_file_loc_public} {uids[key][1]}")

    #             ##MRI only step:
    #             if scantype == "mri":

    #                 # logging.info(f"{scan_to_process.id}:{scan_to_process.scandate}:Finding additional information for mri filelocation csv.")
    #                 #site's vendor & model info
    #                 site = scan_to_process.id.split("_")[0]
    #                 siteinfo_result = subprocess.run(
    #                     ["/project/wolk/ADNI2018/scripts/adni_processing_pipeline/get_site_scanner_info.sh",site],
    #                     capture_output=True, text=True)
    #                 siteinfo_result_list = siteinfo_result.stdout.split("\n")[:-1] # remove extra newline at end
    #                 siteinfo_headers = ["Model2","Model3","Vendor2","Vendor3"]
    #                 for i in range(0,len(siteinfo_result_list)):
    #                     df_newscans.at[index,siteinfo_headers[i]] = siteinfo_result_list[i]

    #         ##after all rows in iterrows
    #         logging.info(f"{scantype}:Saving file location csv with new data")
    #         old_fileloc_path = [os.path.join(fileloc_directory_previousrun,x) for x in \
    #                             os.listdir(fileloc_directory_previousrun) if scantype in x][0]
    #         old_filelocs_df = pd.read_csv(old_fileloc_path)
    #         all_filelocs = pd.concat([df_newscans, old_filelocs_df], ignore_index=True)
    #         #keep most recent (e.g. updated) if any duplicates
    #         all_filelocs.drop_duplicates(subset=['RID','SMARTDATE'],keep='last', inplace=True) 
    #         all_filelocs.sort_values(by=["RID","SMARTDATE"], ignore_index=True, inplace=True)
    #         print(all_filelocs.info())
    #         print(all_filelocs.head())
    #         print(df_newscans.info())
    #         df_newscans.to_csv("/project/wolk/ADNI2018/scripts/adni_processing_pipeline/testing/newmris_convertsymlink_output.csv")
    #         print(old_filelocs_df.info())
            

    #         ##output df to file 
            # if outputcsv:
            #     all_filelocs.to_csv(outputcsv,index=False,header=True)
            # else:
            #     all_filelocs.to_csv(os.path.join(datasetup_directories_path["filelocations"],\
            #                         filenames['filelocations'][scantype]),index=False,header=True)

# print("in convert separate script")