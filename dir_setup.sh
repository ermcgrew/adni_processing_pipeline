#!/usr/bin/bash

newdate=$1

analysis_input_dir="/project/wolk/ADNI2018/analysis_input"
this_date_input_dir=$analysis_input_dir/${newdate}_processing

mkdir -p $this_date_input_dir/${newdate}_collections_csvs \
        $this_date_input_dir/${newdate}_adni_datasheets_csvs \
        $this_date_input_dir/${newdate}_uids
