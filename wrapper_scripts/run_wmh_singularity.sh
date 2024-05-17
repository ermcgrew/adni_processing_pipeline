#!/usr/bin/bash

data_input_folder=$1

module load singularity
SINGULARITYENV_TMPDIR=/tmp
singularity run --writable -B ${data_input_folder}/:/data/exvivo/ /project/wolk/ADNI2018/scripts/wmh_seg/ bash /src/commands_nnunet_inference_WMH_invivo.sh

echo
echo
echo linking WMH outputs to session folders
output_directory="${data_input_folder}/data_for_inference/output_from_nnunet_inference"
dataset="/project/wolk/ADNI2018/dataset"

for f in $output_directory/*.gz ; do
  filename=$(basename $f)
  id=$(echo $filename | cut -d '_' -f 2-4 )  
  date=$(echo $filename | cut -d '_' -f 1 )
  dataset_file="${dataset}/${id}/${date}/${filename}"

  if [[ ! -f $dataset_file ]] ; then
    echo linking file $f
    ln -s $f $dataset_file
  else
    echo file $dataset_file already exists
  fi
done

