# Mineração de Dados - A2: processo completo do KDD

Trabalho da disciplina INF0414, UFG, 2026/2. Base UCMF: 12.873 registros e 21 variáveis. Grupo: Antônio Henrique Queiroz Villar Lopes, João Vitor Fernandes Ferreira, Mateus Nery Bailão e Pedro Augusto Ferreira Matos. Professor: Rogério Lopes Salvini.

**A A2 aproveita e melhora a A1 e completa o KDD inteiro.** A A1 avaliada continua sendo a versão já entregue. A versão atual inclui entendimento do domínio e dos dados, seleção, limpeza, transformação, mineração, avaliação, interpretação e aplicação/documentação do conhecimento. A descrição formal posterior da A2 poderá acrescentar exigências de entrega e apresentação.

## Começar pela A2 completa

- [Relatório integrado em PDF](docs/a2/Relatorio_A2_KDD_Completo.pdf) · [versão em texto](docs/a2/Relatorio_A2_KDD_Completo.md).
- [Decisões, alternativas e justificativas](docs/a2/Decisoes_KDD_Completo.md) · [registro estruturado das microdecisões](docs/a2/Registro_Microdecisoes.csv).
- [Notebook completo executado](notebooks/02_kdd_completo_a2.ipynb).
- [Conceitos utilizados](docs/a2/Conceitos_Utilizados.md) · [estado e verificação](docs/a2/Estado_e_Verificacao.md).
- [Resultados, parâmetros por fold e finais](resultados/a2/kdd_completo/).

O relatório de [pré-processamento](docs/a2/Relatorio_Preprocessamento_A2.pdf), suas [decisões por variável](docs/a2/Decisoes_Preprocessamento_A2.md) e o [notebook da preparação](notebooks/01_preprocessamento_a2.ipynb) são componentes da A2 completa. A [A1 entregue](docs/a1_entregue/README.md) permanece preservada byte a byte. Os [experimentos com a preparação anterior](docs/historico/README.md) estão separados dos resultados atuais.

## O que foi executado

A revisão preserva todas as linhas e os originais, separa erro, suspeita e estimativa, corrige idade relativa quando defensável e aplica representações numéricas explícitas. A mineração compara **81 configurações em cada um de três cenários**, com mediana global/etária e demais parâmetros aprendidos dentro de cada treino de fold. Há CV5-fold, avaliação aninhada3x3 no desenvolvimento e avaliação secundária no teste histórico, já explorado anteriormente.

Foram testados controle majoritário, árvores com diferentes critérios/complexidades/poda/pesos, logística com regularização e representações alternativas, e florestas complementares. Redução, indicadores, qualidade, PCA e sobre/subamostragem foram contestados no desenvolvimento. Os resultados incluem métricas, curvas, intervalos, subgrupos, interpretação e aplicação aos não rotulados. A hipótese inicial de cobertura da aplicação foi rejeitada e substituída por uma regra de suporte explicitada; previsões não viram rótulos de treino.

| Cenário | Informação disponível | BA nested no desenvolvimento | BA no teste histórico |
|---|---|---:|---:|
| A | Medidas, achados e contexto | 0,9191 | 0,9292 |
| B | Sete medidas e SEXO | 0,6309 | 0,6523 |
| B_contexto | A sem PULSOS, B2 e SOPRO | 0,7096 | 0,7416 |

Esses números classificam o rótulo registrado. Não são validação clínica ou estimativa de desempenho em pacientes novos. A diferença entre cenários não prova causalidade; o relatório mostra suportes, erros, alternativas, instabilidade da seleção e limites de cobertura.

## Reproduzir

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
