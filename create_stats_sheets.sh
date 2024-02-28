#!/usr/bin/bash

wblabels=$1
output_dir=$2
mode=$3


function write_header()
{
  mode=$1
  statfile=$2
  
  HEADER="RID,ID,MRIDATE,"

  if [[ $mode == "pet" ]] ; then 
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
        HEADER="${HEADER}\t${roi}_wbtoants_tau_${side}\t${roi}_wbtoants_tau_pvc_${side}\t${roi}_wbtoants_amy_${side}"
      done 
    done

    for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
    | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' \
    | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
      HEADER="$HEADER\t${roi}_wbtoants_tau\t${roi}_wbtoants_taupvc\t${roi}_wbtoants_amy"
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

  elif [[ $mode == "ashst2" ]] ; then 
    list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
    for side in left right; do
      for sf in $list; do
        HEADER="${HEADER}\t${side}_${sf}_vol\t${side}_${sf}_ns"
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
  statfile=$1
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


date=$(echo date + '%Y%m%d')

if [[ $mode == "pet" ]] ; then 
  statfile="${output_dir}/data/tau_amy_ROIvols_compSUVR_${date}.csv"
elif [[ $mode == "structure" ]] ; then 
  statfile="${output_dir}/data/thickness_${date}.csv"
elif [[ $mode == "ashst1" ]] ; then 
  statfile="${output_dir}/data/T1_ASHSvols_MTTHK_PMTAU_${date}.csv"
elif [[ $mode == "ashst2" ]] ; then 
  statfile="${output_dir}/data/T2_ASHSvols_PMTAU_${date}.csv"
elif [[ $mode == "wmh" ]] ; then 
  statfile="${output_dir}/data/WMH_${date}.csv"
fi

write_header $mode $statfile
collate_new_data $mode $statfile
