# Reprodução da A2 completa

A execução segue: entendimento e seleção documentados -> preparação revisada -> busca de modelos -> avaliação -> interpretação -> aplicação com verificação de cobertura -> relatório. Os comandos usam as mesmas funções dos notebooks, sem uma segunda implementação estatística.

## Entrada e ambiente

Obtenha a base pelo material da disciplina. O hash esperado está no [guia de dados](../dados/README.md). O CSV não é distribuído pelo Git. O padrão é `dados/raw/UCMF_raw.csv`; `--source` aceita outro caminho.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

`requirements.lock` registra Python3.14/macOS. Para reproduzir esse ambiente, use `python -m pip install -r requirements.lock` e `python -m pip install -e . --no-deps`. Os extras permitem resolver dependências em outras plataformas; diferenças precisam ser registradas.

## Processo completo

```bash
python tools/run_full_kdd.py
python tools/build_full_kdd_notebook.py
python -m pytest -q
```

A busca principal compara81 configurações por cenário em cinco folds. A avaliação aninhada repete a busca em3x3 folds no desenvolvimento. A execução registrada da mineração levou aproximadamente nove minutos; o tempo depende da máquina. Candidatos, decisões, parâmetros e seeds são registrados antes da avaliação do teste histórico.

Para entrada externa:

```bash
export KDD_SOURCE="/caminho/para/UCMF_raw.csv"
python tools/run_full_kdd.py --source "$KDD_SOURCE"
python tools/build_full_kdd_notebook.py --source "$KDD_SOURCE"
```

O notebook completo permite reutilizar uma execução concluída compatível. A compatibilidade exige fonte, protocolo, código de ajuste e hashes dos artefatos; os modelos são reaplicados e as métricas conferidas. Para executar essa mesma opção pelo terminal:

```bash
python tools/run_full_kdd.py --reuse-mining
```

Reutilizar não muda hiperparâmetros pelo teste. A aplicação e os relatórios são regenerados sem novo treinamento. `--skip-preparation` é uma opção técnica para quem já possui a preparação local correspondente.

## Componentes isolados

```bash
python tools/run_preprocessing.py
python tools/build_preprocessing_report.py
python tools/build_preprocessing_notebook.py
python tools/run_application.py
python tools/build_full_kdd_report.py
python tools/export_aggregates.py
```

As duas últimas ferramentas consomem resultados já produzidos. O relatório completo exporta agregados da mineração e da aplicação para `resultados/a2/kdd_completo/`. O gerador da preparação exporta apenas seu relatório; `export_aggregates.py` copia os diagnósticos agregados dessa etapa.

## Saídas e limites

`artifacts/a2_preprocessing/` contém base semântica, base da política, proveniência, intervenções, matrizes e transformadores. `artifacts/a2_mining/` contém os experimentos congelados, auditoria de252 ajustes internos de pré-processamento, predições e modelos. `artifacts/a2_application/` registra a revisão de cobertura e as demonstrações por linha; `artifacts/a2_kdd/` registra ambiente e reaplicação dos modelos. Todas essas pastas permanecem locais.

O relatório integrado e as decisões estão em `docs/a2/`; o notebook completo é `notebooks/02_kdd_completo_a2.ipynb`. A A1 histórica não é reescrita. O notebook da preparação é um componente do processo completo.

Em clone sem dados ou artefatos, testes dependentes desses arquivos são pulados explicitamente; os testes unitários usam exemplos pequenos. A validação integral requer a fonte e uma execução completa. Os resultados são acadêmicos, sujeitos às hipóteses documentadas sobre rótulos, grupos candidatos e exploração prévia.
