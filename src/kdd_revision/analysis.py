# Historical exploratory reference retained for reproducibility; current A2 preprocessing uses kdd_revision.preprocessing.
"""Reproducible descriptive audit of all original columns, without model tuning.

Run explicitly: python -m kdd_revision.analysis. Import does not write files.
"""
from pathlib import Path
import json
import math
from hashlib import sha256
import numpy as np
import pandas as pd
from scipy import stats
from .schema import ORIGINAL, NUMERIC, CATEGORICAL, TARGET, PROJECT_ROOT, SOURCE_DEFAULT
from .prepare import safe_model_frame


def numeric_summary(s):
    values=pd.to_numeric(s,errors='coerce').replace([np.inf,-np.inf],np.nan).dropna()
    return {'n_numeric':len(values),'mean':values.mean(),'median':values.median(),
            'sd':values.std(),'min':values.min(),'q1':values.quantile(.25),
            'q3':values.quantile(.75),'max':values.max()}


def variable_profiles(frame, name, raw=False):
    records=[]
    for col in ORIGINAL:
        if col not in frame:
            records.append({'dataset':name,'variable':col,'present':False,'n_rows':len(frame)})
            continue
        s=frame[col]
        missing=s.astype(str).str.strip().eq('') if raw else s.isna()
        row={'dataset':name,'variable':col,'present':True,'n_rows':len(frame),
             'missing_definition':'literal_blank_only' if raw else 'explicit_null',
             'missing_n':int(missing.sum()),'missing_pct':100*missing.mean(),
             'distinct_nonmissing':int(s[~missing].nunique()),'dtype':str(s.dtype)}
        if col in NUMERIC:row.update(numeric_summary(s))
        records.append(row)
    return pd.DataFrame(records)


def categorical_frequencies(frame,name,raw=False):
    records=[]
    for c in CATEGORICAL:
        if c not in frame:continue
        s=frame[c].astype(object)
        if raw:s=s.map(lambda x:'__VAZIO_LITERAL__' if str(x).strip()=='' else str(x))
        else:s=s.where(s.notna(),'__AUSENTE__')
        for value,n in s.value_counts(dropna=False).items():
            records.append({'dataset':name,'variable':c,'category':str(value),'n':int(n),'denominator':len(frame),'pct':100*n/len(frame)})
    return pd.DataFrame(records)


def paired_correlations(raw, revised):
    """Isolate cell transformations by holding IDs fixed for each pair comparison."""
    a=raw.set_index('ID'); b=revised.set_index('ID'); common=a.index.intersection(b.index)
    records=[]
    for x,y in [('Altura','IDADE'),('Peso','Altura'),('Peso','IDADE')]:
        before=a.loc[common,[x,y]].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
        after=b.loc[common,[x,y]].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
        mask=before.notna().all(axis=1)&after.notna().all(axis=1)
        for stage,frame in [('raw_numeric_as_received',before),('revised_safe',after)]:
            p=frame.loc[mask]
            records.append({'x':x,'y':y,'stage':stage,'same_ids_n':len(p),
                            'pearson':p[x].corr(p[y]) if len(p)>1 else np.nan,
                            'spearman':p[x].corr(p[y],method='spearman') if len(p)>1 else np.nan,
                            'interpretation':'descriptive_same_ids_not_proof_of_correction'})
    return pd.DataFrame(records)


def bivariate_numeric(frame):
    records=[]
    for c in NUMERIC:
        a=frame.loc[frame[TARGET]=='Anormal',c].dropna().astype(float)
        n=frame.loc[frame[TARGET]=='Normal',c].dropna().astype(float)
        row={'variable':c,'n_anormal':len(a),'n_normal':len(n),'missing_anormal':int(((frame[TARGET]=='Anormal')&frame[c].isna()).sum()),'missing_normal':int(((frame[TARGET]=='Normal')&frame[c].isna()).sum()),'mean_anormal':a.mean(),'mean_normal':n.mean(),'median_anormal':a.median(),'median_normal':n.median(),'mean_difference_anormal_minus_normal':a.mean()-n.mean()}
        if min(len(a),len(n))>1:
            test=stats.ttest_ind(a,n,equal_var=False)
            va=a.var(ddof=1)/len(a);vn=n.var(ddof=1)/len(n);se=math.sqrt(va+vn)
            df=(va+vn)**2/(va**2/(len(a)-1)+vn**2/(len(n)-1)) if va+vn else np.nan
            delta=a.mean()-n.mean();critical=stats.t.ppf(.975,df) if np.isfinite(df) else np.nan
            pooled=math.sqrt(((len(a)-1)*a.var(ddof=1)+(len(n)-1)*n.var(ddof=1))/(len(a)+len(n)-2))
            row.update(welch_t=float(test.statistic),p_exploratory=float(test.pvalue),welch_df=df,mean_difference_ci95_low=delta-critical*se,mean_difference_ci95_high=delta+critical*se,cohen_d_pooled=(delta/pooled if pooled else np.nan))
        records.append(row)
    return pd.DataFrame(records)


def bivariate_categorical(frame):
    rows=[]; counts=[]
    for c in CATEGORICAL:
        if c==TARGET or c not in frame:continue
        cat=frame[c].astype(object).where(frame[c].notna(),'__AUSENTE__')
        tab=pd.crosstab(cat,frame[TARGET]).reindex(columns=['Normal','Anormal'],fill_value=0)
        for name,row in tab.iterrows():
            total=int(row.sum());counts.append({'variable':c,'category':name,'normal_n':int(row['Normal']),'anormal_n':int(row['Anormal']),'total':total,'anormal_pct':100*row['Anormal']/total})
        row={'variable':c,'n':int(tab.to_numpy().sum()),'categories':len(tab)}
        if min(tab.shape)>1 and (tab.sum(axis=0)>0).all():
            chi,p,dof,expected=stats.chi2_contingency(tab,correction=False)
            adequate=bool(expected.min()>=1 and (expected<5).mean()<=.2)
            row.update(chi2=chi,dof=dof,min_expected=expected.min(),pct_cells_expected_lt5=100*(expected<5).mean(),asymptotic_conditions_met=adequate,p_asymptotic_if_adequate=p if adequate else np.nan,cramers_v_descriptive=math.sqrt(chi/(tab.to_numpy().sum()*min(tab.shape[0]-1,tab.shape[1]-1))))
        else:
            row.update(test_status='not_testable_single_class_or_category',asymptotic_conditions_met=False,p_asymptotic_if_adequate=np.nan)
        rows.append(row)
    return pd.DataFrame(rows),pd.DataFrame(counts)


def missing_by_group(frame,group,label):
    rows=[]
    for value,idx in group.groupby(group,dropna=False).groups.items():
        sub=frame.loc[idx]
        for col in ORIGINAL:
            rows.append({'grouping':label,'group':str(value),'variable':col,'n_rows':len(sub),'missing_n':int(sub[col].isna().sum()),'missing_pct':100*sub[col].isna().mean()})
    return pd.DataFrame(rows)


def _json_safe(value):
    if isinstance(value,dict):return {str(k):_json_safe(v) for k,v in value.items()}
    if isinstance(value,list):return [_json_safe(v) for v in value]
    if isinstance(value,(np.integer,)):return int(value)
    if isinstance(value,(np.floating,float)) and not np.isfinite(value):return None
    if isinstance(value,np.floating):return float(value)
    return value


def run_analysis(project_root=PROJECT_ROOT):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    root=Path(project_root);out=root/'artifacts/analysis';fig=out/'figures';fig.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(SOURCE_DEFAULT,dtype=str,keep_default_na=False)
    treated=pd.read_csv(root/'artifacts/prepared/dados_tratados.csv',dtype={'ID':str},low_memory=False)
    safe=safe_model_frame(treated)
    eligibility=pd.read_csv(root/'artifacts/prepared/elegibilidade.csv',dtype={'ID':str})
    historic=pd.read_csv(root.parent/'Atividades Praticas/Atividades Resolvidas/saida/UCMF_final.csv',dtype={'ID':str})
    eligible_ids=eligibility.loc[eligibility.elegivel_principal,'ID'];base=safe[safe.ID.isin(eligible_ids)].copy()
    profiles=pd.concat([variable_profiles(raw,'raw',True),variable_profiles(treated,'treated_all'),variable_profiles(safe,'safe_all'),variable_profiles(base,'safe_eligible'),variable_profiles(historic,'historical_A1')],ignore_index=True)
    profiles.to_csv(out/'perfil_21_variaveis.csv',index=False)
    freqs=pd.concat([categorical_frequencies(raw,'raw',True),categorical_frequencies(treated,'treated_all'),categorical_frequencies(base,'safe_eligible'),categorical_frequencies(historic,'historical_A1')],ignore_index=True);freqs.to_csv(out/'categorias_completas.csv',index=False)
    pairs=paired_correlations(raw,safe);pairs.to_csv(out/'antropometria_mesmos_ids.csv',index=False)
    numeric=bivariate_numeric(base);numeric.to_csv(out/'bivariadas_numericas.csv',index=False)
    cat,cat_counts=bivariate_categorical(base);cat.to_csv(out/'bivariadas_categoricas.csv',index=False);cat_counts.to_csv(out/'contingencias_completas.csv',index=False)
    missing_by_group(base,base[TARGET],'target').to_csv(out/'ausencias_por_alvo.csv',index=False)
    periods=treated['meta_Atendimento_hypothesis_2003_2010'].str[:4].fillna('SEM_DATA_HIPOTESE')
    missing_by_group(safe,periods,'year_historical_assumption_not_confirmed').to_csv(out/'ausencias_por_periodo_hipotetico.csv',index=False)
    flag_cols=[c for c in treated if c.startswith('flag_')]
    pd.DataFrame([{'flag':c,'n':int(treated[c].sum()),'pct':100*treated[c].mean()} for c in flag_cols]).to_csv(out/'flags_qualidade.csv',index=False)
    current=base.set_index('ID');old=historic.set_index('ID');common=current.index.intersection(old.index)
    compare=[]
    for c in ORIGINAL:
        if c in ['ID'] or c not in old:continue
        a=current.loc[common,c];b=old.loc[common,c]
        item={'variable':c,'same_ids_n':len(common),'missing_revised':int(a.isna().sum()),'missing_historical':int(b.isna().sum())}
        if c in NUMERIC:
            av=pd.to_numeric(a,errors='coerce');bv=pd.to_numeric(b,errors='coerce');both=av.notna()&bv.notna()
            item['different_valid_values']=int((~np.isclose(av[both],bv[both],equal_nan=True)).sum())
        compare.append(item)
    pd.DataFrame(compare).to_csv(out/'comparacao_historico_mesmos_ids.csv',index=False)
    summary={'n_raw':len(raw),'n_treated':len(treated),'n_eligible':len(base),'n_historical':len(historic),'common_ids_historical':len(common),'revised_only_ids':len(current.index.difference(old.index)),'historical_only_ids':len(old.index.difference(current.index)),'target_counts':base[TARGET].value_counts().to_dict(),'numeric_features':NUMERIC,'categorical_features_includes_context':CATEGORICAL,'paired_correlations':pairs.to_dict('records'),'date_unambiguous_counts':{c:int(treated[c].notna().sum()) for c in ['Atendimento','DN']},'temporal_hypothesis_covered':int(treated.meta_Atendimento_hypothesis_2003_2010.notna().sum()),'clinical_derivatives_status':{'imc_arithmetic':'executed_if_parents_valid','cdc_percentiles':'not_executed_official_data_download_unverified','fc_percentiles':'not_executed_full_reference_unverified','ppa_recalculated':'not_executed_height_percentile_bridge_unverified','ppa_historical':'preserved_scenarios_A_B_contexto_only'},'warnings':['Exploratory comparisons; all source already examined in A1.','Welch tests mean differences, not medians. Cramer V is descriptive; p omitted if expected counts insufficient.','Time hypothesis is not an authenticated chronology.','Historical quality envelopes are assumptions, not clinical truths.','No diagnostics, clinical validation, or predictive improvement proved by EDA.']}
    (out/'analysis_summary.json').write_text(json.dumps(_json_safe(summary),ensure_ascii=False,indent=2,allow_nan=False))
    # Readable figures with fixed dimensions; no row identifiers shown.
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig1,ax=plt.subplots(figsize=(10,7));m=100*base[ORIGINAL].isna().mean().sort_values();ax.barh(m.index,m.values,color='#27647b');ax.set(xlabel='% de ausentes — população elegível revisada',xlim=(0,105),title=f'Cobertura dos 21 campos (n={len(base):,})');fig1.tight_layout();fig1.savefig(fig/'ausencias_21_variaveis.png',dpi=160);plt.close(fig1)
    fig2,axs=plt.subplots(1,2,figsize=(11,4));
    for ax,data,label in zip(axs,[raw,safe],['Bruto: numéricos como recebidos','Revisado: política segura']):
        a=pd.to_numeric(data.IDADE,errors='coerce');h=pd.to_numeric(data.Altura,errors='coerce');mask=a.notna()&h.notna();ax.scatter(a[mask],h[mask],s=4,alpha=.18,color='#27647b');ax.set(xlabel='Idade (anos)',ylabel='Altura (cm)',title=f'{label}\npares disponíveis n={int(mask.sum()):,}')
    fig2.suptitle('Amostras diferentes neste painel; comparação pareada está na tabela');fig2.tight_layout();fig2.savefig(fig/'altura_idade_contexto.png',dpi=160);plt.close(fig2)
    fig3,axs=plt.subplots(2,4,figsize=(13,7));
    for ax,col in zip(axs.ravel(),NUMERIC):
        vals=[base.loc[base[TARGET]==k,col].dropna() for k in ['Normal','Anormal']];ax.boxplot(vals,tick_labels=['Normal','Anormal'],showfliers=False);ax.set(title=col,ylabel={'Peso':'kg','Altura':'cm','IMC':'kg/m²','IDADE':'anos','PA SISTOLICA':'mmHg','PA DIASTOLICA':'mmHg','FC':'bpm'}[col]);ax.text(.5,.02,f'n={len(vals[0])}/{len(vals[1])}',ha='center',transform=ax.transAxes,fontsize=8)
    axs.ravel()[-1].axis('off');fig3.suptitle('Política segura por alvo: pontos fora dos bigodes ocultos apenas na figura');fig3.tight_layout();fig3.savefig(fig/'numericas_por_alvo.png',dpi=160);plt.close(fig3)
    fig4,ax=plt.subplots(figsize=(8,4));counts=base[TARGET].value_counts().reindex(['Normal','Anormal']);ax.bar(counts.index,counts.values,color=['#27647b','#b44e39']);ax.set(ylabel='Linhas',title='População revisada: mesma composição para os cenários A e B');
    for i,v in enumerate(counts):ax.text(i,v+40,f'{v:,} ({100*v/len(base):.1f}%)',ha='center')
    ax.set_ylim(0,max(counts)*1.15);fig4.tight_layout();fig4.savefig(fig/'populacao_alvo.png',dpi=160);plt.close(fig4)
    docs=root/'docs';docs.mkdir(exist_ok=True)
    lines=['# Análise da A1 revisada','', 'Gerada diretamente das tabelas em `artifacts/analysis`. Não é evidência de melhora preditiva ou validação clínica.','',f'Bruto: **{len(raw):,}** linhas. Tratado: **{len(treated):,}**, sem eliminar registros. Elegíveis para experimentos: **{len(base):,}**, apenas alvo conhecido. A entrega histórica tinha **{len(historic):,}** linhas. A versão revisada recupera para a análise {len(current.index.difference(old.index))} linhas anteriormente excluídas; isso não as declara pacientes diferentes nem prova que a deduplicação antiga era errada em todos os casos.','', '## Decisões e cobertura','', 'A política principal mascara valores suspeitos pelos envelopes históricos, preservando-os na base tratada. Esses envelopes são hipóteses de qualidade, não verdade clínica. A sensibilidade conservadora mantém os valores suspeitos. Não há quantis amostrais apagando idade, peso ou altura.','',f'Datas inequívocas reconhecidas: Atendimento {summary["date_unambiguous_counts"]["Atendimento"]}, nascimento {summary["date_unambiguous_counts"]["DN"]}. A coluna temporal hipotética cobre {summary["temporal_hypothesis_covered"]} linhas e usa explicitamente a janela histórica; não equivale a data confirmada. A idade usa fonte original válida, idade textual explícita ou datas inequívocas conforme proveniência.','', '## Comparação antropométrica pareada','', '| Par | Etapa | Mesmos IDs | Pearson | Spearman |','|---|---|---:|---:|---:|']
    for row in pairs.to_dict('records'):lines.append(f'| {row["x"]} × {row["y"]} | {row["stage"]} | {row["same_ids_n"]} | {row["pearson"]:.3f} | {row["spearman"]:.3f} |')
    lines+=['','Nessa tabela, os IDs são mantidos entre antes/depois em cada par. Diferentes pares podem ter conjuntos diferentes. Correlação maior não prova correção dos dados. O gráfico de contexto mostra a população disponível de cada etapa e não isola efeito de células.','', '## Bivariadas e testes','', 'As tabelas numéricas informam n por classe, média, mediana, diferença de médias Anormal−Normal, intervalo de Welch e tamanho de efeito padronizado. O teste de Welch testa médias; não interpretar seu p como teste das medianas. São explorações sem controle confirmatório de multiplicidade e sem pressupor causalidade ou independência perfeita de pacientes.','', 'As tabelas categóricas incluem todas as categorias, inclusive ausência, e publicam esperadas. O p assintótico fica ausente quando há esperadas menores que 1 ou mais de 20% menores que 5. O V de Cramér continua descritivo. Categoria rara não é descartada automaticamente por frequência.','', '## Transformações prontas para treino','', '`build_preprocessor(feature_names, scale=True, add_missing=True, log=False)` cria um pré-processador novo e não ajustado. Todas as estatísticas são aprendidas pelo fit em treino/fold. Numéricas: mediana e indicador opcional, log1p opcional somente não negativo, escala opcional. Categóricas: ausência explícita e one-hot com categorias desconhecidas ignoradas. Campos inteiramente ausentes são mantidos com política documentada.','', 'Os cenários são listas explícitas: A inclui contexto e exame; B contém apenas medidas e SEXO; B_contexto é ablação adicional. Metadados, IDs, datas, alvo e flags não entram por inferência de dtype. Indicadores de ausência são parte experimental e precisam de ablação.','', '## Derivados clínicos','', 'IMC aritmético está disponível quando seus pais têm qualidade adequada. Percentis CDC e FC não foram executados: arquivos externos completos ainda não foram validados. A transcrição da tabela histórica de pressão passou na comparação de 1.904 valores, mas falta uma ponte verificada de centímetros para percentil de estatura. Não recalculamos PPA nem inventamos percentil; preservamos o PPA histórico apenas nos cenários permitidos.','', '## Tabelas e figuras','', '- `perfil_21_variaveis.csv`: cobertura e estatística por etapa para todas as 21 variáveis, inclusive campo retirado historicamente. No bruto, ausência literal não inclui todas as sentinelas.','- `categorias_completas.csv`: todas as grafias/categorias por etapa, contagem e denominador.','- `comparacao_historico_mesmos_ids.csv`: mesmos indivíduos identificados pelo ID do recorte, sem afirmar unidade paciente/consulta.','- `bivariadas_numericas.csv`, `bivariadas_categoricas.csv`, `contingencias_completas.csv`: estatísticas e suporte.','- `ausencias_por_alvo.csv` e `ausencias_por_periodo_hipotetico.csv`: associações de cobertura, não mecanismo causal de ausência.','- `flags_qualidade.csv`: contagens de suspeitas; flags podem se sobrepor.','- `figures/`: cobertura, antropometria, distribuições por alvo e composição populacional.','', 'O próximo passo é fixar cenários, grupos e partições antes de comparar algoritmos. O relatório detalhado da A2 deve preservar as limitações da identidade e do momento de coleta do alvo.']
    (docs/'ANALISE_A1_REVISADA.md').write_text('\n'.join(lines)+'\n')
    inputs=[Path(SOURCE_DEFAULT),root/'artifacts/prepared/dados_tratados.csv',root/'artifacts/prepared/elegibilidade.csv',root.parent/'Atividades Praticas/Atividades Resolvidas/saida/UCMF_final.csv',Path(__file__),Path(__file__).with_name('transforms.py'),root/'config/schema.json']
    def fingerprint(path):
        return {'path':str(path),'sha256':sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    manifest={'inputs':[fingerprint(p) for p in inputs], 'outputs':[fingerprint(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='analysis_manifest.json']+[fingerprint(docs/'ANALISE_A1_REVISADA.md')], 'note':'Exact input/code/output hashes for this run; no scientific-validity claim.'}
    (out/'analysis_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return summary


if __name__=='__main__':
    result=run_analysis()
    print(json.dumps({k:result[k] for k in ['n_raw','n_treated','n_eligible','n_historical','common_ids_historical','date_unambiguous_counts','clinical_derivatives_status']},ensure_ascii=False,indent=2))
