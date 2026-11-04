# Histórico experimental

Os relatórios desta pasta registram a modelagem exploratória executada com uma preparação anterior. A correção de idade, a nova política de qualidade, a imputação selecionada e a quarentena de equivalência ainda não foram integradas a esses modelos.

Os módulos `prepare.py`, `transforms.py`, `analysis.py`, `experiments.py` e as configurações `protocolo_experimental.json` e `reproducibility_reference.json` foram conservados como referência técnica dessa execução. O código atual de preparação está em `src/kdd_revision/preprocessing/`.

Os resultados antigos não estabelecem desempenho da preparação atual. Para a próxima execução, será necessário usar a limpeza atual, ajustar toda transformação dentro de cada fold e congelar o novo protocolo antes de avaliar modelos. O teste histórico já foi explorado; repetir sua avaliação não cria um teste independente.
