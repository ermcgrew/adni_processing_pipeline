#!/usr/bin/bash

# inputs
BrainLabel=$ROOT/$ID/${MRIDATE}/thickness/${ID}BrainSegmentation.nii.gz
WB_seg=$ROOT/$ID/$MRIDATE/${MRIDATE}_${ID}_wholebrainseg/${MRIDATE}_${ID}_T1w_trim_brainx_ExtractedBrain/${MRIDATE}_${ID}_T1w_trim_brainx_ExtractedBrain_wholebrainseg.nii.gz

module load c3d 
# module load ANTs
# export ANTSPATH=/appl/ANTs-2.3.5/bin
# ANTSPATH=/project/wolk/ADNI_longitudinal-Templates/ants


corticalMask=$outputRoot2/${RID}_GM_Mask.nii.gz
tmpLabels=$outputRoot2/${RID}_antsMalfLabelingCortical.nii.gz


c3d $BrainLabel -threshold 2 2 1 0 -o $corticalMask
c3d $WB_seg -popas A \
    $(for roi in 31 32 47 48 100 101 102 103 104 105 106 107 108 109 112 113 114 115 116 117 118 119 120 121 122 123 124 125 128 129 132 133 134 135 136 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 155 156 157 160 161 162 163 164 165 166 167 168 169 170 171 172 173 174 175 176 177 178 179 180 181 182 183 184 185 190 191 192 193 194 195 196 197 198 199 200 201 202 203 204 205 206 207; \
    do echo "-push A -threshold $roi $roi $roi 0"; done) \
    -accum -add -endaccum -o $tmpLabels

$ANTSPATH/ImageMath 3 $outputRoot2/${RID}_antsMalfLabelingCortical_propogate.nii.gz PropagateLabelsThroughMask $corticalMask $tmpLabels 8 0
#$ANTSPATH/LabelOverlapMeasures 3 $outputRoot/antsMalfLabelingCortical_propogate.nii.gz $tmpLabels $outputRoot/antsWarpedVSPropogated.csv


rm $outputRoot2/*_propogate_label.nii.gz
rm $outputRoot2/*_propogate_speed.nii.gz
rm $outputRoot2/${RID}_GM_Mask.nii.gz
rm $outputRoot2/${RID}_antsMalfLabelingCortical.nii.gz
