#!/usr/bin/bash

Help()
{
    echo "For use with ADNI files only."
    echo "Get commands to copy flair files to lambda-picsl for white matter hyperintensity analysis" 
    echo "and move output files back to bscid or copy output files to session folders."
    echo 
    echo "Options:"
    echo "-c     Copy output files to session folders."
    echo "-d     directory name in /project/wolk_2/ADNI2018/analysis_input/ that contains both data_for_inference/ and output_from_nnunet_inference/."
    echo "-g     Print commands to copy files and run docker container to the terminal"
    echo "-h     Print this help."
    echo "-u     Your bscsub/chead/lambda-picsl username."
    
    echo Example usages: 
    echo "bash wmh.sh -d 2023_04_03 -u emcgrew -g"
    echo "bash wmh.sh -d 2023_04_03 -c"
    }

Get_commands()
{
echo Printing commands for username $username and directory $directory.
echo "Format is @clustername:working/directory$"
echo "      command to copy and run"

echo "ONE"
echo "@scisub$"
echo "      scp -r $username@bscsub.pmacs.upenn.edu:/project/wolk_2/ADNI2018/analysis_input/$directory/data_for_inference $username@chead.uphs.upenn.edu:/home/$username"

echo "TWO"
echo "@lambda-picsl:/data/$username$"
echo "      scp -r $username@chead.uphs.upenn.edu:/home/$username/data_for_inference/ ." 

echo "THREE"
echo "@lambda-picsl$"
echo "      docker pull pulks/docker_hippogang_exvivo_segm:v1.3.0"

echo "FOUR"
echo "@lambda-picsl$"
echo "      docker run --gpus all --privileged -v /data/$username/:/data/exvivo/ -it pulks/docker_hippogang_exvivo_segm:v1.3.0 /bin/bash -c "bash /src/commands_nnunet_inference_WMH_invivo.sh" >> logs.txt"

echo "FIVE"
echo "@lambda-picsl:/data/$username/data_for_inference$"
echo "      scp -r ./output_from_nnunet_inference $username@chead.uphs.upenn.edu:/home/$username/"

echo "SIX"
echo "@chead:~$"
echo "      scp -r ./output_from_nnunet_inference $username@bscsub.pmacs.upenn.edu:/project/wolk_2/ADNI2018/analysis_input/$directory"
}


Copy_outputs(){
echo Copying WMH outputs from $directory directory to session folders

output_directory="/project/wolk_2/ADNI2018/analysis_input/$directory"
dataset="/project/wolk_2/ADNI2018/dataset"
for f in $output_directory/output_from_nnunet_inference/*.gz ; do
    filename=$(basename $f)
    id=$(echo $filename | cut -d '_' -f 2 )
    date=$(echo $filename | cut -d '_' -f 1 )

  if [[ -d ${dataset}/${id}/${date}/ ]] ; then
    echo copying file $f
    cp $f ${dataset}/${id}/${date}/${date}_${id}_wmh.nii.gz
  else
    echo folder for session $id/$date does not exist yet
  fi
done
}

# Get the options
while getopts "cd:hgu:" option; do
    case $option in
        h) # display Help
            Help
            exit;;
        d) 
            directory=$OPTARG;;
        u) 
            username=$OPTARG;;
        g) 
            Get_commands;;    
        c) 
            Copy_outputs;;
        \?) # Invalid option
            echo "Error: Invalid option"
            exit;;
    esac
done