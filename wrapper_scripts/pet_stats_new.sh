#!/usr/bin/bash

# Usage:
# ./pet_stats.sh id mridate taudate amydate  
# wholebrainseg wbsegtoants wblabelfile
# icv.txt 
# cleanup/seg_left cleanup/seg_right cleanup/seg_both
# t1tau t1tausuvr t1tausuvrpvc t2taureg t1amyreg t2amyreg 
# stats_output_file 
# ASHST1dir/final/${id}  


# export DOERODE=true
# TMPDIR=$(mktemp -d)
# export TMPDIR

# id=$1  
# mridate=$2
# taudate=$3
# amydate=$4

# wholebrainseg=$5
# wbsegtoants=$6
# wblabelfile=$7

# icvfile=$8

# cleanup_left=$9
# cleanup_right=${10}
# cleanup_both=${11}

# t1tau=${12}
# t1tausuvrpvc=${14}
# t2tau=${15} 
# t1amy=${16} 
# t2amy=${17} 

# stats_output_file=${18}

# t1_ashs_seg_prefix=${19}


t1tausuvr=${13}
t1amysuvr=${20}
T1_to_T2_transform=${21}


for pettype in tau amy ; do 
    # echo "Doing stats for ${pettype}"
    if [ "$pettype" == "tau" ] ; then
        T1_pet_suvr=$t1tausuvr
    else
        T1_pet_suvr=$t1amysuvr
    fi

    # echo c3d command: T1_to_T2_transform x T1_pet_suvr = T2_pet_suvr
    T2_pet_suvr="$TMPDIR/T2_pet_suvr.nii.gz"

    for suvr_or_pvc in suvr pvc ; do 
        # echo "doing stats for ${suvr_or_pvc}"
        if [ "$suvr_or_pvc" == "suvr" ] ; then

            t1_pet_something=$T1_pet_suvr
            t2_pet_something=$T2_pet_suvr

        else 
            # echo "T1_pet_pvc = T1_pet_suvr x c3d command"

            T1_pet_pvc=$TMPDIR/T1_pet_pvc.nii.gz
            # module load PETPVC/1.2.10
            # FWHM=8.0
            # pvc_vc $T1_pet_suvr $T1_pet_pvc -x $FWHM -y $FWHM -z $FWHM

            # echo T2_pet_pvc=T1_to_T2_transform x $T1_pet_pvc
            T2_pet_pvc="$TMPDIR/T2_pet_pvc.nii.gz"

            t1_pet_something=$T1_pet_pvc
            t2_pet_something=$T2_pet_pvc

        fi

        for side in left right ; do 
            echo "${pettype}:${suvr_or_pvc}:${side}:ASHST2"

            if [ ${pettype} == 'tau' ] ; then 
                echo "${pettype}:${suvr_or_pvc}:${side}:do WBseg BRAAK regions"
                echo "${pettype}:${suvr_or_pvc}:${side}:do ASHST1 regions"
            fi

            if [ ${side}  == 'right' ] ; then 
                echo "${pettype}:${suvr_or_pvc}:${side}:do 'Both' ASHST2 regions"
                echo "${pettype}:${suvr_or_pvc}:${side}:do T1 wbseg regions"

                if [[ ${pettype} == 'amy' && ${suvr_or_pvc} == 'suvr' ]] ; then 
                    echo "${pettype}:${suvr_or_pvc}:${side}:do compuSUVR"
                fi
            fi


        done

    done

done