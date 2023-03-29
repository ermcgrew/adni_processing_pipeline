#!/bin/bash
#$ -S /bin/bash
# Usage: brainx.sh $FILE
## code originally from /project/hippogang_1/srdas/wd/TAUPET/longnew/brainx_phil.sh

FILE=$1
TEMPLATE_DIR=/project/hippogang_1/srdas/keep/pennTemplate
export ANTSPATH=/project/wolk_1/ADNI_longitudinal-Templates/ants/
# need to export this var for the t1BrainExtraction.sh script to run

/project/hippogang_1/srdas/homebin/altAntsBrainExtraction/t1BrainExtraction.sh \
   -a $FILE \
   -t ${TEMPLATE_DIR}/template.nii.gz \
   -m ${TEMPLATE_DIR}/templateBrainMask.nii.gz \
   -r ${TEMPLATE_DIR}/templateBrainExtractionRegistrationMask.nii.gz \
   -l 1 \
   -o ${FILE%.nii.gz}_brainx_
