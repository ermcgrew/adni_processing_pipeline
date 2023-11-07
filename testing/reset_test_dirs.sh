# #!/usr/bin/bash
# cd /project/wolk/ADNI2018/scripts/pipeline_test_data/
mridata="/project/wolk/ADNI2018/analysis_input/adni_data_setup_csvs/20230731_processing_status/mri_processing_status.csv"

foldertestone=necktrim_trimtestants_ashsroot_pauly
foldertesttwo=necktrim_trimtestants_ashsroot_lxie
# testfolder=necktrim_preprocessedInput

testroot="/project/wolk/ADNI2018/scripts/pipeline_test_data"
dataroot="/project/wolk/ADNI2018/dataset"
csvtoread="/project/wolk/ADNI2018/analysis_input/testversions_processingstatuscsvs/anchored_processing_status.csv"

cat $csvtoread | while read line ; do 
    id=$( echo $line | cut -d "," -f 1 )
    taudate=$( echo $line | cut -d "," -f 6)
    mridate=$( echo $line | cut -d "," -f 15)
    amydate=$( echo $line | cut -d "," -f 36)
    echo $id, $taudate, $mridate, $amydate

    if [[ $id == "ID" ]] ; then
        continue 
    else
        taudir="${id}/${taudate}"
        amydir="${id}/${amydate}"
        mridir="${id}/${mridate}"

        mkdir -p "${testroot}/${taudir}"
        cp ${dataroot}/${taudir}/*taupet.nii.gz "${testroot}/${taudir}"

        mkdir -p "${testroot}/${amydir}"
        cp ${dataroot}/${amydir}/*amypet.nii.gz "${testroot}/${amydir}"

        mkdir -p "${testroot}/${mridir}"
        cp ${dataroot}/${mridir}/*T1w.nii.gz ${dataroot}/${mridir}/*T2w.nii.gz "${testroot}/${mridir}"
    fi

done
# cat $mridata | while read line ; do 
#     id=$( echo $line | cut -d "," -f 3 )
#     date=$( echo $line | cut -d "," -f 2)
#     echo $id, $date
#     if [[ $id == "ID" || $date == "2022-06-23" || $date == "2022-07-01" || $date == "2022-11-21" || $date == "2022-10-17" ]] ; then
#         continue 
#     else
        # for root in $foldertestone $foldertesttwo ; do
#             for i in {1..5} ; do 
#                 # mkdir -p ./${root}_${i}/${id}/${date}
#                 # cp ./${id}/${date}/*T1w_trimtestants.nii.gz ./${id}/${date}/*T1w.nii.gz ./${id}/${date}/*T2w.nii.gz ./${root}_${i}/${id}/${date}
#                 ##run python?      
#             done
#         done
#     fi
# done


# mkdir -p ./${foldertestone}/024_S_2239/2019-06-03
# mkdir -p ./${foldertestone}/033_S_0734/2018-10-10
# mkdir -p ./${foldertestone}/114_S_6917/2021-04-16
# mkdir -p ./${foldertestone}/100_S_0069/2020-01-23

# mkdir -p ./${foldertesttwo}/018_S_2155/2022-11-21
# mkdir -p ./${foldertesttwo}/024_S_2239/2019-06-03
# mkdir -p ./${foldertesttwo}/033_S_0734/2018-10-10
# mkdir -p ./${foldertesttwo}/068_S_0127/2020-03-12
# mkdir -p ./${foldertesttwo}/114_S_6917/2021-04-16
# mkdir -p ./${foldertesttwo}/941_S_6581/2022-10-17
# mkdir -p ./${foldertesttwo}/100_S_0069/2020-01-23


# cp -r ./018_S_2155/2022-11-21/* ./${foldertestone}/018_S_2155/2022-11-21
# cp -r ./024_S_2239/2019-06-03/* ./${foldertestone}/024_S_2239/2019-06-03
# cp -r ./033_S_0734/2018-10-10/* ./${foldertestone}/033_S_0734/2018-10-10
# cp -r ./068_S_0127/2020-03-12/* ./${foldertestone}/068_S_0127/2020-03-12
# cp -r ./114_S_6917/2021-04-16/* ./${foldertestone}/114_S_6917/2021-04-16
# cp -r ./941_S_6581/2022-10-17/* ./${foldertestone}/941_S_6581/2022-10-17
# cp -r ./100_S_0069/2020-01-23/* ./${foldertestone}/100_S_0069/2020-01-23

# cp -r ./018_S_2155/2022-11-21/* ./${foldertesttwo}/018_S_2155/2022-11-21
# cp -r ./024_S_2239/2019-06-03/* ./${foldertesttwo}/024_S_2239/2019-06-03
# cp -r ./033_S_0734/2018-10-10/* ./${foldertesttwo}/033_S_0734/2018-10-10
# cp -r ./068_S_0127/2020-03-12/* ./${foldertesttwo}/068_S_0127/2020-03-12
# cp -r ./114_S_6917/2021-04-16/* ./${foldertesttwo}/114_S_6917/2021-04-16
# cp -r ./941_S_6581/2022-10-17/* ./${foldertesttwo}/941_S_6581/2022-10-17
# cp -r ./100_S_0069/2020-01-23/* ./${foldertesttwo}/100_S_0069/2020-01-23



# cp -r ./018_S_2155/2022-11-21/*T1w_trimtestants.nii.gz ./${foldertestone}/018_S_2155/2022-11-21
# cp -r ./941_S_6581/2022-10-17/*T1w_trimtestants.nii.gz ./${foldertestone}/941_S_6581/2022-10-17
# cp -r ./018_S_2155/2022-11-21/*T1w_trimtestants.nii.gz ./${foldertesttwo}/018_S_2155/2022-11-21
# cp -r ./941_S_6581/2022-10-17/*T1w_trimtestants.nii.gz ./${foldertesttwo}/941_S_6581/2022-10-17

# #  ASHS mri files (ASHSICV, ASHST1, ASHST1_MTLCORTEX_MTTHK)
# cp -r ./018_S_2155/2022-11-21/ASHS* ./${testfolder}/018_S_2155/2022-11-21
# cp -r ./024_S_2239/2019-06-03/ASHS* ./${testfolder}/024_S_2239/2019-06-03
# cp -r ./033_S_0734/2018-10-10/ASHS* ./${testfolder}/033_S_0734/2018-10-10
# cp -r ./068_S_0127/2020-03-12/ASHS* ./${testfolder}/068_S_0127/2020-03-12
# cp -r ./114_S_6917/2021-04-16/ASHS* ./${testfolder}/114_S_6917/2021-04-16
# cp -r ./941_S_6581/2022-10-17/ASHS* ./${testfolder}/941_S_6581/2022-10-17
# cp -r ./100_S_0069/2020-01-23/ASHS* ./${testfolder}/100_S_0069/2020-01-23

# # ASHS T2 folders
# cp -r ./018_S_2155/2022-11-21/sfsegnibtend* ./${testfolder}/018_S_2155/2022-11-21
# cp -r ./024_S_2239/2019-06-03/sfsegnibtend* ./${testfolder}/024_S_2239/2019-06-03
# cp -r ./033_S_0734/2018-10-10/sfsegnibtend* ./${testfolder}/033_S_0734/2018-10-10
# cp -r ./068_S_0127/2020-03-12/sfsegnibtend* ./${testfolder}/068_S_0127/2020-03-12
# cp -r ./114_S_6917/2021-04-16/sfsegnibtend* ./${testfolder}/114_S_6917/2021-04-16
# cp -r ./941_S_6581/2022-10-17/sfsegnibtend* ./${testfolder}/941_S_6581/2022-10-17
# cp -r ./100_S_0069/2020-01-23/sfsegnibtend* ./${testfolder}/100_S_0069/2020-01-23

# # superres
# cp -r ./018_S_2155/2022-11-21/super* ./018_S_2155/2022-11-21/*denoised* ./${testfolder}/018_S_2155/2022-11-21
# cp -r ./024_S_2239/2019-06-03/super* ./024_S_2239/2019-06-03/*denoised* ./${testfolder}/024_S_2239/2019-06-03
# cp -r ./033_S_0734/2018-10-10/super* ./033_S_0734/2018-10-10/*denoised* ./${testfolder}/033_S_0734/2018-10-10
# cp -r ./068_S_0127/2020-03-12/super* ./068_S_0127/2020-03-12/*denoised* ./${testfolder}/068_S_0127/2020-03-12
# cp -r ./114_S_6917/2021-04-16/super* ./114_S_6917/2021-04-16/*denoised* ./${testfolder}/114_S_6917/2021-04-16
# cp -r ./941_S_6581/2022-10-17/super* ./941_S_6581/2022-10-17/*denoised* ./${testfolder}/941_S_6581/2022-10-17
# cp -r ./100_S_0069/2020-01-23/super* ./100_S_0069/2020-01-23/*denoised* ./${testfolder}/100_S_0069/2020-01-23

# ## check these locs too:
# # rm analysis_input/cleanup 
# cp -r /project/wolk/ADNI2018/analysis_input/cleanup/* ./${testfolder}/cleanup










# # remove petreg files 
# # rm ./018_S_2155/2019-09-16/2019-09-16_018_S_2155_amypet_to*
# # rm ./018_S_2155/2021-11-30/2021-11-30_018_S_2155_taupet_to*
# # rm ./024_S_2239/2019-06-19/2019-06-19_024_S_2239_taupet_*
# # rm ./024_S_2239/2019-05-23/2019-05-23_024_S_2239_amypet_*
# # rm ./033_S_0734/2018-10-10/2018-10-10_033_S_0734_taupet_to*
# # rm ./033_S_0734/2017-10-16/2017-10-16_033_S_0734_amypet_*
# # rm ./068_S_0127/2020-06-17/2020-06-17_068_S_0127_taupet_to*
# # rm ./068_S_0127/2020-06-11/2020-06-11_068_S_0127_amypet_*
# # rm ./100_S_0069/2020-01-23/2020-01-23_100_S_0069_amypet_to*
# # rm ./100_S_0069/2020-02-05/2020-02-05_100_S_0069_taupet_to*
# # rm ./114_S_6917/2021-08-11/2021-08-11_114_S_6917_taupet_to*
# # rm ./114_S_6917/2021-06-02/2021-06-02_114_S_6917_amypet_to*


# # remove ASHS mri files (ASHSICV, ASHST1, ASHST1_MTLCORTEX_MTTHK)
# rm -r ./018_S_2155/2022-11-21/ASHS*
# rm -r ./024_S_2239/2019-06-03/ASHS*
# rm -r ./033_S_0734/2018-10-10/ASHS*
# rm -r ./068_S_0127/2020-03-12/ASHS*
# rm -r ./114_S_6917/2021-04-16/ASHS*
# rm -r ./941_S_6581/2022-10-17/ASHS*
# rm -r ./100_S_0069/2020-01-23/ASHS*

# #remove just ASHS T1 and MTTHK
# # rm -r ./018_S_2155/2022-11-21/ASHST1*
# # rm -r ./024_S_2239/2019-06-03/ASHST1*
# # rm -r ./033_S_0734/2018-10-10/ASHST1*
# # rm -r ./068_S_0127/2020-03-12/ASHST1*
# # rm -r ./114_S_6917/2021-04-16/ASHST1*
# # rm -r ./941_S_6581/2022-10-17/ASHST1*
# # rm -r ./100_S_0069/2020-01-23/ASHST1*

# #remove ASHS T2 folders
# rm -r ./018_S_2155/2022-11-21/sfsegnibtend*
# rm -r ./024_S_2239/2019-06-03/sfsegnibtend*
# rm -r ./033_S_0734/2018-10-10/sfsegnibtend*
# rm -r ./068_S_0127/2020-03-12/sfsegnibtend*
# rm -r ./114_S_6917/2021-04-16/sfsegnibtend*
# rm -r ./941_S_6581/2022-10-17/sfsegnibtend*
# rm -r ./100_S_0069/2020-01-23/sfsegnibtend*

# #remove superres
# rm -r ./018_S_2155/2022-11-21/super* ./018_S_2155/2022-11-21/*denoised* 
# rm -r ./024_S_2239/2019-06-03/super* ./024_S_2239/2019-06-03/*denoised*
# rm -r ./033_S_0734/2018-10-10/super* ./033_S_0734/2018-10-10/*denoised*
# rm -r ./068_S_0127/2020-03-12/super* ./068_S_0127/2020-03-12/*denoised*
# rm -r ./114_S_6917/2021-04-16/super* ./114_S_6917/2021-04-16/*denoised*
# rm -r ./941_S_6581/2022-10-17/super* ./941_S_6581/2022-10-17/*denoised*
# rm -r ./100_S_0069/2020-01-23/super* ./100_S_0069/2020-01-23/*denoised*

# ## check these locs too:
# # rm analysis_input/cleanup 
# rm -r /project/wolk/ADNI2018/analysis_input/cleanup/*

# # rm analysis_output/stats 
# # rm /project/wolk/ADNI2018/analysis_output/stats/stats_mri*

