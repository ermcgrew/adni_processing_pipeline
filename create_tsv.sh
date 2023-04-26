#!/usr/bin/bash

function create_tsv_header()
{
  HEADER="RID\tID\tICV\tSlice_Thickness"
  list=$(echo CA1 CA2 CA3 DG MISC SUB ERC BA35 BA36 PHC sulcus CA HIPP EXTHIPPO EXTHIPPOno36 MTLno36)
  for side in left right; do
    for sf in $list; do
      HEADER="${HEADER}\t${side}_${sf}_vol\t${side}_${sf}_ns\t${side}_${sf}_tau\t${side}_${sf}_amy"
    done
  done

  HEADER="$HEADER\tHIPPboth_tau\tHIPPboth_amy\tEXTHIPPno36both_tau\tEXTHIPPno36both_amy\tMTLno36both_tau\tMTLno36both_amy\tcereb_tau\tcereb_amy\tocc_tau\tocc_amy\tpostcing_tau\tpostcing_amy\tinftemp_tau_R\tinftemp_amy_R\tinftemp_tau_L\tinftemp_amy_L\tmidtemp_tau_R\tmidtemp_amy_R\tmidtemp_tau_L\tmidtemp_amy_L\tsuptemp_tau_R\tsuptemp_amy_R\tsuptemp_tau_L\tsuptemp_amy_L\tsuppariet_tau_R\tsuppariet_amy_R\tsuppariet_tau_L\tsuppariet_amy_L\tcalc_tau_R\tcalc_amy_R\tcalc_tau_L\tcalc_amy_L\tangular_tau_R\tangular_amy_R\tangular_tau_L\tangular_amy_L\tsupfront_tau_R\tsupfront_amy_R\tsupfront_tau_L\tsupfront_amy_L"
  
  for roi in $(cat $SDROOT/wholebrainlabels_itksnaplabelfile.txt | grep -v '#' | sed -n '9,$p' | grep -v -E 'vessel|Chiasm|Caudate|Putamen|Stem|White|Accumb|Cerebell|subcallo|Vent|allidum|CSF' | cut -f 2 -d \" | sed -e 's/\( \)\{1,\}/_/g' ); do
    HEADER="$HEADER\t${roi}_tau\t${roi}_amy\t${roi}_thickness"
  done

  echo -e "${HEADER}\t$(cat $PETFILE | sed -n "1p")" > stats_lr_cleanup_corr_nogray.tsv
}

function collate_new_data ()
{
  for fn in $(ls cleanup/stats/*whole.txt | cut -f 3 -d "/"); do

    id=$(cat cleanup/stats/$fn | head -n 1 | awk -F ' ' '{print $1}')
    RID=$(echo $id | cut -f 3 -d "_")
    tp=$(echo $fn | cut -f 7 -d "_")

    ICV=$(cat $SDROOT/${id}/$tp/${SFSEG}/final/${id}_icv.txt | awk '{print $2}')
    ICV=$(printf %10.2f $ICV)

    newline="$RID\t$id\t0$ICV"

    cat cleanup/stats/$fn | sed -e "s/^$id/$newline/g" | tee -a stats_lr_cleanup_corr_nogray.tsv

  done
}