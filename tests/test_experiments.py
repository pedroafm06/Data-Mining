import inspect
import numpy as np
import pandas as pd
import pytest
from kdd_revision.experiments import (Candidate,assert_separate,bootstrap_group_ci,
 build_model,make_splits,metric_dict,select_from_development,subgroup_summary,
 cross_validate_candidate,positive_proba)


def synthetic(n=100):
    y=np.tile([0,1],n//2)
    groups=pd.Series([f'g{i//2}' for i in range(n)])
    ids=pd.Series([str(i) for i in range(n)])
    x=pd.DataFrame({'Peso':np.arange(n,dtype=float)+1,'SEXO':np.where(y==1,'F','M')})
    return x,y,groups,ids


def test_group_partition_no_overlap_same_population_and_reproducibility():
    x,y,g,ids=synthetic()
    a,b,folds=make_splits(y,g,ids)
    c,d,folds2=make_splits(y,g,ids)
    np.testing.assert_array_equal(a,c);np.testing.assert_array_equal(b,d)
    assert len(a)+len(b)==len(y)
    assert not set(g.iloc[a])&set(g.iloc[b])
    assert sorted(np.concatenate([val for _,val in folds]).tolist())==list(range(len(a)))
    for tr,va in folds:
        assert not set(g.iloc[a[tr]])&set(g.iloc[a[va]])


def test_overlap_guards_detect_group_even_with_distinct_ids():
    with pytest.raises(ValueError,match='group'):
        assert_separate(np.array([0]),np.array([1]),pd.Series(['0','1']),pd.Series(['g','g']))


def test_selection_interface_has_no_test_data_and_selects_from_oof_only():
    x,y,g,ids=synthetic();dev,hold,folds=make_splits(y,g,ids)
    options=[Candidate('dummy','dummy',{}),Candidate('tree','tree',{'max_depth':2,'min_samples_leaf':2})]
    best,scores,fs,oof=select_from_development(x.iloc[dev].reset_index(drop=True),y[dev],folds,['Peso','SEXO'],options)
    assert best.name=='tree'
    assert len(oof['tree'])==len(dev)
    assert 'test' not in inspect.signature(select_from_development).parameters
    assert np.isfinite(oof['tree']).all()
    assert not set(ids.iloc[hold])&set(ids.iloc[dev])


def test_imputer_and_scaler_use_training_only_and_unseen_category_supported():
    train=pd.DataFrame({'Peso':[1.,3.,np.nan,5.],'SEXO':['M','F','M','F']})
    model=build_model(Candidate('lr','logistic',{'C':1.}),['Peso','SEXO'])
    model.fit(train,[0,1,0,1])
    num=model.named_steps['preprocess'].named_transformers_['numeric']
    stats=num.named_steps['impute'].statistics_.copy();mean=num.named_steps['scale'].mean_.copy()
    p=positive_proba(model,pd.DataFrame({'Peso':[1.e8,np.nan],'SEXO':['NEW',None]}))
    assert np.isfinite(p).all();np.testing.assert_array_equal(stats,[3.]);np.testing.assert_array_equal(mean,num.named_steps['scale'].mean_)


def test_model_rejects_target_id_and_metadata():
    for forbidden in ['ID','NORMAL X ANORMAL','meta_IDADE_source','flag_Peso_suspect_envelope']:
        with pytest.raises(ValueError):build_model(Candidate('dummy','dummy',{}),['Peso',forbidden])


def test_all_missing_numeric_train_and_missing_category_does_not_crash():
    x=pd.DataFrame({'Peso':[np.nan]*6,'SEXO':[None]*6})
    model=build_model(Candidate('lr','logistic',{'C':1.}),['Peso','SEXO']);model.fit(x,[0,1]*3)
    assert len(positive_proba(model,x))==6


def test_metric_confusion_and_ap_vs_accuracy():
    m=metric_dict([0,0,1,1],[.1,.8,.6,.3])
    assert (m['tn'],m['fp'],m['fn'],m['tp'])==(1,1,1,1)
    assert m['balanced_accuracy']==.5
    assert m['specificity']==.5 and m['recall']==.5
    assert m['average_precision']!=m['balanced_accuracy']


def test_bootstrap_group_resampling_reproducible_and_contains_point_for_perfect_case():
    y=np.tile([0,1],10);p=y*.8+.1;groups=np.repeat(np.arange(10),2)
    a=bootstrap_group_ci(y,p,groups,n_resamples=20);b=bootstrap_group_ci(y,p,groups,n_resamples=20)
    assert a==b;assert a['intervals']['balanced_accuracy']==[1.,1.]


def test_cv_refuses_overlapping_training_validation_indices():
    x,y,_,_=synthetic(20)
    with pytest.raises(ValueError,match='overlap'):
        cross_validate_candidate(x,y,[(np.array([0,1,2]),np.array([2,3]))],Candidate('d','dummy',{}),['Peso'])


def test_subgroups_report_support_and_omit_tiny_groups():
    n=50;data=pd.DataFrame({'SEXO':['M']*40+['F']*10,'IDADE':[4.]*n,'SOPRO':['Ausente']*n,
      'Peso':[10.]*n,'Altura':[100.]*n,'IMC':[10.]*n,'PA SISTOLICA':[90.]*n,'PA DIASTOLICA':[60.]*n,'FC':[80.]*n})
    y=np.tile([0,1],25);p=y*.8+.1
    r=subgroup_summary(data,y,p)
    assert 'F' not in r.loc[r.dimension=='sexo','subgroup'].tolist()
    m=r[(r.dimension=='sexo')&(r.subgroup=='M')].iloc[0]
    assert m.n==40 and m.positive_support==20 and m.recall==1


@pytest.mark.parametrize('path,replacement',[
    (('threshold',),.7),
    (('outer_split','random_state'),99),
    (('candidate_budget','forest','n_estimators'),999),
    (('bootstrap','n_resamples'),100),
    (('temporal_secondary','cutoff'),'2010-01-01'),
    (('scenarios',),['A','B']),
])
def test_protocol_changes_are_rejected_before_any_experiment_output(tmp_path,path,replacement):
    import json
    from pathlib import Path
    from kdd_revision.schema import PROJECT_ROOT
    from kdd_revision.experiments import run_experiments,validate_protocol
    protocol=json.loads((PROJECT_ROOT/'config/protocolo_experimental.json').read_text())
    validate_protocol(protocol)
    target=protocol
    for key in path[:-1]:target=target[key]
    target[path[-1]]=replacement
    (tmp_path/'config').mkdir()
    (tmp_path/'config/protocolo_experimental.json').write_text(json.dumps(protocol))
    with pytest.raises(ValueError,match='Protocol mismatch'):
        run_experiments(tmp_path)
    assert not (tmp_path/'artifacts').exists()
