import json, os, re, sqlite3, sys
sys.path.insert(0,'.')
from labs import IV, IV_LOOPS, SEED, SEED2
import harness
os.chdir('run'); bad=0
for i,L in enumerate(IV):
    if L['kind']=='design':
        miss=[k[0] for k in L['keys'] if not re.search(k[1],' '.join(L['model']),re.I)]
        if miss: bad+=1; print('KEYS NOT IN MODEL',i,L['title'],miss)
        assert sum(1 for q in L['questions'] if q[1])==3 and len(L['questions'])==6
        for t in L['trade']: assert 0<=t['a']<len(t['o'])
    elif L['kind']=='py':
        p=lambda code: json.loads(harness._run(json.dumps(dict(code=code,prelude=L.get('prelude',''),tests=L['tests'],files={},limit=3000000))))
        sol=p(L['solution']); st=p(L['starter'])
        if not all(r['ok'] for r in sol): bad+=1; print('SOLUTION FAILS',i,[r for r in sol if not r['ok']][:2])
        f=[r['label'] for r in st if not r['ok']]
        print(i,L['title'],'| buggy starter fails',len(f),'of',len(st),':',f)
        if not f: bad+=1; print('STARTER PASSES',i)
    else:
        for nm,seed in (('visible',SEED),('hidden',SEED2)):
            db=sqlite3.connect(':memory:'); db.executescript(seed); print(i,nm,db.execute(L['solution']).fetchall())
print('iv labs',len(IV),'loops',len(IV_LOOPS),'problems',bad)
