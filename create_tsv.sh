#!/usr/bin/bash

function create_tsv_header()
{
  # echo "header function"
  HEADER="RID\tID\tICV\tSlice_Thickness"
  # echo "first bit"
  list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
  for side in left right; do
    for sf in $list; do
      HEADER="${HEADER}\t${side}_${sf}_vol\t${side}_${sf}_ns\t${side}_${sf}_tau\t${side}_${sf}_amy"
    done
  done
  # echo "second bit done"

  HEADER="$HEADER\tHIPPboth_tau\tHIPPboth_amy\tEXTHIPPno36both_tau\tEXTHIPPno36both_amy\t\
  MTLno36both_tau\tMTLno36both_amy\tcereb_tau\tcereb_amy\tocc_tau\tocc_amy\tpostcing_tau\tpostcing_amy\t\
  inftemp_tau_R\tinftemp_amy_R\tinftemp_tau_L\tinftemp_amy_L\tmidtemp_tau_R\tmidtemp_amy_R\tmidtemp_tau_L\t\
  midtemp_amy_L\tsuptemp_tau_R\tsuptemp_amy_R\tsuptemp_tau_L\tsuptemp_amy_L\tsuppariet_tau_R\t\
  suppariet_amy_R\tsuppariet_tau_L\tsuppariet_amy_L\tcalc_tau_R\tcalc_amy_R\tcalc_tau_L\tcalc_amy_L\t\
  angular_tau_R\tangular_amy_R\tangular_tau_L\tangular_amy_L\tsupfront_tau_R\tsupfront_amy_R\t\
  supfront_tau_L\tsupfront_amy_L"
  
  # echo "third bit done"

  for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
  | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' \
  | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
    HEADER="$HEADER\t${roi}_tau\t${roi}_amy\t${roi}_thickness"
  done
  # echo "last bit done"

  # echo -e "${HEADER}\t$(cat $PETFILE | sed -n "1p")" > $analysis_output_dir/stats_lr_cleanup_corr_nogray_$date.tsv
    #cat PETFILE print out the header from petfile as the last part of the created header string
}

function collate_new_data ()
{
  for file in $(ls $cleanup_file_dir/*whole.txt | cut -f 3 -d "/"); do
    cat $cleanup_file_dir/$file | tee -a $analysis_output_dir/stats_lr_cleanup_corr_nogray_$date.tsv
    #tee splits output so it's saved to file (-a is append) and also goes to stdout--unecessary?
  done
}

wblabels=$1
cleanup_file_dir=$2
analysis_output_dir=$3
date=$(echo $analysis_output_dir | cut -f 6 -d "/")

echo "Writing tsv header"
# create_tsv_header
# collate_new_data