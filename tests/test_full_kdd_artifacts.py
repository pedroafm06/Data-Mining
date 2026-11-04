import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from hashlib import sha256
from sklearn.model_selection import StratifiedGroupKFold
from kdd_revision.schema import PROJECT_ROOT

A=PROJECT_ROOT/'artifacts/a2_mining'
pytestmark=pytest.mark.skipif(not (A/'verification.json').exists(),reason='Run full KDD locally to verify real artifacts')


def test_all_frozen_candidates_and_selection_precede_test():
    results=json.loads((A/'verification.json').read_text());assert results['complete']
    choices=json.loads((A/'selected_before_test.json').read_text())['selected'];scores=pd.read_csv(A/'candidatos_cv.csv')
    assert len(scores)==81*3 and not scores[['scenario','candidate']].duplicated().any()
    for scenario,c in choices.items():
        group=scores[scores.scenario.eq(scenario)];chosen=group[group.candidate.eq(c['name'])].iloc[0]
        assert chosen.mean_balanced_accuracy>=group.mean_balanced_accuracy.max()-1e-12
    events=json.loads((A/'events.json').read_text());f=next(i for i,e in enumerate(events) if e['event']=='all_selections_frozen')
    assert all(i>f for i,e in enumerate(events) if e['event']=='test_evaluated')


def test_every_selection_and_nested_audit_matches_train_only_membership():
    mapping=pd.read_csv(A/'particoes_modelagem.csv',dtype={'ID':str});dev=mapping[mapping.partition.eq('development')].reset_index(drop=True)
    oof=pd.read_csv(A/'oof_A.csv',dtype={'ID':str});assert dev.ID.tolist()==oof.ID.tolist()
    y=oof.y.to_numpy();groups=dev.group.to_numpy()
    def splits(y,g,k,seed):return list(StratifiedGroupKFold(k,shuffle=True,random_state=seed).split(np.zeros(len(y)),y,g))
    ordinary=splits(y,groups,5,43);outer=splits(y,groups,3,52)
    nested=[splits(y[train],groups[train],3,53+k) for k,(train,_) in enumerate(outer)]
    audits=json.loads((A/'fold_preprocessing_audit.json').read_text());assert len(audits)==252
    for a in audits:
        if a['scope']=='selection':members=dev;train,val=ordinary[a['fold']]
        else:
            k=int(a['scope'].rsplit('_',1)[1]);otrain,_=outer[k];members=dev.iloc[otrain].reset_index(drop=True)
            train,val=nested[k][a['fold']]
        assert not(set(members.group.iloc[train])&set(members.group.iloc[val]))
        digest=lambda x:sha256('\n'.join(x).encode()).hexdigest()
        assert a['fit_ids_sha256']==digest(members.ID.iloc[train])
        assert a['validation_ids_sha256']==digest(members.ID.iloc[val])
        assert a['parameters']['n_fit']==len(train) and not a['parameters']['target_received']
