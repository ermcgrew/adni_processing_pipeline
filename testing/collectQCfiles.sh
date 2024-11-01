#!/usr/bin/bash

# Display Help
Help()
{
   echo "Collect files to perform QC."
   echo "Syntax: collectQCfiles.sh [-|h|i|q|s]"
   echo "options:"
   echo "-i     Required. Input file of sessions to QC, e.g. 'WBseg_todo_20221121.csv'."
   echo "-h     Print this help."
   echo "-q     Required. QC type: 3TT1, 3TT2, Amy_MRI_reg, Tau_MRI_reg, WBSeg."
   echo "-s     Required. Scan Type: MRI3T, TauPET, AmyloidPET."
   echo
   echo "Usage example: "
   echo "bash collectQCfiles.sh -i ABC_3T_T1_noQC_20230306.csv -q 3TT1 -s MRI3T"
}

# Get the options
while getopts "hi:q:s:" option; do
  case $option in
      h) # display Help
         Help
         exit;;
      i) 
         inputfile=$OPTARG ;;    
      q) 
         qctype=$OPTARG ;;
      s) 
         scantype=$OPTARG ;;
      
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

echo "Reading sessions from file: $inputfile"

#static variables
qcroot="/project/wolk/ADNI2018/dataset/QC"
currentdate=`date +%Y%m%d`
filename="${qctype}_${currentdate}_QCtodo"
ratings_file=${qcroot}/${qctype}/${currentdate}/${filename}_ratings.csv
dir_for_pngs=${qcroot}/${qctype}/${currentdate}/${filename}_images

#make directories for copied QC images
if [[ ! -d $dir_for_pngs ]] ; then 
   mkdir -p $dir_for_pngs
   touch $ratings_file
fi

#read csv, copy files according to QC type
cat $inputfile |  while read line; do
   id=$(echo $line | cut -f 2 -d , )  
   scandate=$(echo $line | cut -f 3 -d , )

   sessionfilepath=/project/wolk/ADNI2018/dataset/$id/$scandate

   if [[ $qctype == "3TT1" ]] ; then 
      if [[ $id == "ID" ]] ; then 
         echo ID,SCANDATE,QC_MRI,QC_ICV,QC_LMTL_ASHST1_3T,\
         QC_RMTL_ASHST1_3T,QC_COMMENTS >> $ratings_file
         mkdir $dir_for_pngs/ICV
         mkdir $dir_for_pngs/ASHS
      else 
         if [[ -d "$sessionfilepath/sfsegnibtend" ]] ; then

            mkdir $dir_for_pngs/ASHS/${id}_${scandate}
            echo $id,$scandate >> $ratings_file 
            cp $sessionfilepath/${scandate}_${id}_T1w.nii.gz \
               $sessionfilepath/ASHST1/final/${id}_left_lfseg_corr_nogray.nii.gz \
               $sessionfilepath/ASHST1/final/${id}_right_lfseg_corr_nogray.nii.gz \
               $sessionfilepath/ASHST1/qa/qa_seg_bootstrap_corr_nogray_left_qa.png \
               $sessionfilepath/ASHST1/qa/qa_seg_bootstrap_corr_nogray_right_qa.png \
               $dir_for_pngs/ASHS/${id}_${scandate}         
            cp $sessionfilepath/ASHSICV/qa/qa_seg_multiatlas_corr_nogray_left_qa.png \
               $dir_for_pngs/ICV/${id}_${scandate}_icv_corr_nogray_left_qa.png  
         else
            echo $id,$scandate does not have ASHST1 folder
         fi
      fi

   elif [[ $qctype == "3TT2" ]] ; then
      if [[ $id == "ID" ]] ; then 
         echo ID,SCANDATE,T2_QC_L,T2_QC_R,T2_QC_COMMENT,\
         L_Seg_ASHST2_3T,L_QC_COMMENT_ASHST2_3T,R_Seg_ASHST2_3T,R_QC_COMMENT_ASHST2_3T >> $ratings_file
      else 
         if [[ -d "$sessionfilepath/sfsegnibtend" ]] ; then
            echo $id,$scandate >> $ratings_file  
            mkdir $dir_for_pngs/${id}_${scandate}
            cp $sessionfilepath/${scandate}_${id}_T2w.nii.gz \
               $sessionfilepath/sfsegnibtend/final/${id}_left_lfseg_corr_nogray.nii.gz \
               $sessionfilepath/sfsegnibtend/final/${id}_right_lfseg_corr_nogray.nii.gz \
               $sessionfilepath/sfsegnibtend/qa/qa_seg_bootstrap_corr_nogray_left_qa.png \
               $sessionfilepath/sfsegnibtend/qa/qa_seg_bootstrap_corr_nogray_right_qa.png \
               $dir_for_pngs/${id}_${scandate}
         else
            echo $id,$scandate does not have ASHST2Prisma folder
         fi
      fi         

   elif [[ $qctype == "WBSeg" ]] ; then 
      if [[ $id == "ID" ]] ; then 
         echo ID,SCANDATE,QUALITY,COMMENTS >> $ratings_file
      else
         output=$sessionfilepath/${scandate}_${id}_wbseg_qa.png
         if [[ -f $output ]] ; then
            cp $output $dir_for_pngs
            echo $id,$scandate >> $ratings_file
         else
            echo $id,$scandate,nofile >> $ratings_file
         fi
      fi
   elif [[ $qctype == *"_MRI_reg" ]] ; then  
      if [[ $id == "ID" ]] ; then 
         echo ID,PETDATE,MRIDATE,QUALITY,COMMENTS >> $ratings_file
      else
         mridate=$scandate
         petdate=$(echo $line | cut -f 2 -d , ) ##check which column

         sessionfilepath=/project/wolk/Prisma3T/relong/$id/$scantype/$petdate/processed

         if [[ $qctype == "Amy_MRI_reg" ]] ; then 
            qcpng=$sessionfilepath/${petdate}_${id}_amypet6mm_to_${mridate}_T1_qa.png
         elif [[ $qctype == "Tau_MRI_reg" ]] ; then 
            qcpng=$sessionfilepath/${petdate}_${id}_taupet6mm_to_${mridate}_T1_qa.png
         fi

         if [[ ! -f $qcpng ]] ; then
            echo no qc image found for $sessionfilepath
         else 
            cp $qcpng $dir_for_pngs/$copied_name
            echo $id,$petdate,$mridate >> $ratings_file
         fi
      fi 
   fi
done 

echo zip -r ${filename}.zip $filename