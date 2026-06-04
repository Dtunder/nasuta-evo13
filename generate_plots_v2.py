# -*- coding: utf-8 -*-
"""3 zusaetzliche, FAKTISCH KORREKTE Charts (Cybernetic Dark Theme).
Daten: echte Eval-Logs (Ø30/100% @1M, MaskablePPO MLP, max=30 Runden)."""
import os, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=os.path.dirname(os.path.abspath(__file__)); ASSET=os.path.join(HERE,"_assets")
os.makedirs(ASSET,exist_ok=True)
BG='#0E1726'; FG='#E7ECF4'; MUT='#93A3BD'; GRID='#1E2C45'
GREEN='#34D399'; CYAN='#38BDF8'; RED='#F87171'; AMBER='#F5B74D'; PURP='#A78BFA'
plt.rcParams.update({'text.color':FG,'axes.labelcolor':FG,'xtick.color':FG,
  'ytick.color':MUT,'axes.edgecolor':'#2A3A55','font.family':'DejaVu Sans','font.size':12})

def style(ax):
    ax.set_facecolor(BG); ax.grid(True,axis='y',color=GRID,lw=0.7)
    for sp in ('top','right'): ax.spines[sp].set_visible(False)

# ---- A: Benchmark (4 Methoden, kanonische Zahlen aus _EVO12_FACTS.md §3) ----
# Baselines = dokumentierte Bestwerte (Paper/Sovereign n=25, Heuristik det.);
# Evo 12 = gemessen (10 Seeds). Siehe _BENCHMARK_VERGLEICH.md.
fig,ax=plt.subplots(figsize=(9,4.7),dpi=200); fig.patch.set_facecolor(BG); style(ax)
names=['Paper UCT\n(MCTS)','Sovereign\nMCTS','Heuristik\n(det.)','Spread+Ceiling\n(Evo 12)']
vals=[3.28,7.08,24,30]; cols=[RED,AMBER,CYAN,GREEN]
b=ax.bar(names,vals,color=cols,width=0.62,zorder=3)
ax.axhline(30,ls=':',color=GREEN,lw=1.1); ax.text(3.46,30.4,'Sieg = 30',color=GREEN,fontsize=10,ha='right')
for rect,v in zip(b,vals):
    lbl=f'{v:.2f}' if v<10 else f'{int(v)}'
    ax.text(rect.get_x()+rect.get_width()/2,v+0.7,lbl,ha='center',color=FG,fontsize=15,fontweight='bold')
ax.set_ylabel('Ø überlebte Runden'); ax.set_ylim(0,33)
ax.set_title('Baselines: dokumentierte Bestwerte · Evo 12: gemessen (100 %)',color=MUT,fontsize=10.5,pad=10)
fig.tight_layout(); fig.savefig(os.path.join(ASSET,'F_benchmark.png'),facecolor=BG); plt.close(fig)

# ---- B: Reward-Evolution (die ehrliche Story) ----
fig,ax=plt.subplots(figsize=(9,4.7),dpi=200); fig.patch.set_facecolor(BG); style(ax)
rn=['Quadratische\nPop-Strafe','Centering /\nMin-Margin','Spread +\nCeiling-Guard']
rv=[6,6,30]; rc=[RED,RED,GREEN]; cause=['Suicide-Trap','Überpopulation','100% survived']
b=ax.bar(rn,rv,color=rc,width=0.6,zorder=3)
for rect,v,c in zip(b,rv,cause):
    ax.text(rect.get_x()+rect.get_width()/2,v+0.7,f'Ø{v}',ha='center',color=FG,fontsize=14,fontweight='bold')
    ax.text(rect.get_x()+rect.get_width()/2,v/2,c,ha='center',va='center',color=BG,fontsize=10,fontweight='bold',rotation=0)
ax.annotate('',xy=(2,29),xytext=(0,7),arrowprops=dict(arrowstyle='->',color=MUT,lw=1.5,ls=':'))
ax.set_ylabel('Ø Runden überlebt'); ax.set_ylim(0,33)
ax.set_title('Reward-Evolution: Empirie schlägt Theorie',color=FG,fontsize=13,pad=12)
fig.tight_layout(); fig.savefig(os.path.join(ASSET,'F_reward_evolution.png'),facecolor=BG); plt.close(fig)

# ---- C: Death-Cause Progression (Whack-a-Mole -> geloest) ----
fig,ax=plt.subplots(figsize=(9,4.7),dpi=200); fig.patch.set_facecolor(BG); style(ax)
x=[0.25,0.5,0.75,1.0]; y=[14,14,14,30]
causes=['Überpopulation','QoL-Decke','AP out of range','survived ✓']
ccol=[RED,RED,RED,GREEN]
ax.plot(x,y,'-',color=CYAN,lw=2.5,zorder=2)
for xi,yi,c,col in zip(x,y,causes,ccol):
    ax.scatter([xi],[yi],s=140,color=col,zorder=4,edgecolors=BG,linewidths=1.5)
    dy=1.6 if yi<20 else -3.2
    ax.annotate(c,xy=(xi,yi),xytext=(xi,yi+dy),ha='center',color=col,fontsize=11,fontweight='bold')
ax.text(0.5,11.4,'„Whack-a-Mole": Agent flickt eine Wand, reißt die nächste auf',
        color=MUT,fontsize=10.5,ha='center')
ax.set_xlabel('Trainings-Steps (Mio.)'); ax.set_ylabel('Ø Runden überlebt')
ax.set_xticks(x); ax.set_xticklabels(['0.25','0.5','0.75','1.0'])
ax.set_ylim(0,34); ax.set_xlim(0.18,1.07)
fig.tight_layout(); fig.savefig(os.path.join(ASSET,'F_deathcause.png'),facecolor=BG); plt.close(fig)

print("OK:", [f for f in os.listdir(ASSET) if f.startswith('F_')])
