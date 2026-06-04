import pandas as pd
import matplotlib.pyplot as plt
import os

def create_plots():
    log_dir = 'nasuta_evo/logs'
    csv_file = os.path.join(log_dir, 'evo10_local_ppo_results.csv')
    if not os.path.exists(csv_file): return
    
    df = pd.read_csv(csv_file)
    
    # Paper Baseline Werte (aus EVO8_VERGLEICHSBERICHT.md)
    paper_rounds = 2.0
    paper_balance = -38.0
    
    # Plot 1: Runden-Vergleich
    plt.figure(figsize=(10, 5))
    plt.bar(['Paper Baseline', 'Evo-10 Model'], [paper_rounds, df['rounds_survived'].mean()], color=['red', 'blue'])
    plt.title('Überlebensrunden: Paper vs. Evo-10')
    plt.ylabel('Runden')
    plt.savefig(os.path.join(log_dir, 'rounds_comparison.png'))
    
    # Plot 2: Balance-Vergleich
    plt.figure(figsize=(10, 5))
    plt.bar(['Paper Baseline', 'Evo-10 Model'], [paper_balance, df['balance'].mean()], color=['red', 'green'])
    plt.title('Balance-Performance: Paper vs. Evo-10')
    plt.ylabel('Balance')
    plt.savefig(os.path.join(log_dir, 'balance_comparison.png'))
    
    print("Diagramme unter nasuta_evo/logs/ gespeichert.")

create_plots()
