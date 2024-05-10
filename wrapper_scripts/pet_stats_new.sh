#!/usr/bin/bash

# Usage:
# ./pet_stats.sh 
# id mridate taudate amydate  
# wholebrainseg wbsegtoants wblabelfile
# icv.txt 
# cleanup/seg_left cleanup/seg_right cleanup/seg_both
# t1tausuvr t1amysuvr 
# stats_output_file 
# ASHST1dir/final/${id}  


# export DOERODE=true
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

# t1tausuvr=${}
# t1amysuvr=${}

# stats_output_file=${}

# t1_ashs_seg_prefix=${}

# t1_to_t2_transform=${}   ##from sfsegnibtend/flirt_t2_to_t1/
# t2_nifti={}
# t1trim={}   ##for creating transform if it's not saved in ashs folder)


t1tausuvr=taupet6mm_to_mprageANTS_suvr.nii.gz
t1amysuvr=amypet6mm_to_mprageANTS_suvr.nii.gz
t1_to_t2_transform="flirt_t2_to_t1_inv.mat" 

TMPDIR=tmpdir



module load PETPVC/1.2.10

# TMPDIR=$(mktemp -d)

for pettype in tau amy ; do 
    # echo "Doing stats for ${pettype}"
    if [ "$pettype" == "tau" ] ; then
        t1_pet_suvr=$t1tausuvr
    else
        t1_pet_suvr=$t1amysuvr
    fi

    echo Make T2 to ${pettype} suvr registration

    if [[ ! -f $t1_to_t2_transform ]] ; then 
        echo First make T1 to T2 transform file
        mkdir -p $SDROOT/$id/$tp/${SFSEG}/flirt_t2_to_t1
		c3d $t2_nifti -resample 100x100x500% -region 20x20x0% 60x60x100% -type short -o $TMPDIR/tse_iso.nii.gz
		/project/hippogang_1/srdas/homebin/greedy -d 3 -a -dof 6 -m MI -n 100x100x10 -i $TMPDIR/tse_iso.nii.gz $t1trim -ia-identity -o $t1_to_t2_transform
    fi

    t2_pet_suvr="$TMPDIR/T2_${pettype}pet_suvr.nii.gz"
    c3d $t2_nifti $t1_pet_suvr -reslice-matrix $t1_to_t2_transform -o $t2_pet_suvr

    for suvr_or_pvc in suvr pvc ; do 
        # echo "doing stats for ${suvr_or_pvc}"
        if [ "$suvr_or_pvc" == "suvr" ] ; then
            t1_pet_touse=$t1_pet_suvr
            t2_pet_touse=$t2_pet_suvr
        else 
            echo Make PVC versions of petreg images
            ##### T1 PVC
            t1_pet_pvc=$TMPDIR/T1_${pettype}pet_pvc.nii.gz
            pvc_vc $T1_pet_suvr $T1_pet_pvc -x 8.0 -y 8.0 -z 8.0
            
            ##### Make T2 PVC
            t2_pet_pvc="$TMPDIR/T2_${pettype}pet_pvc.nii.gz"
            c3d $t2_nifti $t1_pet_pv -reslice-matrix $t1_to_t2_transform -o $t2_pet_pvc

            ##### set pvc file to variables for loop
            t1_pet_touse=$t1_pet_pvc
            t2_pet_touse=$t2_pet_pvc

        fi

        for side in left right ; do 
            echo "${pettype}:${suvr_or_pvc}:${side}:ASHST2 with:${t2_pet_touse}"

            if [ ${pettype} == 'tau' ] ; then 
                echo "${pettype}:${suvr_or_pvc}:${side}:do WBseg BRAAK regions with:${t1_pet_touse}"
                echo "${pettype}:${suvr_or_pvc}:${side}:do ASHST1 regions with:${t1_pet_touse}"
            fi

            if [ ${side}  == 'right' ] ; then 
                echo "${pettype}:${suvr_or_pvc}:${side}:do 'Both' ASHST2 regions with:${t2_pet_touse}"
                echo "${pettype}:${suvr_or_pvc}:${side}:do T1 wbseg regions with:${t1_pet_touse}"

                if [[ ${pettype} == 'amy' && ${suvr_or_pvc} == 'suvr' ]] ; then 
                    echo "${pettype}:${suvr_or_pvc}:${side}:do compuSUVR with:${t1_pet_touse}"
                fi
            fi


        done

    done

done

# rm -rf $TMPDIR