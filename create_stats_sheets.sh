#!/usr/bin/bash

function write_header()
{
  HEADER="RID\tID\tMRIDATE\tAMYDATE\tTAUDATE\tICV\tSlice_Thickness"
  list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
  for side in left right; do
    for sf in $list; do
      HEADER="${HEADER}\t${side}_${sf}_vol\t${side}_${sf}_ns\t${side}_${sf}_tau\t${side}_${sf}_amy"
    done
  done

  HEADER="$HEADER\tHIPPboth_tau\tHIPPboth_amy\tEXTHIPPno36both_tau\tEXTHIPPno36both_amy\t\
  MTLno36both_tau\tMTLno36both_amy\tcereb_tau\tcereb_amy\tocc_tau\tocc_amy\tpostcing_tau\tpostcing_amy\t\
  inftemp_tau_R\tinftemp_amy_R\tinftemp_tau_L\tinftemp_amy_L\tmidtemp_tau_R\tmidtemp_amy_R\tmidtemp_tau_L\t\
  midtemp_amy_L\tsuptemp_tau_R\tsuptemp_amy_R\tsuptemp_tau_L\tsuptemp_amy_L\tsuppariet_tau_R\t\
  suppariet_amy_R\tsuppariet_tau_L\tsuppariet_amy_L\tcalc_tau_R\tcalc_amy_R\tcalc_tau_L\tcalc_amy_L\t\
  angular_tau_R\tangular_amy_R\tangular_tau_L\tangular_amy_L\tsupfront_tau_R\tsupfront_amy_R\t\
  supfront_tau_L\tsupfront_amy_L"
  
  for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
  | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' \
  | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
    HEADER="$HEADER\t${roi}_tau\t${roi}_amy\t${roi}_thickness"
  done

  #PMTAU
  for i in Anterior Posterior; do
  HEADER="$HEADER\t${i}_pmtauthick\t${i}_pmtauweightedthick\t${i}_pmtaujac\t${i}_pmtauweightedjac"
  
  echo -e "${HEADER}" > $this_run_analysis_output_dir/$tsvfilename
  echo -e "${HEADER}" > $this_run_analysis_output_dir/$structonly


  ##########################################
  #for ashst1 & mtthk header
  ashsheader="RID,ID,MRIDATE,ICV_ASHSICV"

  # ASHS T1 baseline volume and thickness
  for type in VOL; do
  for side in L R M; do
  for sub in AHippo PHippo ERC BA35 BA36 PHC; do
    ashsheader="$ashsheader,${side}_${sub}_${type}_ASHST1_3T"
  done
  done
  done

  # thickness
  for side in L R M; do
  for type in MeanTHK MedianTHK; do
  for sub in Hippo ERC BA35 BA36 PHC; do
    ashsheader="$ashsheader,${side}_${sub}_${type}_MSTTHKMT_ASHST1_3T"
  done
  done
  done

  # thickness quality of fit
  for side in L R; do
  for sub in Hippo ERC BA35 BA36 PHC ALL; do
    ashsheader="$ashsheader,${side}_${sub}_${type}_MSTFitQuality_ASHST1_3T"
  done
  done

  echo -e "${ashsheader}" > $this_run_analysis_output_dir/$ashst1csv

}

function collate_new_data ()
{
  for file in $(find ${stats_output_dir}/*whole.txt); do
    cat $file >> $this_run_analysis_output_dir/$tsvfilename
  done
  for file in $(find ${stats_output_dir}/*structonly.txt); do
    cat $file >> $this_run_analysis_output_dir/$structonly
  done
  for file in $(find ${stats_output_dir}/*ashst1.txt); do
    cat $file >> $this_run_analysis_output_dir/$ashst1csv
  done

}

wblabels=$1
stats_output_dir=$2
this_run_analysis_output_dir=$3

date=$(echo $this_run_analysis_output_dir | cut -f 6 -d "/")
tsvfilename="pet_ashst2_stats_corr_nogray_${date}.tsv"
ashst1csv="ASHS_T1MTTHK_${date}.csv"
structonly="structonly_ashst2_stats_corr_nogray_${date}.tsv"

# echo "Writing tsv header"
write_header
collate_new_data
