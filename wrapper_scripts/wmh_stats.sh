#!/usr/bin/bash

id=$1
mridate=$2
flair=$3
wmh_mask=$4
outputfile=$5

RID=$(echo $id | cut -f 3 -d "_")

###White matter hyperintensity from FLAIR nifti (volume of region 1)
wmh_vol=$( c3d $flair $wmh_mask -lstat | awk '{print $7}' | tail -n 1 )


echo -e $RID,$id,$mridate,$wmh_vol | tee $outputfile
