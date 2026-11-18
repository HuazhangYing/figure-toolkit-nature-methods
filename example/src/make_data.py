"""Generate an explicitly simulated paired-donor kinase-inhibition study.

This is a figure-design fixture, not an empirical study or a validated simulator.
Use --overwrite to deliberately replace the editable source tables.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SEED=41827

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overwrite',action='store_true')
    args=parser.parse_args()
    root=ROOT/'data'
    if list(root.glob('*.csv')) and not args.overwrite:
        raise SystemExit('Data already exist; use --overwrite to regenerate. Plotting reads your existing CSVs.')
    rng=np.random.default_rng(SEED)
    donors=[f'D{i:02d}' for i in range(1,13)]
    baseline=rng.normal(112,16,12)
    inhibition=np.clip(rng.normal(.62,.10,12),.25,.85)
    paired=[]; dose=[]; kinetic=[]; methods=[]
    for i,donor in enumerate(donors):
        paired.extend([(donor,'Vehicle',baseline[i]),(donor,'Compound X',baseline[i]*(1-inhibition[i]))])
        for conc in np.logspace(-2,2,9):
            value=baseline[i]*(.12+.88/(1+conc/(.8*np.exp(rng.normal(0,.22)))))+rng.normal(0,2.4)
            dose.append((donor,conc,value))
        for condition,level in [('Vehicle',baseline[i]),('Compound X',baseline[i]*(1-inhibition[i]))]:
            for time in [0,5,10,20,30,45,60]:
                product=level*.065*time/(1+time/85)+rng.normal(0,1.4)
                kinetic.append((donor,condition,time,product))
        # Technical duplicates are explicitly retained, then averaged per donor.
        for rep in [1,2]:
            methods.append((donor,rep,baseline[i]+rng.normal(0,2.5),baseline[i]*1.035+1.5+rng.normal(0,4.2)))
    pd.DataFrame(paired,columns=['donor','condition','activity_nmol_min_mg']).to_csv(root/'paired_activity.csv',index=False)
    pd.DataFrame(dose,columns=['donor','concentration_um','activity_nmol_min_mg']).to_csv(root/'dose_response.csv',index=False)
    pd.DataFrame(kinetic,columns=['donor','condition','time_min','product_nmol_mg']).to_csv(root/'kinetics.csv',index=False)
    pd.DataFrame(methods,columns=['donor','technical_replicate','reference_activity','candidate_activity']).to_csv(root/'method_comparison.csv',index=False)
    # Anonymous protein identifiers avoid implying evidence about real proteins.
    n=420
    mu=rng.normal(21,1.4,n)
    effects=np.r_[rng.normal(-.85,.25,55),rng.normal(.65,.22,40),rng.normal(0,.06,n-95)]
    rows=[]
    for j in range(n):
        donor_baseline=mu[j]+rng.normal(0,.40,len(donors))
        donor_change=effects[j]+rng.normal(0,.30+(j%5)*.06,len(donors))
        for i,donor in enumerate(donors):
            rows.extend([(f'P{j+1:04d}',donor,'Vehicle',donor_baseline[i]),(f'P{j+1:04d}',donor,'Compound X',donor_baseline[i]+donor_change[i])])
    pd.DataFrame(rows,columns=['protein','donor','condition','log2_intensity']).to_csv(root/'proteomics.csv',index=False)
    (root/'simulation.json').write_text(json.dumps({'synthetic':True,'seed':SEED,'n_donors':12,'n_proteins':420,'purpose':'publication-style figure demonstration only','design':'paired donor; technical duplicates in method comparison only','simulation':'baseline and treatment effects generated from Gaussian distributions; no experimental observations'},indent=2))
    print('Created editable simulated CSVs in',root)

if __name__=='__main__': main()
