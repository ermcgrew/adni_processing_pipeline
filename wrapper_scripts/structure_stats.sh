#!/usr/bin/bash

wholebrainseg=$1 
thickness=$2
wblabelfile=$3
outputfile=$4

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

echo -e $statline | tee $outputfile

rm -r $TMPDIR