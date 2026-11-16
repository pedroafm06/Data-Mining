# Revisão final do relatório da A2 · 16/11/2026

A revisão compara as duas propostas com a rubrica do SIGAA, o relatório entregue na A1, o dicionário UCMF e os resultados obtidos por nova execução. A branch de João (Petas) inclui os sete commits da branch de Antônio e acrescenta um commit próprio. Os artefatos das duas propostas continuam acessíveis pelos commits de origem.

| Origem | Contribuição | Decisão para o relatório |
|---|---|---|
| Antônio, [522eed7](https://github.com/pedroafm06/Data-Mining/commit/522eed7) | Reconstrução da partição com quebras de linha portáveis e compilação IEEE no Windows | Incorporada, com verificação do arquivo oficial do Windows e manifesto de compilação ampliado. A compilação final ocorreu no macOS. |
| Antônio, [55f6f4d](https://github.com/pedroafm06/Data-Mining/commit/55f6f4d) e [f4a6637](https://github.com/pedroafm06/Data-Mining/commit/f4a6637) | Cenário com 13 atributos e pontuação do teste histórico | O cenário CLINICO entrou como comparação exploratória e recebeu os mesmos folds corrigidos. O teste histórico já foi examinado, compartilha padrões brutos com o desenvolvimento e ficou fora do resultado final. |
| Antônio, [8055f1e](https://github.com/pedroafm06/Data-Mining/commit/8055f1e) | Perfil de erros por sopro e idade | Recalculado nas previsões externas. A presença, a ausência explícita e a falta de preenchimento de SOPRO têm significados distintos. |
| Antônio, [81c867a](https://github.com/pedroafm06/Data-Mining/commit/81c867a) e [6a5d947](https://github.com/pedroafm06/Data-Mining/commit/6a5d947) | Redação, tabelas geradas da execução, leitura dos resultados e organização do README | Incorporadas a separação dos cenários, a geração de tabelas e a ligação entre artigo, dados, código e relatório. O resultado principal permanece FISIO8 porque a fonte não estabelece a cronologia nem a participação dos achados na rotulagem. |
| Antônio, [ee1115d](https://github.com/pedroafm06/Data-Mining/commit/ee1115d) | Slides e roteiro com 15 slides principais | Material para a etapa de apresentação. O conteúdo precisa acompanhar o protocolo e os números do artigo final. |
| João, [c4efa0b](https://github.com/pedroafm06/Data-Mining/commit/c4efa0b) | Bootstrap pareado, regras da árvore, reconciliação A1–A2, revisão de rubrica e dos slides | Incorporados ao relatório com os números da execução final. Os intervalos condicionam aos ajustes existentes. As regras são descritivas do treino. As mudanças dos slides ficam para a revisão da apresentação. |

## Agrupamento, seleção e escopo dos resultados

A origem da dúvida sobre duplicação foi a reconciliação da A1. A A1 retirou 987 cópias exatas sem considerar o ID, 752 sem rótulo e 235 rotuladas. A A2 preservou as linhas rotuladas. A regra anterior agrupava equivalências preparadas com pelo menos oito preditores preenchidos, além de reaproveitar componentes históricos. Isso permitia que cópias esparsas permanecessem separadas.

Na comparação bruta sem ID e sem alvo, seis assinaturas que somam 118 linhas atravessavam folds externos anteriores. A revisão une todas as linhas com os mesmos valores brutos aos componentes já existentes. A amostra continua com 9.361 linhas, agora em 9.166 componentes (antes, 9.279). Cada assinatura fica em um único fold externo. Três conjuntos com 110 registros têm entradas brutas idênticas e rótulos discordantes. A regra agrupa também esses registros, pois não consulta o resultado para decidir a equivalência. Sete assinaturas brutas somam 146 linhas distribuídas entre o desenvolvimento e o teste histórico. Essa sobreposição é uma razão adicional para excluir o teste histórico da estimativa final. Os grupos continuam sendo aproximações de dependência, sem identificação longitudinal confirmada.

A referência majoritária, árvore, logística e floresta compartilham as partições. Cada procedimento escolhe a configuração somente dentro do treino externo. As métricas externas comparam famílias e a análise exploratória. As regras da árvore ajustada com todo o desenvolvimento descrevem as entradas e suportes do treino. Os intervalos pareados de 95% reamostram os componentes das previsões externas em 2.000 réplicas. Eles deixam de fora a variabilidade de novos ajustes e populações.

A A1 identificou MOTIVO1 e MOTIVO2 como riscos de vazamento. Ambos ficam fora dos preditores nos três cenários. O resultado principal usa FISIO8 e STRICT4 mostra sensibilidade à retirada conjunta de IMC e sinais vitais. Em CLINICO, a inclusão de SOPRO, B2, PULSOS, PPA e HDA1 ajuda a mostrar a dependência do bloco. A disponibilidade de um achado antes do laudo ainda permitiria sua incorporação na formação do alvo. O aumento de desempenho não confirma nem descarta esse mecanismo.

## Conferência das execuções

Em uma cópia isolada, reexecutei o commit de João com o mesmo CSV. A maior diferença entre a BA publicada nas branches e a BA reproduzida no macOS foi de 0,19 ponto percentual. As árvores coincidiram e a diferença máxima ocorreu na floresta de STRICT4. Os números do artigo vêm de outra execução, a dos folds corrigidos, com as métricas recalculadas diretamente das previsões externas das doze combinações de cenário e família e as 60 seleções internas conferidas.

## Dados publicados e materiais de apoio

A execução final usa a base clínica local. Os arquivos de resultados desta revisão publicam métricas agregadas, diagnósticos por atributo, resumos de importância e dados necessários para conferir o artigo. O exportador calcula os resumos a partir da execução verificada e mantém previsões por linha, modelos, partições locais e tabelas de categorias detalhadas em `artifacts/`. As branches de revisão contêm tabelas de categorias unitárias com rótulos agregados, sem identificação nominal verificada. Esses arquivos e a ancestralidade das branches ficaram fora da integração ao ramo principal.

O [artigo IEEE](../../paper/a2_ieee_2026_11_07/output/pdf/Artigo_A2_IEEE.pdf) é o arquivo para submissão em 18/11 pelo SIGAA. O [relatório da A1](../a1_entregue/Relatorio_A1_Entregue.pdf) documenta as decisões já entregues. Os [resultados da revisão final](../../resultados/a2/revisao_final_2026_11_16/reviewed_results.json) registram a análise e a verificação.

## Conferência da rubrica

| Item | Onde conferir no artigo |
|---|---|
| IEEE de conferências, duas colunas, até cinco páginas | Quatro páginas renderizadas e verificadas usando IEEEtran 1.8b. |
| Resumo único de 100 a 150 palavras, autores e objetivo | Página 1, resumo e seção I. |
| Origem da base, alvo, desequilíbrio, exploração e vazamento | Seção II, Tabela I e Figuras 1 e 2. MOTIVO1 e MOTIVO2 excluídos dos três cenários; achados adicionais apenas na análise exploratória. |
| Pré-processamento, validação, baseline, modelos e ajuste | Seção III. Regras de limpeza, transformações por treino, 105 candidatos por cenário e validação cruzada aninhada agrupada. |
| Métricas, erros e importância | Seção IV, Tabelas II e III. Métricas externas, intervalos pareados, erro por subgrupo, importância por permutação e regra descritiva. |
| Conclusão, limites e referências | Seção V e referências. |
| Reprodutibilidade | Rodapé clicável na primeira página, código e resultados no GitHub e sementes na seção III. |
| Uso de IA generativa | Declaração após a conclusão. |

O relatório fica pronto para envio pelo SIGAA no prazo da rubrica. A apresentação é uma etapa separada, com revisão do grupo a partir do artigo e das versões já existentes.
