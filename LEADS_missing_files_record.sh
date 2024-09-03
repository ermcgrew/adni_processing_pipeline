#!/usr/bin/bash

dataset="/project/wolk/Prisma3T/relong/LEADS/data"
date=$( date "+%Y%m%d_%T" )

mode="mrionly"
# mode="pet"

if [[ $mode == "mrionly" ]] ; then 

    mricsv="/project/wolk/Prisma3T/relong/LEADS/LEADS_MRI_sessions_20240814.csv"
    record="/project/wolk/Prisma3T/relong/LEADS/analysis_output/file_exist_record_${date}.csv"

    header="ID,MRIDATE,T1_exist,trim_exist,thick_exist,brainx_exist,wbseg_exist,infcereb_exist,wbsegtoants_exist,superres_exist,t1ashs_exist,icvashs_exist,t2_exist,t2ashs_exist,t2ashstse_exist,prccleanupL_exist,prccleanupR_exist,prccleanupB_exist,flair_exist,flairnoskull_exist,flairwmh_exist"
    echo $header > $record

    cat $mricsv | while read line ; do
        id=$(echo $line | cut -d , -f 1 )
        mridate=$(echo $line | cut -d , -f 3)

        if [[ $id != "ID" ]] ; then 
            row="${id},${mridate}"
            sessiondir="${dataset}/${id}/MRI3T/${mridate}/processed"

            tone="${sessiondir}/${id}_${mridate}_mprage.nii.gz"
            tone_trim="${sessiondir}/${id}_${mridate}_mprage_trim.nii.gz"
            thick="${sessiondir}/thickness/${id}CorticalThickness.nii.gz"
            brainx="${sessiondir}/${id}_${mridate}_T1w_trim_brainx_ExtractedBrain.nii.gz"
            wbseg="${sessiondir}/${id}_${mridate}_wholebrainseg/${id}_${mridate}_T1w_trim_brainx_ExtractedBrain/${id}_${mridate}_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz"
            infcereb="${sessiondir}/${id}_${mridate}_wholebrainseg/${id}_${mridate}_T1w_trim_brainx_ExtractedBrain/inferior_cerebellum.nii.gz"
            wbsegtoANTs="${sessiondir}/${id}_${mridate}_wholebrainseg/${id}_${mridate}_T1w_trim_brainx_ExtractedBrain/${id}_${mridate}_T1w_trim_brainx_ExtractedBrain_wholebrainseg_cortical_propagate.nii.gz"

            superres="${sessiondir}/${id}_${mridate}_mprage_trim_denoised_SR.nii.gz"
            ashst1="${sessiondir}/ASHST1/final/${id}_left_lfseg_heur.nii.gz"
            ashsicv="${sessiondir}/ASHSICV/final/${id}_left_lfseg_corr_nogray.nii.gz"
        
            ttwo="${sessiondir}/${id}_${mridate}_tse.nii.gz"
            ashst2="${sessiondir}/sfsegnibtend/final/${id}_left_lfseg_corr_nogray.nii.gz"
            ashstse="${sessiondir}/sfsegnibtend/tse.nii.gz"
            prc_cleanup_left="/project/wolk/Prisma3T/relong/LEADS/analysis_input/cleanup/${id}_${mridate}_seg_left.nii.gz"
            prc_cleanup_right="/project/wolk/Prisma3T/relong/LEADS/analysis_input/cleanup/${id}_${mridate}_seg_right.nii.gz"
            prc_cleanup_both="/project/wolk/Prisma3T/relong/LEADS/analysis_input/cleanup/${id}_${mridate}_seg_both.nii.gz"

            flair="${sessiondir}/${id}_${mridate}_flair.nii.gz"
            flair_noskull="${sessiondir}/${id}_${mridate}_flair_skullstrip.nii.gz"
            flair_wmh="${sessiondir}/${id}_${mridate}_flair_wmh.nii.gz"

            # echo $t1
            if [[ ! -f $tone ]] ; then 
                # echo "missing T1"
                row=$row,0,0,0,0,0,0,0,0,0,0
            else
                # echo 'found T1'
                row=$row,1
                
                ## Check for Trim
                if [[ ! -f $tone_trim ]] ; then 
                    # echo 'missing trim'
                    row=$row,0,0,0,0,0,0,0
                else 
                    # echo 'found trim'
                    row=$row,1

                    ## Thickness
                    if [[ ! -f $thick ]] ; then 
                        # echo 'missing thick'
                        row=$row,0
                    else 
                        # echo 'found thick'
                        row=$row,1
                    fi

                    ## Whole brain extraction 
                    if [[ ! -f $brainx ]] ; then 
                        # echo 'missing brainx'
                        row=$row,0
                    else 
                        # echo 'found brainx'
                        row=$row,1
                    fi

                    ## Whole brain seg
                    if [[ ! -f $wbseg ]] ; then 
                        # echo 'missing wbseg'
                        row=$row,0
                    else 
                        # echo 'found wbseg'
                        row=$row,1
                    fi

                    ## inf cereb
                    if [[ ! -f $infcereb ]] ; then 
                        # echo 'missing infcereb'
                        row=$row,0
                    else 
                        # echo 'found infcereb'
                        row=$row,1
                    fi

                    ## whole brain to ANTs
                    if [[ ! -f $wbsegtoANTs ]] ; then 
                        # echo 'missing wbsegtoANTs'
                        row=$row,0
                    else 
                        # echo 'found wbsegtoANTs'
                        row=$row,1
                    fi
            
                    ## Super resolution
                    if [[ ! -f $superres ]] ; then 
                        # echo 'missing superres'
                        row=$row,0,0
                    else 
                        # echo 'found superres'
                        row=$row,1
                        
                        ## ASHS T1
                        if [[ ! -f $ashst1 ]] ; then 
                            # echo 'missing ashs t1'
                            row=$row,0
                        else 
                            # echo 'found ashs t1'
                            row=$row,1
                        fi
                    fi

                    ## ASHS ICV
                    if [[ ! -f $ashsicv ]] ; then 
                        # echo 'missing ashs icv'
                        row=$row,0
                    else 
                        # echo 'found ashs icv'
                        row=$row,1
                    fi
                fi
            fi

            if [[ ! -f $ttwo ]] ; then 
            #  echo "missing T2"
                row=$row,0,0,0,0,0,0
            else
                # echo 'found T2'
                row=$row,1

                ## t2 ASHS
                if [[ ! -f $ashst2 ]] ; then 
                    # echo 'missing t2 ashs'
                    row=$row,0
                else 
                    # echo 'found  t2 ashs'
                    row=$row,1
                fi

                ## t2 ASHS tse (for making prc-cleanup)
                if [[ ! -f $ashstse ]] ; then 
                    # echo 'missing t2 ashs tse'
                    row=$row,0
                else 
                    # echo 'found  t2 ashs tse'
                    row=$row,1
                fi

                ## prc-cleanup left
                if [[ ! -f $prc_cleanup_left ]] ; then 
                    # echo 'missing prc_cleanup left'
                    row=$row,0
                else  
                    # echo 'found prc_cleanup left'
                    row=$row,1
                fi

                ## prc-cleanup right
                if [[ ! -f $prc_cleanup_right ]] ; then 
                    # echo 'missing prc_cleanup right'
                    row=$row,0
                else 
                    # echo 'found prc_cleanup right'
                    row=$row,1
                fi

                ## prc-cleanup both
                if [[ ! -f $prc_cleanup_both ]] ; then 
                    # echo 'missing prc_cleanup both'
                    row=$row,0
                else 
                    # echo 'found prc_cleanup both'
                    row=$row,1
                fi
            fi

            if [[ ! -f $flair ]] ; then 
                # echo 'missing flair'
                row=$row,0,0,0
            else  
                # echo 'found flair'
                row=$row,1

                ## skull strip FLAIR
                if [[ ! -f $flair_noskull ]] ; then 
                    # echo 'missing skull strip flair'
                    row=$row,0,0
                else 
                    row=$row,1

                    ## WMH 
                    if [[ ! -f $flair_wmh ]] ; then 
                        # echo 'missing wmh'
                        row=$row,0
                    else 
                        row=$row,1
                    fi
                fi            
            fi

            # tee $row >> $record
            echo $row
            echo $row >> $record
            # sleep 0.1
        fi
    done

elif [[ $mode == 'pet' ]] ; then 

    tauanchcsv="/project/wolk/Prisma3T/relong/LEADS/LEADS_tau_anchored_20240814.csv"
    record="/project/wolk/Prisma3T/relong/LEADS/analysis_output/file_exist_record_pet_${date}.csv"

    header="ID,MRIDATE,TAUDATE,AMYDATE,tau_exist,taut1_exist,taut1suvr_exist,amy_exist,amyt1_exist,amyt1suvr_exist"
    echo $header >> $record 

    cat $tauanchcsv | while read line ; do 
        id=$(echo $line | cut -d , -f 1 )
        taudate=$(echo $line | cut -d , -f 3 )
        mridate=$(echo $line | cut -d , -f 5 )
        amydate=$(echo $line | cut -d , -f 13 )
        if [[ $id == "ID" ]] ; then 
            continue
        else
            row="${id},${mridate},${taudate},${amydate}"

            taudir=${dataset}/${id}/${taudate}
            taunifti=${taudir}/${taudate}_${id}_taupet6mm.nii.gz
            taureg=${taudir}/${taudate}_${id}_taupet6mm_to_${mridate}_T1.nii.gz
            tausuvr=${taudir}/${taudate}_${id}_taupet6mm_to_${mridate}_T1_SUVR.nii.gz
            
            amydir=${dataset}/${id}/${amydate}
            amynifti=${amydir}/${amydate}_${id}_amypet6mm.nii.gz
            amyreg=${amydir}/${amydate}_${id}_amypet6mm_to_${mridate}_T1.nii.gz
            amysuvr=${amydir}/${amydate}_${id}_amypet6mm_to_${mridate}_T1_SUVR.nii.gz

            if [[ ! -f $taunifti ]] ; then 
                row="${row},0,0,0"
            else
                row="${row},1"
                if [[ ! -f $taureg ]] ; then 
                    row="${row},0,0"
                else
                    row="${row},1"
                    if [[ ! -f $tausuvr ]] ; then 
                        row="${row},0"
                    else
                        row="${row},1"
                    fi
                fi
            fi

            if [[ ! -f $amynifti ]] ; then 
                row="${row},0,0,0"
            else
                row="${row},1"
                if [[ ! -f $amyreg ]] ; then 
                    row="${row},0,0"
                else
                    row="${row},1"
                    if [[ ! -f $amysuvr ]] ; then 
                        row="${row},0"
                    else
                        row="${row},1"
                    fi
                fi
            fi

            echo $row
            # sleep 0.1
            echo $row >> $record
        fi
    done
fi