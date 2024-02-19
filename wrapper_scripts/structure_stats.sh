#!/usr/bin/bash

id=$1  
wholebrainseg=$2 
thickness=$3 
wblabelfile=$4
mridate=$5

# Mask with GM
tissueseg=$(echo $thickness | sed -e 's/CorticalThickness/BrainSegmentation/g')
# All ROIs thickness
MASKCOMM="$tissueseg -interp NN -reslice-identity -thresh 2 2 1 0 -times"
c3d $wholebrainseg -dup $MASKCOMM -as A $thickness -interp NN -reslice-identity -push A  -lstat > $TMPDIR/allthick.txt
for i in $(cat $wblabelfile | grep -v '#' | sed -n '9,$p' | \
    grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' | awk '{print $1}' ); do    
        THISTHICK=$(cat $TMPDIR/allthick.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $2}')
        statline="$statline\t $THISTHICK"
done

echo -e $statline >> ${stats_output_dir}/stats_mri_${mridate}_${id}_structure.txt