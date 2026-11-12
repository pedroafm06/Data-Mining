# Histórico experimental

Os relatórios desta pasta registram a modelagem exploratória executada com uma preparação anterior. A correção de idade, a nova política de qualidade, a imputação selecionada e a separação do registro com cópia no teste ainda não foram integradas a esses modelos.

Os módulos `prepare.py`, `transforms.py`, `analysis.py`, `experiments.py` e as configurações `protocolo_experimental.json` e `reproducibility_reference.json` foram conservados como referência técnica dessa execução. O código atual de preparação está em `src/kdd_revision/preprocessing/`.

Os resultados antigos não estabelecem desempenho da preparação atual. O teste histórico já foi explorado; repetir sua avaliação não cria um teste independente.

- [Protocolo experimental anterior](Protocolo_Experimental_Anterior.md) · [resultados experimentais anteriores](Resultados_Experimentais_Anteriores.md).

## Desenvolvimento anterior da A2

- [Relatório integrado em PDF](../a2/Relatorio_A2_KDD_Completo.pdf) · [versão em texto](../a2/Relatorio_A2_KDD_Completo.md).
- [Decisões, alternativas e justificativas](../a2/Decisoes_KDD_Completo.md) · [registro estruturado das microdecisões](../a2/Registro_Microdecisoes.csv).
- [Notebook completo executado](../../notebooks/02_kdd_completo_a2.ipynb).
- [Conceitos utilizados](../a2/Conceitos_Utilizados.md) · [estado e verificação](../a2/Estado_e_Verificacao.md).
- [Resultados, parâmetros por fold e finais](../../resultados/a2/kdd_completo/).

O relatório de [pré-processamento](../a2/Relatorio_Preprocessamento_A2.pdf), suas [decisões por variável](../a2/Decisoes_Preprocessamento_A2.md) e o [notebook da preparação](../../notebooks/01_preprocessamento_a2.ipynb) são componentes da A2 completa. A [A1 entregue](../a1_entregue/README.md) permanece preservada byte a byte.

## Comparação histórica de cenários

A revisão preserva todas as linhas e os originais, separa erro, suspeita e estimativa, corrige idade relativa quando defensável e aplica representações numéricas explícitas. A mineração compara **81 configurações em cada um de três cenários**, com mediana global/etária e demais parâmetros aprendidos dentro de cada treino de fold. Há CV 5-fold, avaliação aninhada 3x3 no desenvolvimento e avaliação secundária no teste histórico, já explorado anteriormente.

Foram testados controle majoritário, árvores com diferentes critérios/complexidades/poda/pesos, logística com regularização e representações alternativas, e florestas complementares. Redução, indicadores, qualidade, PCA e sobre/subamostragem foram contestados no desenvolvimento. Os resultados incluem métricas, curvas, intervalos, subgrupos, interpretação e aplicação aos não rotulados. A hipótese inicial de cobertura da aplicação foi rejeitada e substituída por uma regra de suporte explicitada; previsões não viram rótulos de treino.

| Cenário | Informação disponível | BA nested no desenvolvimento | BA no teste histórico |
|---|---|---:|---:|
| A | Medidas, achados e contexto | 0,9191 | 0,9292 |
| B | Sete medidas e SEXO | 0,6309 | 0,6523 |
| B_contexto | A sem PULSOS, B2 e SOPRO | 0,7096 | 0,7416 |

Esses números classificam o rótulo registrado com a preparação anterior e não são os resultados finais da A2 (veja o [README principal](../../README.md)).

## Reproduzir os experimentos anteriores

Requer Python 3.11 ou superior. A execução registrada usou Python 3.14 e as versões de `requirements.lock` em macOS.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Coloque a cópia da base fornecida pela disciplina em `dados/raw/UCMF_raw.csv`; [origem e hash esperados](../../dados/README.md). Em seguida:

```bash
python tools/run_full_kdd.py
python tools/build_full_kdd_notebook.py
python -m pytest -q
```

O primeiro comando refaz a busca. O notebook reutiliza uma busca concluída somente após verificar compatibilidade e reaplicar os modelos. Para atualizar aplicação e relatório reutilizando modelos compatíveis: `python tools/run_full_kdd.py --reuse-mining`. As instruções detalhadas estão no [guia de reprodução](../Reproducao.md).

## Organização do código anterior

`src/kdd_revision/preprocessing/` implementa a preparação atual; `mining.py` e `full_kdd.py` implementam a busca e avaliação anteriores; `application.py` verifica cobertura; `reproduction.py` confere a execução salva. `config/a2_kdd_protocol.json` congela candidatos, critérios e sementes dessa fase.
