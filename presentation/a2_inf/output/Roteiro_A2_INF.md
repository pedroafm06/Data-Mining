# Roteiro da apresentação da A2

Tempo planejado de 14 min 35 s, com 25 s de margem até o limite de 15 minutos.

- Antônio Henrique · 2:50
- João Vitor · 4:00
- Mateus Nery · 3:35
- Pedro Matos · 4:10

## 1. Classificação de registros cardíacos pediátricos

Antônio Henrique · 0:00 a 0:25

Boa tarde. Somos Antônio, João, Mateus e Pedro. Investigamos quanto as medidas de um atendimento de cardiologia pediátrica ajudam a prever o rótulo que ficou na ficha. Vamos acompanhar uma ficha de exemplo, ver como os modelos foram avaliados e interpretar onde eles acertaram e erraram.

## 2. O que o modelo tenta prever

Antônio Henrique · 0:25 a 1:10

Imaginem uma ficha com idade, peso e frequência cardíaca. Na base, cada ficha rotulada traz também uma classe registrada, Normal ou Anormal. No treino, o modelo vê as medidas e a classe de cada exemplo. Na avaliação, recebe só as informações definidas como entrada. Ele produz uma previsão e nós a comparamos com o rótulo registrado. Esse é o sentido de classificação aqui. O acerto mede a concordância com o registro da base.

## 3. De onde vêm os dados

Antônio Henrique · 1:10 a 2:05

A base reúne atendimentos no Real Hospital Português, em Recife. O arquivo original tinha 12.873 registros. Desses, 11.704 tinham rótulo. Reservamos 2.342 para o teste histórico e separamos um por equivalência, chegando a 9.361 fichas de desenvolvimento, as que usamos na nossa comparação. Elas incluem 5.394 Normal e 3.967 Anormal. Essa distribuição importa para a avaliação. Uma regra que sempre responda Normal já fica perto de 58% de acerto no total, embora deixe passar todos os registros Anormal. O Mateus vai mostrar como a métrica trata essa diferença.

## 4. Limpeza e transformação

Antônio Henrique · 2:05 a 2:50

Padronizamos as unidades e marcamos medidas suspeitas como ausentes para aproveitar o restante da ficha. Na amostra analisada, cada uma das duas medidas de pressão ficou ausente ou foi mascarada em cerca de 56% dos registros. Testamos preencher lacunas com a mediana, que é o valor central entre as medidas conhecidas no treino, ou com a mediana da faixa etária. Guardamos um indicador do preenchimento. Agora o João mostra quais campos entraram na comparação.

## 5. Quando uma entrada já traz a resposta

João Vitor · 2:50 a 3:45

Imaginem que o encaminhamento diz que a cardiopatia já está estabelecida. Se a frase entra no modelo, ele pode se apoiar em uma informação que antecipa o rótulo. Isso é um exemplo de vazamento. Tiramos os dois campos de motivo de encaminhamento dos três cenários. Sopro, segunda bulha e pulsos também pedem cuidado, porque podem ter participado da decisão registrada. Por isso, a comparação principal parte de medidas como idade, peso e frequência cardíaca. Depois medimos quanto a pontuação muda quando o modelo recebe também achados do exame.

## 6. Três maneiras de classificar

João Vitor · 3:45 a 4:45

Primeiro usamos uma referência bem simples. Ela responde Normal para todas as fichas porque essa é a classe mais frequente. A árvore de decisão aprende uma sequência de perguntas. A logística combina as medidas, atribui pesos e estima a probabilidade de Anormal. Já a floresta aleatória reúne 150 árvores por configuração. Cada uma aprende com uma amostra sorteada e considera parte das medidas em suas perguntas. A floresta combina as estimativas delas para chegar a uma previsão. Para comparar as famílias, usamos as mesmas fichas e divisões. Vamos ver duas perguntas que a árvore de fato aprendeu.

## 7. Uma regra que a árvore aprendeu

João Vitor · 4:45 a 5:35

Aqui estão os primeiros passos da árvore ajustada com todo o conjunto de desenvolvimento do cenário principal. Primeiro ela pergunta se o peso é de até 8,85 quilos. Nesse ramo, a próxima pergunta usa um corte de idade de cerca de 14 dias. No ramo acima de 8,85 quilos, ela pergunta se a frequência cardíaca é de até 98,5 batimentos por minuto. A árvore segue com outras perguntas até chegar a uma previsão. Esses cortes foram aprendidos nesta base. Eles descrevem como o modelo organiza as fichas.

## 8. Como avaliamos os modelos

João Vitor · 5:35 a 6:50

Dividimos as fichas em cinco partes. Em cada rodada, separamos quatro para ajuste e uma para avaliação. Dentro das quatro partes de ajuste, fazemos novas divisões para escolher configurações, como a profundidade máxima da árvore. Ao todo, havia 105 configurações por cenário, contando a referência majoritária. Escolhemos a melhor configuração de cada família usando apenas as divisões internas, treinamos novamente com as quatro partes e avaliamos na quinta. Repetimos até que cada parte tenha servido uma vez para avaliação. Isso é validação cruzada aninhada. Além disso, mantivemos no mesmo grupo as fichas com entradas brutas idênticas, para a cópia de uma ficha ficar junto da original. Agora o Mateus mostra como pontuamos essas previsões.

## 9. Acurácia balanceada

Mateus Nery · 6:50 a 7:50

Vamos imaginar cem fichas Normal e cem Anormal. A referência responde sempre Normal. Ela acerta cem por cento das Normal e zero por cento das Anormal. A acurácia balanceada é a média dos dois percentuais, então vale cinquenta por cento nesse exemplo. Usamos a mesma lógica na base real. A sensibilidade é a fração de fichas Anormal que o modelo reconhece, e a especificidade é a fração de fichas Normal que ele reconhece. Cada taxa conta com o mesmo peso na média, mesmo quando temos mais fichas de uma classe.

## 10. A floresta teve o melhor resultado

Mateus Nery · 7:50 a 9:00

No cenário principal, todos os modelos receberam as mesmas oito entradas. A referência ficou em 50%, a árvore em 61,69%, a logística em 62,03% e a floresta em 63,27%. A vantagem da floresta sobre a logística foi de 1,24 ponto percentual. Para ver como a diferença variava, sorteamos grupos de fichas e recalculamos a comparação nas previsões que já tínhamos. O intervalo de 95% ficou entre 0,43 e 2,01 pontos. Essa vantagem foi pequena dentro desta avaliação. A média também esconde quais fichas o modelo teve mais dificuldade de reconhecer. Vamos abrir a pontuação olhando os acertos e erros por classe.

## 11. Os erros da floresta

Mateus Nery · 9:00 a 10:25

Cada linha da tabela é o rótulo registrado e cada coluna é a previsão. Dos 3.967 registros Anormal, a floresta reconheceu 2.308, ou 58,18%. Os outros 1.659 receberam previsão Normal. Isso dá cerca de 42 por cem. Na classe Normal ela acertou 3.687, ou 68,35%, e marcou 1.707 como Anormal. A média de 58,18% e 68,35% explica o resultado de 63,27%. Também comparamos idades nos registros Anormal com idade conhecida. A mediana foi 6,51 anos entre os que a floresta deixou passar e 0,59 ano entre os reconhecidos. Essa diferença descreve grupos desta base. Ela ajuda a identificar onde vale investigar o desempenho com mais cuidado. O Pedro mostra quais medidas influenciam a pontuação.

## 12. Quais medidas a floresta mais usou

Pedro Matos · 10:25 a 11:10

Trocamos entre as fichas os valores de uma medida por vez e mantivemos as outras entradas como estavam. Assim, os valores ainda existem, mas deixam de estar ligados às fichas originais. Quando fizemos isso com a frequência cardíaca, a acurácia balanceada caiu 4,80 pontos. Para peso, caiu 2,76, e para idade, 1,40. Esse teste mede quanto a floresta se apoia nessas medidas. Se dois campos carregam informações parecidas, um pode compensar parte da troca no outro.

## 13. O resultado muda com as entradas

Pedro Matos · 11:10 a 12:15

Com quatro informações, peso, altura, idade e sexo, a melhor acurácia balanceada foi 59,55%, com a árvore. No cenário principal, acrescentamos o índice de massa corporal, as duas medidas de pressão e a frequência cardíaca. A floresta chegou a 63,27%. Quando adicionamos mais cinco campos, entre eles achados como sopro e pulsos, a árvore chegou a 91,92%. Cada número do slide é o melhor resultado observado naquele conjunto. Se usarmos a árvore nos dois casos para comparar diretamente, a passagem de oito para treze entradas aumentou a pontuação em 30,23 pontos. O cenário com achados é exploratório. Vamos ver por que o sopro chama atenção.

## 14. O papel do sopro

Pedro Matos · 12:15 a 13:00

Sopro é um som que pode ser ouvido durante o exame do coração. Considerando as fichas em que o campo estava preenchido, em 5.814 havia ausência registrada e 587 tinham rótulo Anormal, ou 10,1%. Nas outras 3.529, o sopro estava presente. Dessas, 3.375 tinham rótulo Anormal, ou 95,6%. A comparação mostra uma associação forte na base. No próximo slide vemos o quanto a própria árvore dependeu dessa informação para prever.

## 15. Quanto a árvore depende do sopro

Pedro Matos · 13:00 a 13:55

Na árvore que recebeu os achados do exame, repetimos o teste de embaralhar os valores entre fichas. Trocar o sopro fez a acurácia balanceada cair 38,57 pontos, mantendo os outros campos como estavam. Repetir o teste só com B2, que é a segunda bulha cardíaca, produziu uma queda de 3,21 pontos. A diferença mostra o quanto a árvore depende do sopro. A base registra o achado e o rótulo, mas a ordem da coleta e o critério de rotulagem seguem incertos. O sopro pode ter ajudado a definir esse mesmo rótulo.

## 16. O que os resultados permitem concluir

Pedro Matos · 13:55 a 14:35

No cenário principal, a floresta chegou a 63,27% de acurácia balanceada e reconheceu cerca de 58 de cada cem fichas rotuladas Anormal. A comparação exploratória mostrou o peso do sopro quando incluímos os achados. Para levar a avaliação a novos atendimentos, precisamos documentar a ordem da coleta, confirmar como o rótulo é definido e testar o procedimento em uma amostra independente. Obrigado. Podemos responder às perguntas.

## Arguição

**Por que usamos o cenário CLINICO como exploratório?**

A origem dos achados e seu possível uso no rótulo seguem incertos. O resultado de 91,92% mostra quanto a comparação muda quando esses campos entram e precisa ser interpretado à luz dessa incerteza.

**A análise provou que SOPRO vaza o rótulo?**

A fração de fichas Anormal varia com o registro do sopro e a árvore perde 38,57 pontos quando embaralhamos esse campo. Isso demonstra quanto a árvore depende do sopro. Para confirmar a origem dessa associação precisamos conhecer a coleta e a construção do rótulo.

**Por que a contagem rotulada da A2 é maior que a da A1?**

A A1 removeu 987 cópias exatas, das quais 235 tinham rótulo. A A2 preservou as linhas rotuladas. Assim, a contagem passou de 11.469 para 11.704, antes de reservar o teste histórico e retirar uma linha por equivalência candidata.

**Qual a diferença entre os cortes externos e internos?**

Os cortes internos escolhem os ajustes usando apenas a parte disponível para treino. Os cortes externos avaliam o procedimento já escolhido em registros reservados. São cinco externos e três internos por rodada externa.

**O que mudou no agrupamento das fichas?**

O esquema anterior distribuía 118 fichas com entradas brutas idênticas por folds externos diferentes. A revisão juntou essas entradas nos mesmos grupos, sem usar ID nem rótulo para definir igualdade. O desenvolvimento permaneceu com 9.361 registros e passou de 9.279 para 9.166 grupos candidatos.

**Como construíram os intervalos da comparação?**

Usamos 2.000 reamostragens de grupos de fichas. Em cada uma, comparamos os modelos sobre os mesmos grupos e recalculamos a pontuação. Os intervalos descrevem a variação possível sobre as previsões existentes e dependem dos cortes e treinamentos já feitos.

**Qual foi o papel do teste histórico?**

O teste histórico foi reservado antes da análise e já havia sido examinado em fases anteriores. Ele compartilha padrões brutos de entrada com o desenvolvimento. A avaliação final usa as previsões feitas nas partes reservadas da validação cruzada. Uma confirmação independente exige nova amostra com coleta e rotulagem documentadas.

**Os cortes da árvore servem como referência clínica?**

Os cortes de peso, idade e frequência cardíaca foram aprendidos pela árvore ajustada às fichas de desenvolvimento. Eles descrevem os primeiros passos daquele modelo e dependem da amostra e do treinamento. A adoção de critérios clínicos exige evidência própria.

**O que explica a diferença de idade nos erros?**

Entre as fichas Anormal com idade conhecida, a mediana dos casos previstos como Normal foi 6,51 anos, e a dos reconhecidos foi 0,59 ano. A diferença é descritiva. Avaliar em que idades a floresta de fato erra mais exige medir a taxa de erro por faixa etária e investigar a composição de cada faixa.
