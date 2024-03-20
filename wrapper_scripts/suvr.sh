#!/usr/bin/bash

##Make Tau T1 SUVR image

wbseg=$1
infcereb=$2
t1reg=$3
t1suvr=$4

CEREB=$(c3d $wbseg -as SEG \
    -thresh 38 38 1 0 -erode 1 2x2x2vox -popas A \
    -push SEG -thresh 39 39 1 0 -erode 1 2x2x2vox -popas B \
    -push SEG -thresh 71 71 1 0 -erode 1 2x2x2vox -popas C \
    -push SEG -thresh 72 72 1 0 -erode 1 2x2x2vox -popas D \
    -push SEG -thresh 73 73 1 0 -erode 1 2x2x2vox -popas E \
    -push A -push B -add -push C -add -push D -add -push E -add \
    $infcereb -times -as CEREB \
    $t1reg -interp NN -reslice-identity -push CEREB  -lstat | \
    sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')

c3d $t1reg -scale $(echo "1 / $CEREB" | bc -l ) -o $t1suvr