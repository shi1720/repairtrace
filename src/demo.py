"""A reproducible certificate for the complementary access-change example."""
import json
from pathlib import Path
import networkx as nx
from model import exact_milp,costs,compile_provenance,eval_provenance,export_provenance,evaluate_export
root=Path(__file__).resolve().parents[1]
g=nx.DiGraph([('a','b'),('b','t'),('a','c'),('c','t'),('d','t')]);w={v:1 for v in g};w['a']=100
candidates=[('a','b'),('a','c'),('d','t')]
value,selected,meta=exact_milp(g,w,['t'],candidates,2)
compiled=compile_provenance(g);before=costs(g,w,['t'])[0];answers=eval_provenance(compiled,selected)
certificate={'primitive_edges':list(g.edges),'efforts':w,'editable_edges':candidates,'budget':2,'target':'t','selected':selected,'before':before,'after':value,'required_after':[u for u in g if answers[u,'t']],'solver':meta,'scope':'Additive conjunctive access model; edit feasibility supplied externally.'}
(root/'results/demo_certificate.json').write_text(json.dumps(certificate,indent=2))
print(json.dumps(certificate,indent=2))

export=export_provenance(g,w,['t'],candidates)
loaded=json.loads(json.dumps(export))
assert evaluate_export(loaded,selected)==answers
(root/'results/demo_provenance_export.json').write_text(json.dumps(export,indent=2))
