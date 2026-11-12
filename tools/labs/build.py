import json, sqlite3, html, sys
sys.path.insert(0, '.')
from labs import LABS, SEED, SEED2, UNSEEN, GYM, GYMS as GYMS_NEW, EXTRA_PLAN, EXAM_FORMS, IV, IV_LOOPS, LESSONS, PRO
GYMS = [dict(key='sql', name='SQL Gym', short='SQL', base=40, blurb='Five levels: write queries, join and aggregate, make them correct, make them fast, and decide.', intro='SQL here runs on SQLite in your browser, which differs in small ways from Postgres, BigQuery or Snowflake; the lessons point out where. Level 4 is partly concept work: partitioning and warehouse cost cannot run in a browser database, so those parts are checks and a written design exercise, and the labs there read query plans.', levels=GYM)] + GYMS_NEW
from drills import EXTRA, SETUPS
SPARK = {f: open('sparklite/' + f, encoding='utf-8').read() for f in ('pyspark/__init__.py', 'pyspark/sql/__init__.py', 'pyspark/sql/functions.py')}
from plan import PLAN, MOCK
PLAN.update(EXTRA_PLAN)
from syntax import CARD as SYNCARD, new_for, GLOSS
from starter import STARTER
from outcomes import OUTCOMES, WEEK_SHARE

src = open('local.html', encoding='utf-8').read()

def rep(old, new, s=None):
    global src
    assert src.count(old) == 1, (src.count(old), old[:80])
    src = src.replace(old, new)

# ---- lab data: plans, mocks, SQL row counts ----
db = sqlite3.connect(':memory:'); db.executescript(SEED)
pats = []
for day, ls in LABS.items():
    for i, L in enumerate(ls):
        if (day, i) in MOCK: L['mock'] = True
        if not L.get('gym') and L['kind'] in ('py', 'sql') and 'solution' in L and 'new' not in L:
            nw = new_for(day, L['solution'])
            if nw: L['new'] = nw
        if L['kind'] == 'sql':
            L['rows'] = len(db.execute(L['solution']).fetchall())
        elif L['kind'] == 'py' and not L.get('bug') and not L.get('gym'):
            assert (day, i) in PLAN, ('missing plan', day, i)
            pat, steps, free = PLAN[(day, i)]
            L['pat'], L['steps'] = pat, steps
            if free: L['free'] = True
            if pat not in pats: pats.append(pat)
assert set(PLAN) <= {(d, i) for d, ls in LABS.items() for i in range(len(ls))}

PATWHY = {
 "read input & print": "you read the lines you're given, convert them, and print results",
 "loop & build a list": "you go through items one by one and collect results",
 "while loop": "you repeat until a condition changes and don't know the count in advance",
 "string methods": "split, join, strip, lower and slicing can do the heavy lifting",
 "hash map / set": "you need to count things or ask \"have I seen this?\" instantly",
 "try/except": "some inputs will fail and you must handle them instead of crashing",
 "running total": "each answer builds on the one before it",
 "track best so far": "one pass is enough if you remember the best (or lowest) value seen so far",
 "class with methods": "some data and the actions on it belong together",
 "file reading": "you open a file with with, read it, and it closes automatically",
 "two pointers": "the data is sorted and you move one end or the other",
 "sliding window": "you need a contiguous stretch that grows on the right and shrinks on the left",
 "stack": "the most recent item must be handled first, as with brackets or the next warmer day",
 "binary search": "the data is sorted and you need O(log n): halve the range each step",
 "linked list pointers": "you rewire next pointers carefully, often with a dummy head",
 "recursion": "the answer for a node comes from the answers for its children",
 "BFS/DFS": "you explore connected cells or nodes, marking what you've visited",
 "dynamic programming": "the answer for n is built from answers for smaller n",
 "sort then scan": "after sorting, the items that interact sit next to each other",
 "heap": "you repeatedly need the smallest item, or the k largest",
 "prefix sums": "sums or products of stretches come from running totals",
 "validation rules": "you check each rule in turn and collect what's wrong",
 "loop with retries": "you try, catch the failure, and try again up to a limit",
 "string search & parse": "you find positions in text, cut out the part you need, and parse it",
 "slicing": "you take a piece of a list or string by position",
 "math formula": "you apply a known formula carefully, piece by piece",
 "agent loop": "you ask the model, run what it asks for, feed the result back, and repeat",
 "guard clauses": "you reject anything unsafe early and allow only what's left",
 "dedupe & clean": "real exports repeat rows and mix formats, so decide what makes a record unique before you add anything up",
 "flatten nested data": "the data is nested JSON and you need flat rows, so walk down safely with .get",
 "regex redaction": "you need to find text by its shape (an email, a phone number) and replace it",
 "evaluation metrics": "someone asks \"is it good?\" and you answer with a number you compute per case and average",
 "token bucket": "you allow bursts up to a limit but refill slowly over time",
 "filter, select, sort": "the question is \"which rows, which columns, in what order\": the same three moves in SQL, pandas and PySpark",
 "group & aggregate": "the question says per category, per customer or for each: group, then sum, count or average",
 "clean, join, aggregate": "the data is messy and split across two tables: clean first, join second, add up last",
}
assert all(p in PATWHY for p in pats), [p for p in pats if p not in PATWHY]

# ---- tables shown in SQL labs ----
TBLS = {}; tables = ""
for name in ["employees", "customers", "orders", "users", "events", "logins", "experiment", "daily"]:
    cur = db.execute(f"SELECT * FROM {name}")
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    tables += f'<p class="eyebrow">{name}</p><div class="tablebox"><table class="mini"><thead><tr>' + "".join(f"<th>{c}</th>" for c in cols) + "</tr></thead><tbody>"
    for r in rows:
        tables += "<tr>" + "".join('<td><span class="muted">NULL</span></td>' if v is None else f"<td>{html.escape(str(v))}</td>" for v in r) + "</tr>"
    tables += "</tbody></table></div>"
    TBLS[name] = tables; tables = ""

def js(v): return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")
tail = open('tail.js', encoding='utf-8').read()
import glob as _g
tail = tail.replace("/*__VIZ_EXTRA__*/", "\n".join(open(f, encoding="utf-8").read() for f in sorted(_g.glob("viz/*.js"))))
for k, v in {"__LABS__": LABS, "__SEED__": SEED, "__SEED2__": SEED2, "__UNSEEN__": UNSEEN, "__EXAMFORMS__": EXAM_FORMS, "__IVLABS__": IV, "__IVLOOPS__": IV_LOOPS, "__LESSONS__": LESSONS, "__PRO__": PRO, "__EXTRA__": EXTRA, "__SETUPS__": SETUPS, "__SPARK__": SPARK, "__TBLS__": TBLS, "__GYM__": GYM, "__GYMS__": GYMS, "__GLOSS__": GLOSS, "__STARTER__": STARTER, "__SYNCARD__": {d: [[e[0], e[1], e[2]] for e in es] for d, es in SYNCARD.items()}, "__HARNESS__": open('harness.py').read(), "__PATTERNS__": pats, "__PATWHY__": PATWHY, "__OUTCOMES__": OUTCOMES, "__WEEKSHARE__": WEEK_SHARE}.items():
    assert tail.count(k) == 1, k
    tail = tail.replace(k, js(v))

# ---- replace the script from State onward ----
a = src.index("/* ---------- State ---------- */")
b = src.index("</script>", a)
src = src[:a] + tail + "\n" + src[b:]

# ---- content fixes in DAYS ----
rep('build:"Install Python 3.12 and VS Code, then', 'build:"Phone only, no laptop? Skip the install: write the scripts in the practice lab below, which runs real Python in your browser. (Install Python from python.org and VS Code once you have a laptop, before Day 6.) With a laptop: install the latest stable Python 3 from python.org and VS Code, then')
rep('T("Return the <code>k</code> most common items in <code>nums</code> using Counter.",[`Counter(nums).most_common(k)`]',
    'T("Get the <code>k</code> most common <b>(item, count) pairs</b> in <code>nums</code> using Counter.",[`Counter(nums).most_common(k)`]')
rep('T("Push <code>x</code> onto the heap list <code>h</code>.",[`heapq.heappush(h, x)`]',
    'T("Push <code>x</code> onto the heap list <code>h</code>.",[`heapq.heappush(h, x)`,`heappush(h, x)`]')
rep('"LC 185 Department Top Three Salaries"', '"LC 185 Department Top Three Salaries (rated Hard: a stretch, skip it if stuck)"')
rep('gate:"Week 3 test: solve 2 of 3 unseen mediums in time while explaining aloud."', 'gate:"Week 3 test: 3 unseen problems (1 easy, 2 medium), 40 minutes each, explaining aloud. Pass = the easy plus one medium. Missing a medium is normal after one week of patterns: log it in your gaps list and redo it in two days."')
rep("`AnalysisException: [UNRESOLVED_COLUMN] A column with name 'amout' cannot be resolved`",
    '"AnalysisException: [UNRESOLVED_COLUMN.WITH_SUGGESTION] A column or function parameter with name `amout` cannot be resolved. Did you mean one of the following? [`amount`, `category`]"')

# ---- header: labs passed instead of XP; forgiving streak tooltip ----
rep('<div class="stat streak" title="Days in a row with practice">', '<div class="stat streak" title="Days practised in a row. One missed day a week won\'t break it.">')
rep('<div class="stat xp" title="Experience points from drills"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg><span id="xp">0</span></div>',
    '<div class="stat xp" title="Code labs passed"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M8 7l-5 5 5 5M16 7l5 5-5 5"/></svg><span id="labsN">0</span><span class="muted">labs</span></div>')

# ---- brand ----
rep('<title>Blank File</title>', '<title>ShipCode</title>')
rep('<span>&gt;_</span>Blank File</div>', '<span>&gt;_</span>ShipCode</div>')

# ---- navigation: add Think tab ----
rep('''  <a href="#errors" data-tab="errors">''', '''  <a href="#think" data-tab="think"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/></svg>Think</a>
  <a href="#errors" data-tab="errors">''')
rep('.tabs .col{display:grid;grid-template-columns:repeat(4,1fr)}', '.tabs .col{display:grid;grid-template-columns:repeat(5,1fr)} .tabs a{padding:9px 2px!important;font-size:.7rem!important} .tabs a.desk{display:none} @media (min-width:1000px){.tabs a.desk{display:flex}}')


# ---- UI refresh: week dots in the header, reference drawer, Reference tab only in the desktop sidebar ----
rep('''<a href="#ref" data-tab="ref">''', '''<a href="#ref" data-tab="ref" class="desk">''')
rep('''<div class="stat streak" title="Days practised in a row. One missed day a week won't break it.">''', '''<div class="stat streak" role="button" tabindex="0" data-hud="week" aria-label="Streak and this week" title="Tap to see this week">''')
rep('''<span id="streak">0</span><span class="muted">d</span></div>''', '''<span id="streak">0</span><span class="muted sfx">d</span><span class="wk" id="wkDots" aria-hidden="true"></span></div>''')
rep('''<span id="labsN">0</span><span class="muted">labs</span></div>''', '''<span id="labsN">0</span><span class="muted sfx">labs</span></div>
  <button class="hbtn" data-drawer="open" aria-label="Search and reference" aria-haspopup="dialog" title="Search and reference (Ctrl or Cmd + K)"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11"/></svg></button>''')
rep('''<div class="sheet" id="sheet" hidden>''', '''<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Search and reference" hidden>
  <div class="dr-back" data-drawer="close"></div>
  <div class="dr-panel" tabindex="-1"><div class="dr-head"><input id="drQ" type="search" placeholder="Search days, labs, errors" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Search"><button class="xbtn" data-drawer="close" aria-label="Close">×</button></div><div class="dr-body" id="drBody"></div></div>
</aside>
<div class="sheet" id="sheet" hidden>''')

# ---- styles for labs ----
css = r'''
.proof input{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--surface);color:inherit;font:inherit;margin:4px 0}
.proof ul{list-style:none;padding:0;margin:8px 0;display:flex;flex-direction:column;gap:4px}
.proof li.y::before{content:"✓ ";color:var(--ok);font-weight:700}.proof li.n::before{content:"✗ ";color:var(--bad);font-weight:700}
.card.back{border-left:4px solid var(--accent)}.card.back blockquote{margin:8px 0;padding-left:12px;border-left:2px solid var(--line);font-style:italic}

.runmsg{white-space:pre-wrap;word-break:break-word;max-height:9.5em;overflow:auto;font-size:.82rem;margin:6px 0}

.symrow{display:flex;gap:6px;overflow-x:auto;padding:6px 0;-webkit-overflow-scrolling:touch}
.sym{flex:0 0 auto;min-width:40px;min-height:40px;padding:0 10px;border:1px solid var(--line);border-radius:8px;background:var(--surface);font-family:var(--f-mono);font-size:1rem;color:inherit}
@media (hover:hover) and (pointer:fine){.symrow{display:none}}

.brief{margin:8px 0;padding:12px 14px;border-left:3px solid var(--accent);background:var(--accent-soft);border-radius:0 10px 10px 0}
.brief p{margin:4px 0 0;font-style:italic}
.replybox{margin-top:12px;padding:12px;border:1px dashed var(--line);border-radius:12px;display:flex;flex-direction:column;gap:6px}
.replybox p{margin:0}
.fl{display:flex;flex-direction:column;gap:5px;align-items:stretch}
.fl-n{position:relative;display:flex;justify-content:space-between;gap:8px;align-items:center;padding:7px 10px;border:2px solid var(--line);border-radius:10px;background:var(--surface);font-size:.86rem;transition:background .2s,border-color .2s}
.fl-n:not(:last-child):not(.side)::after{content:"↓";position:absolute;left:50%;bottom:-15px;color:var(--muted);font-size:.75rem}
.fl-n.side{margin-top:10px;border-style:dashed}
.fl-n.seen{border-color:var(--ok);background:var(--ok-soft)}
.fl-n.cur{border-color:var(--accent);background:var(--accent-soft);box-shadow:0 0 0 3px var(--accent-soft)}
.fl-d{font-family:var(--f-mono);font-size:.72rem;color:var(--muted);white-space:nowrap}
.linkbtn{background:none;border:0;padding:0;color:var(--accent);font:inherit;font-weight:600;cursor:pointer;text-align:left;text-decoration:underline;text-underline-offset:2px}

[hidden]{display:none!important}
/* motivation */
.hero{display:flex;flex-direction:column;gap:10px;padding-top:8px}
.hero h1{font-size:clamp(2rem,7vw,2.8rem)}
.lead{font-size:1.06rem;line-height:1.6}
.how{list-style:none;margin:0;padding:0;display:grid;gap:12px;counter-reset:h}
.how li{display:grid;grid-template-columns:34px 1fr;gap:4px 12px;counter-increment:h}
.how li::before{content:counter(h);grid-row:span 2;width:30px;height:30px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:grid;place-items:center;font-family:var(--f-mono);font-weight:500}
.how b{font-family:var(--f-display)} .how span{color:var(--muted);font-size:.95rem}
.field{display:flex;flex-direction:column;gap:8px}
.chipbtn{font:inherit;font-size:.88rem;padding:8px 14px;border-radius:99px;border:1px solid var(--line);background:var(--surface);cursor:pointer;min-height:40px}
.chipbtn.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.dayhead{display:flex;flex-direction:column;gap:8px}
.dayhead .can{font-size:1.02rem} .dayhead .can b{color:var(--ok)}
.dayhead .why{color:var(--muted);font-size:.93rem;border-left:3px solid var(--line);padding-left:10px}
.session{border:2px solid var(--accent)}
.sbar{height:10px;background:var(--line);border-radius:99px;overflow:hidden}
.sbar span{display:block;height:100%;background:var(--ok);border-radius:99px;transition:width .4s}
.parts{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.parts li{display:grid;grid-template-columns:24px 1fr auto;gap:10px;align-items:center;padding:7px 0;border-top:1px solid var(--line)}
.parts li:first-child{border-top:0}
.pk{width:22px;height:22px;border-radius:50%;border:2px solid var(--line);display:grid;place-items:center;font-size:.75rem;font-weight:700}
.parts li.done .pk{background:var(--ok);border-color:var(--ok);color:var(--surface)}
.parts li.done .pn{color:var(--muted)}
.parts li.next .pk{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.parts li.next .pn{font-weight:600}
.pt{font-family:var(--f-mono);font-size:.74rem;color:var(--muted);white-space:nowrap}
.big-cta{min-height:52px;font-size:1.02rem}
.lesson>summary{display:flex;justify-content:space-between;align-items:center;cursor:pointer;list-style:none;gap:10px}
.lesson>summary::-webkit-details-marker{display:none}
.lesson[open]>summary{margin-bottom:4px}
.selfcheck{display:flex;gap:10px;align-items:center;font-weight:500;cursor:pointer;padding-top:4px}
.selfcheck input{width:20px;height:20px;accent-color:var(--ok)}
.labrow.passed{border-color:var(--ok-soft)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px}
.stats div{background:var(--bg);border-radius:10px;padding:10px;display:flex;flex-direction:column;gap:2px;text-align:center}
.stats b{font-family:var(--f-display);font-size:1.5rem;font-variant-numeric:tabular-nums}
.stats span{font-size:.78rem;color:var(--muted)}
.heat{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-top:6px;max-width:220px}
.heat span{aspect-ratio:1;border-radius:4px;background:var(--line)}
.heat span.on{background:var(--ok)} .heat span.today{outline:2px solid var(--accent);outline-offset:1px}
.skills{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.skills li{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:start;font-size:.93rem}
.sk{font-family:var(--f-mono);font-size:.72rem;padding:2px 7px;border-radius:99px;background:var(--code);color:var(--muted);white-space:nowrap}
.sk.ok{background:var(--ok-soft);color:var(--ok)}
.skills.locked{color:var(--muted);border-top:1px dashed var(--line);padding-top:10px}
.celebrate{align-items:center;text-align:center;gap:14px;padding-top:16px}
.celebrate .stats{width:100%}
.celebrate .tomorrow,.celebrate .share,.celebrate .lvl{width:100%;text-align:left}
.share{display:flex;flex-direction:column;gap:8px}
.burst{width:84px;height:84px;border-radius:50%;background:var(--ok);color:var(--surface);display:grid;place-items:center;font-size:2.4rem;font-weight:800;animation:pop .5s cubic-bezier(.2,1.4,.4,1) both}
.levelup{background:var(--accent-soft);border-radius:12px;padding:12px 18px;width:100%}
.levelup h2{color:var(--accent)}
.fb.pass{animation:pop .35s ease-out both}
.nudge{border-left:3px solid var(--warn);background:var(--warn-soft);border-radius:8px;padding:10px 12px;display:flex;flex-direction:column;gap:4px;font-size:.92rem;margin-top:8px}
@keyframes pop{from{transform:scale(.85);opacity:0}to{transform:scale(1);opacity:1}}
@media (prefers-reduced-motion:reduce){.burst,.fb.pass{animation:none}}

/* watch it run */
.stepper{border:2px solid var(--accent);border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:10px;background:var(--surface)}
.sp-head{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.sp-head select{flex:1 1 160px;min-width:0;font:inherit;font-size:.85rem;padding:7px 8px;border-radius:8px;border:1px solid var(--line);background:var(--surface);color:var(--fg);min-height:36px}
.sp-code{padding:8px 0;max-height:260px;overflow:auto;font-size:.82rem;line-height:1.55}
.sp-code span{display:block;padding:0 12px 0 0;white-space:pre;border-left:4px solid transparent}
.sp-code i{display:inline-block;width:2.4em;text-align:right;margin-right:12px;color:var(--muted);font-style:normal;user-select:none}
.sp-code span.cur{background:var(--accent-soft);border-left-color:var(--accent);font-weight:500}
.sp-code span.ret{background:var(--ok-soft);border-left-color:var(--ok)}
.sp-code span.was{background:color-mix(in srgb,var(--line) 45%,transparent)}
.sp-note{font-size:.9rem}
.sp-vars table{min-width:0}
.sp-vars td:first-child{color:var(--accent)}
.sp-vars td{font-family:var(--f-mono);font-size:.82rem;word-break:break-word}
.sp-vars tr.chg td{background:var(--warn-soft)} .sp-vars tr.chg td:last-child{font-weight:600}
.sp-out{max-height:120px;overflow:auto;font-size:.8rem}
.sp-ctrl{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.sp-ctrl input[type=range]{flex:1 1 120px;accent-color:var(--accent);min-height:36px}
.sp-ask{background:var(--accent-soft);border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:8px}
.sp-fb{font-size:.9rem;background:var(--bg);border-radius:8px;padding:8px 10px}
.sp-end p{font-size:.92rem}
/* pattern diagrams */
.vz-open{justify-content:flex-start;text-align:left}
.vz-list{display:flex;flex-direction:column;gap:8px}
.vz-stage{display:flex;flex-direction:column;gap:14px;align-items:flex-start;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px 14px;overflow-x:auto}
.vz-say{font-size:1.02rem;line-height:1.5;min-height:3.2em}
.vz-arr{display:flex;gap:6px;padding-bottom:22px}
.vz-cell{position:relative;width:40px;height:44px;border:2px solid var(--line);border-radius:8px;display:grid;place-items:center;background:var(--bg);font-family:var(--f-mono);transition:background .25s,border-color .25s}
.vz-v{font-weight:600}
.vz-i{position:absolute;top:-17px;font-size:.66rem;color:var(--muted)}
.vz-p{position:absolute;bottom:-21px;font-family:var(--f-mono);font-size:.66rem;color:var(--accent);white-space:nowrap;font-weight:600}
.vz-cell.cur{border-color:var(--accent);background:var(--accent-soft)}
.vz-cell.hit{border-color:var(--ok);background:var(--ok-soft)}
.vz-cell.win{border-color:var(--accent)}
.vz-cell.done{opacity:.75} .vz-cell.out{opacity:.3}
.vz-box{display:flex;flex-direction:column;gap:6px}
.vz-kv{display:flex;flex-wrap:wrap;gap:6px}
.vz-pair{font-family:var(--f-mono);font-size:.82rem;padding:4px 9px;border-radius:99px;background:var(--code)}
.vz-stat{font-family:var(--f-mono);font-size:.85rem}
.vz-row{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start}
.vz-stack{display:flex;flex-direction:column-reverse;gap:4px;min-width:60px;align-items:center}
.vz-stack .eyebrow{order:-1}
.vz-sc{width:44px;height:30px;border:2px solid var(--line);border-radius:6px;display:grid;place-items:center;font-family:var(--f-mono);font-weight:600;background:var(--bg)}
.vz-sc.top{border-color:var(--accent);background:var(--accent-soft)}
.vz-stack{flex-direction:column}
.vz-tree{width:100%;max-width:380px;height:auto}
.vz-tree line{stroke:var(--line);stroke-width:2}
.vz-node circle{fill:var(--bg);stroke:var(--line);stroke-width:2}
.vz-node text{font-family:var(--f-mono);font-size:10px;text-anchor:middle;fill:var(--muted)}
.vz-node.call circle{stroke:var(--accent);fill:var(--accent-soft)} .vz-node.call text{fill:var(--fg)}
.vz-node.done circle{stroke:var(--ok);fill:var(--ok-soft)} .vz-node.done text{fill:var(--fg)}
.vz-node text.vz-ret{fill:var(--ok);font-weight:700}
.vz-grid{display:grid;gap:4px}
.vz-g{width:34px;height:34px;border-radius:6px;display:grid;place-items:center;font-family:var(--f-mono);font-size:.8rem;border:2px solid transparent}
.vz-g.water{background:var(--code);color:var(--muted)} .vz-g.land{background:var(--line)}
.vz-g.isl0{background:var(--accent-soft);color:var(--accent)} .vz-g.isl1{background:var(--ok-soft);color:var(--ok)} .vz-g.isl2{background:var(--warn-soft);color:var(--warn)}
.vz-g.cur{border-color:var(--fg)}
.vz-t{min-width:0;width:auto} .vz-t td,.vz-t th{padding:4px 9px}
.vz-t tr.cur td{background:var(--accent-soft)} .vz-t tr.hit td{background:var(--ok-soft)} .vz-t tr.gone td{opacity:.3;text-decoration:line-through}
.vz-t td:first-child{color:var(--fg)}
.null{color:var(--bad);font-family:var(--f-mono);font-weight:600}

/* readiness, reps, journal, rebuild */
.areas{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.areas li{display:flex;flex-direction:column;gap:4px}
.areas .an{display:flex;justify-content:space-between;gap:10px;font-size:.92rem;font-weight:500}
.areas li.upcoming .an,.areas li.upcoming .pmeta{color:var(--muted)}.areas li.upcoming .sbar{opacity:.6}
.areas li.ready .sbar span{background:var(--ok)} .areas li.solid .sbar span{background:var(--accent)} .areas li.building .sbar span{background:var(--warn)}
.sbar.sm{height:6px}
.jl{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.jl li{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:8px 0;border-top:1px solid var(--line)}
.jl li:first-child{border-top:0}
#ltimer.over{color:var(--warn);font-weight:600}
.hint.warn{color:var(--warn);font-weight:500}
.pz{border:2px dashed var(--warn);border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:10px}
.pz-chosen{margin:0;padding-left:26px;display:flex;flex-direction:column;gap:4px}
.pz-pool{display:flex;flex-direction:column;gap:4px;border-top:1px dashed var(--line);padding-top:8px}
.pzl{width:100%;text-align:left;font-family:var(--f-mono);font-size:.8rem;white-space:pre;overflow-x:auto;padding:7px 10px;border:2px solid var(--line);border-radius:8px;background:var(--surface);cursor:pointer;min-height:36px}
.pzl:hover{border-color:var(--accent)} .pzl.right{border-color:var(--ok);background:var(--ok-soft)} .pzl.wrong{border-color:var(--bad);background:var(--bad-soft)}
/* labs */
.warm{border-left:3px solid var(--warn)}
.labs{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.labrow{width:100%;display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:center;text-align:left;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);cursor:pointer;min-height:48px}
.labrow:hover{border-color:var(--accent)}
.lk{font-family:var(--f-mono);font-size:.7rem;letter-spacing:.05em;text-transform:uppercase;color:var(--accent);white-space:nowrap}
.lt{font-weight:600;min-width:0;overflow-wrap:anywhere}
.expect summary,.card details summary,details.tables summary{cursor:pointer;font-weight:600}
.expect ul{margin-top:8px}
.phasebar{flex:1;display:flex;gap:4px;min-width:0}
.phasebar span{flex:1;text-align:center;font-family:var(--f-mono);font-size:.68rem;padding:4px 2px;border-radius:6px;background:var(--line);color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.phasebar span.on{background:var(--accent);color:var(--accent-ink)} .phasebar span.done{background:var(--ok-soft);color:var(--ok)}
.plan{margin:0;padding-left:22px;display:flex;flex-direction:column;gap:6px}
.plan .empty{list-style:none;margin-left:-22px}
.pool{display:flex;flex-direction:column;gap:8px;border-top:1px dashed var(--line);padding-top:10px}
.stepbtn{width:100%;text-align:left;padding:10px 12px;border:2px solid var(--line);border-radius:10px;background:var(--surface);cursor:pointer;font-size:.92rem;min-height:44px}
.stepbtn:hover{border-color:var(--accent)} .stepbtn.right{border-color:var(--ok);background:var(--ok-soft)} .stepbtn.wrong{border-color:var(--bad);background:var(--bad-soft)}
input.code{width:100%;font-family:var(--f-mono);font-size:.95rem;padding:12px;border-radius:12px;border:2px solid var(--line);background:var(--surface);color:var(--fg);min-height:48px}
input.code:focus{border-color:var(--accent);outline:none}
textarea.code.small{min-height:80px}
.ed{display:grid;grid-template-columns:auto 1fr;border:2px solid var(--line);border-radius:12px;overflow:hidden;background:var(--surface)}
.ed:focus-within{border-color:var(--accent)}
.gutter{margin:0;padding:12px 8px;background:var(--code);color:var(--muted);text-align:right;user-select:none;overflow:hidden;border-radius:0;font-size:.85rem;line-height:1.5;min-width:2.6em;height:340px}
.codearea{display:block;width:100%;height:340px;resize:vertical;border:0;outline:none;padding:12px;font-family:var(--f-mono);font-size:.85rem;line-height:1.5;background:transparent;color:var(--fg);white-space:pre;overflow:auto;tab-size:4}
.tests{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.tests li{display:grid;grid-template-columns:20px 1fr;gap:8px;min-width:0}
.tests li div{min-width:0;display:flex;flex-direction:column;gap:4px}
.tests .mark{font-weight:700} .tests .pass .mark{color:var(--ok)} .tests .fail .mark{color:var(--bad)}
pre.tb{color:var(--bad);background:var(--surface)}
.cmp pre{background:var(--surface)}
table.mini{min-width:0;font-size:.8rem} table.mini td,table.mini th{padding:5px 8px} table.mini td:first-child{color:var(--fg)}
details.tables{display:flex;flex-direction:column;gap:6px}
details.tables .tablebox{margin-bottom:8px}
.method{margin:0;padding-left:22px;display:flex;flex-direction:column;gap:8px}
.editor-card{gap:10px}
@media (max-width:420px){.gutter,.codearea{height:300px}}
'''
rep('@media (prefers-reduced-motion:reduce)', css + '@media (prefers-reduced-motion:reduce)')

# ---- modern theme (modern.css) and font swap ----
import re as _re
modern = open('modern.css', encoding='utf-8').read()
modern += "\n".join(open(f, encoding='utf-8').read() for f in sorted(_g.glob('viz/*.css')))
rep('</style>', modern + '</style>')
_n = len(src)
src = _re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=Bricolage[^"]*">', '', src)   # fonts are self-hosted now (see @font-face in modern.css)
assert len(src) != _n, 'font link not swapped'

if not src.startswith('<meta charset'):
    src = '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n' + src
open('index_new.html', 'w', encoding='utf-8').write(src)
print('built', len(src), 'bytes;', sum(len(v) for v in LABS.values()), 'labs;', len(pats), 'patterns')
