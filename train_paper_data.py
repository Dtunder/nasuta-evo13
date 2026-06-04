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


def train_one(mode, seed, timesteps, device, eval_freq):
    os.environ["EVO13_REWARD_MODE"] = mode
    env = Monitor(make_survival_env(mode=mode))
    eval_env = make_survival_env(mode=mode)

    csv_path = os.path.join(HERE, "logs", f"training_log_{mode}_seed{seed}.csv")
    cb = PaperMetricsCallback(eval_env=eval_env, eval_freq=eval_freq,
                              csv_path=csv_path, eval_seed=seed, verbose=1)

    model = MaskablePPO("MlpPolicy", env, verbose=0, device=device, seed=seed,
                        n_steps=2048, learning_rate=3e-4, batch_size=64,
                        n_epochs=10, gamma=0.99, ent_coef=0.01)

    t0 = time.time()
    print(f"\n===== TRAIN  mode={mode}  seed={seed}  steps={timesteps}  device={device} =====")
    model.learn(total_timesteps=timesteps, callback=cb, progress_bar=False)
    dt = time.time() - t0

    ckpt = os.path.join(HERE, "checkpoints", f"evo13_{mode}_seed{seed}.zip")
    model.save(ckpt)
    print(f"  -> fertig in {dt/60:.1f} min | Log: {csv_path} | Modell: {ckpt}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="survival", choices=["survival", "perround", "balance"])
    ap.add_argument("--seeds", default="17,18,19,20,21")
    ap.add_argument("--timesteps", type=int, default=800_000)
    ap.add_argument("--device", default="cpu")        # "cuda" auf Colab
    ap.add_argument("--eval_freq", type=int, default=2000)
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    print(f"EVO13 Multi-Seed Training | mode={args.mode} | seeds={seeds} | "
          f"{args.timesteps} steps | eval alle {args.eval_freq} | device={args.device}")
    for seed in seeds:
        train_one(args.mode, seed, args.timesteps, args.device, args.eval_freq)
    print("\nALLE SEEDS FERTIG. Plot:  python plot_paper_3panel.py --mode", args.mode)


if __name__ == "__main__":
    main()
