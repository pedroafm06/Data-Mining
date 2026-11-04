import numpy as np
import pandas as pd
import pytest
from kdd_revision.mining import candidates, fit_model, cross_validate, select_candidate, combine_groups
from kdd_revision.schema import SCENARIOS, NUMERIC


def example(n=100):
    x=pd.DataFrame({'ID':[str(i) for i in range(n)]})
    for c in SCENARIOS['A']:
        x[c]=np.arange(n,dtype=float)+1 if c in NUMERIC else ['a','b']*(n//2)
    x['IDADE']=np.tile([.5,3,8,16],n//4)
    return x


def test_budget_unique_and_simple_tie_break():
    cs=candidates()
    assert len(cs)==81 and len({c['name'] for c in cs})==81
    scores=pd.DataFrame({'candidate':[c['name'] for c in cs], 'mean_balanced_accuracy':[.5]*81})
    assert select_candidate(scores,cs)['kind']=='dummy'


def test_fitted_statistics_do_not_include_validation_or_target():
    x=example();y=np.arange(100)%2
    x.loc[80:,'Peso']=100000
    model=fit_model(x.iloc[:80],y[:80],candidates()[1],SCENARIOS['B'])
    assert model.preprocessor.n_fit_==80
    assert model.preprocessor.medians_['Peso']==40.5
    before=model.preprocessor.metadata()
    p=model.proba(x.iloc[80:])
    assert np.isfinite(p).all() and before==model.preprocessor.metadata()


def test_each_cv_fit_excludes_validation_ids():
    x=example();y=np.arange(100)%2
    folds=[(np.arange(50),np.arange(50,100)),(np.arange(50,100),np.arange(50))]
    scores,oof,audit=cross_validate(x,y,folds,candidates()[1:3],SCENARIOS['B'])
    assert len(scores)==2 and len(oof)==2
    assert all(a['n_fit']==50 and not a['overlap'] for a in audit)
    assert all(np.isfinite(p).all() for p in oof.values())


def test_group_union_is_transitive_and_preserves_uninformative_distinction():
    x=example(100);x.loc[1,SCENARIOS['A']]=x.loc[0,SCENARIOS['A']]
    reference=pd.DataFrame({'ID':x.ID,'candidate_group':['historic'+str(i) for i in range(100)]})
    reference.loc[2,'candidate_group']=reference.loc[1,'candidate_group']
    g=combine_groups(x,reference)
    assert g.iloc[0]==g.iloc[1]==g.iloc[2]
    assert g.iloc[3]!=g.iloc[0]


def test_invalid_folds_rejected_before_fit():
    x=example();y=np.arange(100)%2
    with pytest.raises(ValueError,match='overlap'):
        cross_validate(x,y,[(np.arange(60),np.arange(50,100))],candidates()[:1],SCENARIOS['B'])
