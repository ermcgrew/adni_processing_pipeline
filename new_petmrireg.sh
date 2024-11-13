#!/usr/bin/bash

##### Change these vars
logfile="/project/wolk/ADNI2018/analysis_output/logs/2024_10_21T09_55_44.log"
thisbatch_date="20241104"
#####


thisbatch_uid_dir="/project/wolk/ADNI2018/analysis_input/${thisbatch_date}_processing/${thisbatch_date}_uids"
todaydate=$( date +"%Y%m%d")

cat $logfile | grep Running | grep Tau | cut -f 2-4 -d : | sed 's/:/,/g' >> ${thisbatch_uid_dir}/new_taumrireg_fromrunlog_${todaydate}.csv

cat $logfile | grep Running | grep Amyloid | cut -f 2-4 -d : | sed 's/:/,/g' >> ${thisbatch_uid_dir}/new_amymrireg_fromrunlog_${todaydate}.csv