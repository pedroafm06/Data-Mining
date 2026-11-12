import numpy as np
import pandas as pd
import pytest
from kdd_revision.rubric_audit import SCENARIOS_AUDIT, CLINICO, EXCLUDED_REASONS, FORBIDDEN, search_space, validate_features, audit_preprocessor
from kdd_revision.preprocessing.transformer import AppliedPreprocessor, MISSING, UNSEEN
from kdd_revision.schema import ORIGINAL


def test_clinico_is_primary_and_keeps_fields_available_before_the_report():
    assert list(SCENARIOS_AUDIT)[0]=='CLINICO'
    assert CLINICO==['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC','SEXO','PPA','SOPRO','B2','PULSOS','HDA 1']
    for field in ['SOPRO','B2','PULSOS','HDA 1','PPA']:validate_features(['IDADE',field])


def test_clinico_excludes_identifiers_origin_referral_reason_and_sparse_hda2():
    assert FORBIDDEN=={'ID','Atendimento','DN','Convenio','MOTIVO1','MOTIVO2','HDA2','NORMAL X ANORMAL'}
    assert set(EXCLUDED_REASONS)==FORBIDDEN and set(CLINICO)|FORBIDDEN==set(ORIGINAL)
    for field in sorted(FORBIDDEN):
        with pytest.raises(ValueError):validate_features(['IDADE',field])


def test_sensitivity_pools_are_nested_subsets_of_clinico():
    assert SCENARIOS_AUDIT['FISIO8']==['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC','SEXO']
    assert SCENARIOS_AUDIT['STRICT4']==['Peso','Altura','IDADE','SEXO']
    assert set(SCENARIOS_AUDIT['STRICT4'])<set(SCENARIOS_AUDIT['FISIO8'])<set(CLINICO)


def test_published_budget_contains_three_learned_families_and_dummy():
    c=search_space();assert len(c)==105 and len({x['name'] for x in c})==105
    assert {k:sum(x['kind']==k for x in c) for k in ['dummy','tree','logistic','forest']}=={'dummy':1,'tree':48,'logistic':32,'forest':24}


def test_age_conditioning_cannot_be_hidden_when_age_is_removed():
    c=next(x for x in search_space() if x['imputation']=='age')
    with pytest.raises(ValueError,match='IDADE'):audit_preprocessor(c,['Peso','SEXO'])


def test_clinico_categories_use_training_vocabulary_with_missing_and_unknown_columns():
    train=pd.DataFrame({'ID':['1','2','3'],'IDADE':[1.,2.,3.],'SOPRO':['Ausente','Sistolico',None]})
    val=pd.DataFrame({'ID':['4','5'],'IDADE':[1.,2.],'SOPRO':['Continuo',None]})
    prep=AppliedPreprocessor(features=['IDADE','SOPRO'],age_group_columns=(),log_columns=()).fit(train)
    assert prep.vocabularies_['SOPRO']==['Ausente','Sistolico',MISSING,UNSEEN]
    out=prep.transform(val)
    onehot=out[[c for c in out if c.startswith('SOPRO__')]].to_numpy()
    assert onehot.sum(axis=1).tolist()==[1,1]
    assert onehot[0].tolist()==[0,0,0,1] and onehot[1].tolist()==[0,0,1,0]
