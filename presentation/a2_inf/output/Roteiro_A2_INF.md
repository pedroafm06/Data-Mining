# Roteiro da apresentação da A2

Tempo planejado de 14 min 10 s, com 50 s de margem até o limite de 15 minutos.

- Antônio Henrique · 2:50
- João Vitor · 3:45
- Mateus Nery · 3:35
- Pedro Matos · 4:00

## 1. Classificação de registros cardíacos pediátricos

Antônio Henrique · 0:00 a 0:25

Boa tarde. Somos Antônio, João, Mateus e Pedro. Nosso trabalho começa com uma pergunta. Quanto conseguimos prever sobre um registro de cardiologia pediátrica a partir das medidas que ele contém? Vamos mostrar como comparamos os modelos e o que mudou quando acrescentamos achados do exame.

## 2. O que o modelo tenta prever

Antônio Henrique · 0:25 a 1:15

Imaginem uma ficha como a do slide. Nela há informações como a idade e a frequência cardíaca. Cada ficha também tem um rótulo, Normal ou Anormal, já registrado na base. Para treinar, o modelo recebe exemplos em que conhecemos as medidas e o rótulo. Quando vamos avaliar, entregamos apenas as medidas da ficha. O modelo escolhe um dos dois rótulos e depois conferimos se bateu com o que estava registrado. Essa é uma tarefa de classificação. O que medimos é a capacidade de reproduzir o rótulo da base.

## 3. De onde vêm os dados

Antônio Henrique · 1:15 a 2:00

Os dados vieram de atendimentos no Real Hospital Português, em Recife. O arquivo tinha 12.873 registros. Na avaliação final usamos 9.361 registros com rótulo, dos quais 5.394 eram Normal e 3.967 eram Anormal. Essa diferença importa. Se eu sempre disser Normal, vou acertar mais da metade das fichas, mas vou perder todas as da outra classe. Daqui a pouco o Mateus explica como a métrica leva isso em conta. Antes dos modelos, fizemos um preparo rápido dessas medidas.

## 4. Limpeza e transformação

Antônio Henrique · 2:00 a 2:50

Na limpeza, padronizamos unidades e marcamos valores suspeitos como ausentes. Assim, se uma medida estiver inutilizável, ainda podemos usar as outras informações da ficha. Depois da limpeza, cada medida de pressão estava ausente em 56% dos registros. Para preencher uma medida que falta, testamos usar o valor central de todo o treino ou da faixa etária. Marcamos que aquele valor foi preenchido. Na regressão logística, ajustamos também a escala das medidas. Aprendemos esses valores só com a parte de treino. Agora o João vai explicar o que escolhemos deixar fora das entradas.

## 5. Quando uma entrada já traz a resposta

João Vitor · 2:50 a 3:50

Pensem numa ficha cujo motivo do encaminhamento diz que a cardiopatia já está estabelecida. Esse texto pode antecipar o rótulo que queremos prever. Chamamos de vazamento de informação quando o modelo recebe algo que entrega a resposta ou que não estaria disponível na hora da previsão. Por isso, os dois campos de motivo de encaminhamento ficaram fora dos três cenários. Sopro, segunda bulha e pulsos também pedem cuidado, porque podem ter ajudado a determinar o próprio rótulo. Como a base não esclarece essa origem, nosso cenário principal usa oito medidas e características, como idade, peso e frequência cardíaca. Testamos os achados separadamente para entender o efeito de incluí-los.

## 6. Três maneiras de classificar

João Vitor · 3:50 a 5:10

Primeiro montamos uma referência bem simples. Como Normal é o rótulo mais frequente, ela responde Normal para todas as fichas. Em seguida testamos três modelos. A árvore de decisão faz uma sequência de perguntas. Ela pode perguntar se o peso está acima de certo valor, seguir por um ramo e então consultar outra medida. A árvore aprende quais perguntas fazer. A regressão logística combina as medidas e seus pesos para estimar uma probabilidade de o rótulo ser Anormal. Usamos a mesma regra de corte para todos os modelos que produzem esse tipo de pontuação. A floresta aleatória reúne muitas árvores. Cada uma aprende com uma amostra e considera subconjuntos de medidas ao decidir. A floresta combina as estimativas delas. Essas abordagens têm jeitos diferentes de aprender. Para a comparação ser justa, todas recebem os mesmos dados em cada rodada.

## 7. Como avaliamos os modelos

João Vitor · 5:10 a 6:35

Avaliar na mesma ficha que o modelo usou para aprender pode inflar o resultado. Então dividimos os registros em cinco partes. Em cada rodada, quatro partes ficam disponíveis para treino e uma fica reservada para avaliar a previsão. Dentro da parte de treino, fazemos cortes menores para escolher os ajustes, por exemplo o tamanho de uma árvore. Depois treinamos com o ajuste escolhido e fazemos as previsões na parte reservada. Repetimos a rodada até que cada uma das cinco partes tenha servido para avaliar. No fim, cada ficha tem uma previsão feita quando estava de fora do treino. Também mantivemos juntas as fichas com entradas brutas idênticas, para evitar que uma cópia servisse de atalho na avaliação. Os modelos foram comparados nas mesmas fichas e nos mesmos cortes. Com as previsões em mãos, o Mateus mostra como transformamos os acertos em uma pontuação.

## 8. Acurácia balanceada

Mateus Nery · 6:35 a 7:40

Lembram da regra que responde Normal em todas as fichas? Vamos imaginar um exemplo com cem fichas Normal e cem Anormal. Nessa regra, acertamos todas as cem Normal e deixamos passar todas as cem Anormal. Ou seja, temos cem por cento de acerto dentro de uma classe e zero dentro da outra. A acurácia balanceada faz a média desses dois percentuais. Nesse exemplo, ela vale cinquenta por cento. Para a nossa base, fazemos a mesma conta dentro de cada classe, mesmo tendo quantidades diferentes de fichas. Assim, Normal e Anormal pesam igualmente na comparação.

## 9. A floresta teve o melhor resultado

Mateus Nery · 7:40 a 8:50

Aqui todos os modelos recebem as mesmas oito entradas do cenário principal. A referência de responder sempre Normal fica em 50%. A árvore chega a 61,69%, a regressão logística a 62,03% e a floresta a 63,27%. A floresta teve a maior pontuação nessa avaliação e ficou 1,24 ponto percentual acima da logística. Para entender a variação dessa diferença, repetimos a comparação sorteando os grupos de fichas. O intervalo de 95% que obtivemos, com essas previsões já produzidas, vai de 0,43 a 2,01 pontos. A vantagem observada é pequena. Para entender o que a pontuação de 63,27% representa, precisamos olhar também para onde a floresta errou.

## 10. Os erros da floresta

Mateus Nery · 8:50 a 10:10

Na tabela, cada linha mostra o rótulo que estava registrado. Cada coluna mostra o que a floresta previu. Olhem a linha Anormal. Dos 3.967 registros dessa classe, a floresta reconheceu 2.308. Isso dá 58,18%. Os outros 1.659 receberam previsão Normal. Em números redondos, de cada cem registros Anormal, a floresta reconheceu 58 e deixou passar 42. Agora olhem a linha Normal. A floresta reconheceu 3.687 e marcou 1.707 como Anormal. O acerto dentro da classe Normal foi de 68,35%. A média de 58,18 e 68,35 é aproximadamente os 63,27% do gráfico anterior. Essas discordâncias são com o rótulo da ficha. O Pedro vai mostrar quais medidas mais influenciaram a pontuação e o que acontece quando mudamos as entradas.

## 11. Quais medidas a floresta mais usou

Pedro Matos · 10:10 a 10:55

Para entender de quais medidas a floresta dependeu, experimentamos embaralhar uma por vez entre as fichas da avaliação. Por exemplo, trocamos os valores de frequência cardíaca entre as fichas e deixamos os demais campos como estavam. A pontuação caiu 4,80 pontos. Quando embaralhamos o peso, a queda foi de 2,76 pontos. Isso mostra o quanto essas medidas ajudaram a floresta nesta avaliação. O teste mede a dependência do modelo, e a relação entre as próprias medidas também pode influenciar essa queda.

## 12. O resultado muda com as entradas

Pedro Matos · 10:55 a 11:55

O que acontece se mudarmos as informações mostradas aos modelos? Com apenas peso, altura, idade e sexo, o melhor resultado observado foi 59,55%, com a árvore. Com oito entradas, incluindo as medidas de pressão e a frequência cardíaca, a floresta chegou aos 63,27% que já vimos. Quando acrescentamos cinco campos, entre eles achados do exame como sopro, a árvore chegou a 91,92%. Aqui cada barra mostra a maior pontuação observada naquele conjunto de entradas. Se mantivermos a árvore para comparar diretamente, incluir o bloco de cinco campos elevou a pontuação em 30,23 pontos. Esse último resultado é exploratório. Vamos olhar mais de perto o que há por trás dele.

## 13. O papel do sopro

Pedro Matos · 11:55 a 13:10

O sopro é um som que pode ser ouvido durante o exame do coração. Entre as fichas que registram ausência de sopro, cerca de 10% têm rótulo Anormal. Entre as que registram presença, cerca de 96% têm esse rótulo. Estamos olhando apenas para as fichas em que o status do sopro era conhecido. Ao embaralhar essa informação entre as fichas, a pontuação da árvore do cenário exploratório caiu 38,57 pontos. Isso mostra uma forte dependência desse campo. A questão é de onde vem essa relação. O achado pode estar associado à condição registrada e também pode ter influenciado a decisão que produziu o rótulo. Como a base não informa a ordem da coleta e os critérios usados para dar o rótulo, não dá para separar essas explicações aqui.

## 14. O que os resultados permitem concluir

Pedro Matos · 13:10 a 14:10

Na comparação principal, a floresta teve a maior acurácia balanceada, com 63,27%. Vimos também que ela reconhece cerca de 58 em cada cem registros rotulados Anormal. Quando damos ao modelo os achados do exame, a pontuação sobe muito e passa a depender bastante do sopro. O trabalho mostra duas coisas que precisamos saber antes de interpretar uma pontuação. Quais informações estavam disponíveis para prever? Como foi definido o próprio rótulo? Para avaliar o uso em novos atendimentos, o próximo passo é documentar esses dois pontos e testar em um conjunto independente de registros. Obrigado. Podemos responder às perguntas.

## Arguição

**Por que o cenário CLINICO não é o principal se chegou a 91,92%?**

A base não esclarece quando os achados ficaram disponíveis nem se eles participaram da definição do rótulo. O cenário com achados mede como a comparação muda quando esses campos entram. A interpretação depende da origem deles.

**A análise provou que SOPRO vaza o rótulo?**

A proporção de rótulos Anormal muda muito com SOPRO e a árvore perde 38,57 pontos quando permutamos esse campo. Isso comprova dependência da previsão neste experimento. A origem dessa associação exige conhecer a coleta e a rotulagem.

**Por que a contagem rotulada da A2 é maior que a da A1?**

A A1 removeu 987 cópias exatas, das quais 235 tinham rótulo. A A2 preservou as linhas rotuladas. Assim, a contagem passou de 11.469 para 11.704, antes de reservar o teste histórico e retirar uma linha por equivalência candidata.

**Qual a diferença entre os cortes externos e internos?**

Os cortes internos escolhem os ajustes usando apenas a parte disponível para treino. Os cortes externos avaliam o procedimento já escolhido em registros reservados. São cinco externos e três internos por rodada externa.

**O que mudou no agrupamento das fichas?**

O esquema anterior distribuía 118 fichas com entradas brutas idênticas por folds externos diferentes. A revisão juntou essas entradas nos mesmos grupos, sem usar ID nem rótulo para definir igualdade. O desenvolvimento permaneceu com 9.361 registros e passou de 9.279 para 9.166 grupos candidatos.

**Como construíram os intervalos da comparação?**

Usamos 2.000 reamostragens de grupos de fichas. Em cada uma, comparamos os modelos sobre os mesmos grupos e recalculamos a pontuação. Os intervalos descrevem a variação possível sobre as previsões existentes e dependem dos cortes e treinamentos já feitos.

**Por que não usar o teste histórico para confirmar o resultado?**

Ele já havia sido examinado e ainda compartilha padrões brutos de entrada com o desenvolvimento. A avaliação final usa previsões externas da validação cruzada. Uma verificação independente exige uma nova amostra com coleta e rotulagem documentadas.
