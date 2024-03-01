#!/usr/bin/bash

wholebrainseg=$1 
thickness=$2
wblabelfile=$3
outputfile=$4
pmtau_template_dir=$5
id=$6
mridate=$7


RID=$(echo $id | cut -f 3 -d "_")
statline="$RID,$id,$mridate"

TMPDIR=$(mktemp -d)

# Mask with GM
tissueseg=$(echo $thickness | sed -e 's/CorticalThickness/BrainSegmentation/g')
MASKCOMM="$tissueseg -interp NN -reslice-identity -thresh 2 2 1 0 -times"
c3d $wholebrainseg -dup $MASKCOMM -as A $thickness -interp NN -reslice-identity -push A -lstat > $TMPDIR/allthick.txt

# All ROIs thickness
for i in $(cat $wblabelfile | grep -v '#' | sed -n '9,$p' | \
    grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' | awk '{print $1}' ); do    
        THISTHICK=$(cat $TMPDIR/allthick.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
        statline="$statline,$THISTHICK"
done

################ PM Tau #############
# Mask with GM
jacobian=$(echo $tissueseg | sed -e 's/BrainSegmentation/SubjectToTemplateLogJacobian/g' )
tempgmmask=$pmtau_template_dir/adninormalgmmask.nii.gz
TEMPMASKCOMM="$tempgmmask -interp NN -reslice-identity -thresh 1 1 1 0 -times"
# PMTAU Anterior and Posterior ROI
pmtau=$(dirname $thickness)/template_avg_density_cutoff_mild_Tau_tangles_to_t1.nii.gz
pmfreq=$(dirname $thickness)/template_avg_density_Tau_tangles_to_t1.nii.gz
apmask=$(dirname $thickness)/ap.nii.gz
# PMTAU Anterior and Posterior ROI template space
pmtautemp=$pmtau_template_dir/template_avg_density_cutoff_mild_Tau_tangles_to_ADNINormal.nii.gz
pmfreqtemp=$pmtau_template_dir/template_avg_density_Tau_tangles_to_ADNINormal.nii.gz
apmasktemp=$pmtau_template_dir/ap.nii.gz
# Thresholded PMTAU mask
PMTAUTHRESH=0.2
c3d $apmask -dup $pmtau -interp NN -reslice-identity -thresh $PMTAUTHRESH 1 1 0 -times \
    -dup $MASKCOMM -as APMASKED -dup $thickness -interp NN -reslice-identity -push APMASKED  \
    -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauthick.txt
c3d $apmasktemp -dup $pmtautemp -interp NN -reslice-identity -thresh $PMTAUTHRESH 1 1 0 -times \
    -dup $TEMPMASKCOMM -as APMASKED -dup $jacobian -interp NN -reslice-identity -push APMASKED  \
    -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtaujac.txt
# Weighted PMTAU thickness
c3d $apmask -dup $pmfreq -interp NN -reslice-identity -as PMTAU -thresh $PMTAUTHRESH 1 1 0 -times \
    -dup $MASKCOMM -as APMASKED $thickness -interp NN -reslice-identity -push PMTAU -times -push APMASKED \
    -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauweightedthick.txt
c3d $apmasktemp -dup $pmfreqtemp -interp NN -reslice-identity -as PMTAU -thresh $PMTAUTHRESH 1 1 0 -times \
    -dup $TEMPMASKCOMM -as APMASKED $jacobian -interp NN -reslice-identity -push PMTAU -times -push APMASKED \
    -lstat | sed -n '3,$p' | awk ' { OFS=","; print $1,$2}' > $TMPDIR/pmtauweightedjac.txt
# PMTAU thresholded thickness ANT and POST
ANT=1
POST=2
for i in $ANT $POST; do
    THISTHICK=$(cat $TMPDIR/pmtauthick.txt | grep "^${i}," | cut -f 2 -d "," ) 
    PMTAU="$PMTAU,$THISTHICK"
    THISTHICK=$(cat $TMPDIR/pmtauweightedthick.txt | grep "^${i}," | cut -f 2 -d "," ) 
    PMTAU="$PMTAU,$THISTHICK"
    THISJAC=$(cat $TMPDIR/pmtaujac.txt | grep "^${i}," | cut -f 2 -d "," ) 
    PMTAU="$PMTAU,$THISJAC"
    THISJAC=$(cat $TMPDIR/pmtauweightedjac.txt | grep "^${i}," | cut -f 2 -d "," ) 
    PMTAU="$PMTAU,$THISJAC"
done

statline="$statline$PMTAU" ##PMTAU var starts with comma

echo -e $statline | tee $outputfile

rm -r $TMPDIR