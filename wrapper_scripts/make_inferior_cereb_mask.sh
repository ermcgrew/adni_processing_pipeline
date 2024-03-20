#!/usr/bin/bash

##Make a mask of the inferior cerebellum to use in tau-t1 registration calculations

wbseg=$1
inf_cereb_mask=$2

wbdir=$(dirname "$wbseg")
allcereb="${wbdir}/whole_cerebellum.nii.gz"

##From Sandy's utility find_infcereb
c3d $wbseg -replace 38 inf 39 inf 40 inf 41 inf 71 inf 72 inf 73 inf -thresh inf inf 1 0 -o $allcereb
c3d $allcereb -cmv -oo $wbdir/coordmap%d.nii.gz

##from Sandy's utility findaxisdir
ORIENT=$(c3d $allcereb -info | head -n 1 | awk '{print $NF}' )
pos=$(echo $ORIENT | grep -b -o "I")
dir=pos
if [ "$pos" == "" ]; then
    pos=$(echo $ORIENT | grep -b -o "S")
    dir=neg
fi

axpos=$(expr ${pos:0:1} )
maxaxslice=$(c3d $wbdir/coordmap${axpos}.nii.gz $allcereb -times $allcereb -lstat | sed -n "3p" | awk '{print $4}' ) 
minaxslice=$(c3d $wbdir/coordmap${axpos}.nii.gz $allcereb -times $allcereb -lstat | sed -n "3p" | awk '{print $5}' ) 
if [ "$dir" == "neg" ]; then
    minslice=$(echo "$maxaxslice - ( $maxaxslice - $minaxslice )/2 " | bc -l )
    maxslice=$maxaxslice
else
    minslice=$minaxslice
    maxslice=$(echo "$minaxslice + ( $maxaxslice - $minaxslice )/2 " | bc -l )
fi

c3d $allcereb $wbdir/coordmap${axpos}.nii.gz -thresh $minslice $maxslice 1 0 -times -o $inf_cereb_mask
rm -f $allcereb $wbdir/coordmap?.nii.gz	