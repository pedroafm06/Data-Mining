# Apresentação da A2 · Grupo 3 · INF/UFG

A apresentação acompanha o [artigo IEEE final](../../paper/a2_ieee_2026_11_07/output/pdf/Artigo_A2_IEEE.pdf) e os [resultados agregados de 16/11](../../resultados/a2/revisao_final_2026_11_16/reviewed_results.json). O fundo e a tipografia seguem a apresentação da A1 no Canva.

- [Apresentação editável](output/Apresentacao_A2_INF.pptx)
- [Slides em PDF](output/Apresentacao_A2_INF.pdf)
- [Roteiro e perguntas de arguição](output/Roteiro_A2_INF.md)

São 14 slides e 14 min 10 s planejados entre os quatro integrantes. O slide de limpeza e transformação soma 50 s. As falas também aparecem nas notas do PowerPoint.

## Recriar o PowerPoint

O gerador lê a síntese dos resultados e o roteiro estruturado do repositório. Na raiz do projeto, extraia o fundo original da A1 e execute o gerador usando o runtime de apresentações:

~~~sh
mkdir -p work/a2_apresentacao_inf
pdfimages -f 1 -l 1 -j docs/a1_entregue/Apresentacao_A1_Entregue.pdf work/a2_apresentacao_inf/template
node presentation/a2_inf/build_deck.mjs
~~~

Defina RUNTIME_NODE_MODULES e CODEX_PRESENTATIONS_SKILL com os caminhos do runtime de apresentações e da pasta de suas ferramentas. O PDF foi exportado a partir do PowerPoint pelo LibreOffice Impress.
