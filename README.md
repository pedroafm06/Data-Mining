# Mineração de Dados - A2: processo completo do KDD

Trabalho da disciplina INF0414, UFG, 2026/2. Base UCMF: 12.873 registros e 21 variáveis. Grupo: Antônio Henrique Queiroz Villar Lopes, João Vitor Fernandes Ferreira, Mateus Nery Bailão e Pedro Augusto Ferreira Matos. Professor: Rogério Lopes Salvini.

**A A2 aproveita e melhora a A1 e completa o KDD inteiro.** A A1 avaliada continua sendo a versão já entregue. A versão atual inclui entendimento do domínio e dos dados, seleção, limpeza, transformação, mineração, avaliação, interpretação e aplicação/documentação do conhecimento. A entrega da A2 segue a descrição publicada no SIGAA.

## Entrega da A2

- **Submissão no SIGAA em 18/11.** Artigo de quatro páginas no formato IEEE. [Artigo_A2_IEEE.pdf](paper/a2_ieee_2026_11_07/output/pdf/Artigo_A2_IEEE.pdf)
- **Apresentação oral.** 22 slides, todos apresentados, no modelo institucional usado na A1. O roteiro ampliado tem 1.889 palavras e estima 14 min 46 s a 135 palavras/min, incluindo transições; confirmar em ensaio com os quatro integrantes. [PPTX editável](presentation/a2_inf/output/Apresentacao_A2_INF.pptx) · [PDF dos slides](presentation/a2_inf/output/Apresentacao_A2_INF.pdf) · [Roteiro e arguição](presentation/a2_inf/output/Roteiro_A2_INF.md) · [Guia de estudo e defesa](presentation/a2_inf/output/Guia_Defesa_A2.md)
- [Auditoria das 21 variáveis](docs/a2/auditoria_2026_11_07/Parecer_Semantico_e_Decisoes.md), [verificação experimental](docs/a2/auditoria_2026_11_07/Verificacao_Experimental.json) e [conferência da rubrica da entrega](docs/a2/Revisao_Final_A2.md#conferência-da-rubrica).
- As contribuições do Antônio e do João (Petas) foram incorporadas seletivamente em [c99f812](https://github.com/pedroafm06/Data-Mining/commit/c99f812). [Parecer por contribuição](docs/a2/Revisao_Final_A2.md)
- [Código e instruções de reprodução da A2](#reproduzir-a-revisão-da-a2).

### Resultados da revisão final

A comparação usa 9.361 registros, 105 configurações por cenário e validação aninhada com cinco folds externos e três internos. O agrupamento une cópias brutas exatas às equivalências anteriores, sem comparar ID ou rótulo. As tabelas e os intervalos pareados da A2 estão nos [resultados da revisão final](resultados/a2/revisao_final_2026_11_16/).

| Cenário | Papel | Entradas | Maior BA observada |
|---|---|---|---|
| FISIO8 | Principal | Peso, altura, IMC, idade, PAS, PAD, FC e sexo | Floresta · 63,27% |
| STRICT4 | Sensibilidade | Peso, altura, idade e sexo | Árvore · 59,55% |
| CLINICO | Ensaio exploratório | FISIO8 mais PPA, SOPRO, B2, PULSOS e HDA1 | Árvore · 91,92% |

MOTIVO1 e MOTIVO2 ficam fora de todos os modelos. FISIO8 e STRICT4 também retiram os achados diagnósticos de origem ou cronologia incerta. CLINICO mede quanto a pontuação depende desses campos. Sua participação na definição do rótulo segue desconhecida. O teste histórico ficou fora da avaliação final.

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

O programa verifica a versão da fonte pelo SHA-256 e reconstrói a partição histórica a partir das regras e sementes e agrupa cópias exatas no desenvolvimento. O protocolo fixa `random_state=42` nos estimadores estocásticos, 743 nos folds externos, 811 mais o índice do fold nos internos e 43 na seleção final. Dados clínicos, previsões por registro e modelos ajustados ficam em arquivos locais ignorados pelo Git. As [métricas externas](resultados/a2/revisao_final_2026_11_16/family_nested_metrics.csv) e a [síntese dos resultados](resultados/a2/revisao_final_2026_11_16/reviewed_results.json) estão disponíveis no repositório.

O [guia de compilação do artigo](paper/a2_ieee_2026_11_07/README.md) explica como gerar o PDF a partir dos resultados agregados. O [protocolo final](config/a2_final_protocol_2026_11_16.json) identifica os cenários, as sementes e a grade completa.

## Desenvolvimento anterior da A2

- [Auditoria de 7 de novembro com o agrupamento anterior](resultados/a2/auditoria_2026_11_07/).
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
