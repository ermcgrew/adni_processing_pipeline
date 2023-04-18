#!/usr/bin/bash

ASHS_ROOT=$1
atlas=$2
t1trim=$3
t2link=$4
output_directory=$5
id=$6
z_opt=$7
m_opt=$8

export $ASHS_ROOT

#standard options
options="-a $atlas -g $t1trim -f $(readlink -f $t2link) \
          -w $output_directory -d -T  -I ${id}"

#addtional options for T1, T2 ASHS only (t2link == t1trim only for ICV)
if [[ $t2link != $t1trim ]] ; then 
    options="$options -l -s 1-7 -z $z_opt -m $m_opt -M"
fi

#additional option for T2 ASHS only
if [[ $t2link =~ "T2w" ]] ; then 
    options="$options -B"
fi

#run ASHS
echo $ASHS_ROOT/bin/ashs_main.sh $options
          
#Remove intermediate files
# rm -rf $output_directory/multiatlas $output_directory/bootstrap $output_directory/*raw.nii.gz



: '
Options:

for T1, T2, and ICV:
-a atlas
-w {self.filepath}/ASHSICV // /sfsegnibtend // /ASHST1
-g {self.t1trim}
-f {self.superres}/{self.t1trim}/{self.t2nifti}
-d
-T
-I {self.id}

T1, T2 only:
-l  (Use LSF instead of SGE, SLURM or GNU parallel)
-s 1-7 (Run only one stage (see below); also accepts range (e.g. -s 1-3)--there are 7 stages total?)
-z {long_scripts}/ashs-fast-z.sh (Provide a path to an executable script that will be used to retrieve SGE, LSF, SLURM or
                    GNU parallel options for different stages of ASHS.)
-m {long_scripts}/identity.mat  (Provide the .mat file for the transform between the T1w and T2w image.)
-M (The mat file provided with -m is used as the final T2/T1 registration.
                    ASHS will not attempt to run registration between T2 and T2.)

T2 only: 
-B (Do not perform the bootstrapping step, and use the output of the initial joint
                    label fusion (in multiatlas directory) as the final output.)


example usage (ICV): 
bash wrapper_scripts/run_ashs.sh \
/project/hippogang_2/longxie/pkg/ashs/ashs-fast \
/home/lxie/ASHS_atlases/ICVatlas_3TT1 \
/project/wolk_2/ADNI2018/scripts/pipeline_test_data/114_S_6917/2021-04-16/2021-04-16_114_S_6917_T1w_trim.nii.gz \
/project/wolk_2/ADNI2018/scripts/pipeline_test_data/114_S_6917/2021-04-16/2021-04-16_114_S_6917_T1w_trim.nii.gz \
/project/wolk_2/ADNI2018/scripts/pipeline_test_data/114_S_6917/2021-04-16/ASHSICV \
114_S_6917 \
/home/lxie/ADNI2018/scripts/ashs-fast-z.sh \
/home/lxie/ADNI2018/scripts/identity.mat 
'