import os, sys
import numpy as np
import pandas as pd
import torch
import glob

base_dir = r"C:\Users\user\nasuta_evo\resume_new_account"
temp_zip_dir = base_dir
sys.path.insert(0, os.path.join(temp_zip_dir, "src"))
sys.path.insert(0, os.path.join(temp_zip_dir, "evo11"))

import torch.nn as nn
_o = nn.LSTM.__init__
def _p(self,i,h,*a,**k): return _o(self,int(i),int(h),*a,**k)
nn.LSTM.__init__ = _p

from survival_env import make_survival_env
from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

# Suche nach der 1M Datei (nimmt die neueste)
zips = glob.glob(os.path.join(base_dir, "*balanced_1M_steps.zip"))
if not zips:
    # Falls sie in Downloads liegt
    dl_path = os.path.expanduser(r"~\Downloads\*1000000_steps.zip")
    zips = glob.glob(dl_path)

if not zips:
    print("FEHLER: Finde keine *1000000_steps.zip Datei!")
    sys.exit(1)

ckpt_path = max(zips, key=os.path.getctime)
print(f">>> Lade Modell für Audit: {ckpt_path}\n")

model = MaskablePPO.load(ckpt_path, device="cpu")

e = make_survival_env()
obs, _ = e.reset(seed=42)

print("Runde | San | Aufk | QoL | Prod | Umwelt | Pol | BevW | Bev ")
print("-" * 70)

inner = e.unwrapped
def print_state(v, r):
    print(f"  {int(r):02d}  | {int(v[0]):3d} | {int(v[1]):4d} | {int(v[2]):3d} | {int(v[3]):4d} | {int(v[4]):6d} | {int(v[5]):3d} | {int(v[6]):4d} | {int(v[7]):3d} ")

print_state(inner.V, inner.V[8])

done = False
while not done:
    mask = get_action_masks(e)
    action, _ = model.predict(obs, action_masks=mask, deterministic=True)
    obs, r, term, trunc, info = e.step(action)
    done = term or trunc
    print_state(inner.V, inner.V[8])

print("\n" + "="*50)
print("             AUDIT - BEFUND")
print("="*50)

state = inner.V[:8]
max_v = np.max(state)
min_v = np.min(state)

print(f"Maximaler End-Zustand: {max_v}")
print(f"Minimaler End-Zustand: {min_v}\n")

exploit = False
if min_v <= 3:
    print(" WARNUNG: Ein Wert ist extrem nah am Tod (Wall-Hugging am unteren Rand).")
    exploit = True
if max_v >= 45:
    print(" WARNUNG: Ein Wert explodiert fast (Wall-Hugging am oberen Rand).")
    exploit = True

if not exploit:
    print(" VERDICT: Echter kybernetischer Sieg! Der Agent hat das komplexe")
    print(" Gleichgewicht verstanden und hält die Gesellschaft in der Balance.")
else:
    print(" VERDICT: Exploit-Verdacht. Der Agent hat vermutlich ein Schlupfloch")
    print(" gefunden, bei dem er einen Wert gefährlich ausreizt, ohne sofort zu sterben.")
