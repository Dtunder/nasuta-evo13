# Hyperparameter-Rechtfertigung — Evo 12.3 Reward-Gewichte

> Antwort auf Sonus Frage: *„Garantiere, dass deine Werte die optimalen sind —
> oder schreibe ehrlich: Wir haben mit dieser Methode die besten Ergebnisse gefunden."*
> Linie (vom User bestätigt): **ehrlich dokumentieren, kein neues Training.**

---

## 1. Die Werte

| Hyperparameter | Wert | Rolle |
|---|---|---|
| Spread-Gewicht | `+3.0` | Variablen zusammenhalten (Stabilität) |
| Ceiling-Guard-Gewicht | `-8.0` | Überkippen über die obere Wand bestrafen |
| Ceiling-Schwelle | `0.80` | ab wann die obere Wand „gefährlich" wird (oberstes 20 %-Band) |
| Base-Reward | `+1.0`/Step | Überleben |
| Balance-Nudge | `+0.05` | leichte Zusatz-Stabilisierung |
| Terminal | `±50` | Sieg (R≥30) / Tod |

---

## 2. Ehrliche Aussage (offizielle Formulierung)

> **Wir können nicht garantieren, dass diese Werte das globale Optimum sind.**
> Wir haben kein vollständiges Hyperparameter-Grid trainiert (Rechenkosten).
> Stattdessen haben wir die Reward-**Struktur** systematisch durch Iteration
> entwickelt und mit der finalen Methode (**Spread + Ceiling-Guard**) die besten
> Ergebnisse aller getesteten Varianten erreicht: **Ø 30/30 Runden, 100 % Win-Rate**
> über 10 Seeds nach 1 Mio. Trainings-Steps.

Diese Formulierung ist auf jeder Folie / in jedem Bericht zulässig und ehrlich.

---

## 3. Warum das überzeugend ist — die Struktur wurde empirisch validiert

Nicht die exakten Zahlen, sondern die **Reward-Struktur** ist das Ergebnis
systematischer Ablation. Jede Alternative wurde getestet und ist messbar gescheitert:

| Reward-Variante | Idee | Ergebnis | Warum gescheitert |
|---|---|---|---|
| Quadratische Pop-Strafe `-0.1*(pop-30)²` | Überpopulation hart bestrafen | **Ø 6** | **Suicide-Trap**: früher Tod minimiert die kumulierte Strafe → Agent stirbt absichtlich früh |
| Centering / Min-Margin | Abstand zur Mitte maximieren | **Ø 6** | Überpopulations-Plateau, kein Lernsignal für Endgame |
| Spread **ohne** Ceiling-Guard | nur Variablen zusammenhalten | **Ø 21** | überlebt lange, kippt aber an der **oberen** Wand (QoL 29→30) |
| **Spread + Ceiling-Guard** (final) | Spread + obere Wand schützen | **Ø 30 / 100 %** | ✅ löst genau den Oe21-Killer |

**Kernargument:** Die Gewichte sind nicht willkürlich — `-8.0` (Ceiling) ist
bewusst stärker als `+3.0` (Spread), damit der Agent in den letzten Runden die
Wand-Vermeidung über die reine Spread-Maximierung stellt. Die `0.80`-Schwelle ist
so gesetzt, dass der Guard **nur** im obersten 20 %-Band greift → Runden 1–20
bleiben unberührt, nur das Endgame wird abgesichert.

---

## 4. Was ein vollständiger Optimalitäts-Beweis bräuchte (falls je gefragt)

- Grid über `Spread ∈ {1,3,5}` × `Ceiling ∈ {-4,-8,-12}` × `Schwelle ∈ {0.7,0.8,0.9}`
  = 27 Kombinationen × je ~1 Mio. Steps × mehrere Seeds.
- Geschätzt: **Tage** GPU/CPU-Zeit. Aktuell **nicht** durchgeführt (bewusste Quota-Entscheidung).
- Sensitivität: erwartbar robust, da die Struktur (Guard > Spread, enges oberes Band)
  den Mechanismus erklärt — die exakten Zahlen sind sekundär.

---

## 5. Sprechzettel für die Präsentation (1 Satz)

> „Die Reward-Gewichte sind empirisch durch Ablation gefunden — wir garantieren
> kein globales Optimum, aber jede getestete Alternative war messbar schlechter,
> und diese Methode erreicht als einzige stabil 30/30 Runden."

Quelle aller Zahlen: `_EVO12_FACTS.md`.
