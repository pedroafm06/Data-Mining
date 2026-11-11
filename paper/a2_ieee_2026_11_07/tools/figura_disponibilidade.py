"""Rebuild the manuscript figure from the reviewed aggregate results."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
summary = json.loads((ROOT / "results/reviewed_results.json").read_text())
missing = summary["missing_percent_by_fisio_variable"]
columns = ["Peso", "Altura", "IMC", "IDADE", "PA SISTOLICA", "PA DIASTOLICA", "FC", "SEXO"]
labels = ["Peso", "Altura", "IMC", "Idade", "PAS", "PAD", "FC", "Sexo"]
values = [missing[column] for column in columns]

fig, ax = plt.subplots(figsize=(3.46, 1.92), layout="constrained")
ax.barh(labels, values, color="#376e92", height=0.65)
ax.invert_yaxis()
ax.set(xlabel="Ausentes ou mascarados (%)", xlim=(0, 68), xticks=range(0, 61, 10))
ax.xaxis.label.set_size(8)
ax.tick_params(labelsize=7, length=0)
ax.set_axisbelow(True)
ax.grid(axis="x", alpha=0.24)
for spine in ax.spines.values():
    spine.set_visible(False)
for index, value in enumerate(values):
    ax.text(value + 0.8, index, f"{value:.1f}".replace(".", ","), va="center", fontsize=7)

fig.savefig(ROOT / "figures/disponibilidade.pdf")
