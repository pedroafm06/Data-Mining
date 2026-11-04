# Reprodução da preparação atual

Execute os comandos a partir da raiz clonada do repositório. O CSV não é incluído no Git; obtenha-o pelo material da disciplina e confira [o hash da entrada](../dados/README.md).

## Ambiente

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

`requirements.lock` registra as versões da execução original em Python 3.14/macOS. A instalação pelos extras resolve dependências da plataforma atual. Para reproduzir o ambiente macOS registrado, use `python -m pip install -r requirements.lock` e depois `python -m pip install -e . --no-deps`. Diferenças de versões precisam ser registradas.

## Preparação, relatório e notebook

```bash
python tools/run_preprocessing.py --source dados/raw/UCMF_raw.csv
python tools/build_preprocessing_report.py --source dados/raw/UCMF_raw.csv
python tools/build_preprocessing_notebook.py
python -m pytest -q
```

O notebook chama as mesmas funções da biblioteca. Para manter o CSV em outra pasta:

```bash
export KDD_SOURCE="/caminho/para/UCMF_raw.csv"
python tools/run_preprocessing.py --source "$KDD_SOURCE"
python tools/build_preprocessing_report.py --source "$KDD_SOURCE"
python tools/build_preprocessing_notebook.py
```

O comando de preparação permite `--partitions` para informar a partição e `--output-dir` para escolher outra pasta de artefatos. O padrão é `config/particoes_referencia.csv` e `artifacts/a2_preprocessing/`. Use os mesmos parâmetros ao gerar o relatório. `--help` documenta as opções de cada ferramenta.

O relatório vai para `docs/a2/`, e o notebook para `notebooks/01_preprocessamento_a2.ipynb`. Os geradores sobrescrevem somente as respectivas saídas da revisão; não alteram os documentos históricos da A1.

## Saídas locais

`base_semantica.csv` preserva as 21 variáveis tratadas; `base_para_transformacao.csv` aplica a política de qualidade anterior à imputação. `proveniencia.csv` e `alteracoes.csv` permitem rastrear as decisões. Essas saídas contêm informação por registro e permanecem fora do Git.

As três matrizes principais são `matriz_unidades.csv`, `matriz_padronizada.csv` e `matriz_log_peso_padronizada.csv`. Os sufixos identificam desenvolvimento, teste, quarentena e não rotulados. `mapa_linhas.csv` contém ID, partição e y na mesma ordem. Alvos e IDs separados acompanham cada matriz. O objeto `transformador_preprocessamento.joblib` guarda os parâmetros ajustados e pode reaplicar as representações.

A exportação é conferida contra a reaplicação do objeto salvo. Os indicadores e one-hot permanecem 0/1; cada categórica tem exatamente uma categoria ativa. O manifesto relaciona entrada, configuração, código e saídas. Imputação é estimativa: não a interprete como medida clínica registrada.

Os testes unitários usam exemplos pequenos e não exigem a base clínica. Testes de integração com arquivos locais podem ser pulados em um clone sem dados; a execução completa requer a entrada e os artefatos gerados.
