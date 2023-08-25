#!/usr/bin/bash
cd /project/wolk/ADNI2018/scripts/pipeline_test_data/

# remove petreg files 
# rm ./018_S_2155/2019-09-16/2019-09-16_018_S_2155_amypet_to*
# rm ./018_S_2155/2021-11-30/2021-11-30_018_S_2155_taupet_to*
# rm ./024_S_2239/2019-06-19/2019-06-19_024_S_2239_taupet_*
# rm ./024_S_2239/2019-05-23/2019-05-23_024_S_2239_amypet_*
# rm ./033_S_0734/2018-10-10/2018-10-10_033_S_0734_taupet_to*
# rm ./033_S_0734/2017-10-16/2017-10-16_033_S_0734_amypet_*
# rm ./068_S_0127/2020-06-17/2020-06-17_068_S_0127_taupet_to*
# rm ./068_S_0127/2020-06-11/2020-06-11_068_S_0127_amypet_*
# rm ./100_S_0069/2020-01-23/2020-01-23_100_S_0069_amypet_to*
# rm ./100_S_0069/2020-02-05/2020-02-05_100_S_0069_taupet_to*
# rm ./114_S_6917/2021-08-11/2021-08-11_114_S_6917_taupet_to*
# rm ./114_S_6917/2021-06-02/2021-06-02_114_S_6917_amypet_to*


# remove ASHS mri files (ASHSICV, ASHST1, ASHST1_MTLCORTEX_MTTHK)
# rm -r ./018_S_2155/2022-11-21/ASHS*
# rm -r ./024_S_2239/2019-06-03/ASHS*
# rm -r ./033_S_0734/2018-10-10/ASHS*
# rm -r ./068_S_0127/2020-03-12/ASHS*
# rm -r ./114_S_6917/2021-04-16/ASHS*
# rm -r ./941_S_6581/2022-10-17/ASHS*
# rm -r ./100_S_0069/2020-01-23/ASHS*

#remove just ASHS T1 and MTTHK
rm -r ./018_S_2155/2022-11-21/ASHST1*
rm -r ./024_S_2239/2019-06-03/ASHST1*
rm -r ./033_S_0734/2018-10-10/ASHST1*
rm -r ./068_S_0127/2020-03-12/ASHST1*
rm -r ./114_S_6917/2021-04-16/ASHST1*
rm -r ./941_S_6581/2022-10-17/ASHST1*
rm -r ./100_S_0069/2020-01-23/ASHST1*

#remove ASHS T2 folders
# rm -r ./018_S_2155/2022-11-21/sfsegnibtend*
# rm -r ./024_S_2239/2019-06-03/sfsegnibtend*
# rm -r ./033_S_0734/2018-10-10/sfsegnibtend*
# rm -r ./068_S_0127/2020-03-12/sfsegnibtend*
# rm -r ./114_S_6917/2021-04-16/sfsegnibtend*
# rm -r ./941_S_6581/2022-10-17/sfsegnibtend*
# rm -r ./100_S_0069/2020-01-23/sfsegnibtend*

#remove superres
# rm -r ./018_S_2155/2022-11-21/super* ./018_S_2155/2022-11-21/*denoised* 
# rm -r ./024_S_2239/2019-06-03/super* ./024_S_2239/2019-06-03/*denoised*
# rm -r ./033_S_0734/2018-10-10/super* ./033_S_0734/2018-10-10/*denoised*
# rm -r ./068_S_0127/2020-03-12/super* ./068_S_0127/2020-03-12/*denoised*
# rm -r ./114_S_6917/2021-04-16/super* ./114_S_6917/2021-04-16/*denoised*
# rm -r ./941_S_6581/2022-10-17/super* ./941_S_6581/2022-10-17/*denoised*
# rm -r ./100_S_0069/2020-01-23/super* ./100_S_0069/2020-01-23/*denoised*

## check these locs too:
# rm analysis_input/cleanup 
# rm analysis_output/stats 
rm /project/wolk/ADNI2018/analysis_output/stats/stats_mri*