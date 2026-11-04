# A2: estado do processo completo e verificação

A A2 aproveita e melhora a A1 e reúne o KDD inteiro. Entendimento, seleção, limpeza, transformação, mineração, avaliação, interpretação e aplicação/documentação foram executados. A A1 avaliada permanece sendo a versão entregue, preservada sem alteração de bytes.

## Evidências

- Fonte com 12.873 linhas e 21 variáveis preservada pelo SHA-256 esperado. Bases e três representações aplicadas continuam disponíveis localmente.
- Busca atual: 81 configurações por cenário, em três cenários com a mesma população e partições. São 9.361 registros de desenvolvimento e 2.342 no teste histórico, além de uma quarentena e 1.169 sem alvo.
- CV de cinco folds e avaliação aninhada3x3 no desenvolvimento. Auditoria de252 ajustes internos de imputação, vocabulário e escala, com hashes dos membros e parâmetros aprendidos. Nenhum grupo candidato atravessa ajuste e teste; identidade real de pacientes continua desconhecida.
- Todas as escolhas de classificadores foram congeladas antes das métricas do teste histórico. O teste já tinha passado por exploração, e esse limite não é escondido pela validação aninhada.
- Modelos salvos reaplicados: classes e matrizes de confusão idênticas; diferença máxima dos scores até2,23e-16 na comparação com CSV, dentro da tolerância1e-12.
- 111 testes passaram na conferência integral mais recente. Exemplos pequenos verificam regras e não contaminação; testes locais conferem os artefatos reais e a composição dos folds.
- Notebook completo: cinco células de código executadas, zero erros, sem caminhos pessoais nas células ou saídas. O notebook da preparação é um componente separado.
- Relatório integrado: sete páginas A4, pt-BR, com tabelas e gráficos renderizados e inspecionados. Decisões transversais, julgamento das21 variáveis, 81 configurações e valores aprendidos ficam no registro detalhado e nos agregados.

## Crítica e alternativas

O ganho de reconstrução por idade não garantiu melhor classificação. A imputação entrou na busca dentro dos folds. Redução de atributos, indicadores, preservação de suspeitos, PCA e balanceamento foram testados; ganhos pequenos são tratados como exploratórios. As primeiras hipóteses não foram declaradas ótimas por preferência.

A aplicação inicial que exigia apenas um campo gerava scores para muitos padrões de ausência sem suporte. Ela foi rejeitada. A política final exige padrão de disponibilidade com pelo menos30 exemplos de desenvolvimento e categorias conhecidas; coberturas1/10/30 foram comparadas sem rótulos novos. A aplicação revisada mantém19 scores em A,380 em B e294 em B_contexto; os demais registros recebem abstenção. Cobertura aceita não valida a previsão individual.

## Distribuição e limites

O repositório contém código, documentação, notebook, métricas e parâmetros agregados. A referência histórica de partições tem apenas IDs/grupos, sem medidas clínicas. Base, proveniência por linha, matrizes, predições e modelos serializados permanecem locais.

O processo acadêmico foi completado; não houve submissão no SIGAA ou implantação clínica. A descrição formal posterior da A2 poderá acrescentar exigências de entrega/apresentação. Formação do alvo, unidade paciente/atendimento, cronologia e validade em novos dados continuam sendo limites de evidência, sem serem confundidos com etapas técnicas não executadas.
