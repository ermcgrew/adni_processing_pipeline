#!/usr/bin/bash

ashs_root=$1
atlas=$2
t1trim=$3
t2link=$4
output_directory=$5
id=$6
m_opt=$7

export ASHS_ROOT=$ashs_root
##Modules must unload/load in this order to prevent LIBTIFF version error
module unload matlab/2023a 
module load ImageMagick

#Make ASHST1/ASHSICV/sfsegnibtend directory in session folder
if [[ ! -d $output_directory ]] ; then 
    mkdir -p $output_directory
fi

#standard options
options="-a $atlas -g $t1trim -f $(readlink -f $t2link) \
          -w $output_directory -T -d -I ${id}"

if [[ $t2link =~ "T2w" || $t2link =~ "tse" ]] ; then 
  echo t2 options
   options=$options
else
  #addtional options for T1, ICV ASHS only
  echo t1 and icv options only
  options="$options -m $m_opt -M"
fi

#For ICV ASHS only
if [[ $t2link == $t1trim ]] ; then 
    options="$options -B"
fi

#run ASHS
$ASHS_ROOT/bin/ashs_main.sh $options
          
#Remove intermediate files
rm -rf $output_directory/*raw.nii.gz
##keep bootstrap and multiatlas for ADNI T2 $output_directory/multiatlas $output_directory/bootstrap


# Options:
# for T1, T2, and ICV:
# -a atlas
# -w {self.filepath}/ASHST1 // /sfsegnibtend // /ASHSICV
# -g {self.t1trim}
# -f {self.superres}/{self.t2nifti}/{self.t1trim}
# -T
# -I {self.id}

# T1, ICV only:
# -m {long_scripts}/identity.mat  (Provide the .mat file for the transform between the T1w and T2w image.)
# -M (The mat file provided with -m is used as the final T2/T1 registration.
#                     ASHS will not attempt to run registration between T2 and T2.)

# ICV only: 
# -B (Do not perform the bootstrapping step, and use the output of the initial joint
#                     label fusion (in multiatlas directory) as the final output.)


# ************UPDATE 7/4/2023 & 11/6/2023************
#     - removed -s 1-7 opt: unnecessary, default runs all 7 steps
#     - removed -d opt: debugging log unnecessary
#
#     - Modules must be in order: unload matlab, load ImageMagick to resolve LibTiff version error that prevents
#          creation of qa pngs. 
#     - removed -z {long_scripts}/ashs-fast-z.sh (Provide a path to an executable script that 
#           will be used to retrieve SGE, LSF, SLURM or GNU parallel opts for different stages of ASHS.)
#           -z ashs fast is deprecated in newer versions of ashs
#     - removed -l (Use LSF instead of SGE, SLURM or GNU parallel)
#           separating jobs prevents transer of module unload/load, leading to LibTiff version error still.
      