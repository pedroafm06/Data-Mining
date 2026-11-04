#!/usr/bin/env python3
"""Non-predictive A2 diagnostics, development rows only. Does not access y.

Re-run on the FINAL cleaned data, especially after age corrections. Outputs are
exploratory masking reconstruction errors, not evidence about real missingness.
"""
import argparse,json,sys
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import skew
NUMERIC=['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC']
BINS=[0,.25,.5,1,2,5,10,15,20]

def predict_median(frame,band,column,indices,method):
    table=pd.DataFrame({'v':frame[column],'band':band,'sex':frame.SEXO})
    global_value=table.v.median()
    age=table.groupby('band',dropna=True).v.agg(['median','count'])
    sex=table.groupby(['band','sex'],dropna=True).v.agg(['median','count'])
    values=[]
    for i in indices:
        a=band.iloc[i];s=frame.SEXO.iloc[i];k=(a,s);v=global_value
        if method in ('age','age_sex') and a in age.index and age.loc[a,'count']>=30:v=age.loc[a,'median']
        if method=='age_sex' and k in sex.index and sex.loc[k,'count']>=30:v=sex.loc[k,'median']
        values.append(v)
    return np.array(values,dtype=float)

def run(prepared,partitions,output):
    output.mkdir(parents=True,exist_ok=True)
    data=pd.read_csv(prepared,dtype={'ID':str},low_memory=False)
    parts=pd.read_csv(partitions,dtype={'ID':str})
    ids=parts.loc[parts.partition=='development','ID']
    assert ids.is_unique and set(ids)<=set(data.ID)
    data=data.set_index('ID').loc[ids].reset_index()
    # Input is the EXACT reviewed, pre-imputation representation. Never reapply
    # legacy envelopes here: doing that would silently undo preservation choices.
    band=pd.cut(data.IDADE,bins=BINS,right=False,labels=False)
    profiles=[]
    for c in NUMERIC:
        v=data[c].dropna()
        profiles.append({'column':c,'n':len(v),'missing_pct':100*data[c].isna().mean(),'skew_raw':skew(v,bias=False),'skew_log1p':skew(np.log1p(v),bias=False),'median':v.median(),'minimum':v.min(),'maximum':v.max()})
    pd.DataFrame(profiles).to_csv(output/'transform_profiles.csv',index=False)
    masked=[];bmi=[]
    for rep in range(5):
        rng=np.random.default_rng(194+rep)
        for c in [x for x in NUMERIC if x!='IDADE']:
            obs=np.flatnonzero(data[c].notna());test=rng.choice(obs,size=max(1,int(.2*len(obs))),replace=False)
            train=data.copy();train.loc[test,c]=np.nan;truth=data.loc[test,c].to_numpy()
            for method in ['global','age','age_sex']:
                p=predict_median(train,band,c,test,method)
                masked.append({'rep':rep,'column':c,'method':method,'n':len(test),'MAE':np.mean(abs(truth-p)),'RMSE':np.sqrt(np.mean((truth-p)**2))})
        rng=np.random.default_rng(721+rep);obs=np.flatnonzero(data[['Peso','Altura','IMC']].notna().all(axis=1));test=rng.choice(obs,size=max(1,int(.2*len(obs))),replace=False)
        for mode in ['weight_missing','height_missing','both_missing']:
            train=data.copy();train.loc[test,'IMC']=np.nan
            parents=['Peso'] if mode=='weight_missing' else ['Altura'] if mode=='height_missing' else ['Peso','Altura']
            train.loc[test,parents]=np.nan;filled={}
            for c in ['Peso','Altura','IMC']:
                v=train[c].copy();p=predict_median(train,band,c,test,'age')
                filled[c]=np.where(v.loc[test].notna(),v.loc[test].to_numpy(),p)
            calculated=filled['Peso']/(filled['Altura']/100)**2;truth=data.loc[test,'IMC'].to_numpy()
            bmi.append({'rep':rep,'mode':mode,'n':len(test),'MAE_direct_age_median':np.mean(abs(truth-filled['IMC'])),'MAE_from_imputed_parents':np.mean(abs(truth-calculated)),'RMSE_direct':np.sqrt(np.mean((truth-filled['IMC'])**2)),'RMSE_from_parents':np.sqrt(np.mean((truth-calculated)**2))})
    pd.DataFrame(masked).to_csv(output/'imputation_alternatives.csv',index=False)
    pd.DataFrame(bmi).to_csv(output/'bmi_coherence_alternatives.csv',index=False)
    summary={'n_development':len(data),'uses_target':False,'fits_models':False,'accesses_test_predictors':False,'age_bands':BINS,'minimum_observed_per_group':30,'masking_repetitions':5,'masked_fraction_of_observed':.2,'limitation':'Artificial masking among observed development values, not the real missing-data mechanism. Re-run after any cleaning/age change.'}
    (output/'diagnostic_contract.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepared',type=Path,required=True);p.add_argument('--partitions',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(run(a.prepared,a.partitions,a.output),ensure_ascii=False,indent=2))
