#!/usr/bin/bash

# script to submit to bsub

# BSUB -N  ## send email when job completes

module load python3
module load fsl

echo running python scripts
python app.py


