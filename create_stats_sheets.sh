#!/usr/bin/bash

function write_header()
{
  mode=$1
  statfile=$2
  
  HEADER="RID,ID,MRIDATE,"

  if [[ $mode == "pet_stats" ]] ; then 
    HEADER="${HEADER}\tAMYDATE\tTAUDATE\tICV\tSlice_Thickness"

    ##ASHST2 hippocampal ROIs
    list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
    for side in left right; do
      for sf in $list; do
        HEADER="${HEADER}\t${side}_${sf}_tau\t${side}_${sf}_amy"
      done
    done

    ##Combined hippocampal ROIs and CEREB tau and amy values
    HEADER="$HEADER\tHIPPboth_tau\tHIPPboth_amy\tEXTHIPPno36both_tau\tEXTHIPPno36both_amy\t\
    MTLno36both_tau\tMTLno36both_amy\tcereb_tau\tcereb_amy"

    #Whole brain ROIS: tau, taupvc, amy
    HEADER="$HEADER\tocc_tau\tocc_tau_pvc\tocc_amy\tpostcing_tau\tpostcing_tau_pvc\tpostcing_amy"
    wbrois=$(echo inftemp midtemp suptemp suppariet calc angular supfront)
    for roi in wbrois ; do 
      for side in R L ; do
        HEADER="${HEADER}\t${roi}_tau_${side}\t${roi}_tau_pvc_${side}\t${roi}_amy_${side}"
      done 
    done

    for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
    | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' \
    | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
      HEADER="$HEADER\t${roi}_tau\t${roi}_taupvc\t${roi}_amy"
    done

    #compSUVR
    HEADER="${HEADER}\tcompSUVR"

    #BRAAK stages
    for wbtype in WB_ants WB ; do 
      for tautype in tau tau_suvr ; do 
        for side in L R; do
          for region in BRAAK3 BRAAK4 BRAAK5 BRAAK6 ; do
          HEADER="${HEADER}\t${side}_${region}_${tautype}_${wbtype}"
    done
    done
    done
    done 

  elif [[ $mode == "structure" ]] ; then 
    for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
      | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' \
      | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
      HEADER="$HEADER\t${roi}_thickness"
    done

  elif [[ $mode == "ashst1" ]] ; then 
    HEADER="ICV_ASHSICV"

    # ASHS T1 baseline volume and thickness
    for type in VOL; do
    for side in L R M; do
    for sub in AHippo PHippo ERC BA35 BA36 PHC; do
      HEADER="$HEADER,${side}_${sub}_${type}_ASHST1_3T"
    done
    done
    done

    # thickness
    for side in L R M; do
    for type in MeanTHK MedianTHK; do
    for sub in Hippo ERC BA35 BA36 PHC; do
      HEADER="$HEADER,${side}_${sub}_${type}_MSTTHKMT_ASHST1_3T"
    done
    done
    done

    # thickness quality of fit
    for side in L R; do
    for sub in Hippo ERC BA35 BA36 PHC ALL; do
      HEADER="$HEADER,${side}_${sub}_${type}_MSTFitQuality_ASHST1_3T"
    done
    done
  
    #PMTAU
    for i in Anterior Posterior; do
    HEADER="$HEADER\t${i}_pmtauthick\t${i}_pmtauweightedthick\t${i}_pmtaujac\t${i}_pmtauweightedjac"
    done

  elif [[ $mode == "ASHST2" ]] ; then 
    list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
    for side in left right; do
      for sf in $list; do
        HEADER="${HEADER}\t${side}_${sf}_vol\t${side}_${sf}_ns\t${side}_${sf}_tau\t${side}_${sf}_amy"
      done
    done
    #PMTAU
    for i in Anterior Posterior; do
    HEADER="$HEADER\t${i}_pmtauthick\t${i}_pmtauweightedthick\t${i}_pmtaujac\t${i}_pmtauweightedjac"
    done

  elif [[ $mode == "wmh" ]] ; then 
    HEADER="$HEADER\tWMH_vol"
  fi 

  echo -e "${HEADER}" > $statfile

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
##mode as argument? 

date=$(echo $this_run_analysis_output_dir | cut -f 6 -d "/")

#by mode: statfile =
tsvfilename="pet_ashst2_stats_corr_nogray_${date}.tsv"
ashst1csv="ASHS_T1MTTHK_${date}.csv"
structonly="structonly_ashst2_stats_corr_nogray_${date}.tsv"

# echo "Writing tsv header"
write_header($mode, $statfile)
collate_new_data
