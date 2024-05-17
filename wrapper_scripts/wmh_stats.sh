#!/usr/bin/bash

id=$1
mridate=$2
flair=$3
wmh_mask=$4
outputfile=$5

RID=$(echo $id | cut -f 3 -d "_")

### Voxel Spacing to id older FLAIRs with lower resolution
flair_resolution=$( c3d $flair -info-full | grep Spacing | \
  sed -e "s/[a-zA-Z:,]//g" -e "s/\]//" -e "s/\[//" | awk '{print $3}' )

###White matter hyperintensity from FLAIR nifti (volume of region 1)
wmh_vol=$( c3d $wmh_mask $flair -interp NN -reslice-identity $wmh_mask -lstat | awk '{print $7}' | tail -n 1 )


echo -e $RID,$id,$mridate,$flair_resolution,$wmh_vol | tee $outputfile
