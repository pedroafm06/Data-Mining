> HISTÓRICO: execução exploratória anterior à revisão atual do pré-processamento da A2. Os números abaixo pertencem à preparação antiga e não são resultados da base atual. Referências a arquivos descrevem o acervo local anterior.

# Resultados dos experimentos KDD

Execução acadêmica local. O alvo é o rótulo registrado, sem validação clínica do processo de diagnóstico. Os três cenários usam os mesmos registros e partições.

População: 11704; desenvolvimento: 9362; teste reservado: 2342. Não há IDs nem grupos candidatos compartilhados entre os dois conjuntos. Grupos são equivalências candidatas, não identidade comprovada de paciente.

A inclui achados/contexto; B somente medidas+SEXO; B_contexto adiciona contexto de temporalidade desconhecida. Limiar0,5 fixo. Seleção por balancedaccuracy CV antes de calcular métricas de teste. A base inteira já foi explorada na A1; este teste não é virgem dessa exploração.

## Conceitos utilizados

O núcleo usa separação treino/teste, validação cruzada, pipeline de transformação, ajuste de hiperparâmetros, árvore de decisão, matriz de confusão, precisão, recall, F1, acurácia balanceada e curvas ROC/Precisão-Recall. A árvore tem exemplos no material; isso não equivale a uma explicação completa de todos os algoritmos. Regressão logística, floresta aleatória, average precision, Brier, importância por permutação e intervalos por reamostragem de grupos são comparações ou extensões complementares. A síntese da A1 também usa Welch e V de Cramér como complementos técnicos. Não se atribui às aulas a explicação desses complementos.

| Cenário | Vencedor CV | Balancedaccuracy teste | Recall | Especificidade | Precisão | AP | ROC-AUC | TN/FP/FN/TP |
|---|---|---:|---:|---:|---:|---:|---:|---|
| A | tree_d3_leaf50 | 0.9292 | 0.8881 | 0.9704 | 0.9566 | 0.9340 | 0.9459 | 1310/40/111/881 |
| B | logistic_C0.1_wbalanced | 0.6261 | 0.6048 | 0.6474 | 0.5576 | 0.5846 | 0.6643 | 874/476/392/600 |
| B_contexto | forest_150_d8_leaf10 | 0.7302 | 0.5968 | 0.8637 | 0.7629 | 0.7602 | 0.8068 | 1166/184/400/592 |

## Controles e interpretação

Dummy fixo: balancedaccuracy=0.5000. Regra fixa de sopro nos registros com esse dado: cobertura=0.9979, balancedaccuracy=0.9198. A regra não substitui diagnóstico e sua interpretação depende de como o rótulo foi construído.

Os dados e candidatos não demonstram causalidade. Grande diferença entre A e B pode refletir a proximidade dos achados de exame com o rótulo; não prova circularidade nem desempenho real de triagem. A inclusão de contexto também depende de sua disponibilidade no momento pretendido.

## Arquivos e incerteza

Os três pipelines finais ajustados ficam em `models/`, com metadados de versões/features/protocolo. Eles esperam os dados tratados com a política explícita de qualidade já aplicada, não o CSV bruto. `candidatos_cv.csv`, `metricas_folds.csv` e `previsoes_oof.csv` registram todos os candidatos. `selecoes_congeladas_antes_teste.json` foi escrito antes das métricas de teste. `intervalos_bootstrap_grupos.json` contém ICs percentis de500 reamostragens de grupos candidatos, condicionados ao modelo ajustado; não incluem toda a incerteza do treino/seleção nem resolvem identidade de paciente desconhecida. Desvio entre folds não é IC. AP é average precision, não área trapezoidal PR.

`subgrupos_teste.csv` mostra suporte, erros e recall por sexo, idade, ausências e sopro. Só grupos com n≥20 aparecem; suporte positivo baixo é explicitamente sinalizado. Intervalos Wilson de recall são descritivos por linha, sem correção de grupo. São pistas para investigação, não evidência causal.

## Sensibilidades no desenvolvimento

São comparações exploratórias do candidato fixo, sem voltar ao teste para escolher regras. Incluem medidas suspeitas preservadas, sem indicadores, sem IMC e sem PPA quando presente; log somente quando candidato logístico escolhido.

| Cenário | Variante | Balancedaccuracy CV | DP folds |
|---|---|---:|---:|
| A | sem_indicadores | 0.9194 | 0.0096 |
| A | sem_IMC | 0.9194 | 0.0096 |
| A | suspeitos_preservados | 0.9194 | 0.0096 |
| A | sem_PPA | 0.9194 | 0.0096 |
| B | sem_indicadores | 0.6064 | 0.0177 |
| B | sem_IMC | 0.6113 | 0.0118 |
| B | suspeitos_preservados | 0.5884 | 0.0158 |
| B | log1p | 0.6148 | 0.0131 |
| B_contexto | sem_indicadores | 0.7075 | 0.0111 |
| B_contexto | sem_IMC | 0.7087 | 0.0122 |
| B_contexto | suspeitos_preservados | 0.7072 | 0.0104 |
| B_contexto | sem_PPA | 0.7078 | 0.0110 |

## Tempo sob hipótese histórica

A coluna de data é hipótese de século/janela2003–2010, não data estabelecida. Corte2009-01-01 fixado previamente; sem novo tuning. Os hiperparâmetros foram escolhidos no CV do desenvolvimento global, que inclui datas posteriores ao corte; portanto a seleção não é puramente prospectiva. Essa avaliação é secundária, não independente das escolhas anteriores nem validação cronológica confirmada.

- A: treino=8488, teste=2969, sem data hipotética=247, grupos cruzados=0; balancedaccuracy=0.9265.
- B: treino=8488, teste=2969, sem data hipotética=247, grupos cruzados=0; balancedaccuracy=0.5886.
- B_contexto: treino=8488, teste=2969, sem data hipotética=247, grupos cruzados=0; balancedaccuracy=0.7144.

## Limites e próximos passos

Não há percentis clínicos não verificados, reclassificação de HAS, SMOTE ou interpretação de importância como causa. Permutação usa modelo ajustado em quatro folds e avaliação no quinto do desenvolvimento, com seleção anterior por CV; é exploração pós-seleção. Importâncias por impureza/coeficientes do modelo completo são descritivos.

Continuam necessárias confirmação da semântica do alvo/ID, momento de registro de contexto e rubrica atualizada da A2. A ausência de resposta não impede reprodução acadêmica; impede alegações de eficácia clínica e de identidade amostral confirmada.

Tempo registrado: 22.05s. Protocolo SHA256: `46ae64fe66ccb4480180bfc1c852e6038b68a8bf5f1ac366aa6f44a46791681b`.