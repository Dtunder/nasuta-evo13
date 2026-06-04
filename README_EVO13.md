# EVO 13 — Paper-konforme Datensammlung (Engelhardt et al. Fig.2)

> **Ziel:** Die drei Trainingskurven des Papers (**balance B · rounds r · return**
> über Trainings-Timesteps, mehrere Seeds) für unsere Reward-Varianten erzeugen —
> damit wir uns direkt mit Engelhardt et al. vergleichen können.
>
> **Basis:** Vollkopie von `release_evo12_work`. Original `release_evo12` **und**
> der evo12-Arbeitsordner bleiben unangetastet. Alle Änderungen leben hier.

---

## Was neu ist gegenüber Evo 12

| Datei | Zweck |
|---|---|
| `survival_env.py` | **Reward jetzt umschaltbar** (3 Modi, siehe unten) |
| `paper_logging_callback.py` | Loggt B / r / return **dicht** (alle 2000 Steps) während des Trainings |
| `train_paper_data.py` | Multi-Seed-Training (lokal), erzeugt `logs/training_log_*.csv` |
| `colab_evo13_RUN.py` | Gleiche Pipeline für **Colab-GPU** (alle Modi × Seeds) |
| `plot_paper_3panel.py` | 3-Panel-Plot im Paper-Stil (Savitzky-Golay, 1 Farbe/Seed) |

Der ursprüngliche `LocalProgressCallback` (Evo12) loggte nur alle **250 000** Steps —
zu grob für Kurven. Hier: alle **2 000** Steps → glatte Trainingskurven.

---

## Die drei Reward-Modi

Umschaltbar per `--mode` (oder env `EVO13_REWARD_MODE`):

| Modus | Reward | Ziel | erwartetes Ergebnis |
|---|---|---|---|
| `survival` | Spread + Ceiling-Guard (Evo12-Gewinner) | **R30 überleben** | r=30, B≈12 |
| `perround` | Paper: `Rc=0.5`/Step + B am Ende | **hohes B** | r≈15, B≈28 |
| `balance` | Paper: nur finaler B (sparse, Eq.1) | reines B | r≈15, B hoch |

**Balance B (Paper Eq.1):** `B = 10·[p + 3·D(q)] / (r+3)` für `10 ≤ r ≤ 30`, sonst 0.
Die Spielregel definiert **B > 20 als „exceptionally good"** — 20 ist *nicht* das Maximum.

---

## Ablauf

### Variante A — Lokal (CPU, langsamer)
```powershell
# 1 Modus, 5 Seeds, 800k Steps  (~30 min/Seed auf CPU)
python train_paper_data.py --mode survival --seeds 17,18,19,20,21 --timesteps 800000

# Plot der 3 Panels
python plot_paper_3panel.py --mode survival
```

### Variante B — Colab (GPU, empfohlen)
1. Ordner `release_evo13` nach Google Drive hochladen
   (`MyDrive/nasuta_evo/release_evo13`).
2. Neues Colab-Notebook, **Laufzeit → GPU (T4)**.
3. Inhalt von `colab_evo13_RUN.py` in eine Zelle kopieren, ausführen.
4. Danach `logs/` + `checkpoints/` von Drive zurückholen, lokal plotten:
   ```powershell
   python plot_paper_3panel.py --mode survival
   python plot_paper_3panel.py --mode perround
   ```

> **Kosten:** reines lokales/Colab-PyTorch-Training — **keine Anthropic-/Gemini-Quota.**
> Nur Rechenzeit. 5 Seeds × 800k ≈ 2–3 h CPU bzw. deutlich weniger auf GPU.

---

## Output

- `logs/training_log_{mode}_seed{N}.csv` — Spalten: `timestep, balance_B, rounds_r, return`
- `checkpoints/evo13_{mode}_seed{N}.zip` — trainiertes Modell pro Seed
- `_assets/paper_3panel_{mode}.png` — die 3 Paper-Panels

---

## Für die Präsentation: der Zielkonflikt

Das Paper sagt selbst (Sect. 6.4): *„a longer lasting episode would not improve
(or even diminish) B."* Weil **r im Nenner** steht, schließen sich **max-B** und
**max-Überleben** aus:

- **Paper-Strategie** (`perround`/`balance`): früh stoppen (~R15) → **B ≈ 28**
- **Evo12/13-Strategie** (`survival`): bis **R30** überleben → B ≈ 12, aber **100 % Survival**

Mit `survival` **und** `perround` nebeneinander zeigt ihr beide Enden des Trade-offs
mit **euren eigenen, sauber geloggten** Trainingskurven.
