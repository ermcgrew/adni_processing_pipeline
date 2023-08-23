#!/usr/bin/bash
# sleep 2
# while [[ $(bjobs | grep "emcgrew RUN" | wc -l) -gt 1 ]] ; do 
#     echo "sleeping 8"
#     sleep 8
# done


# echo "all processing and stats creation jobs finished"


# statusvar=$(bsub sleep 10)
# echo "This is the return: $statusvar"


##Matching from end of string
# jobone="testjob_243_T_3251"
# jobtwo="asecond_243_T_3251"
# jobthree="again_243_T_3251"

# finaljob="final_243_T_3251"

# bsub -J $jobone sleep 20
# bsub -J $jobtwo -w 'done(testjob_243_T_3251)' sleep 17
# bsub -J $jobthree -w 'done(asecond_243_T_3251)' sleep 22

# bsub -J $finaljob -w "done(*243_T_3251)" echo this runs when all jobs are done


# [emcgrew@bscsub1 adni_processing_pipeline]$ bjdepinfo -lp 21129875
# The dependency condition of job <21129875> is not satisfied: done(*243_T_3251)
# JOBID          PARENT         PARENT_STATUS  PARENT_NAME  LEVEL
# 21129875       21129874       PEND           *43_T_3251   1

# [emcgrew@bscsub1 adni_processing_pipeline]$ bjdepinfo -c -r 4 21129872
# JOBID          CHILD          CHILD_STATUS  CHILD_NAME  LEVEL
# 21129872       21129873       PEND          *43_T_3251  1
# 21129873       21129874       PEND          *43_T_3251  2
# 21129874       21129875       PEND          *43_T_3251  3





##matching from beginning of string
# jobone="243_T_3251_testingjob"
# jobtwo="243_T_3251_asecond"
# jobthree="243_T_3251_again"

# finaljob="243_T_3251_final"

# bsub -J $jobone sleep 20
# bsub -J $jobtwo -w 'done(243_T_3251_testingjob)' sleep 17
# bsub -J $jobthree -w 'done(243_T_3251_asecond)' sleep 22

# bsub -J $finaljob -w "done(243_T_3251*)" echo this runs when all jobs are done
#bjdepinfo -lp <finaljob>
## [emcgrew@bscsub1 adni_processing_pipeline]$ bjdepinfo -lp 21129868
# The dependency condition of job <21129868> is not satisfied: done(243_T_3251*)
# JOBID          PARENT         PARENT_STATUS  PARENT_NAME  LEVEL
# 21129868       21129865       RUN            *estingjob   1
# 21129868       21129866       PEND           *1_asecond   1
# 21129868       21129867       PEND           *251_again   1


#bjdepinfo -c -r 4 <firstjob>
# [emcgrew@bscsub1 adni_processing_pipeline]$ bjdepinfo -c -r 4 21129865
# JOBID          CHILD          CHILD_STATUS  CHILD_NAME  LEVEL
# 21129865       21129866       RUN           *1_asecond  1
# 21129865       21129868       PEND          *251_final  1
# 21129866       21129867       PEND          *251_again  2
# 21129866       21129868       PEND          *251_final  2
# 21129867       21129868       PEND          *251_final  3

