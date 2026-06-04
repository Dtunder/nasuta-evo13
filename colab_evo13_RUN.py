# -*- coding: utf-8 -*-
"""EVO 13 - Colab-Runner fuer Paper-konforme Datensammlung (GPU).
=============================================================================
ANLEITUNG:
 1. Lade den kompletten Ordner `release_evo13` in dein Google Drive, z.B. nach
    MyDrive/nasuta_evo/release_evo13
 2. Oeffne ein neues Colab-Notebook, Laufzeit -> GPU (T4).
 3. Kopiere dieses gesamte Script in eine Zelle und fuehre es aus
    (passe DRIVE_DIR an, falls dein Pfad abweicht).
=============================================================================
Trainiert die gewuenschten Reward-Modi ueber 5 Seeds (wie Paper, Seeds 17-21)
und loggt B / r / return dicht. Danach lokal `plot_paper_3panel.py` ausfuehren.
"""
import os, sys, subprocess

# ---- 0. Konfiguration -------------------------------------------------------
DRIVE_DIR = "/content/drive/MyDrive/nasuta_evo/release_evo13"
MODES     = ["survival", "perround"]   # + "balance" fuer reine Paper-Baseline
SEEDS     = [17, 18, 19, 20, 21]
TIMESTEPS = 800_000                     # Paper-Standard
EVAL_FREQ = 2000
DEVICE    = "cuda"

# ---- 1. Drive mounten -------------------------------------------------------
try:
    from google.colab import drive
    drive.mount("/content/drive")
except Exception as e:
    print("Kein Colab/Drive (lokal?):", e)

# ---- 2. Dependencies --------------------------------------------------------
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "sb3-contrib==2.3.0", "stable-baselines3==2.3.0",
                "gymnasium==0.29.1", "pandas", "openpyxl", "scipy"], check=False)

# ---- 3. Pfade ---------------------------------------------------------------
assert os.path.isdir(DRIVE_DIR), f"DRIVE_DIR nicht gefunden: {DRIVE_DIR}"
sys.path.insert(0, DRIVE_DIR)
sys.path.insert(0, os.path.join(DRIVE_DIR, "src"))
os.makedirs(os.path.join(DRIVE_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(DRIVE_DIR, "checkpoints"), exist_ok=True)

import torch.nn as nn
_o = nn.LSTM.__init__
def _p(self, i, h, *a, **k): return _o(self, int(i), int(h), *a, **k)
nn.LSTM.__init__ = _p

# train_one aus dem mitgelieferten Script wiederverwenden
import importlib.util
spec = importlib.util.spec_from_file_location("tpd", os.path.join(DRIVE_DIR, "train_paper_data.py"))
tpd = importlib.util.module_from_spec(spec); spec.loader.exec_module(tpd)

# ---- 4. Training ------------------------------------------------------------
for mode in MODES:
    for seed in SEEDS:
        tpd.train_one(mode, seed, TIMESTEPS, DEVICE, EVAL_FREQ)

print("\n=== EVO13 COLAB FERTIG ===")
print("Logs + Checkpoints liegen in:", DRIVE_DIR)
print("Lokal danach:  python plot_paper_3panel.py --mode survival")
print("               python plot_paper_3panel.py --mode perround")
