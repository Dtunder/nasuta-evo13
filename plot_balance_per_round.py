# -*- coding: utf-8 -*-
"""Plottet den balance-Score pro Runde fuer Seed 42 (deterministisch).
balance = (boxD * 3 + POLITICS) * 10 / (ROUND + 3)  -- aus oeko_env.py
Zeigt: wenn der Agent in Runde R sterben wuerde, welchen Score haette er dann?
"""
import os, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "src"))

import torch.nn as nn
_o = nn.LSTM.__init__
def _p(self, i, h, *a, **k): return _o(self, int(i), int(h), *a, **k)
nn.LSTM.__init__ = _p

from survival_env import make_survival_env
from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

MODEL_PATH = os.path.join(HERE, "oekolopoly_evo12_balanced_1M_steps.zip")
ASSET = os.path.join(HERE, "_assets")
os.makedirs(ASSET, exist_ok=True)

model = MaskablePPO.load(MODEL_PATH, device="cpu")
env = make_survival_env()
obs, _ = env.reset(seed=42)
inner = env.unwrapped

rounds, scores = [], []
done = False
while not done:
    mask = get_action_masks(env)
    action, _ = model.predict(obs, action_masks=mask, deterministic=True)
    obs, _, term, trunc, info = env.step(action)
    done = term or trunc

    r = int(inner.V[inner.ROUND])
    # balance_always wird vom env schon berechnet (info key)
    b = info.get('balance (always)', None)
    if b is not None and r not in rounds:
        rounds.append(r)
        scores.append(round(b, 2))

print(f"Runden aufgezeichnet: {rounds}")
print(f"Scores:               {scores}")

# --- Plot ---
BG='#0E1726'; FG='#E7ECF4'; MUT='#93A3BD'; GRID='#1E2C45'
GREEN='#34D399'; CYAN='#38BDF8'; AMBER='#F5B74D'

plt.rcParams.update({'text.color':FG,'axes.labelcolor':FG,'xtick.color':FG,
    'ytick.color':MUT,'axes.edgecolor':'#2A3A55','font.family':'DejaVu Sans','font.size':12})

fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.grid(True, axis='y', color=GRID, lw=0.7)
for sp in ('top','right'): ax.spines[sp].set_visible(False)

ax.plot(rounds, scores, color=CYAN, lw=2.5, zorder=3, marker='o', markersize=5)
ax.fill_between(rounds, scores, alpha=0.12, color=CYAN)

# Highlight Endrunde
ax.scatter([rounds[-1]], [scores[-1]], s=120, color=GREEN, zorder=5, edgecolors=BG, lw=1.5)
ax.annotate(f'R{rounds[-1]}: {scores[-1]:.2f}',
            xy=(rounds[-1], scores[-1]),
            xytext=(-30, 10), textcoords='offset points',
            color=GREEN, fontsize=11, fontweight='bold')

# Sonu-Aussage: Score sinkt mit steigenden Runden -- zeige Trend
if len(scores) >= 2:
    z = np.polyfit(rounds, scores, 1)
    p = np.poly1d(z)
    ax.plot(rounds, p(rounds), '--', color=AMBER, lw=1.2, alpha=0.7, label=f'Trend ({z[0]:+.3f}/Runde)')
    ax.legend(facecolor=BG, edgecolor=GRID, labelcolor=FG, fontsize=10)

ax.set_xlabel('Runde'); ax.set_ylabel('balance-Score in dieser Runde')
ax.set_title('Balance-Score-Verlauf über 30 Runden — Evo 12 Seed 42 (Sieg)\n'
             'Tatsächlicher Score-Stand in jeder Runde des erfolgreichen Laufs',
             color=FG, fontsize=12, pad=12)
ax.set_xlim(0, 32)

out = os.path.join(ASSET, 'balance_per_round.png')
fig.tight_layout()
fig.savefig(out, facecolor=BG)
plt.close(fig)
print(f"\nGespeichert: {out}")
