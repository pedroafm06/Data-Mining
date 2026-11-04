import numpy as np
import pandas as pd
from kdd_revision.analysis import variable_profiles, paired_correlations, bivariate_numeric,bivariate_categorical
from kdd_revision.schema import ORIGINAL,NUMERIC,TARGET


def test_all_original_variables_have_profile_even_when_absent():
    profiles=variable_profiles(pd.DataFrame({'ID':['a','b'],'Peso':[1.,np.nan]}),'fixture')
    assert profiles.variable.tolist()==ORIGINAL
    assert len(profiles)==21
    row=profiles.set_index('variable').loc['Peso'];assert row.missing_n==1 and row.n_numeric==1
    assert not profiles.set_index('variable').loc['HDA2','present']


def test_paired_correlation_compares_same_ids_only():
    raw=pd.DataFrame({'ID':['a','b','c'],'Altura':[1,2,3],'IDADE':[1,2,3],'Peso':[2,4,6]})
    revised=pd.DataFrame({'ID':['c','a','b'],'Altura':[3,1,np.nan],'IDADE':[3,1,2],'Peso':[6,2,4]})
    results=paired_correlations(raw,revised)
    pair=results[(results.x=='Altura')&(results.y=='IDADE')]
    assert pair.same_ids_n.tolist()==[2,2]
    assert np.allclose(pair.pearson,1)


def test_welch_difference_is_means_not_medians():
    frame=pd.DataFrame({c:[1.,2.,9.,10.,11.,12.] for c in NUMERIC})
    frame[TARGET]=['Normal']*3+['Anormal']*3
    rows=bivariate_numeric(frame)
    assert np.allclose(rows.mean_difference_anormal_minus_normal,7)
    assert (rows.mean_difference_ci95_low<rows.mean_difference_ci95_high).all()


def test_sparse_categories_do_not_report_invalid_inferential_p():
    frame=pd.DataFrame({'SEXO':['M','M','M','M','RARO'],TARGET:['Normal','Normal','Anormal','Normal','Anormal']})
    results,counts=bivariate_categorical(frame)
    row=results.set_index('variable').loc['SEXO']
    assert not row.asymptotic_conditions_met
    assert np.isnan(row.p_asymptotic_if_adequate)
    assert counts.total.sum()==5


def test_single_target_class_returns_not_testable():
    frame=pd.DataFrame({'SEXO':['M','F'],TARGET:['Normal','Normal']})
    results,_=bivariate_categorical(frame)
    row=results.set_index('variable').loc['SEXO']
    assert row.test_status=='not_testable_single_class_or_category'
    assert not row.asymptotic_conditions_met
