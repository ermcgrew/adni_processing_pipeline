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

    for pettype in tau amy ; do 
      for suvr_or_pvc in suvr pvc ; do 
        for side in left right ; do 
          list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
          for sf in $list; do
            HEADER="${HEADER},${side}_${sf}_${pettype}_${suvr_or_pvc}_ASHS3TT2"
          done

          if [[ $pettype == "tau" ]] ; then 
            # WB BRAAK 
            for region in BRAAK3 BRAAK4 BRAAK5 BRAAK6 ; do
              HEADER="${HEADER},${side}_${region}_tau_${suvr_or_pvc}_wbtoants"
            done
            # ASHST1
            for sub in AHippo PHippo ERC BA35 BA36 PHC ERCBA35  WholeHippo MTLCortex All; do
              HEADER="$HEADER,${side}_${sub}_tau_${suvr_or_pvc}_ASHS3TT1"
            done
          fi

          if [ ${side}  == 'right' ] ; then 
            ##Combined hippocampal ROIs and CEREB tau and amy values
            HEADER="$HEADER,HIPPboth_${pettype}_${suvr_or_pvc}_ASHS3TT2,EXTHIPPno36both_${pettype}_${suvr_or_pvc}_ASHS3TT2,MTLno36both_${pettype}_${suvr_or_pvc}_ASHS3TT2,cereb_${pettype}_${suvr_or_pvc}"

            #Whole brain ROIS
            HEADER="$HEADER,occ_${pettype}_${suvr_or_pvc}_wbtoants,postcing_${pettype}_${suvr_or_pvc}_wbtoants"
            wbrois=$(echo inftemp midtemp suptemp suppariet calc angular supfront)
            for roi in $wbrois ; do 
              for side_wb in right left ; do
                HEADER="${HEADER},${side_wb}_${roi}_${pettype}_${suvr_or_pvc}_wbtoants"
              done
            done

            for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
            | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF|Thalamus|Forebrain' \
            | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
              HEADER="$HEADER,${roi}_${pettype}_${suvr_or_pvc}_wbtoants"
            done

            if [[ ${pettype} == 'amy' && ${suvr_or_pvc} == 'suvr' ]] ; then 
              #compSUVR
              HEADER="${HEADER},compSUVR" 
            fi
          fi
        done
      done
    done


  elif [[ $mode == "petold" ]] ; then  
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
    HEADER="$HEADER,occ_tau,occ_amy,postcing_tau,postcing_amy"
    wbrois=$(echo inftemp midtemp suptemp suppariet calc angular supfront)
    for roi in $wbrois ; do 
      for side in R L ; do
        HEADER="${HEADER},${roi}_wb_tau_${side},${roi}_wb_amy_${side}"
      done 
    done

    for roi in $(cat $wblabels | grep -v '#' | sed -n '9,$p' \
    | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' \
    | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
      HEADER="$HEADER,${roi}_wb_tau,${roi}_wb_amy"
    done

    #compSUVR
    HEADER="${HEADER},compSUVR"

    #BRAAK stages
    for side in L R; do
      for region in BRAAK3 BRAAK4 BRAAK5 BRAAK6 ; do
        HEADER="${HEADER},${side}_${region}_tau_wb"
      done
    done

    # ASHST1-tau
    for side in L R; do
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
  elif [[ $mode == "petold" ]] ; then 
    for file in $(find ${output_dir}/stats/*pet_oldversion.txt); do
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
elif [[ $mode == "petold" ]] ; then 
  statfile="${output_dir}/data/8mm_tau_amy_ROIvols_compSUVR_${date}.csv"
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
