"""Uncertainty of out-of-fold comparisons and readable rules of a fitted tree.

Both functions read predictions or models that already exist; neither refits,
selects or changes any experiment. The bootstrap resamples candidate groups (the
same unit that the folds keep together) and is paired: every model is scored on
the same resampled rows, so differences keep their correlation. Intervals are
conditional on the fitted models and do not include refitting variability.
"""
import numpy as np
import pandas as pd


def _ba(counts):
    """Balanced accuracy from [..., (tp, fn, tn, fp)] counts."""
    tp, fn, tn, fp = (counts[..., i] for i in range(4))
    with np.errstate(divide='ignore', invalid='ignore'):
        return .5 * (tp / (tp + fn) + tn / (tn + fp))


def paired_cluster_bootstrap(y, predictions, groups, comparisons=(), n_boot=2000, seed=2026, threshold=.5):
    """Percentile 95% intervals for BA of each model and for paired BA differences.

    predictions: {name: probability array aligned with y}; comparisons: [(a, b)] gives BA(a)-BA(b).
    """
    y = np.asarray(y)
    names = list(predictions)
    groups = pd.Series(groups)
    if y.ndim != 1 or set(np.unique(y)) != {0, 1}:
        raise ValueError('Both binary classes are required')
    if n_boot < 1 or len(groups) != len(y) or groups.isna().any():
        raise ValueError('Resample count and group membership must be valid')
    probabilities = {name: np.asarray(values, dtype=float) for name, values in predictions.items()}
    if not names or any(p.shape != y.shape or not np.isfinite(p).all() for p in probabilities.values()):
        raise ValueError('Predictions must be aligned with y and finite')
    codes, _ = pd.factorize(groups)
    n_groups = int(codes.max()) + 1
    # Per-group confusion counts for every model: shape (groups, models, 4).
    per_group = np.zeros((n_groups, len(names), 4))
    for j, name in enumerate(names):
        pred = (probabilities[name] >= threshold).astype(int)
        for k, cell in enumerate([(y == 1) & (pred == 1), (y == 1) & (pred == 0), (y == 0) & (pred == 0), (y == 0) & (pred == 1)]):
            per_group[:, j, k] = np.bincount(codes, weights=cell.astype(float), minlength=n_groups)
    rng = np.random.default_rng(seed); draws = np.empty((n_boot, len(names)))
    for b in range(n_boot):
        weights = np.bincount(rng.integers(0, n_groups, n_groups), minlength=n_groups)
        draws[b] = _ba(np.tensordot(weights, per_group, axes=1))
    draws = draws[np.isfinite(draws).all(axis=1)]
    if not len(draws):
        raise ValueError('No bootstrap resample contains both classes')
    point = _ba(per_group.sum(axis=0))
    out = {'n_boot': n_boot, 'valid_resamples': len(draws), 'seed': seed, 'unit': 'candidate group', 'n_groups': n_groups, 'paired': True,
           'conditional_on_fitted_models': True, 'models': {}, 'differences': []}
    for j, name in enumerate(names):
        lo, hi = np.percentile(draws[:, j], [2.5, 97.5])
        out['models'][name] = {'ba': float(point[j]), 'ci95': [float(lo), float(hi)]}
    index = {n: j for j, n in enumerate(names)}
    for a, b in comparisons:
        d = draws[:, index[a]] - draws[:, index[b]]; lo, hi = np.percentile(d, [2.5, 97.5])
        out['differences'].append({'a': a, 'b': b, 'diff': float(point[index[a]] - point[index[b]]), 'ci95': [float(lo), float(hi)],
                                   'ci_contains_zero': bool(lo <= 0 <= hi)})
    return out


def _condition(entry, threshold, left):
    """Human-readable test for one split of the applied matrix."""
    source = entry['source']
    if entry['kind'] == 'one_hot_binary':
        category = {'__AUSENTE__': 'ausente', '__DESCONHECIDO__': 'desconhecido'}.get(entry['category'], entry['category'])
        return f'{source} ≠ {category}' if left else f'{source} = {category}'
    if entry['kind'] == 'binary_missing_or_masked':
        return f'{source} observado' if left else f'{source} ausente'
    return f'{source} ≤ {threshold:.7g}' if left else f'{source} > {threshold:.7g}'


def tree_rules(fitted, x, y):
    """Root-to-leaf rules of a FittedModel whose classifier is a decision tree, with development support."""
    clf = fitted.classifier
    if not hasattr(clf, 'tree_') or fitted.projection is not None or fitted.representation != 'units':
        raise ValueError('Rules require an unprojected decision tree in original units')
    tree = clf.tree_
    entries = {d['name']: d for d in fitted.preprocessor.column_dictionary_}
    z = fitted.matrix(x); leaf_of_row = clf.apply(z); proba = fitted.proba(x); y = np.asarray(y, dtype=int)
    rules = []

    def walk(node, path):
        if tree.children_left[node] == tree.children_right[node]:
            rows = leaf_of_row == node
            rules.append({'conditions': path, 'n': int(rows.sum()), 'n_anormal': int(y[rows].sum()),
                          'anormal_rate': float(y[rows].mean()) if rows.any() else None,
                          'predicted': 'Anormal' if rows.any() and proba[rows][0] >= .5 else 'Normal'})
            return
        entry = entries[fitted.columns[tree.feature[node]]]; t = float(tree.threshold[node])
        walk(tree.children_left[node], path + [_condition(entry, t, True)])
        walk(tree.children_right[node], path + [_condition(entry, t, False)])

    walk(0, [])
    return rules
