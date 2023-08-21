#!/usr/bin/bash

while [[ $(bjobs | grep "emcgrew RUN" | wc -l) -gt 1 ]] ; do 
    echo "sleeping 8"
    sleep 8
done

echo "all processing and stats creation jobs finished"