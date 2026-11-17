# Revisão final do relatório da A2 · 16/11/2026

A revisão compara as duas propostas com a rubrica do SIGAA, o relatório entregue na A1, o dicionário UCMF e os resultados obtidos por nova execução. A branch de João (Petas) inclui os sete commits da branch de Antônio e acrescenta um commit próprio. Os artefatos das duas propostas continuam acessíveis pelos commits de origem.

| Origem | Contribuição | Decisão para o relatório |
|---|---|---|
| Antônio, [522eed7](https://github.com/pedroafm06/Data-Mining/commit/522eed7) | Reconstrução da partição com quebras de linha portáveis e compilação IEEE no Windows | Incorporada, com verificação do arquivo oficial do Windows e manifesto de compilação ampliado. A compilação final ocorreu no macOS. |
| Antônio, [55f6f4d](https://github.com/pedroafm06/Data-Mining/commit/55f6f4d) e [f4a6637](https://github.com/pedroafm06/Data-Mining/commit/f4a6637) | Cenário com 13 atributos e pontuação do teste histórico | O cenário CLINICO entrou como comparação exploratória e recebeu os mesmos folds corrigidos. O teste histórico já foi examinado, compartilha padrões brutos com o desenvolvimento e ficou fora do resultado final. |
| Antônio, [8055f1e](https://github.com/pedroafm06/Data-Mining/commit/8055f1e) | Perfil de erros por sopro e idade | Recalculado nas previsões externas. A presença, a ausência explícita e a falta de preenchimento de SOPRO têm significados distintos. |
| Antônio, [81c867a](https://github.com/pedroafm06/Data-Mining/commit/81c867a) e [6a5d947](https://github.com/pedroafm06/Data-Mining/commit/6a5d947) | Redação, tabelas geradas da execução, leitura dos resultados e organização do README | Incorporadas a separação dos cenários, a geração de tabelas e a ligação entre artigo, dados, código e relatório. O resultado principal permanece FISIO8 porque a fonte não estabelece a cronologia nem a participação dos achados na rotulagem. |
| Antônio, [ee1115d](https://github.com/pedroafm06/Data-Mining/commit/ee1115d) | Slides e roteiro com 15 slides principais | Material para a etapa de apresentação. O conteúdo precisa acompanhar o protocolo e os números do artigo final. |
| João, [c4efa0b](https://github.com/pedroafm06/Data-Mining/commit/c4efa0b) | Bootstrap pareado, regras da árvore, reconciliação A1–A2, revisão de rubrica e dos slides | Incorporados ao relatório com os números da execução final. Os intervalos condicionam aos ajustes existentes. As regras são descritivas do treino. Os resultados e a discussão orientaram a apresentação final. |

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

O relatório fica pronto para envio pelo SIGAA no prazo da rubrica. A apresentação final usa o template da A1 e os dados da revisão de 16/11. [Slides e roteiro](../../presentation/a2_inf/README.md)

## Errata factual sobre unidades · 17/11/2026

A conferência da seção III-A com `numeric_value` e `prepare_final` mostrou que a redação anterior atribuía ao código uma correção da escala da altura que ele não executa. O texto agora registra a padronização de grafias, separadores decimais e códigos de ausência, declara as unidades adotadas e explicita a conversão de centímetros para metros apenas na fórmula do IMC. Esta correção descreve com precisão o procedimento já executado. A base, as regras de curadoria, os modelos e os resultados permanecem iguais.

## Revisão bibliográfica das referências 3, 4, 5 e 7 · 17/11/2026

A conferência separou metadados bibliográficos comprovados de informações sobre o fornecimento dos materiais na disciplina. Foram examinados os PDFs originais locais, inclusive todas as suas páginas, os metadados do pacote complementar e o estilo `IEEEtran.bst` efetivamente usado pelo artigo. As fontes editoriais de Breiman e Varma/Simon foram consultadas diretamente nos sites dos periódicos.

| Referência | Evidência confirmada | Correção e limite |
|---|---|---|
| [3], `guideline` | `Guideline for diagnostic.pdf`, uma página, no material complementar do trabalho. Não apresenta título editorial, autoria, ano editorial ou URL impressos. O título citado é o nome do arquivo. | A referência identifica o Instituto de Informática/UFG como fornecedor no SIGAA, na oferta INF0414 de 2026/2, sem atribuí-lo como autor original. Declara autoria e data editoriais não identificadas. Não inventa ano original nem URL individual. |
| [4], `ppa` | `Explanation about the PPA variable.pdf`, quatro páginas. O texto começa com “Então vamos começar.” e não credita autor, ano editorial ou URL. O título citado é o nome do arquivo. | Mesma distinção entre fornecedor e autoria original. A oferta 2026/2 identifica o contexto da disciplina, não a publicação do texto. Não usa o nome `Pedro` dos metadados do PDF como autoria bibliográfica. |
| [5], `breiman2001` | Leo Breiman, *Random Forests*, *Machine Learning*, volume 45, número 1, páginas 5–32, outubro de 2001; DOI `10.1023/A:1010933404324`. O [sumário oficial do fascículo 45(1)](https://link.springer.com/journal/10994/volumes-and-issues/45-1) confirma número, mês e paginação; a [página editorial do artigo](https://link.springer.com/article/10.1023/A:1010933404324) confirma DOI e autoria. | Acrescentados `number=1`, mês e URL DOI clicável, mantendo o DOI como metadado. |
| [7], `varma2006` | Sudhir Varma e Richard Simon, *Bias in error estimation when using cross-validation for model selection*, *BMC Bioinformatics*, volume 7, artigo 91, publicado em 23/02/2006. A [página editorial oficial](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-7-91) identifica explicitamente “article number 91” e o DOI. | Retirado `pages=91`, que representava incorretamente uma página. O identificador passou para `note={Art. no. 91}`; acrescentados mês e URL DOI clicável. Não se confundiu número de artigo com número de fascículo. |

Os dois PDFs originais estão em `Atividades Praticas/trabalho pratico (material complementar)/`, na pasta da disciplina, um nível acima da raiz deste repositório. Seus hashes são:

- `Guideline for diagnostic.pdf`: `cec38e5da5dc8501dff90b4b57dcc01b2f6ec48acfb4e4c9d470a8fa7b2d00a3`.
- `Explanation about the PPA variable.pdf`: `5b7fbd347584e9c5c7041daf39995253299f65dc97b6fa5e2e3c3485573c4cad`.

As datas de criação dos PDFs, em 2013 e 2012, e as datas de arquivos do ZIP, em 2017, não demonstram datas editoriais. O campo de autor do segundo PDF contém apenas `Pedro` e seu título automático do Word não é um crédito de autoria nem título de publicação. Esses dados foram preservados como observações de procedência e não convertidos em autoria ou ano nas referências.

O metadado local de origem do ZIP registra o fornecimento do pacote pelo Google Drive. O endereço de download temporário não é reproduzido neste documento público. Ele se refere ao pacote inteiro, e o acesso remoto atual não foi comprovado. Por isso, não foi usado como URL pública individual das referências. Os documentos da auditoria semântica em `docs/a2/auditoria_2026_11_07/` também identificam os dois PDFs como material complementar sem autor original creditado.

A inspeção de `vendor/IEEEtran/bibtex/IEEEtran.bst` mostrou que a lista `ENTRY` não inclui `eid`, `articleno` ou `doi`. A função de artigos formata `pages` com o prefixo de página, portanto `pages=91` produziria “p. 91”. A alternativa aplicada usa `note`, suportado pelo estilo, para explicitar “Art. no. 91”. As URLs DOI foram colocadas no campo `url`, que o estilo efetivamente imprime; o campo `doi` permanece útil como metadado, mas não é a única forma de tornar o identificador visível no PDF.

Não foram alterados dados, experimentos ou métricas. Esta etapa modificou somente a bibliografia e este registro. A compilação conjunta foi realizada após integrar as correções. As quatro páginas finais foram renderizadas e inspecionadas. O [fechamento IEEE](Fechamento_IEEE_2026_11_17.md) registra a verificação consolidada.
