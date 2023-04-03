#!/usr/bin/bash


#Usage:
## -c flag and enter username, current date to print out commands for copying files to lambda-picsl
    #and running docker container

# -m flag and enter current date to copy wmh files to correct session folders

'''
@scisub$$ 
    scp -r <username>@bscsub.pmacs.upenn.edu:/project/wolk_2/ADNI2018/analysis_input/{current_date}_wmh_input/ \
    <username>@chead.uphs.upenn.edu:/home/<username>

@lambda-picsl:/data/<username>$$
    scp -r <username>@chead.uphs.upenn.edu:/home/<username>/{current_date}_wmh_input/ . 

@lambda-picsl$$
    docker pull pulks/docker_hippogang_exvivo_segm:v1.3.0

@lambda-picsl$$
    docker run --gpus all --privileged -v /data/<username>/:/data/exvivo/ \
    -it pulks/docker_hippogang_exvivo_segm:v1.3.0 \
    /bin/bash -c "bash /src/commands_nnunet_inference_WMH_invivo.sh" >> logs.txt

@lambda-picsl:/data/<username>/data_for_inference$$
    scp -r ./output_from_nnunet_inference <username>@chead.uphs.upenn.edu:/home/<username>/

@chead:~$$
    scp -r ./output_from_nnunet_inference \
    <username>@bscsub.pmacs.upenn.edu:/project/wolk_2/ADNI2018/analysis_input/


'''




#move files produced from docker container on lambda to correct session folders
output_directory="/project/wolk_2/ADNI2018/analysis_input/{current_date}"
dataset="/project/wolk_2/ADNI2018/dataset"
for f in $output_directory/output_from_nnunet_inference/*.gz ; do
    filename=$(basename $f)
    ##check file names to make sure cut gets correct field
    sub=$(echo $filename | cut -d '_' -f 2 )
    date=$(echo $filename | cut -d '_' -f 1 )
  fi

  if [[ -d ${dataset}/${sub}/${date}/ ]] ; then
    echo copying file $f
    cp $f ${dataset}/${sub}/${date}/${date}_${sub}_wmh.nii.gz
  else
    echo folder for session $sub/$date does not exist yet
  fi
done