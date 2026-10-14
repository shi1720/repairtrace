import json
from pathlib import Path
import networkx as nx
from model import exhaustive,costs
root=Path(__file__).resolve().parents[1];rows=[]
for c in json.loads((root/'data/guide_metadata.json').read_text()):
 g=nx.DiGraph();w={}
 for d in c['nodes']:
  gid=d['guideid'];g.add_node(gid);w[gid]=d['own_step_count']
  for p in d['prerequisites']:g.add_edge(p if isinstance(p,int) else p['guideid'],gid)
 red=nx.transitive_reduction(g);cand=sorted(red.edges,key=lambda e:(-len(nx.descendants(g,e[1])),e))[:12];targets=sorted(c['targets'])
 a=exhaustive(g,w,targets,cand,2);b=exhaustive(red,w,targets,cand,2)
 rows.append({'device':c['device'],'raw_opt':a[0],'reduced_opt':b[0],'raw_selection':a[1],'reduced_selection':b[1]})
(root/'results/zero_step_sensitivity.json').write_text(json.dumps(rows,indent=2));print(rows)
