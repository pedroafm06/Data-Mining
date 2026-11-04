"""Applied A2 representation. Fits predictors only, never an estimator or y.

Univariate median and fixed-band conditional medians use only fit rows. Mathematical
transformation and scaling affect continuous measurements, never binary indicators.
"""
from hashlib import sha256
import json
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator,TransformerMixin
from ..schema import NUMERIC,CATEGORICAL,TARGET,SCENARIOS

MISSING='__AUSENTE__';UNSEEN='__DESCONHECIDO__'
DEFAULT_BINS=(0,.25,.5,1,2,5,10,15,20)

def token(v):
    if pd.isna(v):return MISSING
    v=str(v)
    if v in (MISSING,UNSEEN):raise ValueError('Source category collides with reserved representation token')
    return v

class AppliedPreprocessor(BaseEstimator,TransformerMixin):
    def __init__(self,features=None,age_group_columns=('Peso','Altura','FC','IMC'),min_count=30,age_bins=DEFAULT_BINS,log_columns=('Peso',)):
        self.features=features;self.age_group_columns=age_group_columns;self.min_count=min_count;self.age_bins=age_bins;self.log_columns=log_columns

    def _validate(self,x):
        if not isinstance(x,pd.DataFrame):raise TypeError('Named DataFrame required')
        if not set(self.features_)<=set(x):raise ValueError('Missing predictor columns')
        for c in self.numeric_:
            v=pd.to_numeric(x[c],errors='raise').to_numpy(dtype=float,na_value=np.nan)
            if np.isinf(v).any():raise ValueError('Invalidate nonfinite values before transformation')
        return x

    def _bands(self,x):
        # Only the observed/derived original age is used, never imputed age.
        return pd.cut(pd.to_numeric(x.IDADE,errors='raise'),self.age_bins,right=False,labels=False)

    def fit(self,x,y=None):
        if y is not None:raise ValueError('A2 transform does not receive y')
        self.features_=list(SCENARIOS['A'] if self.features is None else self.features)
        allowed=set(NUMERIC)|(set(CATEGORICAL)-{TARGET})
        if not self.features_ or len(set(self.features_))!=len(self.features_) or not set(self.features_)<=allowed:raise ValueError('Forbidden or repeated predictors')
        self.numeric_=[c for c in self.features_ if c in NUMERIC];self.categorical_=[c for c in self.features_ if c not in NUMERIC]
        self._validate(x)
        if not set(self.log_columns)<=set(self.numeric_):raise ValueError('Log columns must be named continuous predictors')
        if not set(self.age_group_columns)<=set(self.numeric_):raise ValueError('Age-group columns must be numeric predictors')
        self.medians_={};self.age_medians_={};self.vocabularies_={}
        bands=self._bands(x) if self.age_group_columns else None
        for c in self.numeric_:
            v=pd.to_numeric(x[c],errors='raise')
            if v.notna().sum()==0:raise ValueError(f'No observed fit values for {c}; no silent clinical zero fallback')
            self.medians_[c]=float(v.median())
            group={}
            if c in self.age_group_columns:
                stats=pd.DataFrame({'v':v,'band':bands}).groupby('band',dropna=True).v.agg(['median','count'])
                group={int(k):{'median':float(r['median']),'n':int(r['count'])} for k,r in stats.iterrows() if r['count']>=self.min_count}
            self.age_medians_[c]=group
        for c in self.categorical_:
            values=sorted({token(v) for v in x[c]}-{MISSING,UNSEEN})
            self.vocabularies_[c]=values+[MISSING,UNSEEN]
        self.output_names_=self.numeric_+[f'{c}__imputado' for c in self.numeric_]
        self.column_dictionary_=[{'name':c,'source':c,'kind':'continuous_measurement'} for c in self.numeric_]+[{'name':f'{c}__imputado','source':c,'kind':'binary_missing_or_masked'} for c in self.numeric_]
        for c in self.categorical_:
            for i,v in enumerate(self.vocabularies_[c]):
                name=f'{c}__{i:03d}'
                self.output_names_.append(name);self.column_dictionary_.append({'name':name,'source':c,'category':v,'kind':'one_hot_binary'})
        fitted=self._numeric_values(x)
        self.means_={c:float(fitted[c].mean()) for c in self.numeric_};self.scales_={c:float(fitted[c].std(ddof=0)) or 1. for c in self.numeric_}
        stabilized=fitted.copy()
        for c in self.log_columns:
            if (stabilized[c]<0).any():raise ValueError('log1p needs nonnegative data; do not silently clip')
            stabilized[c]=np.log1p(stabilized[c])
        self.log_means_={c:float(stabilized[c].mean()) for c in self.numeric_};self.log_scales_={c:float(stabilized[c].std(ddof=0)) or 1. for c in self.numeric_}
        self.n_fit_=len(x)
        self.fit_ids_sha256_=sha256('\n'.join(x.ID.astype(str)).encode()).hexdigest() if 'ID' in x else None
        return self

    def _numeric_values(self,x):
        bands=self._bands(x) if self.age_group_columns else None;result=pd.DataFrame(index=x.index)
        for c in self.numeric_:
            v=pd.to_numeric(x[c],errors='raise').astype(float).copy();missing=v.isna()
            fill=pd.Series(self.medians_[c],index=x.index,dtype=float)
            if c in self.age_group_columns:
                by_age=bands.map({k:a['median'] for k,a in self.age_medians_[c].items()})
                fill=by_age.fillna(self.medians_[c]).astype(float)
            v.loc[missing]=fill.loc[missing];result[c]=v
        return result

    def transform(self,x,representation='units'):
        self._validate(x)
        if representation not in ('units','standard','log_weight_standard'):raise ValueError('Unknown representation')
        values=self._numeric_values(x);out=pd.DataFrame(index=x.index)
        for c in self.numeric_:
            v=values[c].copy()
            if representation=='log_weight_standard':
                if c in self.log_columns:
                    if (v<0).any():raise ValueError('Negative log input')
                    v=np.log1p(v)
                v=(v-self.log_means_[c])/self.log_scales_[c]
            elif representation=='standard':v=(v-self.means_[c])/self.scales_[c]
            out[c]=v
        for c in self.numeric_:out[f'{c}__imputado']=x[c].isna().to_numpy(dtype=np.uint8)
        for c in self.categorical_:
            vocabulary=self.vocabularies_[c];known=set(vocabulary)
            tokens=x[c].map(token).map(lambda v:v if v in known else UNSEEN)
            for i,v in enumerate(vocabulary):out[f'{c}__{i:03d}']=tokens.eq(v).to_numpy(dtype=np.uint8)
        out=out[self.output_names_]
        if not np.isfinite(out.to_numpy(dtype=float)).all():raise ValueError('Nonfinite applied matrix')
        return out

    def get_feature_names_out(self,input_features=None):return np.asarray(self.output_names_,dtype=object)

    def metadata(self):
        return {'n_fit':self.n_fit_,'fit_ids_sha256':self.fit_ids_sha256_,'features':self.features_,'numeric':self.numeric_,'categorical':self.categorical_,
                'global_medians':self.medians_,'age_medians':self.age_medians_,'age_bins':list(self.age_bins),'min_count':self.min_count,
                'age_group_columns':list(self.age_group_columns),'log_columns':list(self.log_columns),'vocabularies':self.vocabularies_,
                'means':self.means_,'scales_ddof0':self.scales_,'log_means':self.log_means_,'log_scales_ddof0':self.log_scales_,
                'dictionary':self.column_dictionary_,'binary_columns_scaled':False,'target_received':False,
                'imputed_BMI_not_recomputed_from_imputed_parents':True,'cv_warning':'Refit this transformer inside every training fold for future CV; do not CV a once-transformed development matrix.'}
