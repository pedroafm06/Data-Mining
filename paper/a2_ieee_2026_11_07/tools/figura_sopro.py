"""Render the exploratory association of recorded murmur and target."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager

# Use an installed serif font and embed TrueType outlines in vector PDFs.
font_manager.findfont("STIXGeneral", fallback_to_default=False)
matplotlib.rcParams.update({
    "font.family": "serif",
    "font.serif": ["STIXGeneral"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
eda = json.loads((ROOT / 'results/reviewed_results.json').read_text(encoding='utf-8'))['eda']
counts = eda['sopro_by_status']
fig, ax = plt.subplots(figsize=(3.46, 1.52), layout='constrained')
rates = [100 * row['n_anormal'] / row['n'] for row in counts.values()]
ax.barh(list(counts), rates, height=.48, color=['#54758a', '#007f82'])
for i, rate in enumerate(rates):
    label = f"{rate:.1f}%".replace('.', ',')
    ax.text(rate + 2, i, label, fontsize=8, va='center')
ax.invert_yaxis()
ax.set(xlim=(0, 114), xticks=range(0, 101, 20), xlabel='Registros com rótulo Anormal (%)')
ax.tick_params(labelsize=8, length=0)
ax.xaxis.label.set_size(8)
ax.set_axisbelow(True)
ax.grid(axis='x', alpha=.23)
for spine in ax.spines.values():
    spine.set_visible(False)
fig.savefig(ROOT / 'figures/sopro_rotulo.pdf')
