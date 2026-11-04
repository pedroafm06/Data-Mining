# Historical exploratory reference retained for reproducibility; current A2 preprocessing uses kdd_revision.preprocessing.
"""Local, protocol-frozen experiments. All feature fitting stays inside training folds.

Official APIs: sklearn modules/cross_validation.html, common_pitfalls.html,
modules/model_evaluation.html. No patient record is transmitted.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import time
import warnings
import platform
import joblib
import sklearn

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
    brier_score_loss, confusion_matrix, f1_score, precision_score, recall_score,
    roc_auc_score, roc_curve, precision_recall_curve)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .schema import PROJECT_ROOT, SCENARIOS, TARGET, NUMERIC
from .prepare import safe_model_frame
from .transforms import build_preprocessor


@dataclass(frozen=True)
class Candidate:
    name: str
    kind: str
    params: dict


def candidates():
    result=[Candidate('dummy','dummy',{})]
    for c in [.1,1.]:
        for weight in [None,'balanced']:
            result.append(Candidate(f'logistic_C{c}_w{weight}','logistic',{'C':c,'class_weight':weight}))
    for depth in [3,6]:
        for leaf in [20,50]:
            result.append(Candidate(f'tree_d{depth}_leaf{leaf}','tree',{'max_depth':depth,'min_samples_leaf':leaf}))
    result.append(Candidate('forest_150_d8_leaf10','forest',{'n_estimators':150,'max_depth':8,'min_samples_leaf':10}))
    return result


def build_model(candidate, features, *, add_missing=True, log=False):
    # Explicit named features are the only route to X; preprocessing rejects metadata.
    prep=build_preprocessor(features,scale=candidate.kind=='logistic',add_missing=add_missing,log=log)
    if candidate.kind=='dummy':est=DummyClassifier(strategy='most_frequent')
    elif candidate.kind=='logistic':est=LogisticRegression(**candidate.params,max_iter=3000,random_state=42)
    elif candidate.kind=='tree':est=DecisionTreeClassifier(**candidate.params,random_state=42)
    elif candidate.kind=='forest':est=RandomForestClassifier(**candidate.params,random_state=42,n_jobs=2)
    else:raise ValueError('Unrecognized candidate kind')
    return Pipeline([('preprocess',prep),('model',est)])


def assert_separate(left,right,ids,groups):
    if set(ids.iloc[left]) & set(ids.iloc[right]):raise ValueError('ID overlap')
    if set(groups.iloc[left]) & set(groups.iloc[right]):raise ValueError('Candidate group overlap')


def make_splits(y,groups,ids):
    y=np.asarray(y)
    outer=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=42)
    dev,test=next(outer.split(np.zeros(len(y)),y,groups))
    assert_separate(dev,test,ids,groups)
    folds=[]
    inner=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=43)
    for train,val in inner.split(np.zeros(len(dev)),y[dev],groups.iloc[dev]):
        assert_separate(dev[train],dev[val],ids,groups)
        if len(set(y[dev[train]]))<2 or len(set(y[dev[val]]))<2:raise ValueError('Both classes required in CV')
        folds.append((train,val))
    return dev,test,folds


def positive_proba(model,x):
    est=model.named_steps['model']
    cols=list(est.classes_)
    return model.predict_proba(x)[:,cols.index(1)] if 1 in cols else np.zeros(len(x))


def metric_dict(y,p):
    y=np.asarray(y);p=np.asarray(p);pred=(p>=.5).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    both=len(np.unique(y))==2
    return {'n':len(y),'prevalence':float(np.mean(y)), 'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp),
        'recall':float(recall_score(y,pred,zero_division=0)),
        'specificity':float(tn/(tn+fp)) if tn+fp else None,
        'precision':float(precision_score(y,pred,zero_division=0)),
        'f1':float(f1_score(y,pred,zero_division=0)),
        'balanced_accuracy':float(balanced_accuracy_score(y,pred)) if both else None,
        'roc_auc':float(roc_auc_score(y,p)) if both else None,
        'average_precision':float(average_precision_score(y,p)) if np.any(y==1) else None,
        'brier':float(brier_score_loss(y,p))}


def cross_validate_candidate(x,y,folds,candidate,features,*,add_missing=True,log=False):
    """Only development rows enter; each fold owns a freshly fitted pipeline."""
    y=np.asarray(y);oof=np.full(len(y),np.nan);rows=[]
    for k,(train,val) in enumerate(folds):
        if set(train)&set(val):raise ValueError('Training/validation overlap')
        model=build_model(candidate,features,add_missing=add_missing,log=log)
        with warnings.catch_warnings():
            warnings.simplefilter('error',ConvergenceWarning)
            model.fit(x.iloc[train][features],y[train])
        p=positive_proba(model,x.iloc[val][features]);oof[val]=p
        rows.append({'fold':k,**metric_dict(y[val],p)})
    if not np.isfinite(oof).all():raise ValueError('Incomplete OOF predictions')
    return pd.DataFrame(rows),oof


def select_from_development(x,y,folds,features,candidate_list=None):
    """No test argument exists; selection can only see development inputs."""
    scores=[];allfold=[];predictions={}
    for candidate in candidate_list or candidates():
        fold,p=cross_validate_candidate(x,y,folds,candidate,features)
        predictions[candidate.name]=p
        scores.append({'candidate':candidate.name,'kind':candidate.kind,
            'cv_balanced_accuracy_mean':float(fold.balanced_accuracy.mean()),
            'cv_balanced_accuracy_sd':float(fold.balanced_accuracy.std(ddof=1)),
            'cv_recall_mean':float(fold.recall.mean()),'cv_average_precision_mean':float(fold.average_precision.mean())})
        fold.insert(0,'candidate',candidate.name);allfold.append(fold)
    best_index=max(range(len(scores)),key=lambda i:scores[i]['cv_balanced_accuracy_mean'])
    lookup={c.name:c for c in (candidate_list or candidates())}
    return lookup[scores[best_index]['candidate']],pd.DataFrame(scores),pd.concat(allfold,ignore_index=True),predictions


def bootstrap_group_ci(y,p,groups,n_resamples=500,seed=44):
    """Group percentile intervals conditional on fitted model; no model refitting."""
    y=np.asarray(y);p=np.asarray(p);groups=np.asarray(groups)
    unique=np.unique(groups);indices={g:np.flatnonzero(groups==g) for g in unique}
    rng=np.random.default_rng(seed);metrics=['balanced_accuracy','recall','specificity','precision','roc_auc','average_precision','brier']
    values={m:[] for m in metrics};skipped=0
    for _ in range(n_resamples):
        ix=np.concatenate([indices[g] for g in rng.choice(unique,len(unique),replace=True)])
        if len(np.unique(y[ix]))<2:skipped+=1;continue
        m=metric_dict(y[ix],p[ix])
        for k in metrics:values[k].append(m[k])
    return {'n_resamples':n_resamples,'skipped_single_class':skipped,'unit':'candidate_split_group','conditional_on_fitted_model':True,
        'intervals':{k:[float(np.quantile(v,.025)),float(np.quantile(v,.975))] if v else None for k,v in values.items()}}


def subgroup_summary(data,y,p):
    """Descriptive subgroup support and Wilson recall intervals; no causal inference."""
    rows=[];y=np.asarray(y);p=np.asarray(p)
    def wilson(success,n):
        if n==0:return (None,None)
        z=norm.ppf(.975);a=success/n;d=1+z*z/n
        mid=(a+z*z/(2*n))/d;half=z*np.sqrt(a*(1-a)/n+z*z/(4*n*n))/d
        return float(mid-half),float(mid+half)
    sets={'sexo':data.SEXO.fillna('AUSENTE').astype(str),
          'idade':pd.cut(data.IDADE,[-.00001,1,5,10,15,20],right=False,labels=['<1','1-4','5-9','10-14','15-19']).astype('object').fillna('INDEFINIDA'),
          'sopro':data.SOPRO.fillna('NAO_REGISTRADO').map(lambda z:'SEM_SOPRO' if z=='Ausente' else ('NAO_REGISTRADO' if z=='NAO_REGISTRADO' else 'COM_SOPRO')),
          'ausencias_B':data[SCENARIOS['B']].isna().sum(axis=1).map(lambda n:'0' if n==0 else ('1-2' if n<=2 else '3+'))}
    for dimension,labels in sets.items():
        for label in sorted(labels.unique()):
            mask=np.asarray(labels==label)
            if mask.sum()<20:continue
            m=metric_dict(y[mask],p[mask]);lo,hi=wilson(m['tp'],m['tp']+m['fn'])
            rows.append({'dimension':dimension,'subgroup':label,**m,'recall_wilson_low':lo,'recall_wilson_high':hi,
                'positive_support':m['tp']+m['fn'],'positive_support_below20':m['tp']+m['fn']<20,
                'interval_note':'Wilson descriptive row-based, no group correction; inspect support; no causal inference'})
    return pd.DataFrame(rows)


def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False))


def temporal_evaluation(data,y,groups,candidate,features):
    dates=pd.to_datetime(data['meta_Atendimento_hypothesis_2003_2010'],errors='coerce')
    train=np.flatnonzero((dates<pd.Timestamp('2009-01-01')).to_numpy());test=np.flatnonzero((dates>=pd.Timestamp('2009-01-01')).to_numpy())
    crossed=set(groups.iloc[train])&set(groups.iloc[test]);before=len(train)
    train=np.array([i for i in train if groups.iloc[i] not in crossed],dtype=int)
    info={'status':'hypothetical_chronology_not_confirmed','n_no_hypothesis_date':int(dates.isna().sum()),'n_train':len(train),'n_test':len(test),
          'crossing_candidate_groups':len(crossed),'train_removed_crossing_groups':before-len(train),'cutoff':'2009-01-01','retuned':False,
          'selection_scope':'candidate chosen by global development CV, including dates after temporal cutoff; not purely prospective model selection'}
    if min(len(train),len(test))<100 or len(set(np.asarray(y)[train]))<2 or len(set(np.asarray(y)[test]))<2:
        info['not_executed_reason']='insufficient coverage or classes';return info,None
    model=build_model(candidate,features);model.fit(data.iloc[train][features],np.asarray(y)[train]);p=positive_proba(model,data.iloc[test][features])
    info['metrics']=metric_dict(np.asarray(y)[test],p)
    return info,pd.DataFrame({'ID':data.ID.iloc[test].to_numpy(),'y':np.asarray(y)[test],'p':p})


def create_figures(results,preds,y,out):
    figdir=out/'figures';figdir.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,3,figsize=(12,3.5))
    for ax,(name,m) in zip(axes,results.items()):
        mat=np.array([[m['tn'],m['fp']],[m['fn'],m['tp']]])
        ax.imshow(mat,cmap='Blues');ax.set_xticks([0,1],['Normal','Anormal']);ax.set_yticks([0,1],['Normal','Anormal'])
        for (i,j),v in np.ndenumerate(mat):ax.text(j,i,str(v),ha='center',va='center',color='white' if v>mat.max()*.55 else 'black')
        ax.set_xlabel('Previsto');ax.set_ylabel('Registrado');ax.set_title(f'{name}: {m["candidate"]}')
    fig.suptitle('Teste reservado para modelagem - limiar fixo 0,5');fig.tight_layout();fig.savefig(figdir/'confusoes_teste.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for name,p in preds.items():
        fpr,tpr,_=roc_curve(y,p);prec,rec,_=precision_recall_curve(y,p)
        axes[0].plot(fpr,tpr,label=f'{name}');axes[1].plot(rec,prec,label=f'{name}')
    axes[0].plot([0,1],[0,1],'--',c='gray');axes[1].axhline(np.mean(y),ls='--',c='gray',label='Prevalência')
    axes[0].set(xlabel='Taxa falso positivo',ylabel='Recall',title='ROC');axes[1].set(xlabel='Recall',ylabel='Precisão',title='Precisão-Recall (AP relatada)')
    for ax in axes:ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(figdir/'roc_pr_teste.png',dpi=160);plt.close(fig)


def validate_protocol(protocol):
    """Reject config drift: the protocol records the fixed, supported experiment.

    This JSON is a checked snapshot, not an arbitrary estimator configuration.
    Changing experimental choices requires updating code/tests and a new protocol,
    rather than silently writing a frozen file that the implementation ignores.
    """
    expected = {
        'positive_label': 'Anormal', 'eligibility': 'elegivel_principal',
        'primary_quality_policy': 'mask_suspect',
        'scenarios': ['A', 'B', 'B_contexto'], 'same_population_and_partitions': True,
        'outer_split': {'method': 'StratifiedGroupKFold', 'n_splits': 5,
                        'shuffle': True, 'random_state': 42, 'heldout_fold': 0},
        'inner_cv': {'method': 'StratifiedGroupKFold', 'n_splits': 5,
                     'shuffle': True, 'random_state': 43},
        'selection_metric': 'mean_inner_balanced_accuracy',
        'selection_tie_break': 'candidate order: simpler first', 'threshold': .5,
        'candidate_budget': {
            'dummy': 'most_frequent',
            'logistic': {'C': [.1, 1.], 'class_weight': [None, 'balanced'], 'max_iter': 3000},
            'tree': {'max_depth': [3, 6], 'min_samples_leaf': [20, 50]},
            'forest': {'n_estimators': 150, 'max_depth': 8, 'min_samples_leaf': 10,
                       'class_weight': None, 'n_jobs': 2}},
    }
    for field, value in expected.items():
        if protocol.get(field) != value:
            raise ValueError(f'Protocol mismatch for {field}: fixed implementation and snapshot disagree.')
    for section, fields in {
        'temporal_secondary': {'date': 'meta_Atendimento_hypothesis_2003_2010',
            'cutoff': '2009-01-01', 'pre_cutoff': 'train', 'post_cutoff': 'evaluate',
            'remove_crossing_groups_from_train': True, 'retune': False},
        'bootstrap': {'unit': 'candidate split_group', 'n_resamples': 500, 'random_state': 44},
    }.items():
        for field, value in fields.items():
            if protocol.get(section, {}).get(field) != value:
                raise ValueError(f'Protocol mismatch for {section}.{field}.')
    return protocol


def run_experiments(root=PROJECT_ROOT):
    root=Path(root)
    protocol_path=root/'config/protocolo_experimental.json'
    protocol=validate_protocol(json.loads(protocol_path.read_text()))
    protocol_hash=sha256(protocol_path.read_bytes()).hexdigest()
    out=root/'artifacts/experiments';out.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter();write_json(out/'protocol_frozen.json',{'sha256':protocol_hash,'protocol':protocol})
    base=pd.read_csv(root/'artifacts/prepared/dados_tratados.csv',low_memory=False,dtype={'ID':str})
    eligible=pd.read_csv(root/'artifacts/prepared/elegibilidade.csv',dtype={'ID':str})
    g=pd.read_csv(root/'artifacts/prepared/grupos.csv',dtype={'ID':str})
    ids=eligible.loc[eligible.elegivel_principal,'ID']
    base=base.set_index('ID').loc[ids].reset_index();g=g.set_index('ID').loc[ids].reset_index()
    data=safe_model_frame(base,policy='mask_suspect');groups=g.split_group.reset_index(drop=True)
    y=(data[TARGET]=='Anormal').astype(int).to_numpy();dev,test,folds=make_splits(y,groups,data.ID)
    split=pd.DataFrame({'ID':data.ID,'candidate_group':groups,'partition':'development','inner_fold':-1})
    split.loc[test,'partition']='test'
    for k,(_,val) in enumerate(folds):split.loc[dev[val],'inner_fold']=k
    split.to_csv(out/'particoes.csv',index=False)
    xdev=data.iloc[dev].reset_index(drop=True);ydev=y[dev]
    chosen={};cv_rows=[];fold_rows=[];oof_rows=[]
    for scenario in protocol['scenarios']:
        features=SCENARIOS[scenario]
        best,scores,foldscores,oof=select_from_development(xdev,ydev,folds,features)
        chosen[scenario]=best
        scores.insert(0,'scenario',scenario);cv_rows.append(scores)
        foldscores.insert(0,'scenario',scenario);fold_rows.append(foldscores)
        for name,p in oof.items():oof_rows.append(pd.DataFrame({'scenario':scenario,'candidate':name,'ID':xdev.ID,'y':ydev,'p_oof':p}))
        print('Selected from development',scenario,best.name,flush=True)
    pd.concat(cv_rows,ignore_index=True).to_csv(out/'candidatos_cv.csv',index=False)
    pd.concat(fold_rows,ignore_index=True).to_csv(out/'metricas_folds.csv',index=False)
    pd.concat(oof_rows,ignore_index=True).to_csv(out/'previsoes_oof.csv',index=False)
    # Frozen selection is persisted BEFORE the first test metrics are computed.
    frozen={s:{'name':c.name,'kind':c.kind,'params':c.params,'features':SCENARIOS[s]} for s,c in chosen.items()}
    write_json(out/'selecoes_congeladas_antes_teste.json',{'protocol_sha256':protocol_hash,'selections':frozen,'uses_test_metrics':False})
    sensitivity_rows=[]
    for s,c in chosen.items():
        features=SCENARIOS[s]
        variants=[('sem_indicadores',xdev,features,False,False),('sem_IMC',xdev,[f for f in features if f!='IMC'],True,False),
                  ('suspeitos_preservados',safe_model_frame(base.iloc[dev].reset_index(drop=True),'conservative'),features,True,False)]
        if 'PPA' in features:variants.append(('sem_PPA',xdev,[f for f in features if f!='PPA'],True,False))
        if c.kind=='logistic':variants.append(('log1p',xdev,features,True,True))
        for name,xd,fs,missing,log in variants:
            fscores,p=cross_validate_candidate(xd,ydev,folds,c,fs,add_missing=missing,log=log)
            sensitivity_rows.append({'scenario':s,'variant':name,'candidate_fixed':c.name,'n':len(ydev),'cv_balanced_accuracy_mean':float(fscores.balanced_accuracy.mean()),'cv_balanced_accuracy_sd':float(fscores.balanced_accuracy.std(ddof=1)),'use_for_test_selection':False})
    pd.DataFrame(sensitivity_rows).to_csv(out/'sensibilidades_desenvolvimento.csv',index=False)
    results={};preds={};subgroups=[];boot={};importance=[];coeff=[];temporal={};prediction_rows=[]
    modeldir=out/'models';modeldir.mkdir(exist_ok=True)
    for s,c in chosen.items():
        fs=SCENARIOS[s];model=build_model(c,fs)
        with warnings.catch_warnings():
            warnings.simplefilter('error',ConvergenceWarning);model.fit(xdev[fs],ydev)
        joblib.dump(model,modeldir/f'pipeline_{s}.joblib',compress=3)
        write_json(modeldir/f'metadata_{s}.json',{'scenario':s,'candidate':c.name,'features':fs,'positive_label':'Anormal','positive_code':1,'threshold':.5,'quality_policy':'mask_suspect before this estimator','protocol_sha256':protocol_hash,'python':platform.python_version(),'sklearn':sklearn.__version__,'pandas':pd.__version__,'training_IDs_sha256':sha256('\n'.join(xdev.ID.astype(str)).encode()).hexdigest(),'warning':'Load only trusted local joblib files; dependencies and same named input schema required. Not clinical validation.'})
        p=positive_proba(model,data.iloc[test][fs]);preds[s]=p;results[s]={'candidate':c.name,**metric_dict(y[test],p)}
        boot[s]=bootstrap_group_ci(y[test],p,groups.iloc[test].to_numpy())
        prediction_rows.append(pd.DataFrame({'scenario':s,'ID':data.ID.iloc[test].to_numpy(),'y':y[test],'p':p,'pred':(p>=.5).astype(int)}))
        sg=subgroup_summary(data.iloc[test].reset_index(drop=True),y[test],p);sg.insert(0,'scenario',s);subgroups.append(sg)
        # Exploratory interpretation model: held-out development fold was never used in its fit.
        tr,va=folds[0];imodel=build_model(c,fs);imodel.fit(xdev.iloc[tr][fs],ydev[tr])
        imp=permutation_importance(imodel,xdev.iloc[va][fs],ydev[va],scoring='balanced_accuracy',n_repeats=5,random_state=45,n_jobs=1)
        for col,m,sd in zip(fs,imp.importances_mean,imp.importances_std):importance.append({'scenario':s,'feature':col,'mean_balanced_accuracy_drop':float(m),'sd_repeats':float(sd),'n_validation':len(va),'evaluation':'heldout_development_fold_post_selection_exploratory'})
        names=model.named_steps['preprocess'].get_feature_names_out();est=model.named_steps['model']
        values=getattr(est,'coef_',None)
        if values is not None:
            for name,value in zip(names,values[0]):coeff.append({'scenario':s,'feature':name,'value':float(value),'kind':'coefficient_descriptive'})
        elif hasattr(est,'feature_importances_'):
            for name,value in zip(names,est.feature_importances_):coeff.append({'scenario':s,'feature':name,'value':float(value),'kind':'impurity_importance_descriptive_not_generalization'})
        temporal[s],tp=temporal_evaluation(data,y,groups,c,fs)
        if tp is not None:tp.to_csv(out/f'previsoes_temporais_{s}.csv',index=False)
    # Fixed controls, not candidates selected using the test.
    baseline=np.zeros(len(test));controls={'dummy_fixed':metric_dict(y[test],baseline)}
    murmur=data.iloc[test].SOPRO;known=murmur.notna().to_numpy();mp=(murmur[known]!='Ausente').astype(int).to_numpy()
    controls['murmur_fixed_complete_cases']={'coverage':float(known.mean()),**metric_dict(y[test][known],mp),'note':'fixed descriptive rule; scope conditional on target construction, unknown sopro excluded'}
    write_json(out/'metricas_teste.json',results);write_json(out/'intervalos_bootstrap_grupos.json',boot);write_json(out/'controles_fixos.json',controls);write_json(out/'temporal_hipotetico.json',temporal)
    pd.concat(prediction_rows,ignore_index=True).to_csv(out/'previsoes_teste.csv',index=False)
    pd.concat(subgroups,ignore_index=True).to_csv(out/'subgrupos_teste.csv',index=False)
    pd.DataFrame(importance).to_csv(out/'importancia_permutacao_desenvolvimento.csv',index=False);pd.DataFrame(coeff).to_csv(out/'coeficientes_importancias_descritivos.csv',index=False)
    create_figures(results,preds,y[test],out)
    # Top permutation features and subgroup recall, annotated as descriptive.
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,s in zip(axes,chosen):
        part=pd.DataFrame(importance).query('scenario==@s').nlargest(6,'mean_balanced_accuracy_drop').sort_values('mean_balanced_accuracy_drop')
        ax.barh(part.feature,part.mean_balanced_accuracy_drop);ax.set_title(s);ax.set_xlabel('Queda balancedaccuracy');ax.tick_params(labelsize=8)
    fig.suptitle('Permutação em fold de desenvolvimento fora do ajuste (exploratória)');fig.tight_layout();fig.savefig(out/'figures/permutacao_desenvolvimento.png',dpi=160);plt.close(fig)
    meta={'protocol_sha256':protocol_hash,'n_eligible':len(y),'n_development':len(dev),'n_test':len(test),'n_groups':int(groups.nunique()),'no_ID_overlap':not bool(set(data.ID.iloc[dev])&set(data.ID.iloc[test])),'no_candidate_group_overlap':not bool(set(groups.iloc[dev])&set(groups.iloc[test])),'same_IDs_all_scenarios':True,'threshold':.5,'selection_metric':'inner_cv_balanced_accuracy','test_used_for_selection':False,'elapsed_seconds':round(time.perf_counter()-started,2),'source_manifest_sha256':sha256((root/'artifacts/prepared/manifest.json').read_bytes()).hexdigest()}
    write_json(out/'execution_summary.json',meta)
    write_results_doc(root,meta,results,controls,temporal,pd.concat(cv_rows),pd.DataFrame(sensitivity_rows))
    write_json(out/'manifest.json',{'execution':meta,'outputs':{str(p.relative_to(out)):sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json'},'code_sha256':sha256(Path(__file__).read_bytes()).hexdigest()})
    print(json.dumps({'execution':meta,'test':results},ensure_ascii=False,indent=2),flush=True)
    return meta


def write_results_doc(root,meta,results,controls,temporal,cv,sens):
    text=['# Resultados dos experimentos KDD\n','Execução acadêmica local. O alvo é o rótulo registrado, sem validação clínica do processo de diagnóstico. Os três cenários usam os mesmos registros e partições.\n',
      f'População: {meta["n_eligible"]}; desenvolvimento: {meta["n_development"]}; teste reservado: {meta["n_test"]}. Não há IDs nem grupos candidatos compartilhados entre os dois conjuntos. Grupos são equivalências candidatas, não identidade comprovada de paciente.\n',
      'A inclui achados/contexto; B somente medidas+SEXO; B_contexto adiciona contexto de temporalidade desconhecida. Limiar0,5 fixo. Seleção por balancedaccuracy CV antes de calcular métricas de teste. A base inteira já foi explorada na A1; este teste não é virgem dessa exploração.\n',
      '## Conceitos utilizados\n',
      'O núcleo usa separação treino/teste, validação cruzada, pipeline de transformação, ajuste de hiperparâmetros, árvore de decisão, matriz de confusão, precisão, recall, F1, acurácia balanceada e curvas ROC/Precisão-Recall. A árvore tem exemplos no material; isso não equivale a uma explicação completa de todos os algoritmos. Regressão logística, floresta aleatória, average precision, Brier, importância por permutação e intervalos por reamostragem de grupos são comparações ou extensões complementares. A síntese da A1 também usa Welch e V de Cramér como complementos técnicos. Não se atribui às aulas a explicação desses complementos.\n',
      '| Cenário | Vencedor CV | Balancedaccuracy teste | Recall | Especificidade | Precisão | AP | ROC-AUC | TN/FP/FN/TP |','|---|---|---:|---:|---:|---:|---:|---:|---|']
    for s,m in results.items():text.append(f'| {s} | {m["candidate"]} | {m["balanced_accuracy"]:.4f} | {m["recall"]:.4f} | {m["specificity"]:.4f} | {m["precision"]:.4f} | {m["average_precision"]:.4f} | {m["roc_auc"]:.4f} | {m["tn"]}/{m["fp"]}/{m["fn"]}/{m["tp"]} |')
    text+=['\n## Controles e interpretação\n',f'Dummy fixo: balancedaccuracy={controls["dummy_fixed"]["balanced_accuracy"]:.4f}. Regra fixa de sopro nos registros com esse dado: cobertura={controls["murmur_fixed_complete_cases"]["coverage"]:.4f}, balancedaccuracy={controls["murmur_fixed_complete_cases"]["balanced_accuracy"]:.4f}. A regra não substitui diagnóstico e sua interpretação depende de como o rótulo foi construído.\n',
      'Os dados e candidatos não demonstram causalidade. Grande diferença entre A e B pode refletir a proximidade dos achados de exame com o rótulo; não prova circularidade nem desempenho real de triagem. A inclusão de contexto também depende de sua disponibilidade no momento pretendido.\n',
      '## Arquivos e incerteza\n','Os três pipelines finais ajustados ficam em `models/`, com metadados de versões/features/protocolo. Eles esperam os dados tratados com a política explícita de qualidade já aplicada, não o CSV bruto. `candidatos_cv.csv`, `metricas_folds.csv` e `previsoes_oof.csv` registram todos os candidatos. `selecoes_congeladas_antes_teste.json` foi escrito antes das métricas de teste. `intervalos_bootstrap_grupos.json` contém ICs percentis de500 reamostragens de grupos candidatos, condicionados ao modelo ajustado; não incluem toda a incerteza do treino/seleção nem resolvem identidade de paciente desconhecida. Desvio entre folds não é IC. AP é average precision, não área trapezoidal PR.\n',
      '`subgrupos_teste.csv` mostra suporte, erros e recall por sexo, idade, ausências e sopro. Só grupos com n≥20 aparecem; suporte positivo baixo é explicitamente sinalizado. Intervalos Wilson de recall são descritivos por linha, sem correção de grupo. São pistas para investigação, não evidência causal.\n',
      '## Sensibilidades no desenvolvimento\n','São comparações exploratórias do candidato fixo, sem voltar ao teste para escolher regras. Incluem medidas suspeitas preservadas, sem indicadores, sem IMC e sem PPA quando presente; log somente quando candidato logístico escolhido.\n',
      '| Cenário | Variante | Balancedaccuracy CV | DP folds |','|---|---|---:|---:|']
    for _,r in sens.iterrows():text.append(f'| {r.scenario} | {r.variant} | {r.cv_balanced_accuracy_mean:.4f} | {r.cv_balanced_accuracy_sd:.4f} |')
    text+=['\n## Tempo sob hipótese histórica\n','A coluna de data é hipótese de século/janela2003–2010, não data estabelecida. Corte2009-01-01 fixado previamente; sem novo tuning. Os hiperparâmetros foram escolhidos no CV do desenvolvimento global, que inclui datas posteriores ao corte; portanto a seleção não é puramente prospectiva. Essa avaliação é secundária, não independente das escolhas anteriores nem validação cronológica confirmada.\n']
    for s,m in temporal.items():
        met=m.get('metrics');text.append(f'- {s}: treino={m["n_train"]}, teste={m["n_test"]}, sem data hipotética={m["n_no_hypothesis_date"]}, grupos cruzados={m["crossing_candidate_groups"]}; balancedaccuracy={met["balanced_accuracy"]:.4f}.' if met else f'- {s}: não executado ({m.get("not_executed_reason")}).')
    text+=['\n## Limites e próximos passos\n','Não há percentis clínicos não verificados, reclassificação de HAS, SMOTE ou interpretação de importância como causa. Permutação usa modelo ajustado em quatro folds e avaliação no quinto do desenvolvimento, com seleção anterior por CV; é exploração pós-seleção. Importâncias por impureza/coeficientes do modelo completo são descritivos.\n','Continuam necessárias confirmação da semântica do alvo/ID, momento de registro de contexto e rubrica atualizada da A2. A ausência de resposta não impede reprodução acadêmica; impede alegações de eficácia clínica e de identidade amostral confirmada.\n',f'Tempo registrado: {meta["elapsed_seconds"]}s. Protocolo SHA256: `{meta["protocol_sha256"]}`.']
    (root/'docs/RESULTADOS_EXPERIMENTOS.md').write_text('\n'.join(text))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=PROJECT_ROOT);args=parser.parse_args();run_experiments(args.root)

if __name__=='__main__':main()
