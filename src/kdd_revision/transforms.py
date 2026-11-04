"""Train-fitted feature transformations; no global statistics or implicit feature discovery.

Patterns: sklearn docs for ColumnTransformer, SimpleImputer, OneHotEncoder and
common_pitfalls.html. Every instance must be fitted inside the training fold.
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from .schema import NUMERIC, CATEGORICAL, TARGET


def _categorical_array(x):
    """Normalize pandas NA/None to numpy.nan and nonmissing tokens to strings."""
    frame=pd.DataFrame(x).astype(object)
    return frame.map(lambda v: np.nan if pd.isna(v) else str(v)).to_numpy(dtype=object)


def _numeric_array(x):
    frame=pd.DataFrame(x).apply(pd.to_numeric,errors='raise')
    values=frame.to_numpy(dtype=float,na_value=np.nan)
    if np.isinf(values).any():
        raise ValueError('Non-finite numeric predictor: invalidate source or mask through declared quality policy first.')
    return values


def _nonnegative_log1p(x):
    values=np.asarray(x,dtype=float)
    if (values<0).any():
        raise ValueError('log1p option is restricted to nonnegative predictors; do not silently clip source data.')
    return np.log1p(values)


def build_preprocessor(feature_names, scale=True, add_missing=True, log=False):
    """Return an unfitted preprocessor restricted to named, approved predictors.

    ``feature_names`` is the scenario contract, not a dtype query. Missing
    indicators are part of the fitted preprocessing and must be assessed by
    ablation; metadata flags never enter. Log is an experimental option, not a
    requirement that predictors have normal distributions.
    """
    names=list(feature_names)
    allowed=set(NUMERIC)| (set(CATEGORICAL)-{TARGET})
    if not names or len(set(names))!=len(names):
        raise ValueError('Predictor names must be a non-empty unique list.')
    forbidden=[c for c in names if c not in allowed]
    if forbidden:
        raise ValueError(f'Forbidden or unknown predictors: {forbidden}')
    numeric=[c for c in names if c in NUMERIC]
    categorical=[c for c in names if c not in NUMERIC]
    blocks=[]
    if numeric:
        steps=[('numeric',FunctionTransformer(_numeric_array,feature_names_out='one-to-one')),
               ('impute',SimpleImputer(strategy='median',keep_empty_features=True,add_indicator=add_missing))]
        # Imputation precedes log; missing indicators are 0/1 and remain well-defined.
        # Log on indicators preserves their binary information, and no clinical
        # interpretation is assigned to either transformed representation.
        if log: steps.append(('log',FunctionTransformer(_nonnegative_log1p,feature_names_out='one-to-one')))
        if scale: steps.append(('scale',StandardScaler()))
        blocks.append(('numeric',Pipeline(steps),numeric))
    if categorical:
        steps=[('tokens',FunctionTransformer(_categorical_array,feature_names_out='one-to-one')),
               ('impute',SimpleImputer(strategy='constant',fill_value='__AUSENTE__',keep_empty_features=True)),
               ('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=True))]
        blocks.append(('categorical',Pipeline(steps),categorical))
    return ColumnTransformer(blocks,remainder='drop',verbose_feature_names_out=True)
