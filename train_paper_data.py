# -*- coding: utf-8 -*-
"""EVO 13 - Paper-konforme Datensammlung (lokal, Multi-Seed).
Trainiert MaskablePPO ueber mehrere Seeds und loggt B / r / return dicht ueber
die Trainingszeit (PaperMetricsCallback) -> erzeugt die 3 Paper-Kurven.

Aufruf-Beispiele:
  python train_paper_data.py --mode survival --seeds 17,18,19,20,21 --timesteps 800000
  python train_paper_data.py --mode perround --seeds 17,18 --timesteps 400000 --device cpu
  python train_paper_data.py --mode balance  --seeds 17 --timesteps 800000

Modi (Reward):  survival = Evo12-Gewinner | perround = Paper Rc=0.5 | balance = Paper sparse
HP identisch zum Evo12-Original: MlpPolicy, n_steps=2048, lr=3e-4, batch=64, n_epochs=10, gamma=0.99, ent_coef=0.01
"""
import os, sys, argparse, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "src"))

import torch.nn as nn
_o = nn.LSTM.__init__
def _p(self, i, h, *a, **k): return _o(self, int(i), int(h), *a, **k)
nn.LSTM.__init__ = _p

from stable_baselines3.common.monitor import Monitor
from sb3_contrib.ppo_mask import MaskablePPO
from survival_env import make_survival_env
from paper_logging_callback import PaperMetricsCallback


def train_one(mode, seed, timesteps, device, eval_freq, gamma=0.99, ent_coef=0.01, suffix=""):
    os.environ["EVO13_REWARD_MODE"] = mode
    os.makedirs(os.path.join(HERE, "checkpoints"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    
    env = Monitor(make_survival_env(mode=mode))
    eval_env = make_survival_env(mode=mode)

    # Pfade zum Speichern (ganz normal unter dem angegebenen Seed)
    s_part = f"_{suffix}" if suffix else ""
    csv_path  = os.path.join(HERE, "logs", f"training_log_{mode}_seed{seed}{s_part}.csv")
    best_ckpt = os.path.join(HERE, "checkpoints", f"evo13_{mode}_seed{seed}{s_part}_BEST.zip")
    last_ckpt = os.path.join(HERE, "checkpoints", f"evo13_{mode}_seed{seed}{s_part}_LAST.zip")
    
    # Pfade zum Laden
    load_best_ckpt = best_ckpt
    load_last_ckpt = last_ckpt
    
    # Falls für den neuen Seed noch kein Checkpoint existiert, suchen wir nach dem Basis-Seed (z.B. seed % 100)
    if not os.path.exists(load_last_ckpt) and not os.path.exists(load_best_ckpt):
        base_seed = seed % 100
        cand_best = os.path.join(HERE, "checkpoints", f"evo13_{mode}_seed{base_seed}_BEST.zip")
        cand_last = os.path.join(HERE, "checkpoints", f"evo13_{mode}_seed{base_seed}_LAST.zip")
        if os.path.exists(cand_last):
            load_last_ckpt = cand_last
            print(f"  -> Neuer Seed {seed} startet: Lade existierenden Basis-Checkpoint von Seed {base_seed}")
        elif os.path.exists(cand_best):
            load_best_ckpt = cand_best
            print(f"  -> Neuer Seed {seed} startet: Lade existierenden Basis-BEST-Checkpoint von Seed {base_seed}")
            
    snap_dir = os.path.join(HERE, "checkpoints", f"snapshots_{mode}_seed{seed}{s_part}")
    cb = PaperMetricsCallback(eval_env=eval_env, eval_freq=eval_freq,
                              csv_path=csv_path, eval_seed=seed,
                              best_model_path=best_ckpt, verbose=1,
                              snap_dir=snap_dir)

    if os.path.exists(load_last_ckpt):
        print(f"  -> Lade Checkpoint für Weitertraining: {load_last_ckpt}")
        model = MaskablePPO.load(load_last_ckpt, env=env, device=device)
        model.gamma = gamma
        model.ent_coef = ent_coef
    elif os.path.exists(load_best_ckpt):
        print(f"  -> Lade BEST-Checkpoint für Weitertraining: {load_best_ckpt}")
        model = MaskablePPO.load(load_best_ckpt, env=env, device=device)
        model.gamma = gamma
        model.ent_coef = ent_coef
    else:
        print("  -> Initialisiere neues Modell (kein Basis-Checkpoint gefunden)")
        model = MaskablePPO("MlpPolicy", env, verbose=0, device=device, seed=seed,
                            n_steps=2048, learning_rate=3e-4, batch_size=64,
                            n_epochs=10, gamma=gamma, ent_coef=ent_coef)

    t0 = time.time()
    print(f"\n===== TRAIN  mode={mode}  seed={seed}  steps={timesteps}  device={device} =====")
    model.learn(total_timesteps=timesteps, callback=cb, progress_bar=False)
    dt = time.time() - t0

    model.save(last_ckpt)
    bk = cb.best_key
    print(f"  -> fertig in {dt/60:.1f} min | Log: {csv_path}")
    print(f"     BEST (r={bk[0]}, B={bk[1]:.2f}): {best_ckpt}")
    print(f"     LAST (Endzustand):              {last_ckpt}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="survival", choices=["survival", "perround", "balance", "marathon"])
    ap.add_argument("--seeds", default="22,23,24,25,26")
    ap.add_argument("--timesteps", type=int, default=1_200_000)
    ap.add_argument("--device", default="cpu")        # "cuda" auf Colab
    ap.add_argument("--eval_freq", type=int, default=2000)
    ap.add_argument("--gamma", type=float, default=0.99)
    ap.add_argument("--ent_coef", type=float, default=0.01)
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    print(f"EVO13 Multi-Seed Training | mode={args.mode} | seeds={seeds} | "
          f"{args.timesteps} steps | eval alle {args.eval_freq} | device={args.device} | suffix={args.suffix}")
    for seed in seeds:
        train_one(args.mode, seed, args.timesteps, args.device, args.eval_freq,
                  args.gamma, args.ent_coef, args.suffix)
    print("\nALLE SEEDS FERTIG. Plot:  python plot_paper_3panel.py --mode", args.mode)


if __name__ == "__main__":
    main()
