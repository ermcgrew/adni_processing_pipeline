#!/usr/bin/bash 
### copied from Phil's script /project/picsl/cookpa/antsctAgingLongTest/run_subject.sh

export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=${LSB_DJOB_NUMPROC}

container=/project/picsl/cookpa/antsct-aging/antsct-aging-0.5.1.sif

if [[ $# -eq 0 ]]; then
  echo "$0 <output_dir> <t1w> ... <t1w>"
  exit 1
fi

# module load singularity/3.8.3
module load apptainer

outputDir=$(readlink -f $1)
shift

if [[ ! -d $outputDir ]] ; then
  mkdir -p ${outputDir}
fi

# When passed from app.py, file names are in one string argument, space-separated, 
# which are file names we want to pass to the container
t1w_images=($1) 

# Convert these to absolute paths
for i in ${!t1w_images[@]}; do
  t1w_images[$i]=$(readlink -e ${t1w_images[$i]})
done

# CSV list of input for mounting to container
t1w_csv=$(IFS=,; echo "${t1w_images[*]}")

tmpDir=$(mktemp -d -p /scratch antsct-aging-long.${LSB_JOBID}.XXXXXX.tmpdir)

# export SINGULARITYENV_TMPDIR=/tmp
export APPTAINERENV_TMPDIR=/tmp

singularity run --cleanenv -B ${tmpDir}:/tmp \
    -B $t1w_csv -B ${outputDir}:/data/output \
    ${container} \
    --longitudinal \
    --anatomical-images $(echo "${t1w_images[@]}") \
    --output-dir /data/output \
    --num-threads ${LSB_DJOB_NUMPROC} \
    --trim-neck-mode crop \
    --run-quick 2

rm -rf ${tmpDir}
