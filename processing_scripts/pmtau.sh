#!/usr/bin/bash
# adapted from /project/hippogang_1/srdas/wd/TAUPET/longnew/pmtau_to_invivot1.sh

utilities=/project/wolk/ADNI2018/scripts/adni_processing_pipeline/utilities

sub=$1
THICKDIR=$2
t1ashsseg=$3

pmmap=template_avg_density_cutoff_mild_Tau_tangles.nii.gz
pmfreq=template_avg_density_Tau_tangles.nii.gz

${utilities}/antsApplyTransforms -d 3 \
    -i ${utilities}/pmtau_files/$pmmap -r $THICKDIR/${sub}CorticalThickness.nii.gz \
    -t [$THICKDIR/${sub}SubjectToTemplate0GenericAffine.mat,1] \
    $THICKDIR/${sub}TemplateToSubject0Warp.nii.gz \
    ${utilities}/pmtau_files/abc_to_ADNINormal1Warp.nii.gz \
    ${utilities}/pmtau_files/abc_to_ADNINormal0GenericAffine.mat \
    -o $THICKDIR/${pmmap%.nii.gz}_to_t1.nii.gz
    
${utilities}/antsApplyTransforms -d 3 \
    -i $utilities/pmtau_files/$pmfreq -r $THICKDIR/${sub}CorticalThickness.nii.gz \
    -t [$THICKDIR/${sub}SubjectToTemplate0GenericAffine.mat,1] \
    $THICKDIR/${sub}TemplateToSubject0Warp.nii.gz \
    $utilities/pmtau_files/abc_to_ADNINormal1Warp.nii.gz \
    $utilities/pmtau_files/abc_to_ADNINormal0GenericAffine.mat \
    -o $THICKDIR/${pmfreq%.nii.gz}_to_t1.nii.gz
    
echo "$sub warping done"
OUTDIR=$THICKDIR

# Using ASHS segmentation, find the AH/PH boundary using distance map
MYSEG=$OUTDIR/ashsseg.nii.gz
c3d $THICKDIR/${sub}CorticalThickness.nii.gz \
    $t1ashsseg -interp NN -reslice-identity -o $MYSEG

#to determine -thresh values
voxels=($( c3d $MYSEG  -info | cut -f 3 -d ";" | sed -e "s/[a-zA-Z:,]//g" -e "s/\]//" -e "s/\[//" -e "s/=//" ))
orientation=($( c3d $MYSEG -info | cut -f 5 -d ";" | cut -f 2 -d "=" | sed 's/[A-Z]/ &/g;s/^ //'))
for ((i = 0 ; i < "${#orientation[@]}" ; i++)); do
    if [[ "${orientation[i]}" == "A" || "${orientation[i]}" == "P" ]]; then
        threshmin="${voxels[$i]}"
        threshmax="${threshmin}.2"
    fi
done

c3d $MYSEG -as A -thresh 1 1 1 0 -sdt -popas DISTA -push A -thresh 2 2 1 0 -sdt \
    -dup -times -sqrt -push DISTA -dup -times -sqrt  -add \
    -thresh $threshmin $threshmax 1 0 -o $OUTDIR/bndry.nii.gz -cmv -oo $OUTDIR/coordmap%d.nii.gz

pos=$( ${utilities}/findaxisdir $MYSEG cor | awk '{print $1}' )
dir=$( ${utilities}/findaxisdir $MYSEG cor | awk '{print $2}' )
bndry_centroid=$(c3d $OUTDIR/bndry.nii.gz -centroid | grep CENTROID_VOX | cut -f 2 -d "[" | cut -f 1 -d "]" | sed -e "s/ //g" | cut -f $pos -d , | awk '{printf("%.f\n",$0)}' )

zeropos=$(echo " $pos - 1 " | bc -l )
if [ "$dir" == "neg" ]; then
    c3d $OUTDIR/coordmap${zeropos}.nii.gz -thresh 0 $bndry_centroid 1 2 -o $OUTDIR/ap.nii.gz
else
    c3d $OUTDIR/coordmap${zeropos}.nii.gz -thresh 0 $bndry_centroid 2 1 -o $OUTDIR/ap.nii.gz
fi

rm -f $OUTDIR/coordmap?.nii.gz $OUTDIR/bndry.nii.gz
