"""Primitive-edge access costs, symbolic provenance, exact budgeted optimization."""
import itertools,time
import numpy as np
import networkx as nx
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix

def closure(g, removed=()):
 h=g.copy(); h.remove_edges_from(removed)
 return {t: nx.ancestors(h,t)|{t} for t in h}

def costs(g,weights,targets,removed=()):
 a=closure(g,removed)
 return np.array([sum(weights[v] for v in a[t]) for t in targets],float)

def exhaustive(g,w,targets,candidates,budget,probs=None):
 probs=np.ones(len(targets))/len(targets) if probs is None else np.array(probs)
 best=(float('inf'),())
 for k in range(budget+1):
  for s in itertools.combinations(candidates,k):
   value=float(costs(g,w,targets,s)@probs)
   if value<best[0]-1e-9:best=(value,s)
 return best

def greedy(g,w,targets,candidates,budget):
 selected=[]
 for _ in range(min(budget,len(candidates))):
  e=min((e for e in candidates if e not in selected),key=lambda e:(costs(g,w,targets,selected+[e]).mean(),e))
  selected.append(e)
 return float(costs(g,w,targets,selected).mean()),tuple(selected)

def exact_milp(g,w,targets,candidates,budget,probs=None):
 nodes=list(g); ni={v:i for i,v in enumerate(nodes)}; edges=list(g.edges); ci={e:i for i,e in enumerate(candidates)}
 n=len(nodes); m=len(candidates); q=len(targets); nv=m+n*q
 probs=np.ones(q)/q if probs is None else np.array(probs)
 c=np.zeros(nv)
 for j,t in enumerate(targets):
  for v in nodes:c[m+j*n+ni[v]]=probs[j]*w[v]
 a=lil_matrix((1+q+len(edges)*q,nv)); lb=np.full(a.shape[0],-np.inf); ub=np.full(a.shape[0],np.inf)
 a[0,:m]=1; ub[0]=budget; row=1
 for j,t in enumerate(targets):
  a[row,m+j*n+ni[t]]=1;lb[row]=ub[row]=1;row+=1
  for u,v in edges:
   a[row,m+j*n+ni[u]]=1;a[row,m+j*n+ni[v]]=-1
   if (u,v) in ci:a[row,ci[u,v]]=1
   lb[row]=0;row+=1
 start=time.perf_counter()
 r=milp(c,integrality=np.ones(nv),bounds=Bounds(np.zeros(nv),np.ones(nv)),constraints=LinearConstraint(a.tocsr(),lb,ub),options={'time_limit':120,'mip_rel_gap':0})
 if not r.success:raise RuntimeError(r.message)
 selected=tuple(e for e,i in ci.items() if r.x[i]>.5)
 recomputed=float(costs(g,w,targets,selected)@probs)
 assert abs(r.fun-recomputed)<1e-7
 return recomputed,selected,{'seconds':time.perf_counter()-start,'gap':float(r.mip_gap),'bound':float(r.mip_dual_bound)}

def compile_provenance(g):
 """Shared Boolean circuit: each primitive edge has one surviving-edge variable."""
 nodes=list(nx.topological_sort(g)); edges=list(g.edges); ei={e:i for i,e in enumerate(edges)}
 gates=[]; ref={}
 def gate(kind,args):
  gates.append((kind,args));return len(gates)-1
 zero=gate('const',(False,)); one=gate('const',(True,)); variables={e:gate('edge',(i,)) for e,i in ei.items()}
 for t in reversed(nodes):
  for u in reversed(nodes):
   if u==t:ref[u,t]=one;continue
   terms=[gate('and',(variables[u,v],ref[v,t])) for v in g.successors(u)]
   ref[u,t]=gate('or',tuple(terms)) if terms else zero
 return edges,gates,ref

def eval_provenance(compiled,removed=()):
 edges,gates,ref=compiled; kept=[e not in removed for e in edges]; values=[]
 for kind,args in gates:
  if kind=='const':v=args[0]
  elif kind=='edge':v=kept[args[0]]
  elif kind=='and':v=all(values[i] for i in args)
  else:v=any(values[i] for i in args)
  values.append(v)
 return {pair:values[i] for pair,i in ref.items()}

def export_provenance(g,weights,targets,candidates):
 """Portable IR: visible graphs are presentation-only; primitive identities persist."""
 edges,gates,refs=compile_provenance(g)
 return {'version':1,'nodes':list(g),'primitive_edges':[list(e) for e in edges],
         'efforts':[[v,weights[v]] for v in g], 'targets':list(targets),
         'editable_edges':[list(e) for e in candidates],
         'gates':[[kind,list(args)] for kind,args in gates],
         'pair_outputs':[[u,t,i] for (u,t),i in refs.items()]}

def evaluate_export(obj,removed=()):
 """Evaluate a JSON-round-tripped circuit without the primitive graph library."""
 disabled={tuple(e) for e in removed};kept=[tuple(e) not in disabled for e in obj['primitive_edges']];values=[]
 for kind,args in obj['gates']:
  if kind=='const':v=args[0]
  elif kind=='edge':v=kept[args[0]]
  elif kind=='and':v=all(values[i] for i in args)
  elif kind=='or':v=any(values[i] for i in args)
  else:raise ValueError('Unknown gate '+kind)
  values.append(v)
 return {(u,t):values[i] for u,t,i in obj['pair_outputs']}
