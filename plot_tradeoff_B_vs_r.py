# -*- coding: utf-8 -*-
"""Trade-off balance B vs. Runden r (Paper Fig.8-Stil, Engelhardt et al.).
Kernaussage: B = 10*[p + 3*D(q)] / (r+3)  -- r steht im NENNER.
=> Paper-Strategie: frueh stoppen (~R15) fuer hohes B (~28).
=> Evo12-Strategie: bis R30 ueberleben, B dann niedriger (~12) aber 100% Survival.
Daten: echte Trajektorien aus 1M- und 500k-Checkpoint (kein Neu-Training).
"""
import os, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "src"))

import torch.nn as nn
_o = nn.LSTM.__init__
def _p(self, i, h, *a, **k): return _o(self, int(i), int(h), *a, **k)
nn.LSTM.__init__ = _p

from survival_env import make_survival_env
from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

def trajectory(model_path, seed=42):
    """(rounds, balances) -- B-Stand am Ende jeder Spielrunde."""
    model = MaskablePPO.load(model_path, device="cpu")
    env = make_survival_env(); obs, _ = env.reset(seed=seed); inner = env.unwrapped
    rounds, bals = [], []
    done = False
    while not done:
        mask = get_action_masks(env)
        action, _ = model.predict(obs, action_masks=mask, deterministic=True)
        obs, _, term, trunc, info = env.step(action)
        done = term or trunc
        r = int(inner.V[inner.ROUND])
        b = info.get('balance (always)', None)
        if b is not None and r not in rounds:
            rounds.append(r); bals.append(round(float(b), 3))
    return np.array(rounds), np.array(bals)

P_1M = os.path.join(HERE, "oekolopoly_evo12_balanced_1M_steps.zip")
P_500K = os.path.join(ROOT, "resume_new_account", "evo12_fresh_master_500000_steps.zip")

r1, b1 = trajectory(P_1M)
print(f"1M  : R{r1[-1]}  B_final={b1[-1]:.2f}")
r05, b05 = trajectory(P_500K)
print(f"500k: R{r05[-1]}  B_final={b05[-1]:.2f}")

# --- Theoretische Obergrenze: max Qualitaet p=37, D(q)=5 -> K=37+15=52 ---
rr = np.arange(10, 31)
B_theo = 10 * 52 / (rr + 3)

# --- Plot ---
BG='#0E1726'; FG='#E7ECF4'; MUT='#93A3BD'; GRID='#1E2C45'
GREEN='#34D399'; CYAN='#38BDF8'; AMBER='#F5B74D'; RED='#F87171'; PURP='#A78BFA'
plt.rcParams.update({'text.color':FG,'axes.labelcolor':FG,'xtick.color':FG,
    'ytick.color':MUT,'axes.edgecolor':'#2A3A55','font.family':'DejaVu Sans','font.size':12})

fig, ax = plt.subplots(figsize=(11, 6), dpi=200)
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.grid(True, color=GRID, lw=0.7)
for sp in ('top','right'): ax.spines[sp].set_visible(False)

# "exceptionally good" Zone (B > 20, Spielregel)
ax.axhspan(20, 45, color=GREEN, alpha=0.06, zorder=0)
ax.axhline(20, ls='--', color=GREEN, lw=1.2, alpha=0.8)
ax.text(29.6, 20.8, 'B > 20 = „exceptionally good" (Spielregel)',
        color=GREEN, fontsize=9.5, ha='right', va='bottom')

# Theoretische Obergrenze
ax.plot(rr, B_theo, ':', color=MUT, lw=1.6, label='theoret. Max  B = 520/(r+3)')

# Paper-Optimum (Engelhardt et al. Fig.2): B~28 bei r~14
ax.scatter([14], [28], s=220, marker='*', color=PURP, zorder=6, edgecolors=BG, lw=1.2)
ax.annotate('Paper-Optimum (Engelhardt et al.)\n~R14 · B≈28 — stoppt früh',
            xy=(14, 28), xytext=(15.2, 33), color=PURP, fontsize=10, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=PURP, lw=1.3))

# Unsere 500k-Trajektorie (stirbt R21)
m05 = r05 >= 10
ax.plot(r05[m05], b05[m05], '-o', color=AMBER, lw=2, ms=4, zorder=4,
        label=f'Evo12 @500k  (stirbt R{r05[-1]})')

# Unsere 1M-Trajektorie (Gewinner, R30)
m1 = r1 >= 10
ax.plot(r1[m1], b1[m1], '-o', color=GREEN, lw=2.6, ms=5, zorder=5,
        label=f'Evo12 @1M  (überlebt R30)')
ax.scatter([r1[-1]], [b1[-1]], s=200, color=GREEN, zorder=7, edgecolors=BG, lw=1.5)
ax.annotate(f'Evo12-Sieg\nR30 · B={b1[-1]:.1f} · 100% Survival',
            xy=(r1[-1], b1[-1]), xytext=(24.5, 4.5), color=GREEN, fontsize=10, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=GREEN, lw=1.3))

ax.set_xlabel('gespielte Runden  r'); ax.set_ylabel('balance-Score  B')
ax.set_title('Der Zielkonflikt: Balance-Score B vs. Überleben\n'
             'B = 10·[p + 3·D(q)] / (r+3) — die Runde r steht im Nenner',
             color=FG, fontsize=13, pad=12)
ax.set_xlim(9.5, 30.5); ax.set_ylim(0, 38)
ax.legend(facecolor=BG, edgecolor=GRID, labelcolor=FG, fontsize=10, loc='upper right')

out = os.path.join(HERE, "_assets", "tradeoff_B_vs_r.png")
fig.tight_layout(); fig.savefig(out, facecolor=BG); plt.close(fig)
print(f"\nGespeichert: {out}")
