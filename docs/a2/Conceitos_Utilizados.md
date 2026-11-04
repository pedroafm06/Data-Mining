# Conceitos utilizados na preparação da A2

A escolha de uma técnica depende do problema que ela resolve. A revisão não aplica todas as técnicas disponíveis: cada transformação precisa preservar o significado dos atributos e ter uma finalidade demonstrável.

| Conceito | Decisão aplicada e motivo |
|---|---|
| Processo KDD | Separar seleção e entendimento, limpeza, transformação, mineração, avaliação e interpretação. A revisão atual conclui a preparação; a modelagem com essa versão ainda falta. |
| Tipos, escalas e unidades | ID é identificador nominal; medidas têm unidades explícitas; códigos de achados não viram quantidades; datas mantêm seus estados e candidatos. Isso evita operações aritméticas sem significado. |
| Análise univariada | Contagens, faltantes, quartis, média, mediana, desvio, amplitude e assimetria descrevem as medidas observadas antes de imputar. Estimativas não são apresentadas como medições. |
| Ausência e sentinelas | Zeros usados como sentinela e erros de planilha são tratados conforme a variável. SOPRO Ausente é achado registrado e permanece distinto de campo vazio. |
| Inconsistência léxica | Padronizar grafias e converter formatos completos, preservando os originais; não juntar descrições diferentes de MOTIVO2 por terem o mesmo prefixo. |
| Inconsistência de domínio, lógica e temporal | Rejeitar casos demonstráveis, como medida negativa, e sinalizar hipóteses de qualidade. PAS≤PAD é uma contradição relacional; sem saber o campo errado, a política mascara o par. Datas ambíguas não recebem século por conveniência. |
| Valores atípicos | Um extremo pode ser real. Envelopes históricos geram alertas; o bloqueio operacional conjunto não é faixa de normalidade clínica. Alternativas preservam suspeitas para comparação. |
| Objetos repetidos e duplicação | Todas as linhas são mantidas. Igualdade de atributos é equivalência candidata, não prova de identidade. Um candidato que cruza desenvolvimento/teste é retirado somente do ajuste, conservando o teste histórico. |
| Criação de atributos | Idade relativa deriva de pares de datas compatíveis sob hipótese pediátrica; IMC deriva de peso e altura observados utilizáveis. Intervalo, hipótese e origem são registrados. |
| Imputação por mediana | Comparar mediana global, por idade e por idade/sexo somente no desenvolvimento. Usar grupo etário para Peso, Altura, FC e IMC; global para IDADE, PAS e PAD. Grupos precisam de 30 observados e têm fallback global. |
| Discretização | Faixas fixas de idade condicionam as medianas. A idade permanece contínua na matriz; idade imputada não forma seu próprio grupo. |
| Indicadores de ausência | Sete indicadores binários distinguem valores imputados de medidas disponíveis, sem afirmar que toda ausência tenha o mesmo motivo. |
| One-hot encoding | Categorias nominais, ausência e categoria inédita recebem indicadores distintos, sem criar ordem. Vocabulários são aprendidos só no desenvolvimento. |
| Padronização Z-score | Aplicada somente às medidas contínuas em uma representação separada, com média/desvio do desenvolvimento. Indicadores e one-hot permanecem 0/1. |
| Transformação logarítmica | Uma alternativa aplica log1p apenas ao Peso antes de padronizar. Assimetria, suporte e significado orientam a escolha; log não é aplicado indiscriminadamente. |
| Redução manual de atributos | ID, datas e convênio ficam fora de X principal. A alternativa reduzida também retira IMC e HDA2; a visão completa permanece disponível. |
| Correlação e análise bivariada | Pearson, Spearman, contingências e comparação das distribuições descrevem associações. Aumentar correlação não é objetivo da limpeza, e associação não demonstra causa. |
| Separação desenvolvimento/teste e vazamento | Medianas, vocabulários e escalas são aprendidos no desenvolvimento e aplicados aos demais registros. O alvo não escolhe a transformação. Na futura validação cruzada, todo ajuste precisa ser repetido dentro de cada fold. |
| Codificação do alvo | Normal=0 e Anormal=1; rótulos ausentes/duvidosos não são imputados e ficam fora dos experimentos supervisionados. ID e y são arquivos auxiliares separados de X. |

O mascaramento artificial de 20% das medidas disponíveis, repetido cinco vezes, é um diagnóstico adicional de reconstrução: ele não identifica o mecanismo das ausências reais. O critério exigiu pelo menos 10% de redução de erro absoluto médio e melhora em ao menos quatro repetições para adotar a imputação por idade nas variáveis elegíveis. O ganho do IMC ficou perto do limite (10,26%); a alternativa global também foi aplicada.

Welch e V de Cramér são complementos estatísticos explicitados. Eles ajudam a descrever diferenças e associações, sem substituir o raciocínio sobre qualidade, suporte, tamanho do efeito e construção do alvo. Testes em milhares de registros podem produzir p-valores pequenos para diferenças pouco relevantes.

Min-Max, PCA, seleção automática, outros encodings e reamostragem de classes não foram acrescentados para acumular técnicas. Sua utilidade deverá ser examinada na modelagem conforme a tarefa e o protocolo. Os conceitos de validação cruzada, controle de complexidade, matriz de confusão, precisão, recall e curvas de avaliação pertencem à continuação; resultados antigos estão identificados no histórico.
