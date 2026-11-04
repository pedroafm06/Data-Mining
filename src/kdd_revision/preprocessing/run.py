"""Export the actually applied final A2, without fitting predictive models."""
from pathlib import Path
from hashlib import sha256
import json,joblib
import numpy as np,pandas as pd
from .preparation import prepare_final,model_frame
from .transformer import AppliedPreprocessor
from .diagnostics import run as diagnose
from ..schema import ORIGINAL,NUMERIC,SCENARIOS,SOURCE_DEFAULT,PARTITIONS_DEFAULT,EXPECTED_SOURCE_SHA256,PROJECT_ROOT
ROOT=PROJECT_ROOT

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False))
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()

def serial(v):
    if isinstance(v,dict):return {str(k):serial(x) for k,x in v.items()}
    if isinstance(v,list):return [serial(x) for x in v]
    if isinstance(v,(np.integer,)):return int(v)
    if isinstance(v,(np.floating,)):return None if not np.isfinite(v) else float(v)
    if isinstance(v,float) and not np.isfinite(v):return None
    return v

def export_matrix(out,frame,name,ids,partitions):
    path=out/(name+'.csv');frame.to_csv(path,index=False,float_format='%.17g')
    # ID and y stay separate: matrix rows are aligned with mapa_linhas.csv.
    for partition in ['development','test','unlabeled','quarentena_equivalencia']:
        mask=np.array(partitions)==partition
        frame.loc[mask].to_csv(out/(name+'_'+partition+'.csv'),index=False,float_format='%.17g')
    return {'file':path.name,'n_rows':len(frame),'n_columns':frame.shape[1],'sha256':digest(path)}

def validated_source(source):
    source=Path(source).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f'Clinical CSV not found: {source}. Supply --source /path/to/UCMF_raw.csv; raw clinical data is not distributed in Git.')
    observed=digest(source)
    if observed!=EXPECTED_SOURCE_SHA256:
        raise ValueError(f'Clinical source SHA-256 mismatch: expected {EXPECTED_SOURCE_SHA256}, got {observed}. Stop and inspect the input; this pipeline is validated for the specified case-study source.')
    return source,observed


def validated_partitions(path,raw):
    path=Path(path).expanduser().resolve()
    if not path.is_file():raise FileNotFoundError(f'Partition reference not found: {path}. Supply --partitions or restore config/particoes_referencia.csv.')
    part=pd.read_csv(path,dtype={'ID':str},keep_default_na=False)
    if not {'ID','partition'}<=set(part):raise ValueError('Partition CSV requires ID and partition columns')
    if part.ID.eq('').any() or part.ID.str.strip().ne(part.ID).any() or part.ID.duplicated().any():raise ValueError('Partition IDs must be nonempty, exact and unique')
    if set(part.partition)!= {'development','test'}:raise ValueError('Partition reference must contain development and test only')
    if not set(part.ID)<=set(raw.ID.astype(str)):raise ValueError('Partition ID is absent from the clinical source')
    return path,part


def run_preprocessing(root=ROOT,source=SOURCE_DEFAULT,partitions=PARTITIONS_DEFAULT,output_dir=None):
    root=Path(root).expanduser().resolve()
    source,initial_hash=validated_source(source)
    raw=pd.read_csv(source,dtype=str,keep_default_na=False)
    partitions_path,part=validated_partitions(partitions,raw)
    prepared=prepare_final(raw);data=prepared.data
    expected_ids=set(data.loc[data['NORMAL X ANORMAL'].isin(['Normal','Anormal']),'ID'].astype(str))
    if set(part.ID)!=expected_ids:raise ValueError('Partition reference must cover exactly all source records with a known target; no missing, extra or unlabeled memberships are allowed')
    out=Path(output_dir).expanduser().resolve() if output_dir is not None else root/'artifacts/a2_preprocessing'
    out.mkdir(parents=True,exist_ok=True)
    data[ORIGINAL].to_csv(out/'base_semantica.csv',index=False,float_format='%.17g')
    provenance=data[['ID']+[c for c in data if c.startswith(('meta_','flag_'))]]
    provenance.to_csv(out/'proveniencia.csv',index=False,float_format='%.17g')
    prepared.changes.to_csv(out/'alteracoes.csv',index=False,float_format='%.17g')
    prepared.groups.to_csv(out/'grupos_recalculados.csv',index=False)
    prepared.eligibility.to_csv(out/'elegibilidade.csv',index=False)
    safe=model_frame(data);safe[ORIGINAL].to_csv(out/'base_para_transformacao.csv',index=False,float_format='%.17g')
    safe.to_csv(out/'_diagnostic_input.csv',index=False,float_format='%.17g')
    pmap=part.set_index('ID').partition
    rowmap=pd.DataFrame({'row_number':np.arange(len(data)),'ID':data.ID.astype(str),'partition':data.ID.astype(str).map(pmap).fillna('unlabeled'),
                        'y':data['NORMAL X ANORMAL'].map({'Normal':0,'Anormal':1}).astype('Int64')})
    rowmap['source_partition']=rowmap.partition
    if rowmap.loc[rowmap.partition.ne('unlabeled'),'y'].isna().any():raise ValueError('Known-label partition lost y')
    # Group check uses predictors only and is performed before any statistics fit.
    features=SCENARIOS['A']
    signatures=pd.util.hash_pandas_object(safe[features],index=False).astype(str)
    n_present=safe[features].notna().sum(axis=1)
    eq=pd.DataFrame({'ID':safe.ID.astype(str),'source_partition':rowmap.partition,'hash':signatures,'n_present':n_present})
    informative=eq[(eq.n_present>=8)&eq.source_partition.isin(['development','test'])]
    crossing=informative.groupby('hash').source_partition.nunique()
    cross_hashes=set(crossing[crossing>1].index)
    conflicts=informative[informative.hash.isin(cross_hashes)]
    quarantine=rowmap.source_partition.eq('development') & signatures.isin(cross_hashes)
    rowmap.loc[quarantine,'partition']='quarentena_equivalencia'
    rowmap['adjustment_reason']=np.where(quarantine,'candidate_equivalence_with_frozen_test_no_identity_claim','unchanged')
    rowmap.to_csv(out/'mapa_linhas.csv',index=False)
    rowmap.to_csv(out/'particoes_ajuste.csv',index=False)
    # Targets and identifiers align exactly with each partition matrix row order.
    for partition in ['development','test','unlabeled','quarentena_equivalencia']:
        member=rowmap.partition.eq(partition)
        rowmap.loc[member,['ID']].to_csv(out/('ids_'+partition+'.csv'),index=False)
        if partition!='unlabeled':rowmap.loc[member,['y']].to_csv(out/('y_'+partition+'.csv'),index=False)
    part.to_csv(out/'particoes_congeladas.csv',index=False)
    conflicts.to_csv(out/'equivalencias_candidatas_cruzando_particoes.csv',index=False)
    after=pd.DataFrame({'hash':signatures,'partition':rowmap.partition,'n_present':n_present})
    after=after[(after.n_present>=8)&after.partition.isin(['development','test'])]
    if after.groupby('hash').partition.nunique().gt(1).any():raise AssertionError('A2 fit/test candidate overlap after quarantine')
    diag=diagnose(out/'_diagnostic_input.csv',out/'particoes_ajuste.csv',out/'diagnostics')
    comparison=pd.read_csv(out/'diagnostics/imputation_alternatives.csv')
    means=comparison.groupby(['column','method']).MAE.mean().unstack()
    choices={};age_columns=[]
    # Rules fixed before corrected-age diagnostic: simplicity; group effect >=10%,
    # improvement in >=4/5 repeats; sex complexity needs >=5% further reduction.
    for c in NUMERIC:
        if c=='IDADE':choices[c]={'method':'global','reason':'Do not use imputed age to construct its own stratum'};continue
        gain=float(1-means.loc[c,'age']/means.loc[c,'global'])
        reps=comparison[comparison.column.eq(c)].pivot(index='rep',columns='method',values='MAE')
        wins=int((reps.age<reps['global']).sum())
        sex_gain=float(1-means.loc[c,'age_sex']/means.loc[c,'age'])
        # Unverified BP grouping adds little in pilot and pressure missingness is high;
        # stay with simple medians unless a separately justified protocol is made.
        eligible=c in ['Peso','Altura','FC','IMC'] and gain>=.10 and wins>=4
        if eligible:age_columns.append(c)
        choices[c]={'method':'age_band' if eligible else 'global','MAE_global':float(means.loc[c,'global']),'MAE_age':float(means.loc[c,'age']),
                    'MAE_age_sex':float(means.loc[c,'age_sex']),'relative_MAE_gain_age':gain,'repetitions_improved':wins,'relative_extra_gain_sex':sex_gain,
                    'sex_used':False,'reason':'Fixed-band age conditioning with sufficient observed support' if eligible else 'Parsimony: retain simple median; age effect insufficient or BP deliberately kept simple'}
    dev_ids=rowmap.loc[rowmap.partition.eq('development'),'ID'];dev=safe.set_index('ID').loc[dev_ids].reset_index()
    transformer=AppliedPreprocessor(age_group_columns=tuple(age_columns))
    transformer.fit(dev)
    matrices={}
    for representation,name in [('units','matriz_unidades'),('standard','matriz_padronizada'),('log_weight_standard','matriz_log_peso_padronizada')]:
        matrix=transformer.transform(safe,representation=representation)
        matrices[representation]=export_matrix(out,matrix,name,data.ID,rowmap.partition)
    joblib.dump(transformer,out/'transformador_preprocessamento.joblib')
    dump(out/'parametros_transformacao.json',serial(transformer.metadata()))
    pd.DataFrame(transformer.column_dictionary_).to_csv(out/'dicionario_colunas_matrizes.csv',index=False)
    pd.DataFrame([{'variable':c,**v} for c,v in choices.items()]).to_csv(out/'decisoes_imputacao.csv',index=False)
    # Reduced view preserves parents but excludes derived BMI and very sparse HDA2.
    reduced=[c for c in SCENARIOS['A'] if c not in ['IMC','HDA2']]
    reduced_tr=AppliedPreprocessor(features=reduced,age_group_columns=tuple(c for c in age_columns if c in reduced),log_columns=('Peso',)).fit(dev)
    export_matrix(out,reduced_tr.transform(safe),'matriz_reduzida_unidades',data.ID,rowmap.partition)
    joblib.dump(reduced_tr,out/'transformador_reduzido.joblib')
    dump(out/'parametros_reduzida.json',serial(reduced_tr.metadata()))
    # Alternative quality policies: apply the SAME fit parameters, no refitting.
    historical=model_frame(data,'historical')
    export_matrix(out,transformer.transform(historical),'matriz_politica_historica_unidades',data.ID,rowmap.partition)
    global_tr=AppliedPreprocessor(age_group_columns=()).fit(dev)
    export_matrix(out,global_tr.transform(safe),'matriz_mediana_global_unidades',data.ID,rowmap.partition)
    joblib.dump(global_tr,out/'transformador_mediana_global.joblib')
    dump(out/'parametros_mediana_global.json',serial(global_tr.metadata()))
    # Alternative quality policy: apply the SAME fit parameters, preserving suspects.
    preserve=model_frame(data,'preserve_suspect')
    export_matrix(out,transformer.transform(preserve),'matriz_suspeitos_preservados_unidades',data.ID,rowmap.partition)
    summary={**prepared.summary,'stage':'A2 cleaning and transformations, no predictive model fitted',
             'n_fit':len(dev),'n_quarantine':int(quarantine.sum()),'n_test':int(rowmap.partition.eq('test').sum()),'n_unlabeled':int(rowmap.partition.eq('unlabeled').sum()),
             'matrices':matrices,'imputation_choices':choices,'log_columns':['Peso'],'scaling':'Continuous values only, ddof=0; binary/OHE columns unchanged',
             'quality_policy':'Reviewed quality policy preserves high-weight, early-short-length, positive FC<=500/PAD and observed-parent BMI exceptions; semantic values preserved and historical/preserve variants exported. Remaining masks are reliability hypotheses, not clinical error proofs.',
             'mask_counts_by_numeric':{c:int((data[c].notna()&safe[c].isna()).sum()) for c in NUMERIC},
             'n_preserved_against_historical_masks':{c:int((safe[c].notna()&model_frame(data,'historical')[c].isna()).sum()) for c in NUMERIC},
             'BMI_policy':'Observed-parent arithmetic only after joint ratio5-100 curation guard; both parents of an extreme ratio are quarantined operationally without blaming either or changing age. The entire triad is masked whenever the joint guard is triggered, including historical BMI inside the envelope; otherwise historical-only BMI outside5-100 is also quarantined. These are curation hypotheses, not clinical normal ranges; originals and preserve variant remain. Missing BMI independently imputed only in matrix.',
             'source_sha256':initial_hash,'source_path':str(source),'partition_source_path':str(partitions_path),'partition_sha256':digest(partitions_path),'uses_target_for_transform_choices':False,'models_fitted':False,
             'new_informative_equivalence_groups_crossing_frozen_partitions':len(cross_hashes),'rows_in_crossing_equivalence_groups':len(conflicts),
             'crossing_candidate_groups_after_quarantine':0,
             'adjusted_partition_sha256':digest(out/'particoes_ajuste.csv'),
             'equivalence_interpretation':'Candidate feature equivalence, not patient identity. Historical experiment membership stays unchanged; preprocessing fit member is quarantined before diagnostics/fit, test is unchanged.',
             'relative_age_requires_cohort_assumption':True,'diagnostic_limit':'Artificial masking of observed development values is not evidence for the true missingness mechanism.',
             'future_cv':'Refit imputers, vocabularies and scales inside every future training fold; frozen exported development matrix is not CV-ready.'}
    dump(out/'summary.json',serial(summary))
    policy={'version':'a2-preprocessing-1','scope':'Clean and transform only; predictive models are not fitted','development_only':True,'group_imputation_min_count':30,'quality_preservation_exceptions':{'Peso':'upper-tail >150 not removed by univariate threshold; joint triad guard takes precedence','Altura':'30<=cm<40 retained for age<0.25 or unknown unless joint triad guard','FC':'all positive <=500 retained with flags; >500 operational curation trigger, not physiological maximum','PA DIASTOLICA':'positive values retained unless PAS<=PAD','IMC':'observed-parent pair ratio outside5-100 quarantines both parents and derivative; historical-only outside5-100 or joint triad contradiction quarantined as hypothesis'},
            'age_bins':[0,.25,.5,1,2,5,10,15,20],'group_eligibility_columns':['Peso','Altura','FC','IMC'],'minimum_relative_MAE_gain':.10,'minimum_repetitions_improved':4,
            'categorical_missing':'__AUSENTE__','categorical_unseen':'__DESCONHECIDO__','binary_columns_scaled':False,'log_columns':['Peso'],
            'primary_predictors':SCENARIOS['A'],'excluded_from_primary':['ID','Atendimento','DN','Convenio','NORMAL X ANORMAL'],
            'reduced_excludes':['IMC','HDA2'],'choices':choices}
    dump(root/'config/a2_preprocessing_policy.json',serial(policy))
    # Self-check retransform from the serialized object and exact export alignment.
    restored=joblib.load(out/'transformador_preprocessamento.joblib')
    equal={}
    for representation,info in matrices.items():
        read=pd.read_csv(out/info['file'])
        recomputed=restored.transform(safe,representation=representation)
        delta=float(np.max(abs(read.to_numpy()-recomputed.to_numpy())))
        if list(read)!=list(recomputed) or read.shape!=recomputed.shape or delta>1e-10:raise AssertionError('Export differs from saved transformation')
        equal[representation]={'n_rows':len(read),'n_columns':len(read.columns),'max_abs_export_delta':delta,'finite':bool(np.isfinite(read).all().all())}
    if digest(source)!=initial_hash:raise AssertionError('Original source changed')
    checks={'source_preserved':True,'n_rows_preserved':len(data)==len(raw),'unique_IDs':data.ID.is_unique,
            'fit_development_only':transformer.n_fit_==len(dev_ids),'no_candidate_overlap_after_quarantine':True,'target_used':False,'models_fitted':False,
            'matrix_retransform':equal,'binary_columns_unchanged':True,'frozen_partitions_preserved':digest(partitions_path)==summary['partition_sha256']}
    dump(out/'verification.json',serial(checks))
    sources=[*Path(__file__).parent.glob('*.py'),root/'config/a2_preprocessing_policy.json']
    manifest={'source_input':{'path':str(source),'sha256':initial_hash},'partition_input':{'path':str(partitions_path),'sha256':digest(partitions_path)},'frozen_partition_sha256':digest(partitions_path),
              'code_config':{str(p.relative_to(root)):digest(p) for p in sources},
              'outputs':{str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file() and p.name not in ('manifest.json','A2_FINAL_MANIFESTO.json','verificacao_independente_final.json') and 'report' not in p.relative_to(out).parts}}
    dump(out/'manifest.json',manifest)
    print(json.dumps({'n_rows':len(data),'n_fit':len(dev),'n_test':summary['n_test'],'n_features':len(transformer.output_names_),
                      'relative_age_resolved':summary['n_relative_age_resolved'],'age_group_columns':age_columns,'cross_partition_candidate_groups':len(cross_hashes),
                      'export_verified':True,'models_fitted':False},ensure_ascii=False,indent=2))
    return summary

if __name__=='__main__':run_preprocessing()
