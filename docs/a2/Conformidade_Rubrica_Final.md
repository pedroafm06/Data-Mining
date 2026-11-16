# Conformidade da entrega final da A2 com a rubrica

Conferência da versão final (artigo, slides e código) com os requisitos da descrição da A2 recebida pelo SIGAA em 07/11/2026, na transcrição registrada em [`auditoria_2026_11_07/conformidade_rubrica.json`](auditoria_2026_11_07/conformidade_rubrica.json). Pesos: relatório 60%, apresentação 35%, segurança na arguição 5%. Os números citados no artigo e nos slides vêm de [`reviewed_results.json`](../../resultados/a2/auditoria_2026_11_07/reviewed_results.json); nenhum é digitado à mão.

| ID | Requisito | Onde está | Estado |
|---|---|---|---|
| A2-01 | Artigo IEEE de conferência, duas colunas, até 5 páginas | [`Artigo_A2_IEEE.pdf`](../../paper/a2_ieee_2026_11_07/output/pdf/Artigo_A2_IEEE.pdf), classe IEEEtran oficial; `tools/build.py --final` bloqueia mais de 5 páginas | Atendido |
| A2-02 | Título, integrantes, resumo de 100 a 150 palavras com problema, dados, algoritmos e resultado | Página 1; contagem conferida por `build.py` | Atendido |
| A2-03 | Introdução com contexto, objetivo e relevância | Seção I: prevalência de cardiopatia congênita, falta de especialistas, objetivo de triagem e critério de vazamento | Atendido |
| A2-04 | Dados e EDA: origem, instâncias, atributos, alvo, desbalanceamento, leakage, 1 ou 2 gráficos | Seção II, Fig. 1 (alvo, achados, idade, FC) e Tabela I | Atendido |
| A2-05 | Excluir atributos com data leakage | Tabela I; `CLINICO` e `EXCLUDED_REASONS` em `rubric_audit.py`; FISIO8 e STRICT4 como sensibilidade para a interpretação conservadora | Atendido |
| A2-06 | Justificar limpeza, erros, codificação, imputação e normalização | Seção III-A/B, com os limites de plausibilidade explícitos | Atendido |
| A2-07 | Validação sem contaminação | Validação aninhada agrupada; transformações ajustadas em cada treino; teste histórico só depois da seleção | Atendido |
| A2-08 | Pelo menos dois algoritmos, baseline e modelo complexo, com ajuste de hiperparâmetros | Maioria, árvore CART, logística e floresta; 105 configurações por cenário | Atendido |
| A2-09 | Tabela de métricas, análise crítica, matriz de confusão e importância | Tabelas II a IV, Fig. 2, IC 95% por bootstrap pareado, regras extraídas e análise de erros | Atendido |
| A2-10 | Conclusão, limitações, trabalhos futuros, referências de dados, algoritmos e bibliotecas | Seção V e referências (CART, logística, floresta, bootstrap, validação aninhada, pandas, NumPy, scikit-learn, matplotlib) | Atendido |
| A2-11 | Link público no rodapé da página 1, código organizado, `random_state` fixo | Rodapé verificado por `build.py --final`; sementes no README e na Seção III | Atendido, desde que o `main` público contenha esta versão |
| A2-12 | Sem código e sem capturas de tela | Figuras vetoriais e tabelas LaTeX | Atendido |
| A2-13 | Apresentação de 15 min, slides padronizados, numerados, pouco texto | 15 slides "NN / 15"; roteiro com tempos por integrante | Atendido; tempo depende do ensaio |
| A2-14 | Todos apresentam e respondem | Roteiro divide as falas e lista perguntas prováveis | Depende do grupo |
| A2-15 | Submissão até 18/11/2026 pelo SIGAA | — | Pendente (ação do grupo) |
| A2-16 | Declarar IA generativa: qual, onde, como e para quê | Seção final do artigo e slide de apoio | Atendido |

## Antes de submeter

1. Integrar esta versão ao `main` público, para que o link do rodapé mostre o código do artigo.
2. Conferir que o PDF submetido é o de `paper/a2_ieee_2026_11_07/output/pdf/` gerado com `--final`.
3. Ensaiar a apresentação cronometrada (meta de 14 min 30 s) e as perguntas do roteiro com os quatro integrantes.
