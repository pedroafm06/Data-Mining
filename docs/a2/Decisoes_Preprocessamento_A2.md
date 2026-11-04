# A2: decisões de limpeza e transformação



Esta revisão integra a A2 e termina antes da modelagem. A A1 avaliada é a versão já entregue; suas cópias históricas permanecem preservadas. As transformações foram aplicadas e exportadas, com parâmetros ajustados somente no desenvolvimento já separado. Este relatório cobre a preparação; os modelos atuais são apresentados no relatório integrado da A2.



## Ordem do processo e conceitos



1. Entender tipos, escalas, unidades e finalidade dos 21atributos.

2. Reconhecer ausência, padronizar grafias e converter formatos sem perder o original.

3. Verificar inconsistência léxica, de domínio, lógica e temporal; separar erro comprovado de suspeita.

4. Recalcular idade relativa e IMC quando os insumos observados permitem; guardar origem e incerteza.

5. Examinar repetições e cobertura, sem inventar identidade ou remover raros por predominância.

6. Comparar alternativas de imputação no desenvolvimento, por mascaramento de valores observados, sem alvo.

7. Ajustar imputação, vocabulário, one-hot e escala no desenvolvimento; aplicar o mesmo objeto aos outros registros.

8. Conferir matrizes finitas, indicadores 0/1, nomes, alinhamento, parâmetros e reprodução do transformador salvo.



## A descoberta sobre idade



Em 11.191 registros comparáveis, a idade recebida fica a até 0,01 ano de arredondar dias/352; 11.120 coincidem exatamente. Isso é evidência aritmética da inadequação da coluna para representar idade cronológica; não revela a fórmula original da planilha. 6.722 casos superestimam mais de 0,1 ano e 601 mais de 0,5 ano frente à referência relativa do diagnóstico. A revisão usa datas candidatas compatíveis com o recorte 0–19 anos completos, mantendo intervalo e hipótese, sem fixar século absoluto. Casos sem identificação suficiente não recebem uma data inventada. Valores negativos originais continuam na auditoria.



## Julgamento variável por variável



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