#!/usr/bin/bash
import argparse

import pandas as pd

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

stats_viscodes_csv = stats_csv.split(".")[0] + "_viscodes." + stats_csv.split(".")[1]

print(f"Using stats file {stats_csv}")
print(f"Using MRI file {mri_csv}")

statdf = pd.read_csv(stats_csv)
mrisdf = pd.read_csv(mri_csv)

# statdf.info()
# mrisdf.info()

mrisdf = mrisdf.rename(columns={"SCANDATE.mri":"MRIDATE"}).drop(columns=['NEW.T1','NEW.T2','NEW.FLAIR'])
mrisdf['RID'] = mrisdf['RID'].astype(int)

statsmridf=statdf.merge(mrisdf,how='left',on=['RID','ID','MRIDATE'])
# statsmridf.info()


if args.taus:
    print(f"Using TAU file {tau_csv}")
    print(f"Using AMY file {amy_csv}")

    tausdf = pd.read_csv(tau_csv)
    amysdf = pd.read_csv(amy_csv)

    tausdf = tausdf.rename(columns={"SCANDATE.tau":"TAUDATE"}).drop(columns=['NEW.tau'])    
    amysdf = amysdf.rename(columns={"SCANDATE.amy":"AMYDATE"}).drop(columns=['NEW.amy'])

    statsalluids = statsmridf.merge(tausdf,how='left',on=['RID','ID','TAUDATE']).merge(amysdf,how='left',on=['RID','ID','AMYDATE'])
    # statsalluids.info()
    statsalluids.to_csv(stats_viscodes_csv,index=False,header=True)
    
else:
    ## save just the statsmridf
    statsmridf.to_csv(stats_viscodes_csv,index=False,header=True)