#!/usr/bin/bash
#Usage: multitemplate_thickness.sh subjectID scanDate side ASHS_segmentation_heur output_directory
#adapted from /home/lxie/ADNI2018/scripts/RunT1BaselineLongitudinal_09092022.sh

id=$1
PREFIX=$2
side=$3
AUTOSEG=$4
OUTDIR=$5
OUTCSV=$OUTDIR/${id}_${PREFIX}_${side}_thickness.csv
echo "$id,$side,$AUTOSEG" > $OUTDIR/${id}_${PREFIX}_${side}_log.txt

# load VTK module
module load matlab
module load vtk/7.1.1

if [[ ! -f $OUTCSV ]]; then
mkdir -p $OUTDIR
/home/lxie/ASHS_T1/pipeline_package/MultiTempThkMTLWithHippo/runpipeline_MultiAndUnifiTemplate_single.sh \
    ${id}_${PREFIX} $AUTOSEG $side $OUTDIR >> $OUTDIR/${id}_${PREFIX}_${side}_log.txt
rm -rf $TMPDIR
fi