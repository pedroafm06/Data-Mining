"""Reconstruct frozen historical memberships from source+seeds, without models.

No row IDs have to be published. Diagnostic columns are used only by the frozen
candidate-equivalence recipe, never as new classifiers' predictors.
"""
from pathlib import Path
from hashlib import sha256
import numpy as np
import pandas as pd
from .schema import PROJECT_ROOT,SOURCE_DEFAULT,TARGET,SCENARIOS
from .preprocessing.run import validated_source
from .prepare import prepare_dataframe
from .preprocessing.preparation import prepare_final,model_frame
from .experiments import make_splits
from .mining import combine_groups


def derive_memberships(source=SOURCE_DEFAULT):
    source,_=validated_source(source);raw=pd.read_csv(source,dtype=str,keep_default_na=False)
    historical=prepare_dataframe(raw)
    ids=historical.eligibility.loc[historical.eligibility.elegivel_principal,'ID']
    old=historical.data.set_index('ID').loc[ids].reset_index();oldgroups=historical.groups.set_index('ID').loc[ids,'split_group'].reset_index(drop=True)
    y=old[TARGET].eq('Anormal').astype(int).to_numpy();dev,test,folds=make_splits(y,oldgroups,old.ID)
    reference=pd.DataFrame({'ID':old.ID,'candidate_group':oldgroups,'partition':'development','inner_fold':-1})
    reference.loc[test,'partition']='test'
    for k,(_,val) in enumerate(folds):reference.loc[dev[val],'inner_fold']=k
    current=model_frame(prepare_final(raw).data)
    assignment=current.ID.map(reference.set_index('ID').partition).fillna('unlabeled')
    signature=pd.util.hash_pandas_object(current[SCENARIOS['A']],index=False).astype(str)
    informative=current[SCENARIOS['A']].notna().sum(axis=1).ge(8)&assignment.isin(['development','test'])
    eq=pd.DataFrame({'hash':signature[informative],'partition':assignment[informative]})
    crossed=set(eq.groupby('hash').partition.nunique().loc[lambda x:x.gt(1)].index)
    assignment.loc[assignment.eq('development')&signature.isin(crossed)]='quarentena_equivalencia'
    groups=combine_groups(current,reference)
    extra=assignment.eq('development')&groups.isin(set(groups[assignment.eq('test')]))
    assignment.loc[extra]='quarentena_equivalencia_componente'
    return pd.DataFrame({'ID':current.ID,'group':groups,'partition':assignment}),reference


def bootstrap(root=PROJECT_ROOT,source=SOURCE_DEFAULT):
    root=Path(root);mapping,reference=derive_memberships(source)
    out=root/'artifacts/a2_mining/particoes_modelagem.csv';out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        old=pd.read_csv(out,dtype={'ID':str});pd.testing.assert_frame_equal(old,mapping,check_dtype=False)
    else:mapping.to_csv(out,index=False,lineterminator='\n')
    return {'n_development':int(mapping.partition.eq('development').sum()),'n_test':int(mapping.partition.eq('test').sum()),'membership_sha256':sha256(out.read_bytes()).hexdigest()}
