#!/usr/bin/bash
stats_output_dir=$1
this_run_analysis_output_dir=$2

date=$(echo $this_run_analysis_output_dir | cut -f 6 -d "/")
outputcsv=adni3_ashst2_stats_${date}.csv

HEADER="ID,MRIDATE"
list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
for side in left right; do
    for sf in $list; do
        HEADER="${HEADER},${side}_${sf}_vol,${side}_${sf}_ns"
    done
done

echo -e "${HEADER}" > $this_run_analysis_output_dir/$outputcsv

for file in $(find ${stats_output_dir}/*ashst2.txt); do
    cat $file >> $this_run_analysis_output_dir/$outputcsv
done
