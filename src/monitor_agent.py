import time
import pandas as pd
import matplotlib.pyplot as plt
import os
import subprocess
import numpy as np
from scipy import stats
import git

# Pfade
LOG_DIR = 'nasuta_evo/logs'
CSV_FILE = os.path.join(LOG_DIR, 'evo10_local_ppo_results.csv')
CHART_DIR = 'nasuta_evo/docs/figures'
FINAL_REPORT = 'nasuta_evo/FINAL_LEGIT_ANALYSIS.md'

# Paper Baseline
PAPER_ROUNDS = 2.0
PAPER_BALANCE = -38.0

def get_git_hash():
    try:
        repo = git.Repo(search_parent_directories=True)
        return repo.head.object.hexsha[:7]
    except: return "unknown"

def run_bench():
    subprocess.run(["python", "nasuta_evo/src/evo10_local_bench.py"], check=True)

def update_analysis():
    if not os.path.exists(CSV_FILE): return
    df = pd.read_csv(CSV_FILE)
    
    # Statistiken
    mean_rounds = df['rounds_survived'].mean()
    std_rounds = df['rounds_survived'].std()
    t_stat, p_val = stats.ttest_1samp(df['rounds_survived'], PAPER_ROUNDS)
    
    # Charts erstellen
    os.makedirs(CHART_DIR, exist_ok=True)
    
    # 1. Runden Vergleich mit Fehlerschranken
    plt.figure(figsize=(10, 6))
    plt.bar(['Paper Baseline', 'Evo-10 Model'], [PAPER_ROUNDS, mean_rounds], 
            yerr=[0, std_rounds], capsize=10, color=['#ff9999','#66b3ff'])
    plt.title(f'Statistischer Vergleich: Überlebensrunden (p={p_val:.4f})')
    plt.savefig(os.path.join(CHART_DIR, 'rounds_comparison_stats.png'))
    plt.close()
    
    # 2. Balance-Dichte
    plt.figure(figsize=(10, 6))
    plt.hist(df['balance'], bins=10, alpha=0.7, color='green')
    plt.axvline(PAPER_BALANCE, color='red', linestyle='dashed', label='Paper Baseline')
    plt.title('Verteilung der Balance in Evo-10')
    plt.legend()
    plt.savefig(os.path.join(CHART_DIR, 'balance_distribution.png'))
    plt.close()
    
    # Report schreiben
    with open(FINAL_REPORT, 'w', encoding='utf-8') as f:
        f.write(f"# Offizieller Vergleichsbericht: Paper vs. Evo-10\n")
        f.write(f"**Git Hash:** {get_git_hash()}\n\n")
        f.write(f"## Statistische Signifikanz\n")
        f.write(f"- Paper-Baseline: {PAPER_ROUNDS} Runden\n")
        f.write(f"- Evo-10 Durchschnitt: {mean_rounds:.2f} ± {std_rounds:.2f}\n")
        f.write(f"- P-Wert: {p_val:.6f}\n\n")
        f.write(f"## Fazit für Präsentation\n")
        if p_val < 0.05:
            f.write("- **Ergebnis signifikant:** Evo-10 unterscheidet sich messbar von der Paper-Baseline.\n")
        else:
            f.write("- **Kein signifikanter Unterschied:** Evo-10 stagniert aktuell auf Baseline-Niveau.\n")

if __name__ == "__main__":
    while True:
        run_bench()
        update_analysis()
        time.sleep(600)

