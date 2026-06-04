# -*- coding: utf-8 -*-
"""Checkpoint-Sweep -> rekonstruiert die 3 Paper-Kurven (Engelhardt et al. Fig.2):
   balance B (Eq.1), rounds r, return (kumulativer Agent-Reward).
Evaluiert vorhandene Evo12-Checkpoints ueber mehrere Seeds. KEIN Neu-Training.
Output: _assets/_sweep_results.csv
"""
import os, sys, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # nasuta_evo
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "src"))

import torch.nn as nn
_o = nn.LSTM.__init__
def _p(self, i, h, *a, **k): return _o(self, int(i), int(h), *a, **k)
nn.LSTM.__init__ = _p

from survival_env import make_survival_env
from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

# (steps, pfad) -- Checkpoints derselben Evo12-Reihe ueber die Trainingszeit
CKPTS = [
    (500_000,  os.path.join(ROOT, "resume_new_account", "evo12_fresh_master_500000_steps.zip")),
    (1_000_000, os.path.join(HERE, "oekolopoly_evo12_balanced_1M_steps.zip")),
    (1_500_000, os.path.join(ROOT, "resume_new_account", "evo12_master_1500000_steps.zip")),
    (2_500_000, os.path.join(ROOT, "evo12_master_2500000_steps.zip")),
]

SEEDS = [int(s) for s in (sys.argv[1].split(",") if len(sys.argv) > 1 else "17,18,19,20,21".split(","))]
ASSET = os.path.join(HERE, "_assets"); os.makedirs(ASSET, exist_ok=True)

def eval_one(model, seed):
    env = make_survival_env()
    obs, _ = env.reset(seed=seed)
    inner = env.unwrapped
    ret = 0.0
    done = False
    last_balance = 0.0
    while not done:
        mask = get_action_masks(env)
        action, _ = model.predict(obs, action_masks=mask, deterministic=True)
        obs, rew, term, trunc, info = env.step(action)
        ret += float(rew)
        last_balance = info.get('balance (always)', 0.0)
        done = term or trunc
    r = int(inner.V[inner.ROUND])
    # Paper Eq.1: B = balance nur wenn 10<=r<=30, sonst 0
    B = float(last_balance) if 10 <= r <= 30 else 0.0
    return r, B, ret

rows = [("steps", "seed", "rounds", "balance", "return", "ckpt_ok")]
for steps, path in CKPTS:
    if not os.path.isfile(path):
        print(f"[SKIP] fehlt: {path}")
        rows.append((steps, -1, -1, -1, -1, "missing"))
        continue
    try:
        model = MaskablePPO.load(path, device="cpu")
    except Exception as e:
        print(f"[FAIL load] {steps}: {e}")
        rows.append((steps, -1, -1, -1, -1, f"loadfail:{type(e).__name__}"))
        continue
    for seed in SEEDS:
        try:
            r, B, ret = eval_one(model, seed)
            print(f"  steps={steps:>9} seed={seed:>3}  rounds={r:>2}  B={B:6.2f}  return={ret:8.2f}")
            rows.append((steps, seed, r, round(B, 3), round(ret, 3), "ok"))
        except Exception as e:
            print(f"  [FAIL eval] steps={steps} seed={seed}: {e}")
            rows.append((steps, seed, -1, -1, -1, f"evalfail:{type(e).__name__}"))

out = os.path.join(ASSET, "_sweep_results.csv")
with open(out, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(",".join(str(x) for x in row) + "\n")
print(f"\nGespeichert: {out}  ({len(rows)-1} Zeilen)")
