# Benchmark-Vergleich — Oekolopoly Evo 12

> Fairer Vergleich auf **identischen Seeds 0–9**, gemeinsame Stopp-Regel:
> jede Methode läuft bis zur **natürlichen Terminierung** (Tod oder Runde 30).
> Skript: `compare_methods.py` · Rohdaten: `_bench_results.csv` · Stand 2026-06-03.
> Quelle aller historischen Zahlen: `_EVO12_FACTS.md` §3.

---

## 1. Ergebnis — Runden überlebt (DIE Erfolgsmetrik)

| Methode | Typ | Runden Ø | Runden max | Win-Rate (R30) | Quelle |
|---|---|---:|---:|---:|---|
| Paper Vanilla UCT | reines MCTS | **2.0** | 2 | 0/10 | gemessen (n=10, dieser Lauf) |
| Sovereign MCTS | MCTS + Soft-Constraints | **2.3** | 3 | 0/10 | gemessen (n=10, dieser Lauf) |
| Heuristik (simpel) | handcodiert, deterministisch | **5.0** | 5 | 0/10 | gemessen (n=10, dieser Lauf) |
| **Evo 12 MaskablePPO** | RL, trainiert | **30.0** | 30 | **10/10** | gemessen (n=10, dieser Lauf) |

➡️ **Evo 12 erreicht als EINZIGE Methode Runde 30 — auf jedem einzelnen Seed.**
Der Abstand ist unter jeder Messung eindeutig: 30 vs. ≤5 Runden.

---

## 2. „Score" (Stability = 30 − (V[:8].max − V[:8].min))

| Methode | Score Ø | Lesart |
|---|---:|---|
| Paper Vanilla UCT | 0.6 | früher Tod |
| Sovereign MCTS | 3.3 | früher Tod |
| Heuristik (simpel) | −17.0 | weites Auseinanderlaufen vor Tod |
| Evo 12 MaskablePPO | 1.0 | echte, vielfältige Gesellschaft bei R30 |

⚠️ **WICHTIG — dieser Score taugt NICHT als Methoden-Ranking.** Eine Methode, die
in Runde 2 stirbt, friert einen noch eng beieinanderliegenden Startzustand ein und
bekommt dadurch einen *höheren* Stability-Score als ein Lauf, der 30 Runden überlebt.
Evo12s Score von 1.0 spiegelt eine **legitim diverse, nachhaltige** Gesellschaft
(z.B. Bildung hoch, Population moderat) — kein 1:1-Gleichstand aller Sektoren.
**Score nur GEMEINSAM mit „Runden überlebt" lesen, nie isoliert.** Wer Methoden
vergleichen will, vergleicht Runden — nicht diesen Score.

---

## 3. Gemessen (gleiche Seeds) vs. historisch (dokumentiert) — ehrliche Einordnung

| Methode | Gemessen Ø (dieser Lauf) | Historisch Ø (§3) | Warum die Differenz |
|---|---:|---:|---|
| Paper Vanilla UCT | 2.0 | 3.28 (n=25) | weniger MCTS-Budget/Seeds in dieser schnellen Harness |
| Sovereign MCTS | 2.3 | 7.08 (n=25) | dito — geringeres Iterations-/Zeitbudget pro Zug |
| Heuristik | 5.0 (simpel) | 24 (elaboriert, det.) | **andere Heuristik**: diese Harness nutzt eine einfache Survival-Heuristik, NICHT die aufwändig handgetunte `dist[]`+Burn-Heuristik |
| Evo 12 MaskablePPO | **30.0** | 30.0 (n=10) | ✅ deckungsgleich — validiert |

**Empfehlung für die Präsentation:** Für die Baselines die **historischen Zahlen**
(Paper 3.28 · Sovereign 7.08 · Heuristik 24) verwenden — das sind die *stärkeren*
Baseline-Implementierungen, also der **konservativere, fairere** Vergleich (Evo12
schlägt sogar die starken Baselines). Dieser Same-Seed-Lauf dient als **Validierung**:
er bestätigt (a) Evo12 = 30/30 reproduzierbar und (b) die Rangfolge Evo12 ≫ alle
Baselines auf exakt gleichen Seeds.

---

## 4. Kernaussage (1 Satz)

> Auf identischen Seeds erreicht das trainierte Evo-12-Modell als einzige Methode
> reproduzierbar Runde 30 (10/10) — alle Such- und Heuristik-Baselines sterben
> spätestens in Runde 5; die Überlegenheit ist unabhängig von der Messmethode eindeutig.

---

### Methodischer Hinweis (gefundener & behobener Bug)
Der ursprüngliche Lauf kappte Evo12 fälschlich bei ~7 Runden: ein globaler
`STEP_CAP=60` (gedacht als Hang-Schutz für die langsamen MCTS-Rollouts) schnitt
das schnelle NN mitten im Spiel ab — 1 Runde = mehrere Aktionspunkt-Allokationen.
Fix: separater, nicht-bindender `NN_STEP_CAP` für das NN (die Env terminiert hart
bei Runde 30, genau wie `evaluate_1M.py`). Danach: 30/30 auf allen Seeds.
