"""Monta .build/content.json para build_deck.mjs a partir de reviewed_results.json.

Todo número dos slides e do roteiro vem daqui; nada é digitado no gerador do deck.
"""
from pathlib import Path
import json, hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / 'resultados/a2/auditoria_2026_11_07/reviewed_results.json'
OUT = HERE / '.build'; OUT.mkdir(exist_ok=True)
R = json.loads(SRC.read_text(encoding='utf-8'))


def pt(x, d=1): return f'{x:.{d}f}'.replace('.', ',')
def pct(x, d=1): return pt(100 * x, d) + '%'
def integer(x): return f'{int(round(x)):,}'.replace(',', '.')


FAM = {'dummy': 'Classe majoritária', 'tree': 'Árvore', 'logistic': 'Logística', 'forest': 'Floresta'}
by = {(r['pool'], r['family']): r for r in R['metrics']}
test = {(r['pool'], r['family']): r for r in R['historical_test_metrics']}
best = R['best_family_by_pool']; P = 'CLINICO'
bc, bf, bs = by[P, best[P]], by['FISIO8', best['FISIO8']], by['STRICT4', best['STRICT4']]
eda, rec, err = R['eda'], R['a1_reconciliation'], R['error_analysis'][P]
imp = {(r['pool'], r['family'], r['variable']): r['mean'] for r in R['importance']}
probe = {p['variable']: p['cv_balanced_accuracy'] for p in R['variable_probes']}
cat = {(c['variable'], c['value']): c for c in eda['categories']}
n_dev, n_test = R['n_development'], R['n_historical_test']
spread = max(by[P, f]['balanced_accuracy'] for f in ['tree', 'logistic', 'forest']) - min(by[P, f]['balanced_accuracy'] for f in ['tree', 'logistic', 'forest'])

# Valores formatados usados nos slides (o deck só posiciona strings)
V = {
    'n_source': integer(rec['n_source']), 'n_labelled': integer(rec['n_labelled_a2']), 'n_unlabelled': integer(rec['n_unlabelled']),
    'n_dev': integer(n_dev), 'n_test': integer(n_test), 'n_removed': integer(rec['n_labelled_a2'] - n_dev - n_test),
    'n_normal': integer(eda['class_counts']['Normal']), 'n_anormal': integer(eda['class_counts']['Anormal']), 'pct_anormal': pt(eda['anormal_percent']) + '%',
    'a1_dup': integer(rec['n_a1_duplicates']), 'a1_dup_unl': integer(rec['n_a1_duplicates_unlabelled']), 'a1_dup_lab': integer(rec['n_a1_duplicates_labelled']),
    'a1_final': integer(rec['n_a1_final']), 'dup_same_group': integer(rec['labelled_duplicates_same_group_as_copy']),
    'dup_other_group': integer(rec['labelled_duplicates_other_group']), 'dup_other_part': integer(rec['labelled_duplicates_other_partition_than_copy']),
    'n_groups': integer(R['n_groups_development']), 'n_configs': integer(R['n_configs']), 'acc_dummy': pct(by[P, 'dummy']['accuracy']),
    'age_med_a': pt(eda['box_IDADE']['Anormal']['med']), 'age_med_n': pt(eda['box_IDADE']['Normal']['med']),
    'under1_a': pt(eda['percent_under_1_year']['Anormal']) + '%', 'under1_n': pt(eda['percent_under_1_year']['Normal']) + '%',
    'fc_med_a': pt(eda['box_FC']['Anormal']['med'], 0), 'fc_med_n': pt(eda['box_FC']['Normal']['med'], 0),
    'sop_sis': pct(cat['SOPRO', 'Sistolico']['anormal_rate']), 'sop_aus': pct(cat['SOPRO', 'Ausente']['anormal_rate']),
    'sus_n': integer(eda['convenio_SUS']['n']), 'sus_pct': pt(eda['convenio_SUS']['anormal_percent']) + '%', 'hda2_miss': pt(eda['missing_percent_HDA2']) + '%',
    'probe_sopro': pct(probe['SOPRO']), 'probe_m1': pct(probe['MOTIVO1']), 'probe_m2': pct(probe['MOTIVO2']),
    'ba_clin': pct(bc['balanced_accuracy']), 'sens_clin': pct(bc['recall']), 'spec_clin': pct(bc['specificity']), 'auc_clin_flo': pct(by[P, 'forest']['roc_auc']),
    'ba_fisio': pct(bf['balanced_accuracy']), 'ba_strict': pct(bs['balanced_accuracy']), 'spread_clin': pt(100 * spread, 2),
    'gain_cf': pt(100 * (bc['balanced_accuracy'] - bf['balanced_accuracy'])), 'gain_fs': pt(100 * (bf['balanced_accuracy'] - bs['balanced_accuracy'])),
    'fam_clin': FAM[best[P]].lower(), 'fam_fisio': FAM[best['FISIO8']].lower(), 'fam_strict': FAM[best['STRICT4']].lower(),
    'imp_sopro': pt(100 * imp[P, best[P], 'SOPRO']), 'imp_b2': pt(100 * imp[P, best[P], 'B2']),
    'imp_fc_fisio': pt(100 * imp['FISIO8', best['FISIO8'], 'FC']), 'imp_peso_fisio': pt(100 * imp['FISIO8', best['FISIO8'], 'Peso']),
    'imp_peso_strict': pt(100 * imp['STRICT4', best['STRICT4'], 'Peso']),
    'tn': integer(bc['tn']), 'fp': integer(bc['fp']), 'fn': integer(bc['fn']), 'tp': integer(bc['tp']),
    'fn_pct_anormal': pct(bc['fn'] / (bc['fn'] + bc['tp'])), 'fn_sem_sopro': pt(err['fn_without_murmur_percent']) + '%',
    'fp_com_sopro': pt(err['fp_with_murmur_percent']) + '%', 'anorm_sem_sopro': integer(err['anormal_without_murmur']),
    'norm_com_sopro': integer(err['normal_with_murmur']),
    't_clin': pct(test[P, best[P]]['balanced_accuracy']), 't_fisio': pct(test['FISIO8', best['FISIO8']]['balanced_accuracy']),
    't_strict': pct(test['STRICT4', best['STRICT4']]['balanced_accuracy']),
}

# Tabelas e gráficos
results_main = [['Modelo', 'BA', 'Sensib.', 'Especif.', 'ROC-AUC']] + [
    [FAM[f], pct(by[P, f]['balanced_accuracy']), pct(by[P, f]['recall']), pct(by[P, f]['specificity']), pct(by[P, f]['roc_auc'])]
    for f in ['dummy', 'tree', 'logistic', 'forest']]
results_all = [['Cenário', 'Modelo', 'BA', 'Sens.', 'Esp.', 'Prec.', 'F1', 'AUC', 'AP']]
for pool in ['CLINICO', 'FISIO8', 'STRICT4']:
    for f in ['dummy', 'tree', 'logistic', 'forest']:
        r = by[pool, f]
        results_all.append([pool, FAM[f]] + [pct(r[m]) for m in ['balanced_accuracy', 'recall', 'specificity', 'precision', 'f1', 'roc_auc', 'average_precision']])
test_table = [['Cenário', 'Árvore', 'Logística', 'Floresta']] + [[pool] + [pct(test[pool, f]['balanced_accuracy']) for f in ['tree', 'logistic', 'forest']] for pool in ['CLINICO', 'FISIO8', 'STRICT4']]
scenario_chart = {'categories': ['Árvore', 'Logística', 'Floresta'],
                  'series': [{'name': pool, 'values': [round(100 * by[pool, f]['balanced_accuracy'], 2) for f in ['tree', 'logistic', 'forest']]} for pool in ['STRICT4', 'FISIO8', 'CLINICO']]}
LBL = {'Ausente': 'Sem sopro', 'Sistolico': 'Sopro sistólico', 'Continuo': 'Sopro contínuo', 'Normal': 'B2 normal', 'Hiperfonetica': 'B2 hiperfonética', 'Desdob fixo': 'B2 desdobr. fixo', 'Unica': 'B2 única'}
finding_chart = {'categories': [], 'values': []}
for var, val in [('SOPRO', 'Ausente'), ('SOPRO', 'Sistolico'), ('SOPRO', 'Continuo'), ('B2', 'Normal'), ('B2', 'Hiperfonetica'), ('B2', 'Desdob fixo'), ('B2', 'Unica')]:
    finding_chart['categories'].append(LBL[val]); finding_chart['values'].append(round(100 * cat[var, val]['anormal_rate'], 1))
NAMES = {'PA SISTOLICA': 'PAS', 'PA DIASTOLICA': 'PAD', 'HDA 1': 'HDA1', 'IDADE': 'Idade'}
importance_chart = []
for pool in ['CLINICO', 'FISIO8']:
    rows = sorted([(v, m) for (p, f, v), m in imp.items() if p == pool and f == best[pool]], key=lambda x: -x[1])[:4]
    importance_chart.append({'title': f'{pool} ({FAM[best[pool]].lower()})', 'categories': [NAMES.get(v, v) for v, _ in rows], 'values': [round(100 * m, 2) for _, m in rows]})
confusion = [['Rótulo \\ previsão', 'Normal', 'Anormal'], ['Normal', V['tn'], V['fp']], ['Anormal', V['fn'], V['tp']]]

A = 'Antônio Henrique Queiroz Villar Lopes'; J = 'João Vitor Fernandes Ferreira'; M = 'Mateus Nery Bailão'; P_ = 'Pedro Augusto Ferreira Matos'
notes = []
def note(title, seconds, author, text, qa):
    notes.append({'number': len(notes) + 1, 'title': title, 'seconds': seconds, 'author': author, 'text': text, 'qa': qa})

note('Classificação de registros de cardiologia pediátrica', 30, A,
     'Somos o grupo 3. Vamos mostrar como classificamos registros de cardiologia pediátrica como normais ou anormais, quais atributos deixamos o modelo usar e o que os resultados dizem sobre a origem da informação.',
     [('Qual é a contribuição principal?', 'Uma política de atributos baseada na disponibilidade no momento da previsão e a comparação de quatro modelos em três cenários com o mesmo protocolo.')])
note('Tarefa', 50, A,
     f'A base UCMF vem de atendimentos de cardiologia pediátrica do Real Hospital Português, em Recife. O alvo indica se o registro foi rotulado como normal ou anormal. A classe positiva é Anormal. A pergunta é: com o que se coleta no atendimento, antes do laudo, dá para antecipar esse rótulo? Pensamos no uso como apoio à triagem.',
     [('O modelo diagnostica doença?', 'Não. Ele prevê o rótulo registrado na base, cujo critério de referência não está documentado.')])
note('Dados e partições', 60, A,
     f'São {V["n_source"]} registros e 21 atributos. {V["n_unlabelled"]} não têm rótulo. Dos {V["n_labelled"]} rotulados, {V["n_dev"]} formam o desenvolvimento, onde fazemos toda a escolha de modelos, e {V["n_test"]} formam o teste histórico, separado numa fase anterior. No desenvolvimento, {V["pct_anormal"]} são anormais: um desequilíbrio moderado, por isso usamos acurácia balanceada.',
     [('Por que não descartar o teste histórico?', 'Usamos como avaliação secundária, uma única vez, deixando claro que ele já tinha sido examinado antes.')])
note('O exame físico separa as classes', 60, J,
     f'Este gráfico mostra o percentual de anormais em cada achado do exame. Com sopro sistólico, {V["sop_sis"]} são anormais; sem sopro, {V["sop_aus"]}. B2 alterada também concentra anormais. Esses achados são exatamente o que o cardiologista observa ao examinar a criança.',
     [('Isso não é vazamento?', f'Não pelo nosso critério: o sopro é auscultado no atendimento, antes do laudo. SOPRO sozinho tem BA de {V["probe_sopro"]}, o que mostra poder preditivo, não informação do futuro.')])
note('Idade e frequência cardíaca', 50, J,
     f'As crianças anormais são mais novas: mediana de {V["age_med_a"]} anos contra {V["age_med_n"]}, e {V["under1_a"]} delas têm menos de um ano, contra {V["under1_n"]} dos normais. Isso é compatível com cardiopatias congênitas, percebidas cedo. A FC mediana é {V["fc_med_a"]} contra {V["fc_med_n"]} bpm, mas a FC cai com a idade, então parte dessa diferença é efeito da idade.',
     [('A FC é um marcador de doença?', 'Aqui ela se confunde com a idade; não afirmamos efeito causal.')])
note('Critério de vazamento', 80, J,
     f'Definimos vazamento como usar informação indisponível no momento da previsão. Saem ID e datas brutas; Convênio, que descreve a origem do paciente: no SUS, {V["sus_pct"]} dos {V["sus_n"]} registros são anormais, o que reflete quem encaminhou; MOTIVO1 e MOTIVO2, que trazem o diagnóstico escrito, como cardiopatia congênita, risco já apontado na A1; e HDA2, com {V["hda2_miss"]} de ausentes. Ficam medidas, sinais vitais, exame físico, sintomas e PPA, que é calculada de pressão, idade, sexo e altura.',
     [('Por que a versão anterior excluía SOPRO, B2 e PULSOS?', 'Ela tratava como vazamento tudo o que estivesse próximo do rótulo. Revimos o critério: o que importa é a disponibilidade antes do laudo, e o exame físico está disponível.'),
      ('E se o sopro tiver sido registrado depois do laudo?', 'A base não tem horários. Por isso mantemos os cenários sem exame físico como sensibilidade e declaramos essa suposição como limitação.'),
      ('Convênio está disponível no atendimento. Por que sai?', 'Porque descreve o caminho de encaminhamento e não a criança. Um modelo apoiado nele aprenderia quem encaminha, e não o que se observa.')])
note('Três cenários', 50, M,
     'O cenário principal, CLINICO, tem 13 atributos. FISIO8 retira exame físico, sintomas e PPA e fica com medidas, sinais vitais e sexo. STRICT4 mantém só peso, altura, idade e sexo. Os três usam os mesmos registros e as mesmas partições, o que permite ver de onde vem a informação.',
     [('FISIO8 e STRICT4 viraram o quê?', 'Análises de sensibilidade: mostram quanto do desempenho depende de cada bloco de atributos.')])
note('Da A1 para a A2', 60, M,
     f'A A1 removeu {V["a1_dup"]} duplicados: {V["a1_dup_unl"]} sem rótulo e {V["a1_dup_lab"]} rotulados. Na A2 mantemos os rotulados e colocamos registros iguais no mesmo grupo, que nunca é dividido entre treino e validação; {V["dup_same_group"]} ficam no grupo da cópia. Também mudamos três decisões: idade contínua em vez de faixas, one-hot no sexo e a imputação por faixa etária como opção testada, não como regra.',
     [('Por que não remover os duplicados?', 'O agrupamento evita que cópias caiam em treino e validação ao mesmo tempo, sem perder registros.')])
note('Pré-processamento e validação', 70, M,
     f'Tudo que aprende com os dados, como medianas, escalas e vocabulário das categorias, é ajustado só no treino de cada partição. A validação é aninhada: cinco folds externos para estimar o desempenho e, dentro de cada um, três folds internos para escolher os hiperparâmetros. É estratificada pela classe e agrupada. Sementes fixas: 42 nos modelos, 743 nos folds externos e 811 mais k nos internos.',
     [('Por que aninhada?', 'Para que o mesmo dado não sirva para escolher hiperparâmetros e medir desempenho.')])
note('Modelos e métricas', 50, M,
     f'O baseline simples é a classe majoritária, que sempre diz Normal. Comparamos com três modelos: árvore de decisão, regressão logística e floresta aleatória, com {V["n_configs"]} configurações por cenário. A métrica principal é a acurácia balanceada, média de sensibilidade e especificidade.',
     [('Por que não acurácia comum?', f'A classe majoritária já teria {V["acc_dummy"]} de acurácia sem reconhecer nenhum anormal.')])
note('Resultado principal', 70, P_,
     f'No CLINICO, árvore, logística e floresta ficam a {V["spread_clin"]} ponto uma da outra: é um empate. Pelo critério fixado antes, a árvore tem a maior BA, {V["ba_clin"]}, com sensibilidade de {V["sens_clin"]} e especificidade de {V["spec_clin"]}. A floresta ordena melhor as probabilidades, com ROC-AUC de {V["auc_clin_flo"]}.',
     [('Se empatam, qual vocês usariam?', 'A árvore, por ser a mais simples de explicar; a floresta, se o limiar for ajustado, porque ordena melhor.')])
note('De onde vem a informação', 60, P_,
     f'Tirando o exame físico, a melhor BA cai {V["gain_cf"]} pontos, para {V["ba_fisio"]}. Tirando também os sinais vitais, cai mais {V["gain_fs"]} pontos, para {V["ba_strict"]}. Quase toda a informação está na ausculta. No teste histórico a ordem se mantém: {V["t_clin"]}, {V["t_fisio"]} e {V["t_strict"]}.',
     [('O teste histórico confirma o resultado?', 'Mostra estabilidade dentro da mesma coorte. Como ele já tinha sido examinado, não substitui validação externa.')])
note('Importância dos atributos', 50, P_,
     f'Embaralhar o SOPRO derruba a BA em {V["imp_sopro"]} pontos; B2, em {V["imp_b2"]}. Os outros não mudam nada. Sem o exame, o modelo passa a usar FC ({V["imp_fc_fisio"]}) e peso ({V["imp_peso_fisio"]}), que acompanham a idade.',
     [('Importância é causa?', 'Não. É a perda de desempenho do modelo quando o atributo é embaralhado.')])
note('Análise de erros', 70, P_,
     f'São {V["fn"]} falsos negativos, {V["fn_pct_anormal"]} dos anormais, e todos ({V["fn_sem_sopro"]}) são crianças sem sopro. Entre os {V["fp"]} falsos positivos, {V["fp_com_sopro"]} têm sopro, o que é compatível com sopros inocentes. Numa triagem, o falso negativo é o erro caro: pode atrasar um diagnóstico. Por isso o próximo passo é ajustar o limiar para aumentar a sensibilidade.',
     [('Como reduzir os falsos negativos?', 'Baixando o limiar e estudando à parte as crianças anormais sem sopro, com idade, FC e sintomas.')])
note('Conclusão e limitações', 60, A,
     f'O modelo reproduz o raciocínio do exame cardiológico: acerta muito quando há sopro e falha nas crianças sem sopro. As limitações são reais: o rótulo não tem padrão de referência documentado, supomos que o exame foi registrado antes do laudo, a avaliação é interna a uma coorte e os grupos não identificam pacientes. Código, sementes e resultados estão no repositório.',
     [('Qual dado mais mudaria o estudo?', 'O critério de rotulagem e os horários de registro, que confirmariam a disponibilidade de cada atributo.')])
assert len(notes) == 15
total = sum(n['seconds'] for n in notes)
assert total <= 900, total

content = {'V': V, 'notes': notes, 'authors': [A, J, M, P_], 'results_main': results_main, 'results_all': results_all,
           'test_table': test_table, 'scenario_chart': scenario_chart, 'finding_chart': finding_chart,
           'importance_chart': importance_chart, 'confusion': confusion, 'pools': R['pools'], 'excluded': R['excluded_fields'],
           'total_seconds': total, 'source': str(SRC.relative_to(ROOT)).replace('\\', '/'),
           'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest()}
(OUT / 'content.json').write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

# Roteiro
lines = ['# Roteiro e preparação para arguição', '',
         f'15 slides numerados, {total // 60} min {total % 60:02d} s de fala. Três slides de apoio ficam ocultos. Qualquer integrante deve conseguir explicar todo o roteiro.', '']
for a in content['authors']:
    s = sum(n['seconds'] for n in notes if n['author'] == a); lines.append(f'- {a}: {s // 60} min {s % 60:02d} s.')
for n in notes:
    lines += ['', f'## {n["number"]}. {n["title"]}', '', f'Responsável: {n["author"]}. Tempo: {n["seconds"] // 60}:{n["seconds"] % 60:02d}.', '', n['text'], '']
    for q, a in n['qa']:
        lines += [f'**Pergunta provável:** {q}', '', f'**Resposta:** {a}', '']
lines += ['## Preparação conjunta', '',
          'Todos devem saber explicar: o critério de vazamento e por que SOPRO fica e Convênio sai; a diferença entre folds internos e externos; por que as três famílias empatam no CLINICO; o que significa um falso negativo numa triagem; e as limitações. Os números deste roteiro vêm de `' + content['source'] + '`.', '']
(HERE / 'output').mkdir(exist_ok=True)
(HERE / 'output/Roteiro_e_Arguicao.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
print(json.dumps({'slides': len(notes), 'seconds': total, 'best': best}, ensure_ascii=False))
