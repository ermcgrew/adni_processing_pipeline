#!/usr/bin/bash

import argparse
import pandas as pd
import os

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mris", help="filepath of mri uids viscode2 csv")
parser.add_argument("-s", "--stats", help="filepath of stats csv")
parser.add_argument("-t", "--taus", required=False, help="filepath of tau uid csv.")
parser.add_argument("-a", "--amys", required=False, help="filepath of amy uid csv.")

args = parser.parse_args()
stats_csv = args.stats
mri_csv = args.mris
tau_csv = args.taus
amy_csv = args.amys

stats_viscodes_csv = stats_csv.split("_TEMP")[0] + ".csv"

print(f"Using stats file {stats_csv}")
print(f"Using MRI file {mri_csv}")

statdf = pd.read_csv(stats_csv)
mrisdf = pd.read_csv(mri_csv)

mrisdf = mrisdf.rename(columns={"SCANDATE.mri":"MRIDATE","PHASE":"PHASE_mri","VISCODE":"VISCODE_mri","VISCODE2":"VISCODE2_mri"}).drop(columns=['NEW.T1','NEW.T2','NEW.FLAIR'])
mrisdf['RID'] = mrisdf['RID'].astype(int)

statsmridf=statdf.merge(mrisdf,how='left',on=['RID','ID','MRIDATE'])

## Add tau and amy viscode info if it's a pet stats sheet
if args.taus:
    print(f"Using TAU file {tau_csv}")
    print(f"Using AMY file {amy_csv}")

    tausdf = pd.read_csv(tau_csv)
    amysdf = pd.read_csv(amy_csv)

    tausdf = tausdf.rename(columns={"SCANDATE.tau":"TAUDATE","PHASE":"PHASE_tau","VISCODE":"VISCODE_tau","VISCODE2":"VISCODE2_tau","IMAGEUID.tau":"IMAGEUID_tau"}).drop(columns=['NEW.tau'])    
    amysdf = amysdf.rename(columns={"SCANDATE.amy":"AMYDATE","PHASE":"PHASE_amy","VISCODE":"VISCODE_amy","VISCODE2":"VISCODE2_amy","TRACER":"TRACER_amy","IMAGEUID.amy":"IMAGEUID_amy"}).drop(columns=['NEW.amy'])

    statsalluids = statsmridf.merge(tausdf,how='left',on=['RID','ID','TAUDATE']).merge(amysdf,how='left',on=['RID','ID','AMYDATE'])
    print(f"Saving stats + viscodes file to {stats_viscodes_csv}.")
    statsalluids.to_csv(stats_viscodes_csv,index=False,header=True)
    
else:
    ## save just the statsmridf
    print(f"Saving stats + viscodes file to {stats_viscodes_csv}.")
    statsmridf.to_csv(stats_viscodes_csv,index=False,header=True)

print(f"Removing the temporary stats file {stats_csv}.")
os.system(f"rm {stats_csv}")