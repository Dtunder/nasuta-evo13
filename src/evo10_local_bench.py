#!/usr/bin/env python3
"""
Evo-10 Local PPO Benchmark
===========================
Fast, honest baseline using pure model.predict() — no MCTS.
Runs our RecurrentPPO model against seeds 0-9 on the paper-correct env
(30-round cap, balance defined for range(10, 31)).

Output: logs/evo10_local_ppo_results.csv
"""
import os
import sys
import csv
import time
import random
import math
import numpy as np
import torch
import torch.nn as nn

for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_DIR = os.path.join(ROOT_DIR, "engine")
SRC_DIR = os.path.join(ROOT_DIR, "src")
for p in [ENGINE_DIR, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# LSTM patch (same as xai_multiseed.py)
_orig_lstm_init = nn.LSTM.__init__
def _patched_lstm_init(self, input_size, hidden_size, *args, **kwargs):
    return _orig_lstm_init(self, int(input_size), int(hidden_size), *args, **kwargs)
nn.LSTM.__init__ = _patched_lstm_init

import gymnasium as gym
from oeko_core.envs.oeko_env import OekoEnv
from wrappers import OekoActionBuilderWrapper, OekoBoxActionWrapper
from sb3_contrib import RecurrentPPO

MODEL_PATH = os.path.join(ROOT_DIR, "brain", "sota_recurrent_champion.zip")
SEEDS = list(range(10))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
OUT_CSV = os.path.join(LOG_DIR, "evo10_local_ppo_results.csv")
FIELDNAMES = ["seed", "rounds_survived", "balance", "accumulated_reward", "done_reason", "duration_s"]


class Rescaled(gym.ActionWrapper):
    def __init__(self, env):
        super().__init__(env)
        self.action_space = gym.spaces.Box(0.0, 1.0, (6,), dtype=np.float32)

    def action(self, act):
        r = np.array(act, dtype=np.float32)
        r[1] = r[1] * 2.0 - 1.0
        r[5] = r[5] * 2.0 - 1.0
        return r


def run_episode(model, seed: int) -> dict:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    base = OekoEnv(render_mode=None)
    env = Rescaled(OekoBoxActionWrapper(base))
    obs, _ = env.reset(seed=seed)

    lstm_states = None
    episode_starts = np.ones((1,), dtype=bool)
    accumulated_reward = 0.0
    done = False

    while not done:
        action, lstm_states = model.predict(
            obs,
            state=lstm_states,
            episode_start=episode_starts,
            deterministic=True,
        )
        obs, reward, terminated, truncated, info = env.step(action)
        accumulated_reward += float(reward)
        episode_starts = np.array([terminated or truncated])
        done = terminated or truncated

    # Unwrap to the base OekoEnv to read V-state
    inner = base
    return {
        "seed": seed,
        "rounds_survived": int(inner.V[inner.ROUND]),
        "balance": float(getattr(inner, "balance_always", 0.0)),
        "accumulated_reward": round(accumulated_reward, 4),
        "done_reason": str(getattr(inner, "done_info", "unknown")).strip(),
    }


def main():
    if not os.path.exists(MODEL_PATH):
        print(f"[ERR] Model not found: {MODEL_PATH}")
        sys.exit(1)

    print(f"Loading model: {MODEL_PATH}")
    model = RecurrentPPO.load(MODEL_PATH, device="cpu")
    os.makedirs(LOG_DIR, exist_ok=True)

    print(f"\nEvo-10 Local PPO Benchmark | Seeds {SEEDS[0]}-{SEEDS[-1]} | env: 30-round cap + range(10,31) balance")
    print("-" * 72)

    rows = []
    for seed in SEEDS:
        t0 = time.time()
        try:
            result = run_episode(model, seed)
            result["duration_s"] = round(time.time() - t0, 2)
            rows.append(result)
            print(
                f"  Seed {seed:02d} | rounds={result['rounds_survived']:02d} | "
                f"balance={result['balance']:6.2f} | acc_reward={result['accumulated_reward']:8.4f} | "
                f"reason={result['done_reason'][:40]} ({result['duration_s']:.1f}s)"
            )
        except Exception as e:
            print(f"  Seed {seed:02d} FAILED: {e}")
            rows.append({"seed": seed, "rounds_survived": -1, "balance": 0.0,
                         "accumulated_reward": 0.0, "done_reason": f"ERROR: {e}", "duration_s": 0.0})

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    valid = [r for r in rows if r["rounds_survived"] >= 0]
    n = len(valid)
    if n > 0:
        rounds_list = [r["rounds_survived"] for r in valid]
        bal_list = [r["balance"] for r in valid]
        acc_list = [r["accumulated_reward"] for r in valid]
        survived_30 = sum(1 for r in rounds_list if r >= 30)

        def ci(vals):
            return 1.96 * np.std(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0

        print("\n" + "=" * 72)
        print(f"SUMMARY: RecurrentPPO@paper-rules | n={n} seeds")
        print(f"  Survived 30 rounds : {survived_30}/{n} ({100*survived_30/n:.0f}%)")
        print(f"  Rounds survived    : {np.mean(rounds_list):.1f} +/- {ci(rounds_list):.1f} (max {max(rounds_list)})")
        print(f"  Balance            : {np.mean(bal_list):.3f} +/- {ci(bal_list):.3f}")
        print(f"  Accumulated reward : {np.mean(acc_list):.4f} +/- {ci(acc_list):.4f}")
        print(f"\nCSV written: {OUT_CSV}")


if __name__ == "__main__":
    main()
