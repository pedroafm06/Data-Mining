# Apresentação da A2 UCMF

A apresentação editável fica em [PowerPoint](output/Apresentacao_A2_UCMF.pptx). Os 14 slides principais também estão disponíveis em [PDF](output/Apresentacao_A2_UCMF.pdf). O [roteiro](output/Roteiro_e_Arguicao.md) distribui 14 min 30 s entre os quatro integrantes e inclui perguntas de arguição. Sete slides de apoio ficam ocultos durante a apresentação e podem ser abertos pelo PowerPoint ou Impress.

O deck foi conferido pela renderização e pela abertura via LibreOffice Impress. As tabelas e os dois gráficos são editáveis. O tempo é uma estimativa de roteiro.

Para reconstruir, execute `python build_data.py` neste diretório após gerar a auditoria experimental na raiz do projeto. O gerador `build_deck.mjs` usa Node.js e o pacote `@oai/artifact-tool` do runtime de apresentações. Defina `CODEX_PRESENTATIONS_SKILL` com o caminho da instalação das ferramentas e `RUNTIME_NODE_MODULES` com o caminho das dependências desse runtime. Execute `node build_deck.mjs --final`. Para conservar o PPTX publicado e gerar uma nova cópia, defina `UCMF_DECK_REVISION` com um sufixo. O PDF é exportado pelo LibreOffice Impress.
