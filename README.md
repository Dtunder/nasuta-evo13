# Oekolopoly Reinforcement Learning Survival & Marathon Model (Evo 13)

This repository contains the complete package for **Ökolopoly Evo 13**, representing a **true cybernetic breakthrough** in Reinforcement Learning on highly non-linear coupled systems. Building upon the Spread + Ceiling-Guard architecture of Evo 12, Evo 13 successfully replicates and compares the three training curves (balance $B$, rounds $r$, return) across multiple seeds, achieving the absolute mathematical optimum in Year 30.

Dieses Repository enthält das komplette Paket für **Ökolopoly Evo 13**. Durch das hochfrequente Logging (alle 2.000 Timesteps) und umschaltbare Reward-Modi ist es gelungen, den systemischen Trade-off der Simulation exakt zu vermessen und auf mehreren Seeds das theoretische Optimum von $B = 15,76$ bei $r = 30$ nachzuweisen.

---

## 🏆 The Breakthrough & Top Performance / Der Durchbruch und Spitzenleistung

While baseline models collapsed early due to local optima, the **Evo 13 RecurrentPPO (LSTM)** agent coupled with the **Sovereign Guardian** successfully reached **Year 30 with a perfect balance score of 15.76** across multiple evaluation seeds.

### Multi-Seed Verification (Year 30 Peak Balance)

The training logs and model checkpoints of the marathon seeds have been fully integrated into this repository:

| Seed | Source Zip File | Target year | Balance Score B | Status |
|------|-----------------|-------------|-----------------|--------|
| **17** | `training_log_survival_seed17.csv` | 30 | **15.7576** | survived (Optimum) |
| **31** | `ergebnisse_marathon_seed_31.zip` | 30 | **15.7576** | survived (Optimum) |
| **32** | `ergebnisse_marathon_seed_32.zip` | 30 | **15.4545** | survived (Close Peak) |
| **33** | `ergebnisse_marathon_seed_33.zip` | 30 | **15.7576** | survived (Optimum) |
| **34** | `ergebnisse_marathon_seed_34.zip` | 30 | **15.7576** | survived (Optimum) |
| **42** | `ergebnisse_marathon_seeds_41_42.zip` | 30 | **15.7576** | survived (Optimum) |

> [!IMPORTANT]
> The score of **15.76** is the absolute mathematical limit at Year 30 under Frederic Vester's balance equation: $B = \frac{10 \times [p + 3 \times D(q)]}{r + 3}$.
> At $r = 30$, this resolves to $\frac{10 \times [13 + 3 \times 13]}{33} = \frac{520}{33} = 15.7576$.

---

## 🧪 Reward Modes / Die drei Reward-Modi

The environment `survival_env.py` supports three umschaltbare reward modes (selectable via `--mode` or env `EVO13_REWARD_MODE`):

1.  **`survival`**: Spread + Ceiling-Guard (Evo 12.3 winner). Focuses on **surviving to round 30**. (Yields $r=30$, $B \approx 12-15.76$).
2.  **`perround`**: Paper baseline (`Rc=0.5` per step + $B$ at terminal state). Focuses on **higher balance**. (Yields $r \approx 15$, $B \approx 28$).
3.  **`balance`**: Paper Eq.1 sparse reward (only final $B$ is returned). (Yields $r \approx 15$, high $B$).

---

## 📁 Repository Structure / Aufbau des Pakets

*   📂 [logs/](file:///G:/Meine%20Ablage/Antigravity/Oekolopoly/release_evo13/logs) - Extracted training log CSVs for all seeds (17, 18, 19, 20, 21, 31, 32, 33, 34, 41, 42).
*   📂 [checkpoints/](file:///G:/Meine%20Ablage/Antigravity/Oekolopoly/release_evo13/checkpoints) - Model weights (`_BEST.zip` and `_LAST.zip`) for marathon runs.
*   📂 [src/](file:///G:/Meine%20Ablage/Antigravity/Oekolopoly/release_evo13/src) - Core engine of Ökolopoly (differential equations & state updates).
*   📄 [EVO13_1576_SCORE_REPORT.md](file:///G:/Meine%20Ablage/Antigravity/Oekolopoly/release_evo13/EVO13_1576_SCORE_REPORT.md) - Deep technical analysis of the optimal 15.76 run.
*   📄 `survival_env.py` - Custom gymnasium environment wrapper with umschaltbare reward modes.
*   📄 `paper_logging_callback.py` - High-frequency training log callback (saves B/r/return every 2,000 steps).
*   📄 `train_paper_data.py` - Local CPU multi-seed training harness.
*   📄 `colab_evo13_RUN.py` - Colab GPU acceleration script.
*   📄 `plot_paper_3panel.py` - Paper-style 3-panel plotting utility (using Savitzky-Golay filtering).

---

## 🚀 Execution & Verification / Ausführung & Verifikation

### Setup
```bash
pip install sb3-contrib==2.3.0 stable-baselines3==2.3.0 gymnasium==0.29.1 pandas openpyxl matplotlib scipy
```

### Run Local Training
```powershell
python train_paper_data.py --mode survival --seeds 17,18,19,20,21 --timesteps 800000
```

### Generate Curve Plots
```powershell
python plot_paper_3panel.py --mode survival
```