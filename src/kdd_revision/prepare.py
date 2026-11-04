"""Conservative, deterministic treatment. No fitted sample quantiles or target-based repair.

Historical spelling patterns/sentinels: analise_e_limpeza.py stages 2–5. New contract:
keep every row, treat ambiguous century as ambiguous, keep suspicion separate from error.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from hashlib import sha256
import json
import math
import re
import unicodedata
import numpy as np
import pandas as pd
from .schema import ORIGINAL, NUMERIC, CATEGORICAL, TARGET, SUSPECT_ENVELOPES, SCENARIOS


def normalize_text(value):
    if value is None or pd.isna(value): return ''
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', str(value)).strip())


def key(value):
    return ''.join(x for x in unicodedata.normalize('NFKD', normalize_text(value)) if not unicodedata.combining(x)).casefold()


MAPS = {
 'SEXO': {'m':'M','masculino':'M','f':'F','feminino':'F'},
 TARGET: {'normal':'Normal','anormal':'Anormal'},
 'SOPRO': {'ausente':'Ausente','sistolico':'Sistolico','diastolico':'Diastolico','continuo':'Continuo','sistolico e diastolico':'Sistolico e diastolico'},
 'PULSOS': {'normais':'Normais','amplos':'Amplos','diminuidos':'Diminuidos','femorais diminuidos':'Femorais diminuidos','outro':'Outro'},
 'B2': {'normal':'Normal','hiperfonetica':'Hiperfonetica','desdob fixo':'Desdob fixo','unica':'Unica','outro':'Outro'},
}
SENTINELS = {'PPA':{'nao calculado','#value!'},'DN':{'???','??????'},'SEXO':{'indeterminado'}}
MONTHS = {'jan':1,'janeiro':1,'fev':2,'fevereiro':2,'mar':3,'marco':3,'abr':4,'abril':4,'mai':5,'maio':5,'jun':6,'junho':6,'jul':7,'julho':7,'ago':8,'agosto':8,'set':9,'setembro':9,'out':10,'outubro':10,'nov':11,'novembro':11,'dez':12,'dezembro':12}

@dataclass(frozen=True)
class DateParse:
    value: str | None
    status: str
    rule: str
    candidates: tuple[str, ...] = ()


def parse_date(value):
    """Accept explicit four-digit years and Excel serials; two-digit years have candidates only.

    Numeric day/month follows documented Brazilian day/month convention. Month-name-first
    is explicit, e.g. Ago/28,/1991. Trailing clinical text is not silently discarded.
    """
    text = normalize_text(value)
    if not text or key(text) in SENTINELS['DN']: return DateParse(None,'missing','empty_or_sentinel')
    if re.fullmatch(r'\d{5}(?:\.0+)?',text):
        n=float(text)
        # Excel 1900 calendar with the historical leap-year adjustment. Serial 60
        # (fictitious 1900-02-29) is not accepted by this supported 5-digit format.
        d=date(1899,12,30)+timedelta(days=n)
        return DateParse(d.isoformat(),'parsed','excel_1900_serial')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}',text):
        try:return DateParse(date.fromisoformat(text).isoformat(),'parsed','iso_8601')
        except ValueError:return DateParse(None,'invalid','invalid_calendar')
    s=key(text).replace('\\','/').replace(',','/').replace('-','/').replace('.','/')
    s=re.sub(r'/+','/',s)
    parts=s.split('/')
    if len(parts)!=3: return DateParse(None,'unrecognized','unsupported_format')
    try:
        if parts[0] in MONTHS:
            month=MONTHS[parts[0]];day=int(parts[1]);year_text=parts[2];rule='month_name_first'
        else:
            day=int(parts[0]);month=MONTHS.get(parts[1]) or int(parts[1]);year_text=parts[2];rule='day_first'
        if not year_text.isdigit() or len(year_text) not in (2,4): raise ValueError
        if len(year_text)==2:
            candidates=[]
            for century in (1900,2000):
                try:candidates.append(date(century+int(year_text),month,day).isoformat())
                except ValueError:pass
            if not candidates:return DateParse(None,'invalid','invalid_calendar')
            return DateParse(None,'ambiguous_century',rule,tuple(candidates))
        d=date(int(year_text),month,day)
        return DateParse(d.isoformat(),'parsed',rule)
    except (ValueError,OverflowError):
        return DateParse(None,'invalid','invalid_calendar_or_token')


def numeric_value(value, column):
    text=normalize_text(value)
    if not text:return (np.nan,'missing','empty')
    if column=='FC':
        m=re.fullmatch(r'(\d{2,3})\s*(?:-|a|ate|até|/)\s*(\d{2,3})',key(text))
        if m:
            lo,hi=map(float,m.groups())
            if lo>hi:return (np.nan,'invalid','reversed_range')
            return ((lo+hi)/2,'approximation','range_midpoint')
    try:v=float(text.replace(',','.'))
    except ValueError:return (np.nan,'unrecognized','not_numeric')
    if not math.isfinite(v):return (np.nan,'invalid','non_finite')
    if column in ['Peso','Altura','IMC'] and v==0:return (np.nan,'missing','zero_sentinel')
    if v<0 or (column in ['FC','PA SISTOLICA','PA DIASTOLICA'] and v==0):
        return (np.nan,'invalid','nonpositive_measurement')
    return (v,'parsed','numeric')


def age_literal(value):
    """Explicit age written in DN is an age approximation, never a birthdate."""
    text=key(value).replace('/','').replace(' ','').replace('e','')
    m=re.fullmatch(r'(\d+)(?:anos|ano|a)(?:(\d+)(?:ms|mes|mss|m))?',text)
    if m:
        years=int(m.group(1));months=int(m.group(2) or 0)
        return years+months/12 if months<12 else np.nan
    m=re.fullmatch(r'(\d+)m',text)
    return int(m.group(1))/12 if m else np.nan


def _serializable(x):
    if x is None or pd.isna(x):return None
    if isinstance(x,np.generic):return x.item()
    return x

@dataclass
class PreparationResult:
    data: pd.DataFrame
    changes: pd.DataFrame
    eligibility: pd.DataFrame
    groups: pd.DataFrame
    summary: dict


def prepare_dataframe(raw):
    """Pure transformation. Input is not modified. No row is discarded or ID fabricated."""
    if list(raw.columns)!=ORIGINAL:raise ValueError('Unexpected input schema/order; inspect source before processing.')
    if raw['ID'].map(normalize_text).eq('').any():raise ValueError('Missing ID prevents reliable traceability.')
    if raw['ID'].map(normalize_text).duplicated().any():raise ValueError('Repeated ID: source identity requires review before processing.')
    data=pd.DataFrame(index=raw.index);changes=[];metadata={};flags={}
    def log(i,col,old,new,rule,status):
        a=_serializable(old);b=_serializable(new)
        # Log all semantic changes and any uncertainty, including unchanged suspected values.
        if str(a)!=str(b) or status not in ('parsed','unchanged'):
            changes.append({'ID':normalize_text(raw.at[i,'ID']),'coluna':col,'valor_bruto':a,'valor_tratado':b,'regra':rule,'status':status})
    for col in ORIGINAL:
        values=[];statuses=[];rules=[]
        for i,v in raw[col].items():
            t=normalize_text(v);k=key(t);new=t;status='parsed';rule='normalize_whitespace_unicode'
            if not t or k in SENTINELS.get(col,set()):new=np.nan;status='missing';rule='empty_or_column_sentinel'
            elif col in NUMERIC:new,status,rule=numeric_value(t,col)
            elif col in MAPS:
                new=MAPS[col].get(k)
                if new is None:
                    if col in ['SEXO',TARGET]:new=np.nan;status='needs_review';rule='unknown_category_not_inferred'
                    else:new=t;status='needs_review';rule='unknown_category_preserved'
                else:rule='documented_category_spelling'
            elif col in CATEGORICAL:
                # Orthographic only: preserve unknown categories, no semantic family grouping.
                new=key(t).upper() if col=='Convenio' else key(t)
                rule='case_accent_space_only'
            values.append(new);statuses.append(status);rules.append(rule)
            log(i,col,v,new,rule,status)
        data[col]=values
        metadata['meta_'+col+'_status']=statuses
        metadata['meta_'+col+'_rule']=rules
    # Date values in original columns become ISO only when unambiguous. Raw cells are
    # retained in the audit log and in meta_*_raw for dates (all original cells elsewhere log).
    for col in ['Atendimento','DN']:
        parsed=[parse_date(v) for v in raw[col]]
        data[col]=[p.value for p in parsed]
        metadata['meta_'+col+'_status']=[p.status for p in parsed]
        metadata['meta_'+col+'_rule']=[p.rule for p in parsed]
        metadata['meta_'+col+'_raw']=raw[col].astype(str).tolist()
        metadata['meta_'+col+'_date_candidates']=[json.dumps(p.candidates) for p in parsed]
        for i,p in zip(raw.index,parsed):log(i,col,raw.at[i,col],p.value,p.rule,p.status)
    # Temporal sensitivity only: pick an ambiguous candidate inside historical
    # concentration window. This is an assumption, never a reliable parsed date.
    metadata['meta_Atendimento_hypothesis_2003_2010']=[next((x for x in p.candidates if 2003<=int(x[:4])<=2010),None) if p.status=='ambiguous_century' else p.value for p in [parse_date(v) for v in raw['Atendimento']]]
    metadata['meta_Atendimento_hypothesis_warning']=['historical_window_assumption_not_confirmed_date']*len(data)
    # Preserve original numeric age/IMC even if a reliable derivation takes precedence.
    metadata['meta_IDADE_original']=data['IDADE'].tolist()
    metadata['meta_IMC_original']=data['IMC'].tolist()
    ages=[];sources=[];agecalcs=[];ageconf=[];dateconf=[]
    for i in data.index:
        orig=data.at[i,'IDADE'];a=data.at[i,'Atendimento'];b=data.at[i,'DN'];derived=np.nan
        bad_pair=False
        if pd.notna(a) and pd.notna(b):
            delta=(date.fromisoformat(a)-date.fromisoformat(b)).days
            bad_pair=delta<0
            if not bad_pair:derived=delta/365.2425
        agecalcs.append(derived);dateconf.append(bad_pair)
        usable_calc=pd.notna(derived) and 0<=derived<20
        usable_orig=pd.notna(orig) and 0<=orig<20
        if usable_calc:new=derived;source='dates_unambiguous'
        elif usable_orig:new=orig;source='original_numeric'
        else:
            literal=age_literal(raw.at[i,'DN'])
            if pd.notna(literal) and 0<=literal<20:new=literal;source='explicit_age_literal_in_DN'
            else:new=np.nan;source='unavailable_or_out_of_cohort'
        conflict=bool(pd.notna(derived) and pd.notna(orig) and abs(orig-derived)>1)
        ages.append(new);sources.append(source);ageconf.append(conflict)
        log(i,'IDADE',raw.at[i,'IDADE'],new,source,'needs_review' if conflict else 'parsed')
    data['IDADE']=ages
    metadata['meta_IDADE_calculated']=agecalcs
    metadata['meta_IDADE_source']=sources
    flags['flag_date_pair_reversed']=dateconf
    flags['flag_age_calculated_outside_cohort']=[bool(pd.notna(x) and not 0<=x<20) for x in agecalcs]
    flags['flag_age_conflict_gt1year']=ageconf
    flags['flag_age_original_outside_cohort']=[bool(pd.notna(x) and not 0<=x<20) for x in metadata['meta_IDADE_original']]
    # Fixed historical envelopes: label suspicion; do not erase a measurement or age.
    for col,(lo,hi) in SUSPECT_ENVELOPES.items():
        flags['flag_'+col+'_suspect_envelope']=data[col].notna() & ~data[col].between(lo,hi)
    flags['flag_pas_le_pad']=data['PA SISTOLICA'].notna() & data['PA DIASTOLICA'].notna() & (data['PA SISTOLICA']<=data['PA DIASTOLICA'])
    metadata['meta_IMC_calculated']=(data['Peso']/(data['Altura']/100)**2).replace([np.inf,-np.inf],np.nan).tolist()
    bmis=[];bmisources=[]
    for i,calc in zip(data.index,metadata['meta_IMC_calculated']):
        orig=data.at[i,'IMC']
        parent_suspect=bool(flags['flag_Peso_suspect_envelope'][i] or flags['flag_Altura_suspect_envelope'][i])
        if pd.notna(calc) and not parent_suspect:new=calc;source='valid_parents_arithmetic'
        elif pd.notna(orig):new=orig;source='original_historical'
        else:new=np.nan;source='unavailable'
        bmis.append(new);bmisources.append(source)
        log(i,'IMC',raw.at[i,'IMC'],new,source,'parsed')
    data['IMC']=bmis;metadata['meta_IMC_source']=bmisources
    flags['flag_IMC_suspect_envelope']=data.IMC.notna() & ~data.IMC.between(*SUSPECT_ENVELOPES['IMC'])
    flags['flag_IMC_parent_suspect']=flags['flag_Peso_suspect_envelope'] | flags['flag_Altura_suspect_envelope']
    # No global anthropometric quantiles; cannot infer age error from measurements.
    flags['flag_target_needs_review']=[key(x) not in ('','normal','anormal') for x in raw[TARGET]]
    for col in ['Peso','Altura','IMC','PA SISTOLICA','PA DIASTOLICA','FC']:
        # Impossible original values have been invalidated. Suspicion remains separate.
        flags['flag_'+col+'_invalid_input']=[s in ('invalid','unrecognized') for s in metadata['meta_'+col+'_status']]
    metadata['meta_row_source_index']=list(range(len(data)))
    for k,v in {**metadata,**flags}.items():data[k]=list(v)
    labeled=data[TARGET].isin(['Normal','Anormal'])
    valid_age=data['IDADE'].notna()
    # Missing age is retained as model-eligible but outside-reference-coverage; an explicit
    # observed invalid/out-of-cohort age without a valid fallback is not cohort-eligible.
    observed_out=data['flag_age_original_outside_cohort'] & ~valid_age
    eligibility=pd.DataFrame({'ID':data.ID,'alvo_conhecido':labeled,'idade_disponivel':valid_age,'candidato_fora_recorte_idade_original':observed_out,'elegivel_principal':labeled,'elegivel_exclui_candidatos_idade':labeled & ~observed_out})
    eligibility['motivo']=np.select([~labeled,observed_out,~valid_age],['alvo_ausente_ou_em_revisao','incluido_candidato_idade_original_fora_recorte','incluido_idade_indisponivel'],default='incluido')
    # Candidate equivalence is NOT patient identity. Exclude y from hash and require
    # substantial information, including date information for primary grouping candidates.
    predictors=[c for c in ORIGINAL if c not in ['ID',TARGET]]
    grouped=[]
    raw_predictors=raw[predictors].apply(lambda s:s.map(normalize_text))
    for i in data.index:
        vals=[_serializable(data.at[i,c]) for c in predictors]
        n=sum(x is not None for x in vals)
        signature=sha256(json.dumps(vals,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        raw_signature=sha256(json.dumps(raw_predictors.loc[i].tolist(),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        informative=n>=8 and (bool(normalize_text(raw.at[i,'DN'])) or bool(normalize_text(raw.at[i,'Atendimento'])))
        grouped.append({'ID':data.at[i,'ID'],'candidate_feature_hash':signature,'candidate_raw_feature_hash':raw_signature,'n_informative_fields':n,'informative_candidate':informative,'split_group':('candidate_'+signature) if informative else 'row_'+str(data.at[i,'ID']),'interpretation':'candidate_equivalence_not_patient_identity'})
    groups=pd.DataFrame(grouped)
    counts=groups.groupby('candidate_feature_hash').size()
    summary={'version':'0.1.0','n_source':len(raw),'n_treated':len(data),'original_columns':ORIGINAL,'target_counts':data[TARGET].astype(object).fillna('SEM_ALVO').value_counts().to_dict(),'n_eligible':int(eligibility.elegivel_principal.sum()),'n_changes':len(changes),'missing_by_original_column':{c:int(data[c].isna().sum()) for c in ORIGINAL},'flags':{k:int(data[k].sum()) for k in flags},'date_statuses':{c:pd.Series(metadata['meta_'+c+'_status']).value_counts().to_dict() for c in ['Atendimento','DN']},'age_sources':pd.Series(sources).value_counts().to_dict(),'candidate_equivalence':{'groups_repeated':int((counts>1).sum()),'rows_in_informative_repeated_groups':int(groups.split_group.duplicated(keep=False).sum()),'identity_confirmed':False,'minimum_present_fields':8},'policy':{'no_row_deletion':True,'no_sample_quantile_repair':True,'two_digit_year':'ambiguous_no_century_selection','suspect_envelopes':'historical_heuristics_not_diagnoses','target_not_imputed':True,'reference_population':'0<=age<20; unknown age retained and reported','primary_feature_lists':SCENARIOS}}
    return PreparationResult(data,pd.DataFrame(changes,columns=['ID','coluna','valor_bruto','valor_tratado','regra','status']),eligibility,groups,summary)


def safe_model_frame(data, policy='mask_suspect'):
    """Explicit matrix policy, retains original data. No fit, statistics or y usage.

    mask_suspect masks historical-envelope values and both PAS/PAD in relational
    inconsistency without asserting which one is wrong. conservative retains suspects.
    Historical PPA is never recomputed or removed merely because parents are missing.
    """
    if policy not in ('mask_suspect','conservative'):raise ValueError('Unknown policy')
    out=data.copy(deep=True)
    if policy=='mask_suspect':
        for c in SUSPECT_ENVELOPES:
            out.loc[out['flag_'+c+'_suspect_envelope'],c]=np.nan
        out.loc[out.flag_IMC_parent_suspect,'IMC']=np.nan
        out.loc[out.flag_pas_le_pad,['PA SISTOLICA','PA DIASTOLICA']]=np.nan
    return out
