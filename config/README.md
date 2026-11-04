# Configurações e etapas

- `a2_kdd_protocol.json`: candidatos, critérios e seeds congelados para a busca de classificadores. Sua seção de aplicação registra a demonstração inicial, posteriormente criticada.
- `a2_application_policy.json`: política final de cobertura da aplicação. A revisão foi motivada por padrões de campos vazios nos não rotulados, sem usar seus rótulos desconhecidos ou escolher por métricas de teste. Os classificadores congelados não mudaram.
- `a2_preprocessing_policy.json`: hipóteses de qualidade e diagnóstico preliminar de imputação da preparação. Global/idade voltam a competir nos treinos de CV da modelagem.
- `a2_effective_estimator_parameters.json`: inclui os parâmetros efetivos da biblioteca, inclusive defaults não variados, para não esconder configurações implícitas. A busca testa somente os eixos publicados; não afirma otimização de todo parâmetro possível.
- `particoes_referencia.csv`: IDs e grupos candidatos da separação histórica, sem medidas clínicas.
- `fontes_didaticas_verificadas.json`: hashes dos materiais da disciplina consultados localmente; os PDFs de terceiros não são redistribuídos.

`protocolo_experimental.json`, `reproducibility_reference.json` e `historico/` pertencem aos experimentos anteriores, separados dos resultados atuais. `schema.json` registra o esquema da base. O código com validação de nomes/ordem é a referência operacional do parser.
