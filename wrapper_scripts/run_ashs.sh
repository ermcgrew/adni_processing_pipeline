#!/usr/bin/bash

ashs_root=$1
atlas=$2
t1trim=$3
t2link=$4
output_directory=$5
id=$6
z_opt=$7
m_opt=$8

export ASHS_ROOT=$ashs_root
module load ImageMagick
module unload matlab/2023a 

#standard options
options="-a $atlas -g $t1trim -f $(readlink -f $t2link) \
          -w $output_directory -d -T -I ${id}"

#addtional options for T1, ICV ASHS only
if [[ $t2link =~ "T2w" ]] ; then 
    echo "skip t2"
else
    options="$options -l -s 1-7 -z $z_opt -m $m_opt -M"
fi

#For ICV ASHS only
if [[ $t2link == $t1trim ]] ; then 
    options="$options -B"
fi

#run ASHS
$ASHS_ROOT/bin/ashs_main.sh $options
          
#Remove intermediate files
rm -rf $output_directory/multiatlas $output_directory/bootstrap $output_directory/*raw.nii.gz



: '
Options:

for T1, T2, and ICV:
-a atlas
-w {self.filepath}/ASHST1 // /sfsegnibtend // /ASHSICV
-g {self.t1trim}
-f {self.superres}/{self.t2nifti}/{self.t1trim}
-d
-T
-I {self.id}

T1, ICV only:
-l  (Use LSF instead of SGE, SLURM or GNU parallel)
-s 1-7 (Run only one stage (see below); also accepts range (e.g. -s 1-3)--there are 7 stages total?)
-z {long_scripts}/ashs-fast-z.sh (Provide a path to an executable script that will be used to retrieve SGE, LSF, SLURM or
                    GNU parallel options for different stages of ASHS.)
-m {long_scripts}/identity.mat  (Provide the .mat file for the transform between the T1w and T2w image.)
-M (The mat file provided with -m is used as the final T2/T1 registration.
                    ASHS will not attempt to run registration between T2 and T2.)

ICV only: 
-B (Do not perform the bootstrapping step, and use the output of the initial joint
                    label fusion (in multiatlas directory) as the final output.)

'