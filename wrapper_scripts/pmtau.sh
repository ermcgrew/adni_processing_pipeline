#!/usr/bin/bash
# adapted from /project/hippogang_1/srdas/wd/TAUPET/longnew/pmtau_to_invivot1.sh

ADNIROOT=/project/wolk_2/ADNI2018/dataset
SANDYROOT=/project/hippogang_1/srdas/wd/TAUPET/longnew

sub=$1
mridate=$2
THICKDIR=$3

pmmap=template_avg_density_cutoff_mild_Tau_tangles.nii.gz
pmfreq=template_avg_density_Tau_tangles.nii.gz


/home/sudas/bin/antsApplyTransforms -d 3 \
    -i ${SANDYROOT}/pmtau/$pmmap -r $THICKDIR/${sub}CorticalThickness.nii.gz \
    -t [$THICKDIR/${sub}SubjectToTemplate0GenericAffine.mat,1] \
    $THICKDIR/${sub}TemplateToSubject0Warp.nii.gz \
    ${SANDYROOT}/abc_to_ADNINormal1Warp.nii.gz \
    ${SANDYROOT}/abc_to_ADNINormal0GenericAffine.mat \
    -o $THICKDIR/${pmmap%.nii.gz}_to_t1.nii.gz
    
/home/sudas/bin/antsApplyTransforms -d 3 \
    -i $SANDYROOT/pmtau/$pmfreq -r $THICKDIR/${sub}CorticalThickness.nii.gz \
    -t [$THICKDIR/${sub}SubjectToTemplate0GenericAffine.mat,1] \
    $THICKDIR/${sub}TemplateToSubject0Warp.nii.gz \
    $SANDYROOT/abc_to_ADNINormal1Warp.nii.gz \
    $SANDYROOT/abc_to_ADNINormal0GenericAffine.mat \
    -o $THICKDIR/${pmfreq%.nii.gz}_to_t1.nii.gz
    
echo "$sub $mridate warping done"
OUTDIR=$THICKDIR

# Find ASHS segmentation, find the AH/PH boundary using distance map
SEG=$ADNIROOT/$sub/$mridate/ASHST1/final/${sub}_right_lfseg_corr_nogray.nii.gz
MYSEG=$OUTDIR/ashsseg.nii.gz
c3d $THICKDIR/${sub}CorticalThickness.nii.gz \
    $SEG -interp NN -reslice-identity -o $MYSEG

pos=$( /home/sudas/bin/findaxisdir $MYSEG cor | awk '{print $1}' )
dir=$( /home/sudas/bin/findaxisdir $MYSEG cor | awk '{print $2}' )

c3d $MYSEG -as A -thresh 1 1 1 0 -sdt -popas DISTA -push A -thresh 2 2 1 0 -sdt \
    -dup -times -sqrt -push DISTA -dup -times -sqrt  -add \
    -thresh 1.0 1.2 1 0 -o $OUTDIR/bndry.nii.gz -cmv -oo $OUTDIR/coordmap%d.nii.gz

bndry_centroid=$(c3d $OUTDIR/bndry.nii.gz -centroid | grep CENTROID_VOX | cut -f 2 -d "[" | cut -f 1 -d "]" | sed -e "s/ //g" | cut -f $pos -d , | awk '{printf("%.f\n",$0)}' )

zeropos=$(echo " $pos - 1 " | bc -l )
if [ "$dir" == "neg" ]; then
    c3d $OUTDIR/coordmap${zeropos}.nii.gz -thresh 0 $bndry_centroid 1 2 -o $OUTDIR/ap.nii.gz
else
    c3d $OUTDIR/coordmap${zeropos}.nii.gz -thresh 0 $bndry_centroid 2 1 -o $OUTDIR/ap.nii.gz
fi

rm -f $OUTDIR/coordmap?.nii.gz $OUTDIR/bndry.nii.gz
