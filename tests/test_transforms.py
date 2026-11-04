import numpy as np
import pandas as pd
import pytest
from kdd_revision.transforms import build_preprocessor


def test_unseen_categories_do_not_change_training_statistics():
    train=pd.DataFrame({'Peso':[10.,20.,np.nan],'SEXO':['M','F',None]})
    p=build_preprocessor(['Peso','SEXO'])
    p.fit(train)
    median=p.named_transformers_['numeric'].named_steps['impute'].statistics_.copy()
    before=p.get_feature_names_out().tolist()
    transformed=p.transform(pd.DataFrame({'Peso':[100000.,np.nan],'SEXO':['NOVA',pd.NA]}))
    assert transformed.shape[0]==2
    np.testing.assert_equal(median,p.named_transformers_['numeric'].named_steps['impute'].statistics_)
    assert before==p.get_feature_names_out().tolist()
    assert median[0]==15


def test_all_missing_columns_are_preserved_and_finite():
    train=pd.DataFrame({'Peso':[np.nan,np.nan],'SEXO':[np.nan,np.nan]})
    p=build_preprocessor(['Peso','SEXO'])
    x=p.fit_transform(train)
    x=x.toarray() if hasattr(x,'toarray') else x
    assert x.shape[1]>=2 and np.isfinite(x).all()
    assert len(p.get_feature_names_out())==x.shape[1]


@pytest.mark.parametrize('name',['ID','DN','Atendimento','NORMAL X ANORMAL','flag_pas_le_pad','meta_IDADE_source','INVENTADO'])
def test_forbidden_predictors(name):
    with pytest.raises(ValueError):build_preprocessor(['Peso',name])


def test_log_is_explicit_and_rejects_negative_input():
    train=pd.DataFrame({'Peso':[0.,2.,3.]})
    p=build_preprocessor(['Peso'],log=True,scale=False,add_missing=False)
    np.testing.assert_allclose(p.fit_transform(train).ravel(),np.log1p(train.Peso))
    with pytest.raises(ValueError):p.transform(pd.DataFrame({'Peso':[-2.]}))


def test_extra_columns_are_dropped_and_input_unmodified():
    frame=pd.DataFrame({'Peso':[2.,4.],'NORMAL X ANORMAL':['Normal','Anormal'],'ID':['a','b']})
    original=frame.copy(deep=True)
    p=build_preprocessor(['Peso'],scale=False,add_missing=False)
    assert p.fit_transform(frame).shape==(2,1)
    pd.testing.assert_frame_equal(frame,original)
