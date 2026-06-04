import os
import sys
import numpy as np
import pandas as pd
import torch

# Registriere lokale Pfade aus dem extrahierten Temp-Zip
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

checkpoint_path = os.path.join(base_dir, "oekolopoly_evo12_balanced_1M_steps.zip")

print(">>> Lade 500k Checkpoint...")
model = MaskablePPO.load(checkpoint_path, device="cpu")

print("\n==================================================")
print("       EVALUATION 500K STEPS (10 SEEDS)")
print("==================================================")

def evaluate_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    e = make_survival_env()
    obs, _ = e.reset(seed=seed)
    done = False
    
    while not done:
        mask = get_action_masks(e)
        action, _ = model.predict(obs, action_masks=mask, deterministic=True)
        obs, r, term, trunc, info = e.step(action)
        done = term or trunc
        
    final_V = e.unwrapped.V
    inner = e.unwrapped
    
    di = (getattr(inner, 'done_info', '') or '')
    dtl = getattr(inner, 'dtl', {})
    etl = getattr(inner, 'etl', {})
    too_high = etl.get(' too high. ') and di.endswith(etl.get(' too high. '))
    
    def _starts(d, key):
        prefix = d.get(key)
        return bool(prefix) and di.startswith(prefix)

    if di.startswith('Maximum number of rounds'):
        death_cause = 'survived'
    elif _starts(dtl, 'Politics'):
        death_cause = 'politics_collapse'
    elif _starts(dtl, 'EnvirDamage'):
        death_cause = 'env_collapse'
    elif _starts(dtl, 'Population'):
        death_cause = 'overpopulation' if too_high else 'extinction'
    elif _starts(dtl, 'ReproRate'):
        death_cause = 'reprorate_collapse'
    elif _starts(dtl, 'QualityOfLife'):
        death_cause = 'quality_of_life_collapse'
    elif _starts(dtl, 'Enlightenment'):
        death_cause = 'education_collapse'
    elif _starts(dtl, 'Production'):
        death_cause = 'production_collapse'
    elif _starts(dtl, 'Redevelop'):
        death_cause = 'sanitation_collapse'
    elif _starts(etl, 'NumAPointsTooLow') or _starts(etl, 'NumAPointsTooHigh'):
        death_cause = 'ap_out_of_range'
    else:
        death_cause = di if di else 'unknown'
        
    return {
        'seed': seed,
        'rounds_survived': int(final_V[8]),
        'stability': float(30 - (np.max(final_V[:8]) - np.min(final_V[:8]))),
        'death_cause': death_cause
    }

results = [evaluate_seed(s) for s in range(10)]
df = pd.DataFrame(results)
avg_rounds = df['rounds_survived'].mean()
max_rounds = df['rounds_survived'].max()

print(df.to_string(index=False))
print(f"\n=== AVG ROUNDS: {avg_rounds:.2f} | MAX ROUNDS: {max_rounds} ===")
