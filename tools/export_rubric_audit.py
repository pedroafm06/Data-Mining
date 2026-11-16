"""Verify the final A2 run and export only aggregated results."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

import joblib
import numpy as np
import pandas as pd

from kdd_revision.evaluation_stats import paired_cluster_bootstrap, tree_rules
from kdd_revision.full_kdd import folds_for
from kdd_revision.mining import metric, select_candidate
from kdd_revision.rubric_audit import ALL_POOLS, AUDIT_DIR, FAMILIES, load_development, search_space
from kdd_revision.schema import SOURCE_DEFAULT, TARGET

RESULT_DIR = Path('resultados/a2/revisao_final_2026_11_16')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def export(source=SOURCE_DEFAULT, root=ROOT):
    root = Path(root)
    audit = root / AUDIT_DIR
    verification = read_json(audit / 'verification.json')
    manifest = read_json(audit / 'manifest.json')
    raw, _, data, y, groups, source_hash = load_development(root, source)
    if not verification['complete'] or verification['source_sha256'] != source_hash:
        raise ValueError('The completed run must match the source CSV')
    for name, digest in manifest['code'].items():
        if sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Run source changed: {name}')
    for name, digest in manifest['outputs'].items():
        if sha256((audit / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Local run artifact changed: {name}')

    metrics = pd.read_csv(audit / 'family_nested_metrics.csv')
    outer_metrics = pd.read_csv(audit / 'outer_fold_metrics.csv')
    expected = {(pool, family) for pool in ALL_POOLS for family in FAMILIES}
    if len(metrics) != len(expected) or set(zip(metrics.pool, metrics.family)) != expected:
        raise ValueError('The run must contain exactly one result per procedure')
    if len(outer_metrics) != 5 * len(expected):
        raise ValueError('The run must contain five outer evaluations per procedure')
    folds = folds_for(y, groups, 5, 743)
    membership = pd.read_csv(audit / 'outer_membership.csv', dtype={'ID': str}).set_index('ID')
    if not membership.index.is_unique or not set(membership.index) == set(data.ID):
        raise ValueError('Each record must appear once in the validation cuts')
    original = pd.read_csv(root / 'artifacts/a2_mining/particoes_modelagem.csv', dtype={'ID': str}).set_index('ID')
    if set(data.ID) & set(original.index[original.partition.eq('test')]):
        raise ValueError('The historical test must remain outside the analysis')
    for fold, (train, val) in enumerate(folds):
        if not set(groups.iloc[train]).isdisjoint(groups.iloc[val]):
            raise ValueError('A component crosses an external split')
        if set(membership.index[membership.outer_fold.eq(fold)]) != set(data.ID.iloc[val]):
            raise ValueError('Recorded external cuts differ from the frozen cuts')

    options = search_space()
    predictions = {}
    for row in metrics.itertuples(index=False):
        pool, family = row.pool, row.family
        frame = pd.read_csv(audit / f'oof_{pool}_{family}.csv', dtype={'ID': str})
        if not frame.ID.equals(data.ID) or not np.array_equal(frame.y, y) or not frame.group.equals(groups):
            raise ValueError(f'Predictions are not aligned: {pool}/{family}')
        probabilities = predictions[f'{pool}/{family}'] = frame.p.to_numpy()
        for name, value in metric(y, probabilities).items():
            np.testing.assert_allclose(getattr(row, name), value, atol=1e-12, rtol=1e-12)
        family_options = [candidate for candidate in options if candidate['kind'] == family]
        for fold, (_, val) in enumerate(folds):
            scores = pd.read_csv(audit / f'inner_scores_{pool}_{fold}.csv')
            choice = select_candidate(scores[scores.kind.eq(family)], family_options)
            outer = outer_metrics.query('pool == @pool and family == @family and outer_fold == @fold').iloc[0]
            if outer.candidate != choice['name']:
                raise ValueError(f'Unexpected internal selection: {pool}/{family}/{fold}')
            for name, value in metric(y[val], probabilities[val]).items():
                np.testing.assert_allclose(outer[name], value, atol=1e-12, rtol=1e-12)

    best = {pool: metrics.loc[metrics.pool.eq(pool)].sort_values('balanced_accuracy', ascending=False).iloc[0].family
            for pool in ALL_POOLS}
    comparisons = [(f'{pool}/{a}', f'{pool}/{b}') for pool in ALL_POOLS
                   for a, b in [('forest', 'logistic'), ('tree', 'forest'), ('tree', 'logistic')]]
    uncertainty = paired_cluster_bootstrap(y, predictions, groups, comparisons)

    raw_body = raw.drop(columns=['ID', TARGET])
    signatures = raw_body.groupby(list(raw_body), sort=False, dropna=False).ngroup()
    original_groups = data.ID.map(original.group)
    grouping = pd.DataFrame({
        'signature': signatures, 'label': y, 'old_group': original_groups,
        'group': groups, 'fold': data.ID.map(membership.outer_fold),
    })
    by_signature = grouping.groupby('signature').agg(
        n=('fold', 'size'), old_groups=('old_group', 'nunique'),
        groups=('group', 'nunique'), folds=('fold', 'nunique'), labels=('label', 'nunique'),
    )
    if (by_signature.groups.gt(1) | by_signature.folds.gt(1)).any():
        raise ValueError('Exact raw matches cross groups or folds')
    duplicate_groups = by_signature.old_groups.gt(1)
    contradictory = by_signature.labels.gt(1)

    base = pd.read_csv(source, dtype=str, keep_default_na=False)
    repeated = base.drop(columns='ID').duplicated()
    labelled = base.ID.map(original.partition).isin(['development', 'test', 'quarentena_equivalencia', 'quarentena_equivalencia_componente'])
    a1 = {
        'raw_duplicate_copies_excluding_id': int(repeated.sum()),
        'labelled_copies': int((repeated & labelled).sum()),
        'unlabelled_copies': int((repeated & ~labelled).sum()),
        'remaining_labelled_after_a1_deduplication': int((~repeated & labelled).sum()),
    }

    errors = {}
    rules = {}
    analysis_families = {'FISIO8': 'forest', 'STRICT4': 'logistic', 'CLINICO': 'tree'}
    no_murmur = data.SOPRO.eq('Ausente').fillna(False)
    with_murmur = data.SOPRO.notna() & ~no_murmur
    for pool, family in analysis_families.items():
        predicted = predictions[f'{pool}/{family}'] >= .5
        fn = (y == 1) & ~predicted
        fp = (y == 0) & predicted
        tp = (y == 1) & predicted
        errors[pool] = {
            'family': family, 'fn': int(fn.sum()), 'fp': int(fp.sum()),
            'fn_explicitly_without_murmur': int((fn & no_murmur).sum()),
            'fp_explicitly_with_murmur': int((fp & with_murmur).sum()),
            'median_age_fn': float(data.loc[fn, 'IDADE'].median()),
            'median_age_tp': float(data.loc[tp, 'IDADE'].median()),
        }
    # The rule extractor is applied to locally generated models from the verified run.
    for pool in ('FISIO8', 'CLINICO'):
        fitted = joblib.load(audit / f'final_model_{pool}_tree.joblib')
        rules[pool] = tree_rules(fitted, data[['ID', *ALL_POOLS[pool]]], y)
        if sum(rule['n'] for rule in rules[pool]) != len(y):
            raise ValueError('Tree leaves must cover the development set')

    importance = pd.read_csv(audit / 'outer_permutation_importance.csv')
    ranking = importance.groupby(['pool', 'family', 'variable']).BA_drop.agg(['mean', 'std']).reset_index()
    probes = pd.read_csv(audit / 'variable_probes.csv')
    summary = {
        'source_sha256': source_hash, 'protocol_sha256': verification['protocol_sha256'],
        'evaluation_code_sha256': manifest['code'],
        'membership_sha256': sha256((root / 'artifacts/a2_mining/particoes_modelagem.csv').read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
        'n_original': len(base), 'n_original_variables': len(base.columns), 'n_labelled': int(labelled.sum()),
        'n_unlabelled': int((~labelled).sum()), 'n_development': len(data),
        'n_historical_test_not_rescored': int(original.partition.eq('test').sum()),
        'class_counts': {'Normal': int((y == 0).sum()), 'Anormal': int((y == 1).sum())},
        'pools': ALL_POOLS, 'primary_pool': 'FISIO8', 'sensitivity_pool': 'STRICT4', 'exploratory_pool': 'CLINICO',
        'best_family_by_pool': best, 'metrics': metrics.to_dict('records'), 'bootstrap': uncertainty,
        'importance': ranking.to_dict('records'), 'errors': errors, 'tree_rules_development': rules,
        'a1_reconciliation': a1,
        'grouping': {
            'previous_groups': original_groups.nunique(), 'final_groups': groups.nunique(),
            'exact_signatures_split_between_old_groups': int(duplicate_groups.sum()),
            'records_in_those_signatures': int(by_signature.loc[duplicate_groups, 'n'].sum()),
            'exact_signatures_with_conflicting_labels': int(contradictory.sum()),
            'records_in_conflicting_signatures': int(by_signature.loc[contradictory, 'n'].sum()),
            'exact_signatures_split_between_final_folds': 0,
            'fold_sizes': [len(val) for _, val in folds],
        },
        'missing_percent_by_fisio_variable': {col: float(100 * data[col].isna().mean()) for col in ALL_POOLS['FISIO8']},
        'eda': {
            'sopro_by_status': {
                label: {'n': int(mask.sum()), 'n_anormal': int(((y == 1) & mask).sum())}
                for label, mask in [('Ausência registrada', no_murmur), ('Presença registrada', with_murmur)]
                if mask.sum() >= 20
            },
            'median_age': {str(k): float(data.loc[y == k, 'IDADE'].median()) for k in (0, 1)},
            'median_fc': {str(k): float(data.loc[y == k, 'FC'].median()) for k in (0, 1)},
            'explicitly_without_murmur_anormal': int(((y == 1) & no_murmur).sum()),
        },
        'variable_probes': probes.astype(object).where(probes.notna(), None).to_dict('records'),
        'collection_controls': pd.read_csv(audit / 'collection_process_controls.csv').to_dict('records'),
        'null_control': read_json(audit / 'permuted_label_control.json'),
        'final_choices': read_json(audit / 'final_choices.json'),
        'verification': {
            'oof_procedures_checked': len(metrics), 'external_selections_checked': len(outer_metrics),
            'historical_test_rows_used': 0, 'source_preserved': verification['source_preserved'],
        },
    }
    out = root / RESULT_DIR
    out.mkdir(parents=True, exist_ok=True)
    for name in ('family_nested_metrics.csv', 'outer_fold_metrics.csv', 'variable_probes.csv',
                 'collection_process_controls.csv'):
        (out / name).write_text((audit / name).read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
    ranking.to_csv(out / 'permutation_summary.csv', index=False, lineterminator='\n')
    (out / 'reviewed_results.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False, default=lambda x: x.item()) + '\n', encoding='utf-8', newline='\n')
    print(f'Verified {len(metrics)} procedures and {len(outer_metrics)} outer choices. Results: {out}')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE_DEFAULT)
    export(parser.parse_args().source)
