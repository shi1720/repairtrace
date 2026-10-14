import json,itertools,platform,time,csv
from pathlib import Path
import numpy as np
import networkx as nx
from model import *
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
def independent(g,removed):
 adj={v:[] for v in g}
 for u,v in g.edges:
  if (u,v) not in removed:adj[u].append(v)
 out={}
 for u in g:
  seen={u}; stack=[u]
  while stack:
   v=stack.pop()
   for x in adj[v]:
    if x not in seen:seen.add(x);stack.append(x)
  for v in g:out[u,v]=v in seen
 return out

def verify():
 count=0;possible=list(itertools.combinations(range(5),2))
 for mask in range(1<<len(possible)):
  g=nx.DiGraph();g.add_nodes_from(range(5));g.add_edges_from(e for i,e in enumerate(possible) if mask>>i&1)
  comp=compile_provenance(g)
  for k in range(3):
   for s in itertools.combinations(list(g.edges),k):
    assert eval_provenance(comp,s)==independent(g,s); count+=1
 rng=np.random.default_rng(71)
 for i in range(80):
  g=nx.DiGraph();g.add_nodes_from(range(8));g.add_edges_from(e for e in itertools.combinations(range(8),2) if rng.random()<.35)
  cand=sorted(g.edges)[:12];w={v:int(rng.integers(1,10)) for v in g};targets=[5,6,7]
  a=exhaustive(g,w,targets,cand,2);b=exact_milp(g,w,targets,cand,2)
  assert abs(a[0]-b[0])<1e-7
 return {'all_five_node_ordered_DAGs':1024,'deletion_assignments':count,'pair_checks':25*count,'milp_exhaustive_matches':80}

def synthetic():
 rows=[]
 for n,p,seed in itertools.product([12,24,48],[.1,.2,.35],range(20)):
  rng=np.random.default_rng(100000*n+1000*round(p*100)+seed)
  g=nx.DiGraph();g.add_nodes_from(range(n));g.add_edges_from(e for e in itertools.combinations(range(n),2) if rng.random()<p)
  cand=sorted(g.edges)
  if len(cand)>12:cand=[cand[i] for i in sorted(rng.choice(len(cand),12,replace=False))]
  w={v:int(rng.integers(1,11)) for v in g};targets=list(range(n-4,n)); base=costs(g,w,targets).mean()
  cl=nx.transitive_closure_dag(g);red=nx.transitive_reduction(g)
  opt,sel=exhaustive(g,w,targets,cand,2); gr,gs=greedy(g,w,targets,cand,2)
  cv,cs=exhaustive(cl,w,targets,cand,2); rv,rs=exhaustive(red,w,targets,cand,2)
  # Every original candidate remains the same intervention label, even if the reduced export discarded its edge.
  cl_actual=costs(g,w,targets,cs).mean(); red_actual=costs(g,w,targets,rs).mean()
  cp=compile_provenance(g);pv=eval_provenance(cp,sel)
  assert all(pv[u,t]==(u in closure(g,sel)[t]) for u in g for t in targets)
  rows.append(dict(n=n,p=p,seed=seed,edges=len(g.edges),candidates=len(cand),base=float(base),opt=float(opt),greedy=float(gr),closure_prediction=float(cv),closure_actual=float(cl_actual),reduction_prediction=float(rv),reduction_actual=float(red_actual),closure_selection=cs,reduction_selection=rs,opt_selection=sel))
 return rows

def public():
 cases=json.loads((ROOT/'data/guide_metadata.json').read_text());rows=[]
 for c in cases:
  g=nx.DiGraph();w={}
  for d in c['nodes']:
   gid=d['guideid'];g.add_node(gid);w[gid]=max(1,d['own_step_count'])
   for p in d['prerequisites']:g.add_edge(p if isinstance(p,int) else p['guideid'],gid)
  assert nx.is_directed_acyclic_graph(g)
  targets=sorted(c['targets']);red=nx.transitive_reduction(g)
  assert all(nx.ancestors(g,t)==nx.ancestors(red,t) for t in targets)
  cand=sorted(red.edges,key=lambda e:(-len(nx.descendants(g,e[1])),e))[:12]
  base=float(costs(g,w,targets).mean())
  rv,rs=exhaustive(g,w,targets,cand,2);tv,ts=exhaustive(red,w,targets,cand,2)
  row=dict(device=c['device'],nodes=len(g),targets=len(targets),raw_edges=len(g.edges),reduced_edges=len(red.edges),candidates=len(cand),base=base,raw_opt=rv,reduced_opt=tv,raw_of_reduced=float(costs(g,w,targets,ts).mean()),reduced_of_raw=float(costs(red,w,targets,rs).mean()),raw_selection=rs,reduced_selection=ts,zero_own_steps=sum(d['own_step_count']==0 for d in c['nodes']))
  rows.append(row)
 return rows

def scaling():
 rows=[]
 for n in [24,48,96]:
  for seed in range(10):
   rng=np.random.default_rng(n*100+seed);g=nx.DiGraph();g.add_nodes_from(range(n));g.add_edges_from(e for e in itertools.combinations(range(n),2) if rng.random()<.08)
   cand=sorted(g.edges);rng.shuffle(cand);cand=sorted(cand[:30]);w={v:int(rng.integers(1,11)) for v in g};targets=list(range(n-6,n))
   v,s,meta=exact_milp(g,w,targets,cand,3)
   rows.append(dict(n=n,seed=seed,edges=len(g.edges),value=v,selection=s,**meta))
 return rows
if __name__=='__main__':
 R.mkdir(exist_ok=True)
 checks=verify();print(checks,flush=True);(R/'verification.json').write_text(json.dumps(checks,indent=2))
 for name,fn in [('synthetic',synthetic),('public',public),('scaling',scaling)]:
  data=fn();(R/(name+'.json')).write_text(json.dumps(data,indent=2));print(name,len(data),flush=True)
 (R/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'networkx':nx.__version__,'platform':platform.platform()},indent=2))
