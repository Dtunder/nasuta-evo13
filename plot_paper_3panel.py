# -*- coding: utf-8 -*-
"""EVO 13 - 3-Panel Trainingskurven im Paper-Stil (Engelhardt et al. Fig.2).
Liest logs/training_log_{mode}_seed*.csv und plottet balance B / rounds r / return
ueber die Trainings-Timesteps, eine Farbe pro Seed, Savitzky-Golay-Glaettung.

Aufruf:  python plot_paper_3panel.py --mode survival
"""
import os, sys, glob, argparse
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

def savgol(y, win=21, poly=3):
    """Savitzky-Golay ohne scipy-Zwang (Fallback: moving average)."""
    y = np.asarray(y, dtype=float)
    if len(y) < win:
        return y
    try:
        from scipy.signal import savgol_filter
        return savgol_filter(y, win if win % 2 else win + 1, poly)
    except Exception:
        k = np.ones(win) / win
        return np.convolve(y, k, mode='same')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="survival")
    ap.add_argument("--smooth", type=int, default=21)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(HERE, "logs", f"training_log_{args.mode}_seed*.csv")))
    if not files:
        print(f"Keine Logs fuer mode={args.mode}. Erst train_paper_data.py laufen lassen.")
        sys.exit(1)

    BG='#0E1726'; FG='#E7ECF4'; MUT='#93A3BD'; GRID='#1E2C45'
    SEED_COLORS = ['#38BDF8', '#F5B74D', '#34D399', '#F87171', '#A78BFA',
                   '#FB7185', '#22D3EE', '#FBBF24']
    plt.rcParams.update({'text.color':FG,'axes.labelcolor':FG,'xtick.color':FG,
        'ytick.color':MUT,'axes.edgecolor':'#2A3A55','font.family':'DejaVu Sans','font.size':11})

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), dpi=200)
    fig.patch.set_facecolor(BG)
    # Spalten-Index im CSV: 0=timestep, 1=balance_B, 2=rounds_r, 3=return
    panels = [(1, "balance B"), (2, "rounds r"), (3, "return")]

    for ax, (col_idx, ylabel) in zip(axes, panels):
        ax.set_facecolor(BG); ax.grid(True, color=GRID, lw=0.6)
        for sp in ('top','right'): ax.spines[sp].set_visible(False)
        for i, fp in enumerate(files):
            seed = os.path.basename(fp).split("seed")[-1].split(".")[0]
            data = np.atleast_2d(np.genfromtxt(fp, delimiter=",", skip_header=1))
            if data.size == 0 or data.shape[1] < 4: continue
            x = data[:, 0] / 1e5
            y = data[:, col_idx]
            c = SEED_COLORS[i % len(SEED_COLORS)]
            ax.plot(x, y, color=c, lw=0.5, alpha=0.25)
            ax.plot(x, savgol(y, args.smooth), color=c, lw=1.8, label=f"{seed}")
        ax.set_xlabel("timestep  (×10$^5$)"); ax.set_ylabel(ylabel)

    axes[1].set_title(f"EVO 13 — Trainingskurven (mode={args.mode}, {len(files)} Seeds)",
                      color=FG, fontsize=13, pad=14)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, title="Seed", loc='lower center', ncol=len(files),
               facecolor=BG, edgecolor=GRID, labelcolor=FG, fontsize=9,
               title_fontproperties={'size': 9})
    fig.tight_layout(rect=(0, 0.07, 1, 1))

    out = os.path.join(HERE, "_assets", f"paper_3panel_{args.mode}.png")
    fig.savefig(out, facecolor=BG); plt.close(fig)
    print(f"Gespeichert: {out}")

if __name__ == "__main__":
    main()
