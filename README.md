# Mineração de Dados — KDD

Trabalho da disciplina INF0414, UFG, 2026/2. Estudo da base UCMF de atendimentos pediátricos, com 12.873 registros e 21 variáveis. Grupo: Antônio Henrique Queiroz Villar Lopes, João Vitor Fernandes Ferreira, Mateus Nery Bailão e Pedro Augusto Ferreira Matos. Professor: Rogério Lopes Salvini.

**A A1 avaliada é a que já foi entregue. Todas as melhorias e etapas novas integram a A2**, conforme orientação do professor comunicada em 04/11/2026. A A2 tem como objetivo concluir o processo KDD; sua descrição detalhada ainda será complementada. Este repositório registra o estado atual do trabalho.

| Material | Estado | Onde começar |
|---|---|---|
| A1 entregue | Preservada, sem alterações | [Relatório original](docs/a1_entregue/Relatorio_A1_Entregue.pdf) · [apresentação original](docs/a1_entregue/Apresentacao_A1_Entregue.pdf) |
| A2: revisão da limpeza e transformação | Executada e verificada | [Relatório](docs/a2/Relatorio_Preprocessamento_A2.pdf) · [decisões por variável](docs/a2/Decisoes_Preprocessamento_A2.md) · [notebook](notebooks/01_preprocessamento_a2.ipynb) |
| Modelagem e avaliação anteriores | Histórico exploratório, com preparação antiga | [Histórico e limitações](docs/historico/README.md) |
| A2: modelagem e avaliação com a base atual | Pendente | [Continuação do KDD](docs/a2/Continuidade_KDD.md) |

A preparação atual preserva todas as linhas, corrige a idade relativa quando há evidência suficiente e separa valores observados, suspeitos e estimados. As representações aplicadas têm 93 atributos: sete medidas, sete indicadores de imputação e 79 colunas one-hot. Há versões em unidades originais, padronizada e com log1p somente no peso seguido de padronização. As alternativas de imputação e de qualidade também foram exportadas localmente. Nenhum classificador foi treinado com essa preparação nesta revisão.

## Organização

- `src/kdd_revision/preprocessing/`: preparação atual da A2 e transformações.
- `notebooks/`: execução comentada da preparação atual.
- `docs/a1_entregue/`: documentos históricos preservados por hash.
- `docs/a2/`: relatório atual, decisões, conceitos e continuidade.
- `docs/historico/`: relatórios dos experimentos com a preparação anterior.
- `resultados/a2/preprocessamento/`: tabelas e diagnósticos agregados da revisão atual.
- `config/`: políticas explícitas, esquema e partições de referência.
- `tests/`: regras de limpeza, prevenção de vazamento, alinhamento e reprodutibilidade.
- `dados/` e `artifacts/`: entrada e saídas locais excluídas do Git.

## Reproduzir a preparação da A2

Requer Python 3.11 ou superior. A execução verificada usou Python 3.14 e as versões de `requirements.lock`. O lock registra o ambiente macOS utilizado; a instalação pelos extras abaixo é a opção portável.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Obtenha a base do material da disciplina e coloque `UCMF_raw.csv` em `dados/raw/`. O [guia de dados](dados/README.md) registra o hash esperado. Em seguida:

```bash
python tools/run_preprocessing.py
python tools/build_preprocessing_report.py
python tools/build_preprocessing_notebook.py
python -m pytest -q
```

Para usar a base guardada em outro local, passe `--source /caminho/UCMF_raw.csv` ao primeiro comando e defina `KDD_SOURCE` com esse caminho para executar o notebook. O gerador de relatório também aceita `--source`. As instruções completas estão no [guia de reprodução](docs/Reproducao.md).

As matrizes completas, seus subconjuntos, alvos, IDs, proveniência e objetos de transformação são gerados em `artifacts/a2_preprocessing/`. As matrizes não incluem ID nem alvo; os arquivos auxiliares preservam a ordem das linhas. A transformação aprende somente com 9.361 registros de desenvolvimento e aplica os mesmos parâmetros ao teste histórico (2.342), a uma quarentena de equivalência e aos 1.169 registros sem alvo.

## Conceitos e limites

Os [conceitos utilizados](docs/a2/Conceitos_Utilizados.md) são explicitados junto da sua finalidade. A melhor regra foi procurada comparando alternativas, sem alegar ótimo universal. A guarda antropométrica é uma hipótese operacional de curadoria, sem estabelecer faixas clínicas de normalidade. O mascaramento artificial não comprova o mecanismo das ausências reais.

Antes de comparar modelos, imputação, vocabulário e escala precisam ser ajustados novamente em cada fold. A matriz de desenvolvimento já transformada serve para inspeção e aplicação, mas não autoriza seleção por validação cruzada com parâmetros aprendidos uma única vez. O teste histórico já passou por exploração; os resultados anteriores não validam a preparação atual. Formação do alvo, unidade paciente/consulta e disponibilidade temporal dos achados continuam exigindo esclarecimento.

A base clínica, a auditoria por linha e os modelos serializados não são distribuídos pelo Git. A lista de partições contém apenas identificadores e grupos candidatos para reproduzir a separação histórica, sem medidas clínicas. Materiais didáticos e referências de terceiros permanecem nas respectivas fontes.
