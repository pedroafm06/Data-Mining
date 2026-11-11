# Mineração de Dados - A2: processo completo do KDD

Trabalho da disciplina INF0414, UFG, 2026/2. Base UCMF: 12.873 registros e 21 variáveis. Grupo: Antônio Henrique Queiroz Villar Lopes, João Vitor Fernandes Ferreira, Mateus Nery Bailão e Pedro Augusto Ferreira Matos. Professor: Rogério Lopes Salvini.

**A A2 aproveita e melhora a A1 e completa o KDD inteiro.** A A1 avaliada continua sendo a versão já entregue. A versão atual inclui entendimento do domínio e dos dados, seleção, limpeza, transformação, mineração, avaliação, interpretação e aplicação/documentação do conhecimento. A entrega da A2 segue a descrição publicada no SIGAA.

## Entrega da A2

- [Artigo em PDF](paper/a2_ieee_2026_11_07/output/pdf/Artigo_A2_IEEE.pdf) no formato IEEE de conferências.
- [Apresentação editável](presentation/a2_2026_11_07/output/Apresentacao_A2_UCMF.pptx), [slides em PDF](presentation/a2_2026_11_07/output/Apresentacao_A2_UCMF.pdf) e [roteiro de 14 min 30 s com arguição](presentation/a2_2026_11_07/output/Roteiro_e_Arguicao.md).
- [Auditoria das 21 variáveis](docs/a2/auditoria_2026_11_07/Parecer_Semantico_e_Decisoes.md), [verificação experimental](docs/a2/auditoria_2026_11_07/Verificacao_Experimental.json) e [conferência da rubrica](docs/a2/auditoria_2026_11_07/conformidade_rubrica.json).
- [Código e instruções de reprodução da A2](#reproduzir-a-revisão-da-a2).

### Resultados da revisão

A revisão refez a comparação com 105 configurações por cenário e validação cruzada aninhada de cinco folds externos e três internos, com estratificação e agrupamento por equivalência candidata. O conjunto de 9.361 registros de desenvolvimento é o mesmo para todos os procedimentos. O teste histórico ficou fora da pontuação.

| Cenário | Melhor família pela BA | BA | Sensibilidade |
|---|---|---:|---:|
| FISIO8 | Floresta aleatória | 62,87% | 59,29% |
| STRICT4 | Regressão logística | 59,74% | 52,03% |

SOPRO, B2, PULSOS, PPA, HDA1, HDA2, MOTIVO1 e MOTIVO2 ficam fora dos preditores nos dois cenários. A revisão também examina a informação contida em padrões de ausência, a dependência dos atributos por permutação e o comportamento com rótulos embaralhados. A cronologia da coleta e o critério diagnóstico de referência continuam desconhecidos. [Métricas e experimentos da revisão](resultados/a2/auditoria_2026_11_07/).

## Reproduzir a revisão da A2

Use o arquivo original `UCMF_raw.csv` disponibilizado na disciplina. O ambiente de referência usa Python 3.14.6 no macOS. Na raiz do repositório, execute:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python tools/run_rubric_audit.py --source "/caminho/para/UCMF_raw.csv"
python tools/export_rubric_audit.py --source "/caminho/para/UCMF_raw.csv"
python -m pytest -q
```

O programa verifica a versão da fonte pelo SHA-256 e reconstrói a partição de desenvolvimento a partir das regras e sementes. O protocolo fixa `random_state=42` nos estimadores estocásticos, 743 nos folds externos, 811 mais o índice do fold nos internos e 43 na seleção final. Dados clínicos, previsões por registro e modelos ajustados ficam em arquivos locais ignorados pelo Git. As [métricas externas](resultados/a2/auditoria_2026_11_07/family_nested_metrics.csv) e a [síntese dos resultados](resultados/a2/auditoria_2026_11_07/reviewed_results.json) estão disponíveis no repositório.

## Desenvolvimento anterior da A2

- [Relatório integrado em PDF](docs/a2/Relatorio_A2_KDD_Completo.pdf) · [versão em texto](docs/a2/Relatorio_A2_KDD_Completo.md).
- [Decisões, alternativas e justificativas](docs/a2/Decisoes_KDD_Completo.md) · [registro estruturado das microdecisões](docs/a2/Registro_Microdecisoes.csv).
- [Notebook completo executado](notebooks/02_kdd_completo_a2.ipynb).
- [Conceitos utilizados](docs/a2/Conceitos_Utilizados.md) · [estado e verificação](docs/a2/Estado_e_Verificacao.md).
- [Resultados, parâmetros por fold e finais](resultados/a2/kdd_completo/).

O relatório de [pré-processamento](docs/a2/Relatorio_Preprocessamento_A2.pdf), suas [decisões por variável](docs/a2/Decisoes_Preprocessamento_A2.md) e o [notebook da preparação](notebooks/01_preprocessamento_a2.ipynb) são componentes da A2 completa. A [A1 entregue](docs/a1_entregue/README.md) permanece preservada byte a byte. Os [experimentos com a preparação anterior](docs/historico/README.md) estão separados dos resultados atuais.

### Comparação histórica de cenários

A revisão preserva todas as linhas e os originais, separa erro, suspeita e estimativa, corrige idade relativa quando defensável e aplica representações numéricas explícitas. A mineração compara **81 configurações em cada um de três cenários**, com mediana global/etária e demais parâmetros aprendidos dentro de cada treino de fold. Há CV5-fold, avaliação aninhada3x3 no desenvolvimento e avaliação secundária no teste histórico, já explorado anteriormente.

Foram testados controle majoritário, árvores com diferentes critérios/complexidades/poda/pesos, logística com regularização e representações alternativas, e florestas complementares. Redução, indicadores, qualidade, PCA e sobre/subamostragem foram contestados no desenvolvimento. Os resultados incluem métricas, curvas, intervalos, subgrupos, interpretação e aplicação aos não rotulados. A hipótese inicial de cobertura da aplicação foi rejeitada e substituída por uma regra de suporte explicitada; previsões não viram rótulos de treino.

| Cenário | Informação disponível | BA nested no desenvolvimento | BA no teste histórico |
|---|---|---:|---:|
| A | Medidas, achados e contexto | 0,9191 | 0,9292 |
| B | Sete medidas e SEXO | 0,6309 | 0,6523 |
| B_contexto | A sem PULSOS, B2 e SOPRO | 0,7096 | 0,7416 |

Esses números classificam o rótulo registrado. Não são validação clínica ou estimativa de desempenho em pacientes novos. A diferença entre cenários não prova causalidade; o relatório mostra suportes, erros, alternativas, instabilidade da seleção e limites de cobertura.

## Reproduzir os experimentos anteriores

Requer Python 3.11 ou superior. A execução registrada usou Python3.14 e as versões de `requirements.lock` em macOS.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Coloque a cópia da base fornecida pela disciplina em `dados/raw/UCMF_raw.csv`; [origem e hash esperados](dados/README.md). Em seguida:

```bash
python tools/run_full_kdd.py
python tools/build_full_kdd_notebook.py
python -m pytest -q
```

O primeiro comando refaz a busca. O notebook reutiliza uma busca concluída somente após verificar compatibilidade e reaplicar os modelos; num clone sem artefatos, ele executa a busca. Para atualizar aplicação e relatório reutilizando explicitamente modelos compatíveis:

```bash
python tools/run_full_kdd.py --reuse-mining
```

`--source /caminho/UCMF_raw.csv` permite entrada externa. `KDD_SOURCE` é reconhecido pelos notebooks; seus geradores também aceitam `--source`. As instruções detalhadas estão no [guia de reprodução](docs/Reproducao.md).

## Organização e rastreabilidade

`src/kdd_revision/preprocessing/` implementa a preparação atual; `mining.py` e `full_kdd.py` implementam a busca e avaliação; `application.py` verifica cobertura; `reproduction.py` confere a execução salva. `config/a2_kdd_protocol.json` congela candidatos, critérios e seeds; `a2_application_policy.json` registra a revisão independente da cobertura. As decisões de limpeza, os parâmetros efetivos dos estimadores e as fontes didáticas verificadas também estão em `config/`.

`artifacts/` guarda localmente bases, proveniência, matrizes, predições, modelos e manifestos. `resultados/` contém apenas agregados e parâmetros de ajuste. Dados clínicos por registro e objetos serializados não são distribuídos pelo Git. A partição de referência contém apenas IDs e grupos candidatos para reproduzir a separação histórica.

A qualidade foi explorada na coorte completa; nested CV não desfaz essa exploração. Grupos candidatos não comprovam identidade de pacientes. A1 preservada, teste explorado e decisões operacionais são explicitados, sem alegação de ótimo universal ou de submissão no SIGAA.
