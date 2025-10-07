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

### Make tmpdir to run ashs in
tmpdir=$( mktemp -d --tmpdir=/scratch )
echo $tmpdir

## standard options
options="-a $atlas -g $t1trim -f $(readlink -f $t2link) \
          -w $tmpdir -T -d -I ${id}"

### for T2 ASHS only
if [[ $t2link =~ "T2w" ]] ; then 
    ##symlink this run data to SDROOT where all T2 runs are stored
    mridate=$( echo $output_directory | rev | cut -d "/" -f 2 | rev)
    link_loc=/project/hippogang_1/srdas/wd/ADNI23/${id}/${mridate}/sfsegnibtend
    if [[ ! -h $link_loc ]] ; then 
        ln -sf $output_directory $link_loc
    fi
else
  #addtional options for T1, ICV ASHS only
  options="$options -m $m_opt -M"
fi

#For ICV ASHS only
if [[ $t2link == $t1trim ]] ; then 
    options="$options -B"
fi

#run ASHS
$ASHS_ROOT/bin/ashs_main.sh $options
          
echo Here are the files in the tmpdir: 
ls -l $tmpdir
echo More extensive: 
tree $tmpdir

#Make ASHST1/ASHSICV/sfsegnibtend directory in session folder
if [[ ! -d $output_directory ]] ; then 
    mkdir -p $output_directory
fi

### Copy result files out of the tmp dir
## always copy log files
cp -r $tmpdir/dump $output_directory

### if success -- check for segmentation file we use for stats in /final
if [[ -f $tmpdir/final/${id}_left_lfseg_heur.nii.gz ]] ; then 

    ## symlink inputs 
    ln -s $t1trim $output_directory/mprage.nii.gz
    ln -s $t2link $output_directory/tse.nii.gz

    ## for T1 ASHS
    if [[ $t2link =~ "denoised_SR" ]] ; then 
        mkdir -p $output_directory/affine_t1_to_template $output_directory/bootstrap/fusion/ $output_directory/final
        cp $tmpdir/affine_t1_to_template/*.mat $output_directory/affine_t1_to_template
        cp $tmpdir/bootstrap/fusion/posterior* $output_directory/bootstrap/fusion
        cp $tmpdir/final/${id}_[lr]* $output_directory/final
        ### all files in /final except icv.txt

        cp -r $tmpdir/flirt_t2_to_t1 $tmpdir/qa $tmpdir/tse_native_chunk_* $output_directory
    
    ## for T2 ASHS 
    elif [[ $t2link =~ "T2w" ]] ; then
        mkdir -p $output_directory/affine_t1_to_template $output_directory/final
        cp $tmpdir/affine_t1_to_template/*.mat $output_directory/affine_t1_to_template
        cp $tmpdir/final/${id}_[lr]* $output_directory/final
        ### all files in /final except icv.txt

        cp -r $tmpdir/bootstrap $tmpdir/flirt_t2_to_t1 $tmpdir/multiatlas $tmpdir/qa $output_directory
    
    ## for ICV ASHS 
    elif [[ $t2link == $t1trim ]] ; then 
        cp -r $tmpdir/final $tmpdir/qa $output_directory
    
    fi 
fi 

### remove tmpdir
rm -rf $tmpdir


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
#     - Modules must be in order: unload matlab, load ImageMagick to resolve LibTiff version error that prevents
#          creation of qa pngs. 
#     - removed -z {long_scripts}/ashs-fast-z.sh (Provide a path to an executable script that 
#           will be used to retrieve SGE, LSF, SLURM or GNU parallel opts for different stages of ASHS.)
#           -z ashs fast is deprecated in newer versions of ashs
#     - removed -l (Use LSF instead of SGE, SLURM or GNU parallel)
#           separating jobs prevents transer of module unload/load, leading to LibTiff version error still.
      
# ************UPDATE 10/7/2025************
#   -Instead of removing unneeded files, ASHS script outputs to tmp dir
#    and only necessary files are copied to final dataset directory.
