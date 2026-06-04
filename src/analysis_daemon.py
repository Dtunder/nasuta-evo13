import time
import pandas as pd
import os

def analyze():
    log_dir = 'nasuta_evo/logs'
    csv_file = os.path.join(log_dir, 'evo10_local_ppo_results.csv')
    if not os.path.exists(csv_file): return
    
    df = pd.read_csv(csv_file)
    stats = df.groupby('seed')['balance'].mean()
    
    with open('nasuta_evo/logs/deep_analysis.md', 'a') as f:
        f.write(f'\n## Analyse {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'- Mean Balance: {stats.mean()}\n')
        f.write(f'- Min Balance: {stats.min()}\n')
        f.write(f'- Reason counts:\n{df["done_reason"].value_counts().to_string()}\n')

while True:
    analyze()
    time.sleep(600)
