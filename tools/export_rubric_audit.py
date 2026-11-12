"""Export aggregate evidence and manuscript inputs; never exports clinical rows.

Every number quoted in the paper and slides must come from reviewed_results.json,
which this script writes from the local audit run (artifacts/a2_rubric_audit).
"""
from pathlib import Path
from hashlib import sha256
import argparse, sys, json, shutil
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src'))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.cbook import boxplot_stats
from kdd_revision.rubric_audit import load_development, SCENARIOS_AUDIT, EXCLUDED_REASONS
from kdd_revision.schema import SOURCE_DEFAULT, TARGET, SCENARIOS
from kdd_revision.preprocessing.preparation import prepare_final, model_frame

OUT = ROOT / 'resultados/a2/auditoria_2026_11_07'
PAPER_RESULTS = ROOT / 'paper/a2_ieee_2026_11_07/results/reviewed_results.json'
PRIMARY, SENSITIVITY = 'CLINICO', ['FISIO8', 'STRICT4']
LABELLED = ['development', 'test', 'quarentena_equivalencia']


def write_text(path, text):
    """LF line endings on every OS, so published SHA-256 values are portable."""
    Path(path).write_text(text, encoding='utf-8', newline='\n')


def copy_lf(src, dst):
    if src.suffix in ('.csv', '.json'):
        write_text(dst, src.read_text(encoding='utf-8').replace('\r\n', '\n'))
    else:
        shutil.copy2(src, dst)


def a1_reconciliation(source):
    """A1 dropped exact duplicates (all columns but ID); A2 keeps labelled copies inside one group."""
    raw = pd.read_csv(source, dtype=str, keep_default_na=False)
    part = pd.read_csv(ROOT / 'artifacts/a2_mining/particoes_modelagem.csv', dtype={'ID': str}).set_index('ID')
    raw = raw.assign(partition=raw.ID.map(part.partition).to_numpy(), group=raw.ID.map(part.group).to_numpy())
    body = raw.drop(columns=['ID', 'partition', 'group'])
    key = pd.util.hash_pandas_object(body, index=False)
    duplicate = body.duplicated(keep='first')
    labelled = raw.partition.isin(LABELLED)
    prepared = model_frame(prepare_final(raw.drop(columns=['partition', 'group'])).data)
    filled = prepared[SCENARIOS['A']].notna().sum(axis=1)  # same informative-field rule used to build the groups
    first_group = raw.assign(key=key)[~duplicate].set_index(key[~duplicate]).group
    first_part = raw.assign(key=key)[~duplicate].set_index(key[~duplicate]).partition
    d = raw[duplicate & labelled].assign(key=key[duplicate & labelled])
    same_group = d.group.to_numpy() == first_group.loc[d.key].to_numpy()
    same_part = d.partition.to_numpy() == first_part.loc[d.key].to_numpy()
    near_empty = filled[duplicate & labelled].to_numpy() < 8
    return {
        'n_source': int(len(raw)), 'n_a1_duplicates': int(duplicate.sum()),
        'n_a1_duplicates_unlabelled': int((duplicate & ~labelled).sum()),
        'n_a1_duplicates_labelled': int((duplicate & labelled).sum()),
        'n_unlabelled': int((~labelled).sum()), 'n_labelled_a2': int(labelled.sum()),
        'n_a1_final': int((~duplicate & labelled).sum()),
        'labelled_duplicates_by_partition': {k: int(v) for k, v in d.partition.value_counts().items()},
        'labelled_duplicates_same_group_as_copy': int(same_group.sum()),
        'labelled_duplicates_other_group': int((~same_group).sum()),
        'labelled_duplicates_other_group_lt8_prepared_fields': int((~same_group & near_empty).sum()),
        'labelled_duplicates_other_partition_than_copy': int((~same_part).sum()),
        'labelled_duplicates_other_partition_with_ge8_fields': int((~same_part & ~near_empty).sum()),
        'group_rule': 'records with identical prepared predictor values and at least 8 non-missing prepared fields share a group; groups never split across folds',
    }


def eda_summary(data, y, assoc):
    def box(column):
        stats = {}
        for label, name in [(0, 'Normal'), (1, 'Anormal')]:
            values = pd.to_numeric(data.loc[y == label, column], errors='coerce').dropna().to_numpy()
            s = boxplot_stats(values, whis=1.5)[0]
            stats[name] = {k: float(s[k]) for k in ['whislo', 'q1', 'med', 'q3', 'whishi', 'mean']} | {'n': int(len(values))}
        return stats
    age = pd.to_numeric(data.IDADE, errors='coerce')
    categories = assoc[assoc.variable.isin(['SOPRO', 'B2', 'PULSOS', 'Convenio', 'HDA 1', 'PPA'])]
    convenio = assoc[assoc.variable.eq('Convenio')].set_index('value')
    sus = convenio.loc['SUS'] if 'SUS' in convenio.index else None
    return {
        'class_counts': {'Normal': int((y == 0).sum()), 'Anormal': int((y == 1).sum())},
        'anormal_percent': float(100 * y.mean()),
        'box_IDADE': box('IDADE'), 'box_FC': box('FC'),
        'percent_under_1_year': {n: float(100 * age[(y == k) & age.notna()].lt(1).mean()) for k, n in [(0, 'Normal'), (1, 'Anormal')]},
        'categories': categories.to_dict('records'),
        'convenio_SUS': None if sus is None else {'n': int(sus.n_development), 'anormal_percent': float(100 * sus.anormal_rate)},
        'missing_percent_by_clinico_variable': {c: float(100 * data[c].isna().mean()) for c in SCENARIOS_AUDIT[PRIMARY]},
        'missing_percent_HDA2': float(100 * data['HDA2'].isna().mean()),
    }


def error_analysis(a, data, best):
    """Aggregate profile of out-of-fold errors by murmur finding and age (no rows exported)."""
    result = {}
    for pool in SCENARIOS_AUDIT:
        oof = pd.read_csv(a / f'oof_{pool}_{best[pool]}.csv', dtype={'ID': str})
        d = data[['ID', 'SOPRO', 'IDADE']].astype({'ID': str}).merge(oof, on='ID', validate='one_to_one')
        pred = d.p.ge(.5); fn = d.y.eq(1) & ~pred; fp = d.y.eq(0) & pred; tp = d.y.eq(1) & pred
        no_murmur = d.SOPRO.eq('Ausente'); murmur = d.SOPRO.notna() & ~no_murmur
        age = pd.to_numeric(d.IDADE, errors='coerce')
        result[pool] = {
            'family': best[pool], 'n_fn': int(fn.sum()), 'n_fp': int(fp.sum()),
            'fn_without_murmur_percent': float(100 * no_murmur[fn].mean()),
            'fp_with_murmur_percent': float(100 * murmur[fp].mean()),
            'anormal_without_murmur': int((d.y.eq(1) & no_murmur).sum()),
            'anormal_without_murmur_percent_of_anormal': float(100 * no_murmur[d.y.eq(1)].mean()),
            'normal_with_murmur': int((d.y.eq(0) & murmur).sum()),
            'median_age_fn': float(age[fn].median()), 'median_age_tp': float(age[tp].median()),
        }
    return result


def figures(metrics, ranking, best):
    figdir = OUT / 'figures'; figdir.mkdir(exist_ok=True)
    for old in figdir.glob('*'):
        old.unlink()
    m = metrics.query('pool==@PRIMARY and family==@best').iloc[0]
    matrix = np.array([[m.tn, m.fp], [m.fn, m.tp]], dtype=int)
    fig, ax = plt.subplots(figsize=(3.4, 2.8), layout='constrained')
    ax.imshow(matrix, cmap='Blues'); ax.set_xticks([0, 1], ['Normal', 'Anormal']); ax.set_yticks([0, 1], ['Normal', 'Anormal'])
    ax.set(xlabel='Predito', ylabel='Rótulo registrado', title=f'{PRIMARY}: {best}')
    for (i, j), v in np.ndenumerate(matrix):
        ax.text(j, i, str(v), ha='center', va='center', color='white' if v > matrix.max() * .55 else 'black')
    fig.savefig(figdir / 'confusao_clinico.png', dpi=180); plt.close(fig)
    q = ranking.query('pool==@PRIMARY and family==@best').sort_values('mean')
    fig, ax = plt.subplots(figsize=(5.1, 3.2), layout='constrained')
    ax.barh(q.variable, q['mean'], xerr=q['std'], color='#376e92'); ax.axvline(0, color='black', lw=.7)
    ax.set(xlabel='Queda média de BA após permutação', title=f'Importância por permutação - {PRIMARY}/{best}'); ax.tick_params(labelsize=8)
    fig.savefig(figdir / 'importancia_clinico.png', dpi=180); plt.close(fig)


def export(source=SOURCE_DEFAULT):
    a = ROOT / 'artifacts/a2_rubric_audit'; OUT.mkdir(parents=True, exist_ok=True)
    check = json.loads((a / 'verification.json').read_text(encoding='utf-8')); assert check['complete']
    names = ['family_nested_metrics.csv', 'historical_test_metrics.csv', 'outer_fold_metrics.csv', 'variable_probes.csv',
             'category_target_associations.csv', 'collection_process_controls.csv', 'permuted_label_control.json',
             'verification.json', 'final_choices.json', 'outer_selections.json', 'preprocessing_audit.json',
             'outer_permutation_importance.csv', 'protocol_before_results.json']
    names += [p.name for p in a.glob('inner_scores_*.csv')] + [p.name for p in a.glob('final_selection_scores_*.csv')] + [p.name for p in a.glob('final_parameters_*.json')]
    for name in names:
        p = a / name
        if p.suffix == '.csv' and 'ID' in pd.read_csv(p, nrows=0).columns:
            raise ValueError('Row-level export rejected')
        copy_lf(p, OUT / name)
    raw, semantic, data, y, groups, sourcehash = load_development(ROOT, source)
    metrics = pd.read_csv(a / 'family_nested_metrics.csv'); test = pd.read_csv(a / 'historical_test_metrics.csv')
    imp = pd.read_csv(a / 'outer_permutation_importance.csv'); assoc = pd.read_csv(a / 'category_target_associations.csv')
    ranking = imp.groupby(['pool', 'family', 'variable']).BA_drop.agg(['mean', 'std']).reset_index()
    write_text(OUT / 'permutation_summary.csv', ranking.to_csv(index=False, lineterminator='\n'))
    best = {pool: metrics.query('pool==@pool and family!="dummy"').sort_values('balanced_accuracy').iloc[-1].family for pool in SCENARIOS_AUDIT}
    figures(metrics, ranking, best[PRIMARY])
    final = {pool: {kind: json.loads((a / f'final_parameters_{pool}_{kind}.json').read_text(encoding='utf-8'))['candidate'] for kind in ['dummy', 'tree', 'logistic', 'forest']} for pool in SCENARIOS_AUDIT}
    probes = pd.read_csv(a / 'variable_probes.csv')
    summary_errors = error_analysis(a, data, best)
    summary = {
        'error_analysis': summary_errors,
        'run_date': '2026-11-12', 'dataset': 'UCMF, disponibilizado na disciplina INF0414; origem descrita como Real Hospital Português, Recife',
        'source_sha256': sourcehash, 'protocol_sha256': check['protocol_sha256'],
        'n_original': 12873, 'n_original_variables': 21, 'n_development': int(len(y)), 'n_historical_test': 2342,
        'development_class_counts': {str(k): int(v) for k, v in pd.Series(y).value_counts().items()},
        'n_groups_development': int(groups.nunique()),
        'pools': SCENARIOS_AUDIT, 'primary_pool': PRIMARY, 'sensitivity_pools': SENSITIVITY, 'excluded_fields': EXCLUDED_REASONS,
        'best_family_by_pool': best, 'final_choices': final,
        'metrics': metrics.to_dict('records'), 'historical_test_metrics': test.to_dict('records'),
        'variable_probes': probes.astype(object).where(probes.notna(), None).to_dict('records'),
        'collection_controls': pd.read_csv(a / 'collection_process_controls.csv').to_dict('records'),
        'null_control': json.loads((a / 'permuted_label_control.json').read_text(encoding='utf-8')),
        'importance': ranking.to_dict('records'),
        'eda': eda_summary(data, y, assoc), 'a1_reconciliation': a1_reconciliation(source),
        'n_configs': check['candidate_count'], 'outer_folds': 5, 'inner_folds': 3,
        'seeds': {'random_state': 42, 'outer_cv': 743, 'inner_cv': '811+k', 'final_selection_cv': 43, 'permutation': '1700+k', 'null_control': [911, 914]},
        'elapsed_seconds': check['elapsed_seconds'],
    }
    text = json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    write_text(OUT / 'reviewed_results.json', text); write_text(PAPER_RESULTS, text)
    files = {str(p.relative_to(OUT)).replace('\\', '/'): sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ('manifesto.json', 'manifesto_publicado.json')}
    write_text(OUT / 'manifesto.json', json.dumps({'source_sha256': sourcehash, 'files_sha256': files, 'self_excluded': True}, ensure_ascii=False, indent=2) + '\n')
    print(OUT.relative_to(ROOT)); return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE_DEFAULT)
    export(parser.parse_args().source)
