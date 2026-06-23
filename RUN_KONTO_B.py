# -*- coding: utf-8 -*-
"""EVO13 - KONTO B  |  survival  |  seeds 24,25  |  1.2M Steps  |  Best-Checkpoint.
=============================================================================
SO BENUTZEN (Colab, ZWEITES Google-Konto):
  1. Neues Colab-Notebook -> Laufzeit -> Laufzeittyp aendern -> GPU (T4)
  2. Den GANZEN Inhalt dieser Datei in EINE Zelle kopieren und ausfuehren.

  WICHTIG - Drive-Zugriff fuer Konto B:
  Damit Konto B denselben Ordner sieht, in Konto A einmalig:
    release_evo13 -> Teilen -> Konto-B-Mail (Bearbeiter)
  Dann in Konto B: "Geteilt mit mir" -> release_evo13 ->
    "Verknuepfung zu Meine Ablage hinzufuegen".
  So schreiben beide Konten in denselben Ordner -> kein Mergen noetig
  (verschiedene Seed-Nummern = verschiedene Dateien).
=============================================================================
"""
import os, sys, subprocess

# ---- Konfiguration (KONTO B) ----
DRIVE_DIR = "/content/drive/MyDrive/Antigravity/Oekolopoly/release_evo13"
SEEDS     = [33, 34]
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

import importlib.util
spec = importlib.util.spec_from_file_location("tpd", os.path.join(DRIVE_DIR, "train_paper_data.py"))
tpd = importlib.util.module_from_spec(spec); spec.loader.exec_module(tpd)

# ---- Training ----
print(f"KONTO B | mode={MODE} | seeds={SEEDS} | {TIMESTEPS} steps | eval alle {EVAL_FREQ}")
for seed in SEEDS:
    tpd.train_one(MODE, seed, TIMESTEPS, "cuda", EVAL_FREQ, GAMMA, ENT_COEF)

print("\n=== KONTO B FERTIG (seeds", SEEDS, ") ===")
print("Ergebnisse in:", DRIVE_DIR, "-> logs/ und checkpoints/")
