# Pedro: estudo e apresentação dos slides 1 a 6

Sua parte abre a apresentação e explica por que a base entregue aos modelos merece ser analisada com cuidado. Você apresenta introdução, dados, seleção das fichas e das variáveis, limpeza e preenchimento. O roteiro estima 3min35s de fala; isso precisa ser confirmado em ensaio. Antônio continua no slide 7, com os atributos derivados e os modelos.

## Como estudar este material

Primeiro entenda cada decisão. Depois pratique explicá-la com suas palavras. Só então use as falas sugeridas para controlar a sequência e o tempo. Decorar frases sem compreender a razão deixa você vulnerável quando o professor muda a pergunta.

Para cada decisão, consiga completar quatro frases: “fizemos isto”; “porque havia este problema”; “implementamos desta maneira”; “ainda existe esta limitação”. Na exposição, use a explicação curta. Na arguição, aprofunde conforme a pergunta. Os exemplos e respostas deste guia são material de estudo; não devem ser todos acrescentados aos 3min35s.

As falas destacadas abaixo reproduzem o roteiro atual. O conteúdo inteiro de cada slide deve aparecer na explicação, mas você não precisa ler cada palavra da tela. Aponte a evidência, explique a relação e volte o olhar para a plateia.

## A lógica que você precisa dominar

KDD significa descoberta de conhecimento em bases de dados. A sequência do trabalho é selecionar, limpar, transformar, modelar e interpretar. Selecionar decide quais fichas e informações podem entrar. Limpar trata representações e inconsistências. Transformar constrói entradas utilizáveis, como idade, indicadores e preenchimentos. Modelar aprende relações. Avaliar e interpretar examina os acertos, os erros e o alcance da conclusão.

Sua missão é preparar essa história. Uma frequência cardíaca registrada como 1.120 exemplifica a ligação: primeiro a limpeza marca a medida suspeita; depois a transformação preenche a ausência usando o treino. Isso não recupera o valor verdadeiro. Essa distinção conecta seus slides à parte do Antônio.

## Slide 1: abrir com clareza

**Mensagem central:** apresentar o grupo e situar o trabalho como um processo completo, do preparo da base à interpretação.

O relatório da A1 já foi entregue e permanece preservado. As melhorias e a conclusão do KDD pertencem à A2. Não é necessário contar toda essa história na abertura, mas você precisa compreendê-la caso o professor pergunte.

**Fala sugerida, igual ao roteiro:**

> Boa tarde. Somos o grupo 3: Antônio Henrique, João Vitor, Mateus Nery e Pedro Matos, do INF da UFG. Apresentamos a segunda avaliação de Mineração de Dados, com o professor Rogério Salvini, neste semestre. O estudo de registros cardíacos pediátricos percorre seleção, limpeza, transformação, comparação dos modelos e interpretação dos resultados.

**Como apresentar:** comece olhando para a plateia. Diga os nomes com calma, situe disciplina e avaliação, e use a última frase para anunciar a sequência. A capa não exige explicação de números ou métodos; evite gastar tempo antecipando todos os resultados. A referência do roteiro é 23 segundos.

**Se o professor perguntar “qual é o objetivo?”:** “Prever a classificação Normal ou Anormal registrada nas fichas e avaliar quanto o desempenho depende das informações disponíveis.” Isso delimita a tarefa sem prometer diagnóstico validado.

**Ligação com o próximo slide:** a pergunta sobre as medidas e o rótulo será explicada junto da origem da base.

## Slide 2: explicar a tarefa

**Mensagem central:** aprendemos a prever uma resposta registrada a partir de informações da ficha.

Imagine uma planilha: cada linha representa um registro e cada coluna descreve um campo. Há 21 campos originais, incluindo o alvo. Isso não significa 21 entradas no modelo. O alvo é a resposta usada para ensinar e avaliar, e nunca entra como informação preditora.

“Supervisionada” significa que o treino tem exemplos com a resposta conhecida. “Positiva” é a convenção de cálculo para Anormal, não uma afirmação de confirmação clínica. Também não sabemos se todas as linhas correspondem a pessoas distintas: uma criança pode aparecer em mais de um registro, mas a base não permite confirmar perfeitamente essa identidade.

**Fala sugerida, igual ao roteiro:**

> A base UCMF reúne 12.873 fichas de cardiologia pediátrica do Real Hospital Português, em Recife, com 21 atributos. A pergunta é se as medidas registradas ajudam a prever a classificação Normal ou Anormal. É uma tarefa de classificação supervisionada: aprendemos com fichas cuja resposta já está registrada. Consideramos Anormal a classe positiva, que queremos reconhecer. Estamos prevendo esse registro, sem afirmar que o modelo confirme um diagnóstico independente. Também falamos em fichas, pois a base não comprova que cada linha corresponda a uma criança diferente.

**Como apresentar:** aponte primeiro o total e a origem, depois a relação entre entradas e resposta. Dê ênfase a “rótulo já registrado”. Não passe rapidamente pela distinção entre ficha e paciente. Referência: 38 segundos.

**Pergunta provável: “Então vocês diagnosticam cardiopatias?”** “Avaliamos concordância com a classificação registrada. Falta uma referência independente suficientemente documentada para afirmar diagnóstico validado.”

**Ligação:** depois de conhecer a base original, a plateia precisa entender quais linhas realmente participaram da avaliação.

## Slide 3: explicar as contagens

**Mensagem central:** o número avaliado resulta de decisões rastreáveis, e as repetições precisam permanecer juntas.

Reconstrua a conta antes de ensaiar: 12.873 = 11.704 com rótulo + 1.169 sem rótulo. Depois, 11.704 - 2.342 - 1 = 9.361 registros de desenvolvimento. Finalmente, 5.394 Normal + 3.967 Anormal = 9.361. As linhas sem resposta não permitem comparar previsão e alvo nesta avaliação supervisionada; continuam preservadas na fonte.

O teste histórico já havia sido examinado. Reutilizá-lo como se fosse intocado daria uma impressão incorreta de independência. A ficha em quarentena tinha equivalência candidata com esse conjunto. Entre os registros de desenvolvimento, 9.166 grupos candidatos mantêm dependências conhecidas juntas. Grupo não é sinônimo de paciente.

**Fala sugerida, igual ao roteiro:**

> Preservamos a fonte original. Das 12.873 fichas, 11.704 têm rótulo; as outras 1.169 não permitem calcular acertos e erros. Retiramos da nova comparação as 2.342 do teste histórico, já examinado antes, e uma ficha com possível equivalência com esse teste. Restaram 9.361: 5.394 Normal e 3.967 Anormal. As repetições foram preservadas e reunidas em 9.166 grupos candidatos. O objetivo é impedir que entradas idênticas apareçam dos dois lados da avaliação. Esses grupos aproximam dependências entre registros, mas não são identidades de pacientes confirmadas.

**Como apresentar:** percorra a tabela de cima para baixo. A cada redução, diga a razão antes de avançar. Termine na frase dos grupos. Referência: 37 segundos; não leia os números como uma sequência sem relação.

**Pergunta provável: “Por que não apagar todas as cópias?”** “A A2 preserva as linhas e controla a dependência na divisão. Uma cópia no treino e outra na avaliação facilitaria reconhecer informação já vista. O agrupamento impede essa separação para as equivalências identificadas.” Isso não garante que todas as visitas de uma mesma pessoa tenham sido reconhecidas.

**Ligação:** selecionar fichas resolve quem entra; selecionar variáveis resolve quais informações entram.

## Slide 4: justificar as entradas

**Mensagem central:** uma variável útil estatisticamente pode ser inadequada para a pergunta de previsão.

As oito entradas principais são idade, sexo, peso, altura, índice de massa corporal, pressão sistólica, pressão diastólica e frequência cardíaca. Memorize por grupos: dados demográficos, medidas corporais e sinais vitais. A disponibilidade dessas medidas para um uso futuro ainda precisaria ser confirmada.

Vazamento ocorre quando o modelo recebe informação da resposta que não deveria ter naquele contexto de previsão. MOTIVO1 e MOTIVO2 contêm conteúdo diagnóstico, como cardiopatia já estabelecida. HDA2 é outro caso: tem cobertura muito pequena e momento de registro incerto. Não use a mesma justificativa automaticamente para todas as exclusões.

ID é identificador; convênio é administrativo; datas brutas servem à derivação de idade. Os cinco campos exploratórios são sopro, B2, pulsos, classificação da pressão e sintomas. B2 representa o segundo som cardíaco. Esses achados podem ter participado da própria construção da resposta.

**Fala sugerida, igual ao roteiro:**

> O conjunto principal tem oito entradas: idade, sexo, peso, altura, índice de massa corporal, pressões sistólica e diastólica e frequência cardíaca. Excluímos os motivos do encaminhamento porque antecipam a resposta, como uma cardiopatia já estabelecida: esse é o risco de vazamento. HDA2, o segundo campo de histórico da doença, sai pela baixa cobertura e origem temporal incerta. ID e convênio não descrevem o estado fisiológico; as datas servem para calcular idade, sem entrar diretamente. Sopro, segundo som cardíaco, pulsos, classificação da pressão e sintomas ficam em uma comparação exploratória, pois sua relação com a rotulagem é incerta.

**Como apresentar:** acompanhe as quatro linhas da tabela e diga a razão de cada grupo. Na fala, “segundo som cardíaco” explica B2. Evite ler os códigos como se todos soubessem seu significado. Referência: 43 segundos.

**Pergunta provável: “Então FISIO8 não tem vazamento?”** “Retiramos fontes importantes de risco, mas não podemos garantir ausência absoluta de incorporação no rótulo. Por exemplo, as pressões também podem ter participado da classificação. O artigo mantém essa limitação explícita.”

**Ligação:** uma informação admissível ainda pode conter erro de representação ou incoerência; por isso vem a limpeza.

## Slide 5: defender a limpeza

**Mensagem central:** tratamos a informação que não conseguimos sustentar sem adivinhar o valor verdadeiro.

Padronizar grafias e separadores decimais reúne formas equivalentes. Conferir datas evita derivar idades contraditórias. Nos pares em que a sistólica é menor ou igual à diastólica, a política mascara ambas, pois não sabemos qual campo errou. Mascarar significa tornar a medida indisponível na matriz usada pelo modelo; o valor original continua preservado.

A FC de 1.120 é um exemplo real. Transformá-la em 112 pareceria plausível, mas seria uma correção sem evidência. O gatilho acima de 500 é uma regra operacional de curadoria, não um máximo fisiológico demonstrado. O projeto também evita descartar automaticamente todo extremo: a revisão abandonou o antigo teto de 220 para FC e preserva outros extremos potencialmente reais sob regras documentadas.

**Fala sugerida, igual ao roteiro:**

> Primeiro padronizamos grafias, números e marcadores de ausência. Depois conferimos datas, coerência entre medidas e valores suspeitos. Na pressão, sistólica menor ou igual à diastólica leva a marcar ambas como indisponíveis, sem presumir que foram trocadas. Neste exemplo real, a frequência cardíaca 1.120 supera a regra de suspeita de 500 batimentos por minuto. Marcamos a célula como ausente e conservamos o restante da ficha. Não corrigimos para 112 porque não sabemos o valor verdadeiro. São regras de curadoria declaradas, não limites clínicos universais.

**Como apresentar:** percorra as primeiras verificações rapidamente e dê atenção ao exemplo 1.120. Faça uma pequena pausa antes de “não corrigimos para 112”. Essa frase mostra o raciocínio da decisão. Referência: 37 segundos.

**Pergunta provável: “Por que exatamente 500?”** “É um gatilho amplo adotado para sinalizar registros suspeitos nesta curadoria, sem tratar toda frequência elevada como erro. Não demonstramos que 500 seja um limite clínico universal ou o corte ótimo; a regra permanece documentada e sujeita a revisão.”

**Ligação:** após mascarar os valores suspeitos, precisamos lidar com as ausências sem perder todas as demais informações das fichas.

## Slide 6: explicar o preenchimento

**Mensagem central:** preenchimento é uma estimativa aprendida no treino, identificada como estimativa e comparada com alternativas.

Os percentuais de cerca de 56% nas pressões e 34,6% no IMC descrevem indisponibilidade após a limpeza e antes da imputação. Incluem ausências originais e valores mascarados. Excluir toda ficha incompleta perderia muita informação. Isso não torna manter qualquer variável automaticamente a melhor escolha.

Para entender a mediana, use este **exemplo didático inventado, que não é uma ficha nem resultado da base**: valores 80, 85, 90, 95 e 300. A mediana é 90, o terceiro valor ordenado. A média é (80 + 85 + 90 + 95 + 300)/5 = 650/5 = 130. O extremo altera muito a média e não desloca da mesma forma a posição central. Essa resistência motiva testar a mediana, mas ela reduz a variabilidade e não conhece o valor que faltou.

A alternativa por idade considera diferenças de crescimento para Peso, Altura, IMC e FC. Cada faixa precisa de 30 observações de treino para aquela variável. Sem suporte, ou sem idade disponível, volta à mediana global. Idade e pressões continuam com mediana global nessas alternativas. A floresta final selecionou a global entre as configurações comparadas.

**Fala sugerida, igual ao roteiro:**

> Depois da limpeza, cerca de 56% das pressões e 34,6% dos índices de massa corporal estavam indisponíveis. Apagar fichas incompletas perderia muita informação. Comparamos a mediana global, valor central menos influenciado por extremos, com a mediana da faixa etária, para considerar o crescimento. Exigimos 30 observações por faixa; sem suporte, usamos a global. No ajuste final da floresta, frequência ausente recebe 92 e indicador de preenchimento um. Essa mediana vem do treino; cada divisão da validação aprende a sua, sem usar as fichas avaliadas.

**Como apresentar:** comece pela quantidade de ausências, compare as duas alternativas e termine no exemplo 92 com indicador 1. Referência: 37 segundos. O exemplo didático da mediana é para estudar ou responder à pergunta; acrescentá-lo inteiro na exposição exige recalcular o tempo.

**Pergunta provável: “92 é o valor correto?”** “Não sabemos o valor verdadeiro. É a mediana da frequência cardíaca no ajuste final da floresta. O indicador 1 registra que houve preenchimento; uma medida observada de 92 teria indicador 0.”

**Pergunta provável: “Usaram a mesma mediana em toda avaliação?”** “Não. Cada divisão aprende os preenchimentos somente em seu treino. As fichas avaliadas não ajudam a calcular esses valores.” O indicador pode carregar padrões da coleta; sua presença não garante ausência de viés.

**Passagem para Antônio:** “Com a seleção e o preenchimento definidos, o Antônio vai mostrar como representamos as informações e como os modelos fazem as previsões.” Essa passagem deve caber nas pausas e transições gerais.

## Ensaiar sem decorar mecanicamente

**Primeira rodada: compreensão.** Sem cronômetro, explique cada slide sem ler a fala. Para cada escolha, diga o problema, a decisão e uma limitação. Quando travar, consulte a explicação e tente novamente. O objetivo é conseguir justificar, não reproduzir frases idênticas.

**Segunda rodada: exposição.** Apresente os seis slides com cronômetro e grave o áudio, se for útil. Compare com a referência de 3min35s. Confira se mencionou todos os elementos visíveis e se explicou a razão das decisões. Se exceder o tempo, retire repetições e desvios; não apague conteúdo necessário nem acelere todas as frases. Ensaiar números em voz alta é essencial, porque sua pronúncia ocupa mais tempo do que parece no texto.

**Terceira rodada: perguntas.** Peça que alguém interrompa sua explicação e mude a formulação das perguntas abaixo. Responda primeiro de modo direto; depois apresente a justificativa. Treine também a passagem para Antônio. Seu colega precisa saber exatamente onde você termina.

Olhe para o slide apenas para localizar o elemento e volte para a plateia. Evite ficar de costas lendo. Faça pausas curtas nas decisões importantes, sobretudo “rótulo registrado”, “grupos não são pacientes” e “não sabemos o valor verdadeiro”.

## Autoteste antes da apresentação

Tente responder sem consultar o texto:

1. Por que 12.873 fichas não significam 12.873 pacientes distintos?
2. Como você chega a 9.361 registros e por que o teste histórico ficou fora?
3. Por que agrupar cópias em vez de permitir que atravessem treino e avaliação?
4. Quais são as oito entradas principais? Por que as exclusões têm motivos diferentes?
5. Por que 1.120 não virou 112? O que significa o limite 500?
6. O que diferencia uma FC observada de 92 de uma FC preenchida com 92?
7. Por que a mediana e a alternativa por idade foram comparadas? Quando ocorre o retorno à global?
8. Qual informação você não tem para afirmar ausência absoluta de vazamento?

Depois, confira respectivamente os slides 2, 3, 3, 4, 5, 6, 6 e 4 deste guia. Para aprofundar todas as variáveis, modelos e métricas, use o Guia de estudo e defesa da A2. Sua parte na exposição não limita o que você precisa conhecer para a arguição.

Se não souber uma resposta, separe o conhecido do desconhecido: “O que implementamos foi isto, por esta razão. Esse ponto específico não foi confirmado na documentação, por isso mantivemos esta limitação”. Não apresente como experimento realizado uma alternativa que você apenas sugeriria testar.

## Fontes do estudo

As falas e tempos vêm de `presentation/a2_inf/roteiro.json`. As justificativas e limites foram conferidos em `presentation/a2_inf/output/Guia_Defesa_A2.md` e nos resultados agregados em `resultados/a2/revisao_final_2026_11_16/reviewed_results.json`. A divisão atual está em `presentation/a2_inf/output/Divisao_Apresentacao_A2.md`. Este material organiza o estudo; não altera os slides, o protocolo ou os resultados.
