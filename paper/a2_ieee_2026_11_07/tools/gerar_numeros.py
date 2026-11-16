"""Generate IEEE tables and numbers directly from the reviewed aggregate JSON."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'results/reviewed_results.json'
OUT = ROOT / 'generated'
POOLS = {'FISIO8': 'Fisio', 'STRICT4': 'Strict', 'CLINICO': 'Clin'}
NAMES = {'dummy': 'Maioria', 'tree': 'Árvore', 'logistic': 'Logística', 'forest': 'Floresta'}
FAMILY_MACROS = {'dummy': 'Dummy', 'tree': 'Tree', 'logistic': 'Logistic', 'forest': 'Forest'}


def decimal(value, places=2):
    return f'{value:.{places}f}'.replace('.', ',')


def percent(value):
    return decimal(100 * value)


def integer(value):
    return f'{value:,}'.replace(',', '.')


def interval(values):
    return f'[{percent(values[0])} a {percent(values[1])}]'


def main():
    source = json.loads(RESULT.read_text(encoding='utf-8'))
    metrics = {(r['pool'], r['family']): r for r in source['metrics']}
    macros = {}
    rows = []
    for pool, name in POOLS.items():
        best = source['best_family_by_pool'][pool]
        macros[f'{name}BestFamily'] = NAMES[best].lower()
        macros[f'{name}BestBA'] = percent(metrics[pool, best]['balanced_accuracy'])
        for family, label in NAMES.items():
            row = metrics[pool, family]
            prefix = name + FAMILY_MACROS[family]
            for short, key in [('BA', 'balanced_accuracy'), ('Sens', 'recall'), ('Spec', 'specificity'),
                               ('AUC', 'roc_auc'), ('AP', 'average_precision')]:
                macros[prefix + short] = percent(row[key])
            for m in ('tn', 'fp', 'fn', 'tp'):
                macros[prefix + m.upper()] = integer(row[m])
            p = source['bootstrap']['models'][f'{pool}/{family}']
            macros[prefix + 'CI'] = interval(p['ci95'])
            ba = percent(row['balanced_accuracy'])
            if family == best:
                ba = rf'\textbf{{{ba}}}'
            scenario = '\\' + name.lower() + '{}' if family == 'dummy' else ''
            values = [ba, *[percent(row[key]) for key in ('recall', 'specificity', 'precision', 'f1', 'average_precision')]]
            rows.append(' & '.join([scenario, label, *values]) + r' \\')
        rows.append(r'\midrule')
    rows[-1] = r'\bottomrule'

    for row in source['bootstrap']['differences']:
        a_pool, a_family = row['a'].split('/')
        b_pool, b_family = row['b'].split('/')
        if a_pool == b_pool and (a_family, b_family) == ('forest', 'logistic'):
            prefix = POOLS[a_pool] + 'Diff'
            macros[prefix + 'BA'] = percent(row['diff'])
            macros[prefix + 'CI'] = interval(row['ci95'])

    for row in source['importance']:
        key = row['pool'], row['family'], row['variable']
        if key in (('FISIO8', 'forest', 'FC'), ('FISIO8', 'forest', 'Peso'),
                   ('CLINICO', 'tree', 'SOPRO'), ('CLINICO', 'tree', 'B2')):
            name = {'FC': 'FC', 'Peso': 'Peso', 'SOPRO': 'Sopro', 'B2': 'Btwo'}[row['variable']]
            macros[POOLS[row['pool']] + 'Imp' + name] = percent(row['mean'])

    for variable, name in [('SOPRO', 'Sopro'), ('B2', 'Btwo'), ('MOTIVO1', 'MotivoUm'), ('MOTIVO2', 'MotivoDois')]:
        probe = next(r for r in source['variable_probes'] if r['variable'] == variable)
        macros['Probe' + name] = percent(probe['cv_balanced_accuracy'])
    for pool, name in POOLS.items():
        mask = next(r for r in source['collection_controls'] if r['pool'] == pool)
        macros[name + 'MaskBA'] = percent(mask['balanced_accuracy'])
        null = next(r for r in source['null_control'] if r['pool'] == pool)
        macros[name + 'NullBA'] = percent(null['metric']['balanced_accuracy'])
        error = source['errors'][pool]
        macros[name + 'NoMurmurFN'] = integer(error['fn_explicitly_without_murmur'])
        macros[name + 'MedianAgeFN'] = decimal(error['median_age_fn'])
        macros[name + 'MedianAgeTP'] = decimal(error['median_age_tp'])
    macros['AnormalSemSopro'] = integer(source['eda']['explicitly_without_murmur_anormal'])
    for k, n in [('0', 'Normal'), ('1', 'Anormal')]:
        macros['MedianAge' + n] = decimal(source['eda']['median_age'][k])
        macros['MedianFC' + n] = decimal(source['eda']['median_fc'][k], 0)
    learning = source['tree_rules_development']['FISIO8']
    broad = max(learning, key=lambda r: r['n'])
    macros['FisioRuleN'] = integer(broad['n'])
    macros['FisioRuleAnormal'] = integer(broad['n_anormal'])
    macros['FisioRulePredicted'] = broad['predicted']
    text = ', '.join(broad['conditions']).replace('≤', r'\(\leq\)').replace('>', r'\(>\)').replace('≠', r'\(\ne\)')
    macros['FisioRuleConditions'] = re.sub(r'\d+\.\d+', lambda m: decimal(float(m[0])), text)
    macros['ClinVsFisio'] = decimal(100 * (metrics['CLINICO', 'tree']['balanced_accuracy'] - metrics['FISIO8', 'tree']['balanced_accuracy']))
    OUT.mkdir(exist_ok=True)
    (OUT / 'tab_resultados.tex').write_text('\n'.join(rows) + '\n', encoding='utf-8', newline='\n')
    (OUT / 'numeros.tex').write_text(''.join(rf'\newcommand{{\{k}}}{{{v}}}' + '\n' for k, v in macros.items()), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
