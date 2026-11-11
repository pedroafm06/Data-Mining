# Artigo A2 no formato IEEE de conferências

[Artigo A2 em PDF](output/pdf/Artigo_A2_IEEE.pdf), com três páginas em duas colunas, resumo de 126 palavras pela contagem de palavras textuais e link público para o código no rodapé da primeira página.

O manuscrito usa a classe de conferência IEEEtran 1.8b e o estilo bibliográfico IEEEtran distribuídos pelo CTAN. O [IEEE Author Center](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/) disponibiliza as instruções e os modelos. A versão dos recursos TeX e os hashes ficam em `provenance.lock.json`. As licenças estão em `vendor/licenses/`.

## Compilar

A compilação registrada usou Tectonic 0.17.0, macOS arm64, Python 3 e Poppler. No diretório do artigo:

```sh
python3 tools/bootstrap.py
python3 tools/build.py --final
```

A primeira compilação pode buscar recursos no servidor TeX. Com o cache preenchido, adicione `--offline` para usar os recursos locais. A configuração do artigo identifica o JSON de resultados e a URL pública. A figura vetorial pode ser recriada a partir desse JSON com `python3 tools/figura_disponibilidade.py` em um ambiente com Matplotlib.
