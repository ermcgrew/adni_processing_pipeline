#!/usr/bin/bash

jobone="mri_243_T_3252_testingjob"
jobtwo="mri_243_T_3252_asecond"
jobthree="mri_243_T_3252_again"
finaljob="pet_243_T_3252_final"
bsub -J $jobone sleep 16
bsub -J "another test job to monitor" sleep 77
bsub -J $jobtwo -w 'done(mri_243_T_3252_testingjob)' sleep 19
bsub -J $jobthree -w 'done(mri_243_T_3252_asecond)' sleep 18
bsub -J $finaljob -w "done(mri_*)" echo this runs when all jobs are done
bsub -J "test_two_wait_codes" -w "done(mri*) && done (pet*)" echo this job runs when two wait code conditions fulfilled
