#!/usr/bin/bash
export DOERODE=true
TMPDIR=$(mktemp -d)
export TMPDIR

id=$1  
mridate=$2
stats_output_dir=$3
t2=$4
cleanup_left=$5
cleanup_right=$6


RID=$(echo $id | cut -f 3 -d "_")
thick=$(c3d $cleanup_left -info-full | grep Spacing | \
  sed -e "s/[a-zA-Z:,]//g" -e "s/\]//" -e "s/\[//" | awk '{print $3}')

statline="${RID},${id},${mridate},${thick}"

#do stats for each hemisphere:
for side in left right; do
    if [ "$side" == "left" ] ; then
        cleanup_seg=$cleanup_left
    elif [ "$side" == "right" ] ; then
        cleanup_seg=$cleanup_right
    fi
    
    ###ASHST2 volumes, number of slices
    c3d $t2 $cleanup_seg -lstat > $TMPDIR/stattau.txt
    ## list is label numbers in stattau.txt file: CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus     
    list=$(echo 1 2 4 3 7 8 10 11 12 13 14)
    for i in $list; do
        THISVOL=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
        THISNSLICE=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
        statline="$statline,$THISVOL,$THISNSLICE"  
    done

    # Combine CA regions (CA1 + CA2 + CA3) to get total CA values
    c3d $t2 $cleanup_seg -replace 2 1 4 1 -as A -push A -lstat > $TMPDIR/stattau.txt
    for i in 1; do
        THISVOL=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
        THISNSLICE=$(cat $TMPDIR/stattau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
        statline="$statline,$THISVOL,$THISNSLICE"
    done

    # Combine hippocampal regions to get total HIPP values 
    c3d $t2 $cleanup_seg -replace 2 1 3 1 4 1 -as A -push A -lstat > $TMPDIR/stathipptau.txt
    for i in 1; do
        THISVOL=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
        THISNSLICE=$(cat $TMPDIR/stathipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
        statline="$statline,$THISVOL,$THISNSLICE"
    done

    # Combine EXTHIPPO regions to get total EXTHIPPO values 
    c3d $t2 $cleanup_seg -replace 1 2 -replace 10 1 11 1 12 1 -as A -push A -lstat > $TMPDIR/statexthipptau.txt
    for i in 1; do
        THISVOL=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
        THISNSLICE=$(cat $TMPDIR/statexthipptau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
        statline="$statline,$THISVOL,$THISNSLICE"
    done

    # Combine EXTHIPPO NO BA36 regions to get total EXTHIPPO NO BA36 values 
    c3d $t2 $cleanup_seg -replace 1 2 -replace 10 1 11 1 -as A -push A -lstat > $TMPDIR/statexthippno36tau.txt
    for i in 1; do
        THISVOL=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
        THISNSLICE=$(cat $TMPDIR/statexthippno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
        statline="$statline,$THISVOL,$THISNSLICE"
    done

    # Combine MTL NO BA36 regions to get total MTL NO BA36 values 
    c3d $t2 $cleanup_seg -replace 2 1 3 1 4 1 10 1 11 1 -as A -push A -lstat > $TMPDIR/statmtlno36tau.txt
    for i in 1; do
        THISVOL=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $7}')
        THISNSLICE=$(cat $TMPDIR/statmtlno36tau.txt | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^$i " | awk '{print $10}')
        statline="$statline,$THISVOL,$THISNSLICE"
    done
done

echo -e $statline | tee ${stats_output_dir}/stats_mri_${mridate}_${id}_ashst2.txt