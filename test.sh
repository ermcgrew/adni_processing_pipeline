#!/usr/bin/bash
Help()
{
   echo "Collect files to perform QC."
   echo "Syntax: collectQCfiles.sh [-|h|i|q|s|t]"
   echo "options:"
   echo "-i     Input file of sessions to QC, e.g. 'WBseg_todo_20221121.csv'."
   echo "-h     Print this help."
   echo "-q     QC type: 3TT1ASHS, 7TT2, 7TT2ASHS, Amy_MRI_reg, Tau_MRI_reg, WBSeg."
   echo "-s     Scan Type: MRI3T, MRI7T, TauPET, AmyloidPET."
   echo "-t     Testing mode: nothing executed, print files to be copied to stdout."
   echo
}

# Get the options
while getopts "hi:q:M:t" option; do
  case $option in
      h) # display Help
         Help
         exit;;
      i) 
         inputfile=$OPTARG;;    
      q) 
         qctype=$OPTARG;;
      M) 
         scantype=$OPTARG;;
      t) 
         testing=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

testvar=${@:$OPTIND:1}
echo $testvar
echo $qctype
echo $scantype
echo $inputfile


#$ bsub -M 4G -N ./test.sh -i WBseg_todo_20221121.csv -q 7TT2 -M MRI7T "testing positional arg"
# Job <19685597> is submitted to queue <bsc_normal>.
## don't use redirect arrow, makes flags interpreted as part of bsub command:
#$ bsub -M 4G -N < ./test.sh -i WBseg_todo_20221121.csv -q 7TT2 -M MRI7T "testing positional arg"
# $7TT2: No such queue. Job not submitted.