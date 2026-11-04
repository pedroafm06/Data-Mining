"""Explicit predictors: metadata never becomes a predictor by dtype inference."""
from pathlib import Path

VERSION = '0.1.0'
TARGET = 'NORMAL X ANORMAL'
NUMERIC = ['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC']
CATEGORICAL = ['Convenio','PULSOS','PPA',TARGET,'B2','SOPRO','HDA 1','HDA2','SEXO','MOTIVO1','MOTIVO2']
ORIGINAL = ['ID','Peso','Altura','IMC','Atendimento','DN','IDADE','Convenio','PULSOS','PA SISTOLICA','PA DIASTOLICA','PPA',TARGET,'B2','SOPRO','FC','HDA 1','HDA2','SEXO','MOTIVO1','MOTIVO2']
BASE_CATEGORICAL = ['PULSOS','PPA','B2','SOPRO','HDA 1','HDA2','SEXO','MOTIVO1','MOTIVO2']
SCENARIOS = {'A': NUMERIC + BASE_CATEGORICAL, 'B': NUMERIC + ['SEXO'], 'B_contexto': NUMERIC + [x for x in BASE_CATEGORICAL if x not in ['PULSOS','B2','SOPRO']]}
# Historical envelopes from old pipeline; suspicion only, not diagnoses or hard validation.
SUSPECT_ENVELOPES = {'Peso':(1.,150.),'Altura':(40.,200.),'IMC':(8.,60.),'FC':(40.,220.),'PA SISTOLICA':(50.,200.),'PA DIASTOLICA':(30.,130.)}
PROJECT_ROOT = next((p for p in Path(__file__).resolve().parents if (p / 'pyproject.toml').is_file()), Path.cwd())
SOURCE_DEFAULT = PROJECT_ROOT / 'dados' / 'raw' / 'UCMF_raw.csv'
PARTITIONS_DEFAULT = PROJECT_ROOT / 'config' / 'particoes_referencia.csv'
EXPECTED_SOURCE_SHA256 = '35e68400d6bec51bbf74857c0f0e0487161b3495b5f4fefbc2cc57af24824ea1'
