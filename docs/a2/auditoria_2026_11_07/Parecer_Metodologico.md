# Parecer metodológico da revisão da A2

> **Fechamento em 11/11/2026.** A reprodução integral em pasta separada reconstruiu a partição por código e repetiu a busca sem pontuar o teste histórico. A verificação dos hashes, das 40 escolhas externas e das métricas recalculadas a partir das previsões está em [Verificacao_Experimental.json](Verificacao_Experimental.json). Isso encerra REP-01, REP-02 e VAL-01. As seções a seguir registram o parecer técnico e o estado no momento da auditoria inicial.

Data: 7 de novembro de 2026. Referência histórica: commit `c8c86e333468cc3cbb1307288f409065166d8d6c`. Este parecer é um documento suplementar de auditoria; não substitui o artigo IEEE de até cinco páginas exigido para a entrega.

**Estado verificável:** não há bloqueador confirmado de vazamento computacional no novo laço de comparação por família; sua execução ainda estava em curso no snapshot revisado. Há duas pendências concretas de reprodução, indexadas como **REP-01** (bootstrap da membresia ignorada no Git) e **REP-02** (manifesto de dependências/entradas), além de **VAL-01** (conferência dos contratos de integração). O registro de estados está em [conformidade_rubrica.json](conformidade_rubrica.json); a análise do código novo está na [seção final](#revisão-estática-da-implementação-nova-em-execução). Nenhuma pontuação nova é inventada ou certificada aqui.

## Objeto, fontes e alcance da conclusão

A revisão examinou o código canônico de preparação, transformação, mineração, avaliação, aplicação e reprodução, seus testes e os resultados agregados da execução c8. Também examinou estaticamente o novo módulo `rubric_audit.py`, seu CLI e seus testes; o estado dessa implementação consta ao final. As cópias locais com sufixo ` 2` foram preservadas e não foram tratadas como fontes canônicas. A rubrica recebida em 07/11/2026 foi lida integralmente; sua identificação e SHA-256 estão em [fonte_rubrica.json](fonte_rubrica.json). A interpretação e as lacunas das 21 variáveis estão em [tabela_semantica_21.json](tabela_semantica_21.json).

Há duas conclusões diferentes. A implementação histórica contém controles efetivos contra o ajuste de medianas, vocabulários e escalas sobre validação ou teste. Entretanto, esses controles não estabelecem que todos os atributos antecedem o diagnóstico, que os grupos representam pessoas diferentes ou que o conjunto histórico de teste permaneceu desconhecido durante o desenvolvimento. Por isso, não é defensável certificar o projeto como “100% sem vazamento”. É possível verificar mecanismos computacionais e declarar precisamente as condições sob as quais uma avaliação interna é interpretável.

Os riscos de SOPRO, B2, PULSOS, PPA, HDA e MOTIVO devem ser julgados por significado, origem e disponibilidade. Uma associação elevada com y ou a perda de desempenho após retirar uma variável não prova vazamento. Inversamente, o ajuste correto dentro dos folds não torna admissível uma variável que revele um diagnóstico já conhecido ou só esteja disponível depois do instante de uso pretendido.

O dicionário descreve NORMAL X ANORMAL como ausência/presença de patologia cardíaca. Não documenta examinador, exames, instante de adjudicação, cegamento nem um padrão de referência independente. A tarefa verificável é, portanto, classificar o rótulo registrado da base, sob hipóteses explícitas de disponibilidade dos preditores. O estudo não demonstra eficácia de primeira detecção, antecipação de um diagnóstico ou desempenho em pessoas novas.

## Proteções efetivamente presentes em c8

`src/kdd_revision/prepare.py:128` e `preprocessing/preparation.py:50` aplicam regras por registro. Não há quantis amostrais usados para reparar medidas nem preenchimento de y a partir de X. A normalização das grafias do alvo é a codificação de y, não seu uso como preditor. IDs, datas absolutas, alvo e metadados não entram em X por inferência de tipo.

Em `mining.py:122–135`, cada treino de fold ajusta seu próprio pré-processador; o cache é descartado ao mudar de fold. `preprocessing/transformer.py:38–75` recusa y e aprende medianas, vocabulário, médias e desvios somente no `fit`. O valor de validação não altera esses parâmetros durante `transform`. A mediana global e a condicional por idade competem novamente na busca interna; a escolha exploratória de reconstrução de valores ausentes não é simplesmente herdada por todos os classificadores.

PCA e reamostragem são ajustadas no treino em `mining.py:87–106`; os laços de sensibilidade reajustam os modelos em cada treino de fold. Reamostrar depois de ajustar a transformação no treino original é uma escolha legítima: não envolve validação ou teste. O limiar de decisão foi fixado em 0,5, e os candidatos finais de todos os cenários foram registrados antes de sua pontuação na execução c8 (`full_kdd.py:138–146`).

As verificações de grupos impedem cruzamento dos componentes candidatos reconhecidos. A preparação colocou uma linha de desenvolvimento em quarentena por equivalência com o teste; a união transitiva posterior não exigiu outras. São 9.361 registros e 9.279 componentes no desenvolvimento, contra 2.342 registros e 2.321 componentes no teste. Isso demonstra separação dos componentes definidos, não identidade longitudinal de pacientes.

Os testes de `test_mining_current.py`, `test_preprocessing.py` e `test_full_kdd_artifacts.py` exercitam ajuste restrito ao treino, estatísticas aprendidas, cobertura das validações, parâmetros por fold, grupos e rejeição de campos proibidos. Esta auditoria não executou a suíte nem a busca histórica. Um teste técnico pode confirmar o contrato implementado; não resolve a origem clínica de uma coluna.

## Achados e limites confirmados

| Achado | Evidência canônica | Classificação e consequência |
|---|---|---|
| A coorte e o teste histórico já haviam sido explorados. | `full_kdd.py:47–48`, `:132–133` e `:195`; `resultados/a2/kdd_completo/verification.json:16–20`. | Limite importante, confiança 100%. A nested CV estima a busca congelada condicionada à preparação prévia; não avalia de forma intocada toda a seleção do KDD. |
| A tabela principal compara cenários com X distintos, e o teste avalia apenas o vencedor de cada cenário. | `full_kdd.py:114–118`, `:141–152`; `Relatorio_A2_KDD_Completo.md:80–84`. | Lacuna comparativa para a nova entrega, confiança 100%. A árvore de A e a floresta de B não isolam o efeito da família. Existem comparações de CV por família nos CSVs; elas não devem ser confundidas com confirmação externa dos melhores candidatos. |
| A variante “sem indicadores” retira somente os sete indicadores numéricos. | `mining.py:90`; `preprocessing/transformer.py:59–66` e `:103–106`. | Limite da ablação, confiança 100%. Continuam 9, 1 e 6 estados categóricos de ausência em A, B e B_contexto. A variante deve ser nomeada “sem indicadores numéricos”. |
| Os grupos são equivalências candidatas, não chaves confirmadas de paciente. | `mining.py:157–176`; `full_kdd.py:29–34` e `:99–106`. | Limite de independência, confiança 100%; contaminação residual entre pessoas não foi demonstrada. Não se pode afirmar generalização para pacientes novos com base somente nesses hashes. |
| Variáveis derivadas e transformações podem conservar informação de um campo retirado de X. | `preprocessing/preparation.py:57–73` e `:96–113`; `preprocessing/transformer.py:34–36`. | Propriedade confirmada do fluxo, confiança 100%; vazamento concreto por esse caminho não foi demonstrado. Exclusões futuras precisam seguir a linhagem e os insumos implícitos da imputação. |
| A admissibilidade dos achados e motivos não é garantida pelo desenho de CV. | Listas em `schema.py:10`; fontes e lacunas em `tabela_semantica_21.json`. | Risco semântico importante. MOTIVO contém conteúdo diagnóstico explícito; sua relação com o mesmo diagnóstico-alvo e o instante de uso continuam condicionados ao objetivo. A exclusão conservadora não deve ser apresentada como prova retrospectiva de que toda associação era vazamento. |

Não foi encontrado no código canônico um estimador de mediana, vocabulário ou escala ajustado na coorte inteira e reutilizado na CV de mineração. Também não foi encontrada seleção univariada automatizada por y antes dos folds. Esse resultado da revisão não exclui influência humana das explorações anteriores sobre a definição da preparação, da grade ou dos cenários; essa influência é reconhecida no próprio protocolo.

O registro “all_selections_frozen_before_test” verifica a ordem desta execução. Ele é útil para impedir ajuste posterior dos seus candidatos, mas não é prova de pré-registro independente anterior a qualquer contato histórico com os dados. Nova divisão aleatória da mesma base também não apaga esse contato.

## Ausência, derivados e conduta de coleta

Na amostra de desenvolvimento c8, a fração de Anormal é 29,33% quando MOTIVO2 está ausente e 46,26% quando está presente. Para PAS, os valores são 47,02% e 36,48%; para HDA1, 34,20% e 45,40%. São frequências descritivas calculadas sobre o desenvolvimento já conhecido, antes de qualquer novo experimento. Mostram que o preenchimento contém informação associada ao rótulo; não identificam se a causa foi conduta diagnóstica, seleção do serviço, época, estado do paciente ou outro fator.

Retirar apenas as colunas categóricas `__AUSENTE__` não elimina essa informação: o vetor one-hot todo zero ainda distingue uma categoria vazia das categorias observadas. Imputação pela moda do treino é uma alternativa que evita esse marcador explícito. Nas numéricas, mesmo sem um bit de imputação, a concentração em uma mediana pode continuar identificável. Assim, “sem indicador explícito” não equivale a “sem qualquer sinal de ausência”. Um modelo que recebe somente máscaras de disponibilidade é um diagnóstico útil, mas uma pontuação acima do acaso desse controle não prova, sozinha, vazamento.

A idade derivada de Atendimento e DN e o IMC derivado de Peso e Altura não usam y no código. Redundância entre preditores também não é vazamento por si. O cuidado necessário é com a disponibilidade e a linhagem: retirar Peso e conservar IMC calculado ainda conserva informação de Peso; retirar IDADE de X e continuar a imputação condicionada por idade ainda usa IDADE. Em c8 há três registros de desenvolvimento com IMC histórico utilizável e pelo menos um pai indisponível no X, e nenhum registro desse tipo no teste. Preservar o IMC histórico é um tradeoff legítimo de aproveitamento, mas não comprova quando ele foi obtido.

Excluir PPA não exclui automaticamente seus pais PAS/PAD, nem demonstra que esses pais sejam indevidos. Se hipertensão tiver integrado a definição do alvo, as medidas podem reconstruir parte do critério; as fontes disponíveis não estabelecem isso. A sensibilidade sem pressão e FC é uma maneira transparente de avaliar dependência desses insumos, sem afirmar previamente que toda informação fisiológica relacionada à doença é proibida.

## Protocolo da revisão metodológica

O desenho abaixo está implementado em `src/kdd_revision/rubric_audit.py` e a execução foi iniciada. Na inspeção estática já existiam o protocolo anterior aos resultados, o mapa de folds e artefatos parciais de ajuste; isso não demonstra conclusão da execução. O estado final deve ser conferido nos seus próprios artefatos e em [conformidade_rubrica.json](conformidade_rubrica.json). Nenhuma métrica nova é atribuída a um experimento apenas por estar planejado ou iniciado.

### População, X e papel dos cenários

O novo estudo usa somente os 9.361 registros do desenvolvimento histórico, com os mesmos grupos candidatos conservadores. Os 2.342 registros do teste histórico não devem ser reaplicados para selecionar famílias, atributos, políticas de ausência, limiares ou hiperparâmetros. A preparação determinística pode manter os registros na base local, mas o laço experimental da revisão não deve consultar seus resultados.

| Conjunto | Preditores | Papel e condição de interpretação |
|---|---|---|
| FISIO8 | Peso, Altura, IMC, IDADE, PA SISTOLICA, PA DIASTOLICA, FC, SEXO. | Cenário principal fisiológico, condicionado à hipótese de medidas disponíveis no estágio de uso. Retira os blocos de achados, diagnóstico derivado, história e encaminhamento. Não é certificação da temporalidade restante. |
| STRICT4 | Peso, Altura, IDADE, SEXO. | Sensibilidade mais restrita; retira IMC, PAS, PAD e FC. Ajuda a avaliar dependência de medidas potencialmente mais próximas do critério clínico e da redundância de IMC. Não confirma uma cronologia que a fonte não fornece. |

ID, Atendimento, DN e os grupos permanecem metadados; datas só alimentam a derivação documentada de idade. Convenio fica fora de X. NORMAL X ANORMAL é exclusivamente y. PULSOS, B2, SOPRO, PPA, HDA1, HDA2, MOTIVO1 e MOTIVO2 ficam fora de todos os cenários principais. São exclusões conservadoras por risco ou incerteza de disponibilidade; não oito constatações equivalentes de vazamento confirmado.

Os cenários antigos A e B_contexto permanecem históricos. Provas auxiliares de um campo suspeito, inclusão/retirada de campos e modelos de ausência são investigações exploratórias. Se forem executadas, devem permanecer separadas da tabela comparativa principal, sem acesso ao teste histórico e sem reclassificar o melhor resultado auxiliar como confirmação do protocolo.

### Comparação entre famílias e validação

A avaliação principal usa cinco folds externos `StratifiedGroupKFold` e três folds internos em cada treino externo. Os membros externos devem ser exatamente os mesmos entre logística, árvore, floresta e dummy, assim como entre FISIO8 e STRICT4. O grupo não pode atravessar treino e validação. Cada registro deve receber exatamente uma predição externa por família e cenário.

A seleção de hiperparâmetros de cada família ocorre apenas nos três folds internos do respectivo treino externo. O vencedor interno é reajustado no treino externo inteiro e produz a predição do seu fold externo. A tabela principal compara essas predições OOF externas por família; não compara o máximo da CV de cada família como se fosse um teste independente. Regressão logística e árvore fornecem referências simples pertinentes; a floresta representa o modelo de maior complexidade, e o dummy é um controle sem informação de X.

Medianas, vocabulários, escala, eventual seleção de atributos, projeções e qualquer decisão adaptativa precisam pertencer ao treino correspondente. Regras determinísticas de limpeza justificadas por fonte ou domínio podem ser aplicadas por registro; se uma política for escolhida por desempenho, essa escolha passa a ser parte da seleção interna. Uma grade menor explicitamente congelada é preferível a ampliar alternativas após olhar os resultados externos e ainda chamar a avaliação de confirmatória. O número exato de candidatos, parâmetros, seeds, membros e hashes deve constar do manifesto da execução, sem ser inferido de uma estimativa de orçamento.

Acurácia balanceada deve ser acompanhada de precisão, recall, F1, especificidade, AP, ROC-AUC e matriz de confusão, com prevalência e denominadores. Métricas sem as duas classes devem ter tratamento explícito. Comparações de diferenças usam os mesmos registros externos; intervalos por componente candidato continuam condicionados à definição imperfeita desses grupos e não abrangem automaticamente toda a incerteza do KDD.

Os controles de alvo permutado e ausência total de informação servem para investigar atalhos, alinhamento e vazamento de implementação. Um controle permutado não precisa produzir exatamente 0,5 de BA, nem uma única permutação oferece um teste exato de ausência de vazamento. Correlação legítima pode permanecer nos preditores admitidos. Os controles não substituem as perguntas sobre origem de y, tempo de coleta e identidade.

### Política de aplicação

A política de suporte deve ser congelada e descrita separadamente do comparativo de classificação. A revisão histórica trocou a regra “algum campo disponível” por categorias conhecidas e pelo menos 30 exemplos com o mesmo padrão de disponibilidade (`application.py:39–44`). Não encontrei evidência de que o corte tenha sido escolhido para elevar a acurácia do teste: o código não retreina modelos nem dispõe dos alvos dos não rotulados. As métricas dos casos aceitos do teste são explicitamente secundárias (`:57–64`).

Essa mudança não deve invalidar retrospectivamente toda a seleção dos classificadores. Contudo, o corte 30 é operacional, não ótimo validado, e cobertura aceita não garante acerto. Cobertura de não rotulados não é desempenho de classificação; previsões não viram rótulos verdadeiros. Qualquer avaliação de abstenção precisa apresentar simultaneamente cobertura e erros no subconjunto aceito, sem comparar denominadores distintos como se fossem equivalentes.

## Destino dos resultados históricos

| Resultado de c8 | Uso defensável | Uso que a evidência não sustenta |
|---|---|---|
| Busca de 81 candidatos por cenário e CV de seleção. | Histórico de desenvolvimento e comparação exploratória no mesmo conjunto de folds. | Estimativa independente dos candidatos escolhidos pelo próprio máximo da CV. |
| Nested 3×3 no desenvolvimento. | Avaliação interna da busca congelada condicionada às decisões anteriores de preparação. | Validação intocada do processo completo de escolha de limpeza, atributos e população. |
| Teste histórico: BA 0,9292 em A, 0,6523 em B e 0,7416 em B_contexto. | Reprodução de uma avaliação secundária já explorada, para o rótulo registrado. | Validação externa independente, desempenho clínico ou confirmação de que os campos utilizados estavam disponíveis antes do alvo. |
| Sensibilidades e importâncias pós-seleção. | Hipóteses, dependência de insumos e análise de fragilidade. | Efeito causal da limpeza, prova isolada de vazamento ou autorização para escolher variantes pelo teste. |
| Regras de árvores adicionais. | Descrição de padrões com seus suportes de treino; identificação de qual modelo gerou a regra. | Explicação exata da floresta vencedora ou regra externamente validada. |
| Coberturas e scores dos não rotulados. | Diagnóstico de suporte e limitações da aplicação acadêmica. | Acurácia, diagnóstico confirmado ou eficácia demonstrada nos casos sem y. |

Se X ou o pré-processamento mudar na revisão, as métricas precisam ser recalculadas. Não basta apagar os nomes das variáveis do texto e manter a pontuação antiga. O cenário B antigo é uma referência mais conservadora que A, mas seus resultados também carregam o histórico de exploração e não substituem a nova comparação por família.

## Exigências da rubrica e critérios de aceite documental

A A2 exige artigo curto no template oficial de conferências da IEEE, em duas colunas e com no máximo cinco páginas. Deve conter cabeçalho com os integrantes e resumo único de 100 a 150 palavras; introdução; dados e EDA com discussão de leakage e um ou dois gráficos relevantes; metodologia; resultados e discussão; conclusão e referências. A distribuição sugerida de espaço é aproximadamente 0,5 página para cabeçalho/resumo, 0,5 para introdução, uma para dados/EDA, uma para metodologia, 1,5 para resultados e 0,5 para conclusão/referências. O limite final de cinco páginas precisa ser verificado no PDF renderizado, sem presumir uma exceção para referências.

O relatório c8 de sete páginas é material suplementar histórico, não um artigo já conforme ao novo limite. O novo PDF precisa ser inspecionado quanto a duas colunas, fontes e elementos do template, figuras legíveis, tabelas, quebras, referências e ausência de capturas de tela usadas como substituto dos resultados. Não deve conter trechos de código. O resumo deve ser contado após a redação final, com os resultados efetivamente executados; o parecer não fornece um principal resultado inventado para preencher esse espaço.

A primeira página deve ter, no rodapé, link funcional para repositório público de código organizado ou Google Colab, com seeds fixadas. Existência de um URL ou acesso autenticado do autor não comprova acesso público. É necessário verificar o destino sem depender de sessão privilegiada, sem expor a base clínica por esse motivo. Esta auditoria não acessou o GitHub, publicou conteúdo ou alterou visibilidade. A condição pública permanece sem certificação até verificação explícita; o link também precisa aparecer no rodapé da primeira página renderizada.

A apresentação tem 15 minutos e deve enfatizar metodologia e resultados. Todos os integrantes devem apresentar e podem ser escolhidos para a arguição. Slides precisam ser padronizados, numerados, com pouco texto e elementos legíveis. A submissão do relatório é em 18/11/2026; as apresentações ocorrem entre 18 e 27/11/2026, por ordem numérica dos grupos. A entrega é exclusivamente pelo SIGAA, sem aceitar como concluída uma submissão que não foi observada. Os pesos são 60% escrita do relatório, 35% apresentação e 5% segurança nas respostas. A rubrica exige informar qual IA generativa foi utilizada, onde, como e para quê.

O registro [conformidade_rubrica.json](conformidade_rubrica.json) separa requisito, evidência, estado e verificação necessária. Um protocolo descrito não é execução; execução não é diagramação IEEE; PDF local não é link público; preparação de material não é submissão nem apresentação realizada.

## Verificações de maior valor para a implementação nova

Antes de declarar o estudo computacionalmente concluído, deve-se confirmar que as predições OOF externas cobrem cada ID exatamente uma vez por família/cenário; que os hashes de membros dos folds são compartilhados; que grupos de treino e validação são disjuntos; que todos os ajustes aprendidos excluem a validação correspondente; que o módulo da revisão não lê os rótulos do teste histórico; e que os campos excluídos e seus derivados proibidos não reaparecem por acesso implícito.

Também são relevantes testes de entradas inválidas, ausência de uma classe, transformação de categorias inéditas, cenários com medidas inteiramente indisponíveis no treino e tratamento documentado dos controles nulos. Assertions que apenas repetem o mesmo valor fixado no código não estabelecem essas propriedades. Depois da execução, métricas devem ser recalculadas das predições salvas e os artefatos devem identificar população, grupos, parâmetros, ambiente e hashes. Este parecer não atesta de antemão que essas verificações passaram.

O alcance máximo da conclusão continua sendo uma avaliação acadêmica interna reproduzível, com exclusões conservadoras e limitações verificáveis. A ausência de protocolo de rotulagem e de timestamps impede a certificação absoluta de não vazamento, mesmo quando a implementação satisfaz todos os contratos técnicos do novo desenho.

## Revisão estática da implementação nova em execução

Foram lidos integralmente `src/kdd_revision/rubric_audit.py` (205 linhas no snapshot examinado), `tools/run_rubric_audit.py` (8 linhas) e `tests/test_rubric_audit.py` (21 linhas). Não foram executados fits, o CLI ou a suíte por esta revisão. Existiam `artifacts/a2_rubric_audit/protocol_before_results.json`, `outer_membership.csv`, resultados dos probes e artefatos parciais dos folds externos de FISIO8. Naquele momento não havia `verification.json` final; portanto, o estado observado é **em execução**, sem certificação de conclusão ou de métricas finais.

A implementação declara exatamente FISIO8 e STRICT4 nas linhas 24–25 e gera 105 candidatos: 48 árvores, 32 logísticas, 24 florestas e um dummy (`search_space`, linhas 40–59). Os cinco folds externos usam seed 743, os três internos usam 811+índice externo e a seleção final em todo o desenvolvimento usa cinco folds com seed 43. Esta última etapa está explicitamente separada da estimativa de desempenho.

O carregamento filtra o CSV bruto pelos IDs de desenvolvimento **antes** de `prepare_final` (`:62–75`). Nenhuma linha do teste histórico é entregue à preparação dessa revisão. O código lê os bytes da fonte completa para validar o SHA-256 e lê a tabela de membros/grupos; isso não equivale a ajustar modelos usando as linhas do teste. A descrição correta é que a revisão não pontua nem usa os rótulos históricos externos para seleção, e não que ela jamais abre o arquivo que também os contém.

Todos os modelos e pools percorrem o mesmo objeto `outer` (`:137` e `:144–146`). Dentro de cada treino externo, `cross_validate` recebe somente o treino externo e escolhe o melhor candidato dentro de cada família (`:148–155`). O reajuste usa o treino externo inteiro e prediz seu conjunto de validação. A tabela `family_nested_metrics.csv` é formada das predições externas de cada família (`:165–177`). Esse desenho corrige a lacuna comparativa principal do relatório c8.

O guard de atributos admite apenas subconjuntos de FISIO8 (`:30–37`); os pools utilizados contêm IDADE, e o guard rejeita imputação etária quando IDADE é retirada. A preparação por linha usa o conjunto completo apenas para suas regras determinísticas. Em STRICT4, as máscaras de Peso/Altura dependem dos próprios pais e da idade, sem conservar PAS, PAD, FC ou os blocos diagnósticos excluídos. Não foi encontrada uma rota desses campos para X dos modelos principais nessa implementação.

Os probes de uma variável são explicitamente diagnósticos (`:93–128`). O alvo produz apenas uma linha descritiva e não é ajustado como preditor. ID ordinal e tokens de datas brutas entram somente nesses probes. Imputação e agrupamento de categorias raras são ajustados no treino de cada fold do probe. Os controles de máscaras de disponibilidade usam uma árvore fixa (`:181–189`), e o controle de alvo permutado usa uma árvore rasa fixa, não uma busca que tenta maximizar a sorte da permutação (`:190–196`). O texto registra corretamente que esse controle não fornece p-valor formal nem prova de ausência de leakage.

Os probes e o controle de coleta usam folds com seed 43; a comparação principal usa seed 743, e o controle permutado usa seed 914 com rótulos permutados. Essa diferença não invalida diagnósticos separados, mas impede tratar uma simples diferença entre suas pontuações como ablação pareada na mesma realização de treino/validação. A permutação por linha também não preserva a estrutura conjunta dos rótulos dentro dos grupos; como não há teste formal de permutação declarado, isso deve permanecer um controle diagnóstico, sem inferência exata sobre a hipótese nula.

### Pendências concretas antes de afirmar reprodução completa

| Pendência | Evidência e impacto | Correção ou aceite necessário |
|---|---|---|
| REP-01 — A entrada de membros/grupos depende de um artefato local ignorado. | `rubric_audit.py:65` abre `artifacts/a2_mining/particoes_modelagem.csv`; `.gitignore:23` exclui `artifacts/`; o CLI no snapshot revisado não gera esse arquivo nem aceita outra entrada. Um clone com código e CSV bruto falha antes do novo estudo se esse requisito não for preparado. Confiança 100%. | Disponibilizar uma referência congelada admissível de IDs/grupos com SHA, ou um bootstrap mínimo documentado que reconstrua exatamente essa membresia sem refazer modelos e métricas do teste histórico. Se a dependência permanecer, comprovar e documentar o passo necessário. |
| REP-02 — O manifesto cobre só parte das dependências executadas e não fixa o hash da entrada de membros/grupos. | `rubric_audit.py:203–204` inclui o módulo novo, `mining.py` e dois arquivos de preprocessing. Também afetam o resultado `prepare.py`, `full_kdd.py`/`folds_for`, `schema.py` e `experiments.py`/métricas; o CSV de membros/grupos é uma entrada substantiva. Confiança 100%. Os membros externos salvos ajudam a reconstruir a execução, mas não substituem a identificação dessa entrada. | Registrar hashes das entradas e dependências efetivas, protocolo e ambiente; confrontar estado inicial/final. Se os arquivos executados e os membros permaneceram iguais, completar o manifesto não exige retreinar os modelos. |
| VAL-01 — Os testes novos ainda não exercitam o laço completo de avaliação nem o carregamento da membresia. | Os três testes em `tests/test_rubric_audit.py` verificam pools/proibições, grade e guard etário. Os testes históricos cobrem o núcleo de transformação/CV, mas não demonstram a integração nova de seleção por família, identidade dos membros externos ou recusa de uma membresia alterada. Confiança 100%. | Acrescentar verificações pequenas e significativas de integração ou conferir os artefatos efetivos: OOF por ID, hashes comuns, grupos disjuntos, seleção baseada somente nos scores internos e rejeição de deriva da referência. Não requer repetir toda a busca apenas para testar esses contratos. |

Não foi identificado nesta revisão estática um bloqueador confirmado de vazamento computacional no comparativo principal. As pendências de entrada e manifesto são problemas concretos de reprodutibilidade e rastreabilidade a resolver antes dessa afirmação final. A execução em curso ainda precisa terminar e ter suas predições e métricas conferidas. Mesmo após essa verificação, permanecem as condições semânticas, temporais e de identidade explicitadas neste parecer.

O encaminhamento aceito para REP-01 é construir um bootstrap a partir da fonte e da receita histórica, sem refazer classificadores ou pontuar o teste, e comparar os IDs/grupos reconstruídos com a referência c8. Para REP-02, o encaminhamento é um manifesto final adicional com todas as entradas e dependências, verificando os módulos canônicos e o sidecar contra os manifestos históricos. Esses encaminhamentos foram comunicados pelo responsável pela implementação; sua conclusão e equivalência ainda não foram verificadas por esta revisão estática. Não se recomenda modificar o código de ajuste enquanto os fits já iniciados estão em execução.
