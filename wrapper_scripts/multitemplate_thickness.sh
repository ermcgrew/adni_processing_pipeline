#!/usr/bin/bash
## Usage: multitemplate_thickness.sh subjectID mridate ASHS_segmentation_heur_left ASHS_segmentation_heur_right output_directory
## adapted from /home/lxie/ADNI2018/scripts/RunT1BaselineLongitudinal_09092022.sh

id=$1
mridate=$2
ashs_seg_left=$3
ashs_seg_right=$4
OUTDIR=$5

# load modules
module load matlab
module load vtk/7.1.1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/project/hippogang_2/pauly/icclibs:/project/hippogang_2/pauly/lib

for side in left right ; do 
    if [[ $side == 'left' ]] ; then 
        OUTCSV=$OUTDIR/${id}_${mridate}_${side}_thickness.csv
        ASHSSEG=$ashs_seg_left
        logfile=$OUTDIR/${id}_${mridate}_${side}_log.txt
    else 
        OUTCSV=$OUTDIR/${id}_${mridate}_${side}_thickness.csv
        ASHSSEG=$ashs_seg_right
        logfile=$OUTDIR/${id}_${mridate}_${side}_log.txt
    fi

    if [[ ! -f $OUTCSV ]]; then

        if [[ ! -d $OUTDIR ]] ; then 
            mkdir -p $OUTDIR
        fi
        
        echo "$id,$side,$ASHSSEG" > $logfile

        /home/lxie/ASHS_T1/pipeline_package/MultiTempThkMTLWithHippo/runpipeline_MultiAndUnifiTemplate_single.sh \
            ${id}_${mridate} $ASHSSEG $side $OUTDIR >> $logfile

        echo $TMPDIR
        rm -rf $TMPDIR
    fi
done