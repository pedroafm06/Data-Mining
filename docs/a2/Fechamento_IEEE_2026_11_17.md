# Fechamento editorial e técnico do artigo IEEE em 17/11/2026

A revisão conferiu os apontamentos recebidos contra o PDF e as fontes reais. Dados, modelos, partições e resultados experimentais permanecem iguais. O artigo continua usando a classe IEEEtran original de conferências, duas colunas, corpo de 10 pontos e o estilo bibliográfico IEEEtran. Não houve redução de fontes ou alteração de margens para acomodar o conteúdo.

| Apontamento | Avaliação e correção |
|---|---|
| Type 3 nas figuras | Confirmado no PDF anterior. As duas figuras usam agora STIXGeneral serifada, com pdf.fonttype 42. O PDF final contém 15 fontes incorporadas, zeroType 3 e zero fontes sem incorporação. O processo de compilação final também bloqueia Type 3 ou fontes não incorporadas. |
| Index Terms junto de Resumo | Corrigido para Palavras-chave, preservando o ambiente e a tipografia da classe IEEE. |
| X indefinido na TabelaI | Corrigido para datas brutas não entrarem nos preditores. NORMAL X ANORMAL continua sendo o nome literal da coluna do alvo. |
| Siglas antes da definição | BA definida no resumo, KDD na introdução, DN/IMC/PAS/PAD/FC/B2 e os históricos da doença na TabelaI, IC na metodologia. As definições seguem o dicionário da disciplina. SOPRO e PULSOS são nomes de campos e recebem explicação clínica. Não foram criadas expansões fictícias. PPA recebe descrição funcional. |
| Referências 3 e 4 | Os originais não identificam autor nem data editorial. A referência declara essa ausência e identifica o fornecimento pelo INF/UFG, via SIGAA, na oferta 2026/2. Essa oferta não é apresentada como ano de publicação original. Não foram inventadas URLs individuais. |
| Referência de Breiman | Número 1,volume 45,páginas 5–32,outubro 2001 e URLDOI conferidos na editora. |
| Referência de Varma e Simon | Volume 7,artigo 91,fevereiro 2006 e URLDOI conferidos na editora. 91 é número do artigo e não página. O estilo bibliográfico imprime esse dado como Art.no.91. |
| Fig. e Figura | Texto e legendas usam Figura. |
| IDADE e SEXO nas figuras | Padronizados conforme os nomes das variáveis. A prosa pode continuar usando idade e sexo como palavras comuns. |
| Última página | Colunas equilibradas com flushend. Conferência visual das quatro páginas após a compilação. |
| Rodapé do repositório | O link público continua no rodapé da primeira página. A URL aparece inteira numa linha e é clicável. O hífen de Data-Mining faz parte do endereço verdadeiro. O rodapé sem marcador separado decorre do thanks da classe IEEE de conferência e foi preservado. |
| Metadados | Título e autores no PDF agora contêm os acentos corretos e o título completo do artigo. |
| Parágrafos interrompidos | Posições de figuras e tabelas revisadas. Uma reserva dinâmica de espaço mantém o começo da subseção de associação unido sem impor uma quebra de coluna desnecessária. |

O resumo tem 121 palavras pelo método documentado no manifesto, que conta palavras alfabéticas no TeX depois de remover comandos. A exigência é 100–150 palavras. A fonte do JSON de resultados do artigo foi comparada com os resultados finais do projeto.

O PDF foi recompilado e as quatro páginas foram renderizadas e inspecionadas. Não há avisos de excesso de largura ou referências indefinidas. O link anotado na página 1 aponta para o repositório correto. Esta é uma verificação local. O arquivo não foi enviado ao serviço IEEE PDF eXpress e esta revisão não certifica aceitação por esse serviço.

SHA256 do PDF final: `323827c785827ebf72b89c9894a7875eeb92f937069332e9a898916d56bd86fc`.

Fontes de conferência: Verificacao_Artigo.json, main.tex, seções do artigo, scripts das figuras, references.bib e o parecer bibliográfico em Revisao_Final_A2.md. Os originais IEEEtran permanecem protegidos pelos hashes de provenance.lock.json.

O bloqueio automático de fontes também foi testado contra o PDF anterior, que continha Type 3: a validação o rejeitou. O PDF corrigido passou pela mesma validação. Artigo, apresentação e materiais de estudo publicados no commit 65c1ce9 foram baixados anonimamente e comparados com os locais, com hashes iguais.
