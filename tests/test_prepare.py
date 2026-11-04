from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from kdd_revision.prepare import parse_date,numeric_value,prepare_dataframe,safe_model_frame
from kdd_revision.schema import ORIGINAL,SCENARIOS,SOURCE_DEFAULT


def rows(**fields):
    data={c:'' for c in ORIGINAL};data.update(ID='1',IDADE='10',**fields)
    return pd.DataFrame([data],columns=ORIGINAL)

@pytest.mark.parametrize('text,expected', [('Ago/28,/1991','1991-08-28'),('29/02/2000','2000-02-29'),('18\\08\\2003','2003-08-18'),('2003-08-18','2003-08-18'),('40000','2009-07-06')])
def test_recognized_dates(text,expected):assert parse_date(text).value==expected

@pytest.mark.parametrize('text',['10/06/97arritmia','!2/01/97','28/03/0/5','31/02/2003','inf','nan','4/anos'])
def test_no_forged_dates(text):assert parse_date(text).value is None


def test_two_digit_year_not_forced():
    result=parse_date('18/08/03');assert result.status=='ambiguous_century';assert result.value is None;assert result.candidates==('1903-08-18','2003-08-18')


def test_zero_age_valid_zero_weight_missing():
    assert numeric_value('0','IDADE')[0]==0
    assert np.isnan(numeric_value('0.00','Peso')[0])

@pytest.mark.parametrize('text',['NaN','inf','-inf','-40'])
def test_impossible_numeric(text):assert np.isnan(numeric_value(text,'Peso')[0])


def test_sentinel_after_normalization_and_absent_sopro():
    raw=rows(PPA='  NãO Calculado ',SEXO='Indeterminado',SOPRO='  Ausente ',**{'NORMAL X ANORMAL':'Normais'})
    result=prepare_dataframe(raw)
    assert pd.isna(result.data.loc[0,'PPA']);assert pd.isna(result.data.loc[0,'SEXO'])
    assert result.data.loc[0,'SOPRO']=='Ausente';assert pd.isna(result.data.loc[0,'NORMAL X ANORMAL'])
    assert not result.eligibility.elegivel_principal.iloc[0]


def test_suspect_anthropometry_does_not_erase_age():
    raw=rows(Peso='500',Altura='240',DN='01/01/2000',Atendimento='01/01/2010',**{'NORMAL X ANORMAL':'Normal'})
    result=prepare_dataframe(raw);assert 9.99<result.data.IDADE.iloc[0]<10.01
    assert result.data.DN.iloc[0]=='2000-01-01';assert result.data.Peso.iloc[0]==500
    safe=safe_model_frame(result.data);assert pd.isna(safe.Peso.iloc[0]);assert safe.IDADE.iloc[0]==result.data.IDADE.iloc[0]


def test_date_conflict_without_causal_repair():
    raw=rows(DN='01/01/1900',Atendimento='01/01/1991',**{'NORMAL X ANORMAL':'Normal'})
    result=prepare_dataframe(raw);assert result.data.IDADE.iloc[0]==10
    assert result.data.flag_age_calculated_outside_cohort.iloc[0]
    assert result.data.flag_age_conflict_gt1year.iloc[0]
    assert result.data.DN.iloc[0]=='1900-01-01'


def test_pas_le_pad_masks_both_without_changing_original_or_ppa():
    raw=rows(PPA='HAS-2 PAS',**{'PA SISTOLICA':'80','PA DIASTOLICA':'80'})
    r=prepare_dataframe(raw);safe=safe_model_frame(r.data)
    assert r.data.flag_pas_le_pad.iloc[0];assert r.data['PA SISTOLICA'].iloc[0]==80
    assert pd.isna(safe['PA SISTOLICA'].iloc[0]) and pd.isna(safe['PA DIASTOLICA'].iloc[0])
    assert safe.PPA.iloc[0]==r.data.PPA.iloc[0]


def test_pure_and_deterministic():
    raw=rows(SOPRO='Ausente',**{'NORMAL X ANORMAL':'Normal'});before=raw.copy(deep=True)
    a=prepare_dataframe(raw);b=prepare_dataframe(raw)
    assert_frame_equal(raw,before);assert_frame_equal(a.data,b.data);assert_frame_equal(a.changes,b.changes)
    assert_frame_equal(a.groups,b.groups);assert a.summary==b.summary


def test_empty_rows_do_not_form_huge_split_group():
    a=rows();b=rows();b.ID='2';raw=pd.concat([a,b],ignore_index=True)
    r=prepare_dataframe(raw);assert r.groups.split_group.nunique()==2


def test_feature_contract_is_explicit():
    assert SCENARIOS['B']==['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC','SEXO']
    assert not any(x.startswith(('meta_','flag_')) or x in ['ID','DN','Atendimento','NORMAL X ANORMAL'] for cols in SCENARIOS.values() for x in cols)


def test_full_source_integrity_and_identity():
    from hashlib import sha256
    import os
    source=Path(os.environ.get('KDD_TEST_SOURCE',str(SOURCE_DEFAULT)))
    if not source.is_file():pytest.skip('Clinical input is excluded from Git; set KDD_TEST_SOURCE for the local source-integrity check')
    before=source.read_bytes();assert sha256(before).hexdigest()=='35e68400d6bec51bbf74857c0f0e0487161b3495b5f4fefbc2cc57af24824ea1'
    raw=pd.read_csv(source,dtype=str,keep_default_na=False).astype(object)
    r=prepare_dataframe(raw)
    assert len(r.data)==len(raw)==12873;assert r.data.ID.tolist()==raw.ID.tolist()
    assert source.read_bytes()==before;json.dumps(r.summary,allow_nan=False)


def test_explicit_age_literal_does_not_fabricate_birth():
    raw=rows(DN='1a/7m');raw.loc[0,'IDADE']=''
    r=prepare_dataframe(raw)
    assert r.data.IDADE.iloc[0]==pytest.approx(1+7/12)
    assert r.data.meta_IDADE_source.iloc[0]=='explicit_age_literal_in_DN'
    assert pd.isna(r.data.DN.iloc[0])


def test_no_alphabetic_suffix_repair():
    assert parse_date('10/06/97arritmia').value is None
    assert parse_date('!2/01/97').value is None


def test_source_import_has_no_write_side_effect(tmp_path, monkeypatch):
    import subprocess,sys,os
    env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[1]/'src'))
    subprocess.run([sys.executable,'-c','import kdd_revision.prepare, kdd_revision.io'],cwd=tmp_path,env=env,check=True)
    assert list(tmp_path.iterdir())==[]
