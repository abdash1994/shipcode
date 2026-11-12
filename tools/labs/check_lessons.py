import json, os, sys
sys.path.insert(0,'.')
from labs import LESSONS, PRO
import harness
os.chdir('run'); bad=0; n=0
ALL = dict(LESSONS)
ALL.update({k: v['s'] for k, v in PRO.items()})
for day,ls in ALL.items():
    for s in ls:
        n+=1; q=s['q']
        if q['k']=='write' and q.get('sql'): continue
        if q['k']=='write':
            run=lambda code: json.loads(harness._run(json.dumps(dict(code=code,prelude=q.get('prelude',''),tests=q['tests'],files={},limit=300000))))
            a=run(q['sol']); b=run(q['starter'])
            if not all(r['ok'] for r in a): bad+=1; print('SOL FAILS',day,s['h'],[r for r in a if not r['ok']][:1])
            if all(r['ok'] for r in b): bad+=1; print('STARTER PASSES',day,s['h'])
        if s.get('run') and not s.get('sql'):
            r=json.loads(harness._run(json.dumps(dict(code=s['code'],prelude='',tests=[dict(label='run',out='',stdin=s.get('stdin',[]))],files={},limit=300000))))[0]
            if r.get('error'): bad+=1; print('EXAMPLE ERRORS IN HARNESS',day,s['h'],r['error'][:120])
print('days+modules',len(ALL),'screens',n,'problems',bad)
