#!/usr/bin/bash

module load ImageMagick
module unload matlab/2023a 

function run_ashs()
{
    ashs_root=$1
    atlas=$2
    t1trim=$3
    t2link=$4
    output_directory=$5
    id=$6
    m_opt=$7
    export ASHS_ROOT=$ashs_root

    if [[ ! -d $output_directory ]] ; then 
        mkdir -p $output_directory
    fi

    #standard options
    options="-a $atlas -g $t1trim -f $(readlink -f $t2link) \
            -w $output_directory -T -I ${id}\
            -N -t 1"

    #addtional options for T1, ICV ASHS only
    if [[ $t2link =~ "T2w" ]] ; then 
        continue
    else
        options="$options -m $m_opt -M"
    fi

    #For ICV ASHS only
    if [[ $t2link == $t1trim ]] ; then 
        options="$options -B"
    fi

    #run ASHS
    $ASHS_ROOT/bin/ashs_main.sh $options

    #Remove intermediate files
    rm -rf $output_directory/multiatlas $output_directory/bootstrap $output_directory/*raw.nii.gz
}

# Run command passed in
if [[ ! $NOCMD ]]; then
    CMD=${1?}
    shift
    $CMD "$@"
fi




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


# ************UPDATE 7/4/2023************
#     - removed -z opt: updates to bsc cluster means that z opt will keep ashs_main 
#                         from creating all required QC pngs.
#         -z {long_scripts}/ashs-fast-z.sh (Provide a path to an executable script that 
#                                             will be used to retrieve SGE, LSF, SLURM or
#                                             GNU parallel opts for different stages of ASHS.)
#     - removed -s 1-7 opt: unnecessary, default runs all 7 steps
#     - removed -d opt: debugging log unnecessary
#     - removed -l opt:    
#         -l  (Use LSF instead of SGE, SLURM or GNU parallel)
#     - added -t 1 and -N opts: per Pauls working script
#     - moved ashs call into function: per Pauls working script
