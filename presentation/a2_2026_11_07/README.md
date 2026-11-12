# Apresentação da A2 UCMF

- [Slides em PDF](output/Apresentacao_A2_UCMF.pdf): 15 slides numerados.
- [PowerPoint editável](output/Apresentacao_A2_UCMF.pptx): os mesmos 15 slides e mais 3 de apoio ocultos (todas as métricas, teste histórico, reprodução e uso de IA). Tabelas e gráficos são nativos e editáveis.
- [Roteiro e arguição](output/Roteiro_e_Arguicao.md): 14 min 30 s divididos entre os quatro integrantes, com as perguntas prováveis, inclusive sobre a decisão de vazamento.

## Reconstruir

Todos os números vêm de `resultados/a2/auditoria_2026_11_07/reviewed_results.json`. Neste diretório:

```sh
python build_data.py          # gera .build/content.json e output/Roteiro_e_Arguicao.md
npm install                   # instala pptxgenjs 3.12.0 (package.json)
node build_deck.mjs           # gera output/Apresentacao_A2_UCMF.pptx
soffice --headless --convert-to pdf --outdir output output/Apresentacao_A2_UCMF.pptx
```

O PDF é exportado pelo LibreOffice Impress, que omite os slides ocultos.
