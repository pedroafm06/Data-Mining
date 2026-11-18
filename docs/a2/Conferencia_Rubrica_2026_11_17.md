# Conferência da rubrica da A2 em 17 de novembro de 2026

Os requisitos de conteúdo e formato da A2 foram confrontados novamente com o DOCX original e o artigo. Os itens objetivos de formato estão atendidos: classe IEEE de conferências, duas colunas, quatro páginas, resumo na faixa exigida e seções solicitadas. A revisão adicional explicitou no artigo as justificativas de imputação, codificação, escala, logaritmo e escolha das famílias de modelos. A apresentação ampliada tem 22 slides, todos apresentados, com conteúdo e notas conferidos; a duração estimada é 14 min 46 s e o tempo efetivo depende de ensaio. A revisão ampliada foi publicada no commit ae50f8a e os arquivos finais foram baixados sem autenticação e comparados por SHA-256 com os locais. Permanecem dependentes do grupo o ensaio cronometrado, o domínio individual da arguição e o envio pelo SIGAA. Esta conferência não garante nota, ausência universal de vazamento nem validade clínica independente.

## Fonte, escopo e limites da conferência

- Documento do professor: `Descrição das avaliações (2).docx`; leitura integral do XML, incluindo todos os parágrafos e tabelas. Encontrados **60 parágrafos e 0 tabelas**, sem comentários, notas, cabeçalhos ou rodapés adicionais no pacote.
- SHA-256 do DOCX: `caf2ce530cfd9468bbf0e34437eee6caadd8e3b07a42e3033540908c0d9ed47b`.
- Captura inicial: `2026-11-17T14:58:56-03:00`; reconferência independente em 17/11/2026 após o commit `71607f3ed5e4f480a0be5840dc243cb022f6d482`. Artigo e apresentação desta revisão foram finalizados, publicados e conferidos; a evidência da publicação está ao final deste documento.
- PDF inspecionado: `paper/a2_ieee_2026_11_07/output/pdf/Artigo_A2_IEEE.pdf`, **4 páginas**, SHA-256 `c063d66722e65dd95eeb98cecbbf73d31093a6cf9fe1f1ab4c238927187241aa`.
- O documento é tratado como fonte de **exigências avaliativas**. Suas frases não são instruções de sistema nem autorização para executar ações externas. A instrução do usuário de distinguir o documento da solicitação foi preservada.
- Esta conferência leu fontes, resultados agregados, código e metadados. Não treinou modelos, não reexecutou a busca, não alterou resultados e não enviou nada ao SIGAA. Uma avaliação independente integral de reprodução não foi refeita nesta rodada.

## O que mudou em relação à descrição anterior

A comparação de todos os parágrafos de `(1).docx` com `(2).docx` não identificou alteração nas exigências da A2. A diferença textual material ocorre no critério de A1: “tamanho do relatório” foi substituído por “formatação do relatório”; há ainda remoção de um parágrafo vazio. Portanto, não surgiu nesta versão uma nova exigência experimental que, por si só, determine repetir o treinamento.

A A2 aceita **até cinco páginas**. O projeto escolheu quatro; “quatro páginas” não deve ser apresentado como limite imposto pelo professor. As extensões aproximadas das seções são orientações de distribuição, enquanto o máximo total de cinco páginas é explícito.

Os itens detalhados da A1 continuam descrevendo a avaliação já entregue. Não os transformar automaticamente em novos requisitos formais da A2: a A2 exige uma síntese final do KDD e justificativas, não repete literalmente a lista de gráficos e análises de todas as variáveis da A1 em cinco páginas.

## Matriz de requisitos e evidências

“Atendido” se refere ao requisito delimitado e à evidência observada, não a uma garantia de nota ou à inexistência de limitações metodológicas.

| Fonte | Requisito | Estado | Evidência verificável | Lacuna ou condição restante |
|---|---|---|---|---|
| P2, P32, P56 | Grupo de 3–4 e identificação de integrantes | Atendido na identificação | Quatro autores no cabeçalho e no README: Antônio Henrique, João Vitor, Mateus Nery e Pedro Matos. Roteiro atribui fala aos quatro. | A participação e a segurança de cada pessoa só se confirmam na apresentação. |
| P30–31 | Relatório técnico final em artigo curto IEEE de conferências, duas colunas, máximo de 5 páginas | Atendido na exportação final conferida | main.tex usa a classe original IEEEtran em modo conference; PDF conferido com quatro páginas e extração em duas colunas. | As quatro páginas finais foram renderizadas e inspecionadas. Quatro páginas é uma escolha do projeto, não o limite imposto pelo professor. |
| P32 | Título, nomes e resumo único de 100–150 palavras com problema, base, algoritmos e principal resultado | Atendido | Cabeçalho com quatro autores; resumo menciona UCMF, classificação, famílias e BA principal de 63,27%. A contagem no PDF por espaços produz 129 palavras; a contagem alfabética do TeX sem comandos produz 121. | Ambos os métodos ficam na faixa 100–150. O manifesto explicita seu método; o resumo visível foi conferido na exportação final. |
| P33; P50 | Introdução: contexto, classificação, objetivo claro e relevância | Atendido no conteúdo | Seção I define Anormal como positivo, discriminação do rótulo cardíaco pediátrico e relevância da seleção/proveniência para interpretar desempenho. | Não confundir concordância com o rótulo com diagnóstico independente ou predição de evento futuro. |
| P34; P50 | Origem, instâncias, atributos, alvo, desbalanceamento e descobertas da EDA | Atendido | Seção II informa hospital de origem, 12.873 registros/21 atributos, 11.704 rotulados, partições, 9.361 de desenvolvimento e 42,38% Anormal; apresenta ausências, idade, FC e associação do sopro. | As contagens são registros, não pacientes distintos comprovados. |
| P34 | Um ou dois gráficos relevantes de EDA | Atendido no PDF final renderizado | Dois gráficos: proporções por status de sopro e indisponibilidade por atributo; texto interpreta as diferenças e os denominadores. | Posicionamento e legibilidade conferidos na exportação final. A rubrica aceita um ou dois, não exige um gráfico para cada variável. |
| P34; P51 | Excluir o atributo identificado com data leakage na A1 | Atendido quanto à exclusão documentada; ausência absoluta de vazamento não demonstrável | A1 entregue registra que MOTIVO1 e MOTIVO2 já indicam o laudo e oferecem risco de vazamento. Os dois são proibidos em todos os três conjuntos de candidatos finais; teste de validate_features cobre essa proibição. | SOPRO/B2 e outros campos permanecem incertos: ficam fora de FISIO8/STRICT4 e só entram em comparação explicitamente exploratória. O critério de construção do rótulo não permite garantir ausência de incorporação em FISIO8. |
| P35; P51 | Pré-processamento com justificativas de limpeza, erros, codificação e normalização | Atendido por síntese explícita no artigo e detalhamento rastreável no repositório | Seção III explica preservação das linhas, coerência de idade/IMC, mediana para reduzir influência de extremos, faixas para diferenças de crescimento, mínimo de 30 observações, one-hot sem ordem artificial, padronização para regularização da logística, log para comprimir a cauda de Peso e unidades originais nas árvores. As razões foram conferidas contra transformer.py e as decisões do projeto. | Os envelopes são hipóteses de curadoria, não limites clínicos. A síntese dentro do limite de cinco páginas não enumera toda célula; as microdecisões estão nos documentos e código ligados pelo repositório. |
| P35; P51 | Protocolo de validação correto e proteção contra contaminação entre treino e avaliação | Atendido no protocolo implementado, com limitações explicitadas | Cinco folds externos/três internos, mesmos cortes entre cenários/famílias, seleção interna por BA, ajuste de medianas/vocabulário/escala no treino, agrupamento de cópias e exclusão do teste histórico já exposto. | Grupos candidatos não garantem separar todas as visitas do mesmo paciente. Exploração anterior da coorte permanece. Não converter o protocolo em prova universal de ausência de vazamento. |
| P35; P52 | Pelo menos dois algoritmos: baseline simples e mais complexo, ajustes básicos | Atendido | Referência majoritária, árvore, logística regularizada e floresta. Grade de 105 por cenário: 1+48+32+24, com escolha por família. Código e protocolo mostram profundidade, folha, C, pesos, representação e imputação. | 150 árvores e corte 0,5 foram fixados; não foram ótimos demonstrados por uma busca sobre todos os valores possíveis. |
| P35–36; P52 | Métricas adequadas e tabela comparativa clara | Atendido no conteúdo | Tabela II traz BA, sensibilidade, especificidade, precisão, F 1 e AP para as quatro famílias nos três cenários. BA é justificada pelo desequilíbrio entre classes e pela referência sempre Normal. | Legibilidade das tabelas conferida nas páginas renderizadas. A ordenação numérica não estabelece superioridade universal. |
| P36; P40; P53 | Análise crítica e interpretação dos erros | Atendido | Tabela III mostra matrizes externas; texto discute 1.659 falsos negativos, 1.707 falsos positivos, sensibilidade e idade dos erros; intervalos pareados dão contexto à diferença de 1,24 p.p. | Intervalos são condicionados às previsões existentes e não incluem um novo treino ou nova coorte; diferença de idade entre grupos não é taxa de erro por idade. |
| P36; P53 | Importância dos atributos e interpretação | Atendido | Seção IV mede permutação: FC/Peso em FISIO8 e SOPRO/B2 em CLINICO, com explicação de dependência e limites de correlação/combinações artificiais. | Importância não demonstra causalidade, cronologia ou ausência de vazamento. |
| P37; P53 | Conclusões relacionadas ao objetivo, limitações e trabalhos futuros | Atendido | Seção V retorna à discriminação do rótulo, desempenho modesto sem achados e dependência da informação; propõe documentação da rotulagem/coleta e coorte independente. | Não afirmar utilidade clínica validada nem que todas as incertezas foram resolvidas. |
| P37; P54 | Referências de dados, algoritmos e bibliotecas | Atendido na presença e correspondência temática | references.bib contém materiais UCMF/SIGAA, scikit-learn, Random Forests, validação aninhada e bootstrap; citações aparecem nas seções correspondentes. | Esta auditoria conferiu presença e correspondência, não revalidou bibliograficamente cada obra externa ou disponibilidade dos materiais restritos do SIGAA. |
| P39; P54 | Link funcional de repositório público no rodapé da primeira página | Atendido no PDF e na consulta pública | Nota do título inclui https://github.com/pedroafm06/Data-Mining; anotação de URL está na página 1 e o README respondeu HTTP 200 sem autenticação na reconferência. | O commit ae50f8a contém a revisão atual. Downloads públicos do artigo, PPTX, PDF dos slides, roteiro, guia e README conferem por SHA-256 com os locais. |
| P39; P49; P54 | Código organizado, random_state fixado e resultados reproduzíveis | Atendido documentalmente; reprodução independente desta rodada não executada | README fornece comandos, hash do CSV e dependências fixadas; run_rubric_audit.py reconstrói/verifica a partição; protocolo fixa 42/743/811+k/43; resultados incluem hashes e verificação de 12 procedimentos/60 seleções externas. | Não reexecutamos modelos nesta auditoria. Um clone novo exige a cópia autorizada do CSV da disciplina, que não é distribuída pelo repositório; isso é documentado. Não declarar reprodução independente integral como realizada aqui. |
| P41 | Sem trechos de código e sem resultados apenas em screenshots | Atendido na fonte e na inspeção textual | Artigo apresenta prosa, tabelas LaTeX e figuras geradas dos resultados, sem blocos de código ou screenshots de ambiente. | Capturas e recortes de tela não substituem a última inspeção visual, especialmente em figuras. |
| P43; P55 | Apresentação de até 15 minutos, ênfase em metodologia/resultados, slides padronizados/numerados/legíveis | Exportado e conferido; ensaio pendente | 22 slides numerados, todos apresentados, com exemplos, metodologia e resultados no template INF. PPTX/PDF, 22 notas e cobertura da fala conferidos. | Roteiro com 1.889 palavras: 14 min 01 s de fala a 135 palavras/min, mais 45 s de transições = 14 min 46 s. Só ensaio comprova o limite; a 130 palavras/min a estimativa ultrapassa 15 min. |
| P42; P56 | Ordem dos grupos, todos apresentam, qualquer membro responde a qualquer pergunta | Participação prevista; execução não comprovada | Grupo 3 identificado; falas contíguas atribuídas aos quatro; roteiro contém notas técnicas e perguntas/respostas de defesa. | Ordem de apresentação depende do professor; domínio individual e segurança nas respostas não são comprovados pelos arquivos. |
| P45–46; P58–59 | Submeter em 18/11 pelo SIGAA; apresentações de 18/11 a 27/11; sem e-mail nem atraso | Requisito identificado; submissão e apresentação não realizadas nesta auditoria | Prazo e canal constam do DOCX e do README. | Gerar os arquivos ou publicar GitHub não equivale a submeter no SIGAA. Falta comprovação de envio e recibo, bem como da apresentação oral. |
| P60 | Declarar IA generativa: qual, onde, como e para quê | Atendido na declaração escrita | Seção própria informa Claude/Claude Code (Anthropic) e Codex (OpenAI), etapas A1/A2, diálogo, scripts/revisões/experimentação/composição e conferência técnica das saídas. | A declaração descreve o uso registrado. Conferir que ela permanece no PDF final e não acrescentar participação humana ou validação clínica não demonstradas. |
| P49, P55–56 | Pesos de avaliação 60% escrita, 35% apresentação, 5% segurança | Registrado; não é resultado alcançado | O documento atribui esses pesos à A2. | Não converter atendimento de itens em garantia de nota, aceitação ou pontuação integral. |

## Pontos que exigem cuidado na declaração de conformidade

1. **Vazamento:** a exclusão exigida é rastreável: a A1 entregue chama MOTIVO1/MOTIVO2 de risco de vazamento e ambos saem de todos os candidatos finais. Isso não prova que FISIO8 esteja livre de qualquer incorporação no rótulo. CLINICO permanece uma sonda exploratória e não substitui o resultado principal. O controle de rótulos permutados próximo de 50% tampouco prova ausência universal de vazamento.
2. **Reprodutibilidade:** código público, hashes, sementes e comandos existem. Não foi feita nesta auditoria uma nova reprodução em clone limpo; o CSV depende do acesso autorizado pela disciplina. Não afirmar que disponibilizar o link equivale a validar a execução em qualquer ambiente.
3. **Tempo e apresentação:** a versão ampliada tem 22 slides, todos apresentados. O roteiro de 1.889 palavras estima 14 min 46 s a 135 palavras/min, com 45 s para transições. Não é tempo aferido; a 130 palavras/min seriam aproximadamente 15 min 17 s. As notas de arguição continuam sendo material de estudo e não slides para pular.
4. **Publicação e submissão:** a revisão atual foi baixada anonimamente do commit ae50f8a e os seis arquivos conferiram por SHA-256 com os locais. GitHub não substitui o envio exclusivo do relatório pelo SIGAA em 18/11.
5. **Qualidade visual e manifestações de validade:** o relatório recompilado tem quatro páginas, classe IEEE original, 15 fontes incorporadas e zero Type 3; as quatro páginas foram inspecionadas após o reforço das justificativas. As limitações reconhecidas de coorte, identidade e rotulagem impedem uma declaração de validade clínica ou de “100% sem problemas”. A rubrica não exige PDF eXpress; não houve submissão a esse serviço.

## Conferências pontuais da versão em fechamento

- Os resultados agregados de `paper/a2_ieee_2026_11_07/results/reviewed_results.json` são semanticamente idênticos aos de `resultados/a2/revisao_final_2026_11_16/reviewed_results.json` nesta leitura.
- O artigo informa a distinção entre seleção por família nos folds e ajuste final em todo o desenvolvimento. Os números de avaliação vêm das previsões externas, não dos escores de treino do ajuste final.
- A grade tem 105 alternativas por cenário: 48 árvores, 32 logísticas, 24 florestas e uma referência. O modelo principal final usa 150 árvores, folha mínima 30, pesos balanceados, mediana global e unidades originais. Esses parâmetros finais não devem ser apresentados como se fossem os de todas as rodadas externas.
- A anotação de URL do PDF aparece na página 1 para o repositório correto. A consulta pública sem autenticação encontrou a indicação Public e arquivos de código/instruções: [repositório consultado](https://github.com/pedroafm06/Data-Mining).
- A ordem do usuário, “todos os slides apresentados, sem apoios ou pulos”, é mais específica que a rubrica. Ela foi preservada: 22 páginas no PDF, 22 slides e notas no PPTX e 22 páginas e notas no Canva. O conteúdo visível foi conferido contra a fala.
- Na reconferência antes de concluir esta auditoria, o SHA-256 do PDF corresponde a `Verificacao_Artigo.json.pdf_sha256`. A divergência transitória observada durante a edição concorrente foi resolvida; os resultados agregados do artigo continuam idênticos aos resultados finais.
- O manifesto conta palavras alfabéticas do TeX sem comandos e registra 121; a extração do resumo do PDF conta 129 unidades por espaços. A diferença é de método, não de mudança no resumo; ambas atendem ao intervalo 100–150.
- O reforço editorial desta rodada foi conferido contra o código: razões da mediana e das faixas, codificação nominal, escala/log e famílias. Não alterou regras, parâmetros, dados, resultados nem o template.
- As extensões aproximadas de cada seção não são quotas rígidas. O DOCX não exige fluxograma; o limite objetivo é de até cinco páginas.

## Verificações finais necessárias antes de entregar

- Concluído: artigo recompilado, quatro páginas renderizadas e inspecionadas; manifesto e cópia de entrega correspondentes ao PDF final.
- Concluído: apresentação ampliada para 22 slides, todas as páginas inspecionadas, falas e notas conferidas; Canva preserva a versão com 22 páginas. Roteiro inclui 31 perguntas de arguição.
- Concluído: pasta A2_Entrega atualizada, checksums verificados, publicação no commit ae50f8a e seis downloads públicos conferidos. A1 entregue preservada sem alterações.
- Ensaiar com os quatro integrantes e relógio. Cada um precisa estudar o conjunto, não somente sua parte, porque qualquer membro pode responder a qualquer pergunta.
- Submeter o relatório exclusivamente no SIGAA no prazo e preservar o comprovante. Esta auditoria não afirma que o envio já ocorreu.

## Extração integral do documento do professor

A numeração P1–P60 abaixo foi criada nesta extração para permitir rastreabilidade; ela não é uma numeração impressa pelo professor. O texto é reproduzido como conteúdo do documento, incluindo exigências da A1, para preservar o contexto. A rubrica contém zero tabelas.

**P1.** AVALIAÇÃO

**P2.** A avaliação será baseada no estudo de caso, desenvolvido nas aulas práticas de laboratório, em grupos de 3 a 4 alunos.

**P3.** A avaliação está dividida em duas partes (A1 e A2). Cada parte será composta por um relatório e uma apresentação oral com arguição.

**P4.** A nota final (NF) será calculada como a média aritmética simples de A1 e A2: NF = (A1 + A2) / 2.

**P5.** *(parágrafo vazio)*

**P6.** A1: Parte 1 – Pré-processamento de dados (limpeza e transformação)

**P7.** Relatório sobre o pré-processamento de dados (limpeza e transformação).

**P8.** Máximo de 5 folhas (fonte Times New Roman, tamanho 12, ou Arial, tamanho 10).

**P9.** O relatório deve conter:

**P10.** Análise estatística univariada (descritiva ou por meio de gráficos) de todas as variáveis.

**P11.** Identificação de possíveis problemas de qualidade em cada variável.

**P12.** Soluções de limpeza para cada um dos problemas de qualidade.

**P13.** Comparação de duas variáveis após a limpeza.

**P14.** Interpretação gráfica das duas variáveis após a limpeza do item anterior.

**P15.** Análise bivariada entre as variáveis dependentes e a variável dependente (variável-alvo), com interpretação.

**P16.** Transformações a serem realizadas no conjunto de dados, com a respectiva justificativa.

**P17.** Não deve haver trechos de código nem simples capturas de tela (screenshots) dos ambientes de desenvolvimento.

**P18.** Apresentação do relatório por ordem numérica dos grupos.

**P19.** Apresentação de 15 min. dos principais pontos (mais relevantes) do relatório.

**P20.** Datas importantes

**P21.** 29/09 - Submissão do relatório no SIGAA

**P22.** 30/09 a 07/10 - Apresentação dos relatórios

**P23.** *(parágrafo vazio)*

**P24.** Critérios de avaliação

**P25.** Qualidade do relatório (50%): formatação do relatório, correção e completude do conteúdo (item 1 acima).

**P26.** Qualidade da apresentação (30%): tempo da apresentação; slides padronizados, numerados, com pouco texto e elementos legíveis (texto, figuras ou tabelas).

**P27.** Segurança na apresentação e nas respostas às perguntas (20%): todos devem apresentar, e qualquer membro do grupo pode ser escolhido para responder a qualquer pergunta.

**P28.** *(parágrafo vazio)*

**P29.** *(parágrafo vazio)*

**P30.** A2: Parte 2 – Resultado final do trabalho no estudo de caso

**P31.** Relatório técnico com o resultado final do trabalho no estudo de caso. O relatório deve seguir o formato de artigo curto seguindo rigorosamente o template de conferências da IEEE (https://www.ieee.org/conferences/publishing/templates) (com 2 colunas e máximo de 5 páginas) e conter as seguintes seções:

**P32.** Cabeçalho e Resumo (~0,5 pág.): Título do trabalho, nomes dos integrantes e um resumo único (100–150 palavras) contendo: problema abordado, dataset utilizado, algoritmos comparados e principal resultado obtido.

**P33.** Introdução (~0,5 pág.): Contextualização do problema, objetivo claro da tarefa de mineração (classificação, regressão, agrupamento ou associação) e relevância da análise.

**P34.** Dados e Análise Exploratória (~1 pág.): Origem do dataset, número de instâncias e de atributos, descrição da variável-alvo e principais descobertas estatísticas (incluindo data leakage e 1 ou 2 gráficos relevantes). O atributo que indique data leakage (conforme visto em A1) deve ser excluído da análise.

**P35.** Metodologia (~1 pág.): Etapas de pré-processamento (limpeza, tratamento de erros e transformações), estratégia de validação e métricas utilizadas, e algoritmos selecionados (pelo menos 2, um baseline simples e outro mais complexo).

**P36.** Resultados e Discussão (~1,5 pág.): Tabela comparativa com as métricas adequadas ao problema, análise crítica do desempenho dos modelos, interpretação dos erros (ex.: matriz de confusão ou resíduos) e importância dos atributos.

**P37.** Conclusão e Referências (~0,5 pág.): Síntese dos resultados em relação ao objetivo, limitações encontradas, sugestões de trabalhos futuros e referências bibliográficas (fontes de dados, algoritmos e bibliotecas).

**P38.** Requisitos Obrigatórios

**P39.** Reprodutibilidade: incluir, no rodapé da primeira página, o link para o repositório público (GitHub ou Google Colab) com o código organizado e o random_state fixado.

**P40.** Foco Analítico: não apenas descreva os números; explique o que os resultados significam no contexto do problema.

**P41.** O relatório não deve conter trechos de código nem apresentar resultados apenas como capturas de tela (screenshots) do ambiente de desenvolvimento.

**P42.** Apresentação do relatório por ordem numérica dos grupos.

**P43.** Apresentação de 15 min. dos principais pontos (mais relevantes) do relatório, com ênfase na metodologia e nos resultados alcançados.

**P44.** Datas importantes

**P45.** 18/11 - Submissão do relatório no SIGAA

**P46.** 18/11 a 27/11 - Apresentação dos relatórios

**P47.** *(parágrafo vazio)*

**P48.** Critérios de avaliação

**P49.** Qualidade da escrita do relatório (60%): organização do texto, correção gramatical, objetividade da linguagem científica, qualidade e correção da implementação experimental, validade da avaliação e reprodutibilidade dos resultados.

**P50.** Formulação do Problema e Dados: define claramente a tarefa de mineração e a relevância do problema. Caracteriza o dataset com precisão (instâncias, atributos, desbalanceamento) e apresenta visualizações pertinentes na EDA.

**P51.** Pré-processamento e Rigor Metodológico: justifica todas as etapas de limpeza, codificação e normalização. Aplica corretamente o protocolo de validação e não apresenta vazamento de dados.

**P52.** Experimentação e Métricas: compara múltiplos algoritmos (pelo menos 2: um baseline simples e outro mais complexo) pertinentes à tarefa, utilizando métricas adequadas ao contexto. Apresenta tabelas claras e realiza ajustes básicos nos hiperparâmetros.

**P53.** Análise Crítica e Discussão: vai além dos números – interpreta os resultados no contexto do domínio, analisa os erros (matriz de confusão), identifica as variáveis mais relevantes e aponta as limitações reais do estudo.

**P54.** Estrutura, Clareza e Reprodutibilidade: respeita o limite de ~5 páginas, apresenta redação técnica clara, figuras legíveis e referências corretas, e disponibiliza um link funcional para o código reprodutível (GitHub/Colab).

**P55.** Qualidade da apresentação (35%): atende ao tempo máximo da apresentação; os slides estão padronizados, numerados, com pouco texto e elementos legíveis (texto, figuras ou tabelas).

**P56.** Segurança na apresentação e nas respostas às perguntas (5%): todos devem apresentar, e qualquer membro do grupo pode ser escolhido para responder a qualquer pergunta.

**P57.** OBSERVAÇÕES GERAIS

**P58.** Sob nenhuma circunstância serão aceitas entregas de atividades avaliativas fora do prazo estipulado ou por e-mail do professor.

**P59.** As entregas devem ocorrer exclusivamente por meio do SIGAA, nas datas estipuladas.

**P60.** O uso de Inteligência Artificial Generativa deve ser informado (qual, onde, como e para quê).


## Atualização técnica de fechamento

A revisão adicional explicitou as justificativas que estavam pouco desenvolvidas na seção de metodologia. O PDF recompilado mantém quatro páginas, 15 fontes incorporadas, zero Type 3, metadados com acentos e o template IEEE de conferências. As quatro páginas foram renderizadas e inspecionadas. O novo hash está registrado no início deste documento e coincide com `Verificacao_Artigo.json`. Resultados, protocolo e modelos não foram alterados. A apresentação tem 22 slides, todos incluídos na fala; o novo roteiro estima 14 min 46 s, ainda dependente de ensaio.

O [parecer de fechamento IEEE](Fechamento_IEEE_2026_11_17.md) registra as correções editoriais anteriores. O parecer agora também registra o novo hash e o reforço das justificativas. A conferência e a publicação dos novos artefatos foram concluídas. Permanecem pendentes o ensaio real e o envio ao SIGAA.

## Publicação anterior conferida

O [commit 65c1ce9](https://github.com/pedroafm06/Data-Mining/commit/65c1ce9438f0269f9036f1f61be294705321b2ab) contém a versão anterior dos artefatos, que foi baixada sem autenticação e comparada por SHA-256 com os arquivos locais daquela rodada: README, artigo, PPTX, PDF dos slides, guia de defesa e roteiro. Todos coincidiram. O hash do artigo daquela versão era `323827c785827ebf72b89c9894a7875eeb92f937069332e9a898916d56bd86fc`. Essa evidência é histórica; a publicação e a conferência da revisão ampliada constam abaixo.

## Publicação da revisão ampliada

O [commit ae50f8a](https://github.com/pedroafm06/Data-Mining/commit/ae50f8ae28401197c802d082c520757c726be44b) publicou o artigo com justificativas reforçadas, a apresentação de 22 slides, o roteiro e as fontes. Downloads sem autenticação de README, artigo, PPTX, PDF dos slides, roteiro e guia de defesa tiveram SHA-256 idênticos aos arquivos locais. As cópias em A2_Entrega também foram verificadas.

O [Canva atual](https://www.canva.com/d/U42sgvNqoAIU4z6) tem 22 páginas e 22 notas; numeração, texto e conversão das tabelas foram conferidos. A versão anterior de 16 slides foi guardada junto às versões anteriores. O roteiro tem 1.889 palavras de fala e 31 perguntas de arguição; as perguntas e notas técnicas são material de estudo, não slides extras.
