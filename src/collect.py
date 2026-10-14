"""Collect only public guide dependency metadata; no guide prose or images."""
import json,time,urllib.request,urllib.parse,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'data'
DEVICES=['Steam_Deck','Fairphone_4','iPhone_13','Nintendo_Switch','Dyson_V6_Motorhead']
def get(path):
 u='https://www.ifixit.com/api/2.0/'+path
 for attempt in range(4):
  try:
   with urllib.request.urlopen(u,timeout=30) as r: return json.load(r)
  except Exception:
   time.sleep(2**attempt)
 raise RuntimeError(u)
def main():
 cache={}; cases=[]
 for device in DEVICES:
  wiki=get('wikis/CATEGORY/'+urllib.parse.quote(device)); targets=[g['guideid'] for g in wiki['guides'] if g['type']=='replacement' and 'GUIDE_PREREQ_ONLY' not in g.get('flags',[])]
  nodes={}; stack=targets[:]
  while stack:
   gid=stack.pop()
   if gid in nodes:continue
   if gid not in cache:
    d=get('guides/'+str(gid))
    cache[gid]={k:d.get(k) for k in ['guideid','title','category','revisionid','url','prerequisites','modified_date']}
    cache[gid]['own_step_count']=sum(s['guideid']==gid for s in d['steps'])
    cache[gid]['total_step_count']=len(d['steps']); time.sleep(.1)
   d=cache[gid]; nodes[gid]=d
   for p in d['prerequisites']:
    pid=p if isinstance(p,int) else p['guideid']; stack.append(pid)
  cases.append({'device':device,'targets':targets,'nodes':list(nodes.values())})
  (OUT/'guide_metadata.json').write_text(json.dumps(cases,indent=2))
  print(device,len(targets),len(nodes),flush=True)
 OUT.mkdir(exist_ok=True)
 (OUT/'guide_metadata.json').write_text(json.dumps(cases,indent=2))
 (OUT/'PROVENANCE.txt').write_text('Source: iFixit API 2.0. Retrieved 2026-10-14. Metadata only. CC BY-NC-SA 3.0; https://www.ifixit.com/api-docs. No LLM training. Product names identify sources; no affiliation.\n')
if __name__=='__main__':main()
