# -*- coding: utf-8 -*-
"""EVO13 - KONTO A  |  survival  |  seeds 22,23,26  |  1.2M Steps  |  Best-Checkpoint.
=============================================================================
SO BENUTZEN (Colab):
  1. Neues Colab-Notebook -> Laufzeit -> Laufzeittyp aendern -> GPU (T4)
  2. Den GANZEN Inhalt dieser Datei in EINE Zelle kopieren und ausfuehren
     (NICHT via !python starten - drive.mount braucht die interaktive Zelle).
=============================================================================
Schreibt pro Seed:
  logs/training_log_survival_seed{N}.csv          (Kurve B/r/return)
  checkpoints/evo13_survival_seed{N}_BEST.zip     (bestes Modell: max r, dann max B)
  checkpoints/evo13_survival_seed{N}_LAST.zip     (Endzustand)
Alte Dateien werden NIE geloescht (automatischer .bak-Schutz).
"""
import os, sys, subprocess

# ---- Konfiguration (KONTO A) ----
DRIVE_DIR = "/content/drive/MyDrive/Antigravity/Oekolopoly/release_evo13"
SEEDS     = [30, 31, 32]      # <-- KONTO B nutzt RUN_KONTO_B.py mit [33, 34]
MODE      = "marathon"        # Evo13-Aggressiv: R30 + B-End-Bonus (Ziel 15,76)
TIMESTEPS = 1_200_000
EVAL_FREQ = 2000
GAMMA     = 0.999             # langer Horizont -> Survival-Bonus frueh sichtbar
ENT_COEF  = 0.02             # mehr Exploration -> raus aus Sprinter-Optima

# ---- Drive mounten ----
try:
    from google.colab import drive
    drive.mount("/content/drive")
except Exception as e:
    print("Kein Colab/Drive (lokal?):", e)

# ---- Dependencies ----
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "sb3-contrib==2.3.0", "stable-baselines3==2.3.0",
                "gymnasium==0.29.1", "scipy"], check=False)

# ---- Pfade ----
assert os.path.isdir(DRIVE_DIR), f"DRIVE_DIR nicht gefunden: {DRIVE_DIR}"
sys.path.insert(0, DRIVE_DIR)
sys.path.insert(0, os.path.join(DRIVE_DIR, "src"))

import torch.nn as nn
_o = nn.LSTM.__init__
def _p(self, i, h, *a, **k): return _o(self, int(i), int(h), *a, **k)
nn.LSTM.__init__ = _p

# train_one aus dem mitgelieferten Script wiederverwenden
import importlib.util
spec = importlib.util.spec_from_file_location("tpd", os.path.join(DRIVE_DIR, "train_paper_data.py"))
tpd = importlib.util.module_from_spec(spec); spec.loader.exec_module(tpd)

# ---- Training ----
print(f"KONTO A | mode={MODE} | seeds={SEEDS} | {TIMESTEPS} steps | eval alle {EVAL_FREQ}")
for seed in SEEDS:
    tpd.train_one(MODE, seed, TIMESTEPS, "cuda", EVAL_FREQ, GAMMA, ENT_COEF)

print("\n=== KONTO A FERTIG (seeds", SEEDS, ") ===")
print("Ergebnisse in:", DRIVE_DIR, "-> logs/ und checkpoints/")
