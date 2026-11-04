"""Isolated final A2 preparation. Original source and historical experiment artifacts stay unchanged."""
from datetime import date
import json
from hashlib import sha256
import numpy as np
import pandas as pd
from ..prepare import prepare_dataframe,parse_date,age_literal,normalize_text
from ..schema import NUMERIC,SUSPECT_ENVELOPES

def anniversary(birth,year):
    """Calendar anniversary; February 29 uses February 28 in non-leap years."""
    try:return birth.replace(year=year)
    except ValueError:return date(year,2,28)

def calendar_age(birth,visit):
    if visit<birth:return np.nan
    completed=visit.year-birth.year
    if visit<anniversary(birth,visit.year):completed-=1
    start=anniversary(birth,birth.year+completed)
    end=anniversary(birth,birth.year+completed+1)
    return completed+(visit-start).days/(end-start).days

def relative_age(visit_value,birth_value):
    """Resolve relative age under the declared pediatric cohort, never absolute century.

    Compatible calendar ages are [0,20). Candidate durations must differ by at
    most one day. A range/candidate provenance remains available even then.
    """
    a,b=parse_date(visit_value),parse_date(birth_value)
    visits=[a.value] if a.value else list(a.candidates)
    births=[b.value] if b.value else list(b.candidates)
    candidates=[]
    for visit in visits:
        for birth in births:
            v,t=date.fromisoformat(visit),date.fromisoformat(birth)
            if v<t or v>=anniversary(t,t.year+20):continue
            candidates.append({'visit':visit,'birth':birth,'days':(v-t).days,'age':calendar_age(t,v)})
    durations=[x['days'] for x in candidates]
    resolved=bool(candidates and max(durations)-min(durations)<=1)
    ages=[x['age'] for x in candidates]
    absolute=a.value is not None and b.value is not None
    return {'resolved':resolved,'age':float(np.mean(ages)) if resolved else np.nan,
            'age_min':min(ages) if ages else np.nan,'age_max':max(ages) if ages else np.nan,
            'days_min':min(durations) if durations else np.nan,'days_max':max(durations) if durations else np.nan,
            'n_compatible_pairs':len(candidates),'absolute_dates_confirmed':absolute,
            'source':'calendar_dates_unambiguous' if resolved and absolute else 'relative_candidates_under_pediatric_cohort' if resolved else 'unresolved',
            'assumption':'0<=calendar_age<20; ambiguous centuries remain ambiguous',
            'candidate_pairs':json.dumps(candidates,ensure_ascii=False)}

def prepare_final(raw):
    raw=raw.reset_index(drop=True).copy()
    result=prepare_dataframe(raw)
    legacy_groups=result.groups.copy()
    legacy_group_summary=dict(result.summary['candidate_equivalence'])
    data=result.data.copy()
    original=pd.to_numeric(raw['IDADE'].str.replace(',','.',regex=False),errors='coerce')
    items=[relative_age(a,b) for a,b in zip(raw.Atendimento,raw.DN)]
    ages=[];sources=[];conflicts=[];absolute_ages=[]
    for i,info in enumerate(items):
        x=original.iloc[i]
        pa,pb=parse_date(raw.Atendimento.iloc[i]),parse_date(raw.DN.iloc[i])
        absolute=calendar_age(date.fromisoformat(pb.value),date.fromisoformat(pa.value)) if pa.value and pb.value else np.nan
        absolute_ages.append(absolute)
        if info['resolved']:age=info['age'];source=info['source']
        else:
            literal=age_literal(raw.DN.iloc[i])
            if pd.notna(literal) and 0<=literal<20:age=float(literal);source='explicit_age_literal_in_DN'
            elif pd.notna(x) and np.isfinite(x) and 0<=x<20:age=float(x);source='original_numeric_unverified_fallback'
            else:age=np.nan;source='unavailable'
        ages.append(age);sources.append(source)
        comparison=info['age'] if info['resolved'] else absolute
        conflicts.append(bool(pd.notna(comparison) and pd.notna(x) and abs(x-comparison)>.1))
    data['IDADE']=ages
    extra={'meta_IDADE_original':original.to_numpy(),'meta_IDADE_original_raw':raw.IDADE.to_numpy(),
           'meta_IDADE_source':sources,'meta_IDADE_raw_status':data.meta_IDADE_status.to_numpy(),'meta_IDADE_raw_rule':data.meta_IDADE_rule.to_numpy(),
           'meta_IDADE_status':['missing' if pd.isna(a) else 'derived_relative' if info['resolved'] else 'fallback_explicit' if source=='explicit_age_literal_in_DN' else 'fallback_unverified' for a,info,source in zip(ages,items,sources)],
           'meta_IDADE_rule':sources,'meta_IDADE_calculated':[x['age'] for x in items],
           'meta_IDADE_absolute_calculated':absolute_ages,
           'meta_IDADE_relative_min':[x['age_min'] for x in items],'meta_IDADE_relative_max':[x['age_max'] for x in items],
           'meta_IDADE_relative_days_min':[x['days_min'] for x in items],'meta_IDADE_relative_days_max':[x['days_max'] for x in items],
           'meta_IDADE_relative_candidates':[x['candidate_pairs'] for x in items],
           'meta_IDADE_relative_n_pairs':[x['n_compatible_pairs'] for x in items],
           'meta_IDADE_relative_assumption':[x['assumption'] for x in items],
           'flag_age_original_negative':original.lt(0).to_numpy(),
           'flag_age_original_outside_cohort':(original.notna()&~original.between(0,20,inclusive='left')).to_numpy(),
           'flag_age_original_diff_gt_point1':conflicts,
           'flag_age_conflict_gt1year':[bool(pd.notna(original.iloc[i]) and pd.notna(x['age'] if x['resolved'] else absolute_ages[i]) and abs(original.iloc[i]-(x['age'] if x['resolved'] else absolute_ages[i]))>1) for i,x in enumerate(items)],
           'flag_age_calculated_outside_cohort':[bool(pd.notna(v) and not 0<=v<20) for v in absolute_ages],
           'flag_IDADE_invalid_input':(raw.IDADE.str.strip().ne('')&(original.isna()|(original<0)|~np.isfinite(original))).to_numpy(),
           'flag_age_relative_unresolved':[not x['resolved'] for x in items]}
    # Retain the untouched raw numerical strings for all seven measured columns.
    for c in NUMERIC:extra['meta_'+c+'_raw']=raw[c].to_numpy()
    for name in extra:
        if name in data:del data[name]
    data=pd.concat([data,pd.DataFrame(extra,index=data.index)],axis=1)
    ratio=(data.Peso/(data.Altura/100)**2).replace([np.inf,-np.inf],np.nan)
    data['flag_anthropometric_pair_extreme_ratio']=ratio.notna()&~ratio.between(5,100)
    # Recompute using OBSERVED parents retained by reviewed quality policy, not
    # after any statistical imputation. Preserve the independent historical BMI.
    parent_masks=quality_masks(data,policy='mask_suspect',include_bmi=False)
    parent_usable=data.Peso.notna()&data.Altura.notna()&~parent_masks['Peso']&~parent_masks['Altura']
    all_calculated=(data.Peso/(data.Altura/100)**2).replace([np.inf,-np.inf],np.nan)
    reviewed_calculated=all_calculated.where(parent_usable)
    historical=pd.to_numeric(raw.IMC.str.replace(',','.',regex=False),errors='coerce')
    historical=historical.where(np.isfinite(historical)&historical.gt(0))
    data['meta_IMC_raw_status']=data.meta_IMC_status
    data['meta_IMC_raw_rule']=data.meta_IMC_rule
    data['meta_IMC_original']=historical
    data['meta_IMC_calculated_observed_all']=all_calculated
    data['meta_IMC_calculated_reviewed']=reviewed_calculated
    data['meta_IMC_original_minus_calculated']=historical-reviewed_calculated
    data['IMC']=reviewed_calculated.combine_first(historical)
    data['meta_IMC_source']=np.select([reviewed_calculated.notna(),historical.notna()],['arithmetic_observed_parents_reviewed','original_historical'],default='unavailable')
    data['meta_IMC_status']=np.select([reviewed_calculated.notna(),historical.notna()],['derived_observed_parents','historical_observed'],default='missing')
    data['meta_IMC_rule']=data.meta_IMC_source
    data['flag_IMC_suspect_envelope']=data.IMC.notna()&~data.IMC.between(*SUSPECT_ENVELOPES['IMC'])
    data['flag_IMC_parent_reviewed_unusable']=~parent_usable
    data['flag_IMC_historical_with_unusable_parents']=data.meta_IMC_source.eq('original_historical')&~parent_usable
    data['flag_IMC_original_difference_gt_point1']=historical.notna()&reviewed_calculated.notna()&abs(historical-reviewed_calculated).gt(.1)
    result.data=data
    result.eligibility['idade_disponivel']=data.IDADE.notna()
    result.eligibility['candidato_fora_recorte_idade_original']=data.flag_age_original_outside_cohort & data.IDADE.isna()
    result.eligibility['elegivel_exclui_candidatos_idade']=result.eligibility.elegivel_principal & ~result.eligibility.candidato_fora_recorte_idade_original
    result.eligibility['motivo']=np.select([~result.eligibility.alvo_conhecido,result.eligibility.candidato_fora_recorte_idade_original,~result.eligibility.idade_disponivel],['alvo_ausente_ou_em_revisao','incluido_candidato_idade_original_fora_recorte','incluido_idade_indisponivel'],default='incluido')
    # New hashes use corrected age; legacy hashes are retained only as reference.
    predictors=[c for c in raw.columns if c not in ['ID','NORMAL X ANORMAL']]
    signatures=[];field_counts=[]
    for i in data.index:
        vals=[None if pd.isna(data.at[i,c]) else data.at[i,c] for c in predictors]
        field_counts.append(sum(v is not None for v in vals))
        signatures.append(sha256(json.dumps(vals,ensure_ascii=False,separators=(',',':')).encode()).hexdigest())
    newgroups=legacy_groups.copy()
    newgroups['legacy_candidate_feature_hash']=newgroups['candidate_feature_hash']
    newgroups['candidate_feature_hash']=signatures
    newgroups['n_informative_fields']=field_counts
    newgroups['informative_candidate']=[n>=8 and bool(normalize_text(dn) or normalize_text(at)) for n,dn,at in zip(field_counts,raw.DN,raw.Atendimento)]
    newgroups['split_group']=['candidate_'+h if informative else 'row_'+str(ID) for h,informative,ID in zip(signatures,newgroups.informative_candidate,newgroups.ID)]
    result.groups=newgroups
    counts=newgroups.groupby('candidate_feature_hash').size()
    result.summary={**result.summary,'version':'a2-preprocessing-1','age_sources':pd.Series(sources).value_counts().to_dict(),
        'legacy_candidate_equivalence_reference':legacy_group_summary,
        'candidate_equivalence':{'groups_repeated':int((counts>1).sum()),'rows_in_informative_repeated_groups':int(newgroups.split_group.duplicated(keep=False).sum()),'identity_confirmed':False,'minimum_present_fields':8,'uses_corrected_age':True},
        'n_relative_age_resolved':sum(x['resolved'] for x in items),'n_negative_original_preserved':int(original.lt(0).sum()),
        'n_relative_age_one_day_interval':sum(x['resolved'] and x['days_min']!=x['days_max'] for x in items),
        'n_original_age_diff_gt_point1':sum(conflicts),'age_policy':'Calendar-based relative age; absolute ambiguous dates never assigned a century; fallback original is unverified.',
        'flags':{c:int(data[c].sum()) for c in data if c.startswith('flag_')},
        'missing_by_original_column':{c:int(data[c].isna().sum()) for c in raw.columns}}
    newlogs=[]
    for i in data.index:
        newlogs.append({'ID':str(data.ID.iloc[i]),'coluna':'IDADE','valor_bruto':raw.IDADE.iloc[i],
                        'valor_tratado':data.IDADE.iloc[i],'regra':sources[i],'status':'relative_age_under_cohort' if items[i]['resolved'] else 'fallback_or_unavailable'})
    result.changes=pd.concat([result.changes.loc[result.changes.coluna.ne('IDADE')],pd.DataFrame(newlogs)],ignore_index=True)
    result.summary['n_changes']=len(result.changes)
    return result

def quality_masks(data,policy='mask_suspect',include_bmi=True):
    """Declared reliability hypotheses, NOT clinical normal ranges.

    Reviewed exceptions preserve potentially real high weights, early/unknown-age
    short length and tachyarrhythmia-compatible heart rates. Historical policy is
    retained separately for sensitivity, never silently called a clinical limit.
    """
    if policy not in ('mask_suspect','preserve_suspect','historical'):raise ValueError('Unknown quality policy')
    masks={c:pd.Series(False,index=data.index) for c in SUSPECT_ENVELOPES}
    if policy=='preserve_suspect':return masks
    for c,(lo,hi) in SUSPECT_ENVELOPES.items():masks[c]=data[c].notna()&~data[c].between(lo,hi)
    if policy=='mask_suspect':
        # 150 kg is not a maximum possible weight; retain upper-tail measurements.
        masks['Peso']=data.Peso.notna()&data.Peso.lt(1)
        compatible_short=data.Altura.between(30,40,inclusive='left')&(data.IDADE.lt(.25)|data.IDADE.isna())
        masks['Altura']&=~compatible_short
        # >500 is an explicit curation trigger, not a physiological maximum.
        masks['FC']=data.FC.notna()&data.FC.gt(500)
        # A very low positive PAD is not a logical contradiction by itself.
        masks['PA DIASTOLICA']=pd.Series(False,index=data.index)
        # Broad JOINT curation guard, not a clinical range or attribution of error.
        joint=(data.Peso/(data.Altura/100)**2).replace([np.inf,-np.inf],np.nan)
        joint_suspect=joint.notna()&~joint.between(5,100)
        masks['Peso']|=joint_suspect
        masks['Altura']|=joint_suspect
        if include_bmi:
            masks['IMC']=data.IMC.notna()&~data.IMC.between(5,100)
            # Arithmetic from observed, retained parents is a defined ratio, not
            # a clinical judgment; preserve positive values with suspicion flags.
            masks['IMC']&=~data.meta_IMC_source.eq('arithmetic_observed_parents_reviewed')
            # A known contradictory triad is quarantined together even if the
            # historical BMI happens to lie just inside the broad guard.
            masks['IMC']|=joint_suspect
    if not include_bmi:masks['IMC']=pd.Series(False,index=data.index)
    if policy=='historical':masks['IMC']|=data.flag_IMC_parent_suspect
    masks['PA SISTOLICA']|=data.flag_pas_le_pad
    masks['PA DIASTOLICA']|=data.flag_pas_le_pad
    return masks


def model_frame(data,policy='mask_suspect'):
    """No learned statistics. Masking is a declared quality hypothesis, not diagnosis."""
    out=data.copy()
    for c,mask in quality_masks(data,policy).items():out.loc[mask,c]=np.nan
    return out
