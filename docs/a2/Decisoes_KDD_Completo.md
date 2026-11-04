# A2 - decisões do processo completo do KDD

Este registro cobre entendimento, seleção, limpeza, transformação, mineração, avaliação, interpretação e aplicação. A A1 entregue permanece como histórico avaliado. A unidade é a linha recebida; não foi comprovado se cada ID representa uma pessoa ou um atendimento independente.

Uma decisão aqui pode ser uma regra determinística, um critério de comparação ou um parâmetro aprendido. Regras e alternativas são explicadas abaixo. Os valores aprendidos não ficam escondidos: medianas por faixa, vocabulários, médias/desvios e hashes do ajuste de cada fold estão em `resultados/a2/kdd_completo/fold_preprocessing_audit.json`; os parâmetros finais de cada cenário estão nos arquivos `final_parameters_*.json`. As alterações por célula permanecem locais em `artifacts/a2_preprocessing/alteracoes.csv` e na proveniência, para evitar distribuir registros clínicos.

## Decisões transversais, com alternativas e limites

### Objetivo: Tarefa

A regra aplicada foi **Classificação supervisionada do rótulo registrado**. O alvo disponível é binário; descobrir padrões associados ao registro, sem fabricar um desfecho clínico independente.

Alternativa examinada ou rejeitada: Regressão, agrupamento e associação não respondem diretamente à pergunta principal. Evidência: Rótulos Normal/Anormal na fonte. Limite: Não equivale a diagnóstico nem causalidade.

### Seleção: Unidade e população

A regra aplicada foi **Preservar 12.873 linhas; supervisionado só com rótulo conhecido**. A informação não estabelece identidade de paciente. Não eliminar coincidências como se fossem duplicações comprovadas.

Alternativa examinada ou rejeitada: Excluir repetidos ou imputar y foi rejeitado. Evidência: Base semântica e elegibilidade. Limite: Paciente versus atendimento ainda precisa de confirmação.

### Limpeza: Esquema e ID

A regra aplicada foi **21 nomes/ordem exatos; ID não vazio e único**. Um identificador ambíguo impede rastrear qualquer alteração.

Alternativa examinada ou rejeitada: Fabricar ID ou juntar automaticamente foi rejeitado. Evidência: Validação antes da preparação. Limite: ID único não comprova pessoa única.

### Limpeza: Texto

A regra aplicada foi **Unicode NFC, espaços condensados; chave sem acento e casefold**. Unificar apenas variações gráficas, preservando significado e texto original na auditoria.

Alternativa examinada ou rejeitada: Fusão por prefixo de motivo foi rejeitada. Evidência: Mapas explícitos e logs de alterações. Limite: Categorias novas clínicas são mantidas e sinalizadas.

### Limpeza: Sentinelas

A regra aplicada foi **Vazio; PPA não calculado/#VALUE!; DN ???; SEXO indeterminado**. Ausência é diferente de normalidade ou de categoria clínica Ausente.

Alternativa examinada ou rejeitada: Moda Normal/Ausente foi rejeitada. Evidência: Sentinelas específicas por coluna. Limite: Não identifica o mecanismo das ausências.

### Limpeza: Número

A regra aplicada foi **Vírgula decimal aceita; não finito, negativo e medida FC/PA zero invalidados; Peso/Altura/IMC zero ausentes**. Os significados diferem por variável; idade zero é válida.

Alternativa examinada ou rejeitada: Cortar dígitos ou mover vírgula para fazer o valor parecer plausível foi rejeitado. Evidência: numeric_value e log por célula. Limite: Extremo positivo não é automaticamente erro.

### Limpeza: Intervalo FC

A regra aplicada foi **Faixa válida de dois valores com 2-3 dígitos -> ponto médio; invertida -> inválida**. É a aproximação simples explicitada, não uma leitura exata.

Alternativa examinada ou rejeitada: Inverter limites silenciosamente foi rejeitado. Evidência: Flag de aproximação e registro bruto. Limite: A variabilidade dentro da faixa não é recuperável.

### Limpeza: Data

A regra aplicada foi **Data completa válida, nome de mês ou serial Excel com 5 dígitos; dia/mês brasileiro; século curto gera 19xx/20xx**. Evitar janela histórica como confirmação do século. Formato precisa corresponder à célula inteira.

Alternativa examinada ou rejeitada: Correção por palpite e descarte de texto residual foram rejeitados. Evidência: parse_date e candidatos locais. Limite: Data absoluta ambígua continua indisponível.

### Criação: Idade relativa

A regra aplicada foi **0 <= idade calendário <20; candidatos com duração divergente em até 1 dia; média e intervalo preservados**. Permite identificar diferença etária sem fixar o século. Tolerância absorve um dia bissexto.

Alternativa examinada ou rejeitada: Dias/352 e imputação pelo corpo foram rejeitados. Evidência: 11.208 resolvidas; hipótese pediátrica declarada. Limite: Não prova a cronologia absoluta.

### Criação: Aniversário bissexto

A regra aplicada foi **29/02 -> 28/02 em ano não bissexto**. Definir uma convenção explícita para fração do ano e fronteira de 20 anos.

Alternativa examinada ou rejeitada: 01/03 é alternativa possível; não misturar convenções. Evidência: Teste de fronteira calendário. Limite: Diferenças locais de um dia não são informação clínica precisa.

### Criação: Fallback de idade

A regra aplicada foi **Idade literal na DN; depois valor original válido <20; depois ausência**. Não preencher uma data ou idade não identificável com certeza falsa.

Alternativa examinada ou rejeitada: Inferir pela antropometria foi rejeitado. Evidência: 18 literais e 1.647 indisponíveis; origem guardada. Limite: Fallback numérico, quando houver, é não verificado.

### Limpeza: Alertas etários

A regra aplicada foi **Diferença >0,1 ano; conflito >1 ano**. São alertas de revisão, não critérios de exclusão automática.

Alternativa examinada ou rejeitada: Excluir idade por baixa correlação foi rejeitado. Evidência: Flags e proveniência. Limite: Pontos de corte operacionais.

### Limpeza: Antropometria

A regra aplicada foi **Guarda conjunta IMC observado fora de 5-100 mascara Peso/Altura/IMC na política; sem atribuir culpado**. Valores individualmente possíveis podem formar um conjunto muito suspeito. A base semântica mantém tudo.

Alternativa examinada ou rejeitada: Corrigir um pai arbitrariamente e apagar idade foram rejeitados. Evidência: Máscaras atuais e sensibilidade suspeitos preservados. Limite: 5-100 não é faixa clínica de normalidade.

### Limpeza: Exceções e máscaras

A regra aplicada foi **Peso<1; altura fora40-200, exceto30-39 se idade<0,25 ou desconhecida; FC>500; PAS envelope50-200; PAD positiva mantida; PAS<=PAD mascara par**. Preservar extremos potencialmente reais e explicitar hipóteses restantes. Peso>150 e FC>220 não são excluídos por esses antigos tetos.

Alternativa examinada ou rejeitada: Política histórica e todos suspeitos preservados estão disponíveis. Evidência: Peso16; Altura18; IMC14; PAS3; PAD1; FC8 mascarados. Limite: São hipóteses de confiabilidade, sem validação clínica individual.

### Criação: IMC

A regra aplicada foi **Peso/(Altura/100)^2 somente com pais observados operacionalmente utilizáveis; histórico como fallback**. Evitar transformar pais imputados em uma medição de IMC.

Alternativa examinada ou rejeitada: Reconstrução após imputar pais foi testada e teve erro maior. Evidência: Ensaios de coerência e origem por linha. Limite: IMC é derivado e redundante; visão sem IMC testada.

### Transformação: Faixas e suporte

A regra aplicada foi **[0;0,25;0,5;1;2;5;10;15;20); mínimo30 por grupo; fallback global**. Capturar crescimento sem grupos muito pequenos. Usar idade disponível antes da imputação.

Alternativa examinada ou rejeitada: Mediana global e idade/sexo foram comparadas. Evidência: Diagnóstico com 20% mascarado, 5 repetições, seeds194-198. Limite: Faixas não foram otimizadas clinicamente.

### Transformação: Escolha preliminar por reconstrução

A regra aplicada foi **Ganho MAE>=10% e melhora em pelo menos4/5 repetições**. Evitar complexidade por ganho mínimo; IMC limítrofe fica explicitado.

Alternativa examinada ou rejeitada: Global sempre exportada; idade/sexo sem ganho suficiente. Evidência: Diagnósticos de preparação. Limite: Para modelos, global/idade são escolhidas dentro da CV, sem herdar a decisão global.

### Transformação: One-hot

A regra aplicada foi **Vocabulário do treino + __AUSENTE__ + __DESCONHECIDO__; exatamente1 por variável**. Nominal não deve ganhar ordem artificial; ausência e categoria inédita são diferentes.

Alternativa examinada ou rejeitada: Ordinal de PPA e binarização dos achados foram rejeitados. Evidência: Testes e metadados por fold. Limite: Dimensão pode variar entre folds; cada modelo usa seu próprio vocabulário.

### Transformação: Escala e log

A regra aplicada foi **Z=(x-media_treino)/DP_treino com ddof0; escala1 se desvio0; log1p só Peso em alternativa logística**. Escalas afetam regularização; árvores usam unidades por interpretabilidade. Bits não são escalados.

Alternativa examinada ou rejeitada: Log indiscriminado, min-max e escala da base inteira foram rejeitados. Evidência: Unidades/standard/log_weight_standard efetivamente comparados. Limite: Z-score não torna normal nem robusta uma medida.

### Validação: Grupos

A regra aplicada foi **União transitiva de grupos candidatos antigos + igualdade informativa atual (>=8 campos)**. Evitar equivalentes atravessando treino/validação mesmo após novas regras.

Alternativa examinada ou rejeitada: Partição aleatória por linha pode compartilhar candidatos. Evidência: Grupos sem interseção; quarentena antes do ajuste. Limite: Não resolve identidade de paciente desconhecida.

### Validação: Separação

A regra aplicada foi **Teste histórico preservado; 5 folds internos seed 43; nested3x3 seeds 52 e 53+fold**. Selecionar dentro de treino e avaliar também o procedimento de escolha. Mesma população/partição nos cenários.

Alternativa examinada ou rejeitada: Usar matriz pronta em CV foi rejeitado. Evidência: Auditoria de hashes de IDs e parâmetros por fold. Limite: Qualidade já foi explorada globalmente; nested não desfaz isso.

### Seleção de modelos: Critério e desempate

A regra aplicada foi **Maior média de acurácia balanceada; empate1e-12 na ordem publicada**. Sem custos confirmados FP/FN, dar peso igual ao recall de ambas classes; ordem resolve empate reprodutivelmente.

Alternativa examinada ou rejeitada: Acurácia isolada e escolha pelo teste foram rejeitadas. Evidência: 81 configurações por cenário, publicadas antes de métricas. Limite: Não é uma utilidade clínica estabelecida nem ótimo global.

### Modelagem: Árvores

A regra aplicada foi **Gini/entropia; profundidade3/6 ou poda alfa0,001/0,005; folhas20/50; pesos None/balanced**. Controlar complexidade, suporte e sobreajuste, sem tratar cada registro como regra.

Alternativa examinada ou rejeitada: Árvore irrestrita sem suporte mínimo foi rejeitada. Evidência: 40 combinações com as duas imputações. Limite: Cortes do modelo são empíricos, não normas clínicas.

### Modelagem: Logística

A regra aplicada foi **C=0,01/0,1/1/10; pesos None/balanced; standard/log-Peso; global/idade; max_iter5000**. Testar quatro ordens de regularização e uma fronteira linear; log reduz influência da cauda do peso.

Alternativa examinada ou rejeitada: Família adicional para comparação com árvores. Evidência: 32 combinações; falha de convergência é erro, não resultado aceito. Limite: Complemento técnico; não atribuir explicação integral do método às aulas.

### Modelagem: Floresta

A regra aplicada foi **150 árvores; profundidade 8/None; folha10; pesos None/balanced; imputação global/idade; seed42; n_jobs2**. Testar agregação de árvores e reduzir variância com orçamento fixo. Folhas limitam a árvore profunda.

Alternativa examinada ou rejeitada: Mais árvores sem orçamento e tuning pelo teste foram rejeitados. Evidência: 8 combinações; parâmetros efetivos registrados. Limite: É comparação complementar, sem garantia de melhor generalização.

### Sensibilidade: Redução e balanceamento

A regra aplicada foi **Sem indicadores/IMC/HDA2/IMC+HDA2/PPA; PCA95 na melhor logística; sobre/subamostragem simples seed45**. Investigar redundância, ausências, informação rara e balanceamento; medir perdas e ganhos.

Alternativa examinada ou rejeitada: SMOTE em one-hot pode produzir categorias e combinações clínicas artificiais; não foi forçado. Evidência: Somente desenvolvimento; mesmas partições. Limite: Pós-seleção exploratória; não reutiliza teste para escolher a variante.

### Avaliação: Limiar e métricas

A regra aplicada foi **p>=0,5; TN/FP/FN/TP; precisão, recall, especificidade, F1, BA, ROC-AUC, AP e Brier**. Exibir os tipos de erro; AP resume PR por definição própria, sem chamar de área trapezoidal.

Alternativa examinada ou rejeitada: Tuning de limiar por teste foi rejeitado. Evidência: Métricas e curvas atuais. Limite: Scores não são probabilidades clínicas calibradas.

### Avaliação: Intervalos e subgrupos

A regra aplicada foi **500 reamostragens de componentes seed44; Wilson em recall de subgrupos n>=20**. Mostrar incerteza e suporte; agrupar dependências candidatas em vez de tratar tudo como independente.

Alternativa examinada ou rejeitada: DP entre folds não é IC. Evidência: Intervalos e suportes publicados. Limite: Bootstrap condicionado ao modelo; Wilson por linha não corrige grupos.

### Interpretação: Importância e regras

A regra aplicada foi **Permutação5 repetições seed46 em validação de desenvolvimento; regras da melhor árvore com contagens reais**. Investigar dependência do modelo sem confundir peso de classe com número observado no nó.

Alternativa examinada ou rejeitada: Importância como causa ou regra clínica foi rejeitada. Evidência: Queda de BA e suportes por folha. Limite: Pós-seleção; atributos correlacionados podem dividir importância.

### Uso: Aplicação e abstenção

A regra aplicada foi **Exigir ao menos1 preditor, padrão de disponibilidade com >=30 exemplos no desenvolvimento e nenhuma categoria inédita; manter score separado de y**. Demonstra a aplicação do conhecimento sem produzir rótulos confirmados ou treinar com autorrotulagem.

Alternativa examinada ou rejeitada: A regra inicial de apenas1 campo foi testada e rejeitada; suportes 1/10/30 foram comparados sem rótulos novos. Evidência: Contagens agregadas e arquivo local por registro. Limite: 30 é suporte operacional, sem ótimo clínico; cobertura aceita também não garante previsão confiável.

### Reprodução: Versões e proteção

A regra aplicada foi **Entrada verificada por SHA; A1 preservada por hash; parâmetros, seeds e saídas registrados**. Permitir conferir que números decorrem do código e dos mesmos dados.

Alternativa examinada ou rejeitada: Alterar A1 entregue ou publicar dados clínicos por linha foi rejeitado. Evidência: Testes, manifestos e reprodução do modelo salvo. Limite: Validação técnica não é avaliação humana ou clínica.

## Julgamento das 21 variáveis

### ID

**Tipo:** Identificador nominal.

**Limpeza:** Preservar para rastreio; retirar de X.

**Transformação:** Não deduplicar pessoas por coincidência de atributos.

**Alternativas e julgamento:** Ordinal/OHE do ID permitiria memorizar identidade; apagar o ID impediria auditoria.

**Limite:** Unicidade não esclarece paciente versus atendimento.

**Evidência desta versão:** 12873 disponíveis antes de imputar; 0 ausentes/invalidado/mascarados (0.00%); 12873 valores distintos.

### Peso

**Tipo:** Quantitativa, kg.

**Limpeza:** Invalidar não numérico/negativo; zero é sentinela; marcar extremos.

**Transformação:** Na matriz: mediana por faixa etária com mínimo de 30 observados e fallback global. Indicador 0/1; Z-score somente na representação reescalada. Log1p apenas na alternativa Log-Peso.

**Alternativas e julgamento:** Mediana global mistura lactentes e adolescentes. Sexo acrescenta pouco. Log só nesta coluna, em alternativa separada.

**Limite:** Imputação estima, não mede; envelope histórico é hipótese de qualidade.

**Evidência desta versão:** 9929 disponíveis antes de imputar; 2944 ausentes/invalidado/mascarados (22.87%); 622 valores distintos.

### Altura

**Tipo:** Quantitativa, cm.

**Limpeza:** Zero vira ausência; preservar original e sinalizar extremos sem apagar idade.

**Transformação:** Na matriz: mediana por faixa etária com mínimo de 30 observados e fallback global. Indicador 0/1; Z-score somente na representação reescalada.

**Alternativas e julgamento:** Mediana geral perde estrutura etária. Não alterar para elevar correlação.

**Limite:** Não distinguir comprimento/estatura sem informação da fonte.

**Evidência desta versão:** 8395 disponíveis antes de imputar; 4478 ausentes/invalidado/mascarados (34.79%); 154 valores distintos.

### IMC

**Tipo:** Quantitativa, kg/m².

**Limpeza:** Calcular só com peso/altura observados utilizáveis; conservar histórico com origem.

**Transformação:** Na matriz: mediana por faixa etária com mínimo de 30 observados e fallback global. Indicador 0/1; Z-score somente na representação reescalada. Não recalcular após imputar peso ou altura; resultado estimado não é medição clínica.

**Alternativas e julgamento:** Não recalcular após imputar pais: o ensaio de reconstrução mostrou perda maior.

**Limite:** Triplas contendo imputação não são medições fisicamente verificadas.

**Evidência desta versão:** 8023 disponíveis antes de imputar; 4850 ausentes/invalidado/mascarados (37.68%); 3488 valores distintos.

### Atendimento

**Tipo:** Data.

**Limpeza:** Preservar texto, candidatos, estado e data absoluta quando inequívoca.

**Transformação:** Fora de X; usar diferença de datas para idade quando defensável.

**Alternativas e julgamento:** Não forçar 19xx/20xx nem substituir data por idade presumida.

**Limite:** Idade relativa pode ser identificável mesmo quando o século absoluto não é.

**Evidência desta versão:** 312 datas absolutas reconhecidas; 12561 sem data absoluta fixada, incluindo séculos ambíguos. Isso não significa campo vazio: há 983 vazios literais na origem. Datas/candidatos brutos permanecem na proveniência.

### DN

**Tipo:** Data.

**Limpeza:** Reconhecer formatos completos; não descartar texto residual para fabricar data.

**Transformação:** Derivação de idade relativa, mantendo candidatos e proveniência; fora de X.

**Alternativas e julgamento:** Não imputar nascimento nem corrigir século automaticamente.

**Limite:** O recorte pediátrico é uma hipótese explícita ao filtrar pares candidatos.

**Evidência desta versão:** 132 datas absolutas reconhecidas; 12741 sem data absoluta fixada, incluindo séculos ambíguos. Isso não significa campo vazio: há 1376 vazios literais na origem. Datas/candidatos brutos permanecem na proveniência.

### IDADE

**Tipo:** Quantitativa, anos.

**Limpeza:** Guardar valor bruto inclusive negativo; priorizar idade relativa coerente com as datas.

**Transformação:** Na matriz: mediana global do desenvolvimento. Indicador 0/1; Z-score somente na representação reescalada.

**Alternativas e julgamento:** Evidência dias/352 invalida tratar a coluna recebida como idade cronológica correta. Não imputar pelo corpo e criar circularidade.

**Limite:** Datas ambíguas continuam ambíguas. Idade original só como fallback identificado; faixas para imputação não usam idade já imputada.

**Evidência desta versão:** 11226 disponíveis antes de imputar; 1647 ausentes/invalidado/mascarados (12.79%); 5838 valores distintos.

### Convenio

**Tipo:** Nominal administrativa.

**Limpeza:** Normalizar grafia sem adivinhar operadora; preservar na base semântica.

**Transformação:** Fora da matriz principal por finalidade e alta cardinalidade.

**Alternativas e julgamento:** OHE de centenas de grafias aumenta dimensão; frequência/target encoding não têm necessidade demonstrada.

**Limite:** Pode refletir seleção institucional; não é variável clínica intrínseca.

**Evidência desta versão:** 8765 disponíveis antes de imputar; 4108 ausentes/invalidado/mascarados (31.91%); 257 valores distintos.

### PULSOS

**Tipo:** Nominal.

**Limpeza:** Preservar achados raros; normalizar somente grafias equivalentes.

**Transformação:** OHE com ausência e categoria inédita explícitas.

**Alternativas e julgamento:** Moda Normais inventaria exame; binarizar todos os achados perderia tipo.

**Limite:** Momento de coleta e relação com alvo ainda precisam de esclarecimento.

**Evidência desta versão:** 11679 disponíveis antes de imputar; 1194 ausentes/invalidado/mascarados (9.28%); 5 valores distintos.

### PA SISTOLICA

**Tipo:** Quantitativa, mmHg.

**Limpeza:** Sinalizar extremos e PAS≤PAD; mascarar ambos nessa política sem escolher o culpado.

**Transformação:** Na matriz: mediana global do desenvolvimento. Indicador 0/1; Z-score somente na representação reescalada.

**Alternativas e julgamento:** Não converter tudo para PPA nem derivar diagnóstico a partir de pressão imputada.

**Limite:** Mais de metade da medida está ausente; máscara artificial não valida ausência real.

**Evidência desta versão:** 5140 disponíveis antes de imputar; 7733 ausentes/invalidado/mascarados (60.07%); 42 valores distintos.

### PA DIASTOLICA

**Tipo:** Quantitativa, mmHg.

**Limpeza:** Mesma política relacional; conservar original e motivo da intervenção.

**Transformação:** Na matriz: mediana global do desenvolvimento. Indicador 0/1; Z-score somente na representação reescalada.

**Alternativas e julgamento:** Não inferir PAD por uma função arbitrária de PAS; estratificação precisa justificar o custo.

**Limite:** Mesmas ressalvas de cobertura e interpretação de PAS.

**Evidência desta versão:** 5132 disponíveis antes de imputar; 7741 ausentes/invalidado/mascarados (60.13%); 30 valores distintos.

### PPA

**Tipo:** Nominal composta histórica.

**Limpeza:** Sentinelas Não calculado/erro de planilha viram ausentes; histórico é preservado.

**Transformação:** OHE do rótulo completo, sem preencher Normal.

**Alternativas e julgamento:** Ordinal puro confundiria gravidade e componente PAS/PAD. Recalcular exigiria insumos externos integralmente verificados.

**Limite:** Não declarar diagnóstico de HAS reconstruído com dados imputados.

**Evidência desta versão:** 2079 disponíveis antes de imputar; 10794 ausentes/invalidado/mascarados (83.85%); 7 valores distintos.

### NORMAL X ANORMAL

**Tipo:** Alvo binário.

**Limpeza:** Normal/Anormal documentados; Normais permanece em revisão; não imputar.

**Transformação:** y separado: Normal=0, Anormal=1; ausente continua desconhecido.

**Alternativas e julgamento:** Alvo nunca entra em X nem orienta escolha de transformações nesta preparação da A2.

**Limite:** Produção do rótulo precisa ser esclarecida; não confundir com diagnóstico independente.

**Evidência desta versão:** 11704 disponíveis antes de imputar; 1169 ausentes/invalidado/mascarados (9.08%); 2 valores distintos.

### B2

**Tipo:** Nominal.

**Limpeza:** Preservar categorias e raros, sem impor gravidade artificial.

**Transformação:** OHE com falta de registro distinta de Normal.

**Alternativas e julgamento:** Moda e descarte por predominância apagariam achados raros.

**Limite:** Pode integrar o processo que gerou o alvo.

**Evidência desta versão:** 11695 disponíveis antes de imputar; 1178 ausentes/invalidado/mascarados (9.15%); 5 valores distintos.

### SOPRO

**Tipo:** Nominal.

**Limpeza:** Ausente é categoria observada; valor não registrado é outra coisa.

**Transformação:** OHE dos tipos, não apenas presença.

**Alternativas e julgamento:** Preencher faltante com Ausente ou selecionar só sem sopro mudaria o significado/população.

**Limite:** Esta preparação transforma o atributo; a disponibilidade em uso futuro é decisão posterior.

**Evidência desta versão:** 11706 disponíveis antes de imputar; 1167 ausentes/invalidado/mascarados (9.07%); 5 valores distintos.

### FC

**Tipo:** Quantitativa, bpm.

**Limpeza:** Converter intervalo válido em ponto médio aproximado; rejeitar intervalo invertido.

**Transformação:** Na matriz: mediana por faixa etária com mínimo de 30 observados e fallback global. Indicador 0/1; Z-score somente na representação reescalada.

**Alternativas e julgamento:** Mediana geral ignora mudança etária; percentis externos incompletos não serão inventados.

**Limite:** Ponto médio não equivale a leitura exata; contexto da aferição é desconhecido.

**Evidência desta versão:** 10995 disponíveis antes de imputar; 1878 ausentes/invalidado/mascarados (14.59%); 99 valores distintos.

### HDA 1

**Tipo:** Nominal estruturada.

**Limpeza:** Conservar significado e distinguir vazio de Assintomático.

**Transformação:** OHE com categoria ausente explícita.

**Alternativas e julgamento:** Moda criaria histórico clínico; códigos não são quantidades.

**Limite:** Temporalidade em relação ao rótulo desconhecida.

**Evidência desta versão:** 8603 disponíveis antes de imputar; 4270 ausentes/invalidado/mascarados (33.17%); 8 valores distintos.

### HDA2

**Tipo:** Nominal estruturada.

**Limpeza:** Conservar mesmo com cobertura baixa; não copiar de HDA1.

**Transformação:** OHE na matriz completa; retirada em representação reduzida documentada.

**Alternativas e julgamento:** Regra de 50% é heurística; vazio não prova que não existe segundo histórico.

**Limite:** Cobertura muito baixa limita utilidade; não foi escolhida por desempenho.

**Evidência desta versão:** 407 disponíveis antes de imputar; 12466 ausentes/invalidado/mascarados (96.84%); 8 valores distintos.

### SEXO

**Tipo:** Nominal.

**Limpeza:** Mapear grafias M/F documentadas; desconhecido não é sexo inferido.

**Transformação:** OHE com falta/inédito explícitos, sem imputar moda.

**Alternativas e julgamento:** Binário+indicador também é válido, mas OHE mantém simetria e explicação uniforme.

**Limite:** Não inferir sexo pelo corpo nem pelo alvo; estratificar imputação por sexo exige ganho adicional.

**Evidência desta versão:** 11452 disponíveis antes de imputar; 1421 ausentes/invalidado/mascarados (11.04%); 2 valores distintos.

### MOTIVO1

**Tipo:** Nominal.

**Limpeza:** Preservar texto completo normalizado, sem ordenar prefixos.

**Transformação:** OHE; falta explícita e separação do segundo motivo.

**Alternativas e julgamento:** Não fundir com MOTIVO2 ou assumir que todo encaminhamento precede diagnóstico.

**Limite:** Algumas categorias já mencionam cardiopatia estabelecida.

**Evidência desta versão:** 11818 disponíveis antes de imputar; 1055 ausentes/invalidado/mascarados (8.20%); 5 valores distintos.

### MOTIVO2

**Tipo:** Nominal.

**Limpeza:** Prefixos iguais com descrições diferentes não são a mesma categoria.

**Transformação:** OHE da descrição completa; vazio separado de ausência clínica.

**Alternativas e julgamento:** Não mapear só pelo número nem preencher com MOTIVO1.

**Limite:** Disponibilidade temporal precisa de esclarecimento antes da modelagem futura.

**Evidência desta versão:** 9377 disponíveis antes de imputar; 3496 ausentes/invalidado/mascarados (27.16%); 16 valores distintos.

## Por que as representações são separadas

A base semântica preserva unidades, faltantes e suspeitas. As matrizes numéricas são representações aplicadas: unidades originais, Z-score e uma alternativa log1p somente em Peso antes do Z-score. Indicadores e one-hot permanecem 0/1. Z-score não torna a distribuição normal e não é robusto a outliers. Log não é imposto a todas as medidas. Não existe uma transformação universalmente ótima antes de definir a finalidade do modelo.

A política principal revisa os alertas: não elimina peso alto só por ultrapassar 150 kg, preserva baixa estatura potencial de lactente e não apaga FC 300 ou PAD positiva por serem extremas. AHA contempla taquiarritmias infantis com FC ≥220. Suspeitas fortes, como registros de FC >500 na amostra, seguem mascaradas por uma regra operacional explícita, sem declarar um limite físico. A política histórica e a alternativa preservada ficam disponíveis; não há prova clínica de erro individual. A alternativa que conserva suspeitos permite inspecionar o efeito da política. Toda imputação continua marcada. PPA histórica não é reconstruída com pressão imputada. IMC não é recalculado a partir de pais imputados: nos ensaios essa estratégia foi pior que preencher o IMC diretamente.

## Consistência conjunta e as duas formas de retenção

Peso e altura individuais não bastam para validar sua combinação. A regra operacional ampla de IMC entre 5 e 100 serve para sinalizar trios que precisam de revisão; não é intervalo clínico de normalidade. Quando a combinação observada ultrapassa essa regra, peso, altura e IMC são mascarados juntos somente na matriz da política revisada, sem decidir qual campo errou nem alterar idade. A base semântica e a variante preservada mantêm tudo. Um IMC histórico sozinho não contorna a sinalização conjunta. A regra permite valores extremos como 84 quando os pais são operacionalmente utilizáveis; não prova validade clínica individual.

Separadamente, uma equivalência candidata cruzava desenvolvimento e teste: apenas o registro do desenvolvimento foi retirado do ajuste. Ele permanece na base e recebe aplicação do transformador. Não há exclusão de pessoas ou confirmação de identidade por essa operação.

## Limites das comparações

O mascaramento artificial verifica reconstrução de valores disponíveis; não demonstra o mecanismo real das ausências. As faixas de idade são operacionais, com mínimo de medidas por grupo e fallback documentado. Sexo só acrescentaria complexidade se o ganho adicional fosse consistente. Não se usam notas de modelos ou o alvo para decidir imputações.

A matriz de desenvolvimento já transformada não serve para selecionar modelos por CV interna sem reajustar o transformador em cada fold. A população já foi explorada em etapas anteriores e o teste não é inteiramente virgem de exploração. Os experimentos históricos não representam a preparação nova; os resultados atuais foram recalculados e constam do relatório integrado da A2.

## Fontes e uso de IA

Tema, dicionário e descrição das avaliações do SIGAA; conceitos das aulas de dados, exploração, limpeza, transformação, criação e redução. Mediana, codificação, Z-score, log e criação de atributos são conceitos empregados. Mediana condicionada por idade é uma aplicação operacional de imputação por tendência central; não uma referência clínica. Welch e V de Cramér são complementos exploratórios, não apresentados como conteúdo necessariamente desenvolvido em aula.

[AHA: valores altos podem ser achados de taquiarritmia, não prova de erro](https://www.heart.org/-/media/CPR-Files/CPR-Guidelines-Files/2025-Algorithms/Algorithm-PALS-Tachyarrhythmia-250117.pdf). Não foi aplicada conduta ou diagnóstico; a fonte fundamenta preservar a incerteza. [Documentação oficial sobre pré-processamento](https://scikit-learn.org/stable/modules/preprocessing.html) e [prevenção de vazamento](https://scikit-learn.org/stable/common_pitfalls.html). Percentis clínicos incompletamente verificados não foram fabricados.

Codex auxiliou a investigação, implementação, comparações, verificações e redação. A leitura do grupo é necessária antes de apresentação ou entrega; testes técnicos não substituem validação clínica ou aprovação do professor.

## Conclusão crítica da busca atual

As 81 configurações e as sensibilidades foram executadas, sem perseguir a pontuação do teste. As vencedoras foram registradas antes de avaliá-lo. As tabelas de CV, nested CV, teste e sensibilidades permitem contestar as escolhas. Nenhuma combinação é declarada melhor em qualquer população ou finalidade. O relatório integrado discute quais ganhos têm suporte e quais continuam exploratórios.
