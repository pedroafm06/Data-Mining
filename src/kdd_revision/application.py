"""Coverage-aware academic application; never labels its own predictions as truth.

The earlier at-least-one-field demonstration is retained as a rejected diagnostic.
This stage uses no new target or test metric and never retunes the frozen models.
"""
from pathlib import Path
from hashlib import sha256
import json
import joblib
import numpy as np
import pandas as pd
from .schema import PROJECT_ROOT,SOURCE_DEFAULT,SCENARIOS
from .preprocessing.run import validated_source
from .preprocessing.preparation import prepare_final,model_frame
from .mining import digest_ids,metric
from .full_kdd import write


def coverage_gate(train,incoming,features,min_support=30):
    observed=incoming[features].notna().sum(axis=1)
    keys=pd.util.hash_pandas_object(train[features].notna(),index=False)
    target=pd.util.hash_pandas_object(incoming[features].notna(),index=False)
    support=target.map(keys.value_counts()).fillna(0).astype(int)
    unseen=pd.Series(False,index=incoming.index)
    for c in features:
        if not pd.api.types.is_numeric_dtype(train[c]):
            unseen|=incoming[c].notna()&~incoming[c].isin(train[c].dropna().unique())
    status=np.select([observed.eq(0),unseen,support.eq(0),support.lt(min_support)],
        ['sem_preditor_disponivel','categoria_inedita','padrao_ausencia_nao_observado','padrao_ausencia_baixo_suporte'],default='cobertura_compativel')
    return pd.DataFrame({'n_observed_predictors':observed,'n_train_same_missing_pattern':support,
        'unseen_category':unseen,'status':status,'accepted':status=='cobertura_compativel'},index=incoming.index)


def run_application(root=PROJECT_ROOT,source=SOURCE_DEFAULT):
    root=Path(root);source,source_hash=validated_source(source);out=root/'artifacts/a2_application';out.mkdir(parents=True,exist_ok=True)
    semantic=prepare_final(pd.read_csv(source,dtype=str,keep_default_na=False)).data;safe=model_frame(semantic)
    mapping=pd.read_csv(root/'artifacts/a2_mining/particoes_modelagem.csv',dtype={'ID':str})
    if safe.ID.tolist()!=mapping.ID.tolist():raise AssertionError('Application row alignment mismatch')
    policy={'version':'A2-application-coverage-v1','minimum_train_pattern_support':30,'support_alternatives':[1,10,30],
        'requirements':['at least one observed predictor','same availability pattern in development','at least 30 development rows with pattern','no novel observed categorical value'],
        'reason':'The at-least-one-field demonstration gave scores to records with unavailable support. This coverage guard rejects unsupported patterns without using their unknown labels or retuning test performance.',
        'threshold_limit':'30 is an operational support requirement, not an empirically optimal clinical threshold. Alternative coverage counts are published; no accuracy can be estimated without labels.',
        'estimation_limit':'Accepted coverage is necessary screening only, not evidence of reliable individual prediction.',
        'model_selection_unchanged':True,'no_test_metrics_used':True,'no_pseudolabel_training':True}
    write(root/'config/a2_application_policy.json',policy)
    summary={};comparisons=[];mask=mapping.partition.eq('unlabeled');devmask=mapping.partition.eq('development')
    for scenario,features in SCENARIOS.items():
        train=safe.loc[devmask,['ID']+features].reset_index(drop=True);incoming=safe.loc[mask,['ID']+features].reset_index(drop=True)
        model_path=root/'artifacts/a2_mining'/f'model_{scenario}.joblib';model=joblib.load(model_path)
        if model.preprocessor.fit_ids_sha256_!=digest_ids(train):raise AssertionError('Coverage fit does not match frozen model development')
        if model.preprocessor.features_!=features:raise AssertionError('Frozen scenario features differ')
        gate=coverage_gate(train,incoming,features);raw=np.full(len(incoming),np.nan)
        available=gate.n_observed_predictors.gt(0);raw[available]=model.proba(incoming.loc[available])
        for minimum in [1,10,30]:
            g=coverage_gate(train,incoming,features,min_support=minimum)
            comparisons.append({'scenario':scenario,'minimum_pattern_support':minimum,'n_accepted':int(g.accepted.sum()),'n_abstained':int((~g.accepted).sum()),'n_unknown_category':int(g.unseen_category.sum())})
        # Secondary description of coverage on the already evaluated historical test.
        # The support policy is never selected using these outcomes.
        test=safe.loc[mapping.partition.eq('test'),['ID']+features].reset_index(drop=True)
        tg=coverage_gate(train,test,features);saved=pd.read_csv(root/'artifacts/a2_mining'/f'predicoes_teste_{scenario}.csv',dtype={'ID':str})
        if saved.ID.tolist()!=test.ID.tolist():raise AssertionError('Test coverage alignment mismatch')
        accepted=tg.accepted.to_numpy();test_coverage={'n_total':len(test),'n_accepted':int(accepted.sum()),'coverage':float(accepted.mean()),
            'accepted_metrics':metric(saved.y.to_numpy()[accepted],saved.p.to_numpy()[accepted]) if accepted.any() and saved.y[accepted].nunique()==2 else None,
            'status':'secondary post-freeze description; not used to choose the coverage policy'}
        gate.insert(0,'ID',incoming.ID);gate['raw_score_for_diagnostic_audit_only']=raw
        gate['p_recorded_anormal']=np.where(gate.accepted,raw,np.nan)
        gate.to_csv(out/f'aplicacao_{scenario}.csv',index=False)
        summary[scenario]={'n_unlabeled':len(incoming),'n_scored':int(gate.accepted.sum()),'n_abstained':int((~gate.accepted).sum()),
            'n_p_ge_half':int((gate.p_recorded_anormal>=.5).sum()),'status_counts':gate.status.value_counts().to_dict(),'model_sha256':sha256(model_path.read_bytes()).hexdigest(),
            'minimum_pattern_support':30,'historical_test_coverage_diagnostic':test_coverage,'not_used_for_training':True,'model_unchanged':True}
    pd.DataFrame(comparisons).to_csv(out/'comparacao_cobertura.csv',index=False);write(out/'summary.json',summary)
    write(out/'verification.json',{'complete':True,'source_sha256':source_hash,'models_unchanged':True,'uses_test_metrics_for_policy_selection':False,'reports_historical_test_coverage':True,'no_pseudolabel_training':True})
    write(out/'manifest.json',{'source_sha256':source_hash,'code_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'outputs_sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='manifest.json'},'self_excluded':True})
    print(json.dumps(summary,ensure_ascii=False,indent=2));return summary
