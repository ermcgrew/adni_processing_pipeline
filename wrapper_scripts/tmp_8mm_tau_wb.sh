#!/usr/bin/bash

### For Xueying -- needs wb tau measures from 8mm SUVR scans using infcereb reference
module load PETPVC/1.2.10

export DOERODE=true
TMPDIR=$(mktemp -d)
export TMPDIR

id=$1  
mridate=$2
taudate=$3

wholebrainseg=$4 ## original to get CEREB tau value
wbsegtoants=$5 ## using prop to ANTs space
wblabelfile=$6

icvfile=$7

t1tau_suvr=$8 ## using 8mm saved as SUVR using infcereb as ref region

stats_output_file=$9

echo "using 8mm T1-tau SUVR file: ${t1tau_suvr}"
echo "using whole brain seg propagated to ANTs space: ${wbsegtoants}"

#ID, ICV vol to stat variable
RID=$(echo $id | cut -f 3 -d "_")
ICV=$( printf %10.2f $(cat $icvfile | awk '{print $5}'))
statline="$RID,$id,$mridate,$taudate,$ICV"
echo got dates and icv



### Get cerebellar reference region to compare radiotracer uptake to
### wholebrain seg + t1-pet reg
wbdir=$( dirname $wholebrainseg )
inf_cereb_mask="${wbdir}/inferior_cerebellum.nii.gz"
plaintau=$( echo $t1tau_suvr | sed 's/_SUVR_infcereb//')
CEREBTAU=$(c3d $wholebrainseg $inf_cereb_mask -times -as SEG -thresh 38 38 1 0 -erode 1 2x2x2vox -popas A \
-push SEG -thresh 39 39 1 0 -erode 1 2x2x2vox -popas B \
-push SEG -thresh 71 71 1 0 -erode 1 2x2x2vox -popas C \
-push SEG -thresh 72 72 1 0 -erode 1 2x2x2vox -popas D \
-push SEG -thresh 73 73 1 0 -erode 1 2x2x2vox -popas E \
-push A -push B -add -push C -add -push D -add -push E -add -as CEREB $plaintau \
-interp NN -reslice-identity -push CEREB  -lstat | \
sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
statline="$statline,$CEREBTAU"
echo got CEREB


##### T1 PVC
TMPDIR=$(mktemp -d)
t1tau_pvc=$TMPDIR/T1_taupet_pvc.nii.gz
pvc_vc $t1tau_suvr $t1tau_pvc -x 8.0 -y 8.0 -z 8.0
echo made pvc version


for t1tau in $t1tau_suvr $t1tau_pvc ; do 

    ####tau & amy values for ROIs from T1 whole brain seg
    # Occipital lobe ROIs
    c3d $wbsegtoants -replace 128 1000 129 1000 144 1000 145 1000 156 1000 157 1000 160 1000 161 1000 \
    -thresh 1000 1000 1 0 -as A $t1tau -interp NN -reslice-identity -push A  -lstat > $TMPDIR/stattauocc.txt
    THISTAU=$(cat $TMPDIR/stattauocc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline,$THISTAU"
    echo got Occ lobe
        
    # Posterior cingulate ROIs
    c3d $wbsegtoants -replace 166 1000 167 1000 -thresh 1000 1000 1 0 -as A $t1tau -interp NN \
    -reslice-identity -push A  -lstat > $TMPDIR/stattaupc.txt
    THISTAU=$(cat $TMPDIR/stattaupc.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
    statline="$statline,$THISTAU"
    echo got posterior cing

    # Other ROIs suitable for looking at subtypes: 
    # inf temporal gyrus (132 133) middle temporal (154 right 155 left) superior temporal 200 201 \
    # superior parietal 198 199 calcarine 108 109 angular gyrus 106 107 190 191 superior frontal
    c3d $wbsegtoants -popas A $(for roi in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; \
    do echo "-push A -thresh $roi $roi $roi 0" ; done) \
        -accum -add -endaccum -as SUM  $t1tau -interp NN -reslice-identity -push SUM -lstat > $TMPDIR/varioustaurois.txt
    for i in 132 133 154 155 200 201 198 199 108 109 106 107 190 191; do
        THISTAU=$(cat $TMPDIR/varioustaurois.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
        statline="$statline,$THISTAU"
    done
    echo completed other ROIs

    #### All ROIs tau, amy
    c3d $wbsegtoants -as A $t1tau -interp NN -reslice-identity -push A  -lstat > $TMPDIR/alltau.txt
    for i in $(cat $wblabelfile | grep -v '#' | sed -n '9,$p' | \
    grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF|Thalamus|Forebrain' | awk '{print $1}' ); do
        THISTAU=$(cat $TMPDIR/alltau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
        statline="$statline,$THISTAU"
    done
    echo got wblabel file regions
done

echo -e $statline | tee $stats_output_file




## to get headers and collect all stats
# header="RID,ID,SCANDATE.mri,SCANDATE.tau,ICV_vol,CEREB_tau"
# for type in suvr pvc ; do
#     header="${header},occ_tau_${type},postcing_tau_${type}"
#     for roi in inftemp midtemp suptemp suppariet calc angular supfront ; do 
#         for side in R L ; do 
#             header="${header},${roi}_${side}_tau_${type}" 
#         done  
#     done

#     for roi in $( cat utilities/wholebrainlabels_itksnaplabelfile.txt | grep -v '#' | sed -n '9,$p' | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF|Thalamus|Forebrain'| cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do 
#         header="${header},${roi}_wb_tau_${type}"
#     done
# done

# echo $header
# outputfile="/project/wolk/ADNI2018/analysis_output/data/wholebrain_8mmtauSUVRinfcereb_xueying_20250328.csv"

# echo $header >> $outputfile
# cat /project/wolk/ADNI2018/analysis_output/stats/8mmtauwb_20250328/* >> $outputfile
