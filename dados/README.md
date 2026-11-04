# Dados de entrada

A base `UCMF_raw.csv` é a fornecida no material do estudo de caso da disciplina. Ela não integra o repositório. Use a cópia à qual você tem acesso pela disciplina.

- Local padrão: `dados/raw/UCMF_raw.csv`.
- SHA-256 esperado: `35e68400d6bec51bbf74857c0f0e0487161b3495b5f4fefbc2cc57af24824ea1`.
- Dimensão esperada: 12.873 registros e 21 variáveis.
- O programa verifica o hash antes de produzir saídas. O arquivo de entrada não é alterado.

A alternativa é passar `--source` à preparação e usar `KDD_SOURCE` no notebook. `config/particoes_referencia.csv` preserva os identificadores, grupos candidatos e folds da separação histórica. A equivalência é candidata; não identifica pacientes com certeza.

As bases tratadas, proveniência, alterações por célula, matrizes, IDs, alvos e objetos serializados são gravados localmente em `artifacts/a2_preprocessing/`, pasta ignorada pelo Git. Não renomeie uma matriz sem manter seu mapa de linhas e sua versão de parâmetros.
