#!/usr/bin/bash

sleep 5 #for jobs to start processing
ALLJOBS=$(bjobs | grep "RUN" | wc -l)
while [ $ALLJOBS -gt 1 ]; do  #don't include this running script
    sleep 60
    ALLJOBS=$(bjobs | grep "RUN" | wc -l)
done

echo "all processing and stats creation jobs finished"