import numpy as np
import pandas as pd
import pytest
from kdd_revision.rubric_audit import SCENARIOS_AUDIT, search_space, validate_features, audit_preprocessor, group_exact_raw_duplicates


def test_primary_pools_reject_diagnostic_administrative_and_target_fields():
    assert SCENARIOS_AUDIT['FISIO8']==['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC','SEXO']
    assert SCENARIOS_AUDIT['STRICT4']==['Peso','Altura','IDADE','SEXO']
    for field in ['NORMAL X ANORMAL','ID','DN','Convenio','PULSOS','B2','SOPRO','PPA','MOTIVO1','MOTIVO2','HDA 1','HDA2']:
        with pytest.raises(ValueError):validate_features(['IDADE',field])


def test_published_budget_contains_three_learned_families_and_dummy():
    c=search_space();assert len(c)==105 and len({x['name'] for x in c})==105
    assert {k:sum(x['kind']==k for x in c) for k in ['dummy','tree','logistic','forest']}=={'dummy':1,'tree':48,'logistic':32,'forest':24}


def test_age_conditioning_cannot_be_hidden_when_age_is_removed():
    c=next(x for x in search_space() if x['imputation']=='age')
    with pytest.raises(ValueError,match='IDADE'):audit_preprocessor(c,['Peso','SEXO'])

def test_diagnostic_fields_only_enter_explicit_exploration():
    validate_features(['IDADE', 'SOPRO', 'B2'], exploratory=True)
    for field in ('MOTIVO1', 'MOTIVO2', 'NORMAL X ANORMAL'):
        with pytest.raises(ValueError):
            validate_features(['IDADE', field], exploratory=True)


def test_exact_raw_duplicates_connect_groups_transitively_without_using_the_label():
    raw = pd.DataFrame({
        'ID': ['1', '2', '3', '4', '5', '6'],
        'NORMAL X ANORMAL': ['Normal', 'Anormal', 'Normal', 'Anormal', 'Normal', 'Normal'],
        'Peso': ['10', '10', '11', '11', '12', '13'],
    })
    groups = pd.Series(['a', 'b', 'b', 'c', 'c', 'd'])
    assert group_exact_raw_duplicates(raw, groups).tolist() == ['a', 'a', 'a', 'a', 'a', 'd']
