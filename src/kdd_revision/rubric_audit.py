"""A2 rubric revision: availability-based predictor policy + family-wise nested evaluation.

Leakage is defined as using information unavailable when the prediction is made.
CLINICO keeps every field collected before the report (anthropometry, vitals,
physical examination, anamnesis and PPA derived from them). It excludes only
identifiers/raw dates, the patient's origin (Convenio), the referral reason fields
(MOTIVO1/2, explicit diagnostic content) and HDA2 (more than 50% missing, A1 rule).
FISIO8 and STRICT4 are sensitivity analyses. Model selection uses DEVELOPMENT rows
only; the historical test is scored once afterwards as a secondary evaluation.
"""
from pathlib import Path
from hashlib import sha256
import json,time,warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import confusion_matrix
from .schema import PROJECT_ROOT,SOURCE_DEFAULT,ORIGINAL,NUMERIC,TARGET
from .preprocessing.run import validated_source
from .preprocessing.preparation import prepare_final,model_frame
from .mining import preprocessor,fit_model,metric,cross_validate,select_candidate,digest_ids
from .full_kdd import folds_for,write

CLINICO=['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC','SEXO','PPA','SOPRO','B2','PULSOS','HDA 1']
EXCLUDED_REASONS={'ID':'identificador','Atendimento':'data bruta (a idade derivada entra como IDADE)','DN':'data bruta (a idade derivada entra como IDADE)',
    'Convenio':'origem do paciente/encaminhamento, nao achado clinico','MOTIVO1':'motivo do encaminhamento com conteudo diagnostico explicito',
    'MOTIVO2':'motivo do encaminhamento com conteudo diagnostico explicito','HDA2':'mais de 50% de ausentes (regra da A1)','NORMAL X ANORMAL':'alvo'}
SCENARIOS_AUDIT={'CLINICO':CLINICO,'FISIO8':['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC','SEXO'],
                 'STRICT4':['Peso','Altura','IDADE','SEXO']}
FORBIDDEN=set(ORIGINAL)-set(CLINICO)
assert FORBIDDEN==set(EXCLUDED_REASONS)
FAMILIES=['dummy','tree','logistic','forest']


def validate_features(features):
    if not features or len(set(features))!=len(features) or not set(features)<=set(CLINICO):raise ValueError('Non-admissible predictor list')


def audit_preprocessor(candidate,features):
    validate_features(features)
    if candidate['imputation']=='age' and 'IDADE' not in features:raise ValueError('IDADE cannot be used implicitly after exclusion')
    return preprocessor(candidate,features)


def search_space():
    values=[]
    def add(kind,params,imp='global',rep='units'):
        body={'kind':kind,'params':params,'imputation':imp,'representation':rep}
        body['name']=f'R{len(values):03d}_{kind}_'+sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()[:8];values.append(body)
    add('dummy',{})
    for criterion in ['gini','entropy']:
        for depth in [2,4,6]:
            for leaf in [50,20]:
                for weight in [None,'balanced']:
                    for imp in ['global','age']:add('tree',{'criterion':criterion,'max_depth':depth,'min_samples_leaf':leaf,'class_weight':weight},imp)
    for c in [.01,.1,1.,10.]:
        for weight in [None,'balanced']:
            for imp in ['global','age']:
                for rep in ['standard','log_weight_standard']:add('logistic',{'C':c,'class_weight':weight},imp,rep)
    for depth in [4,8,None]:
        for leaf in [30,10]:
            for weight in [None,'balanced']:
                for imp in ['global','age']:add('forest',{'n_estimators':150,'max_depth':depth,'min_samples_leaf':leaf,'class_weight':weight},imp)
    return values


def load_partition(root=PROJECT_ROOT,source=SOURCE_DEFAULT,partition='development'):
    root=Path(root);source,source_hash=validated_source(source)
    # Historical memberships are retained; no new supposedly untouched holdout.
    membership=pd.read_csv(root/'artifacts/a2_mining/particoes_modelagem.csv',dtype={'ID':str})
    wanted=membership[membership.partition.eq(partition)].copy()
    raw=pd.read_csv(source,dtype=str,keep_default_na=False)
    raw=raw[raw.ID.isin(set(wanted.ID))].copy().reset_index(drop=True)
    if set(raw.ID)!=set(wanted.ID) or not raw.ID.is_unique:raise ValueError('Development membership mismatch')
    prepared=prepare_final(raw);semantic=prepared.data;data=model_frame(semantic)
    groups=wanted.set_index('ID').loc[data.ID,'group'].reset_index(drop=True)
    expected={'development':9361,'test':2342}[partition]
    if len(data)!=expected:raise ValueError(f'This frozen study requires the recorded {partition} population')
    y=data[TARGET].map({'Normal':0,'Anormal':1})
    if y.isna().any():raise ValueError(f'{partition} label missing')
    return raw,semantic,data,y.to_numpy(dtype=int),groups,source_hash


def load_development(root=PROJECT_ROOT,source=SOURCE_DEFAULT):
    return load_partition(root,source,'development')


def score_historical_test(root,source,final_models,out):
    """Secondary evaluation: final model of each pool/family applied once to the historical test.

    The test rows were examined in earlier project phases (A1 EDA and previous A2 runs),
    so this is not an untouched holdout. Nothing here feeds back into selection.
    """
    _,_,test,ytest,_,_=load_partition(root,source,'test');rows=[]
    for (pool,kind),fitted in final_models.items():
        x=test[['ID']+SCENARIOS_AUDIT[pool]].copy();p=fitted.proba(x)
        rows.append({'pool':pool,'family':kind,**metric(ytest,p)})
    pd.DataFrame(rows).to_csv(out/'historical_test_metrics.csv',index=False)
    return rows


def frozen_protocol(source_hash):
    return {'version':'A2-rubrica-2026-11-12-v2-clinico','source_sha256':source_hash,
        'source_rubric_sha256':'bf38c1c6f777f249c2af733a957a2860787446233acd2325c54c26bc1fda545a',
        'development_only_for_selection':True,'historical_test_scored':'secondary, once, after final selection; previously examined',
        'leakage_definition':'information unavailable at prediction time','excluded_fields':EXCLUDED_REASONS,'primary_pool':'CLINICO','sensitivity_pools':['FISIO8','STRICT4'],'n_development':9361,
        'pools':SCENARIOS_AUDIT,'families':FAMILIES,'candidates':search_space(),
        'outer_cv':{'n_splits':5,'seed':743},'inner_cv':{'n_splits':3,'seed_base':811},
        'final_selection_cv':{'n_splits':5,'seed':43},'criterion':'mean balanced_accuracy in inner CV; ties1e-12 listed order',
        'threshold':.5,'same_outer_folds_for_all_families_and_pools':True,
        'grouping':'Frozen candidate components from c8c86e3; used only to prevent candidate equivalence crossing partitions, not as X',
        'limitations':['target reference standard undocumented','previous cohort-wide exploration remains','groups of identical records do not establish patient identity','CLINICO assumes exam findings, anamnesis and vitals are recorded before the report; FISIO8/STRICT4 measure sensitivity to removing them'],
        'audit_probes':'Single-variable, raw-date/ordinal-ID and missingness probes are development-only diagnostic experiments, never admissible model candidates.',
        'null_control':'Fixed shallow tree with permuted development labels; a null result is not proof of absence of leakage',
        'missingness_limit':'Dropping indicators does not remove median fingerprints; single-column probes refer to prepared fields with declared lineage'}


def single_variable_probes(raw,semantic,data,y,groups,out):
    cv=folds_for(y,groups,5,43);rows=[];category_rows=[]
    for column in ORIGINAL:
        missing=data[column].isna()
        if column==TARGET:
            rows.append({'variable':column,'role':'target_never_used_as_predictor','cv_balanced_accuracy':None,'missingness_BA':None,'note':'Target excluded by construction; no tautological fit'})
            continue
        if column=='ID':x=pd.DataFrame({'v':pd.to_numeric(raw.ID,errors='raise')});numeric=True;representation='ordinal_identifier_audit_only'
        elif column in ['DN','Atendimento']:
            x=pd.DataFrame({'v':raw[column].str.strip().replace('',np.nan)});numeric=False;representation='raw_date_token_no_century_assigned_audit_only'
            missing=x.v.isna()
        else:x=pd.DataFrame({'v':data[column]});numeric=column in NUMERIC;representation='prepared_numeric' if numeric else 'nominal_one_hot'
        x=x.astype(object).where(pd.notna(x),np.nan)
        oof=np.full(len(y),np.nan);missing_oof=np.full(len(y),np.nan)
        for train,val in cv:
            if numeric:
                transform=SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)
            else:
                transform=Pipeline([('fill',SimpleImputer(strategy='constant',fill_value='__MISSING__',keep_empty_features=True)),('onehot',OneHotEncoder(handle_unknown='ignore',min_frequency=10))])
            estimator=Pipeline([('transform',transform),('tree',DecisionTreeClassifier(max_depth=3,min_samples_leaf=30,class_weight='balanced',random_state=42))])
            estimator.fit(x.iloc[train],y[train]);oof[val]=estimator.predict_proba(x.iloc[val])[:,list(estimator.classes_).index(1)]
            indicator=missing.to_numpy(dtype=int).reshape(-1,1)
            model=DecisionTreeClassifier(max_depth=1,min_samples_leaf=30,class_weight='balanced',random_state=42).fit(indicator[train],y[train])
            missing_oof[val]=model.predict_proba(indicator[val])[:,list(model.classes_).index(1)]
        rows.append({'variable':column,'role':'exploratory_not_admissibility_proof','representation':representation,
            'cv_balanced_accuracy':metric(y,oof)['balanced_accuracy'],'missingness_BA':metric(y,missing_oof)['balanced_accuracy'],
            'n_missing':int(missing.sum()),'anormal_rate_missing':float(y[missing].mean()) if missing.any() else None,
            'anormal_rate_present':float(y[~missing].mean()) if (~missing).any() else None,
            'note':'Predictive association cannot prove whether this field formed y or was recorded after it. Prepared variables may retain deterministic ancestors.'})
        if not numeric and column not in ['DN','Atendimento']:
            temp=pd.DataFrame({'value':data[column].fillna('__MISSING__'),'y':y})
            for value,sub in temp.groupby('value'):
                category_rows.append({'variable':column,'value':value,'n_development':len(sub),'n_anormal':int(sub.y.sum()),'anormal_rate':float(sub.y.mean())})
    pd.DataFrame(rows).to_csv(out/'variable_probes.csv',index=False)
    pd.DataFrame(category_rows).to_csv(out/'category_target_associations.csv',index=False)
    return rows


def run(root=PROJECT_ROOT,source=SOURCE_DEFAULT):
    root=Path(root);out=root/'artifacts/a2_rubric_audit';out.mkdir(parents=True,exist_ok=True)
    (out/'verification.json').unlink(missing_ok=True);start=time.monotonic()
    raw,semantic,data,y,groups,source_hash=load_development(root,source)
    policy=frozen_protocol(source_hash);write(root/'config/a2_rubrica_protocol_2026_11_07.json',policy)
    policy_hash=sha256(json.dumps(policy,sort_keys=True).encode()).hexdigest();write(out/'protocol_before_results.json',policy)
    options=search_space();outer=folds_for(y,groups,5,743);final_cv=folds_for(y,groups,5,43)
    membership=[]
    for k,(train,val) in enumerate(outer):
        for i in val:membership.append({'ID':data.ID.iloc[i],'outer_fold':k,'group':groups.iloc[i]})
    pd.DataFrame(membership).to_csv(out/'outer_membership.csv',index=False)
    probes=single_variable_probes(raw,semantic,data,y,groups,out);print('21-variable probes completed',flush=True)
    result_rows=[];outer_rows=[];audits=[];choices=[];perm_rows=[];final_choices={};final_models={}
    for pool,features in SCENARIOS_AUDIT.items():
        validate_features(features);x=data[['ID']+features].copy();oof={kind:np.full(len(y),np.nan) for kind in FAMILIES}
        for fold,(train,val) in enumerate(outer):
            print(f'{pool}: outer {fold+1}/5, 3-fold inner x {len(options)} candidates',flush=True)
            xtrain=x.iloc[train].reset_index(drop=True);inner=folds_for(y[train],groups.iloc[train].reset_index(drop=True),3,811+fold)
            scores,_,audit=cross_validate(xtrain,y[train],inner,options,features)
            scores.drop(columns='fold_metrics').to_csv(out/f'inner_scores_{pool}_{fold}.csv',index=False)
            audits.extend([{'pool':pool,'scope':f'outer{fold}','outer_training_ids_sha256':digest_ids(x.iloc[train]),'outer_validation_ids_sha256':digest_ids(x.iloc[val]),**a} for a in audit])
            for kind in FAMILIES:
                family=[c for c in options if c['kind']==kind];chosen=select_candidate(scores[scores.kind.eq(kind)],family)
                audit_preprocessor(chosen,features)
                fitted=fit_model(xtrain,y[train],chosen,features);p=fitted.proba(x.iloc[val]);oof[kind][val]=p
                row={'pool':pool,'family':kind,'outer_fold':fold,'candidate':chosen['name'],'n_fit':len(train),'n_validation':len(val),**metric(y[val],p)}
                outer_rows.append(row);choices.append({'pool':pool,'family':kind,'fold':fold,'candidate':chosen,'fit_parameters':fitted.preprocessor.metadata()})
                joblib.dump(fitted,out/f'outer_model_{pool}_{kind}_{fold}.joblib')
                if kind!='dummy':
                    rng=np.random.default_rng(1700+fold);baseline=row['balanced_accuracy']
                    for column in features:
                        for rep in range(3):
                            probe=x.iloc[val].copy();probe[column]=rng.permutation(probe[column].to_numpy())
                            perm_rows.append({'pool':pool,'family':kind,'outer_fold':fold,'variable':column,'repeat':rep,'BA_drop':baseline-metric(y[val],fitted.proba(probe))['balanced_accuracy']})
        for kind in FAMILIES:
            if not np.isfinite(oof[kind]).all():raise AssertionError('OOF incomplete')
            f=pd.DataFrame(outer_rows).query('pool == @pool and family == @kind')
            result_rows.append({'pool':pool,'family':kind,'mean_fold_BA':f.balanced_accuracy.mean(),'sd_fold_BA':f.balanced_accuracy.std(ddof=1),**metric(y,oof[kind])})
            pd.DataFrame({'ID':x.ID,'y':y,'p':oof[kind],'group':groups}).to_csv(out/f'oof_{pool}_{kind}.csv',index=False)
        print(f'{pool}: final 5-fold choice per family (not performance estimate)',flush=True)
        score,_,audit=cross_validate(x,y,final_cv,options,features);score.drop(columns='fold_metrics').to_csv(out/f'final_selection_scores_{pool}.csv',index=False)
        audits.extend([{'pool':pool,'scope':'final_selection',**a} for a in audit]);final_choices[pool]={}
        for kind in FAMILIES:
            c=select_candidate(score[score.kind.eq(kind)],[v for v in options if v['kind']==kind]);final_choices[pool][kind]=c
            fitted=fit_model(x,y,c,features);joblib.dump(fitted,out/f'final_model_{pool}_{kind}.joblib');final_models[pool,kind]=fitted
            write(out/f'final_parameters_{pool}_{kind}.json',{'candidate':c,'preprocessor':fitted.preprocessor.metadata(),'training_metrics_descriptive':metric(y,fitted.proba(x))})
    pd.DataFrame(result_rows).to_csv(out/'family_nested_metrics.csv',index=False)
    score_historical_test(root,source,final_models,out);print('historical test scored once (secondary)',flush=True)
    pd.DataFrame(outer_rows).to_csv(out/'outer_fold_metrics.csv',index=False);write(out/'outer_selections.json',choices)
    write(out/'preprocessing_audit.json',audits);write(out/'final_choices.json',final_choices)
    pd.DataFrame(perm_rows).to_csv(out/'outer_permutation_importance.csv',index=False)
    # Separate diagnostics of collection, without confusing a missingness proxy with a proven temporal leak.
    collection=[]
    for pool,features in SCENARIOS_AUDIT.items():
        masks=data[features].isna().astype(float);pred=np.full(len(y),np.nan)
        for train,val in final_cv:
            m=DecisionTreeClassifier(max_depth=3,min_samples_leaf=30,class_weight='balanced',random_state=42).fit(masks.iloc[train],y[train])
            pred[val]=m.predict_proba(masks.iloc[val])[:,list(m.classes_).index(1)]
        collection.append({'pool':pool,'kind':'availability_masks_only','n_features':len(features),**metric(y,pred)})
    pd.DataFrame(collection).to_csv(out/'collection_process_controls.csv',index=False)
    null=[];rng=np.random.default_rng(911);ynull=rng.permutation(y)
    cvnull=folds_for(ynull,groups,5,914)
    fixed=next(c for c in options if c['kind']=='tree' and c['params']['max_depth']==2 and c['params']['class_weight']=='balanced' and c['imputation']=='global')
    for pool,features in SCENARIOS_AUDIT.items():
        score,p,au=cross_validate(data[['ID']+features],ynull,cvnull,[fixed],features)
        null.append({'pool':pool,'fixed_candidate':fixed,'metric':metric(ynull,p[fixed['name']]),'interpretation':'negative diagnostic control; not a formal permutation p-value or proof of no leakage'})
    write(out/'permuted_label_control.json',null)
    checks={'complete':True,'source_sha256':source_hash,'protocol_sha256':policy_hash,'n_development':len(y),'historical_test_rows_used_for_selection':0,'historical_test_rows_scored_secondary':2342,
        'pools':SCENARIOS_AUDIT,'candidate_count':len(options),'outer_folds':5,'inner_folds':3,'families':FAMILIES,
        'same_outer_validation_ids_all_models':True,'outer_oof_once_per_row':True,'preprocessing_audits':len(audits),
        'predictor_policy':'Availability at prediction time; excluded fields and reasons in protocol excluded_fields.',
        'source_preserved':sha256(Path(source).resolve().read_bytes()).hexdigest()==source_hash,'elapsed_seconds':round(time.monotonic()-start,2)}
    write(out/'verification.json',checks)
    manifest={'code':{str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),root/'src/kdd_revision/mining.py',root/'src/kdd_revision/preprocessing/transformer.py',root/'src/kdd_revision/preprocessing/preparation.py']},
        'outputs':{p.name:sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='manifest.json'},'self_excluded':True}
    write(out/'manifest.json',manifest);print(json.dumps(checks,ensure_ascii=False,indent=2),flush=True);return checks
