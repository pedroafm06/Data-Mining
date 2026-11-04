> HISTÓRICO: execução exploratória anterior à revisão atual do pré-processamento da A2. Os números abaixo pertencem à preparação antiga e não são resultados da base atual. Referências a arquivos descrevem o acervo local anterior.

# Protocolo experimental congelado antes da modelagem

Versão 2026-11-04-v1; snapshot conferido contra os parâmetros fixos da implementação em `config/protocolo_experimental.json`. Alvo registrado Anormal=1. A base inteira já foi explorada na A1; o teste é reservado a partir deste protocolo, não virgem de exploração.

A inclui achados e contexto; B inclui somente sete medidas e SEXO; B_contexto é ablação com contexto de temporalidade não confirmada. Mesmos IDs, y e partições nos três cenários. Identificadores, datas, flags e metadados não são preditores. Não interpretar nenhum cenário como dispositivo clínico validado.

Reservar fold0 de StratifiedGroupKFold(5, shuffle=True, random_state=42), aproximadamente20%, como teste. Os grupos são equivalências candidatas de atributos, não identidade comprovada de paciente. Cinco folds internos(seed43) no desenvolvimento. A população inclui todos os alvos conhecidos; idade desconhecida é imputada dentro do treino.

Selecionar por média da balancedaccuracy interna; empate segue ordem de candidatos, mais simples primeiro. Orçamento: Dummy majoritário, quatro regressões logísticas(C=.1/1, peso de classe nenhum/balanced), quatro árvores(profundidade3/6, folha mínima20/50), floresta150árvores(profundidade8, folha mínima10, até2cores). Todas as transformações são ajustadas dentro de cada fold. Limiar0.5 fixo; nenhuma meta clínica foi inventada.

Congelar os três vencedores antes da primeira métrica de teste. Teste avaliado uma vez por vencedor de cenário e controles fixos(Dummy e regra de sopro), sem tuning. Sensibilidades qualitativas e de representação usam somente desenvolvimento. Relatar todos os candidatos, folds e previsões fora do ajuste; dispersão entre folds não é IC.

Métricas: matriz de confusão com contagens, recall, especificidade, precisão, F1, balancedaccuracy, ROC-AUC, average precision(AP, distinta de integração trapezoidal PR-AUC), Brier e prevalência. ICs percentis por bootstrap de grupos candidatos condicionados ao modelo ajustado; não abrangem incerteza da seleção nem identidade de paciente desconhecida. Relatar falhas/ausências de classe nos reamostrados.

Avaliação temporal secundária usa a hipótese histórica2003–2010, corte pré-fixado2009-01-01; grupos que cruzam o corte são retirados do treino temporal. Reutilizar candidato escolhido no CV principal sem novo tuning. Esse CV usa o desenvolvimento global, incluindo datas posteriores ao corte; portanto a seleção de hiperparâmetros não é puramente prospectiva. Cronologia é hipotética; o ajuste temporal não é validação clínica externa nem independente de todas as escolhas anteriores.

Interpretação: importância por permutação de colunas originais em partição de desenvolvimento não usada no ajuste desse modelo de interpretação; seleção prévia usou CV, logo interpretação é exploratória e pós-seleção. Coeficientes/importâncias do modelo ajustado são descritivos. Subgrupos por sexo, idade, quantidade de ausências e sopro, com suporte; cortes não são usados para ajustar o modelo. Nenhuma associação será chamada causal.
