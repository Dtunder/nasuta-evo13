import os
import gymnasium as gym
import numpy as np
from oeko_core.envs.oeko_env import OekoEnv
from wrappers import OekoActionBuilderWrapper
from sb3_contrib.common.wrappers import ActionMasker

# ============================================================================
# EVO 13 - Umschaltbarer Reward (fuer Paper-konforme Datensammlung)
# ----------------------------------------------------------------------------
#  REWARD_MODE (env var EVO13_REWARD_MODE oder make_survival_env(mode=...)):
#    'survival'  -> Evo12-Gewinner: Spread + Ceiling-Guard  (Ziel: R30 ueberleben)
#    'perround'  -> Paper Engelhardt et al.: Rc=0.5/Step + B am Ende (Ziel: hohes B)
#    'balance'   -> Paper sparse: nur B am Ende (Eq.1)       (Ziel: reines B)
#  Balance B nach Paper Eq.1:  B = 10*[p + 3*D(q)] / (r+3)  fuer 10<=r<=30, sonst 0
#  (im Code als info['balance (always)'] bereitgestellt, hier mit r-Gate)
# ============================================================================

PERROUND_RC = float(os.environ.get("EVO13_PERROUND_RC", "0.5"))


def _balance_eq1(info, round_reached):
    """Paper Eq.1: B nur gueltig wenn 10<=r<=30, sonst 0."""
    b = float(info.get('balance (always)', 0.0))
    return b if 10 <= round_reached <= 30 else 0.0


class OekoSurvivalWrapper(gym.Wrapper):
    """Reward-Wrapper mit 3 umschaltbaren Modi (siehe Kopf der Datei)."""

    def __init__(self, env, mode="survival"):
        super().__init__(env)
        self.mode = mode

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        unwrapped = self.env.unwrapped
        is_done = terminated or truncated or getattr(unwrapped, 'done', False)
        round_reached = int(unwrapped.V[unwrapped.ROUND])

        if self.mode == "perround":
            # Paper PerRound: konstanter Bonus pro Step + B am Ende
            shaped_reward = PERROUND_RC
            if is_done:
                shaped_reward += _balance_eq1(info, round_reached)

        elif self.mode == "balance":
            # Paper sparse: nur finaler B (Eq.1)
            shaped_reward = 0.0
            if is_done:
                shaped_reward = _balance_eq1(info, round_reached)

        elif self.mode == "marathon":
            # Evo13-Aggressiv: Survival-Shaping + B-End-Bonus NUR bei R30.
            # Der B-Bonus kommt ausschliesslich bei Erreichen von R30 -> es gibt
            # keinen Anreiz, frueh mit hohem B zu sterben (killt die Sprinter-
            # Strategie). Gedacht fuer hoeheres gamma (0.999) + ent_coef (0.02).
            shaped_reward = 1.0
            v_core = unwrapped.V[0:8].astype(np.float64)
            vmin = unwrapped.Vmin[0:8]; vmax = unwrapped.Vmax[0:8]
            v_norm = np.clip((v_core - vmin) / (vmax - vmin), 0.0, 1.0)
            spread = 1.0 - (float(np.max(v_norm)) - float(np.min(v_norm)))
            shaped_reward += 3.0 * spread
            ceiling = np.maximum(0.0, v_norm - 0.80)
            shaped_reward -= 8.0 * float(np.sum(ceiling))
            if is_done:
                if round_reached >= 30:
                    shaped_reward += 50.0 + 25.0 * _balance_eq1(info, round_reached)
                else:
                    shaped_reward += -50.0

        else:  # "survival" -- Evo12-Gewinner (Spread + Ceiling-Guard)
            shaped_reward = 1.0
            balance_always = info.get('balance (always)', 0.0)
            shaped_reward += 0.05 * balance_always
            v_core = unwrapped.V[0:8].astype(np.float64)
            vmin = unwrapped.Vmin[0:8]; vmax = unwrapped.Vmax[0:8]
            v_norm = np.clip((v_core - vmin) / (vmax - vmin), 0.0, 1.0)
            spread = 1.0 - (float(np.max(v_norm)) - float(np.min(v_norm)))
            shaped_reward += 3.0 * spread
            ceiling = np.maximum(0.0, v_norm - 0.80)
            shaped_reward -= 8.0 * float(np.sum(ceiling))
            if is_done:
                shaped_reward += 50.0 if round_reached >= 30 else -50.0

        # Metriken fuer den Logging-Callback durchreichen (Paper-Metriken)
        info['eval_balance_B'] = _balance_eq1(info, round_reached)
        info['eval_rounds_r'] = round_reached

        return obs, shaped_reward, terminated, truncated, info

    def action_masks(self):
        return self.env.valid_action_mask()


def make_survival_env(mode=None):
    if mode is None:
        mode = os.environ.get("EVO13_REWARD_MODE", "survival")
    base_env = OekoEnv(render_mode=None)
    wrapped_env = OekoActionBuilderWrapper(base_env)
    return OekoSurvivalWrapper(wrapped_env, mode=mode)
