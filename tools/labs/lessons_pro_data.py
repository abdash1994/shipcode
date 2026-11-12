# Data Engineering Pro track: Redis, batch pipelines, orchestration, streaming, warehouses, data quality.
# Exec'd inside lessons.py after the helpers (S, Sd, Q, QE, QC, W, PM) and lessons_py2.py (Sh, Qh, Wh) exist.
# Everything that needs a real service (Redis, Kafka, Airflow, dbt) is display-only (Sd). The practice tasks run on small
# pure-Python models of those systems. Names in this file start with _DE to stay clear of the shared namespace.

# =====================================================================================================
# 1. Redis
# =====================================================================================================
_DE_FR = '''class FakeRedis:
    """A tiny model of Redis. Time is a plain number that YOU move forward with tick()."""
    def __init__(self):
        self.now = 0          # the clock, in seconds
        self.data = {}        # key -> value
        self.exp = {}         # key -> the clock value at which it expires

    def tick(self, seconds):
        self.now += seconds

    def _alive(self, key):
        if key in self.exp and self.exp[key] <= self.now:
            self.data.pop(key, None)
            self.exp.pop(key, None)
        return key in self.data

    def set(self, key, value, ex=None):
        self.data[key] = value
        self.exp.pop(key, None)              # a plain SET clears any old expiry
        if ex is not None:
            self.exp[key] = self.now + ex

    def get(self, key):
        return self.data[key] if self._alive(key) else None

    def delete(self, key):
        if self._alive(key):
            del self.data[key]
            self.exp.pop(key, None)
            return 1
        return 0

    def incr(self, key):
        n = int(self.data[key]) + 1 if self._alive(key) else 1
        self.data[key] = n                   # INCR keeps the existing expiry
        return n

    def expire(self, key, seconds):
        if not self._alive(key):
            return 0
        self.exp[key] = self.now + seconds
        return 1

    def ttl(self, key):
        if not self._alive(key):
            return -2                        # no such key
        if key not in self.exp:
            return -1                        # key exists, never expires
        return self.exp[key] - self.now

    # sorted set: member -> score
    def zadd(self, key, score, member):
        if not self._alive(key):
            self.data[key] = {}
        added = member not in self.data[key]
        self.data[key][member] = score
        return 1 if added else 0

    def zincrby(self, key, amount, member):
        if not self._alive(key):
            self.data[key] = {}
        self.data[key][member] = self.data[key].get(member, 0) + amount
        return self.data[key][member]

    def zrange(self, key, start, stop, rev=False, withscores=False):
        if not self._alive(key):
            return []
        items = sorted(self.data[key].items(), key=lambda kv: (kv[1], kv[0]))
        if rev:
            items.reverse()
        n = len(items)
        if start < 0:
            start = max(n + start, 0)
        if stop < 0:
            stop = n + stop
        items = items[start:stop + 1]        # stop is INCLUDED, like Redis
        return items if withscores else [m for m, s in items]
'''

_DE_FR_PRE = _DE_FR + '''
def raises(fn, exc=Exception):
    try:
        fn()
    except exc:
        return True
    return False
'''

_DE_CACHE_PRE = _DE_FR_PRE + '''
def scenario_cache():
    r = FakeRedis()
    calls = []
    def loader(key):
        calls.append(key)
        return None if key == "user:404" else "row-" + key
    a = get_cached(r, "user:1", loader, 60)
    b = get_cached(r, "user:1", loader, 60)
    after_two = len(calls)
    r.tick(59)
    get_cached(r, "user:1", loader, 60)
    still_cached = len(calls)
    r.tick(1)                                  # 60 seconds have passed: the entry is gone
    d = get_cached(r, "user:1", loader, 60)
    after_expiry = len(calls)
    ttl_after_refill = r.ttl("user:1")
    m1 = get_cached(r, "user:404", loader, 60)
    m2 = get_cached(r, "user:404", loader, 60)
    return dict(a=a, b=b, after_two=after_two, still_cached=still_cached, d=d, after_expiry=after_expiry,
                ttl=ttl_after_refill, miss=[m1, m2], miss_calls=len(calls) - after_expiry, has_404=r.get("user:404"))
'''

_DE_RATE_PRE = _DE_FR_PRE + '''
def scenario_rate(limit, window, steps):
    """steps: list of (seconds_to_wait_first, user). Returns the allow/deny answer for each call."""
    r = FakeRedis()
    out = []
    for wait, user in steps:
        r.tick(wait)
        out.append(allow(r, user, limit, window))
    return out
'''

_DE_BOARD_PRE = _DE_FR_PRE + '''
def scenario_board():
    r = FakeRedis()
    add_points(r, "lb", "asha", 50)
    add_points(r, "lb", "ravi", 70)
    add_points(r, "lb", "meera", 50)
    add_points(r, "lb", "asha", 30)
    return r
'''

PM("de-redis", "Data Engineering Pro", "Redis and caching",
   "Redis sits in front of almost every busy database as a cache, a rate limiter or a queue, and interviewers love asking how you would use it.",
 [
 Sd("What Redis is, and why it is fast",
    "<b>Redis</b> is a database that keeps its data <b>in memory</b> (RAM) instead of on disk, and stores it as <b>keys</b> that point to <b>values</b>, a bit like a giant Python dict that many programs can share over the network. Reading RAM is far faster than reading a disk, so Redis answers in a fraction of a millisecond to a few milliseconds. The trade-off: RAM is smaller and pricier than disk, so you keep in Redis only what needs to be fast: copies of hot data (a <b>cache</b>), counters, queues, leaderboards, sessions. The slow, permanent record usually stays in a normal database such as Postgres. You talk to Redis with short <b>commands</b>, from <code>redis-cli</code> or from a client library. To run a real one on your laptop you need Docker (the lines below are for you to try later; this page cannot run them):",
    "# start a Redis server in a container, then open its command line\n"
    "docker run -d --name my-redis -p 6379:6379 redis\n"
    "docker exec -it my-redis redis-cli\n"
    "\n"
    "# inside redis-cli:\n"
    "127.0.0.1:6379> PING\n"
    "PONG",
    q=QC("Why do teams put Redis in front of a slow database?", ["Repeated reads can be answered from fast memory instead of hitting the database every time", "Redis is the permanent home of all company data", "Redis makes SQL queries shorter"], 0,
         "Redis is a fast, in-memory copy for hot data. The permanent record stays in the main database.")),
 Sd("Strings, expiry and counters",
    "The simplest value is a <b>string</b> (any text or number). <code>SET key value</code> stores it and <code>GET key</code> reads it. Adding <code>EX seconds</code> gives the key a lifetime: when it runs out, Redis deletes the key by itself. That self-cleaning is the heart of caching. <code>TTL key</code> (time to live) tells you the seconds left: <b>-1</b> means the key never expires, <b>-2</b> means the key does not exist. <code>EXPIRE key seconds</code> sets a lifetime on an existing key and <code>DEL key</code> removes a key. <code>INCR key</code> adds 1 to a number stored as a string and returns the new value (a missing key counts as 0, so the first INCR returns 1). Because Redis runs one command at a time, an INCR is never half-done and two programs calling it together never lose a count.",
    "SET greeting hello EX 60     -> OK\n"
    "GET greeting                 -> \"hello\"\n"
    "TTL greeting                 -> (integer) 58     # seconds left\n"
    "INCR page:views              -> (integer) 1\n"
    "INCR page:views              -> (integer) 2\n"
    "EXPIRE page:views 3600       -> (integer) 1      # 1 = done, 0 = no such key\n"
    "DEL greeting                 -> (integer) 1\n"
    "GET greeting                 -> (nil)            # nil = nothing there",
    q=QC("A key was created with <code>SET token abc EX 30</code>. What does <code>GET token</code> return 31 seconds later?", ["(nil), because the key expired and was deleted", "\"abc\", because keys are kept for ever", "An error"], 0,
         "EX 30 means the key lives for 30 seconds. After that it behaves as if it was never set: GET gives nil.")),
 S("A model you can run: FakeRedis",
   "Real Redis needs a server, so here you practise on <b>FakeRedis</b>, a small Python class that copies the behaviour of the commands above. <b>Be clear about what it is: a teaching model.</b> It is not Redis. It has no network, no persistence and only a few commands, and its clock is just a number you move with <code>tick()</code>, so the examples are repeatable. Once you understand the ideas, try the real thing with Docker and <code>redis-cli</code>. Read the class, run it, and notice how expiry works: a key remembers <i>the clock value when it dies</i>, and every read first checks that.",
   _DE_FR + '''
r = FakeRedis()
r.set("greeting", "hello", ex=60)
print(r.get("greeting"), r.ttl("greeting"))
r.tick(45)
print(r.get("greeting"), r.ttl("greeting"))
r.tick(15)
print(r.get("greeting"), r.ttl("greeting"))
print(r.incr("views"), r.incr("views"), r.ttl("views"))''', run=True,
   q=Q("What does this show? (FakeRedis is defined above; the clock starts at 0.)", _DE_FR + '''
r = FakeRedis()
r.set("k", "v", ex=10)
r.tick(4)
r.expire("k", 10)
r.tick(8)
print(r.get("k"), r.ttl("k"))''', ["v 2", "None -2", "v 6"], "EXPIRE restarts the timer: at clock 4 the key was given 10 more seconds, so it dies at clock 14. At clock 12 it is alive with 2 seconds left.")),
 Sd("Hashes, lists, sets and sorted sets",
    "Besides strings, Redis has <b>data structures</b>, each with its own commands. A <b>hash</b> is a small dict stored under one key (a record: <code>HSET user:1 name Asha city Pune</code>). A <b>list</b> is an ordered list you push to and pop from at either end, which makes it a simple <b>queue</b>. A <b>set</b> holds unique values with no order (tags, unique visitors). A <b>sorted set</b> holds unique members, each with a numeric <b>score</b>, always kept in score order. Sorted sets are the classic way to build a <b>leaderboard</b>: ZADD to add or change a score, ZRANGE to read a slice by rank. In a sorted set, members with equal scores are ordered alphabetically. Key names like <code>user:1</code> are only a convention (a colon to group), Redis does not treat them specially.",
    "HSET user:1 name Asha city Pune       -> (integer) 2\n"
    "HGET user:1 city                      -> \"Pune\"\n"
    "HGETALL user:1                        -> name, Asha, city, Pune\n"
    "\n"
    "LPUSH jobs job-a                      -> (integer) 1   # push on the left\n"
    "LPUSH jobs job-b                      -> (integer) 2\n"
    "RPOP jobs                             -> \"job-a\"       # pop from the right: first in, first out\n"
    "\n"
    "SADD tags python redis python         -> (integer) 2   # the repeat is ignored\n"
    "SMEMBERS tags                         -> python, redis\n"
    "\n"
    "ZADD board 100 asha 80 ravi           -> (integer) 2   # score first, then member\n"
    "ZRANGE board 0 -1 WITHSCORES          -> ravi, 80, asha, 100   # lowest score first\n"
    "ZRANGE board 0 1 REV WITHSCORES       -> asha, 100, ravi, 80   # REV = highest first (check the docs for your version)",
    q=QC("You push job-a, then job-b with LPUSH, then call RPOP. Which job comes out, and why does this behave like a queue?", ["job-a: pushes go in at one end and pops come out of the other, so the oldest leaves first", "job-b: the newest always leaves first", "Both at once"], 0,
         "LPUSH adds on the left and RPOP removes from the right, so the first item pushed is the first popped (first in, first out).")),
 S("Pattern 1: cache-aside",
   "The most common use of Redis. The program (not Redis) is in charge: (1) look in the cache; (2) if found, a <b>hit</b>, use it; (3) if not, a <b>miss</b>: ask the slow database, (4) store the answer in the cache with a <b>TTL</b>, (5) return it. The TTL limits how stale the copy can get. Write the steps as a function that takes a <code>loader</code> (the slow call) so the cache logic stays separate from the database.",
   '''cache = {}
db_calls = []

def slow_db(key):
    db_calls.append(key)
    return "row-for-" + key

def get_with_cache(key):
    if key in cache:
        return cache[key]          # hit
    value = slow_db(key)           # miss: go to the database
    cache[key] = value
    return value

get_with_cache("u1"); get_with_cache("u1"); get_with_cache("u2")
print(len(db_calls), db_calls)''', run=True,
   q=W("Write <code>get_cached(r, key, loader, ttl)</code> using the <code>FakeRedis</code> object <code>r</code> (already defined for you). Return <code>r.get(key)</code> if it is there. Otherwise call <code>loader(key)</code>; if the loader returns something other than <code>None</code>, store it with <code>r.set(key, value, ex=ttl)</code>. Return the value (or <code>None</code> when the loader finds nothing; do not cache that).",
       "def get_cached(r, key, loader, ttl):\n    # 1. try the cache\n    # 2. on a miss call loader(key)\n    # 3. cache it with the ttl unless it is None\n    pass\n",
       "def get_cached(r, key, loader, ttl):\n    value = r.get(key)\n    if value is not None:\n        return value\n    value = loader(key)\n    if value is not None:\n        r.set(key, value, ex=ttl)\n    return value\n",
       exprs=[("first two reads give the same value, one database call", "[scenario_cache()['a'], scenario_cache()['b'], scenario_cache()['after_two']]"),
              ("still cached just before the TTL runs out", "scenario_cache()['still_cached']"),
              ("after the TTL it loads again and the new copy has a full TTL", "[scenario_cache()['d'], scenario_cache()['after_expiry'], scenario_cache()['ttl']]"),
              ("a missing row returns None and is not cached", "[scenario_cache()['miss'], scenario_cache()['miss_calls'], scenario_cache()['has_404']]")],
       hint="value = r.get(key); if value is not None: return it. Otherwise value = loader(key), then r.set(key, value, ex=ttl) only when value is not None.",
       prelude=_DE_CACHE_PRE)),
 S("Caching traps: stale data, stampede, eviction",
   "Caching is easy to start and hard to get right. <b>Invalidation</b>: when the database row changes, the cached copy is now wrong. You can delete the key on every write, or accept staleness up to the TTL; a famous joke says naming things and cache invalidation are the two hard problems. <b>Cache stampede</b>: a popular key expires and 1000 requests all miss at once and hit the database together. Fixes: add a little random jitter to TTLs, let only one request rebuild the value (a lock), or refresh before expiry. <b>Eviction</b>: memory is finite. When Redis hits its <code>maxmemory</code> limit it removes keys according to a policy such as <code>allkeys-lru</code> (drop the least recently used); check the docs for the policy list. The idea behind LRU is below. Another pattern, <b>write-through</b>, updates the cache and the database together on each write so reads are always fresh, at the cost of slower writes.",
   '''from collections import OrderedDict

class LRU:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = OrderedDict()
    def get(self, key):
        if key not in self.items:
            return None
        self.items.move_to_end(key)           # now the most recently used
        return self.items[key]
    def put(self, key, value):
        self.items[key] = value
        self.items.move_to_end(key)
        if len(self.items) > self.capacity:
            self.items.popitem(last=False)    # drop the least recently used

c = LRU(2)
c.put("a", 1); c.put("b", 2)
c.get("a")             # touch a
c.put("c", 3)          # over capacity: b is the oldest unused
print(list(c.items))''', run=True,
   q=QC("A product page key expires at noon and 2000 requests arrive in that second. What is the problem called, and what is one fix?", ["A cache stampede; add jitter to TTLs or let only one request rebuild the value", "A memory leak; restart Redis", "A deadlock; add more RAM"], 0,
        "Many simultaneous misses on one hot key all go to the database. Spread out expiry times or make a single request do the rebuild.")),
 S("Pattern 2: a rate limiter with INCR and EXPIRE",
   "To allow at most N requests per user per time window, count them in Redis. The <b>fixed-window</b> recipe: key = <code>rate:&lt;user&gt;</code>. On each request, <code>INCR</code> it. If the result is <b>1</b> (the first request of the window), also set <code>EXPIRE key window_seconds</code> so the counter vanishes when the window ends. Allow the request if the count is at most the limit. Weakness: a burst at the end of one window plus the start of the next can briefly double the allowed rate. In a real system, make INCR and EXPIRE atomic (a script, or <code>SET key 0 EX window NX</code> before INCR; check the docs), otherwise a crash between the two lines leaves a counter that never expires.",
   q=W("Write <code>allow(r, user, limit, window)</code> using <code>r</code> (FakeRedis). Use the key <code>'rate:' + user</code>. Call <code>r.incr</code>; when the count is exactly 1, call <code>r.expire(key, window)</code>. Return <code>True</code> if the count is at most <code>limit</code>, otherwise <code>False</code>.",
       "def allow(r, user, limit, window):\n    key = 'rate:' + user\n    # incr, set the expiry on the first request, compare with limit\n    pass\n",
       "def allow(r, user, limit, window):\n    key = 'rate:' + user\n    n = r.incr(key)\n    if n == 1:\n        r.expire(key, window)\n    return n <= limit\n",
       exprs=[("4 quick calls, limit 3", "scenario_rate(3, 10, [(0, 'asha')] * 4)"),
              ("window ends, the counter resets", "scenario_rate(2, 10, [(0, 'a'), (0, 'a'), (0, 'a'), (9, 'a'), (1, 'a'), (0, 'a'), (0, 'a')])"),
              ("each user has their own counter", "scenario_rate(1, 5, [(0, 'a'), (0, 'b'), (0, 'a'), (0, 'b')])"),
              ("limit 0 blocks everyone", "scenario_rate(0, 5, [(0, 'a')])")],
       hint="n = r.incr(key); if n == 1: r.expire(key, window); return n <= limit",
       prelude=_DE_RATE_PRE)),
 Sd("Pub/sub, queues and persistence",
    "<b>Pub/sub</b> (publish/subscribe): programs <code>SUBSCRIBE</code> to a named <b>channel</b>, and anyone can <code>PUBLISH</code> a message to it; every subscriber connected at that moment receives it. It is fire-and-forget: Redis does not store the message, so a subscriber that is offline misses it. For work you must not lose, use a list as a queue (<code>LPUSH</code> to add, <code>BRPOP</code> to wait for the next job) or look at Redis Streams in the docs. <b>Persistence</b>: memory vanishes when a server restarts, so Redis can save to disk in two ways. <b>RDB</b> takes a snapshot of the whole dataset every so often: small files, fast restarts, but you can lose the last few minutes. <b>AOF</b> (append-only file) logs every write so the data can be rebuilt on start: more durable, bigger files. The Redis docs say to use both if you want safety close to a normal database, and RDB alone if losing a few minutes is acceptable. Redis executes commands one after another on a main thread, which is why single commands like INCR are atomic and why one slow command blocks everyone; check the docs for what newer versions do with extra I/O threads.",
    "# terminal 1\nSUBSCRIBE alerts\n\n# terminal 2\nPUBLISH alerts \"disk almost full\"    -> (integer) 1   # number of subscribers that got it\n\n# a simple job queue\nLPUSH jobs \"resize:42\"\nBRPOP jobs 5          # wait up to 5 seconds for a job\n\n# redis.conf (persistence)\nsave 60 1000          # RDB: snapshot if 1000 keys changed in 60 s\nappendonly yes        # AOF on",
    q=QC("A payment job must not be lost even if the worker is down for an hour. Which Redis feature fits worse?", ["Pub/sub, because messages are not stored for subscribers that are offline", "A list used as a queue", "AOF persistence"], 0,
         "Pub/sub only delivers to subscribers connected right now. A list (or a stream) keeps the job until a worker takes it.")),
 S("Final task: a leaderboard with sorted sets",
   "Games, quizzes and sales dashboards all need a ranked list that updates live. A sorted set does it: <code>ZINCRBY key amount member</code> adds to a score, <code>ZRANGE key 0 n-1 REV WITHSCORES</code> reads the top n. In FakeRedis these are <code>r.zincrby(key, amount, member)</code> and <code>r.zrange(key, start, stop, rev=True, withscores=True)</code>. Remember <code>stop</code> is <b>included</b>, and <code>-1</code> means \"to the end\". Equal scores are ordered alphabetically, and with <code>rev=True</code> that order is reversed.",
   q=W("Write three functions using <code>r</code> (FakeRedis): <code>add_points(r, board, player, points)</code> returns the new score (use <code>zincrby</code>). <code>top(r, board, n)</code> returns the top <code>n</code> as a list of <code>(player, score)</code> pairs, highest first (<code>[]</code> when <code>n</code> is 0 or less; careful, a stop of -1 would mean everything). <code>rank(r, board, player)</code> returns the player's 1-based rank (1 = top) or <code>None</code> if the player is not on the board.",
       "def add_points(r, board, player, points):\n    pass\n\ndef top(r, board, n):\n    pass\n\ndef rank(r, board, player):\n    pass\n",
       "def add_points(r, board, player, points):\n    return r.zincrby(board, points, player)\n\ndef top(r, board, n):\n    if n <= 0:\n        return []\n    return r.zrange(board, 0, n - 1, rev=True, withscores=True)\n\ndef rank(r, board, player):\n    players = r.zrange(board, 0, -1, rev=True)\n    return players.index(player) + 1 if player in players else None\n",
       exprs=[("scores add up", "scenario_board().zrange('lb', 0, -1, withscores=True)"),
              ("top 2", "top(scenario_board(), 'lb', 2)"),
              ("top more than exist", "top(scenario_board(), 'lb', 10)"),
              ("top 0 is empty", "top(scenario_board(), 'lb', 0)"),
              ("ranks (asha 80, ravi 70, meera 50)", "[rank(scenario_board(), 'lb', p) for p in ['asha', 'ravi', 'meera', 'nobody']]"),
              ("empty board", "[top(FakeRedis(), 'x', 3), rank(FakeRedis(), 'x', 'a')]"),
              ("new points keep adding", "add_points(scenario_board(), 'lb', 'ravi', 15)")],
       hint="top: if n <= 0 return []; else r.zrange(board, 0, n-1, rev=True, withscores=True). rank: get all players with rev=True and use list.index.",
       prelude=_DE_BOARD_PRE)),
])

# =====================================================================================================
# 2. Batch pipelines
# =====================================================================================================
_DE_BATCH_PRE = '''import pandas as pd
EVENTS = pd.DataFrame({'id': [1, 2, 3, 4, 5],
                       'updated': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-03', '2025-01-05'],
                       'amount': [10, 20, 30, 40, 50]})
EVENTS2 = pd.DataFrame({'id': [7, 8], 'updated': ['2024-12-30', '2024-12-31'], 'amount': [1, 2]})
TARGET = pd.DataFrame({'id': [1, 2, 3], 'updated': ['2025-01-01', '2025-01-01', '2025-01-02'], 'amount': [10, 20, 30]})
SOURCE = pd.DataFrame({'id': [2, 3, 4, 4, 1],
                       'updated': ['2025-01-03', '2025-01-02', '2025-01-03', '2025-01-04', '2024-12-01'],
                       'amount': [25, 99, 40, 45, 5]})
'''

PM("de-batch", "Data Engineering Pro", "Batch pipelines",
   "Nightly and hourly batch jobs still move most of the world's analytics data, and the interview questions are about making them safe to re-run.",
 [
 S("ETL or ELT: where does the transform happen?",
   "A <b>batch pipeline</b> moves data in chunks on a schedule (every hour, every night) instead of record by record. Three stages: <b>Extract</b> (read from a source such as a database, an API or files), <b>Transform</b> (clean, join, reshape), <b>Load</b> (write to the destination, usually a warehouse). In <b>ETL</b> you transform <i>before</i> loading, on your own servers or tool. In <b>ELT</b> you load the raw data into the warehouse first and transform it <i>there</i> with SQL. ELT became popular because modern warehouses are powerful and cheap to scale, and keeping the raw copy means you can re-transform later when the rules change. ETL still fits when data must be cleaned or masked (for example removing personal details) before it may be stored at all.",
   q=QC("Raw JSON files are loaded untouched into warehouse tables, and SQL models later turn them into clean tables. Which pattern is this?", ["ELT: load first, transform inside the warehouse", "ETL: transform before loading", "Streaming"], 0,
        "Loading the raw data first and transforming it afterwards inside the warehouse is ELT.")),
 S("Idempotent loads: run it twice, get the same result",
   "Jobs fail halfway and get re-run, or someone presses the button twice. A load is <b>idempotent</b> if running it again with the same input leaves the destination exactly as if it ran once. <b>Appending</b> is not idempotent: a re-run duplicates every row. Two safe designs: <b>overwrite the partition</b> (replace everything for that day with the new result) or <b>upsert by key</b> (update the row if the key exists, insert if not). Compare them:",
   '''table = []
def load_append(rows):
    table.extend(rows)

batch = [{"id": 1, "v": 10}, {"id": 2, "v": 20}]
load_append(batch)
load_append(batch)                 # a retry
print("append:", len(table))

by_id = {}
def load_upsert(rows):
    for r in rows:
        by_id[r["id"]] = r

load_upsert(batch)
load_upsert(batch)                 # the same retry
print("upsert:", len(by_id))''', run=True,
   q=Q("What does this show?", '''warehouse = {"2025-01-01": [1, 2, 3]}
def load_partition(day, rows):
    warehouse[day] = list(rows)

load_partition("2025-01-02", [5, 6])
load_partition("2025-01-02", [5, 6])
print(sum(len(v) for v in warehouse.values()))''', ["5", "7", "2"], "Loading a day replaces that day's list, so the retry changes nothing: 3 rows for the first day plus 2 for the second.")),
 Sh("Upsert and dedupe-by-latest in pandas",
   "<b>Upsert</b> = update + insert. With two DataFrames, stack them (<code>pd.concat</code>), then keep one row per key with <code>drop_duplicates(subset='id', keep='last')</code>. <code>keep='last'</code> keeps the row that came <i>later in the stack</i>, so put the new data second. The same call is how you do <b>dedupe by latest</b> when a source sends several versions of a record: first <code>sort_values</code> by the timestamp column, then keep the last row per id. Always sort before relying on <code>keep</code>.",
   "import pandas as pd\n\nold = pd.DataFrame({'id': [1, 2, 3], 'city': ['Pune', 'Delhi', 'Goa']})\nnew = pd.DataFrame({'id': [2, 4], 'city': ['Mumbai', 'Jaipur']})\n\nout = pd.concat([old, new]).drop_duplicates(subset='id', keep='last').sort_values('id')\nprint(out.to_string(index=False))", run=True,
   q=Qh("What does this show? (Predict which row survives.)", "import pandas as pd\nold = pd.DataFrame({'id': [1, 2], 'city': ['Pune', 'Delhi']})\nnew = pd.DataFrame({'id': [2], 'city': ['Mumbai']})\nout = pd.concat([old, new]).drop_duplicates(subset='id', keep='first')\nprint(out[out['id'] == 2]['city'].iloc[0])", ["Delhi", "Mumbai", "Pune"], "keep='first' keeps the earlier copy, so the old Delhi row wins and the update is lost. For an upsert you want keep='last' with the new data stacked second.")),
 S("Incremental loads and the watermark",
   "Re-reading the whole source every night gets slow and expensive. An <b>incremental load</b> only reads rows that are new or changed since last time. The pipeline remembers a <b>watermark</b>: the highest <code>updated_at</code> it has already processed. Next run: read rows with <code>updated_at</code> greater than the watermark, process them, then move the watermark forward to the highest value just seen. Two real-world problems. (1) <b>Ties and late-arriving data</b>: a row stamped inside the already-processed range can show up late (a slow upstream system, a timezone mistake). A common safeguard is a <b>lookback</b>: read from a little before the watermark and rely on an idempotent upsert so the overlap does no harm. (2) <b>Backfill</b> (below) is how you fix history.",
   '''rows = [
    {"id": 1, "updated": "2025-01-01"},
    {"id": 2, "updated": "2025-01-02"},
    {"id": 3, "updated": "2025-01-03"},
]
watermark = "2025-01-01"

def run_once(watermark):
    new = [r for r in rows if r["updated"] > watermark]
    if new:
        watermark = max(r["updated"] for r in new)
    return len(new), watermark

n, watermark = run_once(watermark)
print(n, watermark)
n, watermark = run_once(watermark)      # nothing new: the run is harmless
print(n, watermark)''', run=True,
   q=Q("What does this show?", '''rows = [{"u": 5}, {"u": 7}, {"u": 7}]
wm = 5
new = [r for r in rows if r["u"] > wm]
print(len(new), max(r["u"] for r in new))''', ["2 7", "3 7", "1 7"], "Only the two rows with u = 7 are above the watermark of 5, and the highest value seen is 7.")),
 Sh("Your turn: the watermark filter",
   "Write the two small functions every incremental job has. ISO dates like <code>'2025-01-03'</code> compare correctly as plain text, so you can compare the column to a string directly.",
   q=Wh("Write <code>new_rows(df, watermark)</code> returning the rows of <code>df</code> whose <code>updated</code> is <b>greater than</b> <code>watermark</code> (a string), and <code>next_watermark(df, current)</code> returning the largest <code>updated</code> in <code>df</code>, or <code>current</code> unchanged when <code>df</code> is empty. (<code>pd</code> is already imported.)",
       "def new_rows(df, watermark):\n    pass\n\ndef next_watermark(df, current):\n    pass\n",
       "def new_rows(df, watermark):\n    return df[df['updated'] > watermark]\n\ndef next_watermark(df, current):\n    if len(df) == 0:\n        return current\n    return df['updated'].max()\n",
       [("ids after the watermark", "new_rows(EVENTS, '2025-01-02')['id'].tolist()"),
        ("equal to the watermark is not new", "new_rows(EVENTS, '2025-01-05')['id'].tolist()"),
        ("nothing new", "len(new_rows(EVENTS2, '2025-01-01'))"),
        ("moves forward", "next_watermark(new_rows(EVENTS, '2025-01-02'), '2025-01-02')"),
        ("stays when empty", "next_watermark(new_rows(EVENTS2, '2025-01-01'), '2025-01-01')")],
       _DE_BATCH_PRE, "df[df['updated'] > watermark] filters; df['updated'].max() is the new watermark; guard the empty case with len(df) == 0.")),
 S("Partitions and backfills",
   "Batch data is almost always <b>partitioned by date</b>: stored in a folder per day, such as <code>sales/dt=2025-01-03/</code> (the <code>dt=</code> style is the common Hive convention). A job for one day reads and writes only that day's partition, which makes jobs small, parallel and easy to redo. A <b>backfill</b> means running the pipeline for a range of past dates, for example after you fix a bug or add a new column. It works cleanly only if each daily run is idempotent and takes the date as a <b>parameter</b> rather than reading today's clock inside the code.",
   '''import datetime

def partition_path(table, day):
    return f"{table}/dt={day}/part-0"

def days_between(start, end):
    d = datetime.date.fromisoformat(start)
    stop = datetime.date.fromisoformat(end)
    out = []
    while d <= stop:
        out.append(d.isoformat())
        d += datetime.timedelta(days=1)
    return out

for day in days_between("2025-01-30", "2025-02-02"):
    print(partition_path("sales", day))''', run=True,
   q=Q("How many daily runs does a backfill from 2025-02-27 to 2025-03-02 (both included, not a leap year) need?", '''import datetime
d = datetime.date.fromisoformat("2025-02-27")
stop = datetime.date.fromisoformat("2025-03-02")
n = 0
while d <= stop:
    n += 1
    d += datetime.timedelta(days=1)
print(n)''', ["4", "3", "5"], "Feb 27, Feb 28, Mar 1, Mar 2: four days. February 2025 has 28 days.")),
 Sd("File formats: CSV, JSON, Parquet",
    "<b>CSV</b>: plain text, one row per line, values separated by commas. Easy to open anywhere, but no types (everything is text until you guess), no standard for missing values, and big. <b>JSON</b>: nested records with named fields, good for APIs and for data whose shape varies; also text, so bulky. <b>Parquet</b>: a binary <b>columnar</b> format used by data lakes and warehouses. <i>Row-based</i> files store whole records one after another; <i>columnar</i> files store each column together. An analytics query that needs 2 of 100 columns can then skip the other 98, and values of one column sit together so they <b>compress</b> well. A Parquet file also stores the <b>schema</b> (column names and types) inside it. Downside: you cannot read it in a text editor and it is awkward for single-row edits. Writing Parquet from pandas needs an extra library such as pyarrow:",
    "import pandas as pd\n\ndf = pd.DataFrame({'id': [1, 2], 'city': ['Pune', 'Delhi'], 'amount': [10.5, 20.0]})\n\ndf.to_csv('sales.csv', index=False)\ndf.to_json('sales.json', orient='records')\ndf.to_parquet('sales.parquet')        # needs pyarrow (or fastparquet) installed\n\nback = pd.read_parquet('sales.parquet')\nprint(back.dtypes)                     # types survive the round trip",
    q=QC("A table has 80 columns and a dashboard query reads only 3 of them across 500 million rows. Which format helps most?", ["Parquet, because a columnar file lets the reader skip the other 77 columns", "CSV, because it is plain text", "JSON, because it is nested"], 0,
         "Columnar storage reads only the needed columns, and it compresses well. Text formats must be read in full.")),
 S("Schema evolution",
   "Sources change: a new column appears, one is renamed, a type changes. <b>Schema evolution</b> is how your pipeline copes. Adding a nullable column is usually safe: old rows simply get empty values. Renames and type changes are breaking and need a plan (a contract, a version, a migration). A tolerant way to read mixed old and new data is to project every row onto the full list of columns you expect and fill what is missing with <code>None</code>.",
   '''expected = ["id", "name", "country"]

old_rows = [{"id": 1, "name": "Asha"}]                        # written before country existed
new_rows = [{"id": 2, "name": "Ravi", "country": "IN"}]

def conform(row):
    return {col: row.get(col) for col in expected}

for r in old_rows + new_rows:
    print(conform(r))''', run=True,
   q=Q("What does this show?", '''expected = ["id", "city"]
row = {"id": 7, "city": "Goa", "debug": True}
print(sorted({c: row.get(c) for c in expected}))''', ["['city', 'id']", "['city', 'debug', 'id']", "['id', 'city']"], "The dict comprehension keeps only the expected columns, so the extra 'debug' field is dropped. sorted() puts the names in alphabetical order.")),
 Sh("Final task: an incremental upsert",
   "Put it together the way a real job does: filter the source by the watermark, then upsert into the target so each id keeps its latest version, then report the new watermark. Handle repeated ids inside the source (the latest <code>updated</code> wins) and a source with nothing new.",
   q=Wh("Write <code>run_incremental(target, source, watermark)</code>. <code>target</code> and <code>source</code> are DataFrames with columns <code>id</code>, <code>updated</code> (ISO date text) and <code>amount</code>. (1) Keep source rows with <code>updated</code> greater than <code>watermark</code>. (2) Stack them under <code>target</code> and keep, for each <code>id</code>, the row with the highest <code>updated</code>. (3) Return a dict <code>{'rows': ..., 'watermark': ...}</code> where <code>rows</code> is <code>.to_dict('records')</code> of the result sorted by <code>id</code> (use <code>reset_index(drop=True)</code>), and <code>watermark</code> is the highest <code>updated</code> among the rows you took from the source, or the old watermark if there were none.",
       "def run_incremental(target, source, watermark):\n    # 1. fresh = rows of source after the watermark\n    # 2. concat target + fresh, sort by id and updated, keep the last per id\n    # 3. build the dict to return\n    pass\n",
       "def run_incremental(target, source, watermark):\n    fresh = source[source['updated'] > watermark]\n    merged = pd.concat([target, fresh]).sort_values(['id', 'updated'], kind='stable')\n    merged = merged.drop_duplicates(subset='id', keep='last').sort_values('id').reset_index(drop=True)\n    new_wm = fresh['updated'].max() if len(fresh) else watermark\n    return {'rows': merged.to_dict('records'), 'watermark': new_wm}\n",
       [("normal run", "run_incremental(TARGET, SOURCE, '2025-01-01')"),
        ("old rows are ignored", "run_incremental(TARGET, SOURCE, '2025-01-03')"),
        ("nothing new keeps the watermark", "run_incremental(TARGET, SOURCE, '2099-01-01')"),
        ("empty source", "run_incremental(TARGET, SOURCE.iloc[0:0], '2025-01-02')"),
        ("running it twice is safe", "run_incremental(pd.DataFrame(run_incremental(TARGET, SOURCE, '2025-01-01')['rows']), SOURCE, '2025-01-01')['rows']")],
       _DE_BATCH_PRE, "fresh = source[source['updated'] > watermark]; merged = pd.concat([target, fresh]).sort_values(['id','updated']); then drop_duplicates('id', keep='last'). New watermark = fresh['updated'].max() if len(fresh) else watermark.")),
])

# =====================================================================================================
# 3. Orchestration and reliability
# =====================================================================================================
_DE_ORCH_PRE = '''def err(fn):
    try:
        fn()
    except Exception as e:
        return type(e).__name__ + ": " + str(e)
    return None

SALES = {"extract": [], "clean": ["extract"], "load": ["clean"], "report": ["load"], "alert": ["load"]}
WIDE = {"d": ["b", "c"], "c": ["a"], "b": ["a"], "a": [], "e": []}
CYC = {"a": ["c"], "b": ["a"], "c": ["b"]}
SELF = {"a": ["a"]}
UNK = {"a": ["ghost"]}
'''

_DE_RETRY_PRE = '''def make_flaky(fail_times, exc=ConnectionError):
    state = {"n": 0}
    def fn():
        state["n"] += 1
        if state["n"] <= fail_times:
            raise exc("down %d" % state["n"])
        return "ok after %d" % state["n"]
    return fn

def attempt(fn, **kw):
    delays = []
    try:
        res = retry(fn, sleep=delays.append, **kw)
    except Exception as e:
        res = type(e).__name__ + ": " + str(e)
    return [res, delays]
'''

PM("de-orchestration", "Data Engineering Pro", "Orchestration and reliability",
   "A pipeline that runs once is a script; one that runs every night, retries sensibly and tells you when it breaks is engineering.",
 [
 S("A pipeline is a graph of tasks",
   "A <b>task</b> is one unit of work (extract a table, run a SQL model, send a report). Tasks depend on each other: you cannot load before you have cleaned. Draw tasks as dots and \"must finish first\" as arrows and you get a <b>DAG</b>: a <b>directed acyclic graph</b>. <i>Directed</i>: arrows have a direction. <i>Acyclic</i>: no loops, so there is always something that can run first. An <b>orchestrator</b> (a program such as Apache Airflow) stores the DAG, runs each task when its dependencies are done, runs independent tasks in parallel, retries failures and keeps a history. Here a DAG is a dict that maps each task to the tasks it needs:",
   '''pipeline = {
    "extract": [],
    "clean": ["extract"],
    "load": ["clean"],
    "report": ["load"],
    "alert": ["load"],
}

def ready(dag, done):
    return [t for t, needs in dag.items() if t not in done and all(n in done for n in needs)]

print(ready(pipeline, set()))
print(ready(pipeline, {"extract"}))
print(ready(pipeline, {"extract", "clean", "load"}))''', run=True,
   q=Q("What does this show?", '''dag = {"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]}
done = {"a", "b"}
print([t for t, needs in dag.items() if t not in done and all(n in done for n in needs)])''', ["['c']", "['c', 'd']", "['d']"], "c only needs a, which is done. d needs b and c, and c is not done yet.")),
 S("Running order and spotting a cycle",
   "Repeating <b>ready</b> gives a valid run order, called a <b>topological order</b>: pick a ready task, run it, mark it done, repeat. If at some point <i>nothing</i> is ready but tasks remain, they are waiting on each other in a loop: a <b>cycle</b> (a needs b, b needs a). A scheduler must reject that, otherwise it would wait for ever. The loop below shows the idea in waves (everything that is ready at the same time could run in parallel).",
   '''def waves(dag):
    done = set()
    out = []
    while len(done) < len(dag):
        wave = sorted(t for t, needs in dag.items() if t not in done and all(n in done for n in needs))
        if not wave:
            raise ValueError("cycle")
        out.append(wave)
        done.update(wave)
    return out

print(waves({"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]}))
try:
    waves({"a": ["b"], "b": ["a"]})
except ValueError as e:
    print("error:", e)''', run=True,
   q=QC("Task x needs y, y needs z, z needs x. What does the scheduler find?", ["No task is ever ready: it is a cycle, so the DAG is invalid", "x runs first because it is alphabetical", "All three run at once"], 0,
        "Each task is waiting for another in the loop, so none can start. Orchestrators reject DAGs like this.")),
 S("Your turn: a safe run order",
   "Now write the real scheduler core. Unlike the waves above, it runs <b>one task at a time</b>, and when several are ready it takes the alphabetically smallest, so the answer is always the same.",
   q=W("Write <code>run_order(dag)</code> where <code>dag</code> maps each task to the list of tasks it needs. Return one valid run order as a list. Repeatedly pick the alphabetically smallest task whose needs are all done. Raise <code>ValueError('unknown task: NAME')</code> if a task needs something that is not a key of <code>dag</code> (check this first), and <code>ValueError('cycle')</code> if the tasks cannot all be run. A task that needs itself is a cycle.",
       "def run_order(dag):\n    # 1. check every need exists\n    # 2. repeat: pick the smallest ready task, mark it done\n    # 3. if none is ready but tasks remain: cycle\n    pass\n",
       "def run_order(dag):\n    for task in dag:\n        for need in dag[task]:\n            if need not in dag:\n                raise ValueError('unknown task: ' + need)\n    done = []\n    while len(done) < len(dag):\n        ready = sorted(t for t, needs in dag.items() if t not in done and all(n in done for n in needs))\n        if not ready:\n            raise ValueError('cycle')\n        done.append(ready[0])\n    return done\n",
       exprs=[("the sales pipeline", "run_order(SALES)"),
              ("diamond plus a loose task", "run_order(WIDE)"),
              ("empty graph", "run_order({})"),
              ("cycle", "err(lambda: run_order(CYC))"),
              ("self-dependency", "err(lambda: run_order(SELF))"),
              ("unknown task", "err(lambda: run_order(UNK))")],
       hint="Keep a list done. Each loop: ready = sorted(t for t, needs in dag.items() if t not in done and all(n in done for n in needs)). If ready is empty, raise ValueError('cycle'). Otherwise append ready[0].",
       prelude=_DE_ORCH_PRE)),
 Sd("Airflow in one page (display only)",
    "<b>Apache Airflow</b> is the best-known orchestrator. You describe a workflow as Python code. The words: a <b>DAG</b> (the whole workflow: tasks plus dependencies plus schedule); a <b>task</b> (one node); an <b>operator</b> (a ready-made template for a kind of task, such as running a SQL statement or a bash command; in the <code>@task</code> style a plain Python function becomes a task); the <b>schedule</b> (when to run, e.g. <code>@daily</code> or a cron string); <b>catchup</b> (whether the scheduler creates runs for past schedule intervals missed since <code>start_date</code>; check the docs for the default in your version); a <b>backfill</b> (deliberately running a DAG over past dates). Settings such as <code>retries</code> go in <code>default_args</code> and apply to every task. Each run works on a <b>logical date</b> (the data interval it represents), which is what makes daily partitions and backfills possible. Import paths differ between Airflow 2 and 3 (the sketch below uses the Airflow 3 <code>airflow.sdk</code> style), so always check the docs for your version. You need an Airflow install to run this; it is shown here for reading.",
    "import datetime\n"
    "from airflow.sdk import dag, task\n"
    "\n"
    "@dag(\n"
    "    start_date=datetime.datetime(2025, 1, 1),\n"
    "    schedule=\"@daily\",\n"
    "    catchup=False,\n"
    "    default_args={\"retries\": 2},\n"
    ")\n"
    "def daily_sales():\n"
    "    @task\n"
    "    def extract():\n"
    "        return [1, 2, 3]\n"
    "\n"
    "    @task\n"
    "    def load(rows):\n"
    "        print(len(rows))\n"
    "\n"
    "    load(extract())          # passing extract's result makes load depend on extract\n"
    "\n"
    "daily_sales()\n"
    "\n"
    "# with classic operators, an arrow sets order:  extract_task >> load_task",
    q=QC("What does <code>catchup</code> control?", ["Whether the scheduler creates runs for past intervals that were missed since the start date", "How many times a failed task is retried", "How fast tasks run"], 0,
         "Catchup is about missed past schedule intervals. Retries are a separate setting.")),
 S("Retries, backoff, SLAs and idempotency",
   "Failures are normal. The rule is: <b>retry the failures that can heal, fail fast on the ones that cannot</b>. A network timeout, a busy API or a locked table are <b>transient</b>: wait and try again. A missing column, a code bug or bad credentials are <b>permanent</b>: retrying only wastes time and hides the problem. Retrying immediately can make an overloaded system worse, so use <b>exponential backoff</b>: wait 1 second, then 2, then 4, and so on (often plus a little random <b>jitter</b> so many clients do not retry in step). Retries are only safe if the task is <b>idempotent</b>; otherwise a retry duplicates work. An <b>SLA</b> (service level agreement) is a deadline such as \"the sales table is ready by 7 a.m.\"; the orchestrator or a monitor alerts you when a run is late, even if nothing has actually failed.",
   q=QC("Which failure should NOT be retried automatically?", ["A task crashing because the column <code>amount</code> no longer exists in the source", "A request that timed out once", "A database that was briefly locked"], 0,
        "A changed schema will fail identically every time. Retrying cannot fix it; a person must. Timeouts and short locks often heal.")),
 S("Logs and alerts you can search",
   "When a job runs at 3 a.m., logs are the only witness. Good pipeline logs are <b>structured</b> (one JSON object per line with fixed fields such as <code>job</code>, <code>run_date</code>, <code>rows_in</code>, <code>rows_out</code>, <code>status</code>) so tools can filter and chart them, and they record <b>counts</b>, not just \"done\". <b>Monitoring</b> watches those numbers over time; <b>alerting</b> pages a human when a rule breaks (job failed, job late, row count dropped by half). Alert on things a person can act on; too many alerts and people stop reading them.",
   '''import json

def log(job, run_date, rows_in, rows_out, status):
    return json.dumps({"job": job, "run_date": run_date, "rows_in": rows_in, "rows_out": rows_out, "status": status})

lines = [
    log("sales", "2025-01-01", 1000, 990, "ok"),
    log("sales", "2025-01-02", 1000, 410, "ok"),
]
for line in lines:
    rec = json.loads(line)
    drop = 1 - rec["rows_out"] / rec["rows_in"]
    print(rec["run_date"], "dropped", round(drop * 100), "percent", "ALERT" if drop > 0.2 else "fine")''', run=True,
   q=Q("What does this show?", '''import json
rec = json.loads('{"rows_in": 200, "rows_out": 150}')
print(round((1 - rec["rows_out"] / rec["rows_in"]) * 100))''', ["25", "75", "50"], "50 of 200 rows were dropped, which is 25 percent.")),
 S("Data contracts between teams",
   "A <b>data contract</b> is an agreement between the team that produces data and the teams that use it: which columns exist, their types, which can be empty, how fresh the data is, who to call. Its job is to stop surprises. Without one, a producer renames <code>amount</code> to <code>total</code> in a Friday release and every downstream dashboard breaks silently. With one, the change is checked <i>before</i> it ships, and breaking changes need a new version and a notice. A contract can be as simple as a dict that a test compares with the real data:",
   '''contract = {"id": "int", "amount": "float", "city": "str"}

def check_columns(sample_row, contract):
    problems = []
    for col in contract:
        if col not in sample_row:
            problems.append("missing " + col)
    for col in sample_row:
        if col not in contract:
            problems.append("unexpected " + col)
    return problems

print(check_columns({"id": 1, "amount": 2.5, "city": "Pune"}, contract))
print(check_columns({"id": 1, "total": 2.5, "city": "Pune"}, contract))''', run=True,
   q=QC("A producer wants to rename a column that three other teams read. What does a data contract change about this?", ["The change is flagged as breaking and handled with a new version and notice, instead of silently breaking consumers", "Nothing; renames are always safe", "The column can never change"], 0,
        "Contracts make the dependency explicit, so breaking changes are planned and communicated. Things can still change, just not silently.")),
 S("Final task: retry with exponential backoff",
   "Write the wrapper every pipeline needs. To keep tests fast and repeatable, the waiting is done by a <code>sleep</code> function that is <b>passed in</b>; the tests pass a function that just records the delays.",
   q=W("Write <code>retry(fn, attempts=3, base_delay=1, sleep=None, retry_on=(Exception,))</code>. Call <code>fn()</code> up to <code>attempts</code> times and return its result on the first success. When <code>fn</code> raises an exception that is an instance of <code>retry_on</code> and attempts remain, call <code>sleep(delay)</code> where the delay is <code>base_delay</code> after the 1st failure, <code>base_delay * 2</code> after the 2nd, <code>* 4</code> after the 3rd, and so on, then try again. Do not sleep after the final failed attempt; re-raise that last exception. Any exception not in <code>retry_on</code> is raised at once with no sleeping. If <code>attempts</code> is less than 1, raise <code>ValueError('attempts must be at least 1')</code>. If <code>sleep</code> is <code>None</code> use <code>time.sleep</code>.",
       "import time\n\ndef retry(fn, attempts=3, base_delay=1, sleep=None, retry_on=(Exception,)):\n    # validate attempts, then loop\n    pass\n",
       "import time\n\ndef retry(fn, attempts=3, base_delay=1, sleep=None, retry_on=(Exception,)):\n    if attempts < 1:\n        raise ValueError('attempts must be at least 1')\n    if sleep is None:\n        sleep = time.sleep\n    for i in range(attempts):\n        try:\n            return fn()\n        except retry_on:\n            if i == attempts - 1:\n                raise\n            sleep(base_delay * 2 ** i)\n",
       exprs=[("works first time, no sleeping", "attempt(make_flaky(0))"),
              ("two failures then success", "attempt(make_flaky(2), attempts=4, base_delay=1)"),
              ("gives up and re-raises the last error", "attempt(make_flaky(5), attempts=3, base_delay=2)"),
              ("a non-retryable error is raised at once", "attempt(make_flaky(1, ValueError), attempts=3, retry_on=(ConnectionError,))"),
              ("attempts must be at least 1", "attempt(make_flaky(0), attempts=0)"),
              ("single attempt never sleeps", "attempt(make_flaky(1), attempts=1)")],
       hint="for i in range(attempts): try: return fn() except retry_on: if it was the last attempt, raise; otherwise sleep(base_delay * 2 ** i).",
       prelude=_DE_RETRY_PRE)),
])

# =====================================================================================================
# 4. Streaming and Kafka
# =====================================================================================================
_DE_STREAM_PRE = '''def toy_hash(key):
    return sum(key.encode())

def run_poll(log, committed, max_records, fail_on=None):
    handled = []
    def handler(rec):
        if rec == fail_on:
            raise ValueError("bad record")
        handled.append(rec)
    return [poll(log, committed, max_records, handler), handled]
'''

PM("de-streaming", "Data Engineering Pro", "Streaming and Kafka",
   "Real-time data engineering interviews all come back to the same few Kafka ideas: partitions, keys, offsets, delivery guarantees and windows.",
 [
 S("Events versus batches",
   "A batch job asks \"what happened yesterday?\" once a day. A <b>stream</b> treats data as an endless flow of <b>events</b> (a click, a payment, a sensor reading), each handled soon after it happens. Streaming gives you freshness (fraud alerts in seconds, live dashboards) at the price of harder engineering: events arrive late, out of order, or twice. Many companies use both: streaming for what must be immediate, batch for heavy reporting. <b>Apache Kafka</b> is the most common backbone: a durable, ordered <b>log</b> of events that many programs can write to and read from at their own pace. Producers append to the end of the log; readers keep track of where they are. Nothing is deleted when it is read (it is kept for a retention period you configure), so a new program can replay history.",
   '''log = []                       # a Kafka-like log: append only
def produce(event):
    log.append(event)

produce("login:asha")
produce("click:asha")
produce("login:ravi")

position = 0                    # one reader's place in the log
def read_one():
    global position
    event = log[position]
    position += 1
    return event

print(read_one(), read_one())
print(len(log))                 # reading did not remove anything''', run=True,
   q=Q("What does this show?", '''log = ["a", "b", "c"]
pos = 1
print(log[pos])
pos += 1
print(len(log) - pos)''', ["b\n1", "a\n2", "c\n0"], "Position 1 holds b. After moving to 2, one event (c) is still unread. Reading never shrinks the log.")),
 S("Topics, partitions and keys",
   "A <b>topic</b> is a named log, like <code>orders</code>. One log on one machine cannot grow for ever, so a topic is split into <b>partitions</b>, each its own ordered log that can live on a different server. A <b>producer</b> sends a record with an optional <b>key</b> (for example the user id). Records with the <b>same key always go to the same partition</b>, because the partition is chosen by hashing the key (Kafka's default uses a hash called murmur2; the toy below just adds up the bytes so the answer is repeatable). Ordering is guaranteed <b>only inside one partition</b>, never across partitions. So pick a key whose events must stay in order: all events for one order or one user share a key.",
   '''def toy_hash(key):
    return sum(key.encode())

def partition_for(key, num_partitions):
    return toy_hash(key) % num_partitions

for key in ["user1", "user2", "user1", "user3"]:
    print(key, "->", partition_for(key, 3))''', run=True,
   q=Q("There are 4 partitions. What does this show?", '''def toy_hash(key):
    return sum(key.encode())
print(toy_hash("ab") % 4, toy_hash("ab") % 4)''', ["3 3", "3 0", "0 0"], "'a' is 97 and 'b' is 98, so the sum is 195, and 195 % 4 is 3. The same key always gives the same partition.")),
 S("Your turn: assign events to partitions",
   "Use the toy hash (already defined as <code>toy_hash(key)</code>) to route a batch of keyed events and see how each partition's log ends up.",
   q=W("Write <code>assign(events, n)</code>. <code>events</code> is a list of <code>(key, value)</code> pairs in arrival order; <code>n</code> is the number of partitions. Return a dict that maps every partition number <code>0 .. n-1</code> to the list of values that landed there, in arrival order (an empty list if none). The partition of a key is <code>toy_hash(key) % n</code>. Raise <code>ValueError('n must be at least 1')</code> if <code>n</code> is less than 1.",
       "def assign(events, n):\n    # 1. validate n\n    # 2. start with an empty list per partition\n    # 3. append each value to its partition's list\n    pass\n",
       "def assign(events, n):\n    if n < 1:\n        raise ValueError('n must be at least 1')\n    parts = {p: [] for p in range(n)}\n    for key, value in events:\n        parts[toy_hash(key) % n].append(value)\n    return parts\n",
       exprs=[("three partitions", "assign([('user1', 'e1'), ('user2', 'e2'), ('user1', 'e3'), ('user3', 'e4')], 3)"),
              ("same key stays in order", "assign([('k', 1), ('k', 2), ('k', 3)], 4)"),
              ("empty partitions are listed", "assign([], 2)"),
              ("one partition gets everything", "assign([('a', 1), ('b', 2)], 1)"),
              ("n must be positive", "raises(lambda: assign([], 0), ValueError)")],
       hint="parts = {p: [] for p in range(n)}, then parts[toy_hash(key) % n].append(value) for each event.",
       prelude=_DE_STREAM_PRE + "\ndef raises(fn, exc=Exception):\n    try:\n        fn()\n    except exc:\n        return True\n    return False\n")),
 Sd("Consumers, groups and offsets (display only)",
    "A <b>consumer</b> reads records from a topic. Every record in a partition has an <b>offset</b>: its position number (0, 1, 2, ...). A consumer remembers how far it got by <b>committing</b> an offset, so after a restart it carries on instead of starting over. Consumers join a <b>consumer group</b> (a name such as <code>billing</code>). Kafka divides the partitions among the group's members so that each partition is read by <b>at most one consumer in the group</b>; that is how you scale reading out. If a group has more consumers than partitions, the extra ones sit idle. Two different groups each get all the records, independently. To try it you need a Kafka broker running; the commands below are from the Kafka quickstart and the standard tools (check the docs for your version).",
    "# create a topic with 3 partitions, then write keyed records\n"
    "bin/kafka-topics.sh --create --topic orders --partitions 3 --bootstrap-server localhost:9092\n"
    "bin/kafka-console-producer.sh --topic orders --bootstrap-server localhost:9092 \\\n"
    "    --property parse.key=true --property key.separator=:\n"
    "> user1:order-1\n"
    "\n"
    "# read as part of a group\n"
    "bin/kafka-console-consumer.sh --topic orders --group billing --from-beginning --bootstrap-server localhost:9092\n"
    "\n"
    "# see each partition's committed offset and how far behind the group is\n"
    "bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group billing\n"
    "\n"
    "# the same in Python (confluent-kafka client)\n"
    "from confluent_kafka import Consumer\n"
    "c = Consumer({'bootstrap.servers': 'localhost:9092', 'group.id': 'billing',\n"
    "              'auto.offset.reset': 'earliest', 'enable.auto.commit': False})\n"
    "c.subscribe(['orders'])\n"
    "msg = c.poll(1.0)\n"
    "if msg is not None and msg.error() is None:\n"
    "    print(msg.key(), msg.value())\n"
    "    c.commit(message=msg)        # remember our place, after the work is done",
    q=QC("A topic has 3 partitions and one consumer group has 5 consumers. How many consumers in that group are idle?", ["2, because each partition goes to at most one consumer of the group", "0, because Kafka splits partitions further", "5"], 0,
         "Only 3 consumers can be given a partition, so 2 have nothing to read.")),
 S("Delivery guarantees: at-most, at-least, exactly once",
   "What happens if a consumer crashes between doing the work and committing its offset? The order of the two steps decides. <b>Commit first, then process</b>: a crash after the commit but before the work loses that record forever. This is <b>at-most-once</b> (never twice, maybe zero times). <b>Process first, then commit</b>: a crash after the work but before the commit means the record is read again after restart, so it is processed twice. This is <b>at-least-once</b> (never lost, maybe twice) and is the usual default. <b>Exactly-once</b> means the effect happens once even with failures. Kafka offers features for it (idempotent producers and transactions, mainly for read-process-write inside Kafka; check the docs for the exact guarantees). When your results go to an outside system, the practical recipe is at-least-once delivery plus an <b>idempotent</b> write or a dedupe step (you build one at the end of this module). Run the crash below both ways:",
   '''log = ["a", "b", "c"]

def consume(log, committed, crash_at, commit_first):
    done = []
    for off in range(committed, len(log)):
        if commit_first:
            committed = off + 1
            if off == crash_at:
                return done, committed        # died between the two steps
            done.append(log[off])
        else:
            done.append(log[off])
            if off == crash_at:
                return done, committed        # died between the two steps
            committed = off + 1
    return done, committed

def run(commit_first):
    first, committed = consume(log, 0, 1, commit_first)        # crash while on offset 1
    second, committed = consume(log, committed, None, commit_first)   # restart
    return first + second

print("process then commit:", run(False))
print("commit then process:", run(True))''', run=True,
   q=QC("Your consumer writes totals into a database. A duplicate record would double count, a lost record would lose money. What design is the sensible target?", ["At-least-once delivery plus a write that is safe to repeat (dedupe by id or upsert)", "At-most-once, and hope", "Never commit offsets"], 0,
        "At-least-once never loses data. Making the write idempotent removes the harm from duplicates.")),
 S("Your turn: poll and commit offsets",
   "Model the heart of a consumer: read a batch starting at the committed offset, handle each record, and <b>commit only after the record was handled successfully</b>. If a record fails, stop there and keep the offset on it, so it is retried next time (at-least-once).",
   q=W("Write <code>poll(log, committed, max_records, handler)</code>. <code>log</code> is a list of records, <code>committed</code> the offset to start from. For at most <code>max_records</code> records starting at <code>committed</code>, call <code>handler(record)</code>. After each success, move the offset on by one. If <code>handler</code> raises any exception, stop and return the current offset (do not let the exception escape). Return the new committed offset. Nothing happens when the offset is at or past the end of the log.",
       "def poll(log, committed, max_records, handler):\n    # loop over the next records, handle each, advance the offset only on success\n    pass\n",
       "def poll(log, committed, max_records, handler):\n    offset = committed\n    while offset < len(log) and offset - committed < max_records:\n        try:\n            handler(log[offset])\n        except Exception:\n            return offset\n        offset += 1\n    return offset\n",
       exprs=[("a batch of 2 from the start", "run_poll(['a', 'b', 'c', 'd'], 0, 2)"),
              ("continue from a committed offset", "run_poll(['a', 'b', 'c', 'd'], 2, 10)"),
              ("a failing record stays uncommitted", "run_poll(['a', 'b', 'c', 'd'], 0, 10, fail_on='c')"),
              ("fails on the first record", "run_poll(['x', 'y'], 0, 5, fail_on='x')"),
              ("already at the end", "run_poll(['a'], 1, 5)"),
              ("max_records 0 does nothing", "run_poll(['a', 'b'], 0, 0)")],
       hint="offset = committed; while offset < len(log) and offset - committed < max_records: try handler(log[offset]) except Exception: return offset; then offset += 1.",
       prelude=_DE_STREAM_PRE)),
 S("Windows: counting events over time",
   "A stream never ends, so \"how many orders?\" needs a time slice. A <b>window</b> groups events by time. A <b>tumbling</b> window is a fixed size that never overlaps: 0-59 seconds, 60-119, and so on; each event is in exactly one. A <b>sliding</b> (also called hopping) window has a size and a step smaller than the size, so windows overlap and one event belongs to several (for example the last 60 seconds, recomputed every 10). To find the tumbling window of a timestamp, round it down to a multiple of the size: <code>ts // size * size</code>. Use the <b>event time</b> (when it happened, carried in the record), not the processing time (when you saw it), or a delayed network would move events into the wrong window.",
   '''events = [3, 12, 14, 59, 60, 61, 130]     # event times in seconds
size = 60

def window_start(ts, size):
    return ts // size * size

counts = {}
for ts in events:
    w = window_start(ts, size)
    counts[w] = counts.get(w, 0) + 1
print(counts)''', run=True,
   q=W("Write <code>tumbling_counts(events, size)</code>. <code>events</code> is a list of dicts like <code>{'ts': 125, 'user': 'a'}</code> (<code>ts</code> in seconds, in any order). Return a dict <code>{window_start: count}</code> where <code>window_start = ts // size * size</code>, with keys in increasing order and windows with no events left out. Raise <code>ValueError('size must be positive')</code> if <code>size</code> is 0 or less.",
       "def tumbling_counts(events, size):\n    pass\n",
       "def tumbling_counts(events, size):\n    if size <= 0:\n        raise ValueError('size must be positive')\n    counts = {}\n    for e in events:\n        w = e['ts'] // size * size\n        counts[w] = counts.get(w, 0) + 1\n    return {w: counts[w] for w in sorted(counts)}\n",
       exprs=[("60 second windows", "tumbling_counts([{'ts': 3}, {'ts': 59}, {'ts': 60}, {'ts': 130}, {'ts': 61}], 60)"),
              ("out of order input is fine", "tumbling_counts([{'ts': 25}, {'ts': 1}, {'ts': 12}], 10)"),
              ("gaps are skipped", "tumbling_counts([{'ts': 0}, {'ts': 100}], 10)"),
              ("no events", "tumbling_counts([], 5)"),
              ("size must be positive", "raises(lambda: tumbling_counts([], 0), ValueError)")],
       hint="Build a dict with w = e['ts'] // size * size and counts[w] = counts.get(w, 0) + 1, then return a new dict by iterating sorted(counts).",
       prelude=_DE_STREAM_PRE + "\ndef raises(fn, exc=Exception):\n    try:\n        fn()\n    except exc:\n        return True\n    return False\n")),
 S("Late events and watermarks",
   "Events do not always arrive in order: a phone is offline, a network is slow. An event with an old timestamp may show up after you have already counted that window. A <b>watermark</b> is the stream engine's estimate of \"event time has reached at least this point\"; a simple version is the highest event time seen so far minus an <b>allowed lateness</b>. An event older than the watermark is <b>late</b>: you can drop it, send it to a side output, or update an already published result. A bigger allowed lateness gives more accurate counts but waits longer before results are final. Stream engines such as Flink and Spark Structured Streaming define this precisely in their own ways, so check their docs; the toy below shows the idea.",
   '''arrivals = [10, 12, 25, 11, 30, 14]       # event times, in the order they arrived
lateness = 5
max_ts = None
late = []
for ts in arrivals:
    max_ts = ts if max_ts is None else max(max_ts, ts)
    watermark = max_ts - lateness
    if ts < watermark:
        late.append(ts)
print(late)''', run=True,
   q=Q("Same arrivals, but allowed lateness is 15. What does this show?", '''arrivals = [10, 12, 25, 11, 30, 14]
lateness = 15
max_ts = None
late = []
for ts in arrivals:
    max_ts = ts if max_ts is None else max(max_ts, ts)
    if ts < max_ts - lateness:
        late.append(ts)
print(late)''', ["[14]", "[11, 14]", "[]"], "After 30 arrives the watermark is 15. Event 14 is below it. Event 11 arrived when the watermark was only 10, so it was still on time.")),
 S("Final task: dedupe by event id",
   "Because at-least-once delivery can repeat an event, the usual defence is to remember the ids you have already handled and skip repeats. In real systems that memory is bounded or stored in a database such as Redis; here it is a plain set.",
   q=W("Write <code>dedupe(events)</code>. <code>events</code> is a list of dicts that usually have an <code>'id'</code> key. Return a new list with only the <b>first</b> event for each id, keeping arrival order. Events without an <code>'id'</code> key cannot be compared, so keep all of them. Do not change the input list.",
       "def dedupe(events):\n    # remember the ids you have seen in a set\n    pass\n",
       "def dedupe(events):\n    seen = set()\n    out = []\n    for e in events:\n        if 'id' not in e:\n            out.append(e)\n            continue\n        if e['id'] in seen:\n            continue\n        seen.add(e['id'])\n        out.append(e)\n    return out\n",
       exprs=[("repeats removed, first one kept", "dedupe([{'id': 1, 'v': 'a'}, {'id': 2, 'v': 'b'}, {'id': 1, 'v': 'c'}, {'id': 3, 'v': 'd'}, {'id': 2, 'v': 'e'}])"),
              ("no duplicates", "dedupe([{'id': 'x'}, {'id': 'y'}])"),
              ("empty", "dedupe([])"),
              ("events without an id are all kept", "dedupe([{'v': 1}, {'v': 1}, {'id': 5}, {'id': 5}])"),
              ("input is not modified", "[len(dedupe(L2)), len(L2)]")],
       hint="seen = set(); for each event: if 'id' in it and its id is in seen, skip; otherwise add the id and keep the event.",
       prelude="L2 = [{'id': 1}, {'id': 1}]\n")),
])

# =====================================================================================================
# 5. Warehouses and lakes
# =====================================================================================================
_DE_WH_PRE = '''import json
import copy
def norm(rows):
    return [json.dumps(r, sort_keys=True) for r in rows]

DIM = [
    {"id": 1, "city": "Pune", "valid_from": "2024-01-01", "valid_to": None, "is_current": True},
    {"id": 2, "city": "Delhi", "valid_from": "2024-01-01", "valid_to": "2024-06-01", "is_current": False},
    {"id": 2, "city": "Goa", "valid_from": "2024-06-01", "valid_to": None, "is_current": True},
]
DIM0 = copy.deepcopy(DIM)
'''

_DE_SCHEMA_PRE = '''SCHEMA = {"id": "int", "name": "str", "amount": "float", "active": "bool"}
'''

PM("de-warehouse", "Data Engineering Pro", "Warehouses and lakes",
   "Knowing where data lives and how it is layered decides whether a platform stays cheap and trustworthy or becomes a swamp.",
 [
 S("OLTP and OLAP, row stores and column stores",
   "Two very different jobs. <b>OLTP</b> (online transaction processing) powers apps: many tiny reads and writes of single records (\"update this order\"), always correct, always fast. Databases such as Postgres or MySQL are built for it and store data <b>row by row</b>, so one whole record sits together. <b>OLAP</b> (online analytical processing) answers questions: few queries, each scanning millions of rows but only a few columns (\"total revenue per city\"). Warehouses are built for it and store data <b>column by column</b>, so a query reads only the columns it names, and similar values compress well. Rule of thumb: run the app on OLTP, run the analytics on OLAP, and copy data from one to the other with a pipeline. Below, the same sum in both layouts:",
   '''rows = [
    {"id": 1, "city": "Pune", "amount": 100},
    {"id": 2, "city": "Delhi", "amount": 50},
    {"id": 3, "city": "Pune", "amount": 25},
]
columns = {
    "id": [1, 2, 3],
    "city": ["Pune", "Delhi", "Pune"],
    "amount": [100, 50, 25],
}
print(sum(r["amount"] for r in rows))     # touches every record
print(sum(columns["amount"]))             # touches one list''', run=True,
   q=QC("A table has 1,000 rows and 50 columns. A query sums one column. Roughly how many values does a column store have to read, and a row store?", ["About 1,000 for the column store; a row store reads whole rows, about 50,000 values", "Both read about 1,000", "The column store reads 50,000"], 0,
        "Columnar layout reads only the one column (1,000 values). A row layout has to walk through all fields of every row.")),
 S("Lake, warehouse, lakehouse",
   "A <b>data lake</b> is cheap file storage (an object store such as Amazon S3) where you drop raw files of any kind (CSV, JSON, Parquet, images) and decide the structure when you read them. Flexible and cheap, but with no rules it can turn into a swamp nobody trusts. A <b>data warehouse</b> is a managed database for analytics (BigQuery, Snowflake, Redshift): structured tables, strong SQL, you decide the structure when you write the data, easy and fast but usually pricier per terabyte. A <b>lakehouse</b> keeps the data as open files in the lake but adds a table layer on top (open table formats such as Delta Lake, Apache Iceberg and Apache Hudi) that brings warehouse-like features: transactions, enforced schemas, updates and deletes, and \"time travel\" to earlier versions. Which to choose depends on cost, skills and what tools your team already has; many companies run a mix.",
   q=QC("Which description fits a lakehouse best?", ["Open files in cheap lake storage, with a table format on top that adds transactions and schemas", "A relational database for the website's orders", "A folder of screenshots"], 0,
        "A lakehouse adds table features (ACID transactions, schemas, time travel) to files in a lake.")),
 S("Medallion layers: bronze, silver, gold",
   "A common way to organise a lake or lakehouse is three layers, each more trustworthy than the last. <b>Bronze</b>: raw data exactly as it arrived, never edited (so you can always replay). <b>Silver</b>: cleaned and conformed: duplicates removed, types fixed, bad rows set aside, tables joined to a common shape. <b>Gold</b>: business-ready tables for dashboards and models, such as daily revenue per city. Each layer is built from the previous one by a repeatable job. If a bug is found you fix the logic and rebuild silver and gold from bronze.",
   '''bronze = [
    {"id": 1, "city": " pune ", "amount": "100"},
    {"id": 1, "city": " pune ", "amount": "100"},      # duplicate delivery
    {"id": 2, "city": "Delhi", "amount": "50"},
    {"id": 3, "city": "PUNE", "amount": "25"},
]

seen, silver = set(), []
for r in bronze:
    if r["id"] in seen:
        continue
    seen.add(r["id"])
    silver.append({"id": r["id"], "city": r["city"].strip().title(), "amount": float(r["amount"])})

gold = {}
for r in silver:
    gold[r["city"]] = gold.get(r["city"], 0) + r["amount"]
print(silver[0])
print(gold)''', run=True,
   q=Q("What does this show? (a gold-style total)", '''silver = [{"city": "Goa", "amount": 10.0}, {"city": "Goa", "amount": 5.5}, {"city": "Pune", "amount": 1.0}]
gold = {}
for r in silver:
    gold[r["city"]] = gold.get(r["city"], 0) + r["amount"]
print(gold["Goa"])''', ["15.5", "10.0", "16.5"], "The two Goa rows add up to 10.0 + 5.5 = 15.5; Pune is a separate key.")),
 Sd("dbt: SQL models with tests (display only)",
    "<b>dbt</b> (data build tool) is the standard tool for the \"T\" in ELT. A dbt <b>model</b> is just a <code>SELECT</code> statement saved in a <code>.sql</code> file; dbt turns it into a table or view in your warehouse, so the data never leaves the warehouse. A model reads other models with <code>{{ ref('name') }}</code>; from those references dbt learns the dependencies and builds a <b>lineage</b> graph and runs models in the right order (it is an orchestrator-style DAG again). You describe <b>tests</b> in a YAML file next to the models, such as <code>unique</code> and <code>not_null</code> on a column, and <code>dbt test</code> fails if the data breaks them. Commands: <code>dbt run</code> builds models, <code>dbt test</code> runs tests, <code>dbt build</code> does both in order, <code>dbt docs generate</code> makes browsable docs with the lineage graph. This needs a warehouse connection to run. Check docs.getdbt.com for your version (newer versions write <code>data_tests:</code>; older ones write <code>tests:</code>).",
    "-- models/silver_orders.sql\n"
    "select\n"
    "    order_id,\n"
    "    lower(trim(city)) as city,\n"
    "    cast(amount as numeric) as amount\n"
    "from {{ ref('bronze_orders') }}\n"
    "where order_id is not null\n"
    "\n"
    "-- models/schema.yml\n"
    "version: 2\n"
    "models:\n"
    "  - name: silver_orders\n"
    "    columns:\n"
    "      - name: order_id\n"
    "        data_tests:\n"
    "          - unique\n"
    "          - not_null\n"
    "\n"
    "# terminal\n"
    "dbt build            # run the models and their tests, in dependency order",
    q=QC("In dbt, what tells dbt that one model depends on another?", ["Using <code>{{ ref('other_model') }}</code> inside the SELECT", "The file name", "A comment at the top"], 0,
         "ref() both inserts the right table name and records the dependency, which gives dbt its lineage graph and run order.")),
 S("Partitioning and clustering to control cost",
   "Many warehouses are billed, or slowed, by <b>how much data a query scans</b>. Two layout tools cut that. <b>Partitioning</b> splits a table into chunks by a column, almost always the date. A query with <code>WHERE order_date = '2025-01-03'</code> then reads only that day's partition and skips the rest (called <b>partition pruning</b>). <b>Clustering</b> (or sorting) orders the data inside each partition by columns you often filter on, so the engine can skip blocks that cannot match. The catch: a filter that does not use the partition column (or wraps it in a function) may scan everything. The exact options and billing differ by warehouse, so check your warehouse's docs.",
   '''partitions = {"2025-01-01": 4000, "2025-01-02": 5000, "2025-01-03": 4500, "2025-01-04": 6000}   # rows per day

def rows_scanned(partitions, days=None):
    if days is None:
        return sum(partitions.values())               # no date filter: read everything
    return sum(n for d, n in partitions.items() if d in days)

print(rows_scanned(partitions))
print(rows_scanned(partitions, {"2025-01-03"}))''', run=True,
   q=Q("What does this show?", '''partitions = {"mon": 10, "tue": 20, "wed": 30}
days = {"tue", "wed"}
print(sum(n for d, n in partitions.items() if d in days), sum(partitions.values()))''', ["50 60", "60 60", "30 60"], "Only tue and wed are scanned (20 + 30 = 50) instead of all three days (60).")),
 S("Change data capture (CDC)",
   "How do you copy a busy production database into the warehouse without re-reading the whole table each night? <b>CDC</b>, <b>change data capture</b>: capture only what changed. Log-based CDC reads the database's own transaction log and emits one <b>change event</b> per insert, update or delete, in order (Debezium is a well-known open-source tool that does this and publishes to Kafka). You then <b>apply</b> the events to a copy of the table. Unlike a watermark on <code>updated_at</code>, CDC also sees <b>deletes</b> and every intermediate change. The events must be applied in order, and applying the same event twice must be harmless.",
   '''table = {}
events = [
    {"op": "insert", "id": 1, "row": {"city": "Pune"}},
    {"op": "insert", "id": 2, "row": {"city": "Delhi"}},
    {"op": "update", "id": 1, "row": {"city": "Mumbai"}},
    {"op": "delete", "id": 2},
]

def apply(table, e):
    if e["op"] in ("insert", "update"):
        table[e["id"]] = e["row"]
    elif e["op"] == "delete":
        table.pop(e["id"], None)

for e in events:
    apply(table, e)
print(table)''', run=True,
   q=Q("What does this show?", '''table = {}
for op, i, v in [("insert", 1, "a"), ("update", 1, "b"), ("insert", 2, "c"), ("delete", 1, None)]:
    if op == "delete":
        table.pop(i, None)
    else:
        table[i] = v
print(table)''', ["{2: 'c'}", "{1: 'b', 2: 'c'}", "{}"], "Row 1 is inserted, updated and then deleted. Only row 2 is left.")),
 S("Your turn: check a row against a schema",
   "Bronze to silver needs a gate: does each incoming row match what we expect? Write the check as a function that returns <b>all</b> the problems, not just the first, so the message is useful.",
   q=W("Write <code>check_row(row, schema)</code>. <code>schema</code> maps column name to a type name: <code>'int'</code>, <code>'float'</code>, <code>'str'</code> or <code>'bool'</code> (<code>SCHEMA</code> is defined for you as an example). Return a list of error strings: for each column in schema order, <code>'missing: COL'</code> if the key is absent or its value is <code>None</code>, otherwise <code>'type: COL expected T got G'</code> if the type is wrong (G is the Python type name, e.g. <code>str</code>); then, in alphabetical order, <code>'unexpected: COL'</code> for each key in the row that is not in the schema. A <code>bool</code> is not an <code>int</code>. An <code>int</code> is accepted where <code>'float'</code> is expected. An empty list means the row is valid.",
       "def check_row(row, schema):\n    errors = []\n    # 1. each schema column: missing or wrong type\n    # 2. extra columns, alphabetically\n    return errors\n",
       "def check_row(row, schema):\n    errors = []\n    for col, t in schema.items():\n        v = row.get(col)\n        if v is None:\n            errors.append('missing: ' + col)\n            continue\n        if t == 'int':\n            ok = isinstance(v, int) and not isinstance(v, bool)\n        elif t == 'float':\n            ok = isinstance(v, (int, float)) and not isinstance(v, bool)\n        elif t == 'str':\n            ok = isinstance(v, str)\n        else:\n            ok = isinstance(v, bool)\n        if not ok:\n            errors.append('type: %s expected %s got %s' % (col, t, type(v).__name__))\n    for col in sorted(row):\n        if col not in schema:\n            errors.append('unexpected: ' + col)\n    return errors\n",
       exprs=[("a valid row", "check_row({'id': 1, 'name': 'Asha', 'amount': 2.5, 'active': True}, SCHEMA)"),
              ("int is fine for float", "check_row({'id': 1, 'name': 'Asha', 'amount': 3, 'active': False}, SCHEMA)"),
              ("missing and None", "check_row({'id': 1, 'amount': None, 'active': True}, SCHEMA)"),
              ("wrong types", "check_row({'id': '1', 'name': 5, 'amount': 'x', 'active': 1}, SCHEMA)"),
              ("bool is not an int", "check_row({'id': True, 'name': 'a', 'amount': 1.0, 'active': True}, SCHEMA)"),
              ("extra columns, alphabetical", "check_row({'id': 1, 'name': 'a', 'amount': 1.0, 'active': True, 'zeta': 1, 'beta': 2}, SCHEMA)"),
              ("empty row", "check_row({}, SCHEMA)")],
       hint="Check bool before int by using isinstance(v, int) and not isinstance(v, bool). type(v).__name__ gives 'str', 'int', and so on.",
       prelude=_DE_SCHEMA_PRE)),
 S("Slowly changing dimensions",
   "Facts (an order, a click) never change. But descriptive data does: a customer moves from Pune to Goa. Reports about last year should still say Pune. A <b>slowly changing dimension</b> (SCD) is a table of such descriptions and the policy for changes. <b>Type 1</b>: overwrite the old value; simple, but history is lost. <b>Type 2</b>: keep every version as its own row with <code>valid_from</code>, <code>valid_to</code> and an <code>is_current</code> flag; when something changes you <i>close</i> the current row (set <code>valid_to</code> to the change date, <code>is_current</code> false) and <i>add</i> a new current row. History stays correct, and a join on a date picks the right version. (In dbt this is called a snapshot; check the docs.)",
   '''dim = [{"id": 1, "city": "Pune", "valid_from": "2024-01-01", "valid_to": None, "is_current": True}]

def move(dim, cust_id, new_city, day):
    for row in dim:
        if row["id"] == cust_id and row["is_current"]:
            row["valid_to"] = day
            row["is_current"] = False
    dim.append({"id": cust_id, "city": new_city, "valid_from": day, "valid_to": None, "is_current": True})

move(dim, 1, "Goa", "2025-03-01")
for r in dim:
    print(r["city"], r["valid_from"], r["valid_to"], r["is_current"])''', run=True,
   q=QC("A customer moved on 2025-03-01. A report about orders from 2024-12 must still show their old city. Which SCD type allows that?", ["Type 2, because the old row is kept with its valid dates", "Type 1, because it overwrites the old value", "Neither"], 0,
        "Type 2 keeps each version with the dates it was valid, so old facts can be joined to the version that was true then.")),
 S("Final task: an SCD type 2 merge",
   "Write the merge a nightly dimension job performs. For each incoming record, compare it with the current row and close and re-open when it differs. Use the dates to keep history.",
   q=W("Write <code>scd2_merge(dim, incoming, today)</code>. <code>dim</code> is a list of dicts with keys <code>id</code>, some attributes (e.g. <code>city</code>), <code>valid_from</code>, <code>valid_to</code> and <code>is_current</code> (see <code>DIM</code> for an example). <code>incoming</code> is a list of dicts with <code>id</code> plus the attributes (each id at most once). <code>today</code> is a date string. For each incoming record: if the id has no current row, add a new row (<code>valid_from=today</code>, <code>valid_to=None</code>, <code>is_current=True</code>). If it has a current row whose attributes (every key except <code>id</code> in the incoming record) differ, set that row's <code>valid_to</code> to <code>today</code> and <code>is_current</code> to <code>False</code>, and add a new current row. If nothing differs do nothing. Ids not in <code>incoming</code> stay untouched. Return a <b>new</b> list sorted by <code>(id, valid_from)</code>, and do not modify the input rows.",
       "def scd2_merge(dim, incoming, today):\n    # copy the rows, index the current rows by id, then walk through incoming\n    pass\n",
       "def scd2_merge(dim, incoming, today):\n    out = [dict(r) for r in dim]\n    current = {r['id']: r for r in out if r['is_current']}\n    for rec in incoming:\n        attrs = {k: v for k, v in rec.items() if k != 'id'}\n        cur = current.get(rec['id'])\n        if cur is not None:\n            if all(cur.get(k) == v for k, v in attrs.items()):\n                continue\n            cur['valid_to'] = today\n            cur['is_current'] = False\n        new = dict(rec)\n        new.update(valid_from=today, valid_to=None, is_current=True)\n        out.append(new)\n        current[rec['id']] = new\n    return sorted(out, key=lambda r: (r['id'], r['valid_from']))\n",
       exprs=[("one change, one new customer, one unchanged", "norm(scd2_merge(DIM, [{'id': 1, 'city': 'Mumbai'}, {'id': 2, 'city': 'Goa'}, {'id': 3, 'city': 'Kochi'}], '2025-03-01'))"),
              ("nothing changed", "norm(scd2_merge(DIM, [{'id': 1, 'city': 'Pune'}], '2025-03-01')) == norm(DIM)"),
              ("empty incoming", "norm(scd2_merge(DIM, [], '2025-03-01')) == norm(DIM)"),
              ("the input is not modified", "(scd2_merge(DIM, [{'id': 1, 'city': 'X'}], 'd'), norm(DIM) == norm(DIM0))[1]"),
              ("empty dimension", "norm(scd2_merge([], [{'id': 5, 'city': 'Pune', 'tier': 'gold'}], '2025-01-01'))"),
              ("a change in a second attribute", "norm(scd2_merge([{'id': 1, 'city': 'Pune', 'tier': 'a', 'valid_from': '2024-01-01', 'valid_to': None, 'is_current': True}], [{'id': 1, 'city': 'Pune', 'tier': 'b'}], '2025-02-02'))")],
       hint="Work on copies (dict(r)). Make current = {id: row} for rows with is_current. For each incoming record, compare its non-id keys with the current row; if different, close the old one and append a new row. Sort at the end.",
       prelude=_DE_WH_PRE)),
])

# =====================================================================================================
# 6. Data quality and observability
# =====================================================================================================
_DE_Q_PRE = '''import json
def show(x):
    return json.dumps(x, sort_keys=True)

RULES = {
    "id": {"required": True, "unique": True, "type": "int"},
    "age": {"type": "int", "min": 0, "max": 120},
    "status": {"allowed": ["new", "paid"]},
}
ROWS = [
    {"id": 1, "age": 30, "status": "new"},
    {"id": 2, "age": -5, "status": "paid"},
    {"id": 2, "age": "x", "status": "old"},
    {"status": "new"},
    {"id": 5, "age": 200, "status": None},
]
'''

_DE_QP_PRE = '''import pandas as pd
QDF = pd.DataFrame({'id': [1, 2, 2, 3, 4, 4, 4],
                    'age': [30, -5, 40, None, 200, 25, 25],
                    'email': ['a@x.com', None, 'c@x.com', 'd@x.com', None, None, 'g@x.com']})
QDF2 = pd.DataFrame({'id': [10, 11], 'age': [20, 30], 'email': ['a@x.com', 'b@x.com']})
'''

PM("de-quality", "Data Engineering Pro", "Data quality and observability",
   "Pipelines rarely crash; they quietly produce wrong numbers. Checks, quarantine and lineage are how senior engineers earn trust in data.",
 [
 S("What does good data mean?",
   "\"Bad data\" is vague, so teams name the ways data can be wrong. <b>Completeness</b>: are required values present, and are all expected rows there? <b>Uniqueness</b>: is an id repeated when it should not be? <b>Validity</b>: do values fit the allowed type, range or list (age between 0 and 120, status in a known set)? <b>Consistency / referential integrity</b>: does every order point to a customer that exists? <b>Freshness</b>: is the data recent enough? <b>Volume</b>: is today's row count about what we expect? Each one becomes a small automated <b>check</b> that runs with the pipeline, so a person hears about a problem before a dashboard shows it.",
   q=QC("A pipeline normally loads about 1 million rows a day. Today it loaded 40,000 and reported success. Which quality dimension catches this?", ["Volume (and completeness): the row count is far below normal", "Uniqueness", "Validity of one column"], 0,
        "The job did not fail, but the amount of data is far off. Volume checks compare the count with what is usual.")),
 S("Completeness and null rate",
   "The simplest check counts missing values. The <b>null rate</b> of a column is the share of rows where it is empty: <code>missing / total</code>. Decide what counts as empty (here <code>None</code> and the empty text <code>\"\"</code>) and compare the rate with a threshold: a column that was 1 percent empty last month and is 40 percent empty today means something upstream broke. Guard against an empty table so you do not divide by zero.",
   '''rows = [
    {"id": 1, "email": "a@x.com"},
    {"id": 2, "email": None},
    {"id": 3, "email": ""},
    {"id": 4, "email": "d@x.com"},
]

def null_rate(rows, col):
    if not rows:
        return 0.0
    missing = sum(1 for r in rows if r.get(col) in (None, ""))
    return missing / len(rows)

print(null_rate(rows, "email"))
print(null_rate(rows, "id"))
print(null_rate([], "email"))''', run=True,
   q=Q("What does this show?", '''rows = [{"v": 1}, {"v": None}, {"v": None}, {"v": 4}, {"v": None}]
print(sum(1 for r in rows if r["v"] is None) / len(rows))''', ["0.6", "3", "0.4"], "Three of five rows are None: 3 / 5 = 0.6.")),
 S("Uniqueness, validity and referential integrity",
   "Three more checks, all easy with sets. <b>Uniqueness</b>: find values that appear more than once. <b>Validity</b>: test each value against a range or an allowed list. <b>Referential integrity</b> (a foreign key that really points somewhere): every <code>customer_id</code> in orders must exist in customers; the orphans are the order ids whose customer is missing. Collect the <i>offending values</i>, not just a pass or fail, so the report tells someone where to look.",
   '''orders = [{"id": 1, "cust": 10}, {"id": 2, "cust": 11}, {"id": 2, "cust": 99}]
customers = {10, 11, 12}

seen, dups = set(), set()
for o in orders:
    if o["id"] in seen:
        dups.add(o["id"])
    seen.add(o["id"])
orphans = [o["id"] for o in orders if o["cust"] not in customers]
bad_status = [s for s in ["new", "paid", "oops"] if s not in {"new", "paid"}]
print(sorted(dups), orphans, bad_status)''', run=True,
   q=Q("What does this show?", '''ids = [1, 2, 3, 2, 4, 3, 3]
seen, dups = set(), set()
for i in ids:
    if i in seen:
        dups.add(i)
    seen.add(i)
print(sorted(dups))''', ["[2, 3]", "[2, 3, 3]", "[3]"], "2 and 3 each appear again after their first sighting. Using a set means 3 is listed once.")),
 S("Freshness and volume anomalies",
   "<b>Freshness</b> asks how old the newest data is: <code>now - max(loaded_at)</code>. If the table should update hourly and the newest row is 9 hours old, the pipeline is stuck even though nothing crashed. <b>Volume anomaly</b> asks whether today's row count is plausible compared with recent history: for example, flag it when it is outside 50 to 150 percent of the average of the last 7 days. Both take the \"now\" and the history as <b>inputs</b> so they are easy to test (never read the clock inside the check).",
   '''def hours_old(now, newest):
    return (now - newest) / 3600

def volume_ok(today, history, low=0.5, high=1.5):
    avg = sum(history) / len(history)
    return low * avg <= today <= high * avg

now = 10 * 3600
print(hours_old(now, 1 * 3600))             # newest row is 9 hours old
print(volume_ok(980, [1000, 1100, 900]))
print(volume_ok(300, [1000, 1100, 900]))''', run=True,
   q=Q("What does this show?", '''history = [100, 120, 80]
avg = sum(history) / len(history)
print(avg, 0.5 * avg <= 40 <= 1.5 * avg)''', ["100.0 False", "100.0 True", "100 False"], "The average is 100.0 and the allowed range is 50 to 150. A count of 40 is below 50, so the check fails.")),
 S("Quarantine bad rows instead of failing everything",
   "When a few rows are bad out of millions, stopping the whole load is often wrong; loading them silently is worse. The standard answer is to <b>quarantine</b> them: split the input into good rows (continue) and bad rows (written to a separate table or location with the <b>reason</b>), a <b>dead-letter</b> area (in messaging systems a dead-letter queue holds messages that could not be processed). Someone can inspect, fix and replay them later. Add a limit: if more than, say, 5 percent of rows are quarantined, fail the job anyway, because something big is wrong.",
   '''rows = [{"id": 1, "amount": 10}, {"id": 2, "amount": -3}, {"id": None, "amount": 5}, {"id": 4, "amount": 7}]

good, quarantine = [], []
for r in rows:
    if r["id"] is None:
        quarantine.append({"row": r, "reason": "missing id"})
    elif r["amount"] < 0:
        quarantine.append({"row": r, "reason": "negative amount"})
    else:
        good.append(r)

print(len(good), [q["reason"] for q in quarantine])
if len(quarantine) / len(rows) > 0.25:
    print("too many bad rows: fail the job")''', run=True,
   q=QC("Why keep the bad rows with a reason instead of just deleting them?", ["So people can inspect, fix and replay them, and the pipeline's data loss is visible", "Because deleting is not possible", "To make the table larger"], 0,
        "Dropping rows silently hides problems. A quarantine table keeps evidence and lets you recover the data once the cause is fixed.")),
 S("Lineage: who is affected?",
   "<b>Lineage</b> records which datasets are built from which. When a table turns out to be wrong, lineage tells you everything <i>downstream</i> that is now suspect (so you can warn its owners), and when a dashboard looks odd it tells you what <i>upstream</i> to inspect. Tools such as dbt draw this graph automatically from <code>ref()</code>. <b>Observability</b> is the wider habit: collect freshness, volume, failure and lineage signals in one place so you can ask why a number is wrong without guessing. With a dict of \"table: tables it reads from\" the downstream set is a small graph search:",
   '''reads_from = {
    "silver_orders": ["bronze_orders"],
    "gold_revenue": ["silver_orders", "silver_prices"],
    "dashboard": ["gold_revenue"],
    "silver_prices": ["bronze_prices"],
}

def downstream(table):
    hit = set()
    changed = True
    while changed:
        changed = False
        for t, sources in reads_from.items():
            if t not in hit and (table in sources or any(s in hit for s in sources)):
                hit.add(t)
                changed = True
    return sorted(hit)

print(downstream("bronze_orders"))
print(downstream("bronze_prices"))''', run=True,
   q=Q("What does this show?", '''reads_from = {"b": ["a"], "c": ["b"], "d": ["c", "x"], "e": ["x"]}
hit = set()
for _ in range(4):
    for t, srcs in reads_from.items():
        if "a" in srcs or any(s in hit for s in srcs):
            hit.add(t)
print(sorted(hit))''', ["['b', 'c', 'd']", "['b', 'c', 'd', 'e']", "['b']"], "b reads a, c reads b, and d reads c. e only reads x, which is unrelated to a.")),
 Sh("The same checks in pandas",
   "On a DataFrame the checks are one-liners. <code>df.isna().mean()</code> gives the null rate of every column at once. <code>df['id'].duplicated()</code> marks repeats (all but the first occurrence of each value). <code>df['age'].between(0, 120)</code> is True inside the range (inclusive), and NaN counts as False, so count out-of-range values on the non-missing ones only. Always build the check so it returns numbers or lists you can log, not just prints.",
   "import pandas as pd\n\ndf = pd.DataFrame({'id': [1, 2, 2, 3], 'age': [30, -5, None, 200], 'email': ['a@x.com', None, None, 'd@x.com']})\nprint(df.isna().mean().round(2).to_dict())\nprint(df['id'].duplicated().sum())\nages = df['age'].dropna()\nprint(int((~ages.between(0, 120)).sum()))", run=True,
   q=Qh("What does this show?", "import pandas as pd\ns = pd.Series([5, 5, 7, 5, 9])\nprint(int(s.duplicated().sum()))", ["2", "3", "1"], "duplicated() marks every repeat after the first occurrence: the second and third 5. The first 5 is not a repeat, so the count is 2.")),
 Sh("Your turn: a pandas quality report",
   "Combine the one-liners into a single report dict. Use only pandas operations; no row-by-row loops.",
   q=Wh("Write <code>quality(df)</code> for a DataFrame with columns <code>id</code>, <code>age</code> and <code>email</code>. Return a dict with four keys: <code>'rows'</code> (the number of rows), <code>'null_rate'</code> (a dict from every column name to its share of missing values, rounded to 2 decimals), <code>'duplicate_ids'</code> (a sorted list of the <code>id</code> values that appear more than once), and <code>'bad_ages'</code> (how many non-missing ages are below 0 or above 120). (<code>pd</code> is already imported.)",
       "def quality(df):\n    return {'rows': 0, 'null_rate': {}, 'duplicate_ids': [], 'bad_ages': 0}\n",
       "def quality(df):\n    ages = df['age'].dropna()\n    dup = df['id'][df['id'].duplicated()]\n    return {\n        'rows': len(df),\n        'null_rate': df.isna().mean().round(2).to_dict(),\n        'duplicate_ids': sorted(set(dup.tolist())),\n        'bad_ages': int((~ages.between(0, 120)).sum()),\n    }\n",
       [("the messy table", "quality(QDF)"), ("a clean table", "quality(QDF2)"), ("an empty table", "quality(QDF.iloc[0:0])['rows']")],
       _DE_QP_PRE, "df.isna().mean().round(2).to_dict(); df['id'][df['id'].duplicated()] gives the repeated ids; for ages dropna() first, then ~ages.between(0, 120).")),
 S("Final task: a validator that reports",
   "Build the core of a data-quality framework: rules in, structured report out. A structured report (a dict, not a printed sentence) can be logged, charted, turned into a quarantine table or used to fail the job.",
   q=W("Write <code>validate(rows, rules)</code>. <code>rows</code> is a list of dicts. <code>rules</code> maps a column to a dict that may contain <code>required</code> (bool), <code>type</code> (<code>'int'</code>, <code>'float'</code>, <code>'str'</code> or <code>'bool'</code>), <code>min</code>, <code>max</code>, <code>allowed</code> (list) and <code>unique</code> (bool). Go through the rows in order and, for each row, the columns in the order of <code>rules</code>. A value of <code>None</code> or an absent key is <i>missing</i>: if the column is <code>required</code> record an issue named <code>'required'</code>; either way skip the other checks for it. Otherwise check in this order, recording each failure as an issue: <code>'type'</code> (an <code>int</code> must not be a <code>bool</code>; an <code>int</code> is accepted as <code>float</code>; if the type fails skip the remaining checks for that column), <code>'min'</code> (value below min), <code>'max'</code> (value above max), <code>'allowed'</code> (value not in the list), and <code>'unique'</code> (the value was already seen earlier in this column; the first occurrence is fine). An issue is <code>{'row': index, 'column': col, 'rule': name}</code>. Return <code>{'total': number of rows, 'failed_rows': sorted list of distinct row indexes that have an issue, 'issues': the list in the order found, 'by_rule': {rule name: count}, 'ok': True when there are no issues}</code>.",
       "def validate(rows, rules):\n    issues = []\n    # loop rows, then columns in rules order, record issues\n    return {'total': len(rows), 'failed_rows': [], 'issues': issues, 'by_rule': {}, 'ok': True}\n",
       "def _is_type(v, t):\n    if t == 'int':\n        return isinstance(v, int) and not isinstance(v, bool)\n    if t == 'float':\n        return isinstance(v, (int, float)) and not isinstance(v, bool)\n    if t == 'str':\n        return isinstance(v, str)\n    return isinstance(v, bool)\n\ndef validate(rows, rules):\n    issues = []\n    seen = {col: set() for col in rules}\n    for i, row in enumerate(rows):\n        for col, rule in rules.items():\n            def bad(name):\n                issues.append({'row': i, 'column': col, 'rule': name})\n            v = row.get(col)\n            if v is None:\n                if rule.get('required'):\n                    bad('required')\n                continue\n            if 'type' in rule and not _is_type(v, rule['type']):\n                bad('type')\n                continue\n            if 'min' in rule and v < rule['min']:\n                bad('min')\n            if 'max' in rule and v > rule['max']:\n                bad('max')\n            if 'allowed' in rule and v not in rule['allowed']:\n                bad('allowed')\n            if rule.get('unique'):\n                if v in seen[col]:\n                    bad('unique')\n                seen[col].add(v)\n    by_rule = {}\n    for it in issues:\n        by_rule[it['rule']] = by_rule.get(it['rule'], 0) + 1\n    return {'total': len(rows), 'failed_rows': sorted({it['row'] for it in issues}), 'issues': issues, 'by_rule': by_rule, 'ok': not issues}\n",
       exprs=[("the messy rows", "show(validate(ROWS, RULES))"),
              ("clean data passes", "show(validate([{'id': 1, 'age': 20, 'status': 'new'}, {'id': 2, 'age': 120, 'status': 'paid'}], RULES))"),
              ("no rows", "show(validate([], RULES))"),
              ("a bool is not an int, boundaries are allowed", "show(validate([{'id': True}, {'id': 1, 'age': 0}, {'id': 2, 'age': 121}], RULES))"),
              ("missing but not required is fine", "show(validate([{}, {}], {'x': {'type': 'int', 'unique': True}}))"),
              ("float accepts ints, strings use allowed", "show(validate([{'p': 3, 'c': 'a'}, {'p': 2.5, 'c': 'z'}, {'p': 'x'}], {'p': {'type': 'float', 'min': 3}, 'c': {'allowed': ['a', 'b']}}))")],
       hint="Inside the loops: v = row.get(col). If v is None: record 'required' when asked, then continue. Then type (continue on failure), min, max, allowed, unique with a seen set per column. Finally count issues by rule.",
       prelude=_DE_Q_PRE)),
])
