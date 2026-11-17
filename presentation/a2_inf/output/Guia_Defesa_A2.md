# Guia de estudo e defesa da A2

Este guia acompanha a execução final de 16/11/2026. A A1 entregue permanece como registro histórico. As correções, os novos experimentos e o processo completo de KDD pertencem à A2. Use o roteiro dos slides para a exposição de até 15 minutos e este guia para estudar e responder à arguição.

## A resposta em cerca de um minuto

> Nosso objetivo foi prever o rótulo Normal ou Anormal das fichas de cardiologia pediátrica. Auditamos as 21 variáveis, retiramos entradas com risco de antecipar a resposta e tratamos números, datas e medidas suspeitas. Depois transformamos as entradas com parâmetros aprendidos apenas no treino. Comparamos uma referência sempre Normal com árvore, logística e floresta. A validação aninhada separou a escolha dos ajustes da avaliação, mantendo cópias no mesmo grupo. A floresta obteve 63,27% de acurácia balanceada nas oito entradas principais, mas deixou passar cerca de 42% dos Anormal. Com achados do exame, a pontuação chegou perto de 92%. Esse ganho exige esclarecer se os achados ajudaram a criar o próprio rótulo.

Ao responder qualquer pergunta, siga esta ordem: **o que decidimos, por que, como implementamos e qual limite permanece**. Por exemplo: “Marcamos a FC acima de 500 como suspeita. Fizemos isso para evitar que um valor com forte suspeita de registro entrasse como medida confiável. Preservamos o valor bruto e preenchemos a ausência usando somente o treino. Esse corte é uma regra de curadoria da base e precisa de revisão clínica, não uma fronteira entre saúde e doença”.

## 1. O problema e a sequência do KDD

KDD é o processo de transformar dados em conhecimento que possa ser interpretado. A classificação é uma etapa desse processo. Selecionar entradas, limpar inconsistências e avaliar o resultado também fazem parte do trabalho.

A sequência efetiva foi:

1. Preservar o CSV original e a A1 entregue, com registros das mudanças.
2. Entender a origem da base, o alvo e a semântica de cada variável.
3. Definir quais informações seriam admissíveis em cada cenário e quais linhas tinham rótulo para avaliação supervisionada.
4. Aplicar regras determinísticas por registro: grafias, números, datas, idade, IMC e sinalização de suspeitas.
5. Preservar a composição histórica do desenvolvimento e agrupar dependências, incluindo cópias brutas, antes de dividir para validação.
6. Dentro de cada treino, aprender preenchimentos, categorias e parâmetros de escala. Aplicar esses parâmetros às linhas de validação.
7. Treinar e escolher configurações de cada família nas divisões internas.
8. Gerar previsões nas divisões externas, reunir essas previsões e calcular as métricas.
9. Examinar erros, dependência de atributos, mudanças de cenário e incerteza.
10. Interpretar o alcance do resultado e registrar o que exige nova coleta ou confirmação da origem dos rótulos.

A diferença entre regra fixa e parâmetro aprendido é importante. Converter 51 cm em 0,51 m na fórmula do IMC não usa outras fichas. Calcular a mediana da FC usa um conjunto de fichas e precisa ocorrer apenas no treino. A escolha das próprias regras de curadoria teve influência da exploração anterior da coorte. Por isso, a separação interna reduz vazamento durante os ajustes, mas não produz uma validação externa totalmente independente de todo o desenvolvimento do trabalho.

**Fontes para conferir:** `src/kdd_revision/preprocessing/preparation.py`, `src/kdd_revision/preprocessing/transformer.py`, `src/kdd_revision/rubric_audit.py`, `config/a2_final_protocol_2026_11_16.json`.

## 2. Que dados usamos e o que significa o alvo

A base UCMF reúne fichas de cardiologia pediátrica do Real Hospital Português, em Recife. O arquivo original contém 12.873 registros e 21 colunas. Há 11.704 registros com alvo conhecido e 1.169 sem alvo conhecido. O alvo é a coluna `NORMAL X ANORMAL`. Na avaliação, Normal é 0 e Anormal é 1, a classe positiva.

A comparação final usa 9.361 registros de desenvolvimento, com 5.394 Normal e 3.967 Anormal. Isso corresponde a aproximadamente 57,62% e 42,38%. Portanto, o desequilíbrio existe, mas a classe positiva continua representando uma parcela grande da amostra.

Os 2.342 registros do teste histórico ficaram fora da avaliação final e um registro permaneceu em quarentena por equivalência. A conta é 9.361 + 2.342 + 1 = 11.704. O teste histórico já havia sido examinado e contém padrões brutos também presentes no desenvolvimento. Chamá-lo agora de teste intocado daria uma impressão incorreta. A execução final mantém a composição histórica e calcula sua estimativa com validação aninhada no desenvolvimento. Ela não utiliza as 2.342 linhas para obter a pontuação publicada.

A1 e A2 tratam as cópias de modo diferente. A A1 removeu 987 cópias exatas ao desconsiderar o ID, das quais 235 eram rotuladas e 752 não eram. A A2 preserva as linhas rotuladas e impede a separação de cópias entre treino e validação por agrupamento. A mudança precisa aparecer como decisão da A2, sem reescrever o que foi entregue na A1.

Uma previsão Anormal significa concordância prevista com a classificação registrada. A documentação disponível não estabelece de maneira suficiente quem definiu todos os rótulos, com quais exames, em que instante e com qual independência dos campos da ficha. Assim, erro do modelo significa desacordo com esse rótulo. A base sozinha não permite transformá-lo em diagnóstico clínico validado.

**Fontes para conferir:** `resultados/a2/revisao_final_2026_11_16/reviewed_results.json`, `docs/a2/Revisao_Final_A2.md`, `paper/a2_ieee_2026_11_07/sections/02_dados.tex`.

## 3. Seleção das 21 variáveis

A escolha de entradas parte da pergunta de uso e da disponibilidade das informações. Uma associação forte com o alvo pode ser útil para previsão, mas também pode surgir porque o campo participou da decisão que produziu o rótulo. Correlação e pontuação isoladas não resolvem essa diferença.

Os conjuntos finais são:

- **FISIO8, principal:** Peso, Altura, IMC, IDADE, PA SISTOLICA, PA DIASTOLICA, FC e SEXO.
- **STRICT4, sensibilidade:** Peso, Altura, IDADE e SEXO. Retira IMC e sinais vitais em conjunto.
- **CLINICO, exploratório:** as oito entradas principais mais PPA, SOPRO, B2, PULSOS e HDA 1.

Todos usam os mesmos registros e as mesmas divisões externas. STRICT4 permite observar o efeito da retirada conjunta de informação. Ele não isola o efeito de cada uma das quatro variáveis removidas. CLINICO mostra o efeito de acrescentar um bloco de achados. O ganho do bloco não comprova que cada variável seja utilizável no instante de uma futura previsão.

| Variável | Decisão final e tratamento | Motivo e limite da decisão |
|---|---|---|
| ID | Metadado para rastrear registros, fora de todos os modelos. | Um número de identificação pode codificar ordem ou coorte e facilitar memorização. A base não confirma uma chave longitudinal de paciente. |
| Peso | Entrada dos três cenários. Números em kg, zeros/negativos indisponíveis. Na matriz principal, peso menor que 1 kg e pares antropométricos muito incoerentes recebem máscara. | É uma medida básica. Não impusemos um teto automático de 150 kg na política revisada, pois um peso alto pode ser real. A regra abaixo de 1 kg continua sendo hipótese de curadoria, com limite para prematuros. |
| Altura | Entrada dos três cenários, em cm. Máscaras amplas abaixo de 40 ou acima de 200 cm, com exceção de 30 a menos de 40 cm para idade menor que 3 meses ou desconhecida. Também participa da verificação conjunta com Peso. | Evita tratar toda baixa estatura como erro. O código final não adivinha um fator de conversão de uma célula ambígua. A conversão cm/100 aparece no cálculo do IMC. |
| IMC | Entrada de FISIO8 e CLINICO, fora de STRICT4. Recalculado de peso e altura observados utilizáveis. Pode preservar um histórico positivo quando a reconstrução não é possível, com origem registrada. | Confere a fórmula e fornece uma razão útil ao modelo. É redundante com Peso/Altura e não deve ser interpretado como informação independente. Não é calculado a partir de pais preenchidos estatisticamente. |
| Atendimento | Fora dos preditores. Usado na derivação de idade e na auditoria. | A data pode refletir época e processos do serviço. Anos de dois dígitos podem deixar o século ambíguo. |
| DN | Fora dos preditores. Usado para calcular idade quando a interpretação permite. | A data de nascimento é detalhada e pode funcionar como quase identificador. Não confirma, combinada com sexo, a identidade de uma pessoa. |
| IDADE | Entrada dos três cenários, contínua em anos. Prioridade para idade relativa de datas coerentes, depois idade literal explícita e depois idade numérica válida informada. | A fisiologia e a distribuição de medidas mudam com a idade. Preservar a continuidade mantém resolução no primeiro ano. Fallback informado permanece identificado como não verificado. |
| Convenio | Fora de todos os modelos finais. Grafias podem ser normalizadas para auditoria. | É informação administrativa e pode refletir acesso, origem de encaminhamento e seleção da população. A exclusão não decorre de uma prova de vazamento direto. |
| PULSOS | Apenas CLINICO. Categorias nominais. | É um achado de palpação e aparece no material de investigação diagnóstica. Pode ter participado da referência. Não é a mesma variável que FC. |
| PA SISTOLICA | FISIO8 e CLINICO. Zeros/negativos indisponíveis. Máscara fora de 50 a 200 mmHg e nos pares em que PAS ≤ PAD. | Medida cardiovascular útil, mas com lacuna temporal e possível participação em diagnóstico de hipertensão. O limite é operacional, sem equivalência com normalidade clínica. |
| PA DIASTOLICA | FISIO8 e CLINICO. Zeros/negativos indisponíveis. Máscara em PAS ≤ PAD. A política revisada não apaga automaticamente toda PAD positiva fora do envelope histórico. | Uma PAD baixa isolada pode ser real. Na contradição PAS ≤ PAD, não sabemos qual dos dois campos errou, então ambos ficam indisponíveis para o modelo. |
| PPA | Apenas CLINICO, como categoria histórica. | Já é uma classificação de pressão arterial, derivada das medidas e de contexto pediátrico. Pode reconstruir um componente do alvo se hipertensão o integrar. Não produzimos um novo diagnóstico PPA usando medidas imputadas. |
| NORMAL X ANORMAL | Somente alvo y. Nunca entrada, preenchimento ou cálculo de atributos. | Usá-lo como preditor seria vazamento direto. Não inventamos rótulos para os registros sem resposta. |
| B2 | Apenas CLINICO, nominal. | Representa o segundo som cardíaco. Pode ter sido observado antes da classificação e também ter participado dela. A cronologia e a referência precisam de confirmação. |
| SOPRO | Apenas CLINICO, nominal. Ausência registrada é categoria distinta de campo vazio. | A associação é muito forte, mas o mecanismo pode incluir informação da referência. Não concluímos vazamento apenas a partir da associação. |
| FC | FISIO8 e CLINICO. Zeros/negativos indisponíveis. Intervalos numéricos reconhecidos usam ponto médio, com status de aproximação. FC maior que 500 recebe máscara de suspeita. | Não aplicamos o antigo teto de 220 como se toda taquicardia fosse erro. O corte 500 é um gatilho de curadoria desta base, sujeito a revisão. |
| HDA 1 | Apenas CLINICO. Categorias de sintomas e assintomático, normalizadas por grafia. | Sintomas podem preceder a investigação, mas o momento de registro e o papel na classificação são desconhecidos. Não equivale ao diagnóstico explícito de MOTIVO. |
| HDA2 | Fora dos três cenários finais. | Repete a incerteza temporal de HDA 1 e tem cobertura muito pequena, 12.466 dos 12.873 registros estão vazios na origem. Baixa cobertura não prova vazamento. |
| SEXO | Entrada dos três cenários, categórica. Grafias reconhecidas convergem para F/M. Código sem interpretação confirmada fica ausente e mantém rastreio. | Não há ordem numérica entre categorias. Não usamos o alvo nem medidas corporais para inferir sexo. |
| MOTIVO1 | Fora dos três cenários. | Inclui conteúdo diagnóstico explícito, como cardiopatia já estabelecida. O risco é alto para uma pergunta de primeira identificação. Excluímos a coluna inteira para evitar transferir a informação ao padrão de ausência. |
| MOTIVO2 | Fora dos três cenários. | Contém motivos com cardiopatia congênita/adquirida, além de sinais e suspeitas. Mesma cautela de MOTIVO1. |

### O cuidado que continua valendo para FISIO8

Excluir SOPRO, B2, PPA e os demais achados reduz uma fonte importante de incerteza, mas não comprova que FISIO8 esteja livre de toda incorporação. Por exemplo, PAS e PAD podem participar de uma classificação relacionada a hipertensão. Se essa classificação compôs o alvo, as medidas podem reconstruir parte de sua regra. Por isso, a interpretação de FISIO8 permanece condicionada à disponibilidade e ao papel dessas medidas. STRICT4 reduz essa dependência e oferece uma comparação mais restrita.

**Fontes para conferir:** `docs/a2/auditoria_2026_11_07/tabela_semantica_21.json`, `docs/a2/auditoria_2026_11_07/Parecer_Semantico_e_Decisoes.md`, `src/kdd_revision/rubric_audit.py` e `config/a2_final_protocol_2026_11_16.json`. As recomendações históricas da auditoria devem ser lidas junto do protocolo final, que define os três conjuntos efetivamente avaliados.

## 4. Limpeza, com as regras que precisam de justificativa

### 4.1 Padronização e ausência

Padronizar grafia significa retirar diferenças que não mudam o sentido, como espaços extras, caixa, acentos reconhecidos e separador decimal. Não significa juntar categorias semanticamente diferentes porque isso melhora a pontuação. Números com vírgula decimal são convertidos de modo explícito. Células vazias e sentinelas definidos por campo tornam-se ausentes. Valores não numéricos ou não finitos não entram como medidas.

Peso, altura e IMC iguais a zero são tratados como sentinelas de ausência. Medidas negativas e FC/pressões iguais a zero são inválidas para essa representação. Isso não autoriza tratar todo valor distante da média como errado. A política distingue valor observado, valor suspeito e valor estimado.

### 4.2 A frequência cardíaca de 1.120

Existe na base uma célula de FC com valor 1.120. A regra revisada marca FC acima de 500 como suspeita na matriz de modelagem. Assim, essa célula passa a ausente, enquanto a ficha e suas outras medidas continuam disponíveis. Não a corrigimos para 112, pois isso exigiria adivinhar o erro de digitação.

No ajuste final da floresta, a mediana da FC do desenvolvimento é 92. A representação dessa célula recebe então FC = 92 e indicador de preenchimento = 1. O indicador informa ao modelo que 92 é uma estimativa. Uma FC realmente observada de 92 teria indicador 0. Durante a validação cruzada, cada treino calcula a sua própria mediana, que pode ser diferente de 92.

Esse é um exemplo de dois passos distintos. **Limpeza:** decidir que a célula exige tratamento de suspeita. **Transformação:** converter a ausência numa entrada numérica utilizável pelo algoritmo. O resultado preenchido não é uma medição clínica recuperada.

### 4.3 Coerência entre variáveis

Se a pressão sistólica é menor ou igual à diastólica, há uma contradição operacional entre as duas medidas. Como não sabemos qual campo errou, mascaramos os dois para o modelo. Não trocamos automaticamente os valores nem escolhemos o que parece mais conveniente.

Peso e altura também precisam ser conferidos em conjunto. A relação Peso/(Altura/100)² fora de 5 a 100 aciona uma máscara conjunta de Peso, Altura e IMC. Essa é uma guarda ampla contra combinações muito incoerentes. Não identifica qual dos dois insumos está errado e não é uma faixa clínica de IMC normal. Os valores brutos permanecem preservados.

A política revisada evita alguns apagamentos excessivos da política histórica. Conserva pesos altos em vez de usar 150 kg como teto universal. Permite comprimentos de 30 a menos de 40 cm em crianças muito pequenas ou com idade desconhecida. Mantém FC positivas até 500 e não invalida uma PAD baixa apenas por estar fora do envelope antigo. Essas exceções procuram reduzir a remoção de extremos potencialmente reais. Elas ainda exigem validação clínica independente.

### 4.4 Idade e ambiguidade de datas

A idade precisa corresponder ao atendimento. Nunca usamos a data atual para recalculá-la. O método final calcula idade de calendário, levando em conta aniversários e duração do ano de vida. Quando o ano tem dois dígitos, conserva candidatos de século em vez de escolher silenciosamente um deles.

A idade relativa pode ser resolvida sob a hipótese de uma coorte pediátrica de 0 a menos de 20 anos quando as durações compatíveis diferem no máximo um dia. Isso permite aproveitar uma duração coerente sem afirmar que o século absoluto foi confirmado. Se a relação das datas não resolve a idade, a ordem de fallback é uma idade literal explícita no campo de nascimento e, depois, a idade numérica original entre 0 e menos de 20. O último caso permanece identificado como informação não verificada. Se nada é utilizável, a idade fica ausente e poderá ser preenchida no treino.

Conflitos e origens ficam registrados. Uma idade original fora do recorte não provoca, sozinha, a exclusão automática da ficha rotulada do conjunto principal. A disponibilidade de idade e as limitações da reconstrução continuam auditáveis.

### 4.5 IMC e arredondamento

Um exemplo real contém peso de 5 kg e altura de 51 cm. Para calcular IMC, primeiro usamos 0,51 m. Depois calculamos 5/(0,51²) = aproximadamente 19,22 kg/m². O valor histórico 19,0 não prova erro de medição, pois pode decorrer de arredondamento ou de outra precisão dos insumos.

A reconstrução só tem precedência quando peso e altura são observados e utilizáveis pela política de qualidade. Quando isso é inviável, um IMC histórico positivo pode ser preservado com sua origem registrada e sujeito às verificações da matriz. Se peso e altura precisaram de imputação estatística, não recalculamos IMC a partir deles. Essa operação fabricaria uma razão de estimativas que poderia parecer uma medida observada.

**Fontes para conferir:** `src/kdd_revision/prepare.py`, `src/kdd_revision/preprocessing/preparation.py`, `src/kdd_revision/schema.py`. Os envelopes em `schema.py` são históricos. As exceções revisadas efetivas estão em `quality_masks`, portanto não basta ler os limites antigos isoladamente.

## 5. Transformação e por que cada escolha importa

### 5.1 Mediana global ou por faixa etária

A mediana é o valor central das observações ordenadas. Ela é menos sensível a extremos que a média, mas preenche com uma estimativa simples e reduz a variabilidade dos valores ausentes. Não reproduz a incerteza de uma medida individual.

Comparamos mediana global do treino com mediana por faixas fixas de idade para Peso, Altura, IMC e FC. As faixas, em anos, são de 0 a menos de 0,25; de 0,25 a menos de 0,5; de 0,5 a menos de 1; de 1 a menos de 2; de 2 a menos de 5; de 5 a menos de 10; de 10 a menos de 15; e de 15 a menos de 20. Em linguagem simples, os primeiros limites separam três meses, seis meses e um ano. Cada faixa precisa de pelo menos 30 valores observados no treino para a variável. Caso contrário, ou quando a idade é desconhecida, usamos a mediana global. A idade usada para escolher a faixa é a disponível antes de sua imputação, para evitar uma cadeia circular de estimativas.

A idade e as pressões continuam com mediana global nessas alternativas. Não aplicamos automaticamente a opção por faixa a toda variável. O objetivo da alternativa por idade era respeitar diferenças de crescimento e fisiologia. A possibilidade de perder precisão com grupos pequenos e a distribuição desta base justificam comparar as duas estratégias dentro da validação.

A floresta final escolheu **mediana global**. A árvore e a logística finais escolheram **mediana por faixa** para os campos elegíveis. Assim, não existe uma única imputação vencedora para todos os modelos. A escolha veio da acurácia balanceada interna entre as configurações testadas. Isso não demonstra que uma mediana seja clinicamente a melhor estimativa para cada criança.

### 5.2 Indicadores de preenchimento

Cada variável numérica gera uma coluna binária com 1 para valor ausente ou mascarado e 0 para observado utilizável. Isso permite ao modelo distinguir uma estimativa de uma observação. Há uma contrapartida: o padrão de preenchimento pode revelar o processo de coleta. Uma árvore fixa usando apenas máscaras de disponibilidade alcançou 55,09% de BA em FISIO8. Portanto, parte do sinal pode estar na maneira como os campos foram coletados.

Retirar os indicadores também não apagaria toda informação de ausência. Muitos valores preenchidos ficam exatamente na mediana e o modelo pode reconhecer essa concentração. O controle de máscaras é diagnóstico do processo de coleta, sem prova de vazamento temporal.

### 5.3 Categorias em colunas binárias

One-hot cria uma coluna para cada categoria. No caso de SEXO, um registro F aciona a coluna F e um registro M aciona a coluna M. Evitamos atribuir códigos como F = 1 e M = 2 que poderiam sugerir uma distância ou ordem artificial. O vocabulário é aprendido no treino.

A representação final de SEXO conserva quatro possibilidades: F, M, ausência e categoria desconhecida na aplicação. A tabela dos slides mostra somente as duas categorias conhecidas para facilitar a leitura. Há uma diferença entre categoria original de sexo sem interpretação, que pode virar ausente na preparação semântica, e categoria não vista que aparece depois no transformador, que vai para o marcador desconhecido. Não são o mesmo mecanismo.

FISIO8 tem oito variáveis de origem, mas a matriz final tem **18 colunas**: sete medidas numéricas, sete indicadores numéricos e quatro colunas de SEXO. Essa expansão de representação não equivale a coletar 18 informações independentes.

### 5.4 Padronização e logaritmo

A logística combina contribuições numéricas e utiliza regularização. Se uma variável está em kg e outra em centímetros, a escala influencia a penalização dos coeficientes. A padronização transforma uma medida em (valor − média do treino)/desvio-padrão do treino. Uma unidade passa a corresponder a um desvio-padrão daquele treino. Na representação com log, aplicamos primeiro log(1 + Peso), que comprime diferenças da cauda de pesos altos, e depois padronizamos as medidas contínuas.

Comparamos logística padronizada nas unidades originais e logística com log do peso seguido de padronização. A logística final selecionou a segunda opção. Os indicadores e o one-hot permanecem 0/1, sem padronização. As árvores e a floresta usam as unidades originais, pois suas decisões dependem de cortes e não precisam da mesma equalização de escala.

Não aplicamos PCA, sobremostragem ou subamostragem na comparação final de 105 configurações. O projeto contém investigações e funções para alternativas adicionais, mas isso não as torna parte do procedimento final publicado. Pesos de classe foram comparados com pesos uniformes no treino.

**Fontes para conferir:** `src/kdd_revision/preprocessing/transformer.py`, `src/kdd_revision/mining.py`, `artifacts/a2_rubric_final/final_parameters_FISIO8_tree.json`, `artifacts/a2_rubric_final/final_parameters_FISIO8_logistic.json`, `artifacts/a2_rubric_final/final_parameters_FISIO8_forest.json`.

## 6. Por que esses modelos e quais ajustes testamos

### A referência majoritária

O DummyClassifier sempre escolhe a classe mais frequente do treino, que é Normal nas divisões usadas. Ele mostra o resultado de uma regra que dispensa as medidas. Se uma abordagem complexa não superar essa referência na métrica escolhida, sua utilidade preditiva nessa comparação fica sem sustentação.

### A árvore de decisão

A árvore aprende perguntas sucessivas, como “Peso é menor ou igual a 8,85 kg?”. Cada resposta encaminha a ficha a outro ramo até chegar a uma folha. A folha resume a distribuição de classes do grupo de treino, considerando os pesos usados. Isso ajuda a explicar como o modelo organiza as fichas e permite relações que mudam entre regiões dos dados.

Uma árvore profunda com folhas muito pequenas pode memorizar particularidades. Limitamos profundidade e tamanho mínimo de folha durante a busca. Gini e entropia são dois critérios para avaliar quanto uma divisão separa as classes. Comparamos profundidades 2, 4 e 6, folhas mínimas 20 ou 50, pesos uniformes ou balanceados e duas formas de imputação. A conta é 2 critérios × 3 profundidades × 2 folhas × 2 pesos × 2 imputações = 48 configurações.

A árvore FISIO8 ajustada ao final escolheu Gini, profundidade máxima 6, mínimo de 50 registros por folha, pesos balanceados e imputação por faixa etária. Seus primeiros cortes incluem Peso ≤ 8,85 kg, depois idade de aproximadamente 14 dias nesse ramo, ou FC ≤ 98,5 no outro. São cortes aprendidos nesta base, após preparação, e não limiares clínicos. O desempenho divulgado é o das previsões externas do procedimento de seleção, não o acerto dessa árvore sobre o mesmo treino.

### A regressão logística regularizada

A logística combina coeficientes associados às entradas e converte a soma numa estimativa entre 0 e 1. Uma contribuição muda a estimativa de Anormal, levando em conta as outras variáveis do modelo. Ela fornece uma referência com relação mais simples que as partições e interações de árvores. Coeficiente associado não estabelece causa.

A regularização restringe coeficientes para reduzir ajustes excessivos às particularidades da amostra. No parâmetro C, valores menores significam regularização mais forte. Comparamos C = 0,01, 0,1, 1 e 10, pesos uniformes/balanceados, duas imputações e duas representações. São 4 × 2 × 2 × 2 = 32 configurações. A logística final escolheu C = 1, pesos balanceados, mediana por faixa e log do Peso seguido de padronização. O limite de 5.000 iterações permite buscar convergência, sem significar que todas as execuções usaram exatamente esse número de passos.

### A floresta aleatória

A floresta reúne 150 árvores. Cada árvore aprende com uma amostra sorteada com reposição do treino e considera subconjuntos de atributos ao buscar divisões. Essa diversidade reduz a dependência de uma única árvore. O classificador combina as probabilidades das árvores por média para produzir a estimativa final.

Comparamos profundidades máximas 4, 8 ou sem limite explícito, folhas mínimas 10 ou 30, pesos uniformes/balanceados e duas imputações. São 3 × 2 × 2 × 2 = 24 configurações. O número de 150 árvores ficou fixo nessa grade. Logo, não demonstramos que 150 seja o número ótimo.

A floresta FISIO8 final selecionou profundidade sem limite explícito, pelo menos 30 registros por folha, pesos balanceados, mediana global e medidas nas unidades originais. Sem limite de profundidade não significa ausência de controle: o tamanho mínimo de folha restringe o crescimento. A grade é finita, portanto o resultado é o melhor encontrado entre alternativas declaradas sob esse procedimento, sem prova de ótimo universal.

### Pesos e limiar

Pesos balanceados aumentam a contribuição relativa da classe menos frequente no ajuste. Não criam novos pacientes nem garantem que as duas taxas de erro se igualem. A escolha entre pesos uniformes e balanceados ocorre na validação interna.

A estimativa de Anormal vira classe com limiar fixo de 0,5: p ≥ 0,5 produz Anormal. O limiar não foi otimizado para uma decisão médica. Reduzi-lo tenderia a recuperar mais Anormal, com aumento de positivos entre Normal. Esse compromisso precisaria de uma regra de uso, custos definidos e validação adequada antes de qualquer aplicação.

**Fontes para conferir:** `src/kdd_revision/rubric_audit.py` (`search_space`), `src/kdd_revision/mining.py` e arquivos `final_parameters_FISIO8_*` da execução final.

## 7. Como escolhemos ajustes sem avaliar no mesmo material

Validação cruzada significa dividir o conjunto em partes e alternar o papel de cada parte. A aninhada acrescenta uma separação entre escolher configurações e medir desempenho.

No nível externo, usamos cinco partes. Em uma rodada, quatro partes formam o treino externo e a quinta fica para avaliação externa. Dentro das quatro, três partes internas comparam as configurações. Escolhemos uma configuração **por família** pela média da BA interna. Reajustamos cada vencedora nas quatro partes externas e produzimos previsões na quinta. Repetimos até todas as partes terem passado pela avaliação externa. Cada registro tem uma previsão externa por família e cenário.

A grade tem 105 configurações por cenário: 1 referência, 48 árvores, 32 logísticas e 24 florestas. Isso não quer dizer 105 algoritmos diferentes. Tampouco significa que a quinta parte externa serviu para escolher o melhor ajuste. Medianas, vocabulários, médias e desvios também são aprendidos novamente dentro do respectivo treino.

A estratificação procura manter proporções de classes próximas. O agrupamento mantém dependências conhecidas na mesma parte. São 9.166 componentes, construídos pela união de grupos históricos e linhas com todos os campos brutos iguais ao excluir ID e alvo da comparação. O alvo não determina se duas linhas são cópias. Existem três assinaturas brutas, com 110 registros, que apresentam rótulos discordantes. Mantivemos essa divergência e agrupamos seus registros, pois escolher o rótulo “correto” exigiria evidência adicional.

Nenhuma assinatura exata cruza os folds finais. Isso reduz uma forma de contaminação, mas não comprova separação por paciente: os componentes são aproximações e a base não confirma identidade longitudinal. Após avaliar os procedimentos, uma seleção final em cinco partes de todo o desenvolvimento escolhe os parâmetros de cada modelo para ajuste final. As métricas desse ajuste sobre seu próprio treino são descritivas e não substituem as previsões externas.

Usamos sementes declaradas para repetir os sorteios: estimadores com 42, partes externas com 743, internas com 811 + k e seleção final com 43. A semente permite reproduzir uma execução. Sozinha, não demonstra estabilidade em todas as divisões possíveis.

**Fontes para conferir:** `src/kdd_revision/rubric_audit.py`, `src/kdd_revision/full_kdd.py`, `config/a2_final_protocol_2026_11_16.json`, `docs/a2/Revisao_Final_A2.md`.

## 8. Métricas, com um cálculo usando o resultado real

### A matriz primeiro

Anormal é a classe positiva. Na floresta FISIO8, a matriz externa é:

| Rótulo registrado | Previu Normal | Previu Anormal | Total real |
|---|---:|---:|---:|
| Normal | 3.687 verdadeiros negativos (TN) | 1.707 falsos positivos (FP) | 5.394 |
| Anormal | 1.659 falsos negativos (FN) | 2.308 verdadeiros positivos (TP) | 3.967 |
| Total previsto | 5.346 | 4.015 | 9.361 |

Falso negativo é a ficha Anormal que recebeu previsão Normal. Falso positivo é a ficha Normal que recebeu previsão Anormal. “Positivo” aqui identifica a classe usada no cálculo, sem confirmar doença por uma referência clínica independente.

### As métricas e as perguntas que respondem

| Métrica | Pergunta e cálculo | Floresta FISIO8 | Papel na análise |
|---|---|---:|---|
| Sensibilidade, recall | Dos Anormal, quantos recuperamos? TP/(TP+FN) = 2.308/3.967. | 58,18% | Mostra Anormal que deixamos passar. |
| Especificidade | Dos Normal, quantos reconhecemos? TN/(TN+FP) = 3.687/5.394. | 68,35% | Mostra o outro lado dos erros. |
| Acurácia balanceada, BA | Média da sensibilidade e especificidade. | 63,27% | Critério principal de seleção e comparação, com mesmo peso para as duas classes. |
| Precisão da classe Anormal | Das previsões Anormal, quantas concordam com o rótulo? TP/(TP+FP) = 2.308/4.015. | 57,48% | Quantifica a confiabilidade das previsões positivas nesta população. |
| F1 | Média harmônica entre precisão e sensibilidade: 2TP/(2TP+FP+FN). | 57,83% | Resume as duas taxas focadas na classe positiva, sem incluir TN diretamente. |
| Acurácia comum | Fração total de acertos: (TP+TN)/N = 5.995/9.361. | 64,04% | Complementar. A composição das classes influencia seu valor. |
| ROC-AUC | Quão bem a ordenação de escores separa Normal e Anormal ao variar limiares? | 0,6718 | Complementar da execução. Não é a porcentagem de acertos no limiar 0,5. |
| Precisão média, AP | Resume a precisão ao recuperar parcelas crescentes dos Anormal, variando o limiar. | 59,51% | Avalia a ordenação focada na classe positiva. A prevalência é referência relevante. |
| Brier | Média de (probabilidade prevista − alvo 0/1)². Menor é melhor. | 0,2274 | Complementar da execução para qualidade probabilística. Não demonstra calibração adequada por si só. |

A conta central é BA = (58,1799849% + 68,3537264%)/2 = 63,2668556%, arredondada para 63,27%. Use as taxas sem arredondar no cálculo. A média de 58% e 68% é apenas uma explicação aproximada.

A referência sempre Normal recupera 100% dos Normal e 0% dos Anormal. Sua acurácia comum é 57,62%, mas BA = (100% + 0%)/2 = 50%. Essa é a razão mais intuitiva para adotar BA. Igualar o peso das classes não equivale a definir os custos de um protocolo clínico.

As métricas do artigo são BA, sensibilidade, especificidade, precisão, F1, AP e contagens da matriz. A execução também calcula acurácia comum, ROC-AUC e Brier. Elas devem ser identificadas como complementares quando citadas. Não escolhemos modelos por todas ao mesmo tempo. A seleção interna usa média da BA. O resultado principal reúne as previsões externas de todos os folds; a BA reunida pode diferir levemente da média simples das cinco BAs externas.

A precisão e a AP dependem da composição de classes e da população. Uma AP de 59,51% deve ser comparada com a prevalência de aproximadamente 42,38% nesse conjunto, sem tratar a prevalência como garantia universal de desempenho futuro. As probabilidades foram avaliadas, mas não estabelecemos uma calibração clínica independente. Pesos balanceados também podem influenciar sua interpretação probabilística.

### Por que não usamos só F1 ou ROC-AUC

F1 favorece a leitura da classe positiva e não dá peso explícito aos verdadeiros negativos. ROC-AUC avalia ordenação em muitos limiares e não informa diretamente quantos registros passam como Normal no limiar fixado. Como a pergunta experimental exigia comparar reconhecimento das duas classes, BA foi o critério principal. As outras métricas mostram aspectos que BA sozinha esconde.

**Fontes para conferir:** `src/kdd_revision/experiments.py` (`metric_dict`), `src/kdd_revision/mining.py` (`metric`) e `resultados/a2/revisao_final_2026_11_16/reviewed_results.json`.

## 9. Resultados, importância e o que podemos concluir

### Comparação principal

| Modelo em FISIO8 | BA externa |
|---|---:|
| Sempre Normal | 50,00% |
| Árvore de decisão | 61,69% |
| Regressão logística | 62,03% |
| Floresta aleatória | 63,27% |

A floresta teve o maior valor da comparação principal. Ela supera a logística em 1,24 ponto percentual. O intervalo pareado de 95% dessa diferença é de 0,43 a 2,01 pontos, condicionado aos ajustes já feitos. A BA da floresta tem intervalo de 62,07 a 64,39%. A vantagem é modesta. O resultado não demonstra que florestas sejam universalmente superiores nem que esse modelo esteja pronto para uso clínico.

A floresta ainda deixa passar 1.659 dos 3.967 Anormal, aproximadamente 42 em cada 100. Entre os Normal, 1.707 de 5.394 recebem previsão Anormal, aproximadamente 32 em cada 100. Entre os Anormal com idade válida, a mediana de idade é 6,51 anos nos falsos negativos e 0,59 ano nos verdadeiros positivos. Isso orienta a investigar desempenho por idade em novos dados, sem provar uma causa dos erros.

### Sensibilidade às entradas

STRICT4 obteve maior BA numérica com a árvore, 59,55%. Os intervalos pareados entre suas famílias incluem zero, então não sustentam uma preferência clara entre elas. CLINICO chega a aproximadamente 91,92%, com árvore, logística e floresta muito próximas. Esse salto exige estudar o papel dos achados, não apenas escolher o cenário de maior pontuação.

Nos registros com sopro explicitamente ausente, 587 de 5.814 têm rótulo Anormal, cerca de 10,1%. Nos registros com sopro presente, 3.375 de 3.529 têm rótulo Anormal, cerca de 95,6%. Dezoito registros sem status conhecido ficam fora dessa comparação entre presença e ausência explícitas. Dizer “sem sopro” quando o campo está vazio misturaria ausência de informação com observação negativa.

Esses números são compatíveis com informação preditiva forte. Não esclarecem se o achado precedeu uma referência independente, participou da classificação ou ambas as coisas. Mesmo um campo registrado antes do laudo pode ter sido usado para produzir esse laudo. A cronologia é necessária, mas a independência do padrão de referência também importa.

### Importância por permutação

Na validação externa, embaralhamos uma variável entre as fichas, preservando o modelo e as transformações do treino, e medimos a queda na BA. Repetimos três vezes por variável em cada um dos cinco folds. A queda média indica quanto o procedimento depende daquela informação na configuração avaliada.

Na floresta FISIO8, as maiores quedas são aproximadamente 4,80 pontos para FC, 2,76 para Peso e 1,40 para IDADE. Na árvore CLINICO, SOPRO produz queda de 38,57 pontos e B2, 3,21. A diferença é em pontos percentuais de BA, não em porcentagem de importância ou efeito clínico.

Permutar Peso sem recalcular IMC pode criar combinações pouco realistas, pois os campos têm dependência. A idade também participa da alternativa de imputação por faixa. Como a permutação ocorre antes de reaplicar o transformador, a medida de dependência inclui efeitos indiretos de representação e preenchimento. A correlação entre campos pode repartir ou esconder importância. Portanto, essa análise descreve dependência do procedimento e não causalidade, relevância médica universal ou prova de vazamento.

### Incerteza e controles

O bootstrap sorteia 2.000 conjuntos de componentes com reposição e recalcula as métricas das previsões externas já existentes. A comparação é pareada, pois cada sorteio usa os mesmos componentes para os modelos comparados. Reamostrar componentes preserva mais dependência que sortear linhas isoladas. Os intervalos percentis de 95% continuam condicionados aos folds e modelos ajustados: não incluem a variabilidade de um novo treinamento ou de outra população.

O desvio-padrão entre os folds descreve a variação observada. Os treinos desses folds se sobrepõem. Por isso, não tratamos as cinco pontuações como cinco observações independentes para criar um erro-padrão ingênuo.

Um controle com rótulos permutados e árvore fixa ficou próximo de BA 50%, 49,68% em FISIO8. Isso indica ausência de sinal útil naquele controle específico. Não é um teste formal de permutação com muitas repetições nem uma prova de inexistência de vazamento. O controle de máscaras, já descrito, mostra que a disponibilidade dos campos também carrega informação do processo de coleta.

**Fontes para conferir:** `resultados/a2/revisao_final_2026_11_16/reviewed_results.json`, `src/kdd_revision/evaluation_stats.py`, `src/kdd_revision/rubric_audit.py`, `paper/a2_ieee_2026_11_07/sections/04_resultados.tex`.

## 10. Limitações que precisamos conseguir explicar

A limitação central é a definição e a origem do rótulo. Sem o protocolo de referência, não conseguimos garantir independência entre todas as entradas e a resposta. Os grupos também não comprovam pacientes distintos. A base foi explorada antes da avaliação final, e o teste histórico já foi visto. Além disso, pressão sistólica e diastólica têm cerca de 56% de ausência ou máscara em cada campo no desenvolvimento, o que torna a imputação e a coleta relevantes para a interpretação.

O resultado mede concordância dentro dessa coorte e do procedimento especificado. Ainda precisamos confirmar a referência, os instantes de coleta, a identidade longitudinal, os critérios de inclusão e a estabilidade em novas fichas. Uma nova avaliação deveria ser definida antes de observar os novos resultados e acompanhar subgrupos e calibração, se o objetivo futuro exigir probabilidades.

A frase “foi a melhor opção” precisa vir acompanhada do escopo: melhor entre as configurações da grade pelo critério declarado. A frase “isso é vazamento” precisa vir acompanhada da evidência: alvo como entrada é vazamento direto, enquanto sopro e B2 continuam sob suspeita sem protocolo suficiente. Essa precisão torna a defesa mais forte que prometer certeza onde os dados não a oferecem.

## 11. Perguntas para ensaiar e respostas curtas

As respostas abaixo são pontos de partida para falar com naturalidade. Depois de cada uma, tente explicar um exemplo e o limite sem ler.

### Dados e seleção

**1. Qual é o objetivo do trabalho?**

Estimar quanto os dados da ficha ajudam a prever o rótulo Normal ou Anormal registrado. Fizemos o processo completo de KDD, incluindo auditoria semântica, preparação, modelagem e avaliação. O alvo disponível permite avaliar concordância com o registro.

**2. Por que não usar os 12.873 registros no treino supervisionado?**

Porque 1.169 não têm alvo conhecido. Não inventamos respostas para eles. Dos rotulados, mantivemos a composição histórica e deixamos o teste já exposto fora da comparação final, usando 9.361 no desenvolvimento e validação aninhada.

**3. Por que excluir os motivos de encaminhamento?**

Porque incluem diagnósticos já estabelecidos. Para estudar uma previsão sem antecipar a resposta por esse conteúdo, retiramos MOTIVO1 e MOTIVO2 inteiros dos três cenários. A decisão depende da pergunta de uso, mas é conservadora para primeira identificação.

**4. Sopro é comprovadamente vazamento?**

A documentação não permite afirmar isso. Ele está fortemente associado ao rótulo e aparece no material diagnóstico. Pode ter participado da referência, ou pode ser um achado útil anterior a uma referência independente. Por isso, ficou somente no cenário exploratório.

**5. Se sopro veio antes do diagnóstico, resolveu o problema?**

Ainda precisamos saber se o diagnóstico usou o próprio sopro como parte da referência. Disponibilidade temporal e independência da referência são perguntas diferentes. As duas afetam a interpretação do modelo.

**6. Por que manter a pressão e retirar PPA?**

PPA já é uma classificação derivada e tem risco mais direto de reconstruir um diagnóstico. As medidas brutas entraram no conjunto principal com ressalva, e STRICT4 retira também as pressões, FC e IMC em conjunto. Não afirmamos que manter as medidas elimina todo risco de incorporação.

**7. Por que excluir convênio e ID?**

ID ajuda a rastrear dados, mas pode codificar ordem e memorização. Convênio pode representar acesso e seleção do serviço. Não são medidas do estado do paciente e poderiam prejudicar a interpretação e a transferência para outra população.

### Limpeza

**8. O que foi efetivamente limpo?**

Padronizamos grafias, decimais e sentinelas, tratamos medidas inválidas, verificamos datas, reconstruímos idade e IMC com origem registrada e aplicamos máscaras de suspeita por regras individuais e de coerência entre campos. Preservamos o bruto e o restante da ficha.

**9. Por que não excluir a linha que tem FC 1.120?**

Porque outras medidas da mesma ficha podem ser aproveitáveis. Marcamos só a célula suspeita, preenchemos depois com estatística do treino e guardamos indicador. Excluir a linha poderia remover informação e selecionar a população de forma adicional.

**10. Por que não corrigir 1.120 para 112?**

Não temos evidência de que esse foi o erro de digitação. Qualquer escolha de dígitos seria uma suposição forte. Preferimos registrar a suspeita e conservar o bruto.

**11. De onde veio o limite de FC 500?**

É um gatilho operacional de curadoria desta base, escolhido para preservar extremos menores que poderiam ser reais. Não é um limite clínico de normalidade e precisa de revisão especializada. O modelo final usa essa hipótese declarada.

**12. Por que não apagar todo peso acima de 150 kg ou toda FC acima de 220?**

Porque um extremo pode representar um caso real. A revisão retirou esses tetos automáticos na política principal para reduzir apagamento excessivo, mantendo sinalização e regras mais amplas de curadoria.

**13. O que acontece se PAS é menor que PAD?**

Os dois campos ficam indisponíveis na matriz porque a relação é contraditória para a representação adotada e não sabemos qual valor está errado. Não trocamos as posições automaticamente.

**14. Vocês decidiram que IMC fora de 5 a 100 é clinicamente anormal?**

Não. Esse intervalo é uma guarda ampla para avaliar coerência de Peso e Altura. Fora dele, mascaramos o trio sem atribuir o erro a um campo específico. Normalidade clínica exigiria referências pediátricas e avaliação apropriadas.

**15. Por que usar a data do atendimento para idade?**

O modelo precisa da idade naquele encontro. Usar a data atual criaria uma característica temporalmente errada. Quando o século é ambíguo, conservamos a incerteza e só aproveitamos a idade relativa se a regra pediátrica permitir.

### Transformação

**16. Por que mediana em vez de média?**

A mediana é menos influenciada por valores extremos e fornece uma base simples de preenchimento. Ela continua sendo estimativa, reduz variabilidade e pode esconder diferenças individuais. Por isso, mantivemos o indicador e comparamos estratégias dentro do treino.

**17. A mediana era a mesma para toda criança?**

Na alternativa global, sim, para uma dada variável e treino. Na alternativa por faixa, Peso, Altura, IMC e FC podem usar medianas específicas de idade, se houver pelo menos 30 observações. Caso contrário, voltam à global. A floresta final selecionou global.

**18. Por que a floresta escolheu global se idade parece mais sensata?**

Uma hipótese fisiologicamente plausível não garante melhor resultado preditivo nessa amostra. Comparamos as opções pela BA interna. A escolha é do procedimento para essa família, sem demonstrar que global recupere melhor a medida verdadeira de cada paciente.

**19. O valor 92 veio de todas as fichas, inclusive as avaliadas?**

O 92 dos slides é a mediana do ajuste final em todo o desenvolvimento, usado apenas para ilustrar a representação. Nas previsões externas que produziram as métricas, cada treino calculou sua própria mediana sem usar a parte avaliada.

**20. Por que guardar indicador se já preencheu?**

Para distinguir uma observação real de uma estimativa. Uma FC observada de 92 tem indicador 0 e uma ausência preenchida com 92 tem indicador 1. O padrão de coleta pode carregar informação, então examinamos também esse risco.

**21. Por que recalcular IMC antes de preencher peso e altura?**

Porque a fórmula usa medidas observadas utilizáveis. Recalculá-lo depois de imputar os pais daria uma razão entre estimativas e poderia parecer informação medida. Quando necessário, o IMC recebe seu próprio preenchimento.

**22. Por que one-hot em sexo e achados?**

As categorias não têm distância numérica definida. Criar uma coluna binária por categoria evita uma ordem artificial. O vocabulário vem do treino e mantém ausência e desconhecido separadamente.

**23. Por que padronizar logística e não a floresta?**

A escala afeta a penalização dos coeficientes da logística. Padronizar põe as medidas em unidades de desvio-padrão. Árvores fazem cortes por atributo e podem trabalhar nas unidades originais. Os indicadores 0/1 continuam sem escala adicional.

**24. Por que logaritmo do peso?**

Foi uma alternativa para comprimir a cauda de pesos altos antes da padronização. A logística final escolheu essa representação na validação. Não aplicamos log automaticamente a todas as variáveis nem à floresta final.

### Modelos e validação

**25. Por que escolher árvore, logística e floresta?**

A árvore permite acompanhar perguntas e partições. A logística oferece uma comparação regularizada de relação mais simples. A floresta combina árvores variadas para capturar relações mais complexas. A referência majoritária mostra o que acontece sem usar as medidas.

**26. Por que 150 árvores?**

Foi uma escolha fixa da grade para obter um conjunto de árvores com custo viável. Testamos outras dimensões, como profundidade e folha, mas não demonstramos que 150 seja ótimo. É preciso declarar esse alcance.

**27. O que significa mínimo de 30 fichas por folha?**

Uma região final de uma árvore precisa conter pelo menos esse número de registros de treino. Isso dificulta decisões apoiadas em grupos muito pequenos e restringe memorização. Não garante ausência de sobreajuste.

**28. Sem limite de profundidade não sobreajusta?**

Pode sobreajustar. Na floresta final, a folha mínima de 30 ainda restringe o crescimento, e a escolha passou pela validação interna. O desempenho externo é o que usamos para verificar a capacidade observada de generalização.

**29. O que faz o peso balanceado?**

Aumenta a contribuição relativa da classe menos frequente na função de treino. Não altera o número de registros nem garante taxas iguais. Comparamos seu efeito com pesos uniformes.

**30. Foram 105 modelos independentes?**

Foram 105 configurações por cenário, incluindo uma referência e combinações de ajustes de três famílias. Cada divisão interna reajusta as transformações e os estimadores. A seleção ocorre por família, antes da avaliação externa.

**31. Por que validação aninhada?**

Escolher a configuração e medir sua qualidade na mesma validação favoreceria a opção que se ajustou às particularidades daquela divisão. O nível interno escolhe ajustes e o externo avalia o procedimento em fichas separadas desse ajuste.

**32. As mesmas pessoas ficaram fora do treino?**

Conseguimos garantir que componentes e assinaturas brutas idênticas ficaram juntos. A base não confirma uma identidade longitudinal de paciente, então não podemos garantir separação de todas as pessoas. Essa é uma limitação registrada.

**33. Por que não usar o teste histórico?**

Porque já havia sido examinado e contém padrões que aparecem também no desenvolvimento. Não seria honesto tratá-lo como intocado. A pontuação final vem da validação aninhada agrupada, e uma avaliação externa futura exigiria novas fichas.

### Métricas e interpretação

**34. Por que acurácia balanceada?**

Ela é a média da recuperação de Anormal e do reconhecimento de Normal. A referência sempre Normal acerta 57,62% no total, mas zero Anormal e BA 50%. A BA impede que o maior tamanho de uma classe esconda o fracasso completo na outra.

**35. Sensibilidade e precisão são iguais?**

Não. Sensibilidade pergunta quantos Anormal foram recuperados entre os Anormal reais. Precisão pergunta quantos eram Anormal entre as previsões Anormal. Aqui são 58,18% e 57,48%, respectivamente.

**36. O que significa 63,27% de BA?**

É a média entre sensibilidade 58,18% e especificidade 68,35%. Não é a chance individual de uma ficha estar correta nem a fração total de acertos. A acurácia comum foi 64,04%.

**37. Por que o cenário de 92% não é o principal?**

Porque inclui achados cujo papel na criação do rótulo e momento de disponibilidade estão incompletamente documentados. O valor é um resultado exploratório útil para estudar dependência. Escolher apenas a maior pontuação ignoraria essa incerteza semântica.

**38. O que a importância por permutação prova?**

Mostra quanto a pontuação do procedimento cai ao embaralhar uma entrada. Não prova causalidade ou vazamento. Pode sofrer influência de correlações, relações derivadas e combinações pouco realistas geradas pelo embaralhamento.

**39. O intervalo da diferença exclui zero. A floresta é sempre melhor?**

O intervalo favorece a floresta sobre a logística nesta comparação condicional. Ele reamostra componentes das previsões já produzidas e não inclui novos treinos ou outra população. A vantagem observada é de 1,24 ponto percentual, sem superioridade universal.

**40. Vocês otimizaram o limiar para não perder Anormal?**

Não. Fixamos 0,5 para a comparação. Diminuir o limiar alteraria sensibilidade e falsos positivos. Escolher um limiar de uso exigiria definir custos e validar essa escolha em material separado.

**41. O modelo aprendeu doença ou o processo de preenchimento?**

A base pode conter ambos os sinais. O ensaio com máscaras mostrou BA 55,09% em FISIO8, indicando associação da disponibilidade com o rótulo. Isso pede cuidado com coleta e transportabilidade, sem estabelecer sozinho a origem de todo o sinal.

**42. O controle com rótulos embaralhados provou ausência de vazamento?**

Não. Ele ficou próximo de 50% de BA, como esperado para aquele controle fixo, mas não cobre todos os mecanismos possíveis. Não usamos esse resultado como certificado de segurança semântica.

**43. Quais melhorias novas seriam prioritárias?**

Documentar como o rótulo foi criado e quando cada campo ficou disponível, confirmar a identidade longitudinal e avaliar em novas fichas. Depois, estudar erros por subgrupo, calibração e limiar de decisão conforme uma finalidade definida. Aumentar a complexidade do algoritmo sozinho não resolve essas lacunas.

**44. Qual é a principal conclusão que você defenderia?**

As medidas básicas e fisiológicas apresentam informação preditiva, com ganho modesto e muitos erros na comparação principal. Os achados do exame elevam muito a concordância com o rótulo e exigem esclarecer sua participação na referência. O conhecimento obtido inclui tanto o desempenho quanto as condições que limitam sua interpretação.

## 12. Como estudar para a arguição

Primeiro, explique em voz alta a história de uma célula: FC 1.120, máscara, mediana aprendida no treino e indicador. Depois, explique o IMC de 5 kg e 51 cm. Esses exemplos verificam se você distingue limpeza, derivação e imputação.

Em seguida, desenhe cinco partes e explique o que acontece dentro de quatro delas. Você precisa conseguir dizer de onde vem cada parâmetro sem consultar o roteiro. Depois, reconstrua sensibilidade, especificidade e BA a partir da matriz, começando pelos denominadores.

Por fim, faça uma rodada com as perguntas 4, 5, 19, 32, 37 e 39. Elas verificam os limites mais importantes. Uma resposta forte reconhece a evidência e a lacuna, sem transformar uma hipótese em fato. Se uma pergunta exigir um protocolo clínico que a fonte não fornece, explique o que está documentado e o que seria necessário confirmar.

O objetivo do ensaio é conseguir reconstruir o raciocínio. Decorar apenas nomes de algoritmos e porcentagens deixa as decisões sem sustentação.
