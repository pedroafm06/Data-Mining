# Roteiro e preparação para arguição

15 slides numerados, 14 min 30 s de fala. Três slides de apoio ficam ocultos. Qualquer integrante deve conseguir explicar todo o roteiro.

- Antônio Henrique Queiroz Villar Lopes: 3 min 20 s.
- João Vitor Fernandes Ferreira: 3 min 10 s.
- Mateus Nery Bailão: 3 min 50 s.
- Pedro Augusto Ferreira Matos: 4 min 10 s.

## 1. Classificação de registros de cardiologia pediátrica

Responsável: Antônio Henrique Queiroz Villar Lopes. Tempo: 0:30.

Somos o grupo 3. Vamos mostrar como classificamos registros de cardiologia pediátrica como normais ou anormais, quais atributos deixamos o modelo usar e o que os resultados dizem sobre a origem da informação.

**Pergunta provável:** Qual é a contribuição principal?

**Resposta:** Uma política de atributos baseada na disponibilidade no momento da previsão e a comparação de quatro modelos em três cenários com o mesmo protocolo.


## 2. Tarefa

Responsável: Antônio Henrique Queiroz Villar Lopes. Tempo: 0:50.

A base UCMF vem de atendimentos de cardiologia pediátrica do Real Hospital Português, em Recife. O alvo indica se o registro foi rotulado como normal ou anormal. A classe positiva é Anormal. A pergunta é: com o que se coleta no atendimento, antes do laudo, dá para antecipar esse rótulo? Pensamos no uso como apoio à triagem.

**Pergunta provável:** O modelo diagnostica doença?

**Resposta:** Não. Ele prevê o rótulo registrado na base, cujo critério de referência não está documentado.


## 3. Dados e partições

Responsável: Antônio Henrique Queiroz Villar Lopes. Tempo: 1:00.

São 12.873 registros e 21 atributos. 1.169 não têm rótulo. Dos 11.704 rotulados, 9.361 formam o desenvolvimento, onde fazemos toda a escolha de modelos, e 2.342 formam o teste histórico, separado numa fase anterior. No desenvolvimento, 42,4% são anormais: um desequilíbrio moderado, por isso usamos acurácia balanceada.

**Pergunta provável:** Por que não descartar o teste histórico?

**Resposta:** Usamos como avaliação secundária, uma única vez, deixando claro que ele já tinha sido examinado antes.


## 4. O exame físico separa as classes

Responsável: João Vitor Fernandes Ferreira. Tempo: 1:00.

Este gráfico mostra o percentual de anormais em cada achado do exame. Com sopro sistólico, 95,8% são anormais; sem sopro, 10,1%. B2 alterada também concentra anormais. Esses achados são exatamente o que o cardiologista observa ao examinar a criança.

**Pergunta provável:** Isso não é vazamento?

**Resposta:** Não pelo nosso critério: o sopro é auscultado no atendimento, antes do laudo. SOPRO sozinho tem BA de 91,1%, o que mostra poder preditivo, não informação do futuro.


## 5. Idade e frequência cardíaca

Responsável: João Vitor Fernandes Ferreira. Tempo: 0:50.

As crianças anormais são mais novas: mediana de 2,7 anos contra 4,8, e 35,3% delas têm menos de um ano, contra 17,2% dos normais. Isso é compatível com cardiopatias congênitas, percebidas cedo. A FC mediana é 98 contra 90 bpm, mas a FC cai com a idade, então parte dessa diferença é efeito da idade.

**Pergunta provável:** A FC é um marcador de doença?

**Resposta:** Aqui ela se confunde com a idade; não afirmamos efeito causal.


## 6. Critério de vazamento

Responsável: João Vitor Fernandes Ferreira. Tempo: 1:20.

Definimos vazamento como usar informação indisponível no momento da previsão. Saem ID e datas brutas; Convênio, que descreve a origem do paciente: no SUS, 95,0% dos 60 registros são anormais, o que reflete quem encaminhou; MOTIVO1 e MOTIVO2, que trazem o diagnóstico escrito, como cardiopatia congênita, risco já apontado na A1; e HDA2, com 96,5% de ausentes. Ficam medidas, sinais vitais, exame físico, sintomas e PPA, que é calculada de pressão, idade, sexo e altura.

**Pergunta provável:** Por que a versão anterior excluía SOPRO, B2 e PULSOS?

**Resposta:** Ela tratava como vazamento tudo o que estivesse próximo do rótulo. Revimos o critério: o que importa é a disponibilidade antes do laudo, e o exame físico está disponível.

**Pergunta provável:** E se o sopro tiver sido registrado depois do laudo?

**Resposta:** A base não tem horários. Por isso mantemos os cenários sem exame físico como sensibilidade e declaramos essa suposição como limitação.

**Pergunta provável:** Convênio está disponível no atendimento. Por que sai?

**Resposta:** Porque descreve o caminho de encaminhamento e não a criança. Um modelo apoiado nele aprenderia quem encaminha, e não o que se observa.


## 7. Três cenários

Responsável: Mateus Nery Bailão. Tempo: 0:50.

O cenário principal, CLINICO, tem 13 atributos. FISIO8 retira exame físico, sintomas e PPA e fica com medidas, sinais vitais e sexo. STRICT4 mantém só peso, altura, idade e sexo. Os três usam os mesmos registros e as mesmas partições, o que permite ver de onde vem a informação.

**Pergunta provável:** FISIO8 e STRICT4 viraram o quê?

**Resposta:** Análises de sensibilidade: mostram quanto do desempenho depende de cada bloco de atributos.


## 8. Da A1 para a A2

Responsável: Mateus Nery Bailão. Tempo: 1:00.

A A1 removeu 987 duplicados: 752 sem rótulo e 235 rotulados. Na A2 mantemos os rotulados e colocamos registros iguais no mesmo grupo, que nunca é dividido entre treino e validação; 93 ficam no grupo da cópia. Também mudamos três decisões: idade contínua em vez de faixas, one-hot no sexo e a imputação por faixa etária como opção testada, não como regra.

**Pergunta provável:** Por que não remover os duplicados?

**Resposta:** O agrupamento evita que cópias caiam em treino e validação ao mesmo tempo, sem perder registros.


## 9. Pré-processamento e validação

Responsável: Mateus Nery Bailão. Tempo: 1:10.

Tudo que aprende com os dados, como medianas, escalas e vocabulário das categorias, é ajustado só no treino de cada partição. A validação é aninhada: cinco folds externos para estimar o desempenho e, dentro de cada um, três folds internos para escolher os hiperparâmetros. É estratificada pela classe e agrupada. Sementes fixas: 42 nos modelos, 743 nos folds externos e 811 mais k nos internos.

**Pergunta provável:** Por que aninhada?

**Resposta:** Para que o mesmo dado não sirva para escolher hiperparâmetros e medir desempenho.


## 10. Modelos e métricas

Responsável: Mateus Nery Bailão. Tempo: 0:50.

O baseline simples é a classe majoritária, que sempre diz Normal. Comparamos com três modelos: árvore de decisão, regressão logística e floresta aleatória, com 105 configurações por cenário. A métrica principal é a acurácia balanceada, média de sensibilidade e especificidade.

**Pergunta provável:** Por que não acurácia comum?

**Resposta:** A classe majoritária já teria 57,6% de acurácia sem reconhecer nenhum anormal.


## 11. Resultado principal

Responsável: Pedro Augusto Ferreira Matos. Tempo: 1:10.

No CLINICO, árvore, logística e floresta ficam a 0,04 ponto uma da outra: é um empate. Pelo critério fixado antes, a árvore tem a maior BA, 91,9%, com sensibilidade de 87,5% e especificidade de 96,4%. A floresta ordena melhor as probabilidades, com ROC-AUC de 94,7%.

**Pergunta provável:** Se empatam, qual vocês usariam?

**Resposta:** A árvore, por ser a mais simples de explicar; a floresta, se o limiar for ajustado, porque ordena melhor.


## 12. De onde vem a informação

Responsável: Pedro Augusto Ferreira Matos. Tempo: 1:00.

Tirando o exame físico, a melhor BA cai 29,0 pontos, para 62,9%. Tirando também os sinais vitais, cai mais 3,2 pontos, para 59,7%. Quase toda a informação está na ausculta. No teste histórico a ordem se mantém: 92,9%, 65,2% e 60,3%.

**Pergunta provável:** O teste histórico confirma o resultado?

**Resposta:** Mostra estabilidade dentro da mesma coorte. Como ele já tinha sido examinado, não substitui validação externa.


## 13. Importância dos atributos

Responsável: Pedro Augusto Ferreira Matos. Tempo: 0:50.

Embaralhar o SOPRO derruba a BA em 38,6 pontos; B2, em 3,1. Os outros não mudam nada. Sem o exame, o modelo passa a usar FC (4,9) e peso (2,5), que acompanham a idade.

**Pergunta provável:** Importância é causa?

**Resposta:** Não. É a perda de desempenho do modelo quando o atributo é embaralhado.


## 14. Análise de erros

Responsável: Pedro Augusto Ferreira Matos. Tempo: 1:10.

São 496 falsos negativos, 12,5% dos anormais, e todos (100,0%) são crianças sem sopro. Entre os 195 falsos positivos, 79,0% têm sopro, o que é compatível com sopros inocentes. Numa triagem, o falso negativo é o erro caro: pode atrasar um diagnóstico. Por isso o próximo passo é ajustar o limiar para aumentar a sensibilidade.

**Pergunta provável:** Como reduzir os falsos negativos?

**Resposta:** Baixando o limiar e estudando à parte as crianças anormais sem sopro, com idade, FC e sintomas.


## 15. Conclusão e limitações

Responsável: Antônio Henrique Queiroz Villar Lopes. Tempo: 1:00.

O modelo reproduz o raciocínio do exame cardiológico: acerta muito quando há sopro e falha nas crianças sem sopro. As limitações são reais: o rótulo não tem padrão de referência documentado, supomos que o exame foi registrado antes do laudo, a avaliação é interna a uma coorte e os grupos não identificam pacientes. Código, sementes e resultados estão no repositório.

**Pergunta provável:** Qual dado mais mudaria o estudo?

**Resposta:** O critério de rotulagem e os horários de registro, que confirmariam a disponibilidade de cada atributo.

## Preparação conjunta

Todos devem saber explicar: o critério de vazamento e por que SOPRO fica e Convênio sai; a diferença entre folds internos e externos; por que as três famílias empatam no CLINICO; o que significa um falso negativo numa triagem; e as limitações. Os números deste roteiro vêm de `resultados/a2/auditoria_2026_11_07/reviewed_results.json`.
