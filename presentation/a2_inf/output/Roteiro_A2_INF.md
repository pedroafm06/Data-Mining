# Roteiro da apresentação da A2

22 slides, todos apresentados. Fala com 1889 palavras. A estimativa adota 135 palavras/min, com 45 s de pausas e transições. Duração calculada: 14:46. O tempo real depende de ensaio. As notas técnicas e a arguição são material de estudo, fora da fala planejada.

- Antônio Henrique · 3:35
- João Vitor · 3:56
- Mateus Nery · 3:12
- Pedro Matos · 3:18

## 1. Classificação de registros cardíacos pediátricos

Antônio Henrique · 0:00 a 0:23

Boa tarde. Somos o grupo 3: Antônio Henrique, João Vitor, Mateus Nery e Pedro Matos, do INF da UFG. Apresentamos a segunda avaliação de Mineração de Dados, com o professor Rogério Salvini, neste semestre. O estudo de registros cardíacos pediátricos percorre seleção, limpeza, transformação, comparação dos modelos e interpretação dos resultados.

Notas de apoio, para consulta e arguição

- A resposta prevista é o rótulo registrado NORMAL X ANORMAL. A tarefa não estabelece diagnóstico clínico independente nem prediz desfecho futuro.
- A A2 apresenta o KDD completo: seleção, limpeza, transformação, mineração e interpretação. As melhorias pertencem à A2; a A1 entregue permanece preservada.

## 2. Problema e dados

Antônio Henrique · 0:23 a 1:01

A base UCMF reúne 12.873 fichas de cardiologia pediátrica do Real Hospital Português, em Recife, com 21 atributos. A pergunta é se as medidas registradas ajudam a prever a classificação Normal ou Anormal. É uma tarefa de classificação supervisionada: aprendemos com fichas cuja resposta já está registrada. Consideramos Anormal a classe positiva, que queremos reconhecer. Estamos prevendo esse registro, sem afirmar que o modelo confirme um diagnóstico independente. Também falamos em fichas, pois a base não comprova que cada linha corresponda a uma criança diferente.

Notas de apoio, para consulta e arguição

- A base contém 12.873 registros e 21 atributos originais. Não confundir registros, atendimentos e pacientes; a identidade longitudinal não foi confirmada.
- Classificação supervisionada usa um alvo conhecido no treino. Normal=0 e Anormal=1; positivo é a convenção da classe, não um juízo de valor.
- KDD significa descoberta de conhecimento em bases de dados: a mineração é a etapa dos modelos, inserida em seleção, limpeza, transformação e interpretação.

## 3. Quais fichas entraram na avaliação

Antônio Henrique · 1:01 a 1:38

Preservamos a fonte original. Das 12.873 fichas, 11.704 têm rótulo; as outras 1.169 não permitem calcular acertos e erros. Retiramos da nova comparação as 2.342 do teste histórico, já examinado antes, e uma ficha com possível equivalência com esse teste. Restaram 9.361: 5.394 Normal e 3.967 Anormal. As repetições foram preservadas e reunidas em 9.166 grupos candidatos. O objetivo é impedir que entradas idênticas apareçam dos dois lados da avaliação. Esses grupos aproximam dependências entre registros, mas não são identidades de pacientes confirmadas.

Notas de apoio, para consulta e arguição

- 12.873=11.704 rotulados+1.169 sem rótulo. 11.704−2.342−1=9.361 registros de desenvolvimento. 5.394 Normal+3.967 Anormal=9.361. A proporção Anormal é 42,37795%.
- O teste histórico já havia sido inspecionado e não foi reavaliado na comparação final. Não o chamar de teste final independente.
- Os 9.166 grupos são componentes candidatos. A união incorpora coincidências em campos brutos, excluindo ID e alvo. Nenhuma assinatura exata atravessa os folds externos finais, mas isso não prova separação perfeita por paciente.
- A linha em quarentena foi retirada por equivalência candidata com o teste histórico. As 1.169 linhas sem rótulo não compõem o treino/avaliação supervisionados, mas não foram destruídas na fonte.

## 4. Seleção das variáveis

Antônio Henrique · 1:38 a 2:21

O conjunto principal tem oito entradas: idade, sexo, peso, altura, índice de massa corporal, pressões sistólica e diastólica e frequência cardíaca. Excluímos os motivos do encaminhamento porque antecipam a resposta, como uma cardiopatia já estabelecida: esse é o risco de vazamento. HDA2, o segundo campo de histórico da doença, sai pela baixa cobertura e origem temporal incerta. ID e convênio não descrevem o estado fisiológico; as datas servem para calcular idade, sem entrar diretamente. Sopro, segundo som cardíaco, pulsos, classificação da pressão e sintomas ficam em uma comparação exploratória, pois sua relação com a rotulagem é incerta.

Notas de apoio, para consulta e arguição

- FISIO8 contém Peso, Altura, IMC, IDADE, PA SISTOLICA, PA DIASTOLICA, FC e SEXO. O alvo NORMAL X ANORMAL nunca é preditor.
- MOTIVO1/MOTIVO2 têm conteúdo que pode antecipar o laudo; ficam fora de todos os cenários. HDA2 fica fora pela incerteza temporal e escassa cobertura: 12.466 das 12.873 linhas estão vazias na origem. Baixa cobertura, sozinha, não prova vazamento.
- HDA significa histórico da doença no dicionário fornecido. Não inventar a expansão história da doença atual.
- ID identifica o registro, convênio é administrativo e datas brutas podem refletir coleta ou funcionar como quase identificadores. O contexto/tempo da obtenção das variáveis é parte da seleção, não apenas a associação estatística.
- PPA, SOPRO, B2, PULSOS e HDA1 são adicionados somente no cenário exploratório CLINICO. FISIO8 não é comprovadamente livre de qualquer incorporação no rótulo.

## 5. Limpeza: regras e exemplos

Antônio Henrique · 2:21 a 2:58

Primeiro padronizamos grafias, números e marcadores de ausência. Depois conferimos datas, coerência entre medidas e valores suspeitos. Na pressão, sistólica menor ou igual à diastólica leva a marcar ambas como indisponíveis, sem presumir que foram trocadas. Neste exemplo real, a frequência cardíaca 1.120 supera a regra de suspeita de 500 batimentos por minuto. Marcamos a célula como ausente e conservamos o restante da ficha. Não corrigimos para 112 porque não sabemos o valor verdadeiro. São regras de curadoria declaradas, não limites clínicos universais.

Notas de apoio, para consulta e arguição

- As regras são determinísticas por registro; não aprendem medianas. O arquivo bruto é preservado e cada mudança tem origem/regra documentadas.
- FC 1.120 é um exemplo real no desenvolvimento. O gatilho FC>500 é uma hipótese de curadoria, não um máximo fisiológico demonstrado. Não afirmar que o verdadeiro valor era 112.
- Quando PAS≤PAD, ambas são mascaradas. Não inverter automaticamente as colunas porque não se conhece a origem da inconsistência.
- A política mantém extremos potencialmente reais: pesos altos não são automaticamente excluídos; alturas de 30 a menos de 40 cm podem ser preservadas em idade menor que três meses ou desconhecida; PAD positiva baixa não é descartada só por ser baixa.
- Nenhuma conclusão de diagnóstico pode ser extraída das máscaras de qualidade. Seu objetivo é evitar alimentar os modelos com medidas cuja interpretação não pode ser sustentada.

## 6. Dados ausentes e preenchimento

Antônio Henrique · 2:58 a 3:35

Depois da limpeza, cerca de 56% das pressões e 34,6% dos índices de massa corporal estavam indisponíveis. Apagar fichas incompletas perderia muita informação. Comparamos a mediana global, valor central menos influenciado por extremos, com a mediana da faixa etária, para considerar o crescimento. Exigimos 30 observações por faixa; sem suporte, usamos a global. No ajuste final da floresta, frequência ausente recebe 92 e indicador de preenchimento um. Essa mediana vem do treino; cada divisão da validação aprende a sua, sem usar as fichas avaliadas.

Notas de apoio, para consulta e arguição

- Após limpeza e antes de preencher, PAS=55,9556%, PAD=56,0303% e IMC=34,5690% indisponíveis no desenvolvimento. Arredondamento apresentado: 56%, 56% e 34,6%.
- Mediana global e por faixa etária foram comparadas. Faixas fixas: 0, 0,25, 0,5, 1, 2, 5, 10, 15 e 20 anos; idade no limite inferior pertence à faixa que começa nele. A faixa exige pelo menos 30 valores observados de treino por variável.
- Sem suporte suficiente ou idade disponível, a imputação por idade retorna à mediana global. Ela se aplica a Peso, Altura, IMC e FC, quando esses atributos pertencem ao cenário.
- 92 é a mediana de FC no ajuste final da floresta sobre todo o desenvolvimento. Cada fold aprende sua própria mediana. Indicador1 significa ausente ou mascarado; uma FC observada92 recebe indicador0.
- A mediana resiste melhor a extremos do que a média, mas reduz variação. Indicadores preservam a distinção estimado/observado e podem também carregar padrões da coleta; isso foi investigado, sem prova de inocuidade.

## 7. Idade e IMC: atributos derivados

João Vitor · 3:35 a 4:16

Para idade, usamos a diferença entre nascimento e atendimento quando a interpretação é coerente; datas ambíguas exigem analisar as durações possíveis e a informação original. Mantivemos a idade contínua para preservar diferenças importantes no primeiro ano. Para o índice de massa corporal, ou IMC, usamos peso dividido pela altura em metros ao quadrado. Nesta ficha real, cinco quilos e 51 centímetros, ou 0,51 metro, produzem 19,22 quilos por metro quadrado. A reconstrução usa medidas observadas aproveitáveis, nunca peso e altura preenchidos. Assim, não apresentamos uma razão entre estimativas como se fosse observada.

Notas de apoio, para consulta e arguição

- A idade é calculada por calendário na data do atendimento, não na data atual. Anos com dois dígitos preservam a ambiguidade do século: a idade relativa pode ser resolvida sob 0≤idade<20 quando durações candidatas diferem no máximo um dia.
- Prioridade: duração de datas coerentes; idade literal explícita em DN; idade numérica original válida como fallback não verificado; caso contrário, ausente. As origens são registradas.
- IMC=Peso/(Altura/100)². Exemplo real: 5/(51/100)²=19,2233756 kg/m². O valor histórico19,0 pode refletir arredondamento; não foi provado ser erro de digitação.
- A reconstrução usa pais observados e retidos. Há preservação controlada do IMC histórico quando reconstruir é inviável. O IMC não é recalculado após imputar Peso e Altura.
- Idade contínua evita perder resolução no início da vida. As faixas da imputação não substituem IDADE contínua nos modelos.

## 8. Representação para os modelos

João Vitor · 4:16 a 4:55

Transformamos categorias em colunas indicadoras, a codificação one-hot. Para sexo F, a coluna F recebe um e M recebe zero; para M, ocorre o inverso. Isso evita impor uma ordem numérica às categorias. Na logística, comparamos padronizar as medidas, subtraindo a média e dividindo pelo desvio-padrão, com aplicar antes o logaritmo de um mais o peso. A padronização torna as escalas comparáveis para a penalização; o logaritmo comprime diferenças entre pesos altos. Árvore e floresta mantêm unidades originais, pois decidem por cortes. Tudo é aprendido somente no treino.

Notas de apoio, para consulta e arguição

- One-hot mantém categorias separadas sem supor ordenação ou distâncias numéricas. Além de F/M, o transformador reserva colunas distintas para ausência e categoria não vista no treino.
- Padronização z=(x−média do treino)/desvio-padrão do treino, com ddof0. Se o desvio for zero, o divisor usado é1. Aplica-se somente a medidas contínuas; indicadores e one-hot continuam0/1.
- O logaritmo testado é log(1+Peso), não o logaritmo de todas as variáveis. Depois são padronizadas as medidas contínuas. A compressão da cauda pode ajudar a forma da relação; não é necessária por uma exigência de normalidade da logística.
- Na logística regularizada, escala afeta a penalização dos coeficientes; padronizar torna essa comparação mais coerente. Árvores dependem da ordenação/cortes e usam unidades originais.
- A logística final selecionou log do Peso e padronização, com imputação por faixa. A floresta final selecionou unidades e mediana global. Não transferir automaticamente essa escolha a todos os folds.

## 9. Por que comparar três modelos

João Vitor · 4:55 a 5:33

Comparamos três modelos porque eles representam relações de maneiras diferentes. A árvore faz perguntas sucessivas e permite acompanhar o caminho da decisão. A regressão logística combina contribuições das variáveis em uma relação mais simples. A floresta combina muitas árvores e consegue representar interações mais variadas. Essa diversidade permite avaliar se maior complexidade traz ganho, em vez de escolher o modelo mais sofisticado por princípio. Acrescentamos uma referência que sempre prevê a classe majoritária, Normal: um modelo precisa superar essa estratégia para mostrar utilidade na comparação.

Notas de apoio, para consulta e arguição

- Árvore oferece uma sequência inspecionável; logística regularizada fornece uma relação aditiva no escore; floresta combina árvores e pode captar interações e não linearidades. Isso justifica a diversidade de famílias testadas.
- A referência majoritária é DummyClassifier(strategy=most_frequent). Normal é a classe mais frequente nos treinos usados. A referência não usa as medidas para escolher a classe.
- A complexidade não garante melhor generalização. A comparação usa as mesmas partições e métricas; o ganho observado da floresta sobre a logística é pequeno.

## 10. Como a árvore decide

João Vitor · 5:33 a 6:11

A árvore final começa perguntando se o peso é menor ou igual a 8,85 quilos. No ramo dos menores pesos, aparece um corte de idade próximo de 14 dias; no outro, um corte de frequência cardíaca em 98,5 batimentos por minuto. São perguntas aprendidas dos dados, não regras clínicas. O critério Gini procura separar grupos menos misturados entre Normal e Anormal. Limitar profundidade e exigir um número mínimo de fichas por folha, o grupo final da árvore, restringe divisões muito específicas que poderiam memorizar o treino.

Notas de apoio, para consulta e arguição

- A árvore FISIO8 ajustada ao desenvolvimento escolheu Gini, max_depth6, min_samples_leaf50, pesos balanceados e imputação por idade. Os primeiros cortes são exemplos desse ajuste final, não o modelo de todas as rodadas.
- Primeiro corte Peso≤8,85kg. Nesse ramo, IDADE≤0,03830376ano, aproximadamente14dias. No ramo Peso>8,85kg, FC≤98,5bpm. Os caminhos continuam: não atribuir classe definitiva só por essas primeiras perguntas.
- Gini=1−Σp_classe²; as proporções respeitam os pesos usados no ajuste. Um nó só de uma classe tem impureza0. A escolha da divisão busca reduzir a impureza ponderada dos grupos.
- Profundidade máxima e mínimo de amostras por folha são controles prévios de complexidade. A grade final compara esses controles; não dizer que usou poda posterior por custo-complexidade nessa execução.

## 11. Como a logística e a floresta preveem

João Vitor · 6:11 a 6:51

Na logística, cada entrada contribui para um escore, convertido em uma probabilidade estimada de Anormal. A regularização reduz coeficientes excessivos, ajudando a controlar ajustes muito específicos. Na floresta, 150 árvores são treinadas com amostras e escolhas de atributos variadas; suas probabilidades são combinadas pela média. Isso reduz a dependência de uma única árvore. Nos dois casos usamos o mesmo corte fixo: probabilidade a partir de 0,5 vira Anormal, abaixo disso vira Normal. A comparação avalia os erros gerados por esse corte; ele não foi escolhido para uma aplicação clínica.

Notas de apoio, para consulta e arguição

- A logística calcula um escore linear nas entradas transformadas e aplica a função logística, produzindo um valor entre0e1. A penalizaçãoL2 restringe coeficientes; C menor significa penalização mais forte.
- RandomForestClassifier usa bootstrap por árvore e subconjuntos de atributos nas divisões; a previsão de probabilidade é a média das probabilidades das árvores. Não resumir o comportamento deste código como voto majoritário de rótulos.
- 150 árvores é um valor fixo na grade; não foi demonstrado ser o ótimo. Limiar0,5 também é fixo: p≥0,5→Anormal, p<0,5→Normal.
- Os escores não foram demonstrados como probabilidades clínicas calibradas fora da amostra. Pesos balanceados e possíveis alterações de prevalência importam para essa interpretação.

## 12. Validação sem misturar treino e avaliação

João Vitor · 6:51 a 7:31

Usamos validação cruzada aninhada. Dividimos os registros em cinco partes e repetimos cinco rodadas: quatro partes servem para treinar e uma para avaliar. Dentro do treino, outras três divisões escolhem os ajustes. Depois, o procedimento escolhido prevê a parte externa, que não participou dessa escolha. Assim, cada ficha recebe uma previsão externa. As divisões são iguais para comparar os modelos e preservam aproximadamente as proporções das classes. Fichas do mesmo grupo ficam juntas. Preenchimento, categorias e escalas também são aprendidos dentro de cada treino, evitando usar a avaliação na preparação.

Notas de apoio, para consulta e arguição

- Cinco folds externos e três internos. A seleção ocorre por família e cenário dentro de cada treino externo, usando média de BA interna. O vencedor é reajustado no treino externo para prever o fold reservado.
- Toda ficha recebe uma previsão externa. As métricas finais agregam essas previsões; não são o desempenho de treino do modelo final ajustado ao desenvolvimento inteiro.
- Grupos candidatos ficam indivisíveis e a estratificação aproxima a proporção das classes. Comparações usam os mesmos cortes. A validação aninhada separa ajuste de avaliação interna, mas não substitui nova coorte.
- Sementes:42 nos estimadores,743 nas divisões externas,811+k nas internas do foldk e43 na seleção final. Fixar sementes torna a execução reproduzível, não prova estabilidade sob todo sorteio.
- As regras fixas de curadoria têm histórico de exploração da coorte. Mesmo com parâmetros aprendidos só no treino, não se deve chamar todo o desenvolvimento de independente de qualquer decisão anterior.

## 13. Quais alternativas foram comparadas

Mateus Nery · 7:31 a 8:09

Foram 105 configurações por cenário: 48 árvores, 32 logísticas, 24 florestas e uma referência. Variamos critério, profundidade, mínimo de fichas por folha, pesos das classes e preenchimento; na logística também regularização e representação. Pesos balanceados aumentam a contribuição da classe menos frequente. A escolha usa a melhor acurácia balanceada interna por família. No ajuste final da floresta, ficaram 150 árvores, mínimo de 30 fichas por folha, pesos balanceados, mediana global e unidades originais. Esses parâmetros finais não precisam ser os escolhidos em todas as rodadas externas.

Notas de apoio, para consulta e arguição

- 48 árvores=2 critérios(Gini/entropia)×3 profundidades(2/4/6)×2 folhas(20/50)×2 pesos×2 imputações.
- 32 logísticas=4 valoresC(0,01/0,1/1/10)×2 pesos×2 imputações×2 representações(padronizada/logPeso+padronizada).
- 24 florestas=3 profundidades(4/8/sem limite)×2 folhas(10/30)×2 pesos×2 imputações;150 árvores fixas. Soma com referência1:105 por cenário.
- Ajuste final FISIO8/floresta:150 árvores, profundidade sem limite explícito, folha mínima30, class_weightbalanced, imputação global e unidades. A folha mínima restringe crescimento mesmo sem teto explícito de profundidade.
- Pesos balanced são inversamente proporcionais à frequência de classe do treino. Não é duplicação de linhas nem aplicação de SMOTE; essa grade não inclui reamostragem.
- Em empate numérico na média interna de BA, prevalece a ordem fixa da grade. A busca é finita e não demonstra ótimo universal.

## 14. Por que usar acurácia balanceada

Mateus Nery · 8:09 a 8:47

A acurácia comum é a proporção total de acertos. Como Normal é mais frequente, prever sempre Normal já acerta 57,62% das fichas, mas não reconhece nenhum Anormal. Por isso usamos acurácia balanceada: a média entre especificidade, a proporção de Normal reconhecidos, e sensibilidade, a proporção de Anormal reconhecidos. Para essa referência, temos 100% de especificidade e zero de sensibilidade. A média é 50%. Assim, as duas classes têm o mesmo peso na comparação, e uma pontuação aparentemente razoável não esconde o abandono completo de uma delas.

Notas de apoio, para consulta e arguição

- BA=(sensibilidade+especificidade)/2. Sensibilidade=TP/(TP+FN), entre Anormal; especificidade=TN/(TN+FP), entre Normal. A média é entre taxas por classe, não entre números brutos de acertos.
- A referência é majoritária: 5.394/9.361=57,622% de acurácia total; sensibilidade 0%, especificidade 100%, BA 50%.
- A BA não resume todo o impacto de erros. Por isso mostramos a matriz e taxas separadas. O trabalho relata ainda precisão, F1, precisão média e outras métricas.

## 15. Comparação dos modelos

Mateus Nery · 8:47 a 9:24

Com as oito entradas principais, a referência alcançou 50% de acurácia balanceada; a árvore, 61,69%; a logística, 62,03%; e a floresta, 63,27%. A floresta teve o melhor resultado observado, mas o ganho sobre a logística foi pequeno: 1,24 ponto percentual. Reamostramos os grupos e recalculamos essa diferença, obtendo um intervalo descritivo de 95% entre 0,43 e 2,01 pontos. Isso considera as previsões já produzidas; não inclui treinar tudo novamente nem testar outra população. Portanto, há ganho interno, sem demonstrar uma vantagem universal da floresta.

Notas de apoio, para consulta e arguição

- BA externa agregada FISIO8: árvore 0,6168849; logística 0,6202646; floresta 0,6326686; referência 0,5.
- Diferença floresta−logística: 1,24039 p.p. IC descritivo pareado de 95%: 0,4304 a 2,0110 p.p. IC da BA da floresta: 62,0678% a 64,3942%.
- Intervalos: 2.000 reamostragens de componentes, pareadas entre modelos. São condicionados às previsões, cortes e treinamentos existentes; não incluem novo ajuste completo nem nova coorte.
- Floresta final: 150 árvores, max_depth=null, min_samples_leaf=30, class_weight=balanced, imputação global e medidas nas unidades originais. Folha é o grupo final de uma árvore; exigir suporte mínimo limita a fragmentação em pequenos grupos e pode reduzir memorização. Não garante generalização.
- A configuração final é escolhida por validação interna no desenvolvimento. As métricas das barras vêm dos modelos das rodadas externas, não do modelo final treinado em todo o desenvolvimento. Não usar training_metrics_descriptive como desempenho de avaliação.
- Não afirmar que todas as famílias são estatisticamente diferentes entre si. A comparação destacada é floresta versus logística, com vantagem pequena nesta avaliação.

## 16. Acertos e erros da floresta

Mateus Nery · 9:24 a 10:03

A matriz mostra os acertos e erros das previsões externas. Entre as fichas Normal, a floresta acertou 3.687 e chamou 1.707 de Anormal. Entre as Anormal, reconheceu 2.308 e deixou passar 1.659 como Normal. Estes últimos são falsos negativos. A sensibilidade foi 58,18%, e a especificidade, 68,35%. Em linguagem direta, aproximadamente 42 de cada cem Anormal passaram como Normal. A média balanceada resume o desempenho, mas essas quantidades deixam claro que muitos erros permanecem e que o resultado não sustenta apresentar o modelo como uma triagem validada.

Notas de apoio, para consulta e arguição

- Matriz FISIO8/floresta, linhas e colunas Normal/Anormal: [[3687,1707],[1659,2308]]. TN=3687; FP=1707; FN=1659; TP=2308.
- Sensibilidade 58,17998%; especificidade 68,35373%; taxa de falsos negativos 41,82002%; taxa de falsos positivos 31,64627%. Arredondamentos orais: 58, 42 e 32 por cem.
- O denominador de 42 por cem são os Anormal; o de 32 por cem são os Normal. Nenhum dos dois é o conjunto total de fichas.
- Entre Anormal com idade conhecida, a mediana é 6,51 anos nos falsos negativos e 0,59 ano nos verdadeiros positivos. É comparação descritiva, não taxa de erro por faixa etária nem causalidade.
- Falso negativo significa Anormal no rótulo e Normal na previsão. Não conhecemos a gravidade clínica ou o desfecho desses registros.

## 17. O que as outras métricas acrescentam

Mateus Nery · 10:03 a 10:43

Precisão e sensibilidade respondem a perguntas diferentes. A precisão olha as previsões Anormal: 57,48% delas tinham esse rótulo. A sensibilidade, que vimos antes, olha todos os registros com rótulo Anormal. O F1 combina precisão e sensibilidade em uma média que penaliza o desequilíbrio entre elas; ficou em 57,83%. Já a precisão média, AP, resume a relação entre precisão e recuperação ao variar o ponto de corte dos escores; foi 59,51%. Usamos essas métricas juntas porque nenhuma, isoladamente, descreve a quantidade de alarmes falsos, as omissões e a qualidade da ordenação.

Notas de apoio, para consulta e arguição

- Precisão=2308/(2308+1707)=57,4844%. F1=2TP/(2TP+FP+FN)=57,8301%.
- AP=average_precision_score das probabilidades externas, igual a0,5950686. Resume a precisão ponderada pelos incrementos de recuperação e não é a integral trapezoidal da curva PR.
- A execução também calcula acurácia total64,04%,ROC-AUC0,671838eBrier0,227378. O guia de defesa explica seus papéis.
- Os percentuais do slide vêm de FISIO8/forest, com as mesmas previsões externas da matriz.

## 18. O que aprendemos com os erros

Pedro Matos · 10:43 a 11:22

Também investigamos quem aparece nos erros. Entre Anormal com idade conhecida, os previstos como Normal tinham mediana de 6,51 anos; os reconhecidos tinham mediana de 0,59 ano. Isso sugere examinar melhor o desempenho ao longo da idade, mas não demonstra que ser mais velho cause o erro. Comparar medianas não é calcular taxas por faixa: precisamos saber quantas fichas de cada faixa estavam disponíveis. O próximo aprofundamento deve comparar taxas, ausência de medidas e incerteza nos subgrupos, e verificar se esses padrões aparecem em uma amostra independente.

Notas de apoio, para consulta e arguição

- Para FISIO8/floresta, entre os registros Anormal com idade conhecida, mediana dos falsos negativos=6,5123288 anos; dos verdadeiros positivos=0,5945205ano.
- Esses números descrevem a idade entre tipos de resultado. Não são sensibilidade por faixa, não têm todos os registros de cada faixa no denominador e não provam que idade cause o erro.
- Comparar taxas por faixa exige denominadores e incerteza próprios. Ausência de medidas e composição do atendimento podem contribuir; são hipóteses para investigação, não causas demonstradas.
- O próximo exame de subgrupos não foi executado como nova validação independente nesta revisão dos slides. Não apresentar uma proposta como resultado já observado.

## 19. Quais medidas a floresta mais usou

Pedro Matos · 11:22 a 12:01

Para investigar quais medidas sustentam as previsões, embaralhamos uma variável entre as fichas e avaliamos novamente. Seus valores continuam presentes, mas perdem a ligação com a ficha original. Ao embaralhar frequência cardíaca, a acurácia balanceada caiu 4,80 pontos percentuais; para peso, 2,76; para idade, 1,40. Quanto maior a queda, maior a dependência nesse teste. Isso é importância por permutação, não efeito causal. Variáveis correlacionadas podem compensar umas às outras, e o embaralhamento pode criar combinações pouco realistas. A interpretação descreve o uso da informação por esse procedimento.

Notas de apoio, para consulta e arguição

- Permutação nas partes externas: três repetições por atributo e por fold, reaplicando transformações ajustadas no treino. Quedas médias de BA: FC 4,7988 p.p.; Peso 2,7627 p.p.; IDADE 1,3985 p.p.
- A permutação atua no atributo de origem e reaplica o preparo. A dependência pode incluir indicadores de ausência e seu papel na imputação.
- Atributos correlacionados podem se compensar. O embaralhamento pode criar combinações pouco realistas. Não interpretar as quedas como efeito causal nem ranking universal de relevância clínica.
- Ponto percentual expressa diferença entre percentuais, não porcentagem relativa de queda.

## 20. O resultado muda com as entradas

Pedro Matos · 12:01 a 12:41

Também mudamos quais informações entram. Só com peso, altura, idade e sexo, o melhor resultado foi 59,55%, da árvore. Com as oito entradas principais, a floresta chegou a 63,27%. Com treze entradas, acrescentando sopro, segundo som cardíaco, pulsos, classificação da pressão e sintomas registrados, a árvore chegou a 91,92%. Cada número corresponde à melhor família observada no cenário, nas mesmas fichas e divisões. Esse salto mostra dependência das entradas, não apenas do algoritmo. O último cenário é exploratório: esses achados podem ter participado da própria classificação que tentamos prever.

Notas de apoio, para consulta e arguição

- STRICT4/árvore BA=59,54645%; FISIO8/floresta BA=63,26686%; CLINICO/árvore BA=91,91565%. Arredondamentos: 59,55%, 63,27% e 91,92%.
- As famílias de maior BA observada diferem entre cenários. As barras não isolam um atributo nem representam a mesma família em todos os casos. Usam as mesmas fichas e cortes externos.
- Na mesma família árvore, CLINICO−FISIO8 é aproximadamente 30,23 p.p. Os cinco campos entram como bloco; não atribuir todo o ganho ao sopro.
- CLINICO adiciona PPA, HDA1, SOPRO, B2 e PULSOS. PPA é a classificação histórica de pressão; não foi reconstruída como novo percentil validado. HDA1 agrega o sintoma registrado.
- Em STRICT4 as diferenças entre famílias são pequenas e os intervalos pareados cruzam zero. Não apresentar a árvore como vencedora comprovada para população externa.
- FISIO8 também depende da hipótese de disponibilidade e da relação das medidas com a rotulagem. STRICT4 oferece análise mais restrita dessa dependência.

## 21. O papel do sopro

Pedro Matos · 12:41 a 13:19

O sopro é um som identificado no exame do coração. Quando sua ausência estava explicitamente registrada, 10,1% das fichas eram Anormal; com presença registrada, eram 95,6%. Campo vazio não foi tratado como ausência de sopro. A associação é forte, e embaralhar esse campo reduz a acurácia balanceada da árvore exploratória em 38,57 pontos. Isso mostra dependência, sem provar sua origem. Falta esclarecer quando o achado foi registrado e se integrou a definição do rótulo. Por isso, a pontuação de 91,92% não substitui nosso resultado principal.

Notas de apoio, para consulta e arguição

- Ausência explícita: 5.814 registros, 587 Anormal; 587/5814=10,0963%. Presença conhecida: 3.529 registros, 3.375 Anormal; 3375/3529=95,6362%. Há 18 fichas com status indisponível, fora dos dois denominadores.
- Ausência explícita de sopro e campo sem preenchimento são situações diferentes. Não somar as 18 fichas indisponíveis às de ausência registrada.
- Na árvore CLINICO, permutar SOPRO reduz BA em 38,5718 p.p.; permutar B2, em 3,2118 p.p. Mede dependência preditiva, não prova por si só vazamento nem causalidade.
- Dos 498 falsos negativos da árvore CLINICO, 496 têm ausência explícita de sopro. Ausência de sopro não equivale a Normal.
- Cronologia e incorporação no rótulo são questões distintas. Mesmo um exame anterior ao laudo pode integrar o critério que define a classe; é necessário esclarecer ambas.
- 95,6% é a proporção de rótulo Anormal nesse subconjunto da base, não uma probabilidade universal de doença em crianças com sopro.

## 22. Conclusões e próximos passos

Pedro Matos · 13:19 a 14:01

Concluímos o processo completo: selecionamos entradas, limpamos e transformamos a base, comparamos modelos e interpretamos erros e dependências. A floresta alcançou 63,27% de acurácia balanceada no cenário principal, reconhecendo 58% dos Anormal, superando a referência, com ganho pequeno sobre a logística e muitos Anormal não reconhecidos. As pontuações altas com achados dependem de informações próximas da rotulagem. Antes de propor uso, precisamos documentar paciente e atendimento, ordem de coleta e critério de Normal ou Anormal, e avaliar em novos registros independentes. O conhecimento obtido inclui tanto o desempenho quanto as condições e limitações para interpretá-lo.

Notas de apoio, para consulta e arguição

- Concluir sobre previsão do rótulo registrado, não sobre uso clínico validado. A avaliação é interna, com grupos candidatos e decisões exploratórias anteriores.
- Evidência central: BA 63,27%, sensibilidade 58,18%, aproximadamente 42 de cada 100 Anormal previstos Normal e vantagem pequena da floresta para a logística.
- Os próximos passos começam por unidade paciente/atendimento, ordem de coleta, definição da classe e amostra independente. Trocar o algoritmo não resolve essas lacunas.
- O KDD completo foi realizado: seleção, limpeza, transformação, mineração e interpretação. Concluir o processo não elimina as incertezas da fonte nem estabelece validade fora da base.

## Arguição

**Por que prever Normal ou Anormal não é validar um diagnóstico?**

A resposta disponível é uma classificação registrada na ficha. Não conhecemos suficientemente a referência usada para defini-la nem dispomos de confirmação independente de cada linha. O modelo mede concordância com o registro; a validade clínica exige evidência adicional.

**De onde saíram as 9.361 fichas avaliadas?**

Dos 12.873 originais, 11.704 têm rótulo e 1.169 não têm. Entre os rotulados, 2.342 pertencem ao teste histórico e uma linha foi retirada por equivalência candidata com ele. Restaram 9.361 no desenvolvimento: 5.394 Normal e 3.967 Anormal. Os resultados finais são das previsões externas da validação cruzada nesse desenvolvimento.

**Por que a contagem rotulada da A2 é maior que a da A1?**

A A1 removeu 987 cópias exatas ao ignorar ID; 235 eram rotuladas. A A2 preserva as linhas e trata a dependência no agrupamento da avaliação. Os rotulados passam de 11.469 para 11.704 antes de separar o teste histórico e retirar uma linha. A A1 entregue permanece preservada.

**Por que excluíram MOTIVO1 e MOTIVO2?**

Há conteúdo diagnóstico explícito, como Cardiopatia já estabelecida. A entrada pode antecipar ou integrar a resposta pretendida. A exclusão é guiada por origem e significado, não apenas por uma correlação ou pontuação. Os motivos ficam fora de todos os cenários.

**FISIO8 está comprovadamente livre de vazamento?**

Não. É o cenário principal sob hipótese de disponibilidade das medidas e de relação adequada com a rotulagem, retirando motivos e achados de maior proximidade diagnóstica. FC e pressões também podem participar da investigação. STRICT4 reduz parte dessa dependência, e a documentação insuficiente do rótulo continua sendo uma limitação.

**Por que não corrigir FC 1120 para 112?**

Não podemos confirmar que houve um zero extra. A regra declarada mascara valores acima de 500 como suspeitos e conserva o restante da ficha. Não sabemos o valor verdadeiro. Esse limite serve à curadoria da base, não é um máximo fisiológico estabelecido.

**Por que a ausência recebe 92?**

92 é a mediana de FC aprendida no ajuste final da floresta sobre o desenvolvimento. O exemplo ilustra essa transformação final. Na validação, cada divisão aprende sua mediana apenas no treino. O indicador de preenchimento diferencia uma estimativa de uma medida aproveitável.

**A mediana por idade foi testada?**

Sim. A busca compara global e faixas fixas de idade, exigindo pelo menos 30 observações de treino na faixa; sem suporte ou idade, usa a global. No ajuste final da floresta, foi selecionada a global. Isso não significa que todos os modelos e folds escolheram o mesmo.

**O IMC foi calculado com peso e altura preenchidos?**

Não. A reconstrução usa peso e altura observados utilizáveis. Sem isso, há preservação controlada do histórico ou ausência. Não recomputamos após preencher os insumos, pois a razão seria de estimativas. O exemplo observado usa 5 kg e 51 cm, produzindo 19,2234 kg/m².

**Todos os modelos receberam padronização e logaritmo?**

Não. Árvore e floresta mantêm unidades originais. A logística compara padronizar as medidas originais com aplicar log(1+Peso) somente ao peso antes da padronização. Categorias usam one-hot; colunas binárias não são padronizadas. Todo parâmetro vem do treino de cada divisão.

**Qual a diferença entre divisões externas e internas?**

As três internas escolhem ajustes dentro do treino disponível, separadamente por família. A parte externa reservada avalia o procedimento sem participar da escolha. Em cada uma das cinco rodadas externas, a configuração escolhida é reajustada no treino externo e prevê sua parte reservada. Cada ficha recebe uma previsão externa.

**O que são as 105 configurações?**

Por cenário: 48 árvores, 32 logísticas, 24 florestas e uma referência majoritária. Variam profundidade, folha mínima, pesos, regularização, representação e imputação conforme a família. Cada floresta tem 150 árvores. A busca compara alternativas definidas; não prova que esgotamos todo modelo possível.

**Como trataram registros repetidos e o que mudou na revisão?**

Mantivemos as linhas e unimos grupos quando entradas brutas coincidem, excluindo ID e alvo. A revisão reuniu seis conjuntos, 118 fichas, que atravessavam folds. Os grupos passaram de 9.279 para 9.166 e nenhum desses conjuntos cruza folds externos na nova execução. São componentes candidatos, não identidades de pacientes confirmadas.

**Por que o teste histórico não é a confirmação final?**

Já havia sido examinado em fases anteriores e há padrões brutos compartilhados com o desenvolvimento. Suas 2.342 fichas ficaram fora da nova comparação. A validação aninhada separa ajustes de previsões externas, mas permanece interna. Confirmação independente exige nova amostra com coleta e rotulagem documentadas.

**Por que acurácia balanceada?**

Sempre Normal já acerta 57,62% no total, mas zero Anormal. A BA tira a média do acerto entre Normal e do reconhecimento entre Anormal, dando peso igual às classes; a referência fica em 50%. Também mostramos as taxas separadas, pois a média sozinha não descreve os erros.

**Por que pelo menos trinta fichas por folha na floresta final?**

Folha é o grupo final de uma árvore. Exigir suporte mínimo limita divisões muito específicas em grupos pequenos e pode reduzir memorização. O valor 30 foi escolhido entre alternativas pela validação interna no ajuste final, junto dos demais parâmetros. Não é uma garantia de generalização nem um limiar clínico. Os resultados exibidos vêm das previsões externas, não do treino desse ajuste final.

**Como construíram o intervalo da vantagem da floresta?**

Usamos 2.000 reamostragens pareadas de componentes e recalculamos as métricas das previsões externas existentes. A diferença floresta−logística foi 1,24 p.p., com IC descritivo de 95% de 0,43 a 2,01 p.p. O intervalo depende dos cortes e treinamentos feitos; não inclui novo treinamento nem outra coorte.

**A floresta reconhece 63,27% dos Anormal?**

Não. 63,27% é a média dos acertos por classe. Ela reconhece 58,18% dos Anormal, 2.308 de 3.967, e 68,35% dos Normal, 3.687 de 5.394. Aproximadamente 42 de cada 100 Anormal receberam previsão Normal.

**O que explica a diferença de idade nos erros?**

Entre Anormal com idade conhecida, a mediana é 6,51 anos nos previstos Normal e 0,59 nos reconhecidos. Isso descreve a composição dos grupos, não demonstra causa nem mede taxa de erro por idade. Para concluir sobre faixas, precisamos comparar denominadores, taxas e incerteza em cada uma.

**Os cortes da árvore são referências clínicas?**

Não. Peso de 8,85 kg, idade próxima de 14 dias e FC de 98,5 bpm são cortes aprendidos pela árvore final no desenvolvimento. Ilustram suas perguntas iniciais; não são critérios diagnósticos estabelecidos nem uma regra isolada validada fora da base.

**Permutação identifica as causas do rótulo?**

Não. Mede a queda ao desfazer a ligação de um atributo com sua ficha. Descreve a dependência do procedimento, incluindo efeitos do preenchimento e indicadores. Campos correlacionados podem se compensar e o embaralhamento pode gerar combinações pouco realistas.

**Por que CLINICO é exploratório e SOPRO não é vazamento comprovado?**

Os campos podem participar do critério de rotulagem. Há associação forte: 10,1% Anormal com ausência explícita de sopro e 95,6% com presença. Permutar SOPRO reduz a BA da árvore em 38,57 p.p. Isso mostra dependência, não sua origem. É necessário conhecer cronologia e definição do rótulo; mesmo um exame anterior pode integrar sua construção.

**As pontuações dos cenários isolam o efeito de cada campo?**

Não. Mostram a maior BA observada entre famílias em cada conjunto, nas mesmas fichas e cortes: STRICT4/árvore 59,55%; FISIO8/floresta 63,27%; CLINICO/árvore 91,92%. Na mesma família árvore, acrescentar o bloco aumenta a BA em cerca de 30,23 p.p. É efeito conjunto do bloco, não contribuição causal isolada de cada campo.

**O que é necessário para avançar?**

Documentar paciente versus atendimento, ordem de coleta e critério de Normal/Anormal; definir momento e finalidade da previsão; avaliar em nova amostra independente. O trabalho conclui o KDD e torna as decisões rastreáveis, mas esses próximos passos dependem de informações que a fonte atual não fornece.

**Por que não apagar todas as fichas com algum valor ausente?**

As ausências são numerosas: cerca de56% em cada pressão e34,6% no IMC após limpeza. Exigir completude de todos os campos perderia dados e poderia alterar a composição da amostra. Comparamos imputações dentro do treino, mantemos indicadores e examinamos padrões de coleta. Isso não torna a imputação equivalente a observar a medida real.

**Por que as duas pressões são mascaradas quando a sistólica é menor ou igual à diastólica?**

O par viola a relação esperada entre essas medidas. Sem acesso à ficha original, não sabemos se os campos foram trocados ou qual deles está errado. Mascarar o par evita uma correção inventada, preservando os outros campos e o registro da regra.

**O que significa Gini e por que restringir a árvore?**

Gini mede a mistura de classes num nó:1−Σp². Um grupo de uma única classe tem impureza0. Divisões que reduzem a mistura podem também memorizar grupos muito pequenos; limitar profundidade e folha mínima controla essa especificidade. Comparamos Gini e entropia e diferentes restrições dentro da validação.

**A floresta vota ou faz média?**

Neste RandomForestClassifier, cada árvore produz probabilidades por classe e a floresta usa sua média. O rótulo é então obtido com corte0,5 para a probabilidade de Anormal. Dizer apenas que150rótulos votam não descreve exatamente o cálculo utilizado.

**Por que padronizar a logística e não as árvores?**

A logística regularizada penaliza os coeficientes; diferenças de unidade afetam os tamanhos necessários desses coeficientes. A padronização coloca as medidas contínuas em escalas comparáveis para essa penalização. Árvores usam cortes na ordenação dos valores e não exigem essa equalização.

**O logaritmo foi usado para tornar a logística válida?**

Não. A logística não exige preditores normalmente distribuídos. Comparamos log(1+Peso) porque comprime a cauda dos pesos altos e pode representar melhor a relação com o escore. A escolha veio da validação interna e só o Peso recebe log; as medidas contínuas depois são padronizadas.

**O que é regularização e o que faz o parâmetro C?**

A regularização penaliza coeficientes grandes para limitar ajustes excessivos. Em LogisticRegression,C é inverso da força dessa penalização: menores valores significam maior regularização. A grade comparou0,01;0,1;1;10, e o ajuste final escolheu1. Isso não significa que toda rodada externa escolheu1.
