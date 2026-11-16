"""Gera generated/numeros.tex (macros) e as tabelas do artigo a partir de results/reviewed_results.json.

Nenhum número de resultado é digitado nos .tex: o texto usa as macros definidas aqui.
Convenção dos nomes: \\v<Cenário><Família><Métrica>, p.ex. \\vClinArvBA (percentual com vírgula).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "results/reviewed_results.json").read_text(encoding="utf-8"))
OUT = ROOT / "generated"
POOLS = {"CLINICO": "Clin", "FISIO8": "Fisio", "STRICT4": "Strict"}
FAMS = {"dummy": "Maj", "tree": "Arv", "logistic": "Log", "forest": "Flo"}
FAM_PT = {"dummy": "Classe majoritária", "tree": "Árvore", "logistic": "Logística", "forest": "Floresta"}
METRICS = {"balanced_accuracy": "BA", "recall": "Sens", "specificity": "Esp", "precision": "Prec", "f1": "Fum",
           "roc_auc": "AUC", "average_precision": "AP"}


def pct(x, d=1):
    return f"{100 * x:.{d}f}".replace(".", ",")


def num(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def inteiro(x):
    return f"{int(round(x)):,}".replace(",", "{.}")


macros = {}
for table, prefix in [("metrics", "v"), ("historical_test_metrics", "t")]:
    for r in R[table]:
        key = prefix + POOLS[r["pool"]] + FAMS[r["family"]]
        for m, short in METRICS.items():
            macros[key + short] = pct(r[m])
        for m in ["tn", "fp", "fn", "tp"]:
            macros[key + m.upper()] = inteiro(r[m])
        if table == "metrics":
            macros[key + "Acc"] = pct(r["accuracy"])
            macros[key + "SD"] = num(100 * r["sd_fold_BA"], 2)

best = R["best_family_by_pool"]
for pool, short in POOLS.items():
    macros["best" + short] = FAM_PT[best[pool]].lower()
by = {(r["pool"], r["family"]): r for r in R["metrics"]}
clin = [by["CLINICO", f]["balanced_accuracy"] for f in ["tree", "logistic", "forest"]]
macros["clinBAspread"] = num(100 * (max(clin) - min(clin)), 2)
g_fisio = by["CLINICO", best["CLINICO"]]["balanced_accuracy"] - by["FISIO8", best["FISIO8"]]["balanced_accuracy"]
g_strict = by["FISIO8", best["FISIO8"]]["balanced_accuracy"] - by["STRICT4", best["STRICT4"]]["balanced_accuracy"]
macros["ganhoClinFisio"] = num(100 * g_fisio)
macros["ganhoFisioStrict"] = num(100 * g_strict)
best_clin = by["CLINICO", best["CLINICO"]]
macros["clinFNpctAnormal"] = pct(best_clin["fn"] / (best_clin["fn"] + best_clin["tp"]))

# Dados e reconciliação A1/A2
rec = R["a1_reconciliation"]; eda = R["eda"]
for k in ["n_source", "n_a1_duplicates", "n_a1_duplicates_unlabelled", "n_a1_duplicates_labelled", "n_unlabelled",
          "n_labelled_a2", "n_a1_final", "labelled_duplicates_same_group_as_copy", "labelled_duplicates_other_group",
          "labelled_duplicates_other_partition_than_copy"]:
    macros["rec" + "".join(w.capitalize() for w in k.replace("a1", "aum").replace("a2", "adois").split("_"))] = inteiro(rec[k])
macros["nRetirado"] = inteiro(rec["n_labelled_a2"] - R["n_development"] - R["n_historical_test"])
macros["recDupDev"] = inteiro(rec["labelled_duplicates_by_partition"]["development"])
macros["recDupTest"] = inteiro(rec["labelled_duplicates_by_partition"]["test"])
macros["nDev"] = inteiro(R["n_development"]); macros["nTest"] = inteiro(R["n_historical_test"])
macros["nGroups"] = inteiro(R["n_groups_development"]); macros["nConfigs"] = inteiro(R["n_configs"])
macros["nNormal"] = inteiro(eda["class_counts"]["Normal"]); macros["nAnormal"] = inteiro(eda["class_counts"]["Anormal"])
macros["pctAnormal"] = num(eda["anormal_percent"]); macros["pctNormal"] = num(100 - eda["anormal_percent"])
macros["idadeMedNormal"] = num(eda["box_IDADE"]["Normal"]["med"]); macros["idadeMedAnormal"] = num(eda["box_IDADE"]["Anormal"]["med"])
macros["menosUmAnoNormal"] = num(eda["percent_under_1_year"]["Normal"]); macros["menosUmAnoAnormal"] = num(eda["percent_under_1_year"]["Anormal"])
for k, kn in [("q1", "Qum"), ("med", "Med"), ("q3", "Qtres")]:
    macros["fc" + kn + "Normal"] = num(eda["box_FC"]["Normal"][k], 0)
    macros["fc" + kn + "Anormal"] = num(eda["box_FC"]["Anormal"][k], 0)
macros["susN"] = inteiro(eda["convenio_SUS"]["n"]); macros["susPct"] = num(eda["convenio_SUS"]["anormal_percent"])
macros["missHDAdois"] = num(eda["missing_percent_HDA2"]); macros["missPPA"] = num(eda["missing_percent_by_clinico_variable"]["PPA"])
macros["missPAS"] = num(eda["missing_percent_by_clinico_variable"]["PA SISTOLICA"])
macros["missHDAum"] = num(eda["missing_percent_by_clinico_variable"]["HDA 1"])
cat = {(c["variable"], c["value"]): c for c in eda["categories"]}
macros["sopAusPct"] = pct(cat["SOPRO", "Ausente"]["anormal_rate"]); macros["sopSisPct"] = pct(cat["SOPRO", "Sistolico"]["anormal_rate"])
macros["sopAusN"] = inteiro(cat["SOPRO", "Ausente"]["n_development"]); macros["sopSisN"] = inteiro(cat["SOPRO", "Sistolico"]["n_development"])
macros["btwoNormPct"] = pct(cat["B2", "Normal"]["anormal_rate"]); macros["btwoHiperPct"] = pct(cat["B2", "Hiperfonetica"]["anormal_rate"])
probe = {p["variable"]: p["cv_balanced_accuracy"] for p in R["variable_probes"]}
for v, k in [("SOPRO", "Sopro"), ("MOTIVO1", "MotivoUm"), ("MOTIVO2", "MotivoDois"), ("B2", "Btwo"), ("FC", "FC"), ("Convenio", "Convenio")]:
    macros["probe" + k] = pct(probe[v])

# Importância por permutação (pontos percentuais de BA)
imp = {(r["pool"], r["family"], r["variable"]): r for r in R["importance"]}
for pool, short in POOLS.items():
    fam = best[pool]
    for v, k in [("SOPRO", "Sopro"), ("B2", "Btwo"), ("FC", "FC"), ("Peso", "Peso"), ("IDADE", "Idade")]:
        if (pool, fam, v) in imp:
            macros["imp" + short + k] = num(100 * imp[pool, fam, v]["mean"])
others = [abs(r["mean"]) for (p, f, v), r in imp.items() if p == "CLINICO" and f == best["CLINICO"] and v not in ("SOPRO", "B2")]
macros["impClinOutrosMax"] = num(100 * max(others), 2)

# Análise de erros
for pool, short in POOLS.items():
    e = R["error_analysis"][pool]
    macros["err" + short + "FNsemSopro"] = num(e["fn_without_murmur_percent"])
    macros["err" + short + "FPcomSopro"] = num(e["fp_with_murmur_percent"])
    macros["err" + short + "IdadeFN"] = num(e["median_age_fn"]); macros["err" + short + "IdadeTP"] = num(e["median_age_tp"])
e = R["error_analysis"]["CLINICO"]
macros["anormSemSopro"] = inteiro(e["anormal_without_murmur"]); macros["anormSemSoproPct"] = num(e["anormal_without_murmur_percent_of_anormal"])
macros["normComSopro"] = inteiro(e["normal_with_murmur"])

# Parâmetros finais do modelo destacado
fc = R["final_choices"]["CLINICO"][best["CLINICO"]]
def descreve(c):
    p = c["params"]; peso = "pesos balanceados" if p.get("class_weight") == "balanced" else "pesos uniformes"
    if c["kind"] == "tree":
        return f"critério {p['criterion']}, profundidade máxima {p['max_depth']}, {p['min_samples_leaf']} registros por folha, {peso}"
    if c["kind"] == "forest":
        prof = "sem limite de profundidade" if p["max_depth"] is None else f"profundidade máxima {p['max_depth']}"
        return f"{p['n_estimators']} árvores, {prof}, {p['min_samples_leaf']} registros por folha, {peso}"
    if c["kind"] == "logistic":
        return f"C={num(p['C'], 2)}, {peso}"
    return "classe majoritária"


macros["finalClinParams"] = descreve(fc)
macros["finalClinImput"] = {"global": "mediana global", "age": "mediana por faixa etária"}[fc["imputation"]]

# Incerteza: bootstrap pareado por grupo das previsões externas (IC 95%, pontos percentuais)
U = R["uncertainty"]
def intervalo(lo, hi, d=1):
    return f"[{num(100 * lo, d)}; {num(100 * hi, d)}]"
for name, m in U["models"].items():
    pool, fam = name.split("/")
    macros["ci" + POOLS[pool] + FAMS[fam] + "BA"] = intervalo(*m["ci95"])
macros["ciMeiaLargMax"] = num(100 * max((m["ci95"][1] - m["ci95"][0]) / 2 for m in U["models"].values()))
macros["nBoot"] = inteiro(U["n_boot"])
for d in U["differences"]:
    (pa, fa), (pb, fb) = d["a"].split("/"), d["b"].split("/")
    casas = 2 if abs(d["diff"]) < .01 else 1
    # Os dois sentidos: \dFisioFloFisioLog = floresta − logística e \dFisioLogFisioFlo = logística − floresta.
    for (p1, f1, p2, f2), s in [((pa, fa, pb, fb), 1), ((pb, fb, pa, fa), -1)]:
        key = "d" + POOLS[p1] + FAMS[f1] + POOLS[p2] + FAMS[f2]
        lo, hi = sorted(s * v for v in d["ci95"])
        macros[key] = num(100 * s * d["diff"], casas); macros[key + "CI"] = intervalo(lo, hi, casas)
    if pa != pb:  # queda entre os melhores de cada cenário, sem depender de qual família venceu
        alias = "dCross" + POOLS[pa] + POOLS[pb]
        macros[alias] = num(100 * d["diff"]); macros[alias + "CI"] = intervalo(*d["ci95"])
within = [d for d in U["differences"] if d["a"].split("/")[0] == d["b"].split("/")[0]]
for pool, short in POOLS.items():
    zero = [d["ci_contains_zero"] for d in within if d["a"].startswith(pool + "/")]
    macros["todasZero" + short] = "todas" if all(zero) else "nem todas"

# Conhecimento: regras da árvore final de cada cenário (suporte no desenvolvimento)
UNIDADES = {"Peso": "kg", "Altura": "cm", "IMC": "kg/m\\textsuperscript{2}", "IDADE": "anos", "FC": "bpm", "PA SISTOLICA": "mmHg", "PA DIASTOLICA": "mmHg"}
def condicao(c):
    m = re.fullmatch(r"(.+) (≤|>) ([-0-9.e]+)", c)
    if m:  # limiar numérico: três algarismos significativos e unidade
        var, op, val = m.groups(); v = float(val)
        texto = f"{v:.3g}".replace(".", ","); unidade = UNIDADES.get(var, "")
        if var == "IDADE" and v < 1:  # idades de recém-nascidos ficam legíveis em dias
            texto, unidade = f"{v * 365.25:.0f}", "dias"
        simbolo = "$\\leq$" if op == "≤" else "$>$"
        c = f"{var} {simbolo} {texto}~{unidade}".rstrip("~")
    c = c.replace("≠", "$\\neq$")
    for raw, nice in [("HDA 1", "HDA1"), ("PA SISTOLICA", "PAS"), ("PA DIASTOLICA", "PAD"), ("IDADE", "idade")]:
        c = c.replace(raw, nice)
    return c
for pool, short in POOLS.items():
    regras = R["knowledge"][pool]["rules"]
    partes = []
    for i, r in enumerate(sorted(regras, key=lambda r: -r["n"])):
        cond = " e ".join(condicao(c) for c in r["conditions"])
        partes.append(f"{cond} $\\Rightarrow$ \\textit{{{r['predicted']}}} ({inteiro(r['n'])} registros, {pct(r['anormal_rate'])}\\% anormais)")
    macros["regras" + short] = "; ".join(partes)
    macros["nRegras" + short] = str(len(regras))

OUT.mkdir(exist_ok=True)
lines = ["% Gerado por tools/gerar_numeros.py a partir de results/reviewed_results.json. Não editar."]
for k, v in sorted(macros.items()):
    assert k.isalpha(), k
    lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
(OUT / "numeros.tex").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

# Tabela II: métricas externas de todos os cenários e famílias
rows = []
for pool, short in POOLS.items():
    for i, fam in enumerate(FAMS):
        r = by[pool, fam]
        vals = [pct(r[m], 2) for m in METRICS]
        if fam == best[pool]:
            vals[0] = f"\\textbf{{{vals[0]}}}"
        label = f"\\multirow{{4}}{{*}}{{\\textsc{{{pool.capitalize()}}}}}" if i == 0 else ""
        rows.append(f"{label} & {FAM_PT[fam].replace('Classe majoritária', 'Maioria')} & " + " & ".join(vals) + " \\\\")
    rows.append("\\midrule")
rows[-1] = "\\bottomrule"
(OUT / "tab_resultados.tex").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")

# Tabela III: BA, sensibilidade e especificidade no teste histórico
trow = {(r["pool"], r["family"]): r for r in R["historical_test_metrics"]}
rows = []
for pool in POOLS:
    cells = []
    for fam in ["tree", "logistic", "forest"]:
        cells.append(pct(trow[pool, fam]["balanced_accuracy"], 2))
    rows.append(f"\\textsc{{{pool.capitalize()}}} & " + " & ".join(cells) + " \\\\")
rows.append("\\bottomrule")
(OUT / "tab_teste.tex").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
print(f"{len(macros)} macros em {OUT / 'numeros.tex'}")
