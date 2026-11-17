# Apresentação da A2 · Grupo 3 · INF/UFG

A apresentação acompanha o [artigo IEEE final](../../paper/a2_ieee_2026_11_07/output/pdf/Artigo_A2_IEEE.pdf) e os [resultados agregados de 16/11](../../resultados/a2/revisao_final_2026_11_16/reviewed_results.json). O fundo e a tipografia seguem a apresentação da A1 no Canva.

- [Editar no Canva](https://www.canva.com/d/1a0E5pSF5pW2vtG)
- [Apresentação editável](output/Apresentacao_A2_INF.pptx)
- [Slides em PDF](output/Apresentacao_A2_INF.pdf)
- [Roteiro, notas técnicas e perguntas de arguição](output/Roteiro_A2_INF.md)
- [Guia de estudo e defesa do trabalho](output/Guia_Defesa_A2.md)

São 16 slides, todos apresentados. A fala prevê 13 min 55 s, mais 35 s de pausas e transições. O total planejado é 14 min 30 s e precisa ser confirmado em ensaio pelo grupo. Não há slides de reserva ou destinados a ser pulados.

A sequência acompanha a seleção das entradas, a limpeza, as transformações, a comparação dos modelos, a avaliação e as conclusões. Os exemplos reais mostram a frequência cardíaca registrada como 1.120 e tratada como ausente, o preenchimento com a mediana 92 do ajuste final da floresta, o indicador de preenchimento e o cálculo de IMC a partir de 5 kg e 51 cm. São valores isolados, sem identificadores ou datas de pacientes. Cada treino da validação calcula sua própria mediana.

As notas separam a fala prevista das explicações de apoio. O guia discute as decisões por variável, alternativas de transformação, escolha e ajuste dos modelos, fórmulas e limites das métricas, possíveis vazamentos e perguntas de defesa. Os resultados de avaliação usam as previsões externas da validação aninhada. As configurações finais de ajuste são identificadas separadamente.

## Recriar o PowerPoint

O gerador lê a síntese dos resultados e o roteiro estruturado do repositório. Na raiz do projeto, extraia o fundo original da A1 e execute o gerador usando o runtime de apresentações:

~~~sh
mkdir -p work/a2_apresentacao_inf
pdfimages -f 1 -l 1 -j docs/a1_entregue/Apresentacao_A1_Entregue.pdf work/a2_apresentacao_inf/template
node presentation/a2_inf/build_deck.mjs
~~~

Defina RUNTIME_NODE_MODULES, CODEX_PRESENTATIONS_SKILL e CODEX_PRESENTATIONS_PYTHON com os caminhos do runtime de apresentações e da pasta de suas ferramentas. As verificações recebem nomes exclusivos em cada execução. O PDF é exportado do PowerPoint pelo LibreOffice Impress.
