"""Additional descriptive checks; frozen models are never refitted or reselected."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from .schema import PROJECT_ROOT,SCENARIOS,TARGET
from .mining import metric,preprocessor,select_candidate,candidates
from .full_kdd import folds_for,write


def inspect(root=PROJECT_ROOT):
    root=Path(root);a=root/'artifacts/a2_mining';out=root/'artifacts/a2_kdd';out.mkdir(exist_ok=True)
    data=pd.read_csv(root/'artifacts/a2_preprocessing/_diagnostic_input.csv',dtype={'ID':str},low_memory=False)
    mapping=pd.read_csv(a/'particoes_modelagem.csv',dtype={'ID':str});assert data.ID.tolist()==mapping.ID.tolist()
    mask=mapping.partition.eq('development');dev=data.loc[mask].reset_index(drop=True);groups=mapping.loc[mask,'group'].reset_index(drop=True)
    y=dev[TARGET].map({'Normal':0,'Anormal':1}).to_numpy();scores=pd.read_csv(a/'candidatos_cv.csv');folds=folds_for(y,groups)
    mixture=pd.DataFrame({'group':groups,'y':y}).groupby('group').y.nunique()
    result={'n_development_groups':len(mixture),'groups_with_mixed_labels':int(mixture.gt(1).sum()),'class_counts':pd.Series(y).value_counts().to_dict(),'model_training':{},'pca':{},'resampling_fold_sizes':[]}
    for train,_ in folds:
        counts=np.bincount(y[train],minlength=2);result['resampling_fold_sizes'].append({'original':len(train),'class0':int(counts[0]),'class1':int(counts[1]),'over':int(2*max(counts)),'under':int(2*min(counts)),'preprocessor_fits_before_resampling':True})
    for scenario,features in SCENARIOS.items():
        model=joblib.load(a/f'model_{scenario}.joblib');train_metrics=metric(y,model.proba(dev))
        result['model_training'][scenario]={'training_metrics':train_metrics,'n_encoded_features':len(model.columns),'model_not_refitted':True}
        logistic=select_candidate(scores[scores.scenario.eq(scenario)&scores.kind.eq('logistic')],[c for c in candidates() if c['kind']=='logistic'])
        projections=[]
        for fold,(train,_) in enumerate(folds):
            tr=preprocessor(logistic,features).fit(dev.iloc[train]);z=tr.transform(dev.iloc[train],logistic['representation']);pca=PCA(n_components=.95,svd_solver='full').fit(z)
            projections.append({'fold':fold,'n_fit':len(train),'n_input':z.shape[1],'n_components':int(pca.n_components_),
                'explained_ratio_sum':float(pca.explained_variance_ratio_.sum()),'feature_names':list(z),'components':pca.components_.tolist(),'mean':pca.mean_.tolist(),'explained_variance_ratio':pca.explained_variance_ratio_.tolist()})
        result['pca'][scenario]={'candidate':logistic,'projections':projections,'purpose':'reconstruct and document the tested PCA transform only; classifiers not retuned'}
    write(out/'additional_diagnostics.json',result);return result
