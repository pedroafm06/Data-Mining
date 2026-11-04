"""Copy a fixed set of aggregate diagnostics into the versioned results folder."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def export(root=ROOT):
    root = Path(root)
    source = root / 'artifacts/a2_preprocessing'
    destination = root / 'resultados/a2/preprocessamento'
    destination.mkdir(parents=True, exist_ok=True)
    files = {
        'diagnostics': ['imputation_alternatives.csv', 'bmi_coherence_alternatives.csv',
                        'transform_profiles.csv', 'diagnostic_contract.json'],
        'report': ['perfil_21_variaveis.csv', 'categorias_completas.csv',
                   'decisoes_21_variaveis.csv', 'decisoes_21_variaveis.json',
                   'bivariadas_numericas.csv', 'bivariadas_categoricas.csv',
                   'contingencias.csv', 'altura_idade_pareada.png',
                   'comparacao_imputacoes_resumo.csv'],
        '': ['decisoes_imputacao.csv', 'dicionario_colunas_matrizes.csv', 'verification.json'],
    }
    # ID and absolute dates are identifiers, never nominal frequency exports.
    categories = pd.read_csv(source / 'report/categorias_completas.csv')
    if categories.variable.isin(['ID', 'Atendimento', 'DN']).any():
        raise ValueError('Category export contains identifiers or absolute dates')
    copied = {}
    for folder, names in files.items():
        for name in names:
            original = source / folder / name
            if original.suffix == '.csv':
                columns = pd.read_csv(original, nrows=0).columns
                if any(c in columns for c in ['ID', 'row_number', 'candidate_group']):
                    raise ValueError(f'Row identifiers are not aggregate results: {name}')
            target = destination / name
            shutil.copy2(original, target)
            copied[name] = sha256(target.read_bytes()).hexdigest()
    core = json.loads((source / 'summary.json').read_text())
    summary = {key: core[key] for key in [
        'n_source', 'n_fit', 'n_test', 'n_unlabeled', 'n_quarantine',
        'mask_counts_by_numeric', 'imputation_choices', 'log_columns',
        'source_sha256', 'partition_sha256', 'models_fitted',
        'relative_age_requires_cohort_assumption', 'diagnostic_limit', 'future_cv']}
    summary['etapa'] = 'A2: limpeza e transformação; modelagem com esta preparação pendente'
    summary['representacoes'] = {
        name: {key: value for key, value in info.items() if key in ['n_rows', 'n_columns', 'sha256']}
        for name, info in core['matrices'].items()}
    (destination / 'resumo.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    copied['resumo.json'] = sha256((destination / 'resumo.json').read_bytes()).hexdigest()
    (destination / 'manifesto.json').write_text(json.dumps({
        'scope': 'Aggregate diagnostics of current A2 preprocessing; no clinical rows',
        'source_sha256': core['source_sha256'],
        'files_sha256': copied,
        'self_excluded': True,
    }, ensure_ascii=False, indent=2) + '\n')
    return destination


if __name__ == '__main__':
    print(export().relative_to(ROOT))
