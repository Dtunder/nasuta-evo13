# Oekolopoly Reinforcement Learning Survival Model (Evo 12)

This repository contains the complete package for **Ökolopoly Evo 12**, representing a **true cybernetic victory** in Reinforcement Learning on highly non-linear coupled systems. Using a **Spread + Ceiling-Guard reward** (Evo 12.3), the MaskablePPO agent successfully mastered the game, surviving all 30 rounds in 10/10 seeds while keeping every sector clear of both the upper and lower limits.

Dieses Repository enthält das komplette Paket für **Ökolopoly Evo 12**. Ein **echter kybernetischer Sieg** im Reinforcement Learning! Durch den Einsatz des **Spread- + Ceiling-Guard-Rewards** (Evo 12.3) hat der MaskablePPO-Agent die Simulation bezwungen und überlebt 10/10 Seeds deterministisch bis Runde 30 — und hält dabei jeden Sektor 30 Runden lang sicher fern von oberer und unterer Wand.

---

## 🏆 The Breakthrough / Der Durchbruch

Earlier reward variants ran into local optima: a **quadratic population penalty** `-0.1*(pop-30)²` produced a *suicide-trap* (dying early paid off → Ø6 rounds), and a **centering / min-margin** reward plateaued in overpopulation (Ø6). A pure **Spread/Stability** reward survived all the way to round 21 but then died at the *upper* wall (Quality-of-Life tipping 29→30).
By adding a targeted **Ceiling-Guard** on top of the Spread reward (Evo 12.3), we penalised *only* that one killer — approaching the upper wall — without disturbing rounds 1–20. This forced the agent to keep the whole society in the mid-corridor and survive the endgame. 

Within **1,000,000 steps**, the model achieved a **100% win-rate (30/30 rounds)** across all test seeds.

---

## 📊 Final Evaluation Metrics / Ergebnisse

### 10-Seed Deterministic Summary

| Seed | Rounds Survived | Stability Score | Death Cause |
|------|-----------------|-----------------|-------------|
| 0    | 30              | 1.0             | survived    |
| 1    | 30              | 1.0             | survived    |
| 2    | 30              | 1.0             | survived    |
| 3    | 30              | 1.0             | survived    |
| 4    | 30              | 1.0             | survived    |
| 5    | 30              | 1.0             | survived    |
| 6    | 30              | 1.0             | survived    |
| 7    | 30              | 1.0             | survived    |
| 8    | 30              | 1.0             | survived    |
| 9    | 30              | 1.0             | survived    |

**Average Rounds:** 30.00 / 30  
**Audit Verdict:** Echter kybernetischer Sieg (No exploits/wall-hugging detected!)  
*   **Max State Value at Round 30:** 39 (limit is 48)
*   **Min State Value at Round 30:** 10 (limit is 3)

> **Reading the Stability Score:** it is `30 − (max − min)` over the 8 *raw* sector
> values, so it ranges up to 30. A value of **1.0 does not mean "unstable"** — a healthy,
> sustainable society legitimately holds its sectors at *different* levels (e.g. high
> education, moderate population), so a wide max−min is expected. The real success
> metric is **survival: 30/30 rounds with no sector hitting a wall.** This score must
> **not** be used to rank methods (early death freezes a tight state → misleadingly
> high score) — see `_BENCHMARK_VERGLEICH.md`.

---

## 🧪 Spread + Ceiling-Guard Reward (Evo 12.3 — the actual winner)

> The `survival_env.py` in this package implements exactly this reward. An earlier
> version of this README described a quadratic *Danger-Zone Penalty* — that was a
> **failed** variant (suicide-trap, Ø6), **not** the winning reward. See `_EVO12_FACTS.md`.

```python
# Normalised core variables v = clip((V[0:8]-Vmin)/(Vmax-Vmin), 0, 1)
shaped_reward = 1.0                              # base survival reward / step
shaped_reward += 0.05 * info.get('balance (always)', 0.0)

# Spread / Stability — keeps all sectors together in the mid-corridor (THE driver)
spread = 1.0 - (v.max() - v.min())
shaped_reward += 3.0 * spread

# Ceiling-Guard — penalises ONLY approaching the upper wall (the lone Oe21 killer)
ceiling = np.maximum(0.0, v - 0.80)
shaped_reward -= 8.0 * ceiling.sum()

if is_done:
    shaped_reward += 50.0 if round_reached >= 30 else -50.0  # win / death
```

---

## 🚀 How to Run & Verify / Ausführung & Verifikation

### Setup
```bash
pip install sb3-contrib==2.3.0 stable-baselines3==2.3.0 gymnasium==0.29.1 pandas openpyxl
```

### 1. Perform 10-Seed Summary Evaluation
```bash
python evaluate_1M.py
```

### 2. Run Detailed Forensic Audit (Seed 42 Round-by-Round Log)
```bash
python audit_1M.py
```

---

## 📁 Repository Structure / Aufbau des Pakets

*   `oekolopoly_evo12_balanced_1M_steps.zip` - The final trained neural network (PPO agent)
*   `survival_env.py` - The customized gymnasium wrapper with the Spread + Ceiling-Guard reward
*   `_EVO12_FACTS.md` - Canonical single-source-of-truth for all numbers, methods & reward formulas
*   `_HYPERPARAMETER_RECHTFERTIGUNG.md` - Honest justification of the reward weights
*   `src/` - The core engine of Ökolopoly (differential equations & state updates)
*   `evaluate_1M.py` - Benchmark script for the 10 seeds
*   `audit_1M.py` - Round-by-round auditing tool