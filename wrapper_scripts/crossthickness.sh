#!/bin/bash
# copy of /project/hippogang_1/srdas/wd/TAUPET/longnew/crossthickness.sh

ROOT=/project/wolk_1/ADNI_longitudinal-Templates

export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=1
export ANTSPATH=$ROOT/ants_nov2017/

SUB=$1
FN=$2
OUTDIR=$3

$ROOT/ants_nov2017/antsCorticalThickness.sh \
   -d 3 \
   -o $OUTDIR/$SUB \
   -g 1 \
   -t $ROOT/Normal/T_template0_BrainCerebellum.nii.gz \
   -e $ROOT/Normal/T_template0.nii.gz \
   -m $ROOT/Normal/T_template0_BrainCerebellumProbabilityMask.nii.gz \
   -f $ROOT/Normal/T_template0_BrainCerebellumExtractionMask.nii.gz \
   -p $ROOT/Normal/Priors/priors%d.nii.gz \
   -q 0 \
   -a $FN

rm -f "$OUTDIR/${SUB}SubjectToTemplateLogJacobian.nii.gz"