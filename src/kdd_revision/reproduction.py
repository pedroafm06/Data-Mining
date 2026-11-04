"""Independent checks for frozen-run reuse and end-to-end model reapplication."""
from pathlib import Path
from hashlib import sha256
import json,sys,platform
from importlib.metadata import distributions
import joblib
import numpy as np
import pandas as pd
from .schema import PROJECT_ROOT,SOURCE_DEFAULT,TARGET,SCENARIOS
from .preprocessing.run import validated_source
from .preprocessing.preparation import prepare_final,model_frame
from .full_kdd import write,protocol


def verify_saved_run(root=PROJECT_ROOT,source=SOURCE_DEFAULT):
    root=Path(root);source,source_hash=validated_source(source);a=root/'artifacts/a2_mining'
    j=lambda name:json.loads((a/name).read_text())
    check=j('verification.json');manifest=j('manifest.json')
    if not check['complete'] or check['source_sha256']!=source_hash:raise ValueError('No complete run for the input')
    frozen_hash=sha256(json.dumps(protocol(),sort_keys=True).encode()).hexdigest()
    if frozen_hash!=check['protocol_sha256']:raise ValueError('Search protocol changed; run full mining again')
    # Reporting/application may evolve without pretending the fitting code changed.
    model_files=['src/kdd_revision/mining.py','src/kdd_revision/full_kdd.py','src/kdd_revision/schema.py',
        'src/kdd_revision/prepare.py','src/kdd_revision/preprocessing/preparation.py','src/kdd_revision/preprocessing/transformer.py','src/kdd_revision/experiments.py']
    for name in model_files:
        if sha256((root/name).read_bytes()).hexdigest()!=manifest['code_sha256'][name]:raise ValueError(f'Model-fitting code changed: {name}; rerun mining')
    for name,expected in manifest['outputs_sha256'].items():
        if sha256((a/name).read_bytes()).hexdigest()!=expected:raise ValueError(f'Frozen output changed: {name}')
    events=j('events.json');freeze=next(i for i,e in enumerate(events) if e['event']=='all_selections_frozen')
    assert all(i>freeze for i,e in enumerate(events) if e['event']=='test_evaluated')
    safe=model_frame(prepare_final(pd.read_csv(source,dtype=str,keep_default_na=False)).data)
    mapping=pd.read_csv(a/'particoes_modelagem.csv',dtype={'ID':str});assert safe.ID.tolist()==mapping.ID.tolist()
    test=safe.loc[mapping.partition.eq('test')].reset_index(drop=True);results={}
    reference=pd.read_csv(root/'config/particoes_referencia.csv',dtype={'ID':str})
    assert set(test.ID)==set(reference.loc[reference.partition.eq('test'),'ID'])
    for scenario in SCENARIOS:
        model=joblib.load(a/f'model_{scenario}.joblib');saved=pd.read_csv(a/f'predicoes_teste_{scenario}.csv',dtype={'ID':str})
        assert saved.ID.tolist()==test.ID.tolist()
        y=test[TARGET].map({'Normal':0,'Anormal':1}).to_numpy();assert np.array_equal(y,saved.y.to_numpy())
        p=model.proba(test);delta=float(np.max(abs(p-saved.p.to_numpy())))
        assert delta<=1e-12
        predicted=(p>=.5).astype(int);m=j('test_metrics.json')[scenario]
        counts={'tn':int(((y==0)&(predicted==0)).sum()),'fp':int(((y==0)&(predicted==1)).sum()),
                'fn':int(((y==1)&(predicted==0)).sum()),'tp':int(((y==1)&(predicted==1)).sum())}
        assert all(counts[k]==m[k] for k in counts)
        results[scenario]={'max_abs_prediction_difference':delta,'identical_classes':True,'confusion_counts_verified':counts}
    env={'python':sys.version.split()[0],'platform':platform.system(),'packages':dict(sorted({d.metadata['Name']:d.version for d in distributions()}.items()))}
    out=root/'artifacts/a2_kdd';out.mkdir(parents=True,exist_ok=True);write(out/'environment.json',env)
    output={'complete':True,'source_sha256':source_hash,'protocol_sha256':frozen_hash,'frozen_outputs_verified':len(manifest['outputs_sha256']),
        'models_reapplied':results,'test_membership_unchanged':True,'no_new_model_selection':True}
    write(out/'reproduction.json',output);return output
