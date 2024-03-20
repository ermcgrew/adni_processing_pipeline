#!/usr/bin/bash

##
suvr=$1
pvc=$2

module load PETPVC/1.2.10
FWHM=8.0
# /home/emcgrew/bin/pybatch.sh -m 8G -o $ROOT/$ID/$TAUDATE -N 
# pvcinfcereb 
pvc_vc $suvr $pvc -x $FWHM -y $FWHM -z $FWHM
