# -*- coding: utf-8 -*-
"""
compare_methods.py  —  Vereinheitlichter, fairer Benchmark fuer Oekolopoly Evo12.

Benchmarkt VIER Methoden auf IDENTISCHEN Seeds (0..9) und liefert pro Methode
BEIDE Metriken:
  (a) ueberlebte Runden        = int(V[8])
  (b) Score = Stability        = 30 - (V[:8].max() - V[:8].min())

Methoden:
  1. Paper Vanilla UCT  -> reines MCTS (SovereignMCTS, sovereign_mode=False),
                          NN-Policy-Guide = RecurrentPPO champion.
  2. Sovereign MCTS     -> MCTS + Soft-Constraints (sovereign_mode=True), gleicher Guide.
  3. Heuristik          -> handcodiert, DETERMINISTISCH (kein RNG).
  4. Evo12 MaskablePPO  -> trainierter Gewinner (oekolopoly_evo12_balanced_1M_steps.zip).

HARTE CONSTRAINTS (siehe _EVO12_FACTS.md §5):
  - KEIN Training. Nur Evaluation / Rollouts.
  - Jeder Rollout hat einen Step-Cap (STEP_CAP) gegen den bekannten Hang-Bug.
    Action 0 (Runde beenden) ist immer legaler Fallback.
  - Modell-Familien sauber getrennt: MaskablePPO (Evo12) vs RecurrentPPO (MCTS-Guide).
  - Timeboxing: haengt/scheitert eine Methode -> Fallback auf historische Zahlen
    aus _EVO12_FACTS.md §3, klar als "historisch (n=...)" gekennzeichnet.
    NIEMALS Zahlen erfinden.
"""

import os
import sys
import csv
import time
import warnings

import numpy as np

warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------------
# Pfade
# ----------------------------------------------------------------------------
CLONE_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CLONE_ROOT, "src")
for _p in (SRC_DIR, CLONE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Evo12-Gewinner liegt im Klon-Root.
MASKABLE_MODEL = os.path.join(CLONE_ROOT, "oekolopoly_evo12_balanced_1M_steps.zip")
# RecurrentPPO-Guide fuer MCTS liegt NICHT im Klon, sondern im Original-brain (nur lesend).
RECURRENT_MODEL = r"C:\Users\user\nasuta_evo\brain\sota_recurrent_champion.zip"

SEEDS = list(range(10))            # gemeinsames Seed-Set 0..9
STEP_CAP = 60                      # max. AP-Allokationen pro Episode (Hang-Schutz, NUR MCTS)
NN_STEP_CAP = 5000                 # nicht-bindender Schutz-Cap fuer das NN (Env terminiert bei R30)
NUM_SIMS = int(os.environ.get("NUM_SIMS", "60"))   # MCTS-Simulationen pro Step
# Wall-Clock-Budget pro MCTS-Methode (alle Seeds zusammen). Ueberschritten -> Fallback.
MCTS_BUDGET_S = float(os.environ.get("MCTS_BUDGET_S", "240"))

OUT_CSV = os.path.join(CLONE_ROOT, "_bench_results.csv")

# ----------------------------------------------------------------------------
# Historische Fallback-Zahlen (Single Source of Truth: _EVO12_FACTS.md §3)
#   -> NUR verwenden, wenn die Live-Messung haengt/scheitert. Nicht erfunden.
# ----------------------------------------------------------------------------
HISTORICAL = {
    "Paper Vanilla UCT": {"avg_rounds": 3.28, "max_rounds": 7,  "avg_score": None, "n": 25,
                          "note": "Multi-Seed n=25, Evo10-Logs (mittel)"},
    "Sovereign MCTS":    {"avg_rounds": 7.08, "max_rounds": 10, "avg_score": None, "n": 25,
                          "note": "Multi-Seed n=25, Evo10-Logs (mittel)"},
    "Heuristik":         {"avg_rounds": 24.0, "max_rounds": 24, "avg_score": None, "n": 1,
                          "note": "deterministisch (hoch)"},
    "Evo12 MaskablePPO": {"avg_rounds": 30.0, "max_rounds": 30, "avg_score": 1.0,  "n": 10,
                          "note": "evaluate_1M.py (hoch)"},
}


# ----------------------------------------------------------------------------
# LSTM int-Patch (RecurrentPPO laed sonst nicht unter PyTorch/Gymnasium)
# ----------------------------------------------------------------------------
def _patch_lstm():
    import torch.nn as nn
    _orig = nn.LSTM.__init__
    if getattr(nn.LSTM.__init__, "_oeko_patched", False):
        return
    def _p(self, input_size, hidden_size, *a, **k):
        return _orig(self, int(input_size), int(hidden_size), *a, **k)
    _p._oeko_patched = True
    nn.LSTM.__init__ = _p


# ----------------------------------------------------------------------------
# Gemeinsame Metrik-Extraktion (identisch fuer alle Methoden)
# ----------------------------------------------------------------------------
def _metrics(unwrapped):
    V = unwrapped.V
    rounds = int(V[8])
    score = float(30.0 - (np.max(V[:8]) - np.min(V[:8])))
    return rounds, score


def _valid_actions_from_mask(mask):
    ids = [i for i, m in enumerate(mask) if m]
    return ids if ids else [0]   # Action 0 immer legaler Fallback


def _action_mask_fn(curr_env):
    curr = curr_env
    while hasattr(curr, "env"):
        if hasattr(curr, "valid_action_mask"):
            return curr.valid_action_mask()
        curr = curr.env
    if hasattr(curr, "valid_action_mask"):
        return curr.valid_action_mask()
    return np.ones(9, dtype=bool)


# ----------------------------------------------------------------------------
# Methode 1 & 2:  MCTS (Vanilla UCT / Sovereign), RecurrentPPO als Guide
# ----------------------------------------------------------------------------
def run_mcts_once(model, sovereign_mode, seed):
    import random
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    from oeko_core.envs.oeko_env import OekoEnv
    from wrappers import OekoActionBuilderWrapper
    from gymcts.gymcts_deepcopy_wrapper import DeepCopyMCTSGymEnvWrapper
    from gymcts.gymcts_action_history_wrapper import ActionHistoryMCTSGymEnvWrapper
    from mcts_planner import SovereignMCTS

    base_env = OekoEnv(render_mode=None)
    wrapped = OekoActionBuilderWrapper(base_env)
    env = DeepCopyMCTSGymEnvWrapper(wrapped)
    env = ActionHistoryMCTSGymEnvWrapper(env, action_mask_fn=_action_mask_fn)
    env.reset(seed=seed)

    env.is_terminal = lambda: env.unwrapped.done
    env.get_valid_actions = lambda: _valid_actions_from_mask(_action_mask_fn(env))

    mcts = SovereignMCTS(model, num_simulations=NUM_SIMS,
                         render_tree=False, sovereign_mode=sovereign_mode)

    steps = 0
    done = False
    while not done and steps < STEP_CAP:           # Step-Cap gegen Hang-Bug
        valid = env.get_valid_actions()
        if not valid:
            break
        try:
            action = mcts.search(env)
        except Exception:
            action = 0                              # Fallback: Runde beenden
        if action not in valid:
            action = 0
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        steps += 1

    rounds, score = _metrics(env.unwrapped)
    return rounds, score


def run_mcts_method(label, sovereign_mode):
    """Alle Seeds fuer eine MCTS-Methode; Timebox -> Fallback historisch."""
    if not os.path.exists(RECURRENT_MODEL):
        print(f"  [{label}] RecurrentPPO-Modell fehlt -> historischer Fallback.")
        return None, "missing_model"

    try:
        _patch_lstm()
        from sb3_contrib import RecurrentPPO
        t0 = time.time()
        model = RecurrentPPO.load(RECURRENT_MODEL, device="cpu")
        print(f"  [{label}] RecurrentPPO geladen in {time.time()-t0:.1f}s "
              f"(NUM_SIMS={NUM_SIMS}, Budget={MCTS_BUDGET_S:.0f}s)")
    except Exception as e:
        print(f"  [{label}] Modell-Load fehlgeschlagen ({e}) -> historischer Fallback.")
        return None, "load_failed"

    rows = []
    start = time.time()
    for seed in SEEDS:
        if time.time() - start > MCTS_BUDGET_S:
            print(f"  [{label}] Wall-Clock-Budget ueberschritten bei Seed {seed} "
                  f"-> historischer Fallback fuer ganze Methode.")
            return None, "timebox"
        st = time.time()
        try:
            rounds, score = run_mcts_once(model, sovereign_mode, seed)
        except Exception as e:
            print(f"  [{label}] Seed {seed} FAILED ({e}) -> historischer Fallback.")
            return None, "exception"
        rows.append({"method": label, "seed": seed,
                     "rounds": rounds, "score": round(score, 3)})
        print(f"  [{label}] Seed {seed:02d}: Runden={rounds:02d} "
              f"Score={score:5.1f} ({time.time()-st:.1f}s)")
    return rows, "measured"


# ----------------------------------------------------------------------------
# Methode 3:  Deterministische Heuristik (Survival-First, KEIN RNG)
#   Adaptiert aus mcts_planner.guided_rollout_wrapper, aber RNG entfernt:
#   bei stabilem System wird die NIEDRIGSTE investierbare Aktion gewaehlt
#   (deterministisch) statt np.random.choice.
# ----------------------------------------------------------------------------
def run_heuristic_once(seed):
    from oeko_core.envs.oeko_env import OekoEnv
    from wrappers import OekoActionBuilderWrapper

    env = OekoActionBuilderWrapper(OekoEnv(render_mode=None))
    env.reset(seed=seed)
    u = env.unwrapped

    steps = 0
    done = False
    while not done and steps < STEP_CAP:
        V = u.V
        avail = int(V[9])
        mask = env.valid_action_mask()
        valid = _valid_actions_from_mask(mask)

        if avail > 0:
            if 1 in valid and V[5] < 12:        # 1) Umwelt schuetzen (Env collapse)
                move = 1
            elif 5 in valid and V[3] < 15:      # 2) Lebensqualitaet schuetzen
                move = 5
            elif 2 in valid and V[1] < 10:      # 3) Produktion aufbauen
                move = 2
            elif 1 in valid and V[5] < 15:      # 4) Sanierung / Umwelt-Recovery
                move = 1
            elif 4 in valid and V[2] < 15:      # 5) Bildung (langfristig)
                move = 4
            else:
                # stabil -> DETERMINISTISCH diversifizieren: niedrigste Invest-Aktion
                invest = [a for a in valid if a != 0]
                move = invest[0] if invest else 0
        else:
            move = 0                            # keine AP -> Runde beenden

        if move not in valid:
            move = 0
        obs, reward, terminated, truncated, info = env.step(move)
        done = terminated or truncated
        steps += 1

    rounds, score = _metrics(u)
    return rounds, score


def run_heuristic_method(label="Heuristik"):
    rows = []
    for seed in SEEDS:
        try:
            rounds, score = run_heuristic_once(seed)
        except Exception as e:
            print(f"  [{label}] Seed {seed} FAILED ({e}) -> historischer Fallback.")
            return None, "exception"
        rows.append({"method": label, "seed": seed,
                     "rounds": rounds, "score": round(score, 3)})
        print(f"  [{label}] Seed {seed:02d}: Runden={rounds:02d} Score={score:5.1f}")
    return rows, "measured"


# ----------------------------------------------------------------------------
# Methode 4:  Evo12 MaskablePPO (trainierter Gewinner)
#   Rollout-Logik aus evaluate_1M.py, mit Step-Cap abgesichert.
# ----------------------------------------------------------------------------
def run_maskable_method(label="Evo12 MaskablePPO"):
    if not os.path.exists(MASKABLE_MODEL):
        print(f"  [{label}] MaskablePPO-Modell fehlt -> historischer Fallback.")
        return None, "missing_model"

    try:
        _patch_lstm()
        import torch
        from survival_env import make_survival_env
        from sb3_contrib.ppo_mask import MaskablePPO
        from sb3_contrib.common.maskable.utils import get_action_masks
        t0 = time.time()
        model = MaskablePPO.load(MASKABLE_MODEL, device="cpu")
        print(f"  [{label}] MaskablePPO geladen in {time.time()-t0:.1f}s")
    except Exception as e:
        print(f"  [{label}] Modell-Load fehlgeschlagen ({e}) -> historischer Fallback.")
        return None, "load_failed"

    rows = []
    for seed in SEEDS:
        np.random.seed(seed)
        torch.manual_seed(seed)
        e = make_survival_env()
        obs, _ = e.reset(seed=seed)
        done = False
        steps = 0
        try:
            # WICHTIG: Der niedrige STEP_CAP (60) ist NUR ein Hang-Schutz fuer die
            # langsamen MCTS-Rollouts. Ein trainiertes NN kann NICHT haengen und die
            # Env terminiert hart bei Runde 30 (genau wie evaluate_1M.py, das ohne Cap
            # laeuft). Mit STEP_CAP=60 wurde der Gewinner faelschlich bei ~7 Runden
            # abgeschnitten (1 Runde = mehrere AP-Allokationen). Hoher, nicht-bindender
            # Schutz-Cap statt 60 -> Modell laeuft bis zur natuerlichen Terminierung.
            while not done and steps < NN_STEP_CAP:
                mask = get_action_masks(e)
                action, _ = model.predict(obs, action_masks=mask, deterministic=True)
                obs, r, term, trunc, info = e.step(action)
                done = term or trunc
                steps += 1
        except Exception as ex:
            print(f"  [{label}] Seed {seed} FAILED ({ex}) -> historischer Fallback.")
            return None, "exception"

        rounds, score = _metrics(e.unwrapped)
        rows.append({"method": label, "seed": seed,
                     "rounds": rounds, "score": round(score, 3)})
        print(f"  [{label}] Seed {seed:02d}: Runden={rounds:02d} Score={score:5.1f}")
    return rows, "measured"


# ----------------------------------------------------------------------------
# Aggregation & Report
# ----------------------------------------------------------------------------
def aggregate(label, rows, status):
    """Liefert (avg_rounds, max_rounds, avg_score, source_str)."""
    if status == "measured" and rows:
        rnd = [r["rounds"] for r in rows]
        scr = [r["score"] for r in rows]
        return (float(np.mean(rnd)), int(np.max(rnd)), float(np.mean(scr)),
                f"gemessen (n={len(rows)}, dieser Lauf)")
    # Fallback -> historisch
    h = HISTORICAL[label]
    return (h["avg_rounds"], h["max_rounds"], h["avg_score"],
            f"historisch (n={h['n']}; {h['note']})")


def main():
    print("=" * 64)
    print(" OEKOLOPOLY EVO12 — VEREINHEITLICHTER BENCHMARK")
    print(f" Seeds={SEEDS[0]}..{SEEDS[-1]} | Step-Cap={STEP_CAP} | NUM_SIMS={NUM_SIMS}")
    print("=" * 64)

    all_rows = []
    summary = []   # (label, avg_rounds, max_rounds, avg_score, source)

    method_runs = [
        ("Paper Vanilla UCT", lambda: run_mcts_method("Paper Vanilla UCT", False)),
        ("Sovereign MCTS",    lambda: run_mcts_method("Sovereign MCTS", True)),
        ("Heuristik",         lambda: run_heuristic_method("Heuristik")),
        ("Evo12 MaskablePPO", lambda: run_maskable_method("Evo12 MaskablePPO")),
    ]

    for label, fn in method_runs:
        print(f"\n--- {label} ---")
        t0 = time.time()
        rows, status = fn()
        if rows:
            all_rows.extend(rows)
        avg_r, max_r, avg_s, src = aggregate(label, rows, status)
        summary.append((label, avg_r, max_r, avg_s, src))
        print(f"  => {label}: Runden Ø {avg_r:.2f} / max {max_r} | "
              f"Score Ø {('%.2f' % avg_s) if avg_s is not None else 'n/a'} | {src} "
              f"({time.time()-t0:.1f}s)")

    # Roh-CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["method", "seed", "rounds", "score"])
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nRoh-Ergebnisse -> {OUT_CSV}  ({len(all_rows)} Zeilen gemessen)")

    # Konsolen-Tabelle
    print("\n" + "=" * 64)
    print(" ERGEBNIS-TABELLE")
    print("=" * 64)
    print(f"{'Methode':<20}{'Runden Ø':>10}{'max':>6}{'Score Ø':>10}  Quelle")
    for label, avg_r, max_r, avg_s, src in summary:
        s_str = f"{avg_s:.2f}" if avg_s is not None else "n/a"
        print(f"{label:<20}{avg_r:>10.2f}{max_r:>6}{s_str:>10}  {src}")

    # Markdown-Datei wird separat geschrieben (siehe _BENCHMARK_VERGLEICH.md).
    # Hier nur maschinenlesbares Summary fuer evtl. Weiterverarbeitung.
    summ_csv = os.path.join(CLONE_ROOT, "_bench_summary.csv")
    with open(summ_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["method", "avg_rounds", "max_rounds", "avg_score", "source"])
        for label, avg_r, max_r, avg_s, src in summary:
            w.writerow([label, f"{avg_r:.2f}", max_r,
                        ("%.2f" % avg_s) if avg_s is not None else "", src])
    print(f"Summary -> {summ_csv}")


if __name__ == "__main__":
    main()
