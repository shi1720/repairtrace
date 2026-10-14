import json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'results'
x=json.loads((R/'synthetic.json').read_text()); s={}
for name in ['greedy','closure_actual','reduction_actual']:
 loss=np.array([(r[name]-r['opt'])/r['base']*100 for r in x]);positive=loss[loss>1e-7]
 s[name]={'worse_count':len(positive),'median_baseline_pct':float(np.median(loss)),'max_baseline_pct':float(max(loss)),'median_positive_pct':float(np.median(positive))}
for name,actual in [('closure_prediction','closure_actual'),('reduction_prediction','reduction_actual')]:
 error=np.array([(r[name]-r[actual])/r['base']*100 for r in x]);s[name]={'mismatch_count':int(sum(abs(error)>1e-7)),'median_error_pct':float(np.median(error)),'max_absolute_pct':float(max(abs(error)))}
s['optimal_savings']={'median_pct':float(np.median([(r['base']-r['opt'])/r['base']*100 for r in x]))}
if (R/'public.json').exists():s['public']=json.loads((R/'public.json').read_text())
if (R/'scaling.json').exists():
 z=json.loads((R/'scaling.json').read_text());s['scaling']={str(n):{'median_seconds':float(np.median([r['seconds'] for r in z if r['n']==n])),'max_seconds':max(r['seconds'] for r in z if r['n']==n),'max_gap':max(r['gap'] for r in z if r['n']==n)} for n in [24,48,96]}
(R/'summary.json').write_text(json.dumps(s,indent=2));print(json.dumps(s,indent=2))
