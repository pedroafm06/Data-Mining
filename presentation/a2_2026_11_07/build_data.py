from pathlib import Path
import csv,json,hashlib,statistics
from collections import Counter,defaultdict

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ART=ROOT/'artifacts/a2_rubric_audit'
OUT=HERE/'.build'
OUT.mkdir(exist_ok=True)
def rows(name):
 with (ART/name).open() as f:return list(csv.DictReader(f))
def numrows(name):
 data=rows(name)
 for row in data:
  for k,v in row.items():
   try:row[k]=float(v)
   except (ValueError,TypeError):pass
 return data
verification=json.loads((ART/'verification.json').read_text())
assert verification['complete'] and verification['historical_test_rows_used']==0
assert verification['same_outer_validation_ids_all_models'] and verification['outer_oof_once_per_row']
metrics=numrows('family_nested_metrics.csv')
protocol=json.loads((ART/'protocol_before_results.json').read_text())
assert len(protocol['candidates'])==105
families={'dummy':'Referência','tree':'Árvore','logistic':'Logística','forest':'Floresta'}
by={(r['pool'],r['family']):r for r in metrics}
primary=max((r for r in metrics if r['pool']=='FISIO8'),key=lambda r:r['balanced_accuracy'])
importance=defaultdict(list)
for r in numrows('outer_permutation_importance.csv'):
 if r['pool']=='FISIO8' and r['family']==primary['family']:importance[r['variable']].append(r['BA_drop'])
importance=sorted([{'variable':k,'mean':statistics.mean(v),'n':len(v)} for k,v in importance.items()],key=lambda r:r['mean'],reverse=True)
controls=numrows('collection_process_controls.csv')
null=json.loads((ART/'permuted_label_control.json').read_text())
probes=numrows('variable_probes.csv')
policy=json.loads((ROOT/'docs/a2/auditoria_2026_11_07/Politica_Atributos.json').read_text())
def pt(x,d=1):return f'{x:.{d}f}'.replace('.',',')
def pct(x,d=1):return pt(100*x,d)+'%'
def integer(x):return f'{int(x):,}'.replace(',','.')

notes=[]
def note(title,seconds,author,text,question,answer,sources):
 notes.append(dict(number=len(notes)+1,title=title,seconds=seconds,author=author,text=text,question=question,answer=answer,sources=sources,hidden=False))
A='Antônio Henrique Queiroz Villar Lopes';J='João Vitor Fernandes Ferreira';M='Mateus Nery Bailão';P='Pedro Augusto Ferreira Matos'
note('Classificação de registros cardíacos pediátricos',30,A,
'Apresentamos a revisão final do estudo de caso UCMF. O trabalho tem duas partes conectadas: primeiro auditamos quais informações podem entrar no modelo e quais riscos permanecem. Depois comparamos referência, regressão logística, árvore e floresta com o mesmo protocolo. O foco é explicar o que os resultados sustentam. O modelo tenta classificar o rótulo que existe no registro. O estudo não dispõe de uma referência clínica independente para validar diagnóstico. A revisão mantém a A1 entregue como histórico e torna as novas decisões explícitas.',
'Qual é a contribuição principal?','A revisão completa dos atributos e a comparação entre famílias com as mesmas entradas e folds externos.',['Parecer_Semantico_e_Decisoes.md','protocol_before_results.json'])
note('Tarefa e significado do alvo',60,A,
'A tarefa é uma classificação supervisionada binária. A classe positiva é Anormal. O dicionário descreve o alvo como ausência ou presença de patologia cardíaca, mas não informa quem atribuiu o rótulo, quais exames serviram como referência nem em qual momento cada campo ficou disponível. Isso importa porque prever a decisão registrada é diferente de demonstrar detecção de doença por uma referência independente. A nossa pergunta operacional é quanto medidas disponíveis no registro permitem discriminar esse rótulo, sob uma política conservadora de atributos. As afirmações ficam condicionadas à disponibilidade das medidas antes do uso pretendido. Não chamamos a saída de diagnóstico e não inferimos causa a partir de associação.',
'O modelo prevê doença ou o registro?','O rótulo registrado. A equivalência com diagnóstico independente não foi documentada.',['Variáveis do conjunto de dados (SIGAA 03-11-2026).pdf','Tema do estudo de caso.pdf'])
note('Coorte e partições',70,A,
'A fonte tem 12.873 registros e 21 variáveis. Existem 11.704 rótulos conhecidos após o mapeamento explícito. A divisão histórica contém 9.361 registros de desenvolvimento, 2.342 do teste histórico e um registro em quarentena por equivalência candidata entre partições. Essa linha permanece na base original. Os demais 1.169 registros não têm rótulo utilizável para a classificação supervisionada. A nova execução usa somente o desenvolvimento, com 9.279 componentes candidatos de agrupamento. Esses componentes ajudam a manter possíveis equivalências juntas, mas não provam identidade de paciente. O ID é declarado como do paciente anônimo no dicionário. Sua unicidade na planilha não prova estabilidade entre retornos. O teste antigo já foi explorado e não recebeu nova avaliação nesta revisão.',
'Por que não usar o teste antigo novamente?','Porque a exposição anterior impede apresentá-lo como validação nova e intocada. A nova avaliação usa folds externos no desenvolvimento e assume o histórico de exploração.',['UCMF_raw.csv','a2_mining/particoes_modelagem.csv','verification.json'])
note('Riscos de vazamento nas 21 variáveis',70,A,
'A auditoria separa fatos de suspeitas. MOTIVO1 e MOTIVO2 contêm expressões como cardiopatia já estabelecida e cardiopatia congênita. O conteúdo diagnóstico é explícito, embora não saibamos se veio do mesmo processo que gerou y. SOPRO, B2 e PULSOS aparecem no material de investigação diagnóstica. Isso sugere possível incorporação, mas não prova que o fluxograma fornecido rotulou a UCMF. PPA é uma classificação derivada de hipertensão e seu vínculo com o alvo genérico permanece desconhecido. HDA contém sintomas e Assintomático, sem nomes de cardiopatia nas categorias observadas. Retiramos esse bloco da principal por proveniência incerta, com grau de suspeita diferente. Uma correlação forte, sozinha, não demonstra vazamento. A política não depende apenas do tamanho da associação.',
'Vocês provaram que SOPRO vaza o alvo?','Não. A suspeita tem fundamento semântico, mas falta o protocolo do alvo e a ordem temporal. A remoção é conservadora.',['Politica_Atributos.json','Guideline for diagnostic.pdf','UCMF_raw.csv'])
note('Conjuntos de atributos',60,J,
'FISIO8 contém Peso, Altura, IMC, IDADE, pressões sistólica e diastólica, frequência cardíaca e sexo. STRICT4 conserva Peso, Altura, IDADE e SEXO. Essa escolha foi documentada pelo tipo de informação antes da leitura dos novos resultados. STRICT4 testa uma alternativa mais restrita porque medidas de pressão ou frequência poderiam participar de critérios diagnósticos não documentados. Se HAS integrar o alvo, tirar PPA e manter suas pressões não elimina necessariamente essa informação. STRICT4 também retira o IMC histórico, reduzindo dependência de uma derivação antiga. Por retirar quatro atributos juntos, a diferença entre os conjuntos não identifica o efeito isolado de cada um. Nenhum conjunto recebe certificado de ausência de vazamento.',
'Por que manter medidas que podem estar no critério?','FISIO8 estuda medidas básicas sob uma premissa temporal explícita. STRICT4 documenta a sensibilidade à alternativa mais restrita. A falta de referência impede certeza nos dois.',['Politica_Atributos.json','protocol_before_results.json'])
note('Pré-processamento no treino',60,J,
'A limpeza reconhece grafias, sentinelas e valores suspeitos sem transformar desconhecido em Normal. O alvo recebe apenas o mapeamento explícito de valores válidos. Não corrigimos seu conteúdo com base em SOPRO ou outro achado. As transformações que aprendem com a amostra, como imputação por mediana, escalas e categorias, são ajustadas no treino de cada fold. A busca compara a imputação global e a baseada em idade, quando previstas para a família. Cada validação recebe somente a transformação aprendida no seu treino. Indicadores de ausência merecem cuidado: podem captar o processo de medição, e retirar o indicador explícito não remove necessariamente a marca deixada pela mediana imputada. As derivações mantêm rastreabilidade e as exclusões também valem para codificações dos campos retirados.',
'Por que não imputar antes de dividir?','Porque a mediana, a escala e o vocabulário passariam a conhecer os registros que deveriam apenas avaliar o modelo.',['preprocessing_audit.json','protocol_before_results.json','Politica_Atributos.json'])
note('Validação aninhada',100,J,
'Usamos cinco folds externos e três internos. Pensem primeiro em uma divisão externa: quatro partes ficam no treino e uma fica reservada para avaliar. Dentro das quatro partes de treino, os três folds internos comparam os hiperparâmetros de cada família. A seleção usa a média da acurácia balanceada interna. Depois ajustamos a configuração escolhida em todo o treino externo e produzimos as previsões da parte externa. Repetimos o processo cinco vezes, trocando a parte externa. Assim cada registro recebe uma previsão de um modelo que não o usou no próprio ajuste nem na seleção interna daquela previsão. Concatenamos essas previsões externas para formar as métricas OOF. As quatro famílias e os dois conjuntos usam as mesmas divisões externas, o que permite comparação pareada. Mantemos os grupos candidatos juntos. Isso reduz cruzamento de equivalências candidatas, mas não assegura que todos os retornos de uma pessoa foram detectados. A avaliação é interna à mesma coorte e permanece condicionada a decisões históricas já exploradas.',
'O que significa uma previsão OOF?','É uma previsão produzida quando aquela linha estava no fold externo de avaliação. O ajuste e a escolha interna ocorreram nas demais partes.',['protocol_before_results.json','outer_membership.csv','verification.json'])
note('Algoritmos e métricas',50,M,
'A referência prevê sempre a classe mais frequente e mostra o desempenho sem discriminação individual. A logística oferece uma relação regularizada e simples de interpretar. A árvore permite regras não lineares, e a floresta agrega várias árvores. A busca tem 105 configurações no total: uma referência, 48 árvores, 32 logísticas e 24 florestas. Escolhemos hiperparâmetros dentro de cada família para não comparar uma família ajustada com outra arbitrariamente fixada. A métrica de seleção é a acurácia balanceada, média da sensibilidade e da especificidade. Apresentamos também ROC-AUC, sensibilidade e especificidade. O limiar é 0,5, sem ajuste no teste histórico. Uma acurácia comum aparentemente razoável pode esconder o fato de a referência nunca reconhecer a classe Anormal.',
'Por que acurácia balanceada?','Ela dá o mesmo peso ao acerto de cada classe. A referência tem 57,6% de acurácia comum, mas 50% de BA e sensibilidade zero.',['protocol_before_results.json','family_nested_metrics.csv'])
note('Comparação principal',70,M,
f'Esta tabela resume as previsões externas de FISIO8. A floresta apresenta a maior acurácia balanceada observada, {pct(primary["balanced_accuracy"])}, com ROC-AUC de {pt(primary["roc_auc"],3)}. Sua sensibilidade é {pct(primary["recall"])} e a especificidade é {pct(primary["specificity"])}. A referência fica em 50% de BA. A logística e a árvore também superam numericamente essa referência, mas o ganho de complexidade não produz uma discriminação elevada. Todos os valores vêm das mesmas 9.361 linhas e dos mesmos folds externos. Não confundimos esse resumo com desempenho de treinamento, nem com o escore usado para escolher a configuração final. A maior média observada entre famílias não é uma demonstração de superioridade clínica ou uma validação externa confirmatória. A interpretação precisa considerar a incerteza e os erros, que mostramos a seguir.',
'Esse é o resultado do modelo treinado em todos os dados?','Não. São predições externas da validação aninhada. O ajuste final em todo o desenvolvimento serve à reprodução e não substitui a estimativa OOF.',['family_nested_metrics.csv','outer_fold_metrics.csv'])
note('Erros da floresta em FISIO8',60,M,
f'A matriz usa linha para o rótulo registrado e coluna para a classe predita. Entre {integer(primary["tn"]+primary["fp"])} registros Normal, o modelo classifica {integer(primary["tn"])} como Normal e {integer(primary["fp"])} como Anormal. Entre {integer(primary["fn"]+primary["tp"])} registros Anormal, classifica corretamente {integer(primary["tp"])} e deixa {integer(primary["fn"])} como Normal. Assim, aproximadamente {pct(1-primary["recall"])} dos anormais registrados não são reconhecidos nesse limiar. Falso positivo significa divergir do rótulo Normal, e falso negativo significa divergir do rótulo Anormal. Como a referência clínica do alvo não é independente e validada, tratamos esses termos como erros de classificação do registro. A matriz mostra por que um resumo único de desempenho é insuficiente e por que não há base para propor uso diagnóstico.',
'Um falso negativo aqui significa doença não detectada?','Significa previsão Normal quando o rótulo registrado é Anormal. A interpretação clínica exige referência validada, que não temos.',['family_nested_metrics.csv','oof_FISIO8_forest.csv'])
note('Dependência dos atributos',50,M,
f'A importância por permutação usa o próprio fold externo. Primeiro calculamos a BA naquele fold. Depois embaralhamos uma variável nesse conjunto e medimos quanto a BA cai, mantendo o modelo ajustado. O gráfico resume cinco folds e três repetições por variável na floresta FISIO8. A maior queda média aparece em FC, {pt(100*importance[0]["mean"],1)} pontos percentuais, seguida por Peso. Isso mostra dependência preditiva desse modelo na amostra avaliada. Não demonstra que FC causa a condição, que foi registrada antes de y ou que é independente do critério diagnóstico. Variáveis correlacionadas podem substituir umas às outras, e uma importância pequena não prova irrelevância individual. A presença forte de FC reforça o valor de olhar a sensibilidade STRICT4.',
'Importância é causalidade?','Não. É a perda de desempenho do modelo ao perturbar uma entrada no fold externo, condicionada às outras variáveis e ao modelo.',['outer_permutation_importance.csv'])
note('Sensibilidades e processo de coleta',60,P,
f'A comparação com STRICT4 mantém a população e as divisões externas. A BA observada da floresta cai de {pct(by["FISIO8","forest"]["balanced_accuracy"])} para {pct(by["STRICT4","forest"]["balanced_accuracy"])}. A logística em STRICT4 fica em {pct(by["STRICT4","logistic"]["balanced_accuracy"])}. Isso é uma sensibilidade ao conjunto de informação, sem trocar retrospectivamente a principal pelo melhor valor. Também ajustamos uma árvore fixa usando apenas máscaras de disponibilidade. Em FISIO8 ela alcança BA de {pct(controls[0]["balanced_accuracy"])}, mostrando sinal no padrão de preenchimento. Esse ensaio usa somente desenvolvimento e não equivale à busca aninhada das famílias. Um controle com rótulos permutados fica próximo de 50%, mas é diagnóstico auxiliar, sem p-valor formal e sem provar ausência de vazamento. Os controles sustentam uma interpretação cuidadosa do processo de registro.',
'FISIO8 ser melhor prova que as medidas são legítimas?','Não. Prova apenas uma diferença preditiva neste protocolo. A admissibilidade depende da origem e do momento das medidas.',['family_nested_metrics.csv','collection_process_controls.csv','permuted_label_control.json'])
note('Limites da evidência',60,P,
'A principal limitação é a falta de definição operacional e de referência independente do alvo. A segunda é a sequência de coleta: não temos horários nem histórico de atualização dos campos clínicos. A terceira é a representatividade, porque são registros de um serviço de cardiologia e a modelagem supervisionada depende de rótulo disponível. Os grupos são candidatos, sem identidade de paciente confirmada. Além disso, a coorte e escolhas de qualidade já receberam exploração anterior. A validação aninhada protege a seleção interna de hiperparâmetros desta execução, mas não apaga decisões históricas. O teste antigo não foi reavaliado. Mesmo retirando campos suspeitos, não afirmamos que o conjunto está livre de todos os mecanismos de vazamento. São limites que afetam a conclusão, e não detalhes que uma métrica alta resolveria.',
'Qual informação faltante mais mudaria o estudo?','O protocolo de formação do alvo e a ordem de obtenção das entradas. Isso permitiria decidir sobre incorporação e disponibilidade temporal.',['Parecer_Semantico_e_Decisoes.md','protocol_before_results.json','verification.json'])
note('Conclusão',70,P,
f'A revisão auditou as 21 variáveis e comparou quatro famílias com a mesma entrada e as mesmas divisões externas. A maior BA observada em FISIO8 é {pct(primary["balanced_accuracy"])}, na floresta. Esse resultado indica discriminação limitada do rótulo registrado e precisa ser lido junto dos {integer(primary["fn"])} falsos negativos de registro e dos {integer(primary["fp"])} falsos positivos. A política conservadora exclui os campos de diagnóstico prévio, os achados de maior incerteza e as classificações derivadas. Ela não transforma o alvo em referência independente. O próximo avanço não é apenas buscar outro algoritmo: é esclarecer a formação do rótulo, a ordem de coleta e a identidade estável entre retornos, e então obter uma avaliação confirmatória separada. Os dados originais e a A1 permanecem preservados. O código, as sementes, o protocolo e os manifestos permitem conferir as decisões e os resultados desta execução.',
'O que vocês defendem ao final?','Uma comparação reprodutível e uma política de atributos justificável, com melhora numérica sobre a referência e limites explícitos. Não defendemos diagnóstico clínico validado.',['family_nested_metrics.csv','Politica_Atributos.json','manifest.json'])
assert sum(x['seconds'] for x in notes)==870

content={
 'verification':verification,'protocol':protocol,'metrics':metrics,'primary':primary,'importance':importance,
 'controls':controls,'null':null,'probes':probes,'policy':policy,'notes':notes,
 'authors':[A,J,M,P], 'families':families,
 'counts':{'raw':12873,'columns':21,'known':11704,'unlabeled':1169,'development':9361,'candidate_groups':9279,'old_test':2342,'quarantine':1,'normal_dev':5394,'anormal_dev':3967},
 'sources_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ART.glob('*') if p.is_file() and p.suffix in ['.csv','.json']},
 'status':'verified_numeric_sources_loaded'
}
(OUT/'content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'slides_main':len(notes),'seconds':sum(x['seconds'] for x in notes),'primary_family':primary['family'],'data_source_complete':verification['complete']},ensure_ascii=False))
