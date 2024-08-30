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

id=$1  
mridate=$2
taudate=$3
amydate=$4

wholebrainseg=$5
wbsegtoants=$6
wblabelfile=$7

icvfile=$8

cleanup_left=$9
cleanup_right=${10}
cleanup_both=${11}

t1tausuvr=${12}
t1amysuvr=${13}

stats_output_file=${14}

t1_ashs_seg_prefix=${15}

t1_to_t2_transform=${16}   
t2_nifti=${17}
t1trim=${18}   ##for creating transform if it's not saved in ashs folder


#ID, ICV vol and thickness to stat variable
RID=$(echo $id | cut -f 3 -d "_")
ICV=$( printf %10.2f $(cat $icvfile | awk '{print $5}'))
thick=$(c3d $cleanup_left -info-full | grep Spacing | \
  sed -e "s/[a-zA-Z:,]//g" -e "s/\]//" -e "s/\[//" | awk '{print $3}')
statline="$RID,$id,$mridate,$amydate,$taudate,$ICV,$thick"
# echo $statline 


module load PETPVC/1.2.10
module load greedy
TMPDIR=$(mktemp -d)

for pettype in tau amy ; do 
    echo "Doing stats for ${pettype}"
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
		greedy -d 3 -a -dof 6 -m MI -n 100x100x10 -i $TMPDIR/tse_iso.nii.gz $t1trim -ia-identity -o $t1_to_t2_transform
    fi

    t2_pet_suvr="$TMPDIR/T2_${pettype}pet_suvr.nii.gz"
    c3d $t2_nifti $t1_pet_suvr -reslice-matrix $t1_to_t2_transform -o $t2_pet_suvr

    for suvr_or_pvc in suvr pvc ; do 
        echo "doing stats for ${suvr_or_pvc}"
        if [ "$suvr_or_pvc" == "suvr" ] ; then
            t1_pet_touse=$t1_pet_suvr
            t2_pet_touse=$t2_pet_suvr
        else 
            echo Make PVC versions of petreg images
            ##### T1 PVC
            t1_pet_pvc=$TMPDIR/T1_${pettype}pet_pvc.nii.gz
            pvc_vc $t1_pet_suvr $t1_pet_pvc -x 8.0 -y 8.0 -z 8.0
            
            ##### Make T2 PVC
            t2_pet_pvc="$TMPDIR/T2_${pettype}pet_pvc.nii.gz"
            c3d $t2_nifti $t1_pet_pvc -reslice-matrix $t1_to_t2_transform -o $t2_pet_pvc

            ##### set pvc file to variables for loop
            t1_pet_touse=$t1_pet_pvc
            t2_pet_touse=$t2_pet_pvc

        fi

        for side in left right ; do 
            if [ "$side" == "left" ] ; then
                cleanup_seg=$cleanup_left
            elif [ "$side" == "right" ] ; then
                cleanup_seg=$cleanup_right
            fi

            ####################### ASHST2 regions: cleanupt2_side + t2-pet reg #######################
            echo "${pettype}:${suvr_or_pvc}:${side}:ASHST2 with:${t2_pet_touse}"
            c3d $cleanup_seg $t2_pet_touse -interp NN -reslice-identity $cleanup_seg -lstat > $TMPDIR/statt2pet.txt
            #labels == CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus 
            labels=$(echo 1 2 4 3 7 8 10 11 12 13 14)
            for i in $labels; do
                statline="$statline,$(cat $TMPDIR/statt2pet.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}' )"
            done
            echo $statline

            # Combine CA regions (CA1 + CA2 + CA3) to get total CA values
            c3d $cleanup_seg -replace 2 1 4 1 -as A $t2_pet_touse -interp NN -reslice-identity -push A -lstat > $TMPDIR/statca.txt
            statline="$statline,$(cat $TMPDIR/statca.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}' )"

            # Combine hippocampal regions to get total HIPP values 
            c3d $cleanup_seg -replace 2 1 3 1 4 1 -as A $t2_pet_touse -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathipp.txt
            statline="$statline,$(cat $TMPDIR/stathipp.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}' )"

            # Combine EXTHIPPO regions to get total EXTHIPPO values 
            c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 12 1 -as A $t2_pet_touse -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthipp.txt
            statline="$statline,$(cat $TMPDIR/statexthipp.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}' )"
            
            # Combine EXTHIPPO NO BA36 regions to get total EXTHIPPO NO BA36 values 
            c3d $cleanup_seg -replace 1 2 -replace 10 1 11 1 -as A $t2_pet_touse -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36.txt
            statline="$statline,$(cat $TMPDIR/statexthippno36.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')"
          
            # Combine MTL NO BA36 regions to get total MTL NO BA36 values 
            c3d $cleanup_seg -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2_pet_touse -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36.txt
            statline="$statline,$(cat $TMPDIR/statmtlno36.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')"

            if [ ${pettype} == 'tau' ] ; then 
                ####################### Whole brain Tau measures BRAAK stages 3-6 #######################
                echo "${pettype}:${suvr_or_pvc}:${side}:do WBseg BRAAK regions with:${t1_pet_touse}"
                WBTAULABELIDS=(BRAAK3 BRAAK4 BRAAK5 BRAAK6)
                WBTAULABELLEFTNUMS=("32 34 171 123 135" "173 103 133 155 167" "125 201 127 163 165 205 115 169 101 195 145 169 199 153 191 141 143" "109 115 149 151 177 183")
                WBTAULABELRIGHTNUMS=("31 33 170 122 134" "172 102 132 154 166" "124 200 126 162 164 204 114 168 100 194 144 168 198 152 190 140 142" "108 114 148 150 176 182")
                WBTAU=""
                # extract measurements
                for ((i=0;i<${#WBTAULABELIDS[*]}; i++)); do
                    if [[ -f $wbsegtoants && -f $t1_pet_touse ]]; then
                        if [[ $side == "left" ]]; then
                            REPRULE=$(for lab in ${WBTAULABELLEFTNUMS[i]}; do echo $lab 999; done)
                        else
                            REPRULE=$(for lab in ${WBTAULABELRIGHTNUMS[i]}; do echo $lab 999; done)
                        fi
                        WBTAU="$WBTAU,$(c3d $wbsegtoants -replace $REPRULE -thresh 999 999 1 0 -as SEG \
                        $t1_pet_touse -int 0 -reslice-identity \
                        -push SEG -lstat | awk '{print $2}' | tail -n 1)"
                    else
                        WBTAU="$WBTAU,"
                    fi
                done
                statline="$statline$WBTAU" ##WBTAU variable starts with comma
                echo $statline

                ####################### ASHST1-tau measures #######################
                echo "${pettype}:${suvr_or_pvc}:${side}:do ASHST1 regions with:${t1_pet_touse}"
                ASHST13TTAULABELIDS=(AHippo PHippo ERC BA35 BA36 PHC ERCBA35 WholeHippo MTLCortex     All)
                ASHST13TTAULABELNUMS=(1     2      10  11   12   13  "10 11" "1 2"      "10 11 12 13" "1 2 10 11 12 13")
                SEG=${t1_ashs_seg_prefix}_${side}_lfseg_heur_LW.nii.gz
                if [[ ! -f $SEG ]]; then
                    SEG=${t1_ashs_seg_prefix}_${side}_lfseg_heur.nii.gz
                fi
                TAU=""
                # extract measurements
                for ((i=0;i<${#ASHST13TTAULABELIDS[*]}; i++)); do
                    REPRULE=$(for lab in ${ASHST13TTAULABELNUMS[i]}; do echo $lab 99; done)
                    TAU="$TAU,$(c3d $SEG -replace $REPRULE -thresh 99 99 1 0 -as SEG \
                    $t1_pet_touse -int 0 -reslice-identity -push SEG -lstat | awk '{print $2}' | tail -n 1)"
                done 
                TAU="${TAU:1}"  #remove leading comma
                statline="$statline,$TAU"
                echo $statline

            fi

            if [ ${side}  == 'right' ] ; then 
                ####################### Combined ASHST2 regions: cleanupt2_side + t2-pet reg #######################
                echo "${pettype}:${suvr_or_pvc}:${side}:do 'Both' ASHST2 regions with:${t2_pet_touse}"
                # BOTH HIPP
                c3d $cleanup_both -replace 2 1 3 1 4 1 -as A $t2_pet_touse -interp NN -reslice-identity -push A -lstat > $TMPDIR/stathippboth.txt
                statline="$statline,$(cat $TMPDIR/stathippboth.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}' )"
                # BOTH EXTHIPPO NO BA36
                c3d $cleanup_both -replace 1 2 -replace 10 1 11 1 -as A $t2_pet_touse -interp NN -reslice-identity -push A -lstat > $TMPDIR/statexthippno36both.txt
                statline="$statline,$(cat $TMPDIR/statexthippno36both.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}' )"
                # BOTH MTL NO BA36
                c3d $cleanup_both -replace 2 1 3 1 4 1 10 1 11 1 -as A $t2_pet_touse -interp NN -reslice-identity -push A -lstat > $TMPDIR/statmtlno36both.txt
                statline="$statline,$(cat $TMPDIR/statmtlno36both.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}' )"

                ####################### cereb values from file, saved off during suvr.sh
                if [[ ${suvr_or_pvc} == 'suvr' ]] ; then
                    cerebfile=$( echo $t1_pet_touse | sed 's/.nii.gz/_CEREB.txt/' )
                    statline="$statline,$( cat $cerebfile )"
                fi

                ####################### T1 Whole Brain ROIs #######################
                echo "${pettype}:${suvr_or_pvc}:${side}:do T1 wbseg regions with:${t1_pet_touse}"
                # Occipital lobe ROIs
                c3d $wbsegtoants -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000\
                -thresh 1000 1000 1 0 -as A $t1_pet_touse -interp NN -reslice-identity -push A  -lstat > $TMPDIR/statocc.txt
                statline="$statline,$(cat $TMPDIR/statocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}' )"
                    
                # Posterior cingulate ROIs
                c3d $wbsegtoants -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $t1_pet_touse -interp NN \
                -reslice-identity -push A  -lstat > $TMPDIR/statpc.txt
                statline="$statline,$(cat $TMPDIR/statpc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}' )"
            
                # Other ROIs suitable for looking at subtypes: 
                # inf temporal gyrus (132 133) middle temporal (154 right 155 left) superior temporal 200 201 \
                # superior parietal 198 199 calcarine 108 109 angular gyrus 106 107 190 191 superior frontal
                c3d $wbsegtoants -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; \
                                            do echo "-push A -thresh $roi $roi $roi 0" ; done) \
                                -accum -add -endaccum -as SUM  $t1_pet_touse -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/variousrois.txt
                for i in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; do
                    statline="$statline,$( cat $TMPDIR/variousrois.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}' )"
                done

                #### All ROIs from WB atlas
                c3d $wbsegtoants -as A $t1_pet_touse -interp NN -reslice-identity -push A  -lstat > $TMPDIR/allwb.txt
                for i in $(cat $wblabelfile | grep -v '#' | sed -n '9,$p' | \
                            grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF|Thalamus|Forebrain' | awk '{print $1}' ); do
                    statline="$statline,$(cat $TMPDIR/allwb.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}' )"
                done


                if [[ ${pettype} == 'amy' && ${suvr_or_pvc} == 'suvr' ]] ; then 
                    ####################### Amyloid Comp SUVR #######################
                    echo "${pettype}:${suvr_or_pvc}:${side}:do compuSUVR with:${t1_pet_touse}"
                    # Left_MFG_middle_frontal_gyrus,Right_MFG_middle_frontal_gyrus,Left_ACgG_anterior_cingulate_gyrus,
                    # Right_ACgG_anterior_cingulate_gyrus,Left_PCgG_posterior_cingulate_gyrus,Right_PCgG_posterior_cingulate_gyrus,
                    # Left_AnG_angular_gyrus,Right_AnG_angular_gyrus,Left_PCu_precuneus,Right_PCu_precuneus,
                    # Left_SMG_supramarginal_gyrus,Right_SMG_supramarginal_gyrus,Left_MTG_middle_temporal_gyrus,
                    # Right_MTG_middle_temporal_gyrus,Left_ITG_inferior_temporal_gyrus,Right_ITG_inferior_temporal_gyrus
                    sum=0
                    for i in 142 143 100 101 166 167 106 107 168 169 194 195 154 155 132 133; do
                        THISPET=$(cat $TMPDIR/allwb.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
                        sum=$(echo $sum + $THISPET | bc -l )
                    done
                    compsuvr="0$(echo $sum/16 | bc -l )"
                    statline="$statline,$compsuvr"
                fi
            fi
        done
    done
done

echo 
echo
echo
echo -e $statline | tee $stats_output_file

rm -rf $TMPDIR