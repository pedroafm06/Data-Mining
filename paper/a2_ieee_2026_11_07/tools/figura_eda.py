"""Gera as figuras de EDA e de importância do artigo a partir de results/reviewed_results.json.

Usa apenas agregados (contagens, taxas e estatísticas de boxplot); nenhum registro clínico.
Saídas: figures/eda_alvo_achados.pdf (largura de 2 colunas) e figures/importancia.pdf (1 coluna).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "results/reviewed_results.json").read_text(encoding="utf-8"))
EDA = R["eda"]
BLUE, ORANGE, GRAY = "#376e92", "#b5532a", "#9aa7b1"
plt.rcParams.update({"font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                     "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})


def br(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


LABELS = {"SOPRO": {"Ausente": "ausente", "Sistolico": "sistólico", "Continuo": "contínuo", "Diastolico": "diastólico",
                    "Sistolico e diastolico": "sist.+diast."},
          "B2": {"Normal": "normal", "Hiperfonetica": "hiperfonética", "Desdob fixo": "desdobr. fixo", "Unica": "única", "Outro": "outro"},
          "PULSOS": {"Normais": "normais", "Amplos": "amplos", "Femorais diminuidos": "femorais dim.", "Diminuidos": "diminuídos", "Outro": "outro"}}


def eda_figure():
    fig, axes = plt.subplots(1, 4, figsize=(7.16, 2.15), layout="constrained", gridspec_kw={"width_ratios": [0.95, 2.6, 1, 1]})
    # a) distribuição do alvo
    counts = EDA["class_counts"]; total = sum(counts.values())
    ax = axes[0]
    ax.bar(["Normal", "Anormal"], [counts["Normal"], counts["Anormal"]], color=[GRAY, ORANGE], width=0.65)
    for i, k in enumerate(["Normal", "Anormal"]):
        ax.text(i, counts[k] + total * 0.01, f"{counts[k]:,}".replace(",", ".") + f"\n({br(100 * counts[k] / total)}%)", ha="center", va="bottom", fontsize=6)
    ax.set(title="a) Alvo (desenvolvimento)", ylabel="Registros", ylim=(0, max(counts.values()) * 1.3))
    ax.tick_params(axis="x", labelsize=6)
    # b) % de anormais por categoria (categorias com n >= 20)
    ax = axes[1]; rows = []
    for var in ["SOPRO", "B2", "PULSOS"]:
        cats = [c for c in EDA["categories"] if c["variable"] == var and c["value"] in LABELS[var] and c["n_development"] >= 20]
        cats.sort(key=lambda c: -c["n_development"])
        rows += [(f"{var}: {LABELS[var][c['value']]}", 100 * c["anormal_rate"], c["n_development"]) for c in cats]
    rows = rows[::-1]
    ax.barh(range(len(rows)), [r[1] for r in rows], color=[ORANGE if r[1] > EDA["anormal_percent"] else GRAY for r in rows], height=0.7)
    ax.axvline(EDA["anormal_percent"], color="black", lw=0.7, ls="--")
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    for i, (_, v, n) in enumerate(rows):
        ax.text(v + 1, i, f"{br(v, 0)}% (n={n:,})".replace(",", "."), va="center", fontsize=5.8)
    ax.set(xlim=(0, 135), xticks=range(0, 101, 25), xlabel="Anormais na categoria (%)", title="b) Anormais por achado do exame (n ≥ 20)")
    # c, d) boxplots de IDADE e FC por classe (estatísticas pré-calculadas, sem pontos atípicos)
    for ax, key, title, unit in [(axes[2], "box_IDADE", "c) Idade", "anos"), (axes[3], "box_FC", "d) FC", "bpm")]:
        stats = [dict(EDA[key][k], label=k, fliers=[]) for k in ["Normal", "Anormal"]]
        b = ax.bxp(stats, showfliers=False, showmeans=False, widths=0.55, patch_artist=True)
        for patch, color in zip(b["boxes"], [GRAY, ORANGE]):
            patch.set_facecolor(color); patch.set_alpha(0.75)
        for med in b["medians"]:
            med.set_color("black")
        for i, k in enumerate(["Normal", "Anormal"]):
            ax.text(i + 1, EDA[key][k]["med"], br(EDA[key][k]["med"]), ha="center", va="bottom", fontsize=5.8)
        ax.set(title=title, ylabel=unit)
    fig.savefig(ROOT / "figures/eda_alvo_achados.pdf")
    plt.close(fig)


NAMES = {"PA SISTOLICA": "PAS", "PA DIASTOLICA": "PAD", "HDA 1": "HDA1", "IDADE": "Idade"}


def importance_figure():
    """Três painéis: melhor família de cada cenário, 6 atributos de maior queda média."""
    fig, axes = plt.subplots(1, 3, figsize=(7.16, 1.75), layout="constrained")
    pt = {"tree": "árvore", "logistic": "logística", "forest": "floresta"}
    for ax, pool, letter in zip(axes, ["CLINICO", "FISIO8", "STRICT4"], "abc"):
        family = R["best_family_by_pool"][pool]
        rows = sorted([r for r in R["importance"] if r["pool"] == pool and r["family"] == family], key=lambda r: -r["mean"])[:6][::-1]
        ax.barh([NAMES.get(r["variable"], r["variable"]) for r in rows], [100 * r["mean"] for r in rows],
                xerr=[100 * r["std"] for r in rows], color=BLUE, height=0.65, error_kw={"lw": 0.6, "capsize": 1.5})
        ax.axvline(0, color="black", lw=0.6)
        top = max(100 * (r["mean"] + r["std"]) for r in rows)
        for i, r in enumerate(rows):
            ax.text(max(100 * r["mean"], 0) + 100 * r["std"] + top * 0.03, i, br(100 * r["mean"]), va="center", fontsize=5.8)
        ax.set_xlim(min(0, min(100 * r["mean"] for r in rows)) - top * 0.02, top * 1.25)
        ax.set(title=f"{letter}) {pool} ({pt[family]})", xlabel="Queda de BA (p.p.)")
        ax.grid(axis="x", alpha=0.25); ax.set_axisbelow(True)
    fig.savefig(ROOT / "figures/importancia.pdf")
    plt.close(fig)


if __name__ == "__main__":
    eda_figure()
    importance_figure()
    print("figuras geradas em", ROOT / "figures")
