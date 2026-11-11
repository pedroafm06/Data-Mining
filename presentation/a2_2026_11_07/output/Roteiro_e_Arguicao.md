# Roteiro e preparação para arguição

14 slides principais, 14 min 30 s. Os sete slides de apoio ficam ocultos na apresentação. Qualquer integrante deve compreender todo o roteiro.

- Antônio Henrique Queiroz Villar Lopes: 3 min 50 s.
- João Vitor Fernandes Ferreira: 3 min 40 s.
- Mateus Nery Bailão: 3 min 50 s.
- Pedro Augusto Ferreira Matos: 3 min 10 s.

## 1. Classificação de registros cardíacos pediátricos

Responsável sugerido: Antônio Henrique Queiroz Villar Lopes. Tempo: 0:30.

Apresentamos a revisão final do estudo de caso UCMF. O trabalho tem duas partes conectadas: primeiro auditamos quais informações podem entrar no modelo e quais riscos permanecem. Depois comparamos referência, regressão logística, árvore e floresta com o mesmo protocolo. O foco é explicar o que os resultados sustentam. O modelo tenta classificar o rótulo que existe no registro. O estudo não dispõe de uma referência clínica independente para validar diagnóstico. A revisão mantém a A1 entregue como histórico e torna as novas decisões explícitas.

**Pergunta possível:** Qual é a contribuição principal?

**Resposta:** A revisão completa dos atributos e a comparação entre famílias com as mesmas entradas e folds externos.

**Fontes locais:** Parecer_Semantico_e_Decisoes.md, protocol_before_results.json.

## 2. Tarefa e significado do alvo

Responsável sugerido: Antônio Henrique Queiroz Villar Lopes. Tempo: 1:00.

A tarefa é uma classificação supervisionada binária. A classe positiva é Anormal. O dicionário descreve o alvo como ausência ou presença de patologia cardíaca, mas não informa quem atribuiu o rótulo, quais exames serviram como referência nem em qual momento cada campo ficou disponível. Isso importa porque prever a decisão registrada é diferente de demonstrar detecção de doença por uma referência independente. A nossa pergunta operacional é quanto medidas disponíveis no registro permitem discriminar esse rótulo, sob uma política conservadora de atributos. As afirmações ficam condicionadas à disponibilidade das medidas antes do uso pretendido. Não chamamos a saída de diagnóstico e não inferimos causa a partir de associação.

**Pergunta possível:** O modelo prevê doença ou o registro?

**Resposta:** O rótulo registrado. A equivalência com diagnóstico independente não foi documentada.

**Fontes locais:** Variáveis do conjunto de dados (SIGAA 03-11-2026).pdf, Tema do estudo de caso.pdf.

## 3. Coorte e partições

Responsável sugerido: Antônio Henrique Queiroz Villar Lopes. Tempo: 1:10.

A fonte tem 12.873 registros e 21 variáveis. Existem 11.704 rótulos conhecidos após o mapeamento explícito. A divisão histórica contém 9.361 registros de desenvolvimento, 2.342 do teste histórico e um registro em quarentena por equivalência candidata entre partições. Essa linha permanece na base original. Os demais 1.169 registros não têm rótulo utilizável para a classificação supervisionada. A nova execução usa somente o desenvolvimento, com 9.279 componentes candidatos de agrupamento. Esses componentes ajudam a manter possíveis equivalências juntas, mas não provam identidade de paciente. O ID é declarado como do paciente anônimo no dicionário. Sua unicidade na planilha não prova estabilidade entre retornos. O teste antigo já foi explorado e não recebeu nova avaliação nesta revisão.

**Pergunta possível:** Por que não usar o teste antigo novamente?

**Resposta:** Porque a exposição anterior impede apresentá-lo como validação nova e intocada. A nova avaliação usa folds externos no desenvolvimento e assume o histórico de exploração.

**Fontes locais:** UCMF_raw.csv, a2_mining/particoes_modelagem.csv, verification.json.

## 4. Riscos de vazamento nas 21 variáveis

Responsável sugerido: Antônio Henrique Queiroz Villar Lopes. Tempo: 1:10.

A auditoria separa fatos de suspeitas. MOTIVO1 e MOTIVO2 contêm expressões como cardiopatia já estabelecida e cardiopatia congênita. O conteúdo diagnóstico é explícito, embora não saibamos se veio do mesmo processo que gerou y. SOPRO, B2 e PULSOS aparecem no material de investigação diagnóstica. Isso sugere possível incorporação, mas não prova que o fluxograma fornecido rotulou a UCMF. PPA é uma classificação derivada de hipertensão e seu vínculo com o alvo genérico permanece desconhecido. HDA contém sintomas e Assintomático, sem nomes de cardiopatia nas categorias observadas. Retiramos esse bloco da principal por proveniência incerta, com grau de suspeita diferente. Uma correlação forte, sozinha, não demonstra vazamento. A política não depende apenas do tamanho da associação.

**Pergunta possível:** Vocês provaram que SOPRO vaza o alvo?

**Resposta:** Não. A suspeita tem fundamento semântico, mas falta o protocolo do alvo e a ordem temporal. A remoção é conservadora.

**Fontes locais:** Politica_Atributos.json, Guideline for diagnostic.pdf, UCMF_raw.csv.

## 5. Conjuntos de atributos

Responsável sugerido: João Vitor Fernandes Ferreira. Tempo: 1:00.

FISIO8 contém Peso, Altura, IMC, IDADE, pressões sistólica e diastólica, frequência cardíaca e sexo. STRICT4 conserva Peso, Altura, IDADE e SEXO. Essa escolha foi documentada pelo tipo de informação antes da leitura dos novos resultados. STRICT4 testa uma alternativa mais restrita porque medidas de pressão ou frequência poderiam participar de critérios diagnósticos não documentados. Se HAS integrar o alvo, tirar PPA e manter suas pressões não elimina necessariamente essa informação. STRICT4 também retira o IMC histórico, reduzindo dependência de uma derivação antiga. Por retirar quatro atributos juntos, a diferença entre os conjuntos não identifica o efeito isolado de cada um. Nenhum conjunto recebe certificado de ausência de vazamento.

**Pergunta possível:** Por que manter medidas que podem estar no critério?

**Resposta:** FISIO8 estuda medidas básicas sob uma premissa temporal explícita. STRICT4 documenta a sensibilidade à alternativa mais restrita. A falta de referência impede certeza nos dois.

**Fontes locais:** Politica_Atributos.json, protocol_before_results.json.

## 6. Pré-processamento no treino

Responsável sugerido: João Vitor Fernandes Ferreira. Tempo: 1:00.

A limpeza reconhece grafias, sentinelas e valores suspeitos sem transformar desconhecido em Normal. O alvo recebe apenas o mapeamento explícito de valores válidos. Não corrigimos seu conteúdo com base em SOPRO ou outro achado. As transformações que aprendem com a amostra, como imputação por mediana, escalas e categorias, são ajustadas no treino de cada fold. A busca compara a imputação global e a baseada em idade, quando previstas para a família. Cada validação recebe somente a transformação aprendida no seu treino. Indicadores de ausência merecem cuidado: podem captar o processo de medição, e retirar o indicador explícito não remove necessariamente a marca deixada pela mediana imputada. As derivações mantêm rastreabilidade e as exclusões também valem para codificações dos campos retirados.

**Pergunta possível:** Por que não imputar antes de dividir?

**Resposta:** Porque a mediana, a escala e o vocabulário passariam a conhecer os registros que deveriam apenas avaliar o modelo.

**Fontes locais:** preprocessing_audit.json, protocol_before_results.json, Politica_Atributos.json.

## 7. Validação aninhada

Responsável sugerido: João Vitor Fernandes Ferreira. Tempo: 1:40.

Usamos cinco folds externos e três internos. Pensem primeiro em uma divisão externa: quatro partes ficam no treino e uma fica reservada para avaliar. Dentro das quatro partes de treino, os três folds internos comparam os hiperparâmetros de cada família. A seleção usa a média da acurácia balanceada interna. Depois ajustamos a configuração escolhida em todo o treino externo e produzimos as previsões da parte externa. Repetimos o processo cinco vezes, trocando a parte externa. Assim cada registro recebe uma previsão de um modelo que não o usou no próprio ajuste nem na seleção interna daquela previsão. Concatenamos essas previsões externas para formar as métricas OOF. As quatro famílias e os dois conjuntos usam as mesmas divisões externas, o que permite comparação pareada. Mantemos os grupos candidatos juntos. Isso reduz cruzamento de equivalências candidatas, mas não assegura que todos os retornos de uma pessoa foram detectados. A avaliação é interna à mesma coorte e permanece condicionada a decisões históricas já exploradas.

**Pergunta possível:** O que significa uma previsão OOF?

**Resposta:** É uma previsão produzida quando aquela linha estava no fold externo de avaliação. O ajuste e a escolha interna ocorreram nas demais partes.

**Fontes locais:** protocol_before_results.json, outer_membership.csv, verification.json.

## 8. Algoritmos e métricas

Responsável sugerido: Mateus Nery Bailão. Tempo: 0:50.

A referência prevê sempre a classe mais frequente e mostra o desempenho sem discriminação individual. A logística oferece uma relação regularizada e simples de interpretar. A árvore permite regras não lineares, e a floresta agrega várias árvores. A busca tem 105 configurações no total: uma referência, 48 árvores, 32 logísticas e 24 florestas. Escolhemos hiperparâmetros dentro de cada família para não comparar uma família ajustada com outra arbitrariamente fixada. A métrica de seleção é a acurácia balanceada, média da sensibilidade e da especificidade. Apresentamos também ROC-AUC, sensibilidade e especificidade. O limiar é 0,5, sem ajuste no teste histórico. Uma acurácia comum aparentemente razoável pode esconder o fato de a referência nunca reconhecer a classe Anormal.

**Pergunta possível:** Por que acurácia balanceada?

**Resposta:** Ela dá o mesmo peso ao acerto de cada classe. A referência tem 57,6% de acurácia comum, mas 50% de BA e sensibilidade zero.

**Fontes locais:** protocol_before_results.json, family_nested_metrics.csv.

## 9. Comparação principal

Responsável sugerido: Mateus Nery Bailão. Tempo: 1:10.

Esta tabela resume as previsões externas de FISIO8. A floresta apresenta a maior acurácia balanceada observada, 62,9%, com ROC-AUC de 0,672. Sua sensibilidade é 59,3% e a especificidade é 66,4%. A referência fica em 50% de BA. A logística e a árvore também superam numericamente essa referência, mas o ganho de complexidade não produz uma discriminação elevada. Todos os valores vêm das mesmas 9.361 linhas e dos mesmos folds externos. Não confundimos esse resumo com desempenho de treinamento, nem com o escore usado para escolher a configuração final. A maior média observada entre famílias não é uma demonstração de superioridade clínica ou uma validação externa confirmatória. A interpretação precisa considerar a incerteza e os erros, que mostramos a seguir.

**Pergunta possível:** Esse é o resultado do modelo treinado em todos os dados?

**Resposta:** Não. São predições externas da validação aninhada. O ajuste final em todo o desenvolvimento serve à reprodução e não substitui a estimativa OOF.

**Fontes locais:** family_nested_metrics.csv, outer_fold_metrics.csv.

## 10. Erros da floresta em FISIO8

Responsável sugerido: Mateus Nery Bailão. Tempo: 1:00.

A matriz usa linha para o rótulo registrado e coluna para a classe predita. Entre 5.394 registros Normal, o modelo classifica 3.584 como Normal e 1.810 como Anormal. Entre 3.967 registros Anormal, classifica corretamente 2.352 e deixa 1.615 como Normal. Assim, aproximadamente 40,7% dos anormais registrados não são reconhecidos nesse limiar. Falso positivo significa divergir do rótulo Normal, e falso negativo significa divergir do rótulo Anormal. Como a referência clínica do alvo não é independente e validada, tratamos esses termos como erros de classificação do registro. A matriz mostra por que um resumo único de desempenho é insuficiente e por que não há base para propor uso diagnóstico.

**Pergunta possível:** Um falso negativo aqui significa doença não detectada?

**Resposta:** Significa previsão Normal quando o rótulo registrado é Anormal. A interpretação clínica exige referência validada, que não temos.

**Fontes locais:** family_nested_metrics.csv, oof_FISIO8_forest.csv.

## 11. Dependência dos atributos

Responsável sugerido: Mateus Nery Bailão. Tempo: 0:50.

A importância por permutação usa o próprio fold externo. Primeiro calculamos a BA naquele fold. Depois embaralhamos uma variável nesse conjunto e medimos quanto a BA cai, mantendo o modelo ajustado. O gráfico resume cinco folds e três repetições por variável na floresta FISIO8. A maior queda média aparece em FC, 4,8 pontos percentuais, seguida por Peso. Isso mostra dependência preditiva desse modelo na amostra avaliada. Não demonstra que FC causa a condição, que foi registrada antes de y ou que é independente do critério diagnóstico. Variáveis correlacionadas podem substituir umas às outras, e uma importância pequena não prova irrelevância individual. A presença forte de FC reforça o valor de olhar a sensibilidade STRICT4.

**Pergunta possível:** Importância é causalidade?

**Resposta:** Não. É a perda de desempenho do modelo ao perturbar uma entrada no fold externo, condicionada às outras variáveis e ao modelo.

**Fontes locais:** outer_permutation_importance.csv.

## 12. Sensibilidades e processo de coleta

Responsável sugerido: Pedro Augusto Ferreira Matos. Tempo: 1:00.

A comparação com STRICT4 mantém a população e as divisões externas. A BA observada da floresta cai de 62,9% para 59,5%. A logística em STRICT4 fica em 59,7%. Isso é uma sensibilidade ao conjunto de informação, sem trocar retrospectivamente a principal pelo melhor valor. Também ajustamos uma árvore fixa usando apenas máscaras de disponibilidade. Em FISIO8 ela alcança BA de 56,1%, mostrando sinal no padrão de preenchimento. Esse ensaio usa somente desenvolvimento e não equivale à busca aninhada das famílias. Um controle com rótulos permutados fica próximo de 50%, mas é diagnóstico auxiliar, sem p-valor formal e sem provar ausência de vazamento. Os controles sustentam uma interpretação cuidadosa do processo de registro.

**Pergunta possível:** FISIO8 ser melhor prova que as medidas são legítimas?

**Resposta:** Não. Prova apenas uma diferença preditiva neste protocolo. A admissibilidade depende da origem e do momento das medidas.

**Fontes locais:** family_nested_metrics.csv, collection_process_controls.csv, permuted_label_control.json.

## 13. Limites da evidência

Responsável sugerido: Pedro Augusto Ferreira Matos. Tempo: 1:00.

A principal limitação é a falta de definição operacional e de referência independente do alvo. A segunda é a sequência de coleta: não temos horários nem histórico de atualização dos campos clínicos. A terceira é a representatividade, porque são registros de um serviço de cardiologia e a modelagem supervisionada depende de rótulo disponível. Os grupos são candidatos, sem identidade de paciente confirmada. Além disso, a coorte e escolhas de qualidade já receberam exploração anterior. A validação aninhada protege a seleção interna de hiperparâmetros desta execução, mas não apaga decisões históricas. O teste antigo não foi reavaliado. Mesmo retirando campos suspeitos, não afirmamos que o conjunto está livre de todos os mecanismos de vazamento. São limites que afetam a conclusão, e não detalhes que uma métrica alta resolveria.

**Pergunta possível:** Qual informação faltante mais mudaria o estudo?

**Resposta:** O protocolo de formação do alvo e a ordem de obtenção das entradas. Isso permitiria decidir sobre incorporação e disponibilidade temporal.

**Fontes locais:** Parecer_Semantico_e_Decisoes.md, protocol_before_results.json, verification.json.

## 14. Conclusão

Responsável sugerido: Pedro Augusto Ferreira Matos. Tempo: 1:10.

A revisão auditou as 21 variáveis e comparou quatro famílias com a mesma entrada e as mesmas divisões externas. A maior BA observada em FISIO8 é 62,9%, na floresta. Esse resultado indica discriminação limitada do rótulo registrado e precisa ser lido junto dos 1.615 falsos negativos de registro e dos 1.810 falsos positivos. A política conservadora exclui os campos de diagnóstico prévio, os achados de maior incerteza e as classificações derivadas. Ela não transforma o alvo em referência independente. O próximo avanço não é apenas buscar outro algoritmo: é esclarecer a formação do rótulo, a ordem de coleta e a identidade estável entre retornos, e então obter uma avaliação confirmatória separada. Os dados originais e a A1 permanecem preservados. O código, as sementes, o protocolo e os manifestos permitem conferir as decisões e os resultados desta execução.

**Pergunta possível:** O que vocês defendem ao final?

**Resposta:** Uma comparação reprodutível e uma política de atributos justificável, com melhora numérica sobre a referência e limites explícitos. Não defendemos diagnóstico clínico validado.

**Fontes locais:** family_nested_metrics.csv, Politica_Atributos.json, manifest.json.

## 15. Matriz das 21 variáveis, parte 1 (apoio)

ID: O número não é medida clínica e seu uso pode aprender organização do arquivo. Evidência: O dicionário declara ID do paciente anônimo; todos os IDs observados são distintos. Alternativa: Usar como chave de agrupamento apenas se houver confirmação de estabilidade; analisar agrupamentos candidatos separadamente. Limite: Não renomear conceitualmente como ID de atendimento nem afirmar que IDs distintos provam pessoas distintas.

Peso: Preserva informação antropométrica sem conteúdo diagnóstico explícito documentado. Evidência: Dicionário e valores numéricos observados; nenhuma fonte define Peso como cópia de y. Alternativa: Retirar em análise de sensibilidade; comparar com e sem indicadores de ausência no desenvolvimento. Limite: Peso pode ser consequência de doença/tratamento. Se medido depois do instante de uso, a inclusão deixa de ser defensável.

Altura: É uma medida basal, embora também participe de classificações derivadas. Evidência: Dicionário e explicação de PPA associam medidas corporais às referências pediátricas. Alternativa: Retirar isoladamente para avaliar redundância; não reconstruir valores com o alvo. Limite: Ser pai de PPA não torna automaticamente Altura uma variável vazada; a interpretação depende do alvo e do instante.

IMC: A principal permite uma representação usual da antropometria; a sensibilidade reduz redundância e dependência de cálculo histórico. Evidência: O complemento explica IMC a partir de peso e altura, sem usar y. Alternativa: FISIO sem IMC ou IMC recalculado apenas de pais observados, como ensaios de desenvolvimento. Limite: STRICT também remove pressões e FC; sua diferença de escore não identifica isoladamente o efeito do IMC.

Atendimento: Evita apresentar época de cadastro como explicação clínica. Evidência: O dicionário define data da visita; a base contém formatos e valores que exigem interpretação. Alternativa: Examinar estabilidade por período ou corte temporal, se o parser e a suficiência amostral forem verificados. Limite: Um corte pela data de visita não recupera horário pré-rótulo, não valida séculos ambíguos e não garante separação por paciente.

DN: Conserva idade sem fornecer a data exata ao classificador. Evidência: Dicionário e presença de datas na fonte. Alternativa: Agrupar candidatos por DN e outros campos apenas como sensibilidade, sem chamar grupos de pacientes confirmados. Limite: Pessoas distintas podem compartilhar DN; a coincidência não prova identidade e pode fundir pessoas diferentes.

IDADE: Permite contextualizar medidas corporais e fisiológicas sem levar as datas exatas a X. Evidência: Dicionário; diferença entre data da visita e nascimento é uma derivação disponível. Alternativa: Comparar forma contínua e faixas fixas no desenvolvimento; não escolher faixas pelo teste histórico. Limite: Calcular pela data atual ou por uma visita futura mudaria o instante da previsão; erros das datas podem propagar-se.

**Fontes locais:** Politica_Atributos.json, Parecer_Semantico_e_Decisoes.md.

## 16. Matriz das 21 variáveis, parte 2 (apoio)

Convenio: A pergunta principal privilegia medidas do paciente e reduz dependência da origem administrativa. Evidência: Dicionário identifica seguro; A1 descreve associações com o alvo, sem demonstrar mecanismo causal. Alternativa: Auditar desempenho por grupos administrativos e seu acréscimo apenas no desenvolvimento. Limite: Associação com doença não prova leakage. A exclusão também é uma escolha de transportabilidade e de escopo.

PULSOS: O material diagnóstico usa características dos pulsos para distinguir condições; há risco de reproduzir a decisão registrada. Evidência: Fluxograma inclui ramo dos pulsos; categorias observadas são coerentes com esse tipo de exame. Alternativa: Adicionar o bloco de pulsos no desenvolvimento para medir dependência preditiva, sem promovê-lo à comparação principal. Limite: Não há prova de que o profissional que atribuiu y usou esse ramo; um achado prévio a referência independente pode ser preditor legítimo.

PA SISTOLICA: Mantém a proposta de classificar o registro a partir de medidas; a sensibilidade testa dependência de medidas potencialmente diagnósticas. Evidência: PPA é derivada das pressões segundo as fontes; o alvo só é definido genericamente como patologia cardíaca. Alternativa: Comparar FISIO sem o bloco de pressões e STRICT no desenvolvimento. Limite: Se HAS integrar y, a pressão pode reconstruir parte do critério. Retirar PPA não remove seus pais nem estabelece independência.

PA DIASTOLICA: Aplica a mesma regra semântica a ambas as pressões. Evidência: A explicação complementar apresenta elevação sistólica ou diastólica como fundamento da classificação de HAS. Alternativa: Retirar conjuntamente PAS/PAD para avaliar o bloco; retirada individual não elimina a informação da outra. Limite: A fraca associação agregada que eventualmente surgir não demonstra que a variável era disponível nem que não entrou no critério.

PPA: Evita fornecer ao classificador uma classificação clínica pronta cuja relação com y não está esclarecida. Evidência: Dicionário e complemento descrevem a construção da variável; valores observados incluem classes de HAS. Alternativa: Acréscimo exploratório no desenvolvimento e comparação de valores observados com derivações verificáveis. Limite: Não afirmar doença confirmada por um único valor; não calcular PPA de pressões imputadas para fabricar diagnóstico. Os pais remanescentes em FISIO exigem ressalva.

NORMAL X ANORMAL: Prever a informação registrada sem entregar essa mesma informação ao modelo. Evidência: O dicionário identifica explicitamente a coluna-alvo; há grafias e valores inválidos que exigem mapeamento explícito. Alternativa: Não há alternativa legítima de incluí-lo em X; modelar outro desfecho exige nova definição do problema. Limite: A auditoria não encontrou protocolo para chamar y de diagnóstico independente. Usá-lo em X seria vazamento direto, mas não foi constatado esse uso no schema canônico.

B2: Há risco de reutilizar achado que participou da própria decisão e de exigir exame ausente no estágio pretendido. Evidência: Fluxograma e anexos do material complementar mencionam tipos de B2; dicionário confirma significado. Alternativa: Analisar isoladamente e acrescentar bloco de ausculta no desenvolvimento. Limite: Alta associação não comprova leakage. Um protocolo de coleta prévia e referência independente poderia mudar a decisão.

**Fontes locais:** Politica_Atributos.json, Parecer_Semantico_e_Decisoes.md.

## 17. Matriz das 21 variáveis, parte 3 (apoio)

SOPRO: A remoção conservadora evita depender de um achado fortemente ligado à avaliação diagnóstica fornecida. Evidência: O material pergunta sobre existência de sopro e descreve tipos nos anexos. Alternativa: Ablação e ensaio de variável única apenas no desenvolvimento; referência independente seria necessária para alegação clínica mais forte. Limite: Sopro é um achado, não sinônimo de cardiopatia. Nem associação forte nem previsão imperfeita resolvem a questão de proveniência.

FC: Preserva medida simples na principal e permite sensibilidade a possível contribuição diagnóstica. Evidência: Dicionário a distingue de PULSOS; não foi localizado critério específico que transforme FC em y. Alternativa: Remover FC isoladamente no desenvolvimento, além de STRICT. Limite: Não encontrar regra no material não prova independência. Se medida após conduta ou usada para adjudicar arritmia, a interpretação muda.

HDA 1: A temporalidade e a possível incorporação não estão esclarecidas, embora a evidência seja mais fraca que em MOTIVO. Evidência: As categorias reais não nomeiam cardiopatias estabelecidas; o dicionário é genérico quanto ao momento. Alternativa: FISIO acrescido de HDA1/HDA2 no desenvolvimento, declarando hipótese de anamnese disponível. Limite: Não chamar HDA de conteúdo diagnóstico comprovado, não equiparar sintomas a laudo e não usar melhora de escore para apagar a lacuna temporal.

HDA2: Além da incerteza de proveniência, a informação é muito esparsa e não justifica misturar mecanismos no resultado central. Evidência: 12.466 de 12.873 registros brutos têm campo vazio; os valores preenchidos são sintomas e categorias genéricas. Alternativa: Bloco HDA com e sem HDA2 no desenvolvimento, preservando os mesmos folds. Limite: Baixa cobertura não prova leakage. A ausência pode ser legítima ou processual; sua origem não foi estabelecida.

SEXO: Preserva contexto básico sem conteúdo de diagnóstico explícito. Evidência: Dicionário e categorias históricas M/F, suas grafias e Indeterminado. Alternativa: Retirar isoladamente no desenvolvimento para avaliar dependência; desconhecimento deve permanecer representado sem imputação por y. Limite: Não assumir que Indeterminado é uma categoria clínica nem que toda informação histórica é adequadamente representada pela binarização.

MOTIVO1: Para uma análise conservadora sem diagnóstico pronto, o conteúdo de cardiopatia estabelecida torna a inclusão inadequada. Evidência: A fonte tem 1.158 ocorrências de Cardiopatia já estabelecida, além de suspeita, parecer, check-up e outro. Alternativa: Auditar a contribuição do bloco de motivos somente no desenvolvimento; uma tarefa de reavaliação de pacientes já diagnosticados teria outra definição. Limite: Motivo prévio pode ser legítimo numa tarefa explicitamente posterior ao encaminhamento; esta política não prova que seu valor foi copiado do alvo.

MOTIVO2: A análise principal não deve reutilizar categorias que já anunciam cardiopatia. Evidência: Há 1.041 ocorrências de Cardiopatia congenica e 92 de Cardiopatia adquirida; outras categorias incluem Sopro e HAS/dislipidemia/obesidade. Alternativa: Acréscimo exploratório do bloco de motivos no desenvolvimento, sem recuperar suas categorias sob nomes derivados. Limite: O conjunto é heterogêneo: nem toda categoria contém diagnóstico. Isso não torna a coluna adequada à principal nem demonstra leakage em todas as linhas.

**Fontes locais:** Politica_Atributos.json, Parecer_Semantico_e_Decisoes.md.

## 18. Métricas e classe positiva (apoio)

TP e TN representam concordância com os rótulos registrados. FP e FN representam divergência. A referência que prevê Normal para todos tem sensibilidade zero e especificidade um, portanto BA de 0,5. AUC usa os escores ao longo de limiares e não prova calibração. A definição da classe positiva e o limiar permanecem fixos para as comparações.

**Fontes locais:** family_nested_metrics.csv, protocol_before_results.json.

## 19. Espaço de busca por família (apoio)

Árvore: profundidades 2, 4 e 6, folhas mínimas 20 ou 50, critérios gini/entropy, peso padrão ou balanceado e imputação global ou por idade. Logística: C em 0,01, 0,1, 1 e 10, pesos, duas imputações e representações padronizada ou log/padronizada. Floresta: 150 árvores, profundidade 4, 8 ou ilimitada, folhas 10 ou 30, pesos e imputação. A contagem total de 105 representa o produto das opções em cada família. O número de candidatos não implica o mesmo custo computacional. O protocolo congela a ordem para desempates.

**Fontes locais:** protocol_before_results.json.

## 20. Ensaios com variável única (apoio)

Os ensaios usam uma variável por vez para investigar associação preditiva no desenvolvimento e não para selecionar campos admissíveis. Sua configuração e interpretação são distintas da validação aninhada das famílias. Variáveis preparadas podem manter informação de seus pais determinísticos. Mesmo um escore muito alto não prova incorporação nem retrospectividade, e um baixo não absolve diagnóstico prévio. Os ensaios não participam da escolha do modelo principal.

**Fontes locais:** variable_probes.csv, protocol_before_results.json.

## 21. Fontes e reprodução (apoio)

Fontes primárias: Tema do estudo de caso.pdf, Variáveis do conjunto de dados (SIGAA 03-11-2026).pdf, complementos Guideline for diagnostic.pdf e Explanation about the PPA variable.pdf. A1 é fonte secundária preservada. A rubrica recebida em 07/11/2026 exige artigo IEEE curto e exclusão de campos com leakage. Código e execução: src/kdd_revision/rubric_audit.py, artifacts/a2_rubric_audit/protocol_before_results.json, verification.json e manifest.json. A origem bruta permanece local e não está embutida no deck. IA generativa: Codex/OpenAI apoiou scripts, auditoria, organização metodológica e redação. O grupo deve compreender e conferir todos os resultados e responder pela entrega. Nenhuma alegação de revisão humana posterior é pressuposta.

**Fontes locais:** Politica_Atributos.json, manifest.json, verification.json.

## Preparação conjunta

Cada integrante deve conseguir explicar a classe positiva, a diferença entre treino interno e avaliação externa, o motivo das exclusões, a interpretação da matriz e os limites da referência do alvo. Ensaiar a transição entre autores. O tempo indicado é uma meta de ensaio, não uma medição de apresentação real. Os slides de apoio não entram nos 14 min 30 s.
