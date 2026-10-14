import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
ROOT=Path(__file__).resolve().parents[1];F=ROOT/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'font.family':'DejaVu Sans'})
fig,axs=plt.subplots(1,3,figsize=(7,2.2))
pos={'a':(0,1),'b':(1,1),'t':(2,1)}
for ax,title,extra in [(axs[0],'Primitive chain',False),(axs[1],'Same order, extra primitive',True)]:
 g=nx.DiGraph([('a','b'),('b','t')]);
 if extra:g.add_edge('a','t')
 nx.draw_networkx_nodes(g,pos,ax=ax,node_color='#dce9f3',node_size=700);nx.draw_networkx_labels(g,pos,ax=ax)
 nx.draw_networkx_edges(g,pos,ax=ax,edgelist=[('a','b')],arrows=True,node_size=700,width=1.5)
 nx.draw_networkx_edges(g,pos,ax=ax,edgelist=[('b','t')],arrows=True,node_size=700,width=1.5,edge_color='#bd442a',style='dashed')
 if extra:nx.draw_networkx_edges(g,pos,ax=ax,edgelist=[('a','t')],arrows=True,node_size=700,connectionstyle='arc3,rad=.5',width=1.5)
 ax.set_title(title,fontsize=9);ax.text(1,.55,'Remove dashed constraint',ha='center',fontsize=8);ax.set_xlim(-.5,2.5);ax.set_ylim(.4,1.5);ax.axis('off')
axs[2].axis('off');axs[2].text(.02,.82,'Before edit: identical access\n\nAfter edit:\nchain requires {t}\nextra primitive requires {a, t}\n\nReachability alone cannot\nidentify edit effects.',fontsize=9,va='top')
fig.tight_layout();fig.savefig(F/'ambiguity.pdf',bbox_inches='tight');plt.close(fig)
x=json.loads((ROOT/'results/synthetic.json').read_text());fig,axs=plt.subplots(1,2,figsize=(7,2.65))
names=['Greedy','Closure edits','Reduction edits'];fields=['greedy','closure_actual','reduction_actual']
loss=[[100*(r[f]-r['opt'])/r['base'] for r in x] for f in fields]
axs[0].boxplot(loss,labels=names,showfliers=True,flierprops={'marker':'.','markersize':3},medianprops={'color':'#bd442a'});axs[0].set_ylabel('Excess effort / baseline (%)');axs[0].set_title('(a) Realized recommendation loss',fontsize=9)
for n,col in [(12,'#2c6e9b'),(24,'#cf852a'),(48,'#36826b')]:
 means=[np.mean([100*(r['closure_actual']-r['opt'])/r['base'] for r in x if r['n']==n and r['p']==p]) for p in [.1,.2,.35]]
 axs[1].plot([.1,.2,.35],means,'o-',label=f'{n} tasks',color=col)
axs[1].set_xlabel('Primitive edge probability');axs[1].set_ylabel('Mean excess effort / baseline (%)');axs[1].set_title('(b) Closure-edit sensitivity',fontsize=9);axs[1].legend(frameon=False,fontsize=8)
fig.tight_layout();fig.savefig(F/'synthetic.pdf',bbox_inches='tight');plt.close(fig)
p=json.loads((ROOT/'results/public.json').read_text());plt.rcParams.update({'font.size':7});fig,ax=plt.subplots(figsize=(3.35,2.45));names=['Steam Deck','Fairphone 4','iPhone 13','Switch','Dyson V6'];y=np.arange(5)
raw=[100*(r['base']-r['raw_opt'])/r['base'] for r in p];red=[100*(r['base']-r['reduced_opt'])/r['base'] for r in p]
ax.barh(y-.15,raw,.3,label='Raw-list primitive assumption',color='#2c6e9b');ax.barh(y+.15,red,.3,label='Reduced-list primitive assumption',color='#cf852a');ax.set_yticks(y,labels=names);ax.invert_yaxis();ax.set_xlabel('Predicted step-effort reduction (%)');ax.legend(frameon=False,fontsize=6,loc='lower center',bbox_to_anchor=(.5,-.6));fig.tight_layout();fig.savefig(F/'public.pdf',bbox_inches='tight');plt.close(fig)
