# Mineração de Dados — A2: classificação de registros de cardiologia pediátrica (UCMF)

INF0414, UFG, 2026/2. Grupo 3: Antônio Henrique Queiroz Villar Lopes, João Vitor Fernandes Ferreira, Mateus Nery Bailão e Pedro Augusto Ferreira Matos. Professor: Rogério Lopes Salvini.

## 1. Artigo

[**Artigo_A2_IEEE.pdf**](paper/a2_ieee_2026_11_07/output/pdf/Artigo_A2_IEEE.pdf): formato IEEE de conferências, 5 páginas em 2 colunas. Fontes LaTeX em [`paper/a2_ieee_2026_11_07/`](paper/a2_ieee_2026_11_07/).

## 2. Slides

[**Slides em PDF**](presentation/a2_2026_11_07/output/Apresentacao_A2_UCMF.pdf) (15 slides) · [PowerPoint editável](presentation/a2_2026_11_07/output/Apresentacao_A2_UCMF.pptx) · [roteiro de 14 min 30 s com perguntas de arguição](presentation/a2_2026_11_07/output/Roteiro_e_Arguicao.md).

## 3. Onde está o código de cada tabela e figura

Nenhum número do artigo ou dos slides é digitado à mão. Todos vêm de [`reviewed_results.json`](resultados/a2/auditoria_2026_11_07/reviewed_results.json).

| Saída | Código |
|---|---|
| Experimentos (3 cenários × 4 famílias, validação aninhada, teste histórico) | [`src/kdd_revision/rubric_audit.py`](src/kdd_revision/rubric_audit.py), executado por [`tools/run_rubric_audit.py`](tools/run_rubric_audit.py) |
| `reviewed_results.json`, análise de erros, reconciliação A1/A2, agregados da EDA | [`tools/export_rubric_audit.py`](tools/export_rubric_audit.py) |
| Fig. 1 (alvo, achados de exame, idade e FC) e Fig. 2 (importância) | [`paper/.../tools/figura_eda.py`](paper/a2_ieee_2026_11_07/tools/figura_eda.py) |
| Tabelas II, III e IV e todos os números do texto | [`paper/.../tools/gerar_numeros.py`](paper/a2_ieee_2026_11_07/tools/gerar_numeros.py) → `generated/*.tex` |
| Tabela I (decisão por atributo) | lista de atributos em `rubric_audit.py` (`CLINICO`, `EXCLUDED_REASONS`) |
| Slides e roteiro | [`presentation/.../build_data.py`](presentation/a2_2026_11_07/build_data.py) e [`build_deck.mjs`](presentation/a2_2026_11_07/build_deck.mjs) |
| Limpeza e transformação | [`src/kdd_revision/preprocessing/`](src/kdd_revision/preprocessing/) |

## 4. Como reproduzir

**A base `UCMF_raw.csv` não está no repositório**, por ser dado clínico da disciplina. Use a cópia distribuída no SIGAA (SHA-256 `35e68400…24ea1`, conferido pelo código) e coloque-a em `dados/raw/UCMF_raw.csv` ou passe `--source`.

```sh
python -m venv .venv
.venv/Scripts/activate            # Windows; no macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.lock
python tools/run_rubric_audit.py --source dados/raw/UCMF_raw.csv      # ~20 min
python tools/export_rubric_audit.py --source dados/raw/UCMF_raw.csv
python -m pytest -q
cd paper/a2_ieee_2026_11_07
python tools/bootstrap.py && python tools/gerar_numeros.py && python tools/figura_eda.py
python tools/build.py --final
```

O primeiro comando reconstrói a partição de desenvolvimento e confere seu SHA-256 com o publicado. Registros clínicos, previsões por registro e modelos ajustados ficam em `artifacts/`, ignorado pelo Git; `resultados/` só tem agregados. Para os slides, veja o [README da apresentação](presentation/a2_2026_11_07/README.md).

## 5. Sementes

`random_state=42` nos estimadores; 743 nos 5 *folds* externos; 811+k nos 3 *folds* internos do *fold* externo k; 43 na escolha do modelo final; 1700+k na importância por permutação; 911 e 914 no controle com rótulos embaralhados.

## 6. Resultados

Validação cruzada aninhada no desenvolvimento (9.361 registros), melhor família de cada cenário pela acurácia balanceada (BA). O teste histórico (2.342 registros, já examinado em fases anteriores) é avaliação secundária.

| Cenário | Atributos | Melhor família | BA | Sensibilidade | Especificidade | BA no teste histórico |
|---|---|---|---:|---:|---:|---:|
| **CLINICO** (principal) | 13: medidas, sinais vitais, PPA, exame físico, HDA1 | Árvore | 91,94% | 87,50% | 96,38% | 92,92% |
| FISIO8 (sensibilidade) | 8: medidas, sinais vitais, sexo | Floresta | 62,91% | 58,91% | 66,91% | 65,23% |
| STRICT4 (sensibilidade) | 4: peso, altura, idade, sexo | Logística | 59,74% | 52,03% | 67,45% | 60,33% |

No CLINICO, árvore, logística e floresta diferem menos de 0,05 ponto de BA, porque o sopro concentra a informação. Ficam fora dos preditores: ID, datas brutas, Convênio, MOTIVO1, MOTIVO2 e HDA2. A justificativa está no artigo.

Esta execução foi feita no Windows com o `requirements.lock`. Árvore, logística e referência reproduzem exatamente a execução anterior em macOS; a floresta aleatória mostra pequenas diferenças entre plataformas com as mesmas sementes (por exemplo, BA de FISIO8 62,87% → 62,91%).

---

O desenvolvimento anterior da A2 e a comparação histórica de cenários estão em [`docs/historico/`](docs/historico/README.md). A [A1 entregue](docs/a1_entregue/README.md) permanece preservada byte a byte.
