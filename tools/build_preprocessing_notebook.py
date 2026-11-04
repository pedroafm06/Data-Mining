"""Build the portable A2 preprocessing notebook; execute in a temporary kernel."""
from pathlib import Path
import argparse,json,sys,tempfile
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
ROOT=Path(__file__).resolve().parents[1]

def build(execute=True, source=None):
    n=nbformat.v4.new_notebook()
    n.cells=[nbformat.v4.new_markdown_cell('''# A2: revisão da limpeza e da transformação

Todas as revisões posteriores à A1 entregue integram a **A2**. Esta execução termina **antes da modelagem**; o KDD completo ainda precisa das próximas etapas. Cada decisão é explicada no registro `docs/a2/Decisoes_Preprocessamento_A2.md`.

Sequência: tipos e escalas → ausências e formatos → consistência → criação de idade/IMC → comparação de alternativas → ajuste do pré-processamento no desenvolvimento → aplicação e conferência.

Os séculos ambíguos continuam ambíguos. A idade relativa usa pares candidatos sob o recorte pediátrico, com intervalo e hipótese registrados. A matriz numérica é uma representação com estimativas; não transforma imputação em medição clínica.'''),
      nbformat.v4.new_code_cell('''from pathlib import Path
import sys, json, os
candidates = [Path.cwd(), *Path.cwd().parents]
PROJECT = next((p for p in candidates if (p / "pyproject.toml").is_file() and (p / "src/kdd_revision").is_dir()), None)
if PROJECT is None:
    raise RuntimeError("Abra o notebook dentro do clone Data-Mining.")
sys.path.insert(0, str(PROJECT / "src"))
from kdd_revision.preprocessing.run import run_preprocessing
from kdd_revision.preprocessing_report import generate
SOURCE = Path(os.environ.get("KDD_SOURCE", str(PROJECT / "dados/raw/UCMF_raw.csv"))).expanduser()
if not SOURCE.is_file():
    raise FileNotFoundError("Coloque UCMF_raw.csv em dados/raw/ ou defina KDD_SOURCE antes de iniciar o Jupyter.")
print("Escopo: pré-processamento da A2. Modelagem e avaliação com esta preparação permanecem pendentes.")'''),
      nbformat.v4.new_markdown_cell('''## Preparação e escolha das imputações

Preservamos as 21 variáveis e os valores originais na auditoria. Comparamos mediana global, por idade e por idade/sexo por mascaramento de medidas disponíveis somente no desenvolvimento, sem usar o alvo. Grupos precisam de suporte mínimo e usam fallback. A quarentena conserva a linha na base, retirando-a apenas do ajuste.

Os alertas de qualidade são operacionais, não diagnósticos. A verificação conjunta impede chamar os pais de um IMC extremo de automaticamente utilizáveis só porque passaram por limites individuais.'''),
      nbformat.v4.new_code_cell('''summary = run_preprocessing(PROJECT, source=SOURCE)
print(json.dumps({k: summary[k] for k in ["n_source", "n_fit", "n_test", "n_unlabeled", "models_fitted"]}, indent=2, ensure_ascii=False))'''),
      nbformat.v4.new_markdown_cell('''## Representações efetivamente aplicadas

- **Unidades originais:** imputações por coluna, codificação one-hot e indicadores.
- **Padronizada:** Z-score somente nas medidas contínuas.
- **Log-Peso + Z-score:** alternativa aplicada com log1p só no peso.

Indicadores e one-hot permanecem 0/1. Vocabulário, medianas e escalas são aprendidos só no ajuste. O teste e os não rotulados recebem aplicação sem reajuste. ID e alvo ficam separados de X. Para validação cruzada futura, o pré-processamento precisa ser novamente ajustado em cada fold; a matriz de desenvolvimento pronta não elimina essa exigência.'''),
      nbformat.v4.new_code_cell('''import pandas as pd
import numpy as np
A = PROJECT / "artifacts/a2_preprocessing"
checks = json.loads((A / "verification.json").read_text())
assert checks["source_preserved"] and checks["fit_development_only"]
assert not checks["models_fitted"]
for representation, check in checks["matrix_retransform"].items():
    assert check["finite"] and check["max_abs_export_delta"] <= 1e-10
    print(representation, check["n_rows"], "linhas x", check["n_columns"], "atributos; conferido com o transformador salvo")
display(pd.read_csv(A / "decisoes_imputacao.csv")[["variable", "method"]])'''),
      nbformat.v4.new_markdown_cell('''## Conferência e interpretação da preparação da A2

O relatório descreve medidas antes de imputar e separa as representações estimadas. Pearson/Spearman e bivariadas são descritivos; correlação maior não é prova de limpeza correta. Welch e V de Cramér são complementos técnicos. Não foram inventados percentis ou diagnósticos clínicos, nem balanceados os registros nesta preparação.'''),
      nbformat.v4.new_code_cell('''report_folder = generate(PROJECT, source=SOURCE)
print("Relatório e decisões:", report_folder.relative_to(PROJECT))
print("Bases aplicadas:", A.relative_to(PROJECT))
print("Esta revisão não revalida automaticamente os experimentos anteriores, produzidos com outra idade e outra preparação.")''')]
    n.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}
    path=ROOT/'notebooks/01_preprocessamento_a2.ipynb';path.parent.mkdir(parents=True,exist_ok=True)
    if execute:
        with tempfile.TemporaryDirectory(prefix='a2-preprocessing-kernel-') as tmp:
            d=Path(tmp)/'a2-preprocessing-local';d.mkdir()
            (d/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'A2 preprocessing local','language':'python','env':{'PYTHONPATH':str(ROOT/'src'),**({'KDD_SOURCE':str(Path(source).expanduser().resolve())} if source is not None else {})}}))
            manager=KernelManager(kernel_name='a2-preprocessing-local',kernel_spec_manager=KernelSpecManager(kernel_dirs=[tmp]), transport='ipc', ip=str(Path(tmp)/'a2-kernel'))
            NotebookClient(n,km=manager,timeout=600,resources={'metadata':{'path':str(ROOT)}}).execute()
        codes=[c for c in n.cells if c.cell_type=='code'];errors=[o for c in codes for o in c.outputs if o.output_type=='error']
        if errors or any(c.execution_count is None for c in codes):raise AssertionError('Notebook not fully executed')
    nbformat.write(n,path)
    print(path.relative_to(ROOT))
    return path
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,help='CSV original; caminho usado apenas durante a execução')
    parser.add_argument('--no-execute',action='store_true',help='Gerar sem executar')
    args=parser.parse_args()
    build(execute=not args.no_execute,source=args.source)
