# -*- coding: utf-8 -*-
"""Paper-Logging-Callback (Engelhardt et al. Fig.2-konform).
Spielt alle `eval_freq` Trainings-Steps EINE deterministische Eval-Episode und
loggt (timestep, balance_B, rounds_r, return) in eine CSV. So entstehen die
gleichen drei Trainingskurven wie im Paper.
"""
import os
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
from sb3_contrib.common.maskable.utils import get_action_masks


class PaperMetricsCallback(BaseCallback):
    def __init__(self, eval_env, eval_freq=2000, csv_path="training_log.csv",
                 eval_seed=17, best_model_path=None, verbose=1, snap_dir=None):
        super().__init__(verbose)
        self.eval_env = eval_env
        self.eval_freq = eval_freq
        self.csv_path = csv_path
        self.eval_seed = eval_seed
        self.best_model_path = best_model_path
        self.best_key = (-1, -1e18)   # (rounds_r, balance_B): erst Ueberleben, dann B
        # Snapshot-Verzeichnis: jeder neue R30-B-Hoechstwert wird SOFORT als eindeutig
        # benannte .zip gesichert (nie ueberschrieben) -> kein 15,76-Peak geht je verloren,
        # auch nicht bei Disconnect (wenn snap_dir auf Drive zeigt).
        self.snap_dir = snap_dir
        self.best_r30_B = -1e18
        self._last_eval = 0
        os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
        if best_model_path is not None:   # checkpoints/-Ordner sichern -> kein FileNotFoundError bei save()
            os.makedirs(os.path.dirname(best_model_path) or ".", exist_ok=True)
        if snap_dir is not None:
            os.makedirs(snap_dir, exist_ok=True)
        # Ueberschreib-Schutz: existierende CSV nie verlieren -> .bak-Kopie
        if os.path.exists(self.csv_path):
            import shutil, time as _t
            bak = self.csv_path + f".bak_{int(_t.time())}"
            shutil.copy2(self.csv_path, bak)
            if verbose:
                print(f"  [schutz] alte CSV gesichert -> {os.path.basename(bak)}")
        with open(self.csv_path, "w", encoding="utf-8") as f:
            f.write("timestep,balance_B,rounds_r,return\n")

    def _run_eval_episode(self):
        env = self.eval_env
        obs, _ = env.reset(seed=self.eval_seed)
        inner = env.unwrapped
        ep_return = 0.0
        B = 0.0
        done = False
        while not done:
            mask = get_action_masks(env)
            action, _ = self.model.predict(obs, action_masks=mask, deterministic=True)
            obs, rew, term, trunc, info = env.step(action)
            ep_return += float(rew)
            B = float(info.get('eval_balance_B', 0.0))
            done = term or trunc
        r = int(inner.V[inner.ROUND])
        return B, r, ep_return

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_eval >= self.eval_freq:
            self._last_eval = self.num_timesteps
            B, r, ret = self._run_eval_episode()
            with open(self.csv_path, "a", encoding="utf-8") as f:
                f.write(f"{self.num_timesteps},{B:.4f},{r},{ret:.4f}\n")
            msg = f"  [eval @ {self.num_timesteps:>8}]  B={B:6.2f}  r={r:>2}  return={ret:9.2f}"
            # Best-Checkpoint: erst max rounds_r, dann max B (Marathonlaeufer wie Seed 17)
            if self.best_model_path is not None and (r, B) > self.best_key:
                self.best_key = (r, B)
                self.model.save(self.best_model_path)
                msg += f"   <- NEW BEST (r={r}, B={B:.2f})"
            # SOFORT-Snapshot: jeder neue R30-B-Hoechstwert wird eindeutig gesichert
            # (nie ueberschrieben) -> kein 15,76-Treffer geht verloren, auch bei Disconnect.
            if self.snap_dir is not None and r == 30 and B > self.best_r30_B + 1e-6:
                self.best_r30_B = B
                snap = os.path.join(
                    self.snap_dir, f"R30_t{self.num_timesteps}_B{B:.4f}.zip")
                self.model.save(snap)
                msg += f"   <- R30-SNAPSHOT {os.path.basename(snap)}"
            if self.verbose:
                print(msg)
        return True
