# Artigo A2 no formato IEEE de conferências

O artigo usa duas colunas e inclui o link público do código no rodapé da primeira página. [PDF da entrega](output/pdf/Artigo_A2_IEEE.pdf).

O manuscrito usa a classe de conferência IEEEtran 1.8b e o estilo bibliográfico IEEEtran distribuídos pelo CTAN. O [IEEE Author Center](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/) disponibiliza as instruções e os modelos. A versão dos recursos TeX e os hashes ficam em `provenance.lock.json`. As licenças estão em `vendor/licenses/`.

## Compilar

O Tectonic 0.17.0 está fixado para macOS arm64 e Windows x86-64. Use Python 3.11 ou mais recente e Poppler ou `pypdf` para a conferência da paginação. No diretório do artigo, execute:

```sh
python tools/bootstrap.py
python tools/build.py --final
```

`tools/gerar_numeros.py` atualiza as macros e tabelas LaTeX na compilação final, a partir dos resultados agregados em `results/reviewed_results.json`. O manifesto da compilação identifica esse JSON, o PDF, as fontes LaTeX, as tabelas geradas e as figuras incluídas no manuscrito.

As duas figuras vetoriais podem ser recriadas do mesmo JSON com `python tools/figura_disponibilidade.py` e `python tools/figura_sopro.py`, em um ambiente com Matplotlib.

A primeira compilação pode buscar recursos no servidor TeX. Com o cache preenchido, acrescente `--offline` para usar os recursos locais. O comando final verifica o hash do JSON, o endereço público, a classe IEEEtran de conferências, a extensão do resumo e o limite de cinco páginas.
