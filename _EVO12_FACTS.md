# EVO 12 — Kanonische Faktenbasis (Single Source of Truth)

> **Zweck:** EINE Quelle für alle Zahlen, Methoden-Namen und Reward-Formeln.
> Benchmark-Skript, HP-Doku, README und Präsentation MÜSSEN gegen diese Datei
> geprüft werden. Hintergrund: In früheren Decks (`_v2`) wurde versehentlich der
> *gescheiterte* Reward als Gewinner beschrieben — das darf nicht wieder passieren.
>
> Stand: 2026-06-03 · Klon von `release_evo12` · Original unverändert.

---

## 1. Gewinner-Reward — Evo 12.3 (VERIFIZIERT gegen `survival_env.py`)

Normalisierte Variablen `v = clip((V[0:8]-Vmin)/(Vmax-Vmin), 0, 1)` über die 8 Kern-Variablen.

| Term | Formel | Zweck |
|---|---|---|
| Base survival | `+1.0` pro Step | Überleben belohnen |
| Balance-Nudge | `+0.05 * info['balance (always)']` | leichte Stabilisierung |
| **Spread/Stability** | `+3.0 * (1 - (v.max() - v.min()))` | hält alle Sektoren im Mittelkorridor zusammen — DER Treiber bis Oe21 |
| **Ceiling-Guard** | `-8.0 * Σ max(0, v - 0.80)` | bestraft NUR die obere Wand (QoL kippt 29→30) — der einzige Killer des Oe21-Laufs |
| Terminal | `+50` bei Runde ≥30, sonst `-50` | Sieg/Tod |

**Modell:** `oekolopoly_evo12_balanced_1M_steps.zip` · **MaskablePPO** · 1.000.000 Steps.
**Ergebnis (n=10 Seeds, deterministisch):** Ø **30.00** Runden · **10/10** survived · **100 %** Win-Rate · Stability 1.0 *(Roh-Metrik 0–30; 1.0 ≠ instabil — eine gesunde Gesellschaft hält Sektoren legitim auf verschiedenen Niveaus; Erfolgsmetrik ist Überleben, siehe §3-Caveat)*.

---

## 2. Dokumentierte FEHLSCHLÄGE — NIE als Gewinner darstellen

> Empirie schlägt Theorie. Diese Varianten wurden getestet und sind gescheitert.

| Variante | Formel | Ergebnis | Todesart |
|---|---|---|---|
| **Quadratische Pop-Strafe** | `-0.1 * (pop-30)²` | Ø **6** | **Suicide-Trap** (früh sterben lohnt sich) |
| **Centering / Min-Margin** | Abstand-zur-Mitte-Reward | Ø **6** | Überpopulations-Plateau |

⚠️ **ACHTUNG README/Doku-Bug:** Die `README.md` des Originals beschreibt die
*quadratische Danger-Zone-Penalty* (`-0.1*(pop-30)²`) als Gewinner-Methode.
Das ist FALSCH — das war der gescheiterte Suicide-Trap (Ø6). Der echte Gewinner
ist **Spread + Ceiling-Guard** (siehe §1). → In Klon-README korrigiert.

**Phasenübergang (für Präsentation):** Plateau bei Runde 14 bis ~750k Steps,
Durchbruch 14→30 zwischen 750k–1M Steps.

---

## 3. Vergleichs-Methoden (für den fairen Benchmark)

Vergleichsachse (User-Entscheidung): **beide Tabellen nebeneinander** —
(a) überlebte Runden, (b) Score = Stability `30 - (V[:8].max() - V[:8].min())`,
auf **identischen Seeds**.

| Methode | Typ | Runden (historisch) | Quelle / Konfidenz |
|---|---|---|---|
| **Paper Vanilla UCT** | reines MCTS | Ø 3.28 (max 7) | Multi-Seed n=25, Evo10-Logs — **mittel** |
| **Sovereign MCTS** | MCTS + Soft-Constraints | Ø 7.08 (max 10) | Multi-Seed n=25, Evo10-Logs — **mittel** |
| **Heuristik** | handcodiert, deterministisch | 24 | deterministisch — **hoch** |
| **Evo 12 (MaskablePPO)** | RL, trainiert | Ø 30.00 (100 %) | n=10, `evaluate_1M.py` — **hoch** |

⚠️ **Heuristik-Warnung:** Die alte „Evo7 = 30 Runden 100 %"-Zahl war eine
handcodierte Mogel-Heuristik (`xai_runner.py`: `dist[]` + Burn-Schleife), KEIN MCTS.
Niemals als Lern-Erfolg verkaufen. Die ehrliche Heuristik-Baseline = 24 (deterministisch).

> Historische Runden-Zahlen sind n=25 (Paper/Sovereign) bzw. n=10 (Evo12).
> Der neue Benchmark regeneriert wo möglich **gleiche-Seed**-Zahlen für beide Metriken.
> Wenn eine Methode hier nicht reproduzierbar läuft → historische Zahl + Quelle ausweisen, NICHT erfinden.

**Gemessener Same-Seed-Lauf (2026-06-03, seeds 0–9, `compare_methods.py`):**
Evo12 = **30.0 (10/10)** ✅ validiert · Heuristik(simpel) 5.0 · Sovereign 2.3 · Paper 2.0.
Gemessene Baselines liegen UNTER den historischen (schwächere Impl./geringeres MCTS-Budget) —
für die Präsentation die stärkeren historischen Baselines nutzen (konservativer). Details: `_BENCHMARK_VERGLEICH.md`.

⚠️ **Score-Caveat:** Stability `30-(max-min)` ist KEIN Methoden-Ranking — früher Tod friert einen
eng geclusterten Zustand ein und gibt fälschlich höheren Score. Immer mit „Runden überlebt" zusammen lesen.

---

## 4. Hyperparameter-Rechtfertigung (Linie: ehrlich, kein neues Training)

Die Reward-Gewichte (Spread `+3.0`, Ceiling `-8.0`, Schwelle `0.80`) wurden
**empirisch iterativ** gefunden, nicht durch ein vollständiges Grid bewiesen.

**Offizielle Formulierung (von Sonu freigegeben):**
> „Wir können nicht garantieren, dass dies die global-optimalen Werte sind.
> Wir haben mit dieser Methode (Spread + Ceiling-Guard) die besten Ergebnisse
> unserer getesteten Varianten gefunden — Ø 30/30 Runden bei 100 % Win-Rate."

Beleg = Varianten-Tabelle in §2 (was scheiterte und warum) + Phasenübergang in §1.
Details: `_HYPERPARAMETER_RECHTFERTIGUNG.md`.

---

## 5. Harte Constraints für alle Arbeiten in diesem Klon

- Nur in `release_evo12_work` arbeiten — **Original `release_evo12` NIE anfassen.**
- **KEIN neues Training** (Quota). Nur vorhandenes Modell evaluieren / MCTS rollouts.
- MCTS-Rollouts mit **Step-Cap** absichern (bekannter Rollout-Hang) — Action 0 (Runde beenden) ist immer legaler Fallback.
- Keine Zahl erfinden: jede Zahl bekommt Quelle + Konfidenz.
