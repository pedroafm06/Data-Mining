from hashlib import sha256
import numpy as np
import pandas as pd
import pytest
from kdd_revision.evaluation_stats import paired_cluster_bootstrap, tree_rules
from kdd_revision.mining import fit_model
from kdd_revision.rubric_bootstrap import membership_digest


def _data(n=400, seed=0):
    rng = np.random.default_rng(seed); y = rng.integers(0, 2, n)
    return y, rng.integers(0, n // 2, n).astype(str)


def test_bootstrap_point_estimates_and_intervals_are_ordered():
    y, groups = _data()
    perfect = y.astype(float); constant = np.zeros(len(y))
    out = paired_cluster_bootstrap(y, {'perfect': perfect, 'constant': constant}, groups, [('perfect', 'constant')], n_boot=300)
    assert out['models']['perfect']['ba'] == 1.0 and out['models']['constant']['ba'] == .5
    lo, hi = out['models']['constant']['ci95']; assert lo == hi == .5
    d = out['differences'][0]; assert d['diff'] == .5 and not d['ci_contains_zero']


def test_identical_models_have_a_degenerate_zero_difference():
    y, groups = _data(seed=1); p = np.random.default_rng(2).random(len(y))
    d = paired_cluster_bootstrap(y, {'a': p, 'b': p.copy()}, groups, [('a', 'b')], n_boot=200)['differences'][0]
    assert d['diff'] == 0 and d['ci95'] == [0.0, 0.0] and d['ci_contains_zero']


def test_bootstrap_is_reproducible_and_rejects_misaligned_predictions():
    y, groups = _data(seed=3); p = np.random.default_rng(4).random(len(y))
    a = paired_cluster_bootstrap(y, {'m': p}, groups, n_boot=100, seed=7)
    b = paired_cluster_bootstrap(y, {'m': p}, groups, n_boot=100, seed=7)
    assert a == b
    with pytest.raises(ValueError):
        paired_cluster_bootstrap(y, {'m': p[:-1]}, groups)


def test_tree_rules_describe_one_hot_splits_with_development_support():
    rng = np.random.default_rng(5); n = 300
    sopro = rng.choice(['Ausente', 'Sistolico'], n); y = (sopro == 'Sistolico').astype(int)
    x = pd.DataFrame({'ID': np.arange(n).astype(str), 'IDADE': rng.uniform(0, 18, n), 'SOPRO': sopro})
    candidate = {'kind': 'tree', 'params': {'criterion': 'gini', 'max_depth': 1, 'min_samples_leaf': 20, 'class_weight': None},
                 'imputation': 'global', 'representation': 'units', 'name': 't'}
    fitted = fit_model(x, y, candidate, ['IDADE', 'SOPRO'])
    rules = tree_rules(fitted, x, y)
    assert len(rules) == 2 and sum(r['n'] for r in rules) == n
    by_pred = {r['predicted']: r for r in rules}
    assert by_pred['Anormal']['anormal_rate'] == 1.0 and by_pred['Normal']['anormal_rate'] == 0.0
    assert all(c.startswith('SOPRO') for r in rules for c in r['conditions'])


def test_membership_digest_ignores_platform_line_endings():
    mapping = pd.DataFrame({'ID': ['1', '2'], 'group': ['g1', 'g2'], 'partition': ['development', 'test']})
    expected = sha256(b'ID,group,partition\n1,g1,development\n2,g2,test\n').hexdigest()
    assert membership_digest(mapping) == expected
