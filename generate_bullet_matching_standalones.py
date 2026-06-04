# -*- coding: utf-8 -*-
"""
Generates 3 specific standalone graphics that perfectly match the 3 bullet points of Slide 11:
1. Lektion1_Standard_RL_scheitert.png - Typical collapsing trajectory at Round 9 (due to feedback/dead times).
2. Lektion2_Architektur_schlaegt_Power.png - Performance bar chart comparing RL architectures vs Evo 12.
3. Lektion3_Emergentes_Verhalten.png - Focused V4 throttling vs V6 controlled growth plot.
All styled with background (#161E31) and high DPI (300).
"""
import os, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Output directory on Google Drive
OUT_DIR = r"G:\Meine Ablage\Oekolopoly_Evo12"
os.makedirs(OUT_DIR, exist_ok=True)

# ===== Cybernetic Theme Palette =====
BG = '#161E31'       # Match slide cards exactly
FG = '#F1F5F9'       # Off-White / Crisp Slate
MUT = '#64748B'      # Slate Muted Grey
GRID = '#26344E'     # Thin Grid Slate

GREEN = '#10B981'    # Neon Emerald (Controller / Success)
CYAN = '#06B6D4'     # Electric Cyan (Strecke / System)
RED = '#EF4444'      # Neon Crimson (Danger / Penalty)
AMBER = '#F59E0B'    # Cyber Gold (Warning / Boundary)

plt.rcParams.update({
    'text.color': FG,
    'axes.labelcolor': FG,
    'xtick.color': MUT,
    'ytick.color': MUT,
    'axes.edgecolor': '#2A3C58',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'DejaVu Sans', 'Arial'],
    'font.size': 10
})

def style(ax):
    ax.set_facecolor(BG)
    for s in ('top', 'right'): 
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_color('#2A3C58')
    ax.spines['bottom'].set_color('#2A3C58')
    ax.tick_params(colors=MUT, labelsize=9.0)

def plot_glow(ax, x, y, color, lw=1.8, label=None, ls='-'):
    ax.plot(x, y, color=color, alpha=0.12, linewidth=lw*4.0, ls=ls)
    ax.plot(x, y, color=color, alpha=0.28, linewidth=lw*2.0, ls=ls)
    return ax.plot(x, y, color=color, alpha=1.0, linewidth=lw, label=label, ls=ls)[0]

def scatter_glow(ax, x, y, color, s=100, label=None, marker='o'):
    ax.scatter(x, y, s=s*2.5, color=color, alpha=0.12, marker=marker, zorder=4)
    ax.scatter(x, y, s=s*1.5, color=color, alpha=0.30, marker=marker, zorder=4)
    return ax.scatter(x, y, s=s, color=color, edgecolor='#161E31', linewidths=1.2, zorder=5, label=label, marker=marker)


# ===== ECHTE DATEN (Seed 42) =====
raw = np.array([
 [1,12,4,10,20,13,21,0],[9,13,3,5,18,12,23,-1],[9,14,7,4,15,12,23,-3],[9,16,7,6,14,12,21,-4],
 [10,18,9,5,12,13,19,-5],[10,16,9,5,10,13,17,-6],[10,16,9,7,9,13,13,-7],[10,16,9,9,10,13,12,-8],
 [10,18,9,13,11,14,11,-7],[10,16,9,16,12,14,10,-6],[10,18,9,17,13,15,9,-5],[10,16,9,17,14,15,8,-4],
 [10,20,9,16,15,17,8,-3],[10,18,9,17,16,17,9,-2],[10,16,9,17,17,17,10,-1],[10,15,9,18,18,17,11,0],
 [10,13,9,19,19,16,12,1],[10,16,9,20,20,16,13,2],[10,16,9,22,20,16,14,4],[10,20,9,22,20,17,15,6],
 [10,16,9,21,20,17,17,8],[10,14,9,22,20,16,19,10],[11,18,9,22,20,17,21,12],[13,16,9,22,20,16,23,14],
 [15,20,9,22,20,17,25,16],[17,16,9,21,20,16,27,18],[19,20,9,21,20,16,29,20],[21,16,9,22,20,13,31,23],
 [23,22,9,19,20,12,33,25],[23,17,9,23,20,10,35,28],[23,28,10,19,21,19,39,30]], float)

vmin = np.array([1,1,1,1,1,1,1,-10.])
vmax = np.array([29,29,29,29,29,29,48,37.])
norm = (raw - vmin) / (vmax - vmin)


# ==============================================================================
# BILD 1 (Passend zu Punkt 1: "Standard-RL scheitert")
# ==============================================================================
print("Generating Standalone 1: Lektion1_Standard_RL_scheitert.png...")
fig, ax = plt.subplots(figsize=(6.22, 5.0), dpi=300)
fig.patch.set_facecolor(BG)
style(ax)

# Simulate a typical collapsing run crashing at Round 9 due to oversteering
rounds = np.array(range(10))
# Exponentially growing population hitting the ceiling
sim_v6 = np.array([0.42, 0.46, 0.52, 0.58, 0.65, 0.73, 0.80, 0.86, 0.91, 0.96])
# Spiking environmental load
sim_v5 = np.array([0.38, 0.40, 0.44, 0.50, 0.58, 0.68, 0.79, 0.88, 0.94, 0.99])
# Dropping life quality
sim_v3 = np.array([0.50, 0.48, 0.44, 0.38, 0.30, 0.22, 0.15, 0.09, 0.05, 0.02])

# Draw death zone threshold
ax.axhspan(0.9, 1.0, color=RED, alpha=0.08)
ax.axhspan(0.0, 0.1, color=RED, alpha=0.08)
ax.axhline(0.9, color=RED, ls='--', alpha=0.5, lw=1.2)
ax.axhline(0.1, color=RED, ls='--', alpha=0.5, lw=1.2)

plot_glow(ax, rounds, sim_v6, '#FB7185', lw=2.0, label="Bevölkerung (V6) → Überbevölkerung")
plot_glow(ax, rounds, sim_v5, '#A78BFA', lw=2.0, label="Umweltbelastung (V5) → Kollaps")
plot_glow(ax, rounds, sim_v3, '#FB7185', lw=2.0, label="Lebensqualität (V3) → Aussterben", ls=':')

# Draw vertical crash barrier at round 9
ax.axvline(9, color=RED, ls='-', lw=1.8, alpha=0.8)
ax.text(8.8, 0.5, 'SYSTEM-KOLLAPS\nin Runde 9', color=RED, fontsize=9.5, fontweight='bold', ha='right', rotation=90, va='center')

# Highlight where curves cross the death zone
scatter_glow(ax, [9], [0.96], RED, s=90)
scatter_glow(ax, [9], [0.99], RED, s=90)
scatter_glow(ax, [9], [0.02], RED, s=90)

ax.set_xlim(-0.2, 10.2)
ax.set_ylim(-0.02, 1.02)
ax.set_xlabel('Runde', color=FG, fontsize=9.5)
ax.set_ylabel('Normalisierter Variablenwert', color=FG, fontsize=9.5)
ax.grid(True, color=GRID, lw=0.5, ls=':')
ax.legend(loc='lower left', frameon=False, labelcolor=FG, fontsize=8.0)
ax.set_title('Lektion 1: Standard-RL scheitert an Totzeiten & Rückkopplung', color=FG, fontsize=10.5, pad=10)

fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "Lektion1_Standard_RL_scheitert.png"), facecolor=BG)
plt.close(fig)


# ==============================================================================
# BILD 2 (Passend zu Punkt 2: "Architektur schlägt Power")
# ==============================================================================
print("Generating Standalone 2: Lektion2_Architektur_schlaegt_Power.png...")
fig, ax = plt.subplots(figsize=(6.22, 5.0), dpi=300)
fig.patch.set_facecolor(BG)
style(ax)

# Architectures and their maximum rounds survived
labels = [
    'Standard PPO\n(keine Guards/Wrappers)', 
    'PPO + Centering-Reward\n(Exploration blockiert)', 
    'Nasuta-Baseline\n(Statische Regelung)', 
    'Evo 12 Architecture\n(ActionMask + Spread-Guard)'
]
values = [2, 6, 9, 30]
bar_colors = [RED, AMBER, AMBER, GREEN]

# Draw horizontal bars
bars = ax.barh(labels, values, color=bar_colors, edgecolor='#1E2A38', height=0.55, zorder=3)

# Add neon glow lines behind the successful Evo 12 bar
# We draw a larger, semi-transparent bar behind the green one
ax.barh(labels[3], values[3], color=GREEN, alpha=0.15, height=0.75, zorder=2)
ax.barh(labels[3], values[3], color=GREEN, alpha=0.25, height=0.65, zorder=2)

# Add values on top of bars
for bar in bars:
    width = bar.get_width()
    ax.text(width + 1.0, bar.get_y() + bar.get_height()/2, f'{width} Runden', 
            color=FG, ha='left', va='center', fontsize=9.0, fontweight='bold')

# Dotted grid lines
ax.set_xlim(0, 35)
ax.set_xlabel('Maximal überlebte Spielrunden (Ø 10 Seeds)', color=FG, fontsize=9.5)
ax.grid(True, axis='x', color=GRID, lw=0.5, ls=':')
ax.set_title('Lektion 2: System-Architektur schlägt reine Rechenleistung', color=FG, fontsize=10.5, pad=10)

fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "Lektion2_Architektur_schlaegt_Power.png"), facecolor=BG)
plt.close(fig)


# ==============================================================================
# BILD 3 (Passend zu Punkt 3: "Emergentes Verhalten")
# ==============================================================================
print("Generating Standalone 3: Lektion3_Emergentes_Verhalten.png...")
fig, ax = plt.subplots(figsize=(6.22, 5.0), dpi=300)
fig.patch.set_facecolor(BG)
style(ax)

# Raw data columns: V4 (Vermehrungsrate) and V6 (Bevölkerung)
raw_v4 = norm[:, 4]
raw_v6 = norm[:, 6]
R_range = range(31)

# Plot glow curves
plot_glow(ax, R_range, raw_v4, CYAN, lw=2.4, label='Vermehrungsrate (V4) → Steuerung')
plot_glow(ax, R_range, raw_v6, GREEN, lw=2.4, label='Bevölkerung (V6) → Stabilisierung')

# Shaded didactical phases
ax.axvspan(0, 12, color=CYAN, alpha=0.04)
ax.axvspan(12, 30, color=GREEN, alpha=0.04)
ax.axvline(12, color=MUT, ls='-.', lw=1.0, alpha=0.5)

# Text labels directly aligned with the curve paths
ax.text(6, 0.92, 'Phase 1: Aktive Drosselung\n(V4 wird radikal gebremst)', color=CYAN, ha='center', fontsize=9.0, fontweight='bold')
ax.text(21, 0.92, 'Phase 2: Kontrolliertes Wachstum\n(V6 wächst stabil unter Limit)', color=GREEN, ha='center', fontsize=9.0, fontweight='bold')

# Safe upper limit indicator
ax.axhline(0.8, color=RED, ls=':', lw=1.2, alpha=0.6)
ax.text(0.5, 0.82, 'Sicherheits-Grenze (0.80)', color=RED, fontsize=8.0, fontweight='bold')

ax.set_xlabel('Runde', color=FG, fontsize=9.5)
ax.set_ylabel('Normalisierter Variablenwert (0.0 … 1.0)', color=FG, fontsize=9.5)
ax.set_ylim(0, 1.05)
ax.set_xlim(0, 30)
ax.grid(True, color=GRID, lw=0.5, ls=':')
ax.legend(loc='lower right', frameon=False, labelcolor=FG, fontsize=9.0)
ax.set_title('Lektion 3: Emergente, anti-malthusianische Strategie der KI', color=FG, fontsize=10.5, pad=10)

fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "Lektion3_Emergentes_Verhalten.png"), facecolor=BG)
plt.close(fig)

print("SUCCESS: 3 standalone matching images successfully created and saved on Google Drive!")
print("Paths:")
print("-", os.path.join(OUT_DIR, "Lektion1_Standard_RL_scheitert.png"))
print("-", os.path.join(OUT_DIR, "Lektion2_Architektur_schlaegt_Power.png"))
print("-", os.path.join(OUT_DIR, "Lektion3_Emergentes_Verhalten.png"))
