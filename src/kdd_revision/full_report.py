"""Integrated A2 report and decision register, consuming executed current results."""
from pathlib import Path
from hashlib import sha256
from html import escape
import json,re,shutil
import pandas as pd
from .schema import PROJECT_ROOT
from .mining import estimator


def load(p):return json.loads(Path(p).read_text())
def number(x,d=3):return '-' if pd.isna(x) else f'{float(x):.{d}f}'.replace('.',',')
def integer(x):return f'{int(x):,}'.replace(',','.')
def table_md(headers,rows):
    def cell(x):return str(x).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(cell,headers))+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(cell,r))+' |' for r in rows])


def export(root):
    a=root/'artifacts/a2_mining';out=root/'resultados/a2/kdd_completo';out.mkdir(parents=True,exist_ok=True)
    names=['candidatos_cv.csv','nested_results.json','selected_before_test.json','test_metrics.json','controls.json','intervals.json',
        'subgrupos.csv','sensibilidades.csv','importancia_permutacao.csv','unlabeled_application.json','verification.json','events.json','fold_preprocessing_audit.json']
    for s in ['A','B','B_contexto']:
        names.extend([f'folds_{s}.csv',f'final_parameters_{s}.json',f'regras_arvore_{s}.csv',f'tree_dictionary_{s}.json',f'arvore_{s}.txt'])
    for name in names:
        p=a/name
        if p.suffix=='.csv' and 'ID' in pd.read_csv(p,nrows=0).columns:raise ValueError('Row-level export rejected')
        shutil.copy2(p,out/name)
    for p in (a/'figures').glob('*.png'):shutil.copy2(p,out/p.name)
    for name in ['summary.json','comparacao_cobertura.csv','verification.json']:
        shutil.copy2(root/'artifacts/a2_application'/name,out/('application_'+name))
    return out


def decision_register(root,verification,selected,cv,sensitivity):
    rows=[]
    def add(stage,key,value,why,alternative,evidence,limit=''):
        rows.append({'etapa':stage,'decisao':key,'valor_ou_regra':value,'por_que':why,'alternativas':alternative,'evidencia':evidence,'limite':limit})
    fixed=[
    ('Objetivo','Tarefa','Classificação supervisionada do rótulo registrado','O alvo disponível é binário; descobrir padrões associados ao registro, sem fabricar um desfecho clínico independente.','Regressão, agrupamento e associação não respondem diretamente à pergunta principal.','Rótulos Normal/Anormal na fonte.','Não equivale a diagnóstico nem causalidade.'),
    ('Seleção','Unidade e população','Preservar 12.873 linhas; supervisionado só com rótulo conhecido','A informação não estabelece identidade de paciente. Não eliminar coincidências como se fossem duplicações comprovadas.','Excluir repetidos ou imputar y foi rejeitado.','Base semântica e elegibilidade.','Paciente versus atendimento ainda precisa de confirmação.'),
    ('Limpeza','Esquema e ID','21 nomes/ordem exatos; ID não vazio e único','Um identificador ambíguo impede rastrear qualquer alteração.','Fabricar ID ou juntar automaticamente foi rejeitado.','Validação antes da preparação.','ID único não comprova pessoa única.'),
    ('Limpeza','Texto','Unicode NFC, espaços condensados; chave sem acento e casefold','Unificar apenas variações gráficas, preservando significado e texto original na auditoria.','Fusão por prefixo de motivo foi rejeitada.','Mapas explícitos e logs de alterações.','Categorias novas clínicas são mantidas e sinalizadas.'),
    ('Limpeza','Sentinelas','Vazio; PPA não calculado/#VALUE!; DN ???; SEXO indeterminado','Ausência é diferente de normalidade ou de categoria clínica Ausente.','Moda Normal/Ausente foi rejeitada.','Sentinelas específicas por coluna.','Não identifica o mecanismo das ausências.'),
    ('Limpeza','Número','Vírgula decimal aceita; não finito, negativo e medida FC/PA zero invalidados; Peso/Altura/IMC zero ausentes','Os significados diferem por variável; idade zero é válida.','Cortar dígitos ou mover vírgula para fazer o valor parecer plausível foi rejeitado.','numeric_value e log por célula.','Extremo positivo não é automaticamente erro.'),
    ('Limpeza','Intervalo FC','Faixa válida de dois valores com 2-3 dígitos -> ponto médio; invertida -> inválida','É a aproximação simples explicitada, não uma leitura exata.','Inverter limites silenciosamente foi rejeitado.','Flag de aproximação e registro bruto.','A variabilidade dentro da faixa não é recuperável.'),
    ('Limpeza','Data','Data completa válida, nome de mês ou serial Excel com 5 dígitos; dia/mês brasileiro; século curto gera 19xx/20xx','Evitar janela histórica como confirmação do século. Formato precisa corresponder à célula inteira.','Correção por palpite e descarte de texto residual foram rejeitados.','parse_date e candidatos locais.','Data absoluta ambígua continua indisponível.'),
    ('Criação','Idade relativa','0 <= idade calendário <20; candidatos com duração divergente em até 1 dia; média e intervalo preservados','Permite identificar diferença etária sem fixar o século. Tolerância absorve um dia bissexto.','Dias/352 e imputação pelo corpo foram rejeitados.','11.208 resolvidas; hipótese pediátrica declarada.','Não prova a cronologia absoluta.'),
    ('Criação','Aniversário bissexto','29/02 -> 28/02 em ano não bissexto','Definir uma convenção explícita para fração do ano e fronteira de 20 anos.','01/03 é alternativa possível; não misturar convenções.','Teste de fronteira calendário.','Diferenças locais de um dia não são informação clínica precisa.'),
    ('Criação','Fallback de idade','Idade literal na DN; depois valor original válido <20; depois ausência','Não preencher uma data ou idade não identificável com certeza falsa.','Inferir pela antropometria foi rejeitado.','18 literais e 1.647 indisponíveis; origem guardada.','Fallback numérico, quando houver, é não verificado.'),
    ('Limpeza','Alertas etários','Diferença >0,1 ano; conflito >1 ano','São alertas de revisão, não critérios de exclusão automática.','Excluir idade por baixa correlação foi rejeitado.','Flags e proveniência.','Pontos de corte operacionais.'),
    ('Limpeza','Antropometria','Guarda conjunta IMC observado fora de 5-100 mascara Peso/Altura/IMC na política; sem atribuir culpado','Valores individualmente possíveis podem formar um conjunto muito suspeito. A base semântica mantém tudo.','Corrigir um pai arbitrariamente e apagar idade foram rejeitados.','Máscaras atuais e sensibilidade suspeitos preservados.','5-100 não é faixa clínica de normalidade.'),
    ('Limpeza','Exceções e máscaras','Peso<1; altura fora40-200, exceto30-39 se idade<0,25 ou desconhecida; FC>500; PAS envelope50-200; PAD positiva mantida; PAS<=PAD mascara par','Preservar extremos potencialmente reais e explicitar hipóteses restantes. Peso>150 e FC>220 não são excluídos por esses antigos tetos.','Política histórica e todos suspeitos preservados estão disponíveis.','Peso16; Altura18; IMC14; PAS3; PAD1; FC8 mascarados.','São hipóteses de confiabilidade, sem validação clínica individual.'),
    ('Criação','IMC','Peso/(Altura/100)^2 somente com pais observados operacionalmente utilizáveis; histórico como fallback','Evitar transformar pais imputados em uma medição de IMC.','Reconstrução após imputar pais foi testada e teve erro maior.','Ensaios de coerência e origem por linha.','IMC é derivado e redundante; visão sem IMC testada.'),
    ('Transformação','Faixas e suporte','[0;0,25;0,5;1;2;5;10;15;20); mínimo30 por grupo; fallback global','Capturar crescimento sem grupos muito pequenos. Usar idade disponível antes da imputação.','Mediana global e idade/sexo foram comparadas.','Diagnóstico com 20% mascarado, 5 repetições, seeds194-198.','Faixas não foram otimizadas clinicamente.'),
    ('Transformação','Escolha preliminar por reconstrução','Ganho MAE>=10% e melhora em pelo menos4/5 repetições','Evitar complexidade por ganho mínimo; IMC limítrofe fica explicitado.','Global sempre exportada; idade/sexo sem ganho suficiente.','Diagnósticos de preparação.','Para modelos, global/idade são escolhidas dentro da CV, sem herdar a decisão global.'),
    ('Transformação','One-hot','Vocabulário do treino + __AUSENTE__ + __DESCONHECIDO__; exatamente1 por variável','Nominal não deve ganhar ordem artificial; ausência e categoria inédita são diferentes.','Ordinal de PPA e binarização dos achados foram rejeitados.','Testes e metadados por fold.','Dimensão pode variar entre folds; cada modelo usa seu próprio vocabulário.'),
    ('Transformação','Escala e log','Z=(x-media_treino)/DP_treino com ddof0; escala1 se desvio0; log1p só Peso em alternativa logística','Escalas afetam regularização; árvores usam unidades por interpretabilidade. Bits não são escalados.','Log indiscriminado, min-max e escala da base inteira foram rejeitados.','Unidades/standard/log_weight_standard efetivamente comparados.','Z-score não torna normal nem robusta uma medida.'),
    ('Validação','Grupos','União transitiva de grupos candidatos antigos + igualdade informativa atual (>=8 campos)','Evitar equivalentes atravessando treino/validação mesmo após novas regras.','Partição aleatória por linha pode compartilhar candidatos.','Grupos sem interseção; quarentena antes do ajuste.','Não resolve identidade de paciente desconhecida.'),
    ('Validação','Separação','Teste histórico preservado; 5 folds internos seed 43; nested3x3 seeds 52 e 53+fold','Selecionar dentro de treino e avaliar também o procedimento de escolha. Mesma população/partição nos cenários.','Usar matriz pronta em CV foi rejeitado.','Auditoria de hashes de IDs e parâmetros por fold.','Qualidade já foi explorada globalmente; nested não desfaz isso.'),
    ('Seleção de modelos','Critério e desempate','Maior média de acurácia balanceada; empate1e-12 na ordem publicada','Sem custos confirmados FP/FN, dar peso igual ao recall de ambas classes; ordem resolve empate reprodutivelmente.','Acurácia isolada e escolha pelo teste foram rejeitadas.','81 configurações por cenário, publicadas antes de métricas.','Não é uma utilidade clínica estabelecida nem ótimo global.'),
    ('Modelagem','Árvores','Gini/entropia; profundidade3/6 ou poda alfa0,001/0,005; folhas20/50; pesos None/balanced','Controlar complexidade, suporte e sobreajuste, sem tratar cada registro como regra.','Árvore irrestrita sem suporte mínimo foi rejeitada.','40 combinações com as duas imputações.','Cortes do modelo são empíricos, não normas clínicas.'),
    ('Modelagem','Logística','C=0,01/0,1/1/10; pesos None/balanced; standard/log-Peso; global/idade; max_iter5000','Testar quatro ordens de regularização e uma fronteira linear; log reduz influência da cauda do peso.','Família adicional para comparação com árvores.','32 combinações; falha de convergência é erro, não resultado aceito.','Complemento técnico; não atribuir explicação integral do método às aulas.'),
    ('Modelagem','Floresta','150 árvores; profundidade 8/None; folha10; pesos None/balanced; imputação global/idade; seed42; n_jobs2','Testar agregação de árvores e reduzir variância com orçamento fixo. Folhas limitam a árvore profunda.','Mais árvores sem orçamento e tuning pelo teste foram rejeitados.','8 combinações; parâmetros efetivos registrados.','É comparação complementar, sem garantia de melhor generalização.'),
    ('Sensibilidade','Redução e balanceamento','Sem indicadores/IMC/HDA2/IMC+HDA2/PPA; PCA95 na melhor logística; sobre/subamostragem simples seed45','Investigar redundância, ausências, informação rara e balanceamento; medir perdas e ganhos.','SMOTE em one-hot pode produzir categorias e combinações clínicas artificiais; não foi forçado.','Somente desenvolvimento; mesmas partições.','Pós-seleção exploratória; não reutiliza teste para escolher a variante.'),
    ('Avaliação','Limiar e métricas','p>=0,5; TN/FP/FN/TP; precisão, recall, especificidade, F1, BA, ROC-AUC, AP e Brier','Exibir os tipos de erro; AP resume PR por definição própria, sem chamar de área trapezoidal.','Tuning de limiar por teste foi rejeitado.','Métricas e curvas atuais.','Scores não são probabilidades clínicas calibradas.'),
    ('Avaliação','Intervalos e subgrupos','500 reamostragens de componentes seed44; Wilson em recall de subgrupos n>=20','Mostrar incerteza e suporte; agrupar dependências candidatas em vez de tratar tudo como independente.','DP entre folds não é IC.','Intervalos e suportes publicados.','Bootstrap condicionado ao modelo; Wilson por linha não corrige grupos.'),
    ('Interpretação','Importância e regras','Permutação5 repetições seed46 em validação de desenvolvimento; regras da melhor árvore com contagens reais','Investigar dependência do modelo sem confundir peso de classe com número observado no nó.','Importância como causa ou regra clínica foi rejeitada.','Queda de BA e suportes por folha.','Pós-seleção; atributos correlacionados podem dividir importância.'),
    ('Uso','Aplicação e abstenção','Exigir ao menos1 preditor, padrão de disponibilidade com >=30 exemplos no desenvolvimento e nenhuma categoria inédita; manter score separado de y','Demonstra a aplicação do conhecimento sem produzir rótulos confirmados ou treinar com autorrotulagem.','A regra inicial de apenas1 campo foi testada e rejeitada; suportes 1/10/30 foram comparados sem rótulos novos.','Contagens agregadas e arquivo local por registro.','30 é suporte operacional, sem ótimo clínico; cobertura aceita também não garante previsão confiável.'),
    ('Reprodução','Versões e proteção','Entrada verificada por SHA; A1 preservada por hash; parâmetros, seeds e saídas registrados','Permitir conferir que números decorrem do código e dos mesmos dados.','Alterar A1 entregue ou publicar dados clínicos por linha foi rejeitado.','Testes, manifestos e reprodução do modelo salvo.','Validação técnica não é avaliação humana ou clínica.'),
    ]
    for args in fixed:add(*args)
    for r in load(root/'artifacts/a2_preprocessing/report/decisoes_21_variaveis.json'):
        for field in ['tipo','limpeza','transformacao','alternativas_e_julgamento','incerteza']:
            add('Variável '+r['variavel'],field,r[field],r['limpeza'] if field=='tipo' else r['alternativas_e_julgamento'],r['alternativas_e_julgamento'],f"{r['ausentes_pre_imputacao']} ausentes/mascarados antes de imputar; {r['valores_distintos']} distintos",r['incerteza'])
    for c in load(root/'config/a2_kdd_protocol.json')['candidates']:
        add('Combinação testada',c['name'],json.dumps(c,ensure_ascii=False,sort_keys=True),'Comparar configuração explícita com as demais sob as mesmas partições.','Demais configurações publicadas.','candidatos_cv.csv e folds por cenário.','Vitória na busca depende do conjunto de candidatos e do critério.')
    frame=pd.DataFrame(rows);frame.to_csv(root/'docs/a2/Registro_Microdecisoes.csv',index=False)
    detailed=(root/'docs/a2/Decisoes_Preprocessamento_A2.md').read_text()
    intro='''# A2 - decisões do processo completo do KDD

Este registro cobre entendimento, seleção, limpeza, transformação, mineração, avaliação, interpretação e aplicação. A A1 entregue permanece como histórico avaliado. A unidade é a linha recebida; não foi comprovado se cada ID representa uma pessoa ou um atendimento independente.

Uma decisão aqui pode ser uma regra determinística, um critério de comparação ou um parâmetro aprendido. Regras e alternativas são explicadas abaixo. Os valores aprendidos não ficam escondidos: medianas por faixa, vocabulários, médias/desvios e hashes do ajuste de cada fold estão em `resultados/a2/kdd_completo/fold_preprocessing_audit.json`; os parâmetros finais de cada cenário estão nos arquivos `final_parameters_*.json`. As alterações por célula permanecem locais em `artifacts/a2_preprocessing/alteracoes.csv` e na proveniência, para evitar distribuir registros clínicos.

## Decisões transversais, com alternativas e limites

'''
    for stage,key,value,why,alt,evidence,limit in fixed:
        intro+=f'### {stage}: {key}\n\nA regra aplicada foi **{value}**. {why}\n\nAlternativa examinada ou rejeitada: {alt} Evidência: {evidence} Limite: {limit}\n\n'
    intro+='## Julgamento das 21 variáveis\n\n'+detailed.split('## Julgamento variável por variável',1)[-1]
    intro+='\n\n## Conclusão crítica da busca atual\n\nAs 81 configurações e as sensibilidades foram executadas, sem perseguir a pontuação do teste. As vencedoras foram registradas antes de avaliá-lo. As tabelas de CV, nested CV, teste e sensibilidades permitem contestar as escolhas. Nenhuma combinação é declarada melhor em qualquer população ou finalidade. O relatório integrado discute quais ganhos têm suporte e quais continuam exploratórios.\n'
    (root/'docs/a2/Decisoes_KDD_Completo.md').write_text(re.sub(r'\n{3,}','\n\n',intro))
    defaults={c['name']:estimator(c).get_params(deep=False) for c in load(root/'config/a2_kdd_protocol.json')['candidates']}
    (root/'config/a2_effective_estimator_parameters.json').write_text(json.dumps(defaults,ensure_ascii=False,indent=2,default=str)+'\n')
    return len(rows)


def decoded(rule,dictionary):
    d={v['name']:v for v in dictionary};parts=[]
    for part in rule.split(' AND '):
        m=re.fullmatch(r'(.*) (<=|>) (.*)',part)
        if not m:parts.append(part);continue
        name,op,value=m.groups();info=d.get(name,{})
        if info.get('kind')=='one_hot_binary':
            category=info.get('category')
            if category=='__AUSENTE__':parts.append(f"{info['source']} {'não registrado' if op=='>' else 'com registro'}")
            elif category=='__DESCONHECIDO__':parts.append(f"{info['source']} {'com' if op=='>' else 'sem'} categoria inédita")
            else:parts.append(f"{info['source']} registrado como {category}" if op=='>' else f"{info['source']} diferente de {category} (inclui falta/inédito)")
        elif info.get('kind')=='binary_missing_or_masked':parts.append(f"{info['source']} {'foi imputado' if op=='>' else 'não foi imputado'}")
        else:parts.append(f'{name} {op} {value}')
    return '; '.join(parts)


def generate(root=PROJECT_ROOT):
    root=Path(root);a=root/'artifacts/a2_mining';check=load(a/'verification.json')
    if not check['complete'] or not check['all_selections_frozen_before_test']:raise ValueError('Incomplete or invalid experiment')
    from .inspection import inspect
    additional=inspect(root)
    out=export(root)
    shutil.copy2(root/'artifacts/a2_kdd/additional_diagnostics.json',out/'additional_diagnostics.json')
    docs=root/'docs/a2';prep=load(root/'artifacts/a2_preprocessing/summary.json');sel=load(a/'selected_before_test.json')['selected']
    cv=pd.read_csv(a/'candidatos_cv.csv');nested=load(a/'nested_results.json');test=load(a/'test_metrics.json');ci=load(a/'intervals.json');apps=load(root/'artifacts/a2_application/summary.json');control=load(a/'controls.json');sens=pd.read_csv(a/'sensibilidades.csv');imp=pd.read_csv(a/'importancia_permutacao.csv')
    n_decisions=decision_register(root,check,sel,cv,sens)
    sections=[]
    def section(title,*paragraphs,table=None,image=None):sections.append({'title':title,'paragraphs':list(paragraphs),'table':table,'image':image})
    section('1. Objetivo e conhecimento procurado',
        'O estudo procura padrões que distinguem Normal de Anormal no rótulo registrado da base UCMF. A tarefa é classificação supervisionada: há exemplos com uma resposta binária disponível. Não se presume um diagnóstico independente nem se anuncia capacidade de triagem antes do exame. Agrupamento, regressão e associação seriam outras tarefas; não substituem essa pergunta.',
        'A A2 reúne o processo inteiro do KDD. Reutilizamos a A1 como ponto de partida, criticamos e melhoramos sua preparação, executamos mineração, avaliação, interpretação e uma aplicação acadêmica. A A1 avaliada continua sendo a versão já entregue; os documentos históricos permanecem idênticos. A descrição formal da A2 ainda poderá acrescentar exigências de apresentação, sem tornar pendente o processo técnico executado aqui.')
    section('2. Seleção, população e entendimento dos dados',
        f'A entrada possui {integer(prep["n_source"])} linhas e 21 variáveis. Conservamos todas as linhas, inclusive equivalências candidatas e registros sem alvo. Normal=0 e Anormal=1; são 6.744 Normais, 4.960 Anormais e 1.169 sem rótulo utilizável. A classificação usa apenas os 11.704 conhecidos antes da quarentena. Não imputamos y. ID único não estabelece paciente único.',
        f'A preparação mantém {integer(check["n_development"])} registros de desenvolvimento, {integer(check["n_test"])} no teste histórico e uma quarentena anterior ao ajuste. A união transitiva dos grupos exigiu {check["extra_group_quarantine"]} quarentenas adicionais. Modelos dos cenários usam os mesmos registros e partições. As equivalências são candidatas; a dependência real entre atendimentos pode continuar maior que a identificada.',
        table=(['Papel','Variáveis'],[['Medidas quantitativas','Peso, Altura, IMC, IDADE, PAS, PAD, FC'],['Nominais de exame/contexto','PULSOS, PPA, B2, SOPRO, HDA1, HDA2, SEXO, MOTIVO1, MOTIVO2'],['Rastreio e fonte de derivação','ID, Atendimento, DN'],['Administrativa fora de X','Convenio'],['Alvo separado de X','NORMAL X ANORMAL']]))
    prof=pd.read_csv(root/'artifacts/a2_preprocessing/report/perfil_21_variaveis.csv').set_index('variable')
    section('3. Exploração e crítica da qualidade',
        'Exploramos tipos, escalas, cobertura, tendência central, dispersão, forma das distribuições, correlação e associações bivariadas. Essas estatísticas usam medidas disponíveis antes da imputação. Faltante, zero-sentinela, inconsistência e outlier têm significados distintos; reduzir desvio ou aumentar correlação não prova que uma limpeza ficou correta.',
        'A idade recebida acompanha dias/352 a até 0,01 ano em 11.191 casos comparáveis, com 11.120 coincidências exatas após arredondamento. Isso sustenta a crítica aritmética, sem revelar a fórmula original. A revisão resolve 11.208 idades relativas por pares de datas compatíveis sob o recorte pediátrico, sem escolher século absoluto. Dezoito idades literais são aproveitadas e 1.647 permanecem indisponíveis.',
        table=(['Medida','Disponíveis','Ausentes %','Mediana','DP'],[[c,integer(prof.loc[c,'n_valid']),number(prof.loc[c,'missing_pct'],1),number(prof.loc[c,'median'],1),number(prof.loc[c,'sd'],1)] for c in ['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC']]))
    section('4. Limpeza e criação de atributos: decisão por evidência',
        'Padronizamos Unicode, espaços e grafias documentadas. Sentinelas são específicas da coluna: SOPRO Ausente é achado registrado e não campo vazio. Prefixos de MOTIVO2 não substituem a descrição completa. Alvos duvidosos não são inferidos. Datas exigem interpretação completa da célula; texto residual e ano ambíguo não são descartados para fabricar certeza.',
        'A idade relativa usa aniversários de calendário e pares candidatos com 0 <= idade <20, tolerando até um dia de divergência na duração e guardando intervalo e hipótese. IMC = Peso/(Altura/100)^2 usa apenas pais observados operacionalmente utilizáveis; quando necessário, o valor histórico permanece com origem. Não recalculamos IMC depois de imputar seus pais.',
        'Envelopes históricos são alertas. Preservamos pesos acima do antigo teto e frequências cardíacas positivas potencialmente reais. A guarda conjunta de razão antropométrica fora de 5-100 mascara o trio na política principal, sem escolher o campo errado ou apagar idade. Essa guarda e os demais cortes restantes são hipóteses de curadoria, não faixas clínicas. Foram mascarados 16 valores de Peso, 18 de Altura, 14 de IMC, 3 de PAS, 1 de PAD e 8 de FC. Uma alternativa com suspeitos preservados foi efetivamente testada.',
        'O registro completo descreve as 21 variáveis, os formatos aceitos, sentinelas, condições, exceções, alternativas e incertezas. Valores brutos, candidatos e intervenções por célula ficam na proveniência local. Isso permite revisar uma decisão sem apagar a fonte.')
    section('5. Transformações e prevenção de vazamento',
        'Comparamos medianas global, por idade e por idade/sexo por mascaramento artificial de 20% de medidas observadas, em cinco repetições apenas no desenvolvimento. Faixas fixas [0;0,25;0,5;1;2;5;10;15;20) precisam de 30 observados e têm fallback global. O diagnóstico favoreceu idade para Peso, Altura, FC e IMC; o IMC foi limítrofe. Isso não identifica o mecanismo das ausências reais.',
        'Na mineração, a imputação global e a condicional por idade voltam a competir dentro de cada treino de fold. Assim, a escolha exploratória anterior não é tratada como um parâmetro já validado. Vocabulários, medianas, médias e desvios também são ajustados em cada treino. A matriz pronta de desenvolvimento não foi usada para selecionar modelos.',
        'Categorias nominais usam one-hot, com estados separados para ausência e categoria inédita. Sete indicadores distinguem imputação de medida disponível. Z-score usa média e DP do treino (ddof=0); log1p é alternativa somente para Peso antes de padronizar. Bits continuam 0/1. Árvores usam unidades originais; logística compara a versão padronizada e a de log-Peso. A representação completa exportada possui 93 colunas, mas o vocabulário de cada fold pertence ao seu próprio treino.')
    section('6. Protocolo experimental e alternativas executadas',
        'Cenário A inclui medidas, contexto e achados. B restringe-se às sete medidas e SEXO. B_contexto retira PULSOS, B2 e SOPRO de A, mantendo contexto cuja temporalidade não foi confirmada. São perguntas de disponibilidade diferentes: A não se anuncia como triagem antes do exame.',
        'Comparamos 81 configurações em cada cenário por cinco folds estratificados e agrupados no desenvolvimento (seed 43). O critério é a média da acurácia balanceada; empates até 1e-12 seguem a ordem publicada. Sem custos confirmados de FP e FN, esse critério considera o recall das duas classes, enquanto precisão, recall e demais métricas continuam visíveis. Não é uma função de utilidade clínica.',
        'A avaliação aninhada usa três folds externos e três internos, só no desenvolvimento (seeds 52 e 53+fold). A busca inteira se repete em cada treino externo. O resultado estima o procedimento de escolha condicionado às decisões de preparação já exploradas; não desfaz a exploração global anterior. Depois, todas as configurações finais são congeladas antes das métricas do teste histórico.',
        table=(['Família','Configurações','Alternativas principais'],[['Controle majoritário','1','Referência sem informação de X'],['Árvore de decisão','40','Gini/entropia, profundidade3/6, folha20/50, poda alfa0,001/0,005, pesos e imputação'],['Regressão logística','32','C0,01/0,1/1/10, pesos, duas imputações e duas representações'],['Floresta aleatória','8','150 árvores, profundidade 8/None, folha10, pesos e imputação']]))
    rows=[]
    for s,m in test.items():
        q=cv[(cv.scenario==s)&(cv.candidate==sel[s]['name'])].iloc[0]
        rows.append([s,{'tree':'Árvore','forest':'Floresta','logistic':'Logística','dummy':'Majoritário'}[sel[s]['kind']],number(q.mean_balanced_accuracy),number(nested[s]['pooled_oof']['balanced_accuracy']),number(m['balanced_accuracy']),number(m['recall']),number(m['precision']),number(m['average_precision']),number(m['brier'])])
    section('7. Resultados atuais e significado da avaliação',
        'Na busca principal, A escolheu árvore rasa com mediana global; B escolheu floresta de profundidade 8 com mediana global; B_contexto escolheu floresta com folha mínima 10 e mediana etária. O ganho de reconstrução da imputação etária não assegurou maior classificação. A teve muitas configurações empatadas em BA; a ordem publicada preferiu a árvore simples. A avaliação externa também escolheu logística em alguns folds de A e B_contexto, mostrando que o vencedor não é estável em todo subconjunto.',
        'CV é a média dos folds usada na seleção. Nested é a acurácia balanceada das predições externas reunidas de modelos escolhidos dentro de cada treino externo. Teste é a avaliação secundária do conjunto histórico previamente explorado. Essas colunas não medem exatamente a mesma coisa; diferenças não demonstram melhora causal da limpeza nem desempenho em população nova.',
        table=(['Cenário','Modelo','CV BA','Nested BA','Teste BA','Recall','Precisão','AP','Brier'],rows))
    section('7.1 Desempenho de ajuste e complexidade',
        'O desempenho no próprio desenvolvimento usado para ajuste é descritivo e tende a ser otimista. A diferença para CV ajuda a investigar sobreajuste; não substitui validação. A busca aninhada escolheu configurações distintas entre folds, portanto a tabela não estabelece um vencedor universal. Os componentes candidatos incluem '+str(additional['groups_with_mixed_labels'])+' grupos de desenvolvimento com rótulos mistos; não corrigimos automaticamente esses rótulos.',
        table=(['Cenário','BA no próprio treino','BA média CV','Atributos codificados'],[[s,number(additional['model_training'][s]['training_metrics']['balanced_accuracy']),number(cv[(cv.scenario==s)&(cv.candidate==sel[s]['name'])].iloc[0].mean_balanced_accuracy),additional['model_training'][s]['n_encoded_features']] for s in test]))
    section('7.2 Tipos de erro, incerteza e controles',
        'Usamos limiar fixo p>=0,5. Recall = TP/(TP+FN), precisão = TP/(TP+FP), especificidade = TN/(TN+FP) e BA = (recall+especificidade)/2. F1 combina precisão/recall. ROC-AUC avalia ordenação de scores e AP resume precisão-recall pela sua definição; AP não é área trapezoidal. Brier descreve erro quadrático do score probabilístico, sem provar calibração clínica.',
        f'O controle majoritário tem BA={number(control["majority"]["balanced_accuracy"])}. A regra fixa de SOPRO cobre {number(100*control["sopro_rule"]["coverage"],1)}% do teste e tem BA={number(control["sopro_rule"]["metrics"]["balanced_accuracy"])} nessa cobertura. Os modelos também foram calculados no mesmo subconjunto para comparação justa. O score binário dessa regra não é probabilidade calibrada.',
        'Os intervalos percentis usam 500 reamostragens dos componentes candidatos, condicionadas ao modelo já ajustado. Não abrangem toda a incerteza da preparação e seleção. Subgrupos publicam suporte e erros; Wilson de recall é descritivo por linha e não corrige dependência de grupo. A instabilidade de um subgrupo pequeno não deve virar uma conclusão geral.',
        table=(['Cenário','TN','FP','FN','TP','Especificidade','F1','IC95 BA'],[[s,m['tn'],m['fp'],m['fn'],m['tp'],number(m['specificity']),number(m['f1']),number(ci[s]['intervals']['balanced_accuracy'][0])+' a '+number(ci[s]['intervals']['balanced_accuracy'][1])] for s,m in test.items()]),image=a/'figures/confusoes.png')
    section('7.3 Curvas e limites de generalização',
        'O limiar controla o compromisso entre erros. As curvas mostram possibilidades, mas nenhum ponto foi escolhido pelo teste. Formação do rótulo, identidade das pessoas, temporalidade dos achados e mudança de população ainda não estão confirmadas. Não executamos validação temporal com séculos ambíguos: uma janela histórica presumida não cria cronologia confiável.',image=a/'figures/curvas.png')
    pivot=sens.pivot(index='variant',columns='scenario',values='mean_cv_balanced_accuracy')
    labels={'PCA95_melhor_logistica':'PCA95 (logística)','principal':'Principal','sem_HDA2':'Sem HDA2','sem_IMC':'Sem IMC','sem_IMC_HDA2':'Sem IMC e HDA2','sem_PPA':'Sem PPA','sem_indicadores':'Sem indicadores','sobreamostragem':'Sobreamostragem','subamostragem':'Subamostragem','suspeitos_preservados':'Suspeitos preservados'}
    section('8. Contestação das escolhas e testes de sensibilidade',
        'Além da busca principal, contestamos o papel dos outliers, indicadores, atributos redundantes/esparsos e balanceamento. Sobreamostragem repete exemplos minoritários; subamostragem reduz majoritários; ambas ficam somente no treino e substituem o peso de classe, sem alterar validação ou teste. PCA95 é testada na melhor logística, com projeção aprendida em cada treino; deve ser comparada à mesma logística sem PCA, não atribuída à vencedora de outra família.',
        'Em B, retirar IMC elevou BA média de 0,6341 para 0,6366: ganho de 0,0025, pequeno frente ao DP de 0,0092 dos folds da configuração principal. Isso é pista, não melhora confirmada. PCA reduziu BA em relação à mesma logística em todos os cenários: A: 0,9192 para 0,9174; B: 0,6186 para 0,6155; B_contexto: 0,7087 para 0,7071. Em A, várias intervenções não alteraram as decisões de classe: os achados de exame dominam esse resultado.',
        'A tabela é exploratória e usa o desenvolvimento após a seleção principal. Um ganho pontual pede nova confirmação; não autoriza trocar o vencedor depois de observar o teste. Piorar também é resultado: informação rara, estimativa e redundância podem afetar cada cenário de modo diferente. Não forçamos toda técnica para acumular conceitos.',
        table=(['Variante','A: CV BA','B: CV BA','B_contexto: CV BA'],[[labels.get(name,name),*[number(pivot.loc[name,s]) if s in pivot else '-' for s in ['A','B','B_contexto']]] for name in pivot.index]))
    for s in test:
        top=imp[imp.scenario.eq(s)].sort_values('mean_drop_balanced_accuracy',ascending=False).head(3)
        words='; '.join(f'{r.variable}: queda {number(r.mean_drop_balanced_accuracy)}' for _,r in top.iterrows())
        section(f'9. Interpretação - cenário {s}',
            f'Na importância por permutação exploratória, os maiores efeitos foram {words}. O cálculo usa um fold de validação do desenvolvimento, não o treino desse modelo. A escolha de configuração já usou desenvolvimento, portanto a análise é pós-seleção. Permutar uma coluna pode quebrar correlações: queda de desempenho não é efeito causal de uma variável.',
            'Para interpretar padrões legíveis, ajustamos também a melhor árvore por CV. As regras abaixo pertencem a essa árvore, que pode ser distinta do modelo vencedor. Suportes e frações são contagens reais no desenvolvimento, não probabilidades de nós ponderados por classe e não estimativas externas. As condições usam a representação após imputação. Um indicador nominal igual0 pode incluir campo vazio ou categoria inédita; não significa ausência clínica do achado.',
            table=(['Regra da árvore','n desenvolvimento','Anormais observados'],[[decoded(r.rule,load(a/f'tree_dictionary_{s}.json')),integer(r.n_development),number(100*r.observed_anormal_fraction,1)+'%'] for _,r in pd.read_csv(a/f'regras_arvore_{s}.csv').sort_values('n_development',ascending=False).head(3).iterrows()]))
    section('10. Conhecimento obtido e aplicação responsável',
        'A leitura integrada deve confrontar o desempenho com a informação disponível. A diferença entre A e B quantifica o valor preditivo de achados/contexto para o rótulo registrado, sem provar circularidade nem independência diagnóstica. Se um modelo rico apenas reproduz um exame que ajudou a formar o alvo, sua pontuação não demonstra capacidade de antecipar o diagnóstico. As medidas sozinhas precisam ser julgadas por seus próprios erros e incertezas.',
        'A primeira aplicação, exigindo apenas um campo disponível, revelou um problema: A atribuía score a 430 registros sem alvo, embora muitos padrões de ausência tivessem suporte inexistente ou muito baixo no desenvolvimento. Rejeitamos essa regra como suficiente. A aplicação revisada exige algum preditor, categorias observadas e um padrão de disponibilidade visto em pelo menos 30 exemplos do treino. Comparamos coberturas para suportes 1/10/30 sem usar rótulos novos nem retunar os modelos. O corte de 30 é operacional, não ótimo comprovado.',
        'A aplicação revisada mantém score para 19 registros em A, 380 em B e 294 em B_contexto; os demais recebem status de abstenção. A pode discriminar melhor registros completos e ao mesmo tempo cobrir muito menos registros sem alvo. Essa é uma descoberta sobre os limites de uso, não um motivo para forçar resultados. Cobertura aceita não prova confiabilidade individual. Predições não viram y ou pseudo-rótulos.',
        table=(['Cenário','Sem alvo','Com score','Abstenções','Score>=0,5'],[[s,r['n_unlabeled'],r['n_scored'],r['n_abstained'],r['n_p_ge_half']] for s,r in apps.items()]))
    section('10.1 Cobertura em dados rotulados e limites da política',
        'A política de suporte foi definida sem selecionar por acurácia do teste. Como diagnóstico secundário, publicamos sua cobertura no teste histórico e o desempenho condicionado aos casos aceitos. Esses números não substituem o teste completo e não podem ser comparados sem considerar a mudança de denominador. A diferença entre a cobertura no teste rotulado e nos não rotulados evidencia uma mudança no padrão de informação disponível.',
        table=(['Cenário','Aceitos / teste','Cobertura %','BA nos aceitos'],[[s,str(r['historical_test_coverage_diagnostic']['n_accepted'])+' / '+str(r['historical_test_coverage_diagnostic']['n_total']),number(100*r['historical_test_coverage_diagnostic']['coverage'],1),number(r['historical_test_coverage_diagnostic']['accepted_metrics']['balanced_accuracy']) if r['historical_test_coverage_diagnostic']['accepted_metrics'] else '-'] for s,r in apps.items()]))
    section('11. Síntese crítica e uso do conhecimento',
        'O processo completo foi executado, mas sua validade é acadêmica e condicionada às hipóteses registradas. O uso sustentado é documentar os padrões e melhorar a coleta: confirmar unidade paciente/atendimento e formação do alvo, preservar datas completas/unidades e registrar quando cada achado foi obtido. Uma implantação clínica ou eficácia diagnóstica não decorre desses experimentos.',
        f'O registro estruturado contém {n_decisions} decisões e configurações, além de todos os parâmetros aprendidos por fold e finais. O conjunto de alternativas foi amplo e explícito; não se afirma ótimo universal. O cuidado decisivo foi impedir que a busca escolhesse pela pontuação do teste e expor os resultados que contradizem preferências iniciais.')
    section('12. Reprodução, conceitos e fontes',
        'Conceitos empregados: KDD iterativo, tipos/escalas, análise univariada/bivariada, ausências e inconsistências, outliers, criação/redução de atributos, mediana, discretização, one-hot, log, padronização, balanceamento, generalização, complexidade/sobreajuste, hold-out, estratificação, grupos, CV, nested CV, tuning, pipeline, matriz de confusão, precisão/recall/F1/BA e curvas ROC/PR. Regressão logística, floresta, AP/Brier, Welch, V de Cramér e intervalos por grupos são complementos explicitados, sem presumir que sua explicação integral esteja nos materiais.',
        'Os dados clínicos e saídas por registro permanecem locais; o repositório contém código, decisões, parâmetros agregados, métricas e notebook. O comando run_full_kdd.py reproduz preparação, mineração e relatório. O notebook completo executa ou confere essa mesma biblioteca, valida os artefatos e reaplica modelos salvos. Versões, SHA da fonte, partições, configurações e seeds são registrados.',
        'Fontes: materiais locais de fundamentos, dados, exploração, limpeza, transformação e avaliação experimental da disciplina; dicionário e tema UCMF; orientação do professor comunicada pelo grupo. APIs verificadas na documentação oficial scikit-learn: prevenção de vazamento, validação cruzada, árvores e avaliação de modelos. Uso de IA: Codex auxiliou investigação, implementação, comparações, testes e redação. A compreensão e defesa oral do trabalho exigem leitura dos integrantes.')
    content=['# A2 - Processo completo do KDD','', 'Grupo 3 - Mineração de Dados, UFG, 2026/2. Antônio Henrique Queiroz Villar Lopes, João Vitor Fernandes Ferreira, Mateus Nery Bailão e Pedro Augusto Ferreira Matos.','']
    for s in sections:
        content.extend(['## '+s['title'],'',*sum(([p,''] for p in s['paragraphs']),[])])
        if s['table']:content.extend([table_md(*s['table']),''])
        if s['image']:content.extend([f'![{s["title"]}](../../resultados/a2/kdd_completo/{s["image"].name})',''])
    content.extend(['Referências técnicas: [vazamento](https://scikit-learn.org/stable/common_pitfalls.html), [validação](https://scikit-learn.org/stable/modules/cross_validation.html), [árvores](https://scikit-learn.org/stable/modules/tree.html), [métricas](https://scikit-learn.org/stable/modules/model_evaluation.html).',''])
    (docs/'Relatorio_A2_KDD_Completo.md').write_text('\n'.join(content));pdf(docs/'Relatorio_A2_KDD_Completo.pdf',sections)
    manifest={str(p.relative_to(out)):sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p.name!='manifesto.json'}
    (out/'manifesto.json').write_text(json.dumps({'source_sha256':check['source_sha256'],'protocol_sha256':check['protocol_sha256'],'files_sha256':manifest,'self_excluded':True},indent=2)+'\n')
    return docs/'Relatorio_A2_KDD_Completo.pdf'


def pdf(path,sections):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfdoc import PDFString
    from reportlab.pdfgen.canvas import Canvas
    import matplotlib
    fonts=Path('/System/Library/Fonts/Supplemental');regular=fonts/'Arial.ttf';bold=fonts/'Arial Bold.ttf'
    if not regular.exists():
        fonts=Path(matplotlib.get_data_path())/'fonts/ttf';regular=fonts/'DejaVuSans.ttf';bold=fonts/'DejaVuSans-Bold.ttf'
    pdfmetrics.registerFont(TTFont('FullRegular',str(regular)));pdfmetrics.registerFont(TTFont('FullBold',str(bold)))
    pdfmetrics.registerFontFamily('FullRegular',normal='FullRegular',bold='FullBold')
    class C(Canvas):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self._doc.Catalog.Lang=PDFString('pt-BR')
    body=ParagraphStyle('BodyFull',fontName='FullRegular',fontSize=10.5,leading=14,spaceAfter=7)
    heading=ParagraphStyle('HeadFull',parent=body,fontName='FullBold',fontSize=12,leading=15,spaceBefore=12,spaceAfter=7,keepWithNext=True,textColor=colors.HexColor('#163b50'))
    cell=ParagraphStyle('CellFull',parent=body,fontSize=8.5,leading=11,spaceAfter=0)
    width=A4[0]-76;story=[Paragraph('A2 - Processo completo do KDD',heading),Paragraph('Mineração de Dados - UFG - Grupo 3 - 04/11/2026',body),Paragraph('Antônio Henrique Queiroz Villar Lopes, João Vitor Fernandes Ferreira, Mateus Nery Bailão e Pedro Augusto Ferreira Matos',body)]
    for s in sections:
        story.append(Paragraph(escape(s['title']),heading))
        for p in s['paragraphs']:story.append(Paragraph(escape(p),body))
        if s['table']:
            headers,rows=s['table'];n=len(headers)
            if n==2:widths=[width*.27,width*.73]
            elif n==3:widths=[width*.62,width*.18,width*.20] if headers[0].startswith('Regra') else [width*.25,width*.15,width*.60]
            else:widths=[width/n]*n
            cells=[[Paragraph(escape(str(x)),cell) for x in row] for row in [headers,*rows]]
            t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcebf1')),('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#c1d4de')),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.extend([t,Spacer(1,8)])
        if s['image']:
            from PIL import Image as PILImage
            w,h=PILImage.open(s['image']).size;story.extend([Image(str(s['image']),width=width,height=width*h/w),Spacer(1,8)])
    def page(canvas,doc):
        canvas.saveState();canvas.setFont('FullRegular',8);canvas.setFillColor(colors.HexColor('#526c7a'));canvas.drawString(38,23,'A2 - KDD completo | classificação do rótulo registrado | Grupo 3');canvas.drawRightString(A4[0]-38,23,str(doc.page));canvas.restoreState()
    SimpleDocTemplate(str(path),pagesize=A4,leftMargin=38,rightMargin=38,topMargin=33,bottomMargin=38,title='A2 - Processo completo do KDD',author='Grupo 3 - UFG').build(story,onFirstPage=page,onLaterPages=page,canvasmaker=C)
