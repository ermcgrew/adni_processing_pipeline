#!/usr/bin/bash

Site=$1
SCANNERFILE=/project/hippogang_1/srdas/wd/ADNI2/ADNI2_vs_ADNI3_MRI_Scanner_edited_withADNI2scannerchangeforT2.csv

searchSite=$(echo $Site | sed -e "s/^0//g" | sed -e "s/^0//g")
Scanline=$(cat $SCANNERFILE | grep ^${searchSite}, )
if [ "$Scanline" != "" ]; then
    Model2=$(echo $Scanline | cut -f 9 -d "," | sed -e 's/ //g')
    Model3=$(echo $Scanline | cut -f 4 -d "," | sed -e 's/ //g')
    Vendor2=$(echo $Scanline | cut -f 8 -d "," | sed -e 's/ //g')
    Vendor3=$(echo $Scanline | cut -f 3 -d "," | sed -e 's/ //g')
fi

echo $Model2
echo $Model3
echo $Vendor2
echo $Vendor3