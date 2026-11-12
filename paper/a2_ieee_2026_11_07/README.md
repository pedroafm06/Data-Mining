# Artigo A2 no formato IEEE de conferências

[Artigo A2 em PDF](output/pdf/Artigo_A2_IEEE.pdf): cinco páginas em duas colunas, resumo de 136 palavras (contagem de `tools/build.py`) e link do repositório no rodapé da primeira página.

## De onde vem cada número, tabela e figura

Nenhum resultado é digitado no texto. A cadeia é:

1. `tools/run_rubric_audit.py` e `tools/export_rubric_audit.py` (raiz do repositório) geram `results/reviewed_results.json`.
2. `tools/gerar_numeros.py` lê esse JSON e escreve `generated/numeros.tex` (macros usadas no texto), `generated/tab_resultados.tex` (Tabela II) e `generated/tab_teste.tex` (Tabela IV). A Tabela III usa macros do mesmo arquivo.
3. `tools/figura_eda.py` lê o mesmo JSON e gera `figures/eda_alvo_achados.pdf` (Fig. 1) e `figures/importancia.pdf` (Fig. 2).

| Elemento | Gerador | Fonte |
|---|---|---|
| Fig. 1 (alvo, achados, idade, FC) | `tools/figura_eda.py` | `eda` |
| Tabela I (decisão por atributo) | texto em `sections/02_dados.tex` | `excluded_fields`, `pools` |
| Tabela II (métricas) | `tools/gerar_numeros.py` | `metrics` |
| Tabela III (matrizes de confusão) | macros de `tools/gerar_numeros.py` | `metrics` |
| Fig. 2 (importância por permutação) | `tools/figura_eda.py` | `importance` |
| Tabela IV (teste histórico) | `tools/gerar_numeros.py` | `historical_test_metrics` |
| Análise de erros e reconciliação A1/A2 | macros | `error_analysis`, `a1_reconciliation` |

## Compilar

A classe IEEEtran 1.8b e o estilo bibliográfico vêm do CTAN e estão em `vendor/`; versões e hashes ficam em `provenance.lock.json`. O Tectonic 0.17.0 oficial está fixado para macOS arm64 e Windows x86_64. No diretório do artigo:

```sh
python tools/bootstrap.py
python tools/gerar_numeros.py
python tools/figura_eda.py
python tools/build.py --final
```

`--final` confere o SHA-256 de `results/reviewed_results.json` com `submission_config.json`, a URL pública do repositório, o limite de cinco páginas e o resumo entre 100 e 150 palavras. Sem `pdfinfo`, a contagem de páginas usa `pypdf`. Com o cache TeX preenchido, `--offline` usa só os recursos locais.
