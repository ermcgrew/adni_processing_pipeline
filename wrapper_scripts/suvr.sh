#!/usr/bin/bash

##Make T1 SUVR image

wbseg=$1
infcereb=$2
t1reg=$3
t1suvr=$4

if [[ $t1reg == *"tau"* ]] ; then 
    # echo "This is a tau file"
    if [[! -f $infcereb ]] ; then 
        exit 1
    else
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
    fi
else
    # echo "this is an amyloid file"
    CEREB=$(c3d $wbseg -as SEG -thresh 38 38 1 0 -popas A \
        -push SEG -thresh 39 39 1 0 -popas B \
        -push SEG -thresh 71 71 1 0 -popas C \
        -push SEG -thresh 72 72 1 0 -popas D \
        -push SEG -thresh 73 73 1 0 -popas E \
        -push SEG -thresh 40 40 1 0 -popas F \
        -push SEG -thresh 41 41 1 0 -popas G \
        -push A -push B -add -push C -add -push D -add -push E -add -push F -add -push G -add \
        -erode 1 2x2x2vox -as CEREB \
        $t1reg -interp NN -reslice-identity -push CEREB  -lstat | \
        sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' | grep "^1 " | awk '{print $2}')
fi

c3d $t1reg -scale $(echo "1 / $CEREB" | bc -l ) -o $t1suvr