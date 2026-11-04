import pandas as pd
from kdd_revision.application import coverage_gate


def test_no_information_or_novel_missing_pattern_is_not_scored():
    train=pd.DataFrame({'Peso':[10.]*40,'SEXO':['F']*40})
    incoming=pd.DataFrame({'Peso':[10.,None,None],'SEXO':['F','F',None]})
    result=coverage_gate(train,incoming,['Peso','SEXO'])
    assert result.status.tolist()==['cobertura_compativel','padrao_ausencia_nao_observado','sem_preditor_disponivel']
    assert result.accepted.tolist()==[True,False,False]


def test_unknown_category_and_low_support_have_distinct_statuses():
    train=pd.DataFrame({'Peso':[10.]*20,'SEXO':['F']*20})
    incoming=pd.DataFrame({'Peso':[10.,10.],'SEXO':['M','F']})
    result=coverage_gate(train,incoming,['Peso','SEXO'])
    assert result.status.tolist()==['categoria_inedita','padrao_ausencia_baixo_suporte']
    assert not result.accepted.any()
