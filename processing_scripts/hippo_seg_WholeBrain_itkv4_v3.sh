#!/bin/bash -x
#$ -S /bin/bash

inputDir=$1   ## the folder holding the image to be segmented  
outputDir=$2  ## have to be the absolute path. E.g. /home/hang3/test instead of ~/test
filename=$3   ## file name with out the extension. E.g. for xyz.nii.gz, filename=xyz
##MOD=$4        ## 1.5T or 3T 
AtlasRoot=$4  ## define the folder that holds the atlases. The path has to be absolute path. There should be ascii file named "subjects" in the folder.
              ## This file contains all subject names of the atlas. For example, if "subject1" is shown in this list, then the atlas image should be 
              ## named as $AtlasRoot/subject1.nii.gz in the folder and the atlas segmentation should be named as $AtlasRoot/subject1_seg.nii.gz
              ## 1.5T hippocampus atlas  /home/hwang3/ahead_joint/turnkey/data/1_5T
              ## 3T hippocampus atlas    /home/hwang3/ahead_joint/turnkey/data/3T
              ## Whole brain atlas       /home/hwang3/ahead_joint/turnkey/data/WholeBrain

sequential=$5 ## whether 1 for running the jobs sequentially or 0 for submitting the jobs to a cluster

## Set the number of cores for the registration job
if [[ -z "$6" ]]; then
    Registration_CPU=2
else
    Registration_CPU=$6
fi

## Set the number of cores for the label job
if [[ -z "$7" ]]; then
    LabelFusion_CPU=2
else
    LabelFusion_CPU=$7
fi

echo "Registration_CPU: "$Registration_CPU
echo "LabelFusion_CPU: "$LabelFusion_CPU

## an example 
## /home/hwang3/ahead_joint/turnkey/bin/hippo_seg.sh /mnt/data/PUBLIC/atrophychallenge/190/190_B /home/hwang3/atrophy/190 190_B 01 1.5T

if [ ! -f $outputDir ]; then
    mkdir $outputDir
fi

workDir=$outputDir/$filename
if [ ! -f $workDir ]; then
    mkdir $workDir
fi
cp $inputDir/$filename.nii.gz $workDir/.


if [[ ! $TMPDIR ]]; then
	if [ -d /scratch ]; then
		export TMPDIR=/scratch
	else
		export TMPDIR=/tmp
	fi
fi

regDir=$workDir/registration
regDir=$(mktemp -d $TMPDIR/ahead.XXXXXXXXXXX)
if [ ! -f $regDir ]; then
    mkdir $regDir
fi
cp $inputDir/$filename.nii.gz $regDir/.
##ImageMath 3 $regDir/${filename}_grad.nii.gz Grad $regDir/$filename.nii.gz

DUMP=$workDir/dump
mkdir $DUMP

ROOT=/home/sudas/bin/ahead_joint/turnkey

export ROOT

BIN_ANTS=$ROOT/ext/Linux/bin/ants
export PATH=$PATH:/home/sudas/bin


if [[ $MOD == "3T" ]]; then
    TIDs=`cat $ROOT/data/ADNI3T/subjects`
    name=3T_hipposeg
fi
if [[ $MOD == "1.5T" ]]; then
    TIDs=`cat $ROOT/data/ADNI1_5T/subjects`
    name=15T_hipposeg
fi

if [[ ! $AtlasRoot == "" ]]; then
    TIDs=`cat $AtlasRoot/subjects`
    name=wholebrainseg
fi

##TIDs=

echo $TIDs
jobIDs=""
ref_id=$filename
for mov_id in $TIDs; do
    if [[ $mov_id == $ref_id ]]; then
            continue;
    fi
    if [ ! -f $regDir/${mov_id}_To_${ref_id} ]; then
        mkdir $regDir/${mov_id}_To_${ref_id}
    fi
    check=`ls $regDir/${mov_id}_To_${ref_id}/*reconstructed_seg.nii.gz`
    if [[ $check != '' ]]; then
         echo $check 'has been processed!';
         continue;
    fi
    echo $ref_id $mov_id
    if [[ $sequential == 0 ]]; then

	 # SGE 
         # id=`qsub -o $DUMP -e $DUMP -cwd -N "register_${mov_id}_To_${ref_id}" -pe serial $Registration_CPU -l h_stack=64M,h_vmem=10.1G,s_vmem=10G -V $ROOT/bin/registerPairsWholeBrain_itkv4_v3.sh $regDir $ref_id $mov_id $AtlasRoot | awk '{print $3}'`
	 # Flexible: can work with LSF/SLURM/SGE
         id=`pybatch -o $DUMP -N "register_${mov_id}_To_${ref_id}" -m 12G $ROOT/bin/registerPairsWholeBrain_itkv4_v3.sh $regDir $ref_id $mov_id $AtlasRoot | awk '{print $2}' | sed -e "s/<//g" | sed -e "s/>//g"`
         # id=`qsub -p -1 -o $DUMP -e $DUMP -cwd -N "register_${mov_id}_To_${ref_id}" -pe serial $Registration_CPU -l h_stack=64M,h_vmem=10.1G,s_vmem=10G -V $ROOT/bin/registerPairsWholeBrain_itkv4_v3.sh $regDir $ref_id $mov_id $AtlasRoot | awk '{print $3}'`
         jobIDs="$jobIDs $id"
         sleep 0.01
    fi
    if [[ $sequential == 1 ]]; then
         $ROOT/bin/registerPairsWholeBrain_itkv4_v3.sh $regDir $ref_id $mov_id $MOD $AtlasRoot
    fi
done
if [[ $sequential == 0 ]]; then
    # SGE
    # $BIN_ANTS/waitForSGEQJobs.pl 1 60 $jobIDs
    # Flexible: can work with LSF/SLURM/SGE
    pybatch -N "waitma" -o $DUMP -w "register_*_To_*" 
fi

export ROOT
##exit

R=2
SR=3
sig=2
lamda=0.1
jobIDs=""
ID=$filename
echo $DUMP
if [[ $sequential == 0 ]]; then
    # SGE 
    # id=`qsub -S /bin/bash  -N lf_${ID} -e $DUMP -o $DUMP -pe serial $LabelFusion_CPU -l h_stack=128M,h_vmem=10.1G,s_vmem=10G  $ROOT/bin/label_fusion_qsub_v3.sh $workDir $ref_id $R $SR $sig $lamda $name | awk '{print $3}'`
    # id=`qsub -S /bin/bash  -p -0 -N lf_${ID} -e $DUMP -o $DUMP -pe serial $LabelFusion_CPU -l h_stack=128M,h_vmem=10.1G,s_vmem=10G  $ROOT/bin/label_fusion_qsub_v3.sh $workDir $ref_id $R $SR $sig $lamda $name | awk '{print $3}'`
    # jobIDs="$jobIDs $id"
    # $BIN_ANTS/waitForSGEQJobs.pl 1 60 $jobIDs
    # Flexible: can work with LSF/SLURM/SGE
    id=`pybatch -o $DUMP -N "lf_${ID}" -m 12G  $ROOT/bin/label_fusion_qsub_v3.sh $workDir $ref_id $R $SR $sig $lamda $name $regDir | awk '{print $2}' | sed -e "s/<//g" | sed -e "s/>//g"`
    sleep 0.1
    pybatch -N "waitlf" -o $DUMP -w "lf_*" 
fi

if [[ $sequential == 1 ]]; then
    $ROOT/bin/label_fusion_qsub_v3.sh $workDir $ref_id $R $SR $sig $lamda $name $regDir
fi

 rm $workDir/${ID}.nii.gz
 rm -r $regDir


