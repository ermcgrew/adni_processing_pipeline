#!/usr/bin/bash

wblabels=$1
output_dir=$2
mode=$3


function write_header()
{
  mode=$1
  statfile=$2
  
  HEADER="RID,ID,MRIDATE"

  if [[ $mode == "pet" ]] ; then 
    HEADER="${HEADER},AMYDATE,TAUDATE,ICV,Slice_Thickness"

    ##ASHST2 hippocampal ROIs
    list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
    for side in left right; do
      for sf in $list; do
        HEADER="${HEADER},${side}_${sf}_tau,${side}_${sf}_amy"
      done
    done

    ##Combined hippocampal ROIs and CEREB tau and amy values
    HEADER="$HEADER,HIPPboth_tau,HIPPboth_amy,EXTHIPPno36both_tau,EXTHIPPno36both_amy,MTLno36both_tau,MTLno36both_amy,cereb_tau,cereb_amy"

    #Whole brain ROIS: tau, taupvc, amy
    HEADER="$HEADER,occ_tau,occ_tau_pvc,occ_amy,postcing_tau,postcing_tau_pvc,postcing_amy"
    wbrois=$(echo inftemp midtemp suptemp suppariet calc angular supfront)
    for roi in $wbrois ; do 
      for side in R L ; do
        HEADER="${HEADER},${roi}_wbtoants_tau_${side},${roi}_wbtoants_tau_pvc_${side},${roi}_wbtoants_amy_${side}"
      done 
    done

    for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
    | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF|Thalamus|Forebrain' \
    | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
      HEADER="$HEADER,${roi}_wbtoants_tau,${roi}_wbtoants_taupvc,${roi}_wbtoants_amy"
    done

    #compSUVR
    HEADER="${HEADER},compSUVR"

    #BRAAK stages
    for tautype in tau tau_suvr ; do 
      for side in L R; do
        for region in BRAAK3 BRAAK4 BRAAK5 BRAAK6 ; do
        HEADER="${HEADER},${side}_${region}_${tautype}_WBants"
    done
    done
    done

  # ASHST1-tau
  for side in L R M; do
  for sub in AHippo PHippo ERC BA35 BA36 PHC ERCBA35  WholeHippo MTLCortex All; do
    HEADER="$HEADER,${side}_${sub}_tau_ASHST1_3T"
  done
  done

  elif [[ $mode == "structure" ]] ; then 
    for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
      | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF|Thalamus|Forebrain' \
      | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
      HEADER="$HEADER,${roi}_thickness"
    done
    
    #PMTAU
    for i in Anterior Posterior; do
    HEADER="$HEADER,${i}_pmtauthick,${i}_pmtauweightedthick,${i}_pmtaujac,${i}_pmtauweightedjac"
    done

  elif [[ $mode == "ashst1" ]] ; then 
    HEADER="$HEADER,ICV_ASHSICV"

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

  elif [[ $mode == "ashst2" ]] ; then 
    HEADER="${HEADER},Slice_Thickness"
    list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
    for side in left right; do
      for sf in $list; do
        HEADER="${HEADER},${side}_${sf}_vol,${side}_${sf}_ns"
      done
    done


  elif [[ $mode == "wmh" ]] ; then 
    HEADER="$HEADER,FLAIR_sequence_resolution,WMH_vol"
  fi 

  echo -e "${HEADER}" > $statfile

}


function collate_new_data ()
{
  mode=$1
  statfile=$2
  if [[ $mode == "pet" ]] ; then
    for file in $(find ${output_dir}/stats/*pet.txt); do
      cat $file >> $statfile
    done
  elif [[ $mode == "structure" ]] ; then 
    for file in $(find ${output_dir}/stats/*structure.txt); do
      cat $file >> $statfile
    done
  elif [[ $mode == "ashst1" ]] ; then 
    for file in $(find ${output_dir}/stats/*ashst1.txt); do
      cat $file >> $statfile
    done
  elif [[ $mode == "ashst2" ]] ; then 
    for file in $(find ${output_dir}/stats/*ashst2.txt); do
      cat $file >> $statfile
    done  
  elif [[ $mode == "wmh" ]] ; then 
    for file in $(find ${output_dir}/stats/*wmh.txt); do
      cat $file >> $statfile
    done  
  fi
}


date=$( date '+%Y%m%d')

if [[ $mode == "pet" ]] ; then 
  statfile="${output_dir}/data/tau_amy_ROIvols_compSUVR_${date}.csv"
elif [[ $mode == "structure" ]] ; then 
  statfile="${output_dir}/data/thickness_PMTAU_${date}.csv"
elif [[ $mode == "ashst1" ]] ; then 
  statfile="${output_dir}/data/T1_ASHSvols_MTTHK_${date}.csv"
elif [[ $mode == "ashst2" ]] ; then 
  statfile="${output_dir}/data/T2_ASHSvols_${date}.csv"
elif [[ $mode == "wmh" ]] ; then 
  statfile="${output_dir}/data/WMH_${date}.csv"
fi

write_header $mode $statfile
collate_new_data $mode $statfile
