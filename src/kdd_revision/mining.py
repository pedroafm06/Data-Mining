"""Current A2 model search. Every fitted transform belongs to its training fold.

APIs: sklearn common_pitfalls.html, cross_validation.html and tree.html.
The test set is intentionally absent from the model-selection interface.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
import warnings
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.decomposition import PCA
from .preprocessing.transformer import AppliedPreprocessor
from .schema import SCENARIOS
from .experiments import metric_dict


def candidates():
    out=[]
    def add(kind,params,imputation='global',representation='units'):
        body={'kind':kind,'params':params,'imputation':imputation,'representation':representation}
        body['name']=f'{len(out):02d}_{kind}_'+sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()[:8]
        out.append(body)
    add('dummy',{})
    for criterion in ['gini','entropy']:
        for depth in [3,6]:
            for leaf in [50,20]:
                for weight in [None,'balanced']:
                    for imp in ['global','age']:
                        add('tree',{'criterion':criterion,'max_depth':depth,'min_samples_leaf':leaf,'class_weight':weight},imp)
    for alpha in [.001,.005]:
        for weight in [None,'balanced']:
            for imp in ['global','age']:
                add('tree',{'max_depth':None,'min_samples_leaf':20,'ccp_alpha':alpha,'class_weight':weight},imp)
    for c in [.01,.1,1.,10.]:
        for weight in [None,'balanced']:
            for imp in ['global','age']:
                for rep in ['standard','log_weight_standard']:
                    add('logistic',{'C':c,'class_weight':weight},imp,rep)
    for depth in [8,None]:
        for weight in [None,'balanced']:
            for imp in ['global','age']:
                add('forest',{'n_estimators':150,'max_depth':depth,'min_samples_leaf':10,'class_weight':weight},imp)
    return out


def estimator(candidate):
    params=candidate['params']
    if candidate['kind']=='dummy':return DummyClassifier(strategy='most_frequent')
    if candidate['kind']=='tree':return DecisionTreeClassifier(**params,random_state=42)
    if candidate['kind']=='logistic':return LogisticRegression(**params,max_iter=5000,random_state=42)
    if candidate['kind']=='forest':return RandomForestClassifier(**params,random_state=42,n_jobs=2)
    raise ValueError('Unsupported kind')


def preprocessor(candidate,features):
    age=tuple(c for c in ['Peso','Altura','FC','IMC'] if c in features) if candidate['imputation']=='age' else ()
    return AppliedPreprocessor(features=list(features),age_group_columns=age,log_columns=('Peso',) if 'Peso' in features else ())


def metric(y,p):
    m=metric_dict(y,p);m['accuracy']=(m['tn']+m['tp'])/m['n'];return m


@dataclass
class FittedModel:
    preprocessor: object
    classifier: object
    representation: str
    columns: list
    projection: object=None

    def matrix(self,x):
        z=self.preprocessor.transform(x,self.representation)[self.columns]
        return self.projection.transform(z) if self.projection is not None else z

    def proba(self,x):
        p=self.classifier.predict_proba(self.matrix(x));classes=list(self.classifier.classes_)
        return p[:,classes.index(1)] if 1 in classes else np.zeros(len(x))


def fit_model(x,y,candidate,features,*,add_missing=True,resampling=None,pca=False):
    prep=preprocessor(candidate,features).fit(x)
    z=prep.transform(x,candidate['representation'])
    columns=[c for c in z if add_missing or not c.endswith('__imputado')];z=z[columns]
    projection=None
    if pca:
        projection=PCA(n_components=.95,svd_solver='full');z=projection.fit_transform(z)
    clf=estimator(candidate);y=np.asarray(y)
    if resampling:
        if resampling not in ['over','under']:raise ValueError('Unknown resampling')
        rng=np.random.default_rng(45);classes,counts=np.unique(y,return_counts=True)
        n=int(max(counts) if resampling=='over' else min(counts));chosen=[]
        for label in classes:
            ix=np.flatnonzero(y==label)
            if len(ix)==n:chosen.extend(ix)
            elif len(ix)<n:chosen.extend(np.r_[ix,rng.choice(ix,n-len(ix),replace=True)])
            else:chosen.extend(rng.choice(ix,n,replace=False))
        chosen=np.asarray(chosen);z=z[chosen] if isinstance(z,np.ndarray) else z.iloc[chosen];y=y[chosen]
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning);clf.fit(z,y)
    return FittedModel(prep,clf,candidate['representation'],columns,projection)


def select_candidate(scores,options):
    maximum=scores.mean_balanced_accuracy.max()
    names=set(scores.loc[scores.mean_balanced_accuracy>=maximum-1e-12,'candidate'])
    return next(c for c in options if c['name'] in names)


def digest_ids(x):return sha256('\n'.join(x.ID.astype(str)).encode()).hexdigest()


def cross_validate(x,y,folds,options,features):
    y=np.asarray(y);oof={c['name']:np.full(len(y),np.nan) for c in options};fold_rows=[];audit=[]
    # Cache is local to one training fold; never share fit statistics across folds.
    for fold,(train,val) in enumerate(folds):
        if set(train)&set(val):raise ValueError('Training/validation overlap')
        if set(x.iloc[train].ID)&set(x.iloc[val].ID):raise ValueError('ID overlap')
        cache={}
        for c in options:
            key=(c['imputation'],c['representation'])
            if key not in cache:
                prep=preprocessor(c,features).fit(x.iloc[train])
                a=prep.transform(x.iloc[train],c['representation']);b=prep.transform(x.iloc[val],c['representation'])
                cache[key]=(a,b)
                audit.append({'fold':fold,'imputation':key[0],'representation':key[1],
                    'n_fit':len(train),'n_validation':len(val),'n_features':len(a.columns),'overlap':False,
                    'fit_ids_sha256':digest_ids(x.iloc[train]),'validation_ids_sha256':digest_ids(x.iloc[val]),
                    'parameters':prep.metadata()})
            a,b=cache[key];clf=estimator(c)
            with warnings.catch_warnings():
                warnings.simplefilter('error',ConvergenceWarning);clf.fit(a,y[train])
            classes=list(clf.classes_);p=clf.predict_proba(b)[:,classes.index(1)] if 1 in classes else np.zeros(len(b))
            oof[c['name']][val]=p
            fold_rows.append({'candidate':c['name'],'fold':fold,**metric(y[val],p)})
    if any(not np.isfinite(p).all() for p in oof.values()):raise ValueError('Incomplete or repeated CV validation coverage')
    # Every sample must be validated exactly once, rather than silently overwritten.
    coverage=np.zeros(len(x),dtype=int)
    for _,val in folds:coverage[val]+=1
    if not np.all(coverage==1):raise ValueError('CV validation coverage must be exactly once')
    f=pd.DataFrame(fold_rows);scores=[]
    for c in options:
        q=f[f.candidate.eq(c['name'])]
        scores.append({'candidate':c['name'],'kind':c['kind'],'imputation':c['imputation'],'representation':c['representation'],
            'params':json.dumps(c['params'],sort_keys=True),'mean_balanced_accuracy':q.balanced_accuracy.mean(),
            'sd_balanced_accuracy':q.balanced_accuracy.std(ddof=1),'mean_recall':q.recall.mean(),
            'mean_average_precision':q.average_precision.mean(),'fold_metrics':q.to_dict('records')})
    return pd.DataFrame(scores),oof,audit


def combine_groups(x,reference):
    ids=x.ID.astype(str).tolist();parent=list(range(len(ids)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def unite(values):
        first={}
        for i,k in enumerate(values):
            if k is None:continue
            if k in first:parent[find(i)]=find(first[k])
            else:first[k]=i
    ref=reference.set_index('ID').candidate_group
    unite([ref.get(i,'single_'+i) for i in ids])
    f=x[SCENARIOS['A']];signatures=pd.util.hash_pandas_object(f,index=False).astype(str)
    unite([h if n>=8 else None for h,n in zip(signatures,f.notna().sum(axis=1))])
    # Stable ID of each connected component, without exposing a row's clinical data.
    members={}
    for i in range(len(ids)):members.setdefault(find(i),[]).append(ids[i])
    labels={k:'group_'+sha256('\n'.join(sorted(v)).encode()).hexdigest() for k,v in members.items()}
    return pd.Series([labels[find(i)] for i in range(len(ids))],index=x.index)
