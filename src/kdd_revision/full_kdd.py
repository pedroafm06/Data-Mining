"""Complete, auditable A2: current preparation -> mining -> evaluation -> patterns.

Search and preprocessing are restricted to development. The historical test is
explicitly a previously explored secondary evaluation, not an untouched holdout.
"""
from pathlib import Path
from hashlib import sha256
import json,time,copy
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.tree import export_text
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .schema import PROJECT_ROOT,SOURCE_DEFAULT,SCENARIOS,TARGET
from .preprocessing.run import validated_source
from .preprocessing.preparation import prepare_final,model_frame
from .mining import candidates,cross_validate,select_candidate,fit_model,metric,combine_groups,digest_ids
from .experiments import bootstrap_group_ci,subgroup_summary


def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)))


def folds_for(y,groups,k=5,seed=43):
    splits=list(StratifiedGroupKFold(n_splits=k,shuffle=True,random_state=seed).split(np.zeros(len(y)),y,groups))
    for train,val in splits:
        if set(np.asarray(groups)[train])&set(np.asarray(groups)[val]):raise AssertionError('Candidate group overlap')
        if len(np.unique(np.asarray(y)[train]))<2 or len(np.unique(np.asarray(y)[val]))<2:raise ValueError('Both classes required')
    return splits


def protocol():
    return {'version':'A2-KDD-completo-v1','target':'Recorded Normal=0 / Anormal=1; not validated independent diagnosis',
        'source_sha256':'35e68400d6bec51bbf74857c0f0e0487161b3495b5f4fefbc2cc57af24824ea1',
        'scenarios':SCENARIOS,'candidates':candidates(),'candidate_count':81,
        'selection':'maximum mean CV balanced_accuracy; exact ties within 1e-12 follow listed candidate order',
        'threshold':.5,'development_cv':{'n_splits':5,'seed':43},
        'nested_cv':{'outer_folds':3,'outer_seed':52,'inner_folds':3,'inner_seed':53,'scope':'development only; inner_seed += outer fold'},
        'bootstrap':{'replications':500,'seed':44,'unit':'candidate connected component','interpretation':'conditional on fitted model; not full selection uncertainty'},
        'preprocessing':'fit imputer/vocabulary/scales inside every train fold; global/age choice part of model search',
        'groups':'union historical candidate groups + current informative exact equivalences; not confirmed patients',
        'test_policy':'same historical test; no tuning from it; selected configurations for all scenarios saved before test scores',
        'history':'quality choices and full cohort were previously explored; nested CV evaluates frozen search conditional on those choices, not the entire KDD selection',
        'sensitivity':'development only, fixed selected configuration: preserve suspects; remove indicators/IMC/HDA2/IMC+HDA2/PPA; random over/under sampling; PCA95 on best logistic',
        'use':'offline application to unlabeled rows; abstain when no predictor is available; predictions never become training labels',
        'temporal':'not executed: ambiguous absolute centuries do not establish temporal validation'}


def tree_rules(bundle,x,y):
    z=bundle.matrix(x);leaves=bundle.classifier.apply(z);rows=[];tree=bundle.classifier.tree_
    def walk(node,path):
        if tree.children_left[node]==tree.children_right[node]:
            member=leaves==node;yy=np.asarray(y)[member]
            rows.append({'leaf':int(node),'rule':' AND '.join(path) or 'all', 'n_development':int(member.sum()),
                'normal':int((yy==0).sum()),'anormal':int((yy==1).sum()),'observed_anormal_fraction':float(yy.mean()),
                'note':'actual observed counts, distinct from class-weighted node probabilities; descriptive training pattern'})
            return
        feature=bundle.columns[tree.feature[node]];threshold=tree.threshold[node]
        walk(tree.children_left[node],path+[f'{feature} <= {threshold:.6g}'])
        walk(tree.children_right[node],path+[f'{feature} > {threshold:.6g}'])
    walk(0,[]);return pd.DataFrame(rows)


def figures(metrics,predictions,y,out):
    out.mkdir(exist_ok=True)
    from sklearn.metrics import roc_curve,precision_recall_curve
    fig,axes=plt.subplots(1,3,figsize=(11,3.5))
    for ax,(scenario,m) in zip(axes,metrics.items()):
        a=np.array([[m['tn'],m['fp']],[m['fn'],m['tp']]])
        ax.imshow(a,cmap='Blues');ax.set_xticks([0,1],['Normal','Anormal']);ax.set_yticks([0,1],['Normal','Anormal'])
        for (i,j),value in np.ndenumerate(a):ax.text(j,i,str(value),ha='center',va='center',color='white' if value>a.max()*.55 else 'black')
        ax.set(xlabel='Previsto',ylabel='Rótulo registrado',title=scenario)
    fig.suptitle('Teste histórico explorado - limiar fixo 0,5');fig.tight_layout();fig.savefig(out/'confusoes.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.8))
    for scenario,p in predictions.items():
        fpr,tpr,_=roc_curve(y,p);precision,recall,_=precision_recall_curve(y,p)
        axes[0].plot(fpr,tpr,label=scenario);axes[1].plot(recall,precision,label=scenario)
    axes[0].plot([0,1],[0,1],'--',color='gray');axes[1].axhline(np.mean(y),ls='--',color='gray',label='Prevalência')
    axes[0].set(xlabel='Taxa de falsos positivos',ylabel='Recall',title='ROC');axes[1].set(xlabel='Recall',ylabel='Precisão',title='Precisão-Recall')
    for ax in axes:ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'curvas.png',dpi=170);plt.close(fig)


def run_mining(root=PROJECT_ROOT,source=SOURCE_DEFAULT):
    root=Path(root);source,source_hash=validated_source(source);out=root/'artifacts/a2_mining';out.mkdir(parents=True,exist_ok=True)
    (out/'verification.json').unlink(missing_ok=True);start=time.monotonic()
    policy=protocol();options=policy['candidates'];write(root/'config/a2_kdd_protocol.json',policy)
    protocol_hash=sha256(json.dumps(policy,sort_keys=True).encode()).hexdigest()
    raw=pd.read_csv(source,dtype=str,keep_default_na=False)
    semantic=prepare_final(raw).data;safe=model_frame(semantic)
    mapping=pd.read_csv(root/'artifacts/a2_preprocessing/mapa_linhas.csv',dtype={'ID':str})
    if safe.ID.tolist()!=mapping.ID.tolist():raise ValueError('Preparation/map order mismatch')
    reference=pd.read_csv(root/'config/particoes_referencia.csv',dtype={'ID':str})
    groups=combine_groups(safe,reference);test_mask=mapping.partition.eq('test');dev_mask=mapping.partition.eq('development')
    crossing=set(groups[dev_mask])&set(groups[test_mask]);extra=dev_mask&groups.isin(crossing)
    dev_mask=dev_mask&~extra
    dev=safe.loc[dev_mask,['ID']+SCENARIOS['A']].reset_index(drop=True)
    test=safe.loc[test_mask,['ID']+SCENARIOS['A']].reset_index(drop=True)
    y=safe.loc[dev_mask,TARGET].map({'Normal':0,'Anormal':1}).to_numpy();yt=safe.loc[test_mask,TARGET].map({'Normal':0,'Anormal':1}).to_numpy()
    gd=groups[dev_mask].reset_index(drop=True);gt=groups[test_mask].reset_index(drop=True)
    if set(gd)&set(gt):raise AssertionError('Group overlap after quarantine')
    cv=folds_for(y,gd);outer=folds_for(y,gd,k=3,seed=52)
    events=[]
    def event(name,**data):events.append({'event':name,**data});write(out/'events.json',events)
    event('protocol_frozen',sha256=protocol_hash)
    group_map=pd.DataFrame({'ID':safe.ID,'group':groups,'partition':mapping.partition})
    group_map.loc[extra,'partition']='quarentena_equivalencia_componente';group_map.to_csv(out/'particoes_modelagem.csv',index=False)
    selected={};tree_selected={};all_scores=[];all_audit=[];nested_results={};cv_predictions={}
    for scenario,features in SCENARIOS.items():
        print(f'{scenario}: CV 5 folds x {len(options)} configurações',flush=True)
        scores,predictions,audit=cross_validate(dev,y,cv,options,features)
        chosen=select_candidate(scores,options);trees=[c for c in options if c['kind']=='tree'];tree_selected[scenario]=select_candidate(scores[scores.kind.eq('tree')],trees)
        selected[scenario]=chosen;cv_predictions[scenario]=predictions[chosen['name']]
        score_export=scores.drop(columns='fold_metrics').copy();score_export.insert(0,'scenario',scenario);all_scores.append(score_export)
        fold_rows=[{'scenario':scenario,**r} for rows in scores.fold_metrics for r in rows]
        pd.DataFrame(fold_rows).to_csv(out/f'folds_{scenario}.csv',index=False)
        all_audit.extend([{'scope':'selection','scenario':scenario,**a} for a in audit])
        nested=np.full(len(y),np.nan);records=[]
        for k,(train,val) in enumerate(outer):
            print(f'{scenario}: nested outer {k+1}/3',flush=True)
            xtrain=dev.iloc[train].reset_index(drop=True);inner=folds_for(y[train],gd.iloc[train].reset_index(drop=True),k=3,seed=53+k)
            score,_,aud=cross_validate(xtrain,y[train],inner,options,features);winner=select_candidate(score,options)
            bundle=fit_model(xtrain,y[train],winner,features);p=bundle.proba(dev.iloc[val]);nested[val]=p
            records.append({'outer_fold':k,'candidate':winner['name'],'n_fit':len(train),'n_validation':len(val),**metric(y[val],p)})
            all_audit.extend([{'scope':f'nested_outer_{k}','scenario':scenario,**a} for a in aud])
            write(out/f'nested_parameters_{scenario}_{k}.json',bundle.preprocessor.metadata())
        nested_results[scenario]={'pooled_oof':metric(y,nested),'outer_folds':records,
            'interpretation':'Nested development estimate of this frozen search; preprocessing quality decisions were previously explored globally'}
        pd.DataFrame({'ID':dev.ID,'y':y,'p_selected_cv':cv_predictions[scenario],'p_nested':nested}).to_csv(out/f'oof_{scenario}.csv',index=False)
        event('scenario_selection_finished',scenario=scenario,candidate=chosen['name'])
    pd.concat(all_scores).to_csv(out/'candidatos_cv.csv',index=False)
    write(out/'fold_preprocessing_audit.json',all_audit);write(out/'nested_results.json',nested_results)
    frozen={'protocol_sha256':protocol_hash,'selected':selected,'best_tree':tree_selected,'stage':'written before test scoring; no test scores used for selection'}
    write(out/'selected_before_test.json',frozen);event('all_selections_frozen')
    results={};preds={};intervals={};subgroups=[];models={};sens=[];importance=[];applications={}
    for scenario,features in SCENARIOS.items():
        chosen=selected[scenario];print(f'{scenario}: fit final + avaliação + sensibilidades',flush=True)
        bundle=fit_model(dev,y,chosen,features);models[scenario]=bundle;joblib.dump(bundle,out/f'model_{scenario}.joblib')
        write(out/f'final_parameters_{scenario}.json',{'candidate':chosen,'transformer':bundle.preprocessor.metadata()})
        p=bundle.proba(test);preds[scenario]=p;results[scenario]={'candidate':chosen['name'],**metric(yt,p)}
        pd.DataFrame({'ID':test.ID,'y':yt,'p':p,'pred':(p>=.5).astype(int)}).to_csv(out/f'predicoes_teste_{scenario}.csv',index=False)
        intervals[scenario]=bootstrap_group_ci(yt,p,gt,n_resamples=500,seed=44)
        subgroup=subgroup_summary(test,yt,p);subgroup.insert(0,'scenario',scenario);subgroups.append(subgroup)
        tree=fit_model(dev,y,tree_selected[scenario],features)
        tree_rules(tree,dev,y).to_csv(out/f'regras_arvore_{scenario}.csv',index=False)
        (out/f'arvore_{scenario}.txt').write_text(export_text(tree.classifier,feature_names=tree.columns,decimals=3,max_depth=30))
        write(out/f'tree_dictionary_{scenario}.json',tree.preprocessor.column_dictionary_)
        if chosen['kind']=='logistic':
            pd.DataFrame({'feature':bundle.columns,'coefficient':bundle.classifier.coef_[0]}).to_csv(out/f'coeficientes_{scenario}.csv',index=False)
        train,val=cv[0];explain=fit_model(dev.iloc[train],y[train],chosen,features);baseline=metric(y[val],explain.proba(dev.iloc[val]))['balanced_accuracy'];rng=np.random.default_rng(46)
        for column in features:
            effects=[]
            for repeat in range(5):
                permuted=dev.iloc[val].copy();permuted[column]=rng.permutation(permuted[column].to_numpy())
                effects.append(baseline-metric(y[val],explain.proba(permuted))['balanced_accuracy'])
            importance.append({'scenario':scenario,'variable':column,'mean_drop_balanced_accuracy':np.mean(effects),'sd_repeats':np.std(effects,ddof=1),'scope':'development validation fold 0; exploratory post-selection, not causal'})
        variants=[('principal',dev,features,{}),('suspeitos_preservados',model_frame(semantic,'preserve_suspect').loc[dev_mask,['ID']+SCENARIOS['A']].reset_index(drop=True),features,{}),
            ('sem_indicadores',dev,features,{'add_missing':False}),('sem_IMC',dev,[c for c in features if c!='IMC'],{}),
            ('sem_HDA2',dev,[c for c in features if c!='HDA2'],{}),('sem_IMC_HDA2',dev,[c for c in features if c not in ['IMC','HDA2']],{}),
            ('sem_PPA',dev,[c for c in features if c!='PPA'],{}),('sobreamostragem',dev,features,{'resampling':'over'}),('subamostragem',dev,features,{'resampling':'under'})]
        for name,data,cols,kwargs in variants:
            if cols==features and name in ['sem_HDA2','sem_PPA']:continue
            oof=np.full(len(y),np.nan);fold_values=[];actual=copy.deepcopy(chosen)
            if kwargs.get('resampling') and actual['kind']!='dummy':actual['params']['class_weight']=None
            for train,val in cv:
                fitted=fit_model(data.iloc[train],y[train],actual,cols,**kwargs);pv=fitted.proba(data.iloc[val]);oof[val]=pv;fold_values.append(metric(y[val],pv)['balanced_accuracy'])
            sens.append({'scenario':scenario,'variant':name,'candidate':actual['name'],'mean_cv_balanced_accuracy':np.mean(fold_values),'sd_cv_balanced_accuracy':np.std(fold_values,ddof=1),'pooled_cv':metric(y,oof)['balanced_accuracy'],'status':'fixed selected candidate; exploratory after selection; no test-based reselection'})
        # PCA is a tested reduction alternative for the strongest CV logistic, never a forced operation.
        logistic=select_candidate(pd.concat(all_scores).query('scenario == @scenario and kind == "logistic"'),[c for c in options if c['kind']=='logistic'])
        vals=[]
        for train,val in cv:
            fitted=fit_model(dev.iloc[train],y[train],logistic,features,pca=True);vals.append(metric(y[val],fitted.proba(dev.iloc[val]))['balanced_accuracy'])
        sens.append({'scenario':scenario,'variant':'PCA95_melhor_logistica','candidate':logistic['name'],'mean_cv_balanced_accuracy':np.mean(vals),'sd_cv_balanced_accuracy':np.std(vals,ddof=1),'status':'exploratory development only; compare to same logistic candidate without PCA'})
        unmask=mapping.partition.eq('unlabeled');unlabeled=safe.loc[unmask,['ID']+SCENARIOS['A']].reset_index(drop=True);available=unlabeled[features].notna().sum(axis=1);eligible=available.gt(0)
        scores=np.full(len(unlabeled),np.nan);scores[eligible]=bundle.proba(unlabeled.loc[eligible])
        pd.DataFrame({'ID':unlabeled.ID,'n_observed_predictors':available,'p_recorded_anormal':scores,'status':np.where(eligible,'demonstracao_sem_rotulo_confirmado','abstencao_sem_informacao')}).to_csv(out/f'aplicacao_nao_rotulados_{scenario}.csv',index=False)
        applications[scenario]={'n_unlabeled':len(unlabeled),'n_scored':int(eligible.sum()),'n_abstained':int((~eligible).sum()),'n_p_ge_half':int((scores>=.5).sum()),'not_used_for_training':True}
        event('test_evaluated',scenario=scenario)
    dummy=models[next(iter(models))];majority=int(pd.Series(y).mode().iloc[0]);constant=np.full(len(yt),majority,dtype=float)
    covered=test.SOPRO.notna().to_numpy();rule=test.loc[covered,'SOPRO'].ne('Ausente').astype(int).to_numpy()
    controls={'majority':metric(yt,constant),'sopro_rule':{'coverage':float(covered.mean()),'n':int(covered.sum()),'metrics':metric(yt[covered],rule),
        'same_coverage_models':{s:metric(yt[covered],p[covered]) for s,p in preds.items()},'interpretation':'binary fixed rule for recorded label; not independent diagnosis or calibrated probability'}}
    write(out/'test_metrics.json',results);write(out/'controls.json',controls);write(out/'intervals.json',intervals);write(out/'unlabeled_application.json',applications)
    pd.concat(subgroups).to_csv(out/'subgrupos.csv',index=False);pd.DataFrame(sens).to_csv(out/'sensibilidades.csv',index=False);pd.DataFrame(importance).to_csv(out/'importancia_permutacao.csv',index=False)
    figures(results,preds,yt,out/'figures')
    checks={'complete':True,'source_sha256':source_hash,'protocol_sha256':protocol_hash,'n_development':len(dev),'n_test':len(test),
        'extra_group_quarantine':int(extra.sum()),'groups_crossing_fit_test':0,'n_candidates_per_scenario':len(options),
        'n_preprocessing_fits_audited':len(all_audit),'all_selections_frozen_before_test':next(i for i,e in enumerate(events) if e['event']=='all_selections_frozen')<min(i for i,e in enumerate(events) if e['event']=='test_evaluated'),
        'nested_cv_complete':True,'n_scopes_scenarios':len(SCENARIOS),'source_preserved':sha256(source.read_bytes()).hexdigest()==source_hash,
        'elapsed_seconds':round(time.monotonic()-start,2),'limits':['preparation decisions previously explored globally','historical test previously explored','candidate groups are not confirmed patient identities','no clinical validation']}
    write(out/'verification.json',checks)
    code=[*list((root/'src/kdd_revision').rglob('*.py')),root/'config/a2_kdd_protocol.json']
    manifest={'source_sha256':source_hash,'protocol_sha256':protocol_hash,'code_sha256':{str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in code},
        'outputs_sha256':{str(p.relative_to(out)):sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p.name!='manifest.json'},'self_excluded':True}
    write(out/'manifest.json',manifest);print(json.dumps(checks,ensure_ascii=False,indent=2),flush=True);return checks
