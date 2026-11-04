"""Build and execute the full A2 notebook without duplicating statistical code."""
from pathlib import Path
import argparse,json,sys,tempfile
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
ROOT=Path(__file__).resolve().parents[1]


def build(execute=True,source=None):
    md=nbformat.v4.new_markdown_cell;code=nbformat.v4.new_code_cell
    n=nbformat.v4.new_notebook(cells=[md('''# A2 - Processo completo do KDD

A A2 aproveita e melhora a A1 e conclui **entendimento, seleção, limpeza, transformação, mineração, avaliação, interpretação e aplicação/documentação**. A A1 entregue permanece preservada.

As decisões e alternativas estão em `docs/a2/Decisoes_KDD_Completo.md`; o relatório integrado reúne resultados e limites. O código abaixo chama a mesma biblioteca dos comandos de reprodução. O alvo é o rótulo registrado, sem validação clínica independente.'''),code('''from pathlib import Path
import os, sys, json, subprocess
import pandas as pd
candidates = [Path.cwd(), *Path.cwd().parents]
PROJECT = next((p for p in candidates if (p / "pyproject.toml").is_file() and (p / "src/kdd_revision").is_dir()), None)
if PROJECT is None:
    raise RuntimeError("Abra o notebook dentro do clone Data-Mining.")
sys.path.insert(0, str(PROJECT / "src"))
SOURCE = Path(os.environ.get("KDD_SOURCE", str(PROJECT / "dados/raw/UCMF_raw.csv"))).expanduser()
if not SOURCE.is_file():
    raise FileNotFoundError("Disponibilize a base da disciplina em dados/raw/ ou defina KDD_SOURCE.")
print("Escopo: A2 com o processo completo do KDD; a A1 entregue é histórica.")'''),md('''## Executar a sequência completa

A entrada e as regras são verificadas; limpeza e transformações são aplicadas. A busca compara 81 configurações por cenário, com imputação/vocabulário/escala ajustados em cada treino de fold. Há CV e nested CV no desenvolvimento. As escolhas são congeladas antes do teste histórico, que já passou por exploração.

Um clone sem artefatos executa toda a busca. Quando existe uma execução completa e compatível, `REUTILIZAR_BUSCA_CONGELADA=True` confere fonte, código de ajuste, protocolo, hashes e reaplicação dos modelos antes de reutilizá-la. A aplicação e os relatórios são atualizados sem tuning. Use False para refazer a busca, mantendo todos os critérios.'''),code('''REUTILIZAR_BUSCA_CONGELADA = True
command = [sys.executable, str(PROJECT / "tools/run_full_kdd.py"), "--source", str(SOURCE)]
if REUTILIZAR_BUSCA_CONGELADA and (PROJECT / "artifacts/a2_mining/verification.json").exists():
    command.append("--reuse-mining")
completed = subprocess.run(command, cwd=PROJECT, capture_output=True, text=True, timeout=1800)
if completed.returncode:
    raise RuntimeError(completed.stderr + completed.stdout)
A = PROJECT / "artifacts/a2_mining"
verification = json.loads((A / "verification.json").read_text())
assert verification["complete"] and verification["all_selections_frozen_before_test"]
print({k: verification[k] for k in ["n_development", "n_test", "n_candidates_per_scenario", "n_preprocessing_fits_audited", "groups_crossing_fit_test"]})'''),md('''## Avaliar a busca e os modelos

A média de CV usada para escolher é distinta da avaliação aninhada do procedimento e da avaliação secundária no teste histórico. Comparamos recall, precisão, especificidade, F1 e BA junto das contagens. Os gráficos não autorizam escolher um limiar pelo teste. Scores e associações não constituem diagnóstico ou causa.'''),code('''metrics = json.loads((A / "test_metrics.json").read_text())
nested = json.loads((A / "nested_results.json").read_text())
display(pd.DataFrame([{ "cenario": scenario, "nested_BA": nested[scenario]["pooled_oof"]["balanced_accuracy"], **result } for scenario, result in metrics.items()]).set_index("cenario"))
from IPython.display import display, Image
display(Image(filename=str(A / "figures/confusoes.png")))
display(Image(filename=str(A / "figures/curvas.png")))'''),md('''## Contestar as escolhas

As sensibilidades comparam qualidade, indicadores, redução e balanceamento no desenvolvimento. PCA usa a melhor logística e precisa ser comparada à mesma configuração sem PCA. São explorações pós-seleção, sem trocar o vencedor pela pontuação do teste. Um ganho pequeno não comprova superioridade fora destes dados.'''),code('''sensitivity = pd.read_csv(A / "sensibilidades.csv")
display(sensitivity.pivot(index="variant", columns="scenario", values="mean_cv_balanced_accuracy"))
importance = pd.read_csv(A / "importancia_permutacao.csv")
display(importance.sort_values(["scenario", "mean_drop_balanced_accuracy"], ascending=[True,False]).groupby("scenario").head(3))'''),md('''## Aplicar o conhecimento, respeitando o suporte dos dados

A aplicação inicial que exigia apenas um campo foi rejeitada: muitos padrões de ausência não tinham suporte no desenvolvimento. A regra revisada exige padrão de disponibilidade presente em pelo menos 30 exemplos e categorias conhecidas. Coberturas para 1/10/30 são publicadas; não há rótulos novos para escolher uma acurácia ótima. Cobertura aceita não valida a previsão individual.

As previsões ficam locais e separadas de y. O conhecimento também orienta corrigir a coleta e esclarecer temporalidade e construção do alvo. Nenhuma implantação clínica foi feita.'''),code('''application = json.loads((PROJECT / "artifacts/a2_application/summary.json").read_text())
display(pd.DataFrame([{ "cenario": scenario, **{k: value[k] for k in ["n_unlabeled", "n_scored", "n_abstained", "n_p_ge_half"]} } for scenario,value in application.items()]))
display(pd.read_csv(PROJECT / "artifacts/a2_application/comparacao_cobertura.csv"))
reproduction = json.loads((PROJECT / "artifacts/a2_kdd/reproduction.json").read_text())
assert reproduction["complete"] and reproduction["test_membership_unchanged"]
assert all(r["identical_classes"] and r["max_abs_prediction_difference"] <= 1e-12 for r in reproduction["models_reapplied"].values())
print("Modelos salvos reaplicados e métricas conferidas; fonte preservada.")
print("Relatório: docs/a2/Relatorio_A2_KDD_Completo.pdf")
print("Decisões: docs/a2/Decisoes_KDD_Completo.md e Registro_Microdecisoes.csv")''')])
    n.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}
    path=ROOT/'notebooks/02_kdd_completo_a2.ipynb'
    if execute:
        with tempfile.TemporaryDirectory(prefix='kdd2-') as tmp:
            spec=Path(tmp)/'kdd2';spec.mkdir()
            env={'PYTHONPATH':str(ROOT/'src')}
            if source is not None:env['KDD_SOURCE']=str(Path(source).expanduser().resolve())
            (spec/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'KDD completo local','language':'python','env':env}))
            km=KernelManager(kernel_name='kdd2',kernel_spec_manager=KernelSpecManager(kernel_dirs=[tmp]),transport='ipc',ip=str(Path(tmp)/'kernel'))
            NotebookClient(n,km=km,timeout=1800,resources={'metadata':{'path':str(ROOT)}}).execute()
        cells=[c for c in n.cells if c.cell_type=='code']
        if any(c.execution_count is None or any(o.output_type=='error' for o in c.outputs) for c in cells):raise AssertionError('Incomplete notebook')
    nbformat.write(n,path);print(path.relative_to(ROOT));return path

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--no-execute',action='store_true');p.add_argument('--source',type=Path)
    args=p.parse_args();build(not args.no_execute,args.source)
