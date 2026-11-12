import json, os, sys
sys.path.insert(0,'.')
from labs import LABS
import harness
os.chdir('run')
def find(title):
    for d,ls in LABS.items():
        for L in ls:
            if L.get('title')==title: return L
def run(L,code):
    r=json.loads(harness._run(json.dumps(dict(code=code,prelude=L.get('prelude',''),tests=L['tests'],files=L.get('files',{}),limit=L.get('limit',3000000)))))
    return [x['label'] if 'label' in x else x.get('name') for x in r if not x['ok']]
M=[
("Build: a resilient LLM client","            p = prompt + '\\nReturn only valid JSON.'\n","            pass\n"),
("Build: a resilient LLM client","                if isinstance(data, dict):\n                    return data","                return data"),
("Build: a guarded agent","                cost += tool['cost']\n","                pass\n"),
("Build: a guarded agent","elif cost + tool['cost'] > self.max_cost","elif cost + tool['cost'] >= self.max_cost"),
("Build: a small orders API","        if key in db['keys']:\n            return db['keys'][key]\n",""),
("Build: a small orders API"," or isinstance(q, bool)",""),
("Build: fetch every page, politely","if waits >= max_waits:","if waits > max_waits:"),
("Build: fetch every page, politely","        waits = 0\n        for item","        for item"),
("Build: a mini RAG pipeline","if start + size >= len(words):","if start + size > len(words):"),
("Build: a mini RAG pipeline","scored.sort()","scored.sort(key=lambda t: t[1])"),
("Build: a Dockerfile that passes your own checks","'USER app', ",""),
("Build: a monthly report from a messy export","keep='first'","keep='last'"),
("Build: an eval harness","except Exception:","except KeyError:"),
]
for t,a,b in M:
    L=find(t)
    a=a.replace('\\\\n','\n').replace("\\n","\n") if False else a
    sol=L['solution']
    a2=a;b2=b.replace('\\n','\n')
    if a2 not in sol:
        print('NOMATCH',t,repr(a2[:50])); continue
    print(t[:38],'->',run(L,sol.replace(a2,b2,1)) or 'SURVIVED')
