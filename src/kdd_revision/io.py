"""Explicit filesystem boundary. All source files are read-only."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import numpy as np
import pandas as pd
from .prepare import prepare_dataframe, safe_model_frame
from .schema import VERSION, SOURCE_DEFAULT, ORIGINAL, NUMERIC, CATEGORICAL, SCENARIOS, PROJECT_ROOT


def file_hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write_prepared(source=SOURCE_DEFAULT, output=None):
    source=Path(source).resolve()
    output=Path(output or PROJECT_ROOT/'artifacts/prepared').resolve()
    if output==source.parent or output in source.parents:
        raise ValueError('Output must be a separate directory')
    source_before=file_hash(source)
    raw=pd.read_csv(source,dtype=str,keep_default_na=False).astype(object)
    result=prepare_dataframe(raw)
    output.mkdir(parents=True,exist_ok=True)
    for name,frame in [('dados_tratados',result.data),('alteracoes',result.changes),('elegibilidade',result.eligibility),('grupos',result.groups)]:
        frame.to_csv(output/(name+'.csv'),index=False)
    # The masked variant and cell changes are explicit, avoiding hidden matrix repair.
    safe=safe_model_frame(result.data)
    variant_changes=[]
    for c in NUMERIC:
        mask=result.data[c].notna() & safe[c].isna()
        for i in result.data.index[mask]:
            variant_changes.append({'ID':result.data.at[i,'ID'],'coluna':c,'antes':result.data.at[i,c],'depois':None,'regra':'explicit_mask_suspect_matrix_policy'})
    safe.to_csv(output/'dados_variante_segura.csv',index=False)
    pd.DataFrame(variant_changes,columns=['ID','coluna','antes','depois','regra']).to_csv(output/'alteracoes_variante_segura.csv',index=False)
    (output/'quality_summary.json').write_text(json.dumps(result.summary,ensure_ascii=False,indent=2,allow_nan=False))
    source_after=file_hash(source)
    if source_before!=source_after:raise RuntimeError('Source changed during preparation')
    # Hash all historical report/slide/notebook sources, not dependencies or new outputs.
    course_root=source.parent.parent
    historical=[]
    for p in course_root.rglob('*'):
        if not p.is_file() or p.suffix not in ('.pdf','.ipynb','.md','.py','.csv','.json','.zip'):continue
        if any(x in p.parts for x in ['node_modules','.git','.venv','Revisao KDD']):continue
        historical.append({'path':str(p.relative_to(course_root)),'bytes':p.stat().st_size,'sha256':file_hash(p)})
    pipeline_files=[x for folder in [PROJECT_ROOT/'src/kdd_revision',PROJECT_ROOT/'config'] for x in folder.rglob('*') if x.is_file() and x.suffix in ('.py','.json')]
    pipeline_files.extend(x for x in [PROJECT_ROOT/'pyproject.toml',PROJECT_ROOT/'requirements.lock',PROJECT_ROOT/'run.sh'] if x.is_file())
    pipeline_manifest={str(x.relative_to(PROJECT_ROOT)):file_hash(x) for x in sorted(pipeline_files)}
    manifest={'pipeline_sha256_by_file':pipeline_manifest,'version':VERSION,'created_utc':datetime.now(timezone.utc).isoformat(),'source':str(source),'source_sha256':source_before,'source_preserved':True,'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'historical_sources':sorted(historical,key=lambda x:x['path']),'outputs':{p.name:file_hash(p) for p in sorted(output.glob('*')) if p.is_file() and p.name!='manifest.json'}}
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return result
