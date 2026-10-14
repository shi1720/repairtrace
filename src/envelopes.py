"""Check sharp partial-provenance bounds on all ordered five-node DAGs."""
import itertools,json
from pathlib import Path
import networkx as nx
from model import closure
possible=list(itertools.combinations(range(5),2));groups={}
for mask in range(1024):
 g=nx.DiGraph();g.add_nodes_from(range(5));g.add_edges_from(e for i,e in enumerate(possible) if mask>>i&1)
 key=tuple(sorted(nx.transitive_closure_dag(g).edges));groups.setdefault(key,[]).append(g)
assignments=0;checks=0
for key,graphs in groups.items():
 hi=nx.DiGraph();hi.add_nodes_from(range(5));hi.add_edges_from(key);lo=nx.transitive_reduction(hi)
 for k in range(3):
  for edits in itertools.combinations(sorted(lo.edges),k):
   low=closure(lo,edits);high=closure(hi,edits);assignments+=1
   observed={t:[] for t in hi}
   for g in graphs:
    actual=closure(g,edits)
    for t in hi:
     assert low[t]<=actual[t]<=high[t];observed[t].append(len(actual[t]));checks+=1
   for t in hi:assert min(observed[t])==len(low[t]) and max(observed[t])==len(high[t])
root=Path(__file__).resolve().parents[1];r={'ordered_DAGs':1024,'reachability_classes':len(groups),'class_edit_assignments':assignments,'target_bound_checks':checks}
(root/'results/envelope_verification.json').write_text(json.dumps(r,indent=2));print(r)
