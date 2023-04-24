#!/usr/bin/bash
# #Usage: multitemplate_thickness.sh subjectID scanDate side ASHS_segmentation_heur output_directory
# #adapted from /home/lxie/ADNI2018/scripts/RunT1BaselineLongitudinal_09092022.sh

# id=$1
# date=$2
# side=$3
# seg=$4
# output_directory=$5

# module load matlab
# module load vtk/7.1.1

# mkdir -p $output_directory
# /home/lxie/ASHS_T1/pipeline_package/MultiTempThkMTLWithHippo/runpipeline_MultiAndUnifiTemplate_single.sh \
#     ${id}_${date} $seg $side $output_directory 

# rm -rf $output_directory/data $output_directory/RegToAtlases $output_directory/RegToInitTemp $output_directory/RegToUT



id=$1
PREFIX=$2
side=$3
AUTOSEG=$4
OUTDIR=$5
OUTCSV=$OUTDIR/${id}_${PREFIX}_${side}_thickness.csv
echo "$id,$side,$AUTOSEG" > $OUTDIR/${id}_${PREFIX}_${side}_log.txt

# load module
module load matlab
module load vtk/7.1.1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/project/hippogang_2/pauly/icclibs

if [[ ! -f $OUTCSV ]]; then
mkdir -p $OUTDIR
/home/lxie/ASHS_T1/pipeline_package/MultiTempThkMTLWithHippo/runpipeline_MultiAndUnifiTemplate_single.sh \
    ${id}_${PREFIX} $AUTOSEG $side $OUTDIR >> $OUTDIR/${id}_${PREFIX}_${side}_log.txt
rm -rf $TMPDIR
fi