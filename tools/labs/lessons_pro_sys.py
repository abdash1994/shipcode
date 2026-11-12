# ---------------------------------------------------------------- System Design Pro (exec'd inside lessons.py)

PM("sys-framework", "System Design Pro", "How to run a design interview",
   "A calm, repeatable method and fast back-of-envelope maths turn a vague prompt into a design you can defend.",
 [
 Sd("The seven moves of a design interview",
   "A design prompt is deliberately vague: <i>design a photo-sharing app</i>. The interviewer is not hunting for one secret answer. They want to see a method. Use the same seven moves every time. (1) <b>Clarify requirements</b>: what must it do, and how well? (2) <b>Estimate scale</b>: users, requests, storage. (3) <b>Define the API and data model</b>: the calls clients make and the things you store. (4) <b>Sketch the high-level boxes</b>: client, servers, database, cache, queue. (5) <b>Deep-dive the bottleneck</b>: the one part that will break first. (6) <b>Discuss trade-offs</b>: what you gave up and why. (7) <b>Cover failure modes</b>: what happens when a server, a disk or a network link dies. Spend the first five minutes on moves 1 and 2; candidates who start drawing at second ten usually draw the wrong thing.",
   "1. Clarify      functional + non-functional requirements\n2. Estimate     QPS, storage, bandwidth\n3. API + data   endpoints, tables/collections\n4. Boxes        client -> LB -> service -> cache -> DB\n5. Deep-dive    the bottleneck (hot key? write rate? fan-out?)\n6. Trade-offs   consistency vs latency, cost vs speed\n7. Failures     what if X dies? retries? backups?",
   q=QC("The interviewer says only: <i>Design a video-sharing site.</i> What is the best next move?", ["Start drawing the database tables", "Ask what the site must do and roughly how many users and videos to expect", "Name the cloud services you would use", "Describe how video compression works"], 1, "Requirements and scale come first. Everything after depends on them, and asking shows you will not build the wrong thing.")),
 Sd("Functional vs non-functional requirements",
   "<b>Functional</b> requirements are what the system does: <i>users can upload a video, follow a channel, search by title</i>. <b>Non-functional</b> requirements are how well it does it: <b>latency</b> (how fast a response comes), <b>availability</b> (the share of time it works), <b>durability</b> (stored data is not lost), <b>consistency</b> (everyone sees the same data), <b>scalability</b> (it keeps working as load grows), and cost. Non-functional requirements decide the architecture. A chat app that may lose a message and a bank ledger that must never lose one are built very differently, even if both just store rows.<br><br>Also write down what is <b>out of scope</b>, such as billing or an admin panel. Saying so out loud keeps a 45-minute interview from sprawling.",
   "Functional:      upload video, watch video, search, comment\nNon-functional:  p99 start time < 2 s, 99.9% available,\n                 uploaded videos never lost, cost-aware\nOut of scope:    payments, ads, live streaming",
   q=QC("Which line is a <b>non-functional</b> requirement?", ["Users can reset their password by email", "The checkout page must respond within 300 ms for 99% of requests", "Admins can delete a user", "Users can upload a profile picture"], 1, "A response-time target says how well the system behaves. The others describe features, which are functional. Note that 'p99' means the 99th percentile: 99 requests in 100 are at least this fast.")),
 S("Powers of two and the units you need",
   "Computers count in powers of two, and interviews use them as shortcuts. Memorise four: <code>2**10</code> is about a <b>thousand</b> (a kilobyte, KB), <code>2**20</code> about a <b>million</b> (a megabyte, MB), <code>2**30</code> about a <b>billion</b> (a gigabyte, GB) and <code>2**40</code> about a <b>trillion</b> (a terabyte, TB). In back-of-envelope work we round 1 KB to 1,000 bytes; the small error does not matter. What matters is getting the number of zeros right.",
   r'''for p in (10, 20, 30, 40):
    print(p, 2 ** p)
print(2 ** 10 * 2 ** 10 == 2 ** 20)''', run=True,
   q=Q("What does this show?", r'''print(2 ** 32)''', ["4294967296", "65536", "2147483648"], "2**32 is 4,294,967,296, about 4.3 billion. That is why a 32-bit counter runs out near 4 billion.")),
 S("Requests per second from daily users",
   "A day has 86,400 seconds, so <b>QPS</b> (queries per second) is <code>daily_users * actions_per_user / 86400</code>. That is the <b>average</b>. Real traffic has busy hours, so engineers also plan for a <b>peak</b>, often 2 to 3 times the average (a rule of thumb, not a law). Reads and writes are counted separately because they scale differently: a photo app may see 100 views for every upload.",
   r'''daily_users = 2_000_000
posts_per_user = 0.5
views_per_user = 50
write_qps = daily_users * posts_per_user / 86_400
read_qps = daily_users * views_per_user / 86_400
print(round(write_qps, 1), round(read_qps, 1))
print(round(read_qps * 3, 1))   # peak, factor 3''', run=True,
   q=W("Write <code>qps(daily_users, actions_per_user, peak_factor=1)</code>. Return the requests per second: <code>daily_users * actions_per_user / 86400 * peak_factor</code>, rounded to 1 decimal.",
       "def qps(daily_users, actions_per_user, peak_factor=1):\n    pass\n",
       "def qps(daily_users, actions_per_user, peak_factor=1):\n    return round(daily_users * actions_per_user / 86400 * peak_factor, 1)\n",
       exprs=[("10M users, 5 actions", "qps(10_000_000, 5)"), ("exactly one per second", "qps(86400, 1)"), ("nobody", "qps(0, 5)"), ("with peak factor", "qps(1_000_000, 10, 3)"), ("tiny rounds to zero", "qps(1000, 1)")],
       hint="Multiply, divide by 86400, multiply by peak_factor, then round(x, 1).")),
 S("Storage per year",
   "Storage = items per day x bytes per item x days kept x copies. Keep units straight: write everything in bytes, then convert at the end (1 GB is about 10**9 bytes, 1 TB about 10**12). <b>Replicas</b> are extra copies kept for safety, so three copies cost three times the space. Remember to ask what you keep: the video file itself is huge, the row describing it is tiny.",
   r'''photos_per_day = 1_000_000
bytes_per_photo = 2_000_000      # about 2 MB
years = 3
copies = 3
total = photos_per_day * bytes_per_photo * 365 * years * copies
print(total / 1e12, "TB")''', run=True,
   q=W("Write <code>storage_gb(items_per_day, bytes_per_item, years, replicas=1)</code>. Return the total gigabytes (1 GB = <code>10**9</code> bytes, 365 days per year), rounded to 1 decimal.",
       "def storage_gb(items_per_day, bytes_per_item, years, replicas=1):\n    pass\n",
       "def storage_gb(items_per_day, bytes_per_item, years, replicas=1):\n    return round(items_per_day * bytes_per_item * 365 * years * replicas / 10 ** 9, 1)\n",
       exprs=[("a million 500-byte rows for 5 years", "storage_gb(1_000_000, 500, 5)"), ("three replicas", "storage_gb(1_000_000, 500, 5, 3)"), ("nothing stored", "storage_gb(0, 500, 5)"), ("tiny", "storage_gb(100, 1000, 1)"), ("large", "storage_gb(10 ** 9, 100, 1, 2)")],
       hint="Multiply all five numbers, divide by 10 ** 9, round to 1 decimal.")),
 S("Bandwidth, and how long things take",
   "<b>Bandwidth</b> is data moved per second: <code>QPS x size of each response</code>. Networks are quoted in <b>bits</b>, files in <b>bytes</b>, and 1 byte is 8 bits, so multiply by 8. The second skill is knowing roughly how long things take. These are <b>rough orders of magnitude</b>, not exact specs; hardware changes, so check a current source before quoting them in writing. Roughly: reading from memory takes about 100 nanoseconds, a random read from an SSD about 100 microseconds, a round trip inside one data centre about half a millisecond, and a round trip between continents about 100 to 150 milliseconds. The point is the ratios: memory is about a thousand times faster than SSD, and a cross-ocean call is over a million times slower than a memory read.",
   r'''ns = {"memory read": 100, "SSD read": 100_000,
      "same data centre round trip": 500_000,
      "cross-continent round trip": 150_000_000}
for name, t in ns.items():
    print(name, "is about", t // ns["memory read"], "x a memory read")
print(1000 * 200 * 8 / 1000, "Mbps")   # 1000 QPS x 200 KB''', run=True,
   q=Q("500 requests per second, each response 100 KB. Bandwidth in megabits per second (QPS x KB x 8 / 1000)?", r'''print(500 * 100 * 8 / 1000)''', ["400.0", "50.0", "4.0"], "500 x 100 KB is 50,000 KB per second, which is 50 MB/s, which is 400 megabits per second.")),
 Sd("Trade-offs and failure modes",
   "Every design choice buys something and costs something. Say both out loud. A cache makes reads fast and cheap, but data can be <b>stale</b> (out of date). Replication improves availability, but copies may briefly disagree. Sharding spreads load, but cross-shard queries get hard. After the trade-offs, walk the failure modes: <b>single point of failure</b> (one component whose death stops everything: add a second), <b>overload</b> (shed or queue work), <b>data loss</b> (backups, replicas), <b>bad deploy</b> (gradual rollout, rollback). A strong answer sounds like: <i>I chose X because the requirement says Y; the cost is Z; if Z hurts we would do W.</i>",
   "Choice            Gain                 Cost\ncache             fast, cheap reads    stale data, invalidation\nreplicas          availability, reads  lag, copies may differ\nsharding          scale writes         cross-shard queries are hard\nqueue             absorbs spikes       delay, duplicates possible",
   q=QC("The interviewer asks: <i>your design caches product prices; what if the price changes?</i> The best answer is:", ["Caching is always correct, so it is not a problem", "Cached prices can be stale; set a short expiry or invalidate on change, and take the price at checkout from the database", "Remove the cache", "Use a bigger cache"], 1, "Name the trade-off (staleness), offer a mechanism (expiry or invalidation) and protect the critical path (read the authoritative price when money is involved).")),
 S("Capacity planning: how many servers?",
   "Servers needed = peak QPS divided by what one server can <i>safely</i> handle. Do not plan to run machines at 100%. Leave <b>headroom</b>, a safety margin (30% is a common starting point), because load spikes and servers fail. Always round up, and never plan for fewer than 2 servers so that one failure does not mean an outage. Real capacity per server comes from load testing, not guessing; in an interview, state your assumption.",
   r'''import math
peak_qps = 700
per_server = 100          # assumed from a load test
headroom_pct = 30
usable = per_server * (100 - headroom_pct) / 100
print(usable, math.ceil(peak_qps / usable))''', run=True,
   q=W("Write <code>servers_needed(peak_qps, qps_per_server, headroom_pct=30)</code>. Usable capacity per server is <code>qps_per_server * (100 - headroom_pct) / 100</code>. Return how many servers are needed, rounded <b>up</b> to a whole number, and never fewer than 2.",
       "def servers_needed(peak_qps, qps_per_server, headroom_pct=30):\n    pass\n",
       "import math\n\ndef servers_needed(peak_qps, qps_per_server, headroom_pct=30):\n    usable = qps_per_server * (100 - headroom_pct) / 100\n    return max(2, math.ceil(peak_qps / usable))\n",
       exprs=[("basic", "servers_needed(700, 100)"), ("tiny load still needs two", "servers_needed(5, 100)"), ("no headroom", "servers_needed(1000, 100, 0)"), ("20 percent headroom", "servers_needed(5000, 250, 20)"), ("zero traffic", "servers_needed(0, 100)")],
       hint="usable = qps_per_server * (100 - headroom_pct) / 100. math.ceil rounds up. max(2, ...) enforces the minimum.")),
 ])

PM("sys-core", "System Design Pro", "Core building blocks",
   "Load balancers, caches, hashing rings and gateways appear in almost every design; knowing how each really works lets you reason instead of recite.",
 [
 Sd("Stateless services and the two ways to scale",
   "A <b>stateless</b> service keeps nothing about a user between requests: no session in its own memory, no file on its own disk that the next request needs. State lives in a database, a cache or the request itself (for example a signed token). Because any server can handle any request, you can add or remove servers freely. Two ways to grow: <b>vertical scaling</b> (scale up) means a bigger machine: simple, but there is a ceiling and one machine is a single point of failure. <b>Horizontal scaling</b> (scale out) means more machines behind a load balancer: no hard ceiling and survives failures, but needs stateless design and more moving parts.",
   "Stateful (hard to scale):  user logs in -> session kept in server A's memory\n                           next request lands on server B -> 'who are you?'\nStateless (easy to scale): session id in a cookie -> looked up in a shared store\n                           any server can answer",
   q=QC("Users keep getting logged out at random after you add a second app server. The sessions are stored in each server's own memory. The best fix is:", ["Buy a bigger single server", "Move sessions to a shared store (database, cache) or use signed tokens so any server can serve any request", "Tell users to log in again", "Add a third server"], 1, "The servers must be stateless. A shared session store, or a signed token such as a JWT carried by the client, removes the dependence on one server's memory.")),
 S("Load balancers: round robin and least connections",
   "A <b>load balancer</b> (LB) is the front door: it receives every request and forwards it to one of several servers. <b>Round robin</b> takes turns: simple, and fine when requests cost about the same. <b>Least connections</b> sends each request to the server with the fewest requests in flight, which helps when some requests are slow. There are also weighted versions for servers of different sizes. An LB can work at layer 4 (it sees only addresses and ports) or layer 7 (it understands HTTP and can route by URL path or header).",
   r'''servers = {"s1": 5, "s2": 0, "s3": 0}   # open connections; s1 is stuck on slow requests

def least_connections(servers):
    return min(servers, key=lambda s: (servers[s], s))

for i in range(4):
    s = least_connections(servers)
    servers[s] += 1
    print("request", i, "->", s)''', run=True,
   q=Q("What does this show?", r'''servers = {"a": 2, "b": 1, "c": 1}
print(min(servers, key=lambda s: (servers[s], s)))''', ["b", "a", "c"], "b and c tie with 1 connection; the tie is broken by name, so b wins. a has 2 and is busiest.")),
 S("Health checks keep traffic away from dead servers",
   "A load balancer is only useful if it stops sending traffic to broken servers. It does this with <b>health checks</b>: every few seconds it calls a small endpoint such as <code>/health</code> on each server. After a few failures in a row the server is marked unhealthy and removed from rotation; when checks pass again it is added back. Requiring several consecutive failures avoids reacting to one blip. A good health endpoint checks what the server truly needs (can it reach its database?), but not so much that a slow dependency makes every server look dead at once.",
   r'''servers = ["s1", "s2", "s3"]
healthy = {"s1": True, "s2": False, "s3": True}
alive = [s for s in servers if healthy[s]]
for i in range(4):
    print("request", i, "->", alive[i % len(alive)])''', run=True,
   q=Q("What does this show?", r'''healthy = {"a": True, "b": False, "c": True, "d": False}
alive = [s for s in healthy if healthy[s]]
print(alive[3 % len(alive)])''', ["c", "a", "d"], "alive is [a, c]. 3 % 2 is 1, and position 1 is c.")),
 S("Caching layers and the hit ratio",
   "Caches stack. A <b>CDN</b> (content delivery network) keeps copies of static files such as images and scripts on servers near users. An <b>application cache</b> (for example an in-memory key-value store) keeps computed results close to your servers. A <b>database cache</b> or buffer keeps hot pages in memory inside the database. The <b>hit ratio</b> is hits divided by all lookups. Average read time is <code>hit_ratio x cache_time + (1 - hit_ratio) x slow_time</code>, so small improvements in a high hit ratio matter a lot: going from 90% to 99% cuts the traffic reaching the database by ten times.",
   r'''qps = 1000
for hit in (0.5, 0.9, 0.99):
    to_db = qps * (1 - hit)
    avg_ms = hit * 1 + (1 - hit) * 20      # cache 1 ms, database 20 ms
    print(hit, round(to_db), "QPS reach the DB, average", round(avg_ms, 2), "ms")''', run=True,
   q=Q("Hit ratio 0.95, cache read 2 ms, database read 40 ms. Average read time in ms?", r'''hit = 0.95
print(round(hit * 2 + (1 - hit) * 40, 2))''', ["3.9", "21.0", "1.9"], "0.95 x 2 = 1.9 and 0.05 x 40 = 2.0, total 3.9 ms.")),
 S("Eviction and expiry: a tiny LRU cache",
   "A cache is smaller than the data behind it, so it must forget something. <b>Eviction</b> policies choose what: <b>LRU</b> (least recently used) drops the entry untouched for longest; <b>LFU</b> drops the least often used. A <b>TTL</b> (time to live) puts an expiry on each entry so stale data cannot live forever. The common pattern is <b>cache-aside</b>: the application checks the cache, on a miss reads the database, then stores the result in the cache. On a write, update the database and delete (or update) the cached entry.",
   r'''from collections import OrderedDict

class LRU:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()
    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)       # now most recently used
        return self.data[key]
    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)   # drop the oldest

c = LRU(2)
c.put("a", 1); c.put("b", 2); c.get("a"); c.put("c", 3)
print(list(c.data))''', run=True,
   q=Q("Capacity 2. Operations: put a, put b, <b>get b</b>, put c. What is left, oldest first?", r'''from collections import OrderedDict
d = OrderedDict()
cap = 2
for op, k in [("put", "a"), ("put", "b"), ("get", "b"), ("put", "c")]:
    if op == "get":
        d.move_to_end(k)
    else:
        d[k] = 1
        d.move_to_end(k)
        if len(d) > cap:
            d.popitem(last=False)
print(list(d))''', ["['b', 'c']", "['a', 'c']", "['a', 'b']"], "Reading b made it recent, so a was the least recently used and was evicted when c arrived.")),
 S("Why key % n breaks when servers change",
   "To pick which cache or shard holds a key, the obvious rule is <code>key % n</code> where n is the number of servers. It spreads keys evenly, but when n changes, almost every key maps to a different server. For a cache that means nearly everything misses at once and the database takes the full load. For shards it means moving most of the data. Let us count how many keys move when we go from 4 servers to 5.",
   r'''keys = range(1000)
moved = sum(1 for k in keys if k % 4 != k % 5)
print(moved, "of 1000 keys moved")''', run=True,
   q=Q("How many of 1000 keys change server when going from 3 to 4 servers with <code>key % n</code>?", r'''print(sum(1 for k in range(1000) if k % 3 != k % 4))''', ["748", "250", "333"], "Most keys move. Ideally only about one quarter (the new server's fair share) should.")),
 S("Consistent hashing: the ring",
   "<b>Consistent hashing</b> fixes this. Imagine a circle of numbers. Hash each server's name to a point on the circle. To place a key, hash it to a point and walk clockwise to the first server. When a server is added, it takes over only the keys between itself and the previous server; the rest stay put. A single point per server gives uneven slices, so each server gets many <b>virtual nodes</b>: it appears at, say, 100 points on the ring. That evens out the load, and when a server dies its keys spread across many neighbours instead of dumping on one. Implementation trick: keep the points in a sorted list and use binary search (<code>bisect</code>) to find the first point at or after the key's hash, wrapping to the start if you fall off the end.",
   r'''import bisect
points = [10, 20, 30]            # server positions on the ring
owners = ["A", "B", "C"]
for h in (5, 10, 25, 35):
    i = bisect.bisect_left(points, h) % len(points)
    print(h, "->", owners[i])''', run=True,
   q=Q("What does this show?", r'''import bisect
print(bisect.bisect_left([10, 20, 30], 25) % 3)''', ["2", "1", "0"], "The first point at or after 25 is 30, which sits at index 2. A hash of 35 would fall off the end and wrap to index 0.")),
 Sd("API gateway, DNS and proxies in plain words",
   "<b>DNS</b> (Domain Name System) is the internet's phone book: it turns <code>shop.example.com</code> into an IP address. Answers are cached and carry a TTL, so changing a record takes time to spread. DNS can also return different addresses by user location to send people to the nearest region. A <b>proxy</b> is a middleman. A <b>forward proxy</b> acts for clients (for example a company filter); a <b>reverse proxy</b> acts for servers: clients talk to it, and it forwards to the real servers, adding caching, TLS termination (it handles the encryption) or load balancing. An <b>API gateway</b> is a reverse proxy specialised for APIs: one entry point that checks authentication, applies rate limits, routes <code>/orders</code> to the orders service and <code>/users</code> to the users service, and logs everything. The gateway handles cross-cutting concerns once so each service does not repeat them.",
   "client -> DNS lookup -> IP of gateway/LB\nclient -> API gateway (auth, rate limit, routing)\n          -> /orders -> orders service\n          -> /users  -> users service",
   q=QC("You run twelve microservices and want API-key checks, rate limits and request logging implemented in one place. Which component?", ["DNS", "API gateway", "A CDN", "A read replica"], 1, "An API gateway is the single front door where those cross-cutting rules are enforced for every service behind it.")),
 S("Build the ring",
   "Time to implement it. Rules, so your answers match the checker exactly: the hash is <code>h(s) = int(md5(s.encode()).hexdigest(), 16)</code>; each node gets <code>vnodes</code> points, named <code>f\"{node}#{i}\"</code> for i from 0; a key goes to the first point whose hash is <b>greater than or equal to</b> the key's hash, wrapping to the first point if there is none. Removing a node removes all its points.",
   q=W("Complete the class <code>Ring</code>: <code>add(node)</code>, <code>remove(node)</code> and <code>get(key)</code> (returns the node that owns the key, or <code>None</code> if the ring is empty).",
       "import hashlib, bisect\n\ndef h(s):\n    return int(hashlib.md5(s.encode()).hexdigest(), 16)\n\nclass Ring:\n    def __init__(self, vnodes=50):\n        self.vnodes = vnodes\n        self.points = []      # sorted list of (hash, node)\n\n    def add(self, node):\n        pass\n\n    def remove(self, node):\n        pass\n\n    def get(self, key):\n        pass\n",
       "import hashlib, bisect\n\ndef h(s):\n    return int(hashlib.md5(s.encode()).hexdigest(), 16)\n\nclass Ring:\n    def __init__(self, vnodes=50):\n        self.vnodes = vnodes\n        self.points = []\n\n    def add(self, node):\n        for i in range(self.vnodes):\n            bisect.insort(self.points, (h(f\"{node}#{i}\"), node))\n\n    def remove(self, node):\n        self.points = [p for p in self.points if p[1] != node]\n\n    def get(self, key):\n        if not self.points:\n            return None\n        i = bisect.bisect_left(self.points, (h(key), \"\"))\n        if i == len(self.points):\n            i = 0\n        return self.points[i][1]\n",
       prelude="""def _build(nodes):
    r = Ring()
    for n in nodes:
        r.add(n)
    return r

def _snap(r, count):
    return {'k%d' % i: r.get('k%d' % i) for i in range(count)}

def _remove_moves_only_its_keys():
    r = _build('ABC')
    before = _snap(r, 300)
    r.remove('B')
    after = _snap(r, 300)
    return all(before[k] == after[k] for k in before if before[k] != 'B') and 'B' not in after.values()

def _add_moves_a_minority_to_the_new_node():
    r = _build('ABC')
    before = _snap(r, 1000)
    r.add('D')
    after = _snap(r, 1000)
    changed = [k for k in before if before[k] != after[k]]
    return len(changed) < 500 and all(after[k] == 'D' for k in changed)
""",
       exprs=[("empty ring", "Ring().get('x')"),
              ("one node owns everything", "[_build('A').get('k1'), _build('A').get('k2')]"),
              ("placement is deterministic", "[_build('ABC').get('key%d' % i) for i in range(8)]"),
              ("removing a node moves only its keys", "_remove_moves_only_its_keys()"),
              ("adding a 4th node moves a minority, all to the new node", "_add_moves_a_minority_to_the_new_node()"),
              ("every node gets some keys", "sorted(set(_snap(_build('ABCD'), 400).values()))")],
       hint="add: insort (h(f'{node}#{i}'), node) for each i. get: bisect_left on (h(key), '') and wrap with i == len -> 0.")),
 ])

PM("sys-data", "System Design Pro", "Data stores and consistency",
   "Choosing a store and understanding what 'consistent' really promises is where most design interviews are won or lost.",
 [
 Sd("SQL or NoSQL: choose by access pattern",
   "<b>Relational (SQL)</b> databases store rows in tables with a fixed schema, join tables, and offer transactions. Choose them when data is structured, has relationships, and correctness matters (orders, payments, accounting). <b>NoSQL</b> is a loose label for several different families. A <b>document</b> store keeps JSON-like documents, read and written whole (product catalogues, user profiles with varying fields). A <b>key-value</b> store is get and put by key, very fast and simple (sessions, caches, feature flags). A <b>wide-column</b> store partitions rows by key and handles huge write volumes with queries mostly by key (systems such as Cassandra and HBase; time-series and event data). A <b>graph</b> database stores nodes and edges and is good at questions about relationships, such as friends of friends. Do not choose by fashion: start from <i>how will we read and write this data?</i> Modern databases blur the lines, so check the current docs for features before you promise one.",
   "Need                                   Reach for\ntransfers, joins, strict correctness   relational (SQL)\nflexible per-item shape, read whole    document\nlookup by key at huge speed            key-value\nmassive writes, query by partition key wide-column\nwho is connected to whom, how far      graph",
   q=QC("A bank transfer must debit one account and credit another, never half-done, and finance runs joined reports on the same data. The best fit is:", ["A key-value cache", "A relational database with transactions", "A graph database", "Object storage"], 1, "Atomic multi-row updates and joins are exactly what relational databases with transactions are built for.")),
 S("Indexes: trading write cost for read speed",
   "Without an <b>index</b> a database finds a row by scanning every row (a <b>full scan</b>). An index is a separate sorted structure (usually a B-tree) that lets it jump straight to matching rows, and also supports range queries like <i>created between X and Y</i>. The price: every index uses extra space and must be updated on every insert, update and delete, so writes get slower. Index the columns you filter, join and sort on; do not index everything. A <b>composite index</b> covers several columns in a set order, and it helps queries that use its leading columns.",
   r'''rows = [{"id": i, "email": f"u{i}@x.com"} for i in range(10000)]

def scan(email):
    checked = 0
    for r in rows:
        checked += 1
        if r["email"] == email:
            return r["id"], checked
    return None, checked

index = {r["email"]: r["id"] for r in rows}      # a dict stands in for the index
print(scan("u9999@x.com"))
print(index["u9999@x.com"])''', run=True,
   q=QC("You add an index on every column of a table that receives thousands of writes per second. What is the main downside?", ["Reads become slower", "Every write must update every index, so writes slow down and storage grows", "The database stops supporting joins", "Indexes make data less durable"], 1, "Indexes speed reads and tax writes. Add the ones your real queries need.")),
 S("Replication, lag and read-your-writes",
   "<b>Replication</b> keeps copies of data on several machines. In the common <b>leader/follower</b> design all writes go to the leader, which sends its changes to followers; reads can go to followers. That scales reads and survives a machine loss (a follower can be promoted, called <b>failover</b>). The catch is <b>replication lag</b>: followers are a little behind. A user saves their profile, the page reloads from a follower, and the old name appears. The promise to restore is <b>read-your-writes</b>: you always see your own updates. Typical fixes: read from the leader for a short time after a user writes, or remember the version the user last wrote and only use followers that have reached it. If writes stop, all copies converge to the same value; this is <b>eventual consistency</b>.",
   r'''leader, follower, log = {}, {}, []

def write(k, v):
    leader[k] = v
    log.append((k, v))          # changes waiting to be copied

def replicate(n):
    for _ in range(n):
        if log:
            k, v = log.pop(0)
            follower[k] = v

write("name", "Asha")
print(follower.get("name"))      # read from the follower too early
replicate(1)
print(follower.get("name"))''', run=True,
   q=Q("What does this show?", r'''leader, follower, log = {}, {}, []
def write(k, v):
    leader[k] = v
    log.append((k, v))
def replicate(n):
    for _ in range(n):
        if log:
            k, v = log.pop(0)
            follower[k] = v
write("x", 1)
write("x", 2)
replicate(1)
print(follower["x"])''', ["1", "2", "None"], "Only the first change has been copied. The follower still shows 1 while the leader already holds 2; that gap is replication lag.")),
 S("Sharding: range vs hash, hot keys, resharding",
   "<b>Sharding</b> (also called partitioning) splits one dataset across machines so no single machine holds or serves it all. <b>Range sharding</b> gives each shard a slice of the key order (ids 1 to 250, 251 to 500, ...): range queries stay on one shard, but sequential keys such as new ids or timestamps pile onto the last shard. <b>Hash sharding</b> hashes the key first, spreading load evenly but scattering neighbours, so range queries must ask every shard. A <b>hot key</b> is one key that gets disproportionate traffic (a celebrity account); no sharding rule fixes that alone, so you cache it or split it into sub-keys. <b>Resharding</b> means changing the number of shards; with plain <code>key % n</code> most data moves, so real systems use many small fixed partitions mapped to servers, or consistent hashing.",
   r'''users = range(1, 1001)
by_hash = [0] * 4
by_range = [0] * 4
for u in users:
    by_hash[u % 4] += 1
    by_range[(u - 1) // 250] += 1
print(by_hash, by_range)
newest = range(901, 1001)             # all the new, busy users
busy_range = [0] * 4
for u in newest:
    busy_range[(u - 1) // 250] += 1
print(busy_range)''', run=True,
   q=Q("What does this show? (the 100 newest users, hash sharding)", r'''busy = [0] * 4
for u in range(901, 1001):
    busy[u % 4] += 1
print(busy)''', ["[25, 25, 25, 25]", "[0, 0, 0, 100]", "[100, 0, 0, 0]"], "Hashing spreads sequential ids evenly, while range sharding sent all 100 to the last shard.")),
 Sd("CAP and PACELC in correct plain words",
   "A <b>network partition</b> means some nodes cannot talk to others (a cable cut, a switch dying). In a distributed system partitions will happen, so <b>partition tolerance is not optional</b>. The real question CAP asks is: <i>while a partition lasts, do you stay Consistent or stay Available?</i> <b>Consistent</b> here means every read sees the most recent write, as if there were one copy. <b>Available</b> means every working node answers every request. A <b>CP</b> choice refuses or errors on the side that cannot confirm the latest data; an <b>AP</b> choice answers with whatever it has, possibly stale, and reconciles later. The old phrase 'pick any two of three' misleads, since you cannot pick 'no partitions'. <b>PACELC</b> adds the everyday case: if there is a Partition, choose Availability or Consistency; Else (no partition), you still trade Latency against Consistency, because waiting for other copies to confirm is slower. Also note: the C in CAP is not the C in ACID; they mean different things. Many databases are tunable per operation, so calling a product simply 'CP' or 'AP' is a simplification; check its docs.",
   "Partition happens:   Consistency  or  Availability   (CAP)\nNo partition (else): Latency      or  Consistency    (PACELC)\n\nCP-style: minority side refuses writes/reads it cannot confirm\nAP-style: every side keeps answering, copies merge later",
   q=QC("Which statement is correct?", ["A distributed system can choose CA by simply avoiding network partitions", "Since partitions cannot be ruled out, the real choice during a partition is consistency versus availability", "CAP says you must always give up consistency", "Availability and latency are the same thing"], 1, "You cannot opt out of partitions. During one, you decide whether to return possibly stale answers (availability) or to refuse until copies agree (consistency).")),
 Sd("ACID, BASE and isolation anomalies",
   "<b>ACID</b> describes a transaction: <b>Atomicity</b> (all of it happens or none), <b>Consistency</b> (it moves the database from one valid state to another, respecting rules like foreign keys), <b>Isolation</b> (concurrent transactions do not trip over each other), <b>Durability</b> (once committed, it survives a crash). <b>BASE</b> (Basically Available, Soft state, Eventually consistent) is a catchy name for the looser style many distributed stores use; treat it as a mindset, not a precise standard. Isolation is a dial, and the weaker settings allow named surprises. <b>Dirty read</b>: you read another transaction's uncommitted data, which may be rolled back. <b>Non-repeatable read</b>: you read a row twice and it changed in between because someone committed. <b>Phantom</b>: you re-run a query and new rows appear. <b>Lost update</b>: two read-modify-write operations overwrite each other. <b>Write skew</b>: two transactions each check a rule using data the other changes, then write different rows, and together they break the rule (two doctors both go off call because each saw the other still on call). Which anomalies are possible at which isolation level differs between databases; check the docs of the one you use.",
   "Lost update:\n  A reads balance 100   B reads balance 100\n  A writes 110          B writes 110   -> should be 120",
   q=Q("What does this show?", r'''balance = 100
a = balance          # client A reads
b = balance          # client B reads
balance = a + 50     # A writes
balance = b + 20     # B writes, overwriting A
print(balance)''', ["120", "170", "150"], "Both clients started from 100, so the second write replaced the first. Fixes: do the add inside the database (balance = balance + 20), lock the row, or check a version number.")),
 Sd("Object, block and file storage",
   "<b>Object storage</b> (Amazon S3 is the best-known example) stores whole blobs under a key, with metadata, through an HTTP API. It is very durable, cheap per gigabyte and scales hugely, but you replace an object whole rather than editing a few bytes, and it is slower than a local disk. Use it for images, videos, backups, logs and data-lake files. <b>Block storage</b> is a raw virtual disk attached to one machine: low latency, the right base for a database or an operating system. <b>File storage</b> is a shared folder tree (like a network drive) that many machines can mount at once, good for shared working files. Rule of thumb: databases on block, shared documents on file, big unstructured blobs on object.",
   "photos, videos, backups, data lake  -> object storage\ndatabase data files, OS disk         -> block storage\nshared folder for many servers       -> file storage",
   q=QC("You must store 50 million user-uploaded photos cheaply, served over HTTP, never edited in place. Best fit?", ["Block storage on one big server", "Object storage, with a CDN in front", "A relational database BLOB column for every photo", "File storage mounted on every server"], 1, "Object storage is built for large numbers of immutable blobs. Keep a small row in the database that points to each object.")),
 S("Quorums: R + W > N",
   "Leaderless stores such as Dynamo-style systems keep <b>N</b> copies of each item. A write is successful when <b>W</b> copies acknowledge it; a read asks <b>R</b> copies and takes the newest version. If <b>R + W &gt; N</b>, every read set must overlap every write set in at least one copy, so a read always touches at least one copy that has the latest acknowledged write. With N=3, W=2, R=2 you tolerate one dead copy for both reads and writes. Raising W makes writes slower but reads cheaper; W=N, R=1 makes reads fast. This overlap is the key idea; real systems add more rules (hinted handoff, read repair, clocks), so do not oversell it as full consistency.",
   r'''from itertools import combinations

def always_overlap(n, r, w):
    replicas = range(n)
    return all(set(rs) & set(ws)
               for rs in combinations(replicas, r)
               for ws in combinations(replicas, w))

print(5 + 0 > 0, always_overlap(5, 3, 3))      # R + W = 6 > 5
print(always_overlap(5, 2, 3))                 # R + W = 5, not > 5''', run=True,
   q=Q("N=6, R=3, W=3. What is <code>R + W &gt; N</code>?", r'''print(3 + 3 > 6)''', ["False", "True", "6"], "3 + 3 equals 6, not more than 6. A read set of 3 and a write set of 3 can be completely different copies, so overlap is not guaranteed.")),
 S("Your turn: quorum maths and reads",
   "Write three small functions. A replica's answer is a pair <code>(version, value)</code>; higher version means newer.",
   q=W("Write <code>quorum_overlaps(n, r, w)</code> returning True when <code>r + w &gt; n</code>. Write <code>failures_tolerated(n, r, w)</code> returning <code>{'reads': n - r, 'writes': n - w}</code>. Write <code>quorum_read(responses, r)</code>: <code>responses</code> is the list of <code>(version, value)</code> replies in arrival order; if fewer than <code>r</code> arrived return <code>None</code>, otherwise look at the first <code>r</code> replies only and return the value with the highest version.",
       "def quorum_overlaps(n, r, w):\n    pass\n\ndef failures_tolerated(n, r, w):\n    pass\n\ndef quorum_read(responses, r):\n    pass\n",
       "def quorum_overlaps(n, r, w):\n    return r + w > n\n\ndef failures_tolerated(n, r, w):\n    return {'reads': n - r, 'writes': n - w}\n\ndef quorum_read(responses, r):\n    if len(responses) < r:\n        return None\n    return max(responses[:r])[1]\n",
       exprs=[("3-2-2 overlaps", "quorum_overlaps(3, 2, 2)"), ("exactly n does not", "quorum_overlaps(6, 3, 3)"), ("read one, write all", "quorum_overlaps(5, 1, 5)"), ("tolerated failures", "failures_tolerated(5, 3, 3)"),
              ("newest of the first r replies", "quorum_read([(1, 'old'), (3, 'new'), (2, 'mid')], 2)"), ("only first r are looked at", "quorum_read([(1, 'old'), (2, 'mid'), (9, 'late')], 2)"), ("not enough replies", "quorum_read([(1, 'a')], 2)"), ("empty", "quorum_read([], 1)")],
       hint="max() on tuples compares the version first. max(responses[:r])[1] is the value of the newest.")),
 ])

PM("sys-async", "System Design Pro", "Queues and reliability",
   "Real systems retry, repeat and fail partway; these patterns keep them correct and alive when things go wrong.",
 [
 Sd("Message queues and logs",
   "A <b>message queue</b> sits between a <b>producer</b> (sends messages) and a <b>consumer</b> (processes them). It lets the producer finish quickly, absorbs traffic spikes, and lets the two sides scale and fail separately. In a typical queue, a message is delivered to one consumer and removed once that consumer <b>acknowledges</b> (acks) it. A <b>log</b> (Kafka is the well-known example) is different: messages are appended to an ordered, retained sequence, and each consumer group tracks its own position (an <b>offset</b>). Nothing is removed on read, so a new consumer can start from the beginning and you can <b>replay</b> history after a bug. Queues suit task distribution (send this email); logs suit event streams several systems read independently. Ordering is usually guaranteed only within one partition, not across the whole topic; check the docs of your broker.",
   "Queue:  producer -> [m3 m2 m1] -> consumer   (m1 removed after ack)\nLog:    producer -> [m1 m2 m3 m4 ...] retained\n                     consumer A at offset 3, consumer B at offset 1",
   q=QC("A new analytics service must process all events from the last 7 days and then keep up with new ones. Which fits best?", ["A classic queue where messages vanish after being read", "A retained log that lets a new consumer read from an earlier offset", "A cache with a TTL of one hour", "A cron job that emails events"], 1, "A log retains history, so a new consumer can replay from an earlier position. A basic queue has already removed the old messages.")),
 S("At-least-once delivery means duplicates",
   "Networks fail. If a consumer processes a message but crashes before acking, the broker redelivers it. So the common guarantee is <b>at-least-once</b>: never lost, sometimes repeated. <b>At-most-once</b> never repeats but may lose messages. 'Exactly once' delivery across a network is not something you can simply assume; what you build is <b>effectively once</b>: at-least-once delivery plus <b>idempotent</b> processing. An operation is <b>idempotent</b> if doing it twice has the same effect as doing it once. The standard tool is an <b>idempotency key</b>: a unique id on each message; the consumer remembers which ids it handled and skips repeats. (Some platforms offer transactional features inside their own boundary; read the documentation for the exact guarantee before relying on it.)",
   r'''events = [{"id": "e1", "amount": 30}, {"id": "e1", "amount": 30}, {"id": "e2", "amount": 10}]  # e1 delivered twice

total = sum(e["amount"] for e in events)       # naive
print(total)

seen, safe_total = set(), 0
for e in events:
    if e["id"] in seen:
        continue
    seen.add(e["id"])
    safe_total += e["amount"]
print(safe_total)''', run=True,
   q=Q("What does this show?", r'''seen, processed = set(), 0
for i in ["a", "b", "a", "c", "b", "a"]:
    if i in seen:
        continue
    seen.add(i)
    processed += 1
print(processed)''', ["3", "6", "2"], "Only the first sight of each id counts: a, b and c.")),
 S("Your turn: process events exactly once in effect",
   "In real life the 'seen' set lives in a database, written in the same transaction as the effect, or protected by a unique constraint. Here we model it in memory.",
   q=W("Write <code>process_events(events)</code>. Each event is a dict with <code>id</code>, <code>account</code> and <code>amount</code>. Add each event's amount to its account's balance, but ignore any event whose <code>id</code> was already seen. Return <code>{'balances': {...}, 'skipped': n}</code> where n counts the ignored duplicates.",
       "def process_events(events):\n    pass\n",
       "def process_events(events):\n    seen = set()\n    balances = {}\n    skipped = 0\n    for e in events:\n        if e['id'] in seen:\n            skipped += 1\n            continue\n        seen.add(e['id'])\n        balances[e['account']] = balances.get(e['account'], 0) + e['amount']\n    return {'balances': balances, 'skipped': skipped}\n",
       exprs=[("no events", "process_events([])"),
              ("simple", "process_events([{'id': 'a', 'account': 'x', 'amount': 5}, {'id': 'b', 'account': 'y', 'amount': 7}, {'id': 'c', 'account': 'x', 'amount': 1}])"),
              ("duplicate ignored", "process_events([{'id': 'a', 'account': 'x', 'amount': 5}, {'id': 'a', 'account': 'x', 'amount': 5}, {'id': 'b', 'account': 'x', 'amount': -2}])"),
              ("same id repeated three times", "process_events([{'id': 'z', 'account': 'q', 'amount': 10}] * 3)"),
              ("same amount, different ids both count", "process_events([{'id': 1, 'account': 'x', 'amount': 4}, {'id': 2, 'account': 'x', 'amount': 4}])")],
       hint="Keep a set of ids seen and a dict of balances. dict.get(key, 0) gives a default.")),
 S("Retries, backoff and the dead-letter queue",
   "Many failures are brief, so retrying helps. But retrying instantly and forever makes outages worse: thousands of clients hammer a struggling service in lockstep (a <b>thundering herd</b>). <b>Exponential backoff</b> waits longer after each failure (1 s, 2 s, 4 s, 8 s, ...) up to a cap. Add <b>jitter</b>, a little randomness, so clients do not retry at the same moment. Retry only errors that may pass (timeouts, 503) and only operations that are safe to repeat (idempotent). After a maximum number of attempts, move the message to a <b>dead-letter queue</b> (DLQ): a side queue of messages that keep failing (called <b>poison messages</b> when the message itself is the problem). Humans or a repair job inspect the DLQ, so one bad message does not block the line.",
   r'''def delay(attempt, base=1, cap=30):
    return min(cap, base * 2 ** attempt)

print([delay(a) for a in range(8)])

max_attempts = 3
dead_letter = []
for msg in ["ok", "poison", "ok2"]:
    for attempt in range(max_attempts):
        if msg != "poison":
            break                         # success
    else:
        dead_letter.append(msg)           # every attempt failed
print(dead_letter)''', run=True,
   q=Q("What does this show?", r'''def delay(attempt, base=1, cap=30):
    return min(cap, base * 2 ** attempt)
print(delay(3, base=2, cap=100))''', ["16", "8", "6"], "2 x 2**3 = 16, which is below the cap of 100.")),
 Sd("Backpressure, timeouts, bulkheads, breakers and degradation",
   "<b>Backpressure</b>: when a consumer is slower than its producer, an unbounded queue just grows until memory or latency explodes. Instead, bound the queue and push back: slow the producer, or reject with HTTP 429 or 503 so callers back off. Better to refuse some work clearly than to accept everything and fail unpredictably. <b>Timeouts</b>: every call to another service needs a time limit; a missing timeout lets slow calls pile up and hold all your threads. <b>Bulkheads</b> (named after ship compartments) give each dependency or customer type its own pool of threads or connections, so one slow dependency cannot drain everything. A <b>circuit breaker</b> stops calling a dependency that is clearly failing: after enough failures it 'opens' and fails instantly for a while, then lets a trial request through to see if it has recovered. <b>Graceful degradation</b> means serving a reduced answer instead of an error: show the product page without recommendations if the recommendation service is down.",
   "closed    -> calls flow; count failures\nopen      -> fail fast, no calls, wait\nhalf-open -> let a trial call through\n               success -> closed    failure -> open",
   q=QC("The recommendations service becomes very slow. Your product page waits 30 s for it, threads fill up, and the whole site hangs. The best set of fixes is:", ["Add more threads", "A short timeout, a circuit breaker, and a fallback that renders the page without recommendations", "Retry each call ten times immediately", "Turn off the product page"], 1, "Bound the wait, stop calling a failing dependency, and degrade gracefully so the core page still works.")),
 S("Rate limiting algorithms",
   "A <b>rate limiter</b> caps how often a client can call you, protecting capacity and fairness. <b>Fixed window</b>: count requests per clock window; simple, but a client can send a full allowance at the end of one window and again at the start of the next, nearly doubling the rate across the boundary. <b>Sliding window log</b>: store each request time and count those in the last N seconds: exact, but uses memory. <b>Sliding window counter</b>: blend the current and previous window counts: cheap and close. <b>Token bucket</b>: a bucket holds up to <i>capacity</i> tokens and refills at a steady rate; each request spends a token; it allows short bursts, then a steady rate. <b>Leaky bucket</b>: requests enter a queue that drains at a fixed rate, smoothing bursts into an even flow. When over the limit, return HTTP 429 (Too Many Requests), often with a <code>Retry-After</code> header. Below, a fixed window of 10 seconds with a limit of 5 lets 10 requests through in 2 seconds.",
   r'''limit = 5                      # per 10-second window
arrivals = [9, 9, 9, 9, 9, 10, 10, 10, 10, 10]   # seconds
counts, allowed = {}, 0
for t in arrivals:
    window = t // 10
    counts[window] = counts.get(window, 0) + 1
    if counts[window] <= limit:
        allowed += 1
print(allowed, "allowed within 2 seconds")''', run=True,
   q=Q("A token bucket starts with 3 tokens and does not refill during this burst. Four requests arrive at the same instant. How many are allowed?", r'''tokens = 3
allowed = 0
for _ in range(4):
    if tokens >= 1:
        tokens -= 1
        allowed += 1
print(allowed)''', ["3", "4", "1"], "Three tokens pay for three requests; the fourth finds the bucket empty.")),
 S("Your turn: token bucket with an explicit clock",
   "Production code reads the system clock. For testing, pass the time in as a number. The bucket starts <b>full</b> at time 0. On each call: first refill, <code>tokens = min(capacity, tokens + (now - last) * refill_per_sec)</code>, set <code>last = now</code>, then spend <code>cost</code> tokens if enough are available.",
   q=W("Write the class <code>TokenBucket(capacity, refill_per_sec)</code> with <code>allow(now, cost=1)</code> returning True or False, and <code>available(now)</code> returning the tokens left after refilling, rounded to 2 decimals. The bucket starts full with <code>last = 0</code>.",
       "class TokenBucket:\n    def __init__(self, capacity, refill_per_sec):\n        pass\n\n    def allow(self, now, cost=1):\n        pass\n\n    def available(self, now):\n        pass\n",
       "class TokenBucket:\n    def __init__(self, capacity, refill_per_sec):\n        self.capacity = capacity\n        self.rate = refill_per_sec\n        self.tokens = capacity\n        self.last = 0\n\n    def _refill(self, now):\n        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)\n        self.last = now\n\n    def allow(self, now, cost=1):\n        self._refill(now)\n        if self.tokens >= cost:\n            self.tokens -= cost\n            return True\n        return False\n\n    def available(self, now):\n        self._refill(now)\n        return round(self.tokens, 2)\n",
       exprs=[("burst then refuse then refill", "(lambda b: [b.allow(0), b.allow(0), b.allow(0), b.allow(0), b.allow(1), b.allow(1)])(TokenBucket(3, 1))"),
              ("never exceeds capacity", "(lambda b: [b.available(1000), b.allow(1000, 3), b.allow(1000)])(TokenBucket(3, 1))"),
              ("fractional refill", "(lambda b: [b.allow(0), b.allow(0), b.available(1), b.allow(1), b.allow(2)])(TokenBucket(2, 0.5))"),
              ("cost bigger than capacity is never allowed", "TokenBucket(5, 1).allow(100, 6)"),
              ("cost of several tokens", "(lambda b: [b.allow(0, 4), b.allow(0, 2), b.available(0), b.allow(3, 5)])(TokenBucket(5, 1))")],
       hint="Refill first on every call: tokens = min(capacity, tokens + (now - last) * rate); last = now. Then compare to cost.")),
 Sd("Sagas, the outbox pattern and failing partway",
   "A user's order touches several services (orders, payments, stock), each with its own database. One big transaction across all of them is usually impractical. A <b>saga</b> splits the work into local steps, each with a <b>compensating action</b> that undoes it: reserve stock, charge card, create shipment; if the charge fails, release the stock. A saga is eventually consistent, not instantly atomic. A second trap is the <b>dual write</b>: you save an order in your database, then publish an event to the broker, and the process dies between the two. The <b>outbox pattern</b> fixes it: in the same database transaction, write the order row and an 'outbox' row describing the event. A separate relay reads the outbox and publishes to the broker, marking rows done. The relay may publish an event twice after a crash, which is why consumers must be idempotent. Neither pattern is magic; they replace a hidden failure with one you can reason about.",
   "Order service DB (one transaction):\n   insert orders(id=7)\n   insert outbox(event='OrderCreated', order=7)\nRelay: read outbox -> publish to broker -> mark sent\n(publish may repeat after a crash -> consumers dedupe)",
   q=QC("Your service saves an order, then crashes before publishing the 'order created' event, so downstream systems never hear about it. Which pattern removes this gap?", ["A longer timeout", "The transactional outbox: write the event row in the same database transaction and publish it from there", "Retrying the whole request from the user's browser", "Using a bigger database"], 1, "The order and its event are committed together or not at all; a relay publishes later. The event may be sent more than once, so consumers must be idempotent.")),
 S("Your turn: a circuit breaker state machine",
   "Model the breaker with three states, <code>'closed'</code>, <code>'open'</code> and <code>'half_open'</code>. Rules: in <b>closed</b> every call is allowed; count <i>consecutive</i> failures; a success resets the count; when the count reaches <code>failure_threshold</code> the state becomes open and the time is remembered. In <b>open</b>, <code>allow(now)</code> returns False until <code>now - opened_at &gt;= reset_timeout</code>, at which moment the state becomes half_open and it returns True. In <b>half_open</b> (our simple model: calls are allowed) a success closes the breaker and clears the count; a failure opens it again at that time.",
   q=W("Write <code>CircuitBreaker(failure_threshold, reset_timeout)</code> with attribute <code>state</code> (starts <code>'closed'</code>), method <code>allow(now)</code> returning True/False, <code>record_success()</code> and <code>record_failure(now)</code>.",
       "class CircuitBreaker:\n    def __init__(self, failure_threshold, reset_timeout):\n        self.state = 'closed'\n\n    def allow(self, now):\n        pass\n\n    def record_success(self):\n        pass\n\n    def record_failure(self, now):\n        pass\n",
       "class CircuitBreaker:\n    def __init__(self, failure_threshold, reset_timeout):\n        self.threshold = failure_threshold\n        self.timeout = reset_timeout\n        self.state = 'closed'\n        self.failures = 0\n        self.opened_at = 0\n\n    def allow(self, now):\n        if self.state == 'open':\n            if now - self.opened_at >= self.timeout:\n                self.state = 'half_open'\n                return True\n            return False\n        return True\n\n    def record_success(self):\n        self.failures = 0\n        self.state = 'closed'\n\n    def record_failure(self, now):\n        if self.state == 'half_open':\n            self.state = 'open'\n            self.opened_at = now\n            return\n        self.failures += 1\n        if self.failures >= self.threshold:\n            self.state = 'open'\n            self.opened_at = now\n",
       prelude="""def _trip(b, n, now=0):
    for _ in range(n):
        b.record_failure(now)
    return b
""",
       exprs=[("starts closed", "CircuitBreaker(3, 10).state"),
              ("opens after threshold failures", "_trip(CircuitBreaker(3, 10), 3).state"),
              ("stays closed below threshold", "_trip(CircuitBreaker(3, 10), 2).state"),
              ("a success resets the count", "(lambda b: (_trip(b, 2), b.record_success(), _trip(b, 2), b.state)[3])(CircuitBreaker(3, 10))"),
              ("open blocks until the timeout", "(lambda b: [b.allow(5), b.allow(9), b.allow(10), b.state])(_trip(CircuitBreaker(2, 10), 2, 0))"),
              ("half-open success closes", "(lambda b: (b.allow(10), b.record_success(), b.state)[2])(_trip(CircuitBreaker(2, 10), 2, 0))"),
              ("half-open failure reopens with a new clock", "(lambda b: (b.allow(10), b.record_failure(12), [b.state, b.allow(20), b.allow(22)])[2])(_trip(CircuitBreaker(2, 10), 2, 0))")],
       hint="Keep failures, opened_at and state. Check the open state first in allow(); the timeout moves it to half_open.")),
 ])

PM("sys-cases", "System Design Pro", "Worked designs",
   "Seeing a handful of classic systems end to end teaches the reusable moves: where the scale is, what to cache, what to queue, what to keep exact.",
 [
 S("URL shortener: requirements, scale and ID strategy",
   "Prompt: <i>design a service that turns a long URL into a short link and redirects visitors.</i> Functional: create a short link, redirect, maybe custom aliases and expiry. Non-functional: redirects must be fast and highly available; links must not collide; reads vastly outnumber writes. Suppose 100 million new links a month and 100 reads per write. Then writes are about 39 per second and reads about 3,900 per second on average, which one cache-fronted fleet handles easily; the storage is the long-term cost. Code length: with 62 symbols (0-9, a-z, A-Z) how many characters cover 10 billion links? Then the <b>ID strategy</b>: a single database counter is a bottleneck; hashing the URL can collide; so a common design is a counter service that hands each app server a <i>block</i> of ids (say 1,000 at a time), and each server turns ids into short strings locally with base62.",
   r'''writes_per_s = 100_000_000 / (30 * 86_400)
print(round(writes_per_s, 1), round(writes_per_s * 100))
n = 1
while 62 ** n < 10_000_000_000:
    n += 1
print(n, "characters")''', run=True,
   q=QC("Many app servers must create unique short codes quickly without asking the database for every single id. Best approach?", ["Every server does SELECT max(id)+1 on one table row", "Each server leases a block of ids (for example 1,000) from a central counter and encodes them", "Use the current second as the code", "Truncate the long URL's hash to two characters and hope"], 1, "Leasing ranges keeps the central counter off the hot path. Block leasing can waste a few ids when a server dies, which is fine.")),
 S("Your turn: base62 encoding",
   "Base62 is just base 10 with a longer alphabet. Repeatedly divide by 62; each remainder picks a character; the remainders read backwards form the string. The alphabet, in order: digits, then lowercase, then uppercase. Zero encodes as <code>'0'</code>.",
   q=W("Write <code>encode(n)</code> (non-negative integer to base62 string) and <code>decode(s)</code> (back to the integer).",
       "ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'\n\ndef encode(n):\n    pass\n\ndef decode(s):\n    pass\n",
       "ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'\n\ndef encode(n):\n    if n == 0:\n        return ALPHABET[0]\n    out = []\n    while n > 0:\n        n, r = divmod(n, 62)\n        out.append(ALPHABET[r])\n    return ''.join(reversed(out))\n\ndef decode(s):\n    n = 0\n    for ch in s:\n        n = n * 62 + ALPHABET.index(ch)\n    return n\n",
       exprs=[("zero", "encode(0)"), ("last single symbol", "encode(61)"), ("first two-symbol code", "encode(62)"), ("mixed", "encode(125)"), ("large", "encode(10 ** 12)"), ("decode two symbols", "decode('10')"), ("decode round trip", "all(decode(encode(n)) == n for n in [0, 1, 61, 62, 3843, 3844, 123456789])"), ("decode uppercase", "decode('Z')")],
       hint="divmod(n, 62) gives (quotient, remainder). Build characters then reverse. For decode: n = n * 62 + index of char.")),
 Sd("Redirects, collisions and analytics",
   "The redirect is an HTTP response: <b>301 Moved Permanently</b> or <b>302 Found</b> (temporary), with a <code>Location</code> header. A 301 tells browsers the move is permanent, so they may cache it and skip your server next time: less load, but you lose click counts and cannot change the target later. A 302 is not cached the same way, so every click reaches you: slightly more load, but accurate analytics and editable links. Other points to raise: <b>collisions</b> (if codes come from hashing, check the database and retry, or use unique ids so collisions cannot happen); <b>custom aliases</b> (check uniqueness); <b>expiry</b> (a TTL or cleanup job); <b>abuse</b> (scan for malicious targets, rate-limit creation); <b>caching</b> hot links in memory since reads dominate. Analytics should be written asynchronously to a queue so counting never slows the redirect.",
   "GET /aZ3k  ->  cache lookup -> (miss) database -> 302 Location: https://long.example/...\n                  \\-> emit click event to a queue (async)",
   q=QC("The product team needs per-link click counts and the ability to change a link's target later. Which redirect status fits better?", ["301, so browsers cache it", "302 (or another temporary redirect), so every click reaches the service", "200 with an HTML page that says 'go away'", "404"], 1, "A temporary redirect keeps your server in the loop for each click; a cached permanent redirect may never reach you again.")),
 Sd("Notification service",
   "Prompt: send push, SMS and email notifications to millions of users. Shape: callers (other services) post a request to a notification API; it validates, applies the user's preferences (opted out of marketing? quiet hours?), renders a template, and puts a job on a <b>queue per channel</b>; channel workers call the providers (the email or SMS vendor) and record the result. Reliability: providers fail, so retry with backoff, then dead-letter; attach an idempotency key so a retried API call does not send two texts; rate-limit per user so nobody gets 40 pings. The classic trap is mixing urgent and bulk traffic: a marketing blast of ten million emails must never delay a one-time password. Use separate queues and worker pools by priority (a bulkhead).",
   "caller -> API -> preferences + template -> queue(OTP, high)\n                                          -> queue(marketing, low)\n                          workers -> provider -> status events -> log/DB",
   q=QC("A marketing blast of 10 million emails delays password-reset messages by an hour. What is the best fix?", ["Add retries to the blast", "Separate queues and worker capacity by priority, so urgent messages never wait behind bulk ones", "Ask users to be patient", "Send the blast more slowly in the same queue"], 1, "Isolating priorities in their own queues and workers is the bulkhead idea applied to notifications.")),
 S("News feed: fan-out on write or on read",
   "Prompt: show each user a timeline of posts from people they follow. <b>Fan-out on write</b> (push): when someone posts, copy the post id into every follower's precomputed feed. Reading is a quick lookup, but a post by an account with millions of followers triggers millions of writes. <b>Fan-out on read</b> (pull): store posts once; when you open the app, fetch recent posts from everyone you follow and merge. Posting is cheap, but reading does much more work. A common compromise is a <b>hybrid</b>: push for normal accounts, and for very popular accounts skip the push and merge their recent posts in at read time. Always put the feed in a cache, page it with a cursor, and rank it if the product needs ranking.",
   r'''followers = 1000          # people who follow the poster
following = 200           # accounts this reader follows
posts_per_day = 2
feed_opens_per_day = 20
push_cost = posts_per_day * followers          # feed writes per day for the poster
pull_cost = feed_opens_per_day * following     # lookups per day for the reader
print(push_cost, pull_cost)''', run=True,
   q=QC("An account with 50 million followers posts. What is the best strategy?", ["Write the post into 50 million feeds immediately", "Do not fan out their posts; merge the celebrity's recent posts into each reader's feed at read time", "Forbid them from posting", "Store the feed in one giant row"], 1, "The hybrid avoids a huge write storm for the rare popular account while keeping the common case fast.")),
 Sd("Chat and messaging basics",
   "Prompt: one-to-one and group chat. A plain HTTP request cannot be pushed to by the server, so clients keep a long-lived <b>WebSocket</b> connection (a persistent two-way channel) to a chat server, or fall back to polling. With many chat servers, how does a message from Alice reach Bob? Keep a <b>presence/session registry</b> mapping each user to the server holding their connection; the sender's server looks up Bob's server and forwards the message (directly or through a publish/subscribe system), which pushes it down Bob's socket. If Bob is offline, the message is already stored and a push notification is sent; when Bob reconnects he fetches what he missed. Store messages durably before acknowledging, partitioned by conversation id, with a per-conversation sequence number so order is clear. Delivery receipts (sent, delivered, read) are small extra events.",
   "Alice -> chat server 2 -> store message (seq 41 in conv C)\n                        -> registry: Bob is on server 7 -> server 7 -> Bob's socket\n                        (Bob offline? keep stored + push notification)",
   q=QC("Alice is connected to chat server 2 and Bob to server 7. What gets Alice's message to Bob?", ["Alice's server looks up which server holds Bob's connection (a session registry) and forwards the message there", "Bob polls every server", "The message is emailed", "Alice connects directly to Bob's server each time"], 0, "A registry of who is connected where lets any server route a message to the right socket. Persist the message first so offline users do not lose it.")),
 S("File storage and sync",
   "Prompt: a Dropbox-style service. Split storage into a <b>metadata service</b> (file names, folders, versions, who owns what, in a database) and a <b>blob store</b> (the actual bytes in object storage). Do not upload whole files each time: cut files into <b>chunks</b>, compute a <b>hash</b> (a fingerprint) of each chunk, and upload only chunks whose hash the server does not already have. That saves bandwidth for edits and gives free <b>deduplication</b> (identical chunks are stored once). Clients learn about changes through a notification or long poll, then download only changed chunks. Conflicts (two edits to the same file offline) are resolved by keeping both versions or by last-writer-wins, a product decision to ask about. A subtle point: with fixed-size chunks, inserting one byte at the start shifts every boundary, so every chunk changes; <b>content-defined chunking</b> picks boundaries from the data itself to avoid that.",
   r'''import hashlib

def fingerprints(data, size=4):
    return [hashlib.sha256(data[i:i + size]).hexdigest()[:6]
            for i in range(0, len(data), size)]

old = b"aaaabbbbccccdddd"
new = b"aaaabbbbXXXXdddd"
a, b = fingerprints(old), fingerprints(new)
print([i for i in range(len(a)) if a[i] != b[i]], "chunk(s) to upload")''', run=True,
   q=QC("Using fixed-size chunks, a user inserts one byte at the very start of a 1 GB file. What happens?", ["Only the first chunk changes", "Every chunk boundary shifts, so essentially every chunk looks new and is re-uploaded", "Nothing; hashes ignore position", "The server rejects the edit"], 1, "Chunk contents are defined by position. Shift the data by one byte and every chunk differs. Content-defined chunking limits the damage to the chunks near the edit.")),
 Sd("A rate limiter as a service",
   "Prompt: a shared rate limiter used by many API servers. Where does it run? Often in the API gateway or as middleware that every request passes through. Where does the count live? Not in each server's own memory (a client would get N times the limit); in a shared fast store such as an in-memory data store, keyed by client and route (for example <code>user:42:/search</code>). The subtle bug is a <b>race condition</b>: two servers both read the count 4 (limit 5), both allow, and both write 5, so six requests got through. The fix is to make check-and-increment <b>atomic</b>: a single atomic increment command, or a small server-side script, that returns the new count in one step. Decide what to do if the limiter store is down: <b>fail open</b> (allow traffic, risking overload) or <b>fail closed</b> (block, risking an outage); the answer depends on what you protect. Reply with 429 and a <code>Retry-After</code> header.",
   "request -> gateway -> limiter: INCR key (atomic) -> count <= limit ? forward : 429\n                        \\-> store down? fail open or closed (decide)",
   q=QC("Two API servers each read the current count (4, limit 5), both allow the request, and both write 5. Six requests got through. What is the right fix?", ["Make the check-and-increment one atomic operation in the shared store", "Raise the limit", "Read the count twice", "Run only one API server"], 0, "The read-then-write gap is the bug. An atomic increment (or script) closes it.")),
 S("Typeahead and top-k with a heap",
   "Prompt: search autocomplete and trending terms. For each prefix the user types, return the best few completions. A <b>trie</b> (prefix tree) stores words letter by letter so all words sharing a prefix share a path. At scale you do not walk the trie per keystroke: you precompute, for popular prefixes, the top 5 suggestions and cache them, rebuilding periodically from query counts in a batch job (suggestions do not need to be real-time). To find the top k items from n counts, a <b>min-heap</b> of size k is efficient: keep the k best seen so far, popping the smallest when a better one arrives, giving O(n log k). Python's <code>heapq.nsmallest(k, items, key=...)</code> does this for you.",
   r'''import heapq
counts = {"apple": 5, "bat": 9, "cat": 5, "dog": 1}
top2 = heapq.nsmallest(2, counts.items(), key=lambda kv: (-kv[1], kv[0]))
print(top2)''', run=True,
   q=W("Write <code>top_k(words, k)</code>: count how often each word occurs in the list and return the <code>k</code> most frequent words as a list of strings, most frequent first. Break ties alphabetically. If there are fewer than k distinct words return them all; if k is 0 return an empty list.",
       "def top_k(words, k):\n    pass\n",
       "import heapq\nfrom collections import Counter\n\ndef top_k(words, k):\n    counts = Counter(words)\n    best = heapq.nsmallest(k, counts.items(), key=lambda kv: (-kv[1], kv[0]))\n    return [w for w, _ in best]\n",
       exprs=[("basic", "top_k(['a', 'b', 'a', 'c', 'b', 'a'], 2)"), ("ties go alphabetical", "top_k(['pear', 'apple', 'fig', 'fig', 'pear', 'apple'], 3)"), ("k larger than distinct", "top_k(['x', 'y', 'x'], 10)"), ("k zero", "top_k(['x'], 0)"), ("empty input", "top_k([], 3)"), ("single winner", "top_k(['z'] * 5 + ['y'] * 2, 1)")],
       hint="Counter(words) counts. heapq.nsmallest with key (-count, word) gives highest count first, ties alphabetical.")),
 ])

PM("sys-data-ai", "System Design Pro", "Designing data and AI systems",
   "Data platforms, RAG, model serving and LLM gateways are the systems data and AI engineers are asked to design; each has its own bottlenecks and failure modes.",
 [
 Sd("Batch vs streaming: an end-to-end data platform",
   "A data platform moves data from where it is born to where it is useful. Layers: <b>sources</b> (app databases, event streams, SaaS tools, files) feed <b>ingestion</b> (batch extracts, or change data capture, <b>CDC</b>, which reads a database's change log, plus event streams) into storage: a <b>data lake</b> (cheap files in object storage, raw and flexible) and/or a <b>warehouse</b> (columnar, SQL-optimised tables for analysis). <b>Transform</b> jobs clean and model it, a <b>serving</b> layer exposes it (BI tools, APIs, feature stores), and dashboards sit on top. <b>Batch</b> processes data in scheduled chunks: simpler, cheaper, easier to rerun; fine when hourly or daily freshness is enough. <b>Streaming</b> processes events continuously: seconds of freshness, but harder (ordering, late data, state, exactly-once effects). Pick the slowest mode that meets the freshness requirement. Supporting needs: orchestration, data quality checks, lineage, access control.",
   "sources -> ingestion (batch / CDC / events) -> lake + warehouse\n        -> transform (clean, model) -> serving (BI, APIs, features) -> dashboards\n   cross-cutting: orchestration, data quality, lineage, access control, cost",
   q=QC("Finance needs yesterday's revenue report by 8 am. The fraud team must act within seconds of a card payment. Which design is right?", ["Streaming for both", "Batch for the finance report, streaming (or an online check) for fraud", "Batch for both", "Neither needs a pipeline"], 1, "Match the mode to the freshness requirement. Batch is simpler and cheaper where daily is enough; only fraud needs seconds.")),
 Sd("Feature stores and training/serving skew",
   "A <b>feature</b> is an input to a model, such as <i>number of orders in the last 30 days</i>. A <b>feature store</b> is a shared system for defining, computing and serving features consistently. It has an <b>offline store</b> (large historical tables, used to build training sets) and an <b>online store</b> (a low-latency key-value lookup of the latest values, used at prediction time). The problem it solves is <b>training/serving skew</b>: the model trained on features computed one way (say, a SQL job) but gets features computed differently in production (a different code path, or stale values), so accuracy collapses in the real world. A related trap is <b>leakage</b>: building training rows using information from after the prediction moment. Fixes: define each feature once and use that definition in both places, and build training sets with <b>point-in-time</b> correct joins (only data available at that time).",
   "definition (one place)\n   -> offline store (history)  -> training set (as of each label's time)\n   -> online store (latest)    -> model at prediction time",
   q=QC("A model scores 92% offline but performs poorly in production. Training computed <code>avg_spend</code> in SQL over all data including later days; serving computes it from the last 30 days. What is the problem and the main fix?", ["The model is too small; train a larger one", "Training/serving skew and leakage; define the feature once and build training data point-in-time correct", "Production traffic is too low", "Use a different programming language"], 1, "The feature differs between training and serving, and training peeked at the future. One shared definition and point-in-time joins address both.")),
 Sd("A RAG platform: ingestion and indexing",
   "<b>RAG</b> (retrieval-augmented generation) answers a question by first retrieving relevant text and giving it to a language model. At scale this is a data pipeline plus a search system. Ingestion: <b>connectors</b> pull documents from sources (drives, wikis, tickets); a <b>parser</b> extracts text (and handles PDFs and tables); a <b>chunker</b> splits text into passages; <b>embedding workers</b> turn each chunk into a vector, in batches, fed by a queue so spikes and retries are handled; a <b>vector index</b> stores vectors for nearest-neighbour search, next to a metadata store holding the chunk text, source, version, tenant and permissions. Record which <b>embedding model and version</b> produced each vector: vectors from different models are not comparable, and queries must be embedded with the same model as the index.",
   "connector -> parse -> chunk -> queue -> embedding workers -> vector index\n                                              \\-> metadata store (text, doc id, version, tenant, ACL)\nquery -> embed (same model) -> top-k search -> (rerank) -> prompt -> LLM",
   q=QC("You want to switch to a newer embedding model. What must you do?", ["Nothing; vectors are interchangeable", "Re-embed all chunks into a new index, embed queries with the new model, then switch over", "Embed only new documents with the new model and search the mixed index", "Re-embed only the queries"], 1, "Vectors from different models live in different spaces. Build a new index in parallel, then swap, keeping the old one for rollback.")),
 Sd("RAG: updates, deletion, tenants and access control",
   "Real corpora change. Detect changes with a content hash or modified time per document, re-chunk and re-embed only what changed, and write the new version before removing the old one so searches never see a gap. <b>Deletion</b> must be a real requirement: remove all chunks by document id from the index, caches and derived stores, and keep a record that it was done (legal and privacy rules often require it; check your own obligations). <b>Multi-tenancy</b> means many customers share the system. Weak isolation: every chunk carries a tenant id and every query is filtered by it, enforced on the server, never trusted from the client. Strong isolation: a separate index or namespace per tenant. <b>Access control</b> inside a tenant: store each chunk's permissions and filter retrieval by the asking user's identity <i>before</i> anything reaches the model. Filtering after generation is too late: the model has already seen, and may quote, the restricted text.",
   "query + user identity -> retrieval filter: tenant = T AND user may read chunk\n                       -> only permitted chunks enter the prompt",
   q=QC("Employees from different teams use one RAG assistant, and some documents are restricted. Where should permissions be enforced?", ["After the model answers, by deleting sentences that look sensitive", "At retrieval time, filtering chunks by the asking user's permissions so restricted text never enters the prompt", "In the prompt: 'please do not reveal secrets'", "On the front-end only"], 1, "Only text that reaches the prompt can leak. Enforce access where chunks are selected, on the server.")),
 Sd("RAG at query time: cache, evaluate, monitor, pay",
   "Query path: embed the question, retrieve the top-k chunks (often with a keyword search blended in), optionally <b>rerank</b> them with a more precise model, build the prompt, call the LLM, and return the answer with citations. <b>Caching</b>: cache query embeddings and popular retrievals; caching whole answers is riskier (stale or permission-specific answers), so key any answer cache by user permissions and corpus version. <b>Evaluation</b>: keep a fixed set of questions with known good source documents or reference answers. Measure retrieval (did the right chunk appear in the top k?) separately from generation (is the answer supported by the retrieved text?), run it before every change, and sample real traffic for human review. <b>Monitoring</b>: latency per stage, empty-retrieval rate, user feedback, token use. <b>Cost</b> mostly comes from LLM tokens: retrieve fewer and shorter chunks, route easy questions to cheaper models, cache, and set per-tenant budgets.",
   "embed -> retrieve -> rerank -> prompt -> LLM -> answer + citations\n   metrics at every hop: latency, hit rate, tokens, feedback",
   q=QC("Answers got worse after you changed the chunking strategy. How should you have caught this before release?", ["You cannot catch this", "Run a fixed evaluation set before and after and compare retrieval hit rate and answer quality", "Ask the LLM if the answers feel better", "Wait for user complaints"], 1, "A fixed eval set turns 'feels worse' into numbers you can compare on every change.")),
 S("Model serving: latency, batching, autoscaling",
   "Serving a model is a latency and cost puzzle. Accelerators such as GPUs process several requests together far more efficiently than one at a time, so servers use <b>batching</b>: wait a few milliseconds to collect requests and run them together. Trade-off: bigger batches raise throughput but add waiting time for each request. For language models, <b>time to first token</b> (how soon text starts streaming) matters to users as much as total time, and streaming the reply makes it feel faster. Measure latency as percentiles (p50, p95, p99), because the slowest few requests define the experience. <b>Autoscaling</b> adds replicas when load rises, using signals such as queue depth, in-flight requests or accelerator utilisation. Large models load slowly (<b>cold start</b>), so keep a warm minimum and scale early. Timeouts, a bounded queue and 429/503 responses protect the service under overload. The numbers below are invented for illustration, not benchmarks.",
   r'''batch_ms = {1: 100, 4: 160, 8: 240}     # invented: batch size -> time for the whole batch
for size, ms in batch_ms.items():
    print(size, "requests ->", round(size * 1000 / ms, 1), "requests per second")''', run=True,
   q=Q("A batch of 16 takes 400 ms in total. Throughput in requests per second (batch size x 1000 / ms)?", r'''print(round(16 * 1000 / 400, 1))''', ["40.0", "16.0", "25.0"], "16 requests per 0.4 seconds is 40 per second. Each request waited up to 400 ms though; that is the latency cost.")),
 S("An LLM gateway: one front door to models",
   "Teams should not each hold their own provider keys and write their own retry code. An <b>LLM gateway</b> is a service in front of the models. It <b>authenticates</b> callers and issues per-team keys; applies <b>rate limits and quotas</b> and budgets; <b>routes</b> each request to a model by rules (cost, task, data sensitivity, context length); <b>logs</b> requests and responses with sensitive fields masked; <b>caches</b> where safe; tracks <b>cost per team</b>; and handles <b>fallback</b>: if the primary model errors or times out, try the next on the list. Routing rules should be simple and explainable. Write two functions as a gateway would.",
   q=W("Write <code>route_model(tokens, needs_reasoning, has_pii, tier)</code> applying rules <b>in this order</b>: if <code>has_pii</code> return <code>'self-hosted'</code>; else if <code>tokens &gt; 8000</code> return <code>'long-context'</code>; else if <code>needs_reasoning</code> return <code>'large'</code>; else if <code>tier == 'free'</code> return <code>'small'</code>; otherwise <code>'medium'</code>. Write <code>pick_available(preferences, down)</code>: return the first model in <code>preferences</code> that is not in <code>down</code>, or <code>None</code> if all are down.",
       "def route_model(tokens, needs_reasoning, has_pii, tier):\n    pass\n\ndef pick_available(preferences, down):\n    pass\n",
       "def route_model(tokens, needs_reasoning, has_pii, tier):\n    if has_pii:\n        return 'self-hosted'\n    if tokens > 8000:\n        return 'long-context'\n    if needs_reasoning:\n        return 'large'\n    if tier == 'free':\n        return 'small'\n    return 'medium'\n\ndef pick_available(preferences, down):\n    for m in preferences:\n        if m not in down:\n            return m\n    return None\n",
       exprs=[("pii wins over everything", "route_model(50000, True, True, 'pro')"), ("long context", "route_model(8001, True, False, 'pro')"), ("boundary is not long", "route_model(8000, False, False, 'pro')"), ("reasoning", "route_model(500, True, False, 'free')"), ("free tier", "route_model(500, False, False, 'free')"), ("default", "route_model(500, False, False, 'pro')"),
              ("first healthy", "pick_available(['a', 'b', 'c'], {'a'})"), ("all down", "pick_available(['a', 'b'], ['a', 'b'])"), ("none down", "pick_available(['a', 'b'], set())"), ("empty list", "pick_available([], set())")],
       hint="Early returns in the rule order. For pick_available, loop and return the first model not in down.")),
 Sd("Security basics and cost control",
   "<b>Authentication</b> (authn) answers <i>who are you?</i> (password, token, certificate); <b>authorization</b> (authz) answers <i>what may you do?</i> (roles, permissions). Check both on every request, on the server, and give each identity the <b>least privilege</b> it needs. <b>Secrets</b> (API keys, passwords) live in a secrets manager and are injected at run time; they are never in source code or logs, and are rotated. <b>Encryption in transit</b> means TLS on every network hop; <b>encryption at rest</b> means disks, databases and object storage are encrypted, with keys managed separately. For LLM features also treat retrieved and user-supplied text as untrusted input (prompt injection is a real risk) and log carefully. <b>Cost control</b>: tag every resource by team so spend can be attributed; set budgets and alerts; right-size and autoscale down; use cheaper storage tiers for cold data; cache; use smaller models where quality allows; put quotas on LLM use; delete what nobody uses.",
   "identity -> authn (who?) -> authz (allowed?) -> least privilege\nsecrets: manager, not code     transport: TLS     storage: encrypted at rest\ncost: tags, budgets, alerts, quotas, autoscale down, cheaper tiers",
   q=QC("A developer accidentally commits a live API key to a Git repository. What is the best first action?", ["Delete the commit and carry on", "Revoke and rotate the key immediately, then move secrets to a secrets manager and add scanning", "Wait to see whether anyone uses it", "Make the repository private and keep the key"], 1, "Once a key has been pushed it must be treated as exposed: history, forks and clones may hold it. Revoke first, clean up second.")),
 S("Observability, SLIs, SLOs and error budgets",
   "<b>Observability</b> is being able to ask why a system misbehaves. Three signals: <b>metrics</b> (numbers over time: request rate, error rate, latency), <b>logs</b> (records of events) and <b>traces</b> (the path of one request across services, with timings). An <b>SLI</b> (service level indicator) is a measured quantity, such as the fraction of requests that succeed in under 300 ms. An <b>SLO</b> (service level objective) is the target for it over a window, such as 99.9% over 30 days. An <b>SLA</b> is a contract with consequences if missed. The <b>error budget</b> is what the SLO allows to go wrong: 100% minus the SLO. For 99.9% over 30 days that is 0.1% of 43,200 minutes, about 43.2 minutes. While budget remains, you can ship and take risks; once it is spent, you slow down and fix reliability. Alerting should be about budget burn that threatens the SLO, not every blip.",
   r'''minutes = 30 * 24 * 60
for slo in (99.0, 99.9, 99.99):
    print(slo, round((100 - slo) / 100 * minutes, 2), "minutes of budget")''', run=True,
   q=W("Write <code>error_budget_minutes(slo_pct, days=30)</code>: the minutes of allowed unavailability, <code>(100 - slo_pct) / 100 * days * 24 * 60</code>, rounded to 2 decimals. Write <code>budget_left(slo_pct, days, downtime_minutes)</code>: the budget minus the downtime so far, rounded to 2 decimals (negative means the budget is overspent).",
       "def error_budget_minutes(slo_pct, days=30):\n    pass\n\ndef budget_left(slo_pct, days, downtime_minutes):\n    pass\n",
       "def error_budget_minutes(slo_pct, days=30):\n    return round((100 - slo_pct) / 100 * days * 24 * 60, 2)\n\ndef budget_left(slo_pct, days, downtime_minutes):\n    return round(error_budget_minutes(slo_pct, days) - downtime_minutes, 2)\n",
       exprs=[("three nines, 30 days", "error_budget_minutes(99.9)"), ("two nines", "error_budget_minutes(99)"), ("four nines", "error_budget_minutes(99.99)"), ("a week", "error_budget_minutes(99.9, 7)"), ("perfect slo", "error_budget_minutes(100)"), ("some left", "budget_left(99.9, 30, 10)"), ("overspent", "budget_left(99.9, 30, 50)"), ("exactly spent", "budget_left(99, 30, 432)")],
       hint="(100 - slo) / 100 is the allowed fraction. Multiply by days * 24 * 60 minutes, then round(x, 2).")),
 ])

PM("sys-interview-drills", "System Design Pro", "Eight timed prompts",
   "Practice the first five minutes and the deep-dive on eight realistic prompts, so the method becomes a reflex.",
 [
 Sd("Drill 1: nearby drivers for a ride-hailing app",
   "Set a 5-minute timer. <b>Prompt: design the service that shows riders the nearby available drivers and updates as they move.</b> Before reading the options, write your own first question and your guess at the bottleneck. Then choose the best pair below.",
   None,
   q=QC("Pick the best first clarifying question and the main bottleneck.", ["Ask: 'Which programming language?' Bottleneck: the map UI", "Ask: 'How many drivers and riders, and how fresh must locations be?' Bottleneck: the very high rate of location writes plus geospatial lookups for 'nearby'", "Ask: 'Do we need dark mode?' Bottleneck: login", "Ask: 'What is the budget?' Bottleneck: the payment screen"], 1, "Freshness and scale decide everything. Millions of drivers pinging every few seconds is a huge write stream, held in memory, and 'nearby' needs a spatial index (geohash cells, quadtree or similar), usually sharded by area. Old positions are disposable, so durability matters little: a good non-functional insight to state.")),
 Sd("Drill 2: a web crawler",
   "<b>Prompt: design a crawler that fetches billions of pages for a search engine.</b> Think: what is a URL frontier, and why would a site complain?",
   None,
   q=QC("Pick the best first clarifying question and the main bottleneck.", ["Ask: 'How many pages, how often must they be refreshed, and what content types?' Bottleneck: the URL frontier (scheduling, de-duplicating URLs, politeness limits per site, prioritising)", "Ask: 'What font for the results page?' Bottleneck: the search box", "Ask: 'Is it for mobile?' Bottleneck: parsing CSS", "Ask: 'Can I use a single machine?' Bottleneck: the keyboard"], 0, "Fetching is easy to parallelise; deciding what to fetch next is hard. Skip duplicates (hashes, URL normalisation), obey robots.txt and per-host rate limits (politeness), prioritise by importance and freshness, and handle traps like infinite calendars.")),
 Sd("Drill 3: a real-time game leaderboard",
   "<b>Prompt: design a leaderboard for a game with 10 million players. Show the top 100 and each player's own rank.</b>",
   None,
   q=QC("Pick the best first clarifying question and the main bottleneck.", ["Ask: 'How often do scores change, and must the rank be exact and instant?' Bottleneck: computing rank over a constantly updated ordered set (needs a sorted structure, sharding by score range, or approximate ranks)", "Ask: 'What colour are the badges?' Bottleneck: images", "Ask: 'Which cloud?' Bottleneck: DNS", "Ask: 'Do players have names?' Bottleneck: the name field"], 0, "Top-N is easy to cache. Your own exact rank among 10 million requires counting how many scores are higher, which needs an ordered structure with fast insert and rank (in-memory sorted sets do this), possibly sharded; or return an approximate rank for players deep in the list. Say which you chose and why.")),
 Sd("Drill 4: a RAG chatbot over company documents",
   "<b>Prompt: design an assistant that answers employee questions from internal wikis, tickets and PDFs for 20,000 employees.</b>",
   None,
   q=QC("Pick the best first clarifying question and the main bottleneck.", ["Ask: 'Which document sources, who may see what, and how fresh must answers be?' Bottleneck: ingestion quality plus per-user access control at retrieval, and answer quality (evaluation)", "Ask: 'Which logo?' Bottleneck: the chat bubble", "Ask: 'Could we fine-tune on everything and skip retrieval?' Bottleneck: GPU shortage", "Ask: 'How long is the demo?' Bottleneck: the demo"], 0, "Permissions and freshness drive the architecture. The usual bottlenecks are not raw speed but retrieval quality, keeping the index in sync with source documents, enforcing who can see which chunk, and measuring quality with an evaluation set.")),
 Sd("Drill 5: movie or event ticket booking",
   "<b>Prompt: design a ticket booking system where a popular show goes on sale at noon.</b>",
   None,
   q=QC("Pick the best first clarifying question and the main bottleneck.", ["Ask: 'Is it okay if two people buy the same seat?' (no) so: 'How many users hit one show at once, and how long do we hold a seat during checkout?' Bottleneck: contention on the same few seats; double-booking must be impossible", "Ask: 'What is the app icon?' Bottleneck: the icon", "Ask: 'Can we cache the seat map forever?' Bottleneck: cache size", "Ask: 'Do we need search?' Bottleneck: autocomplete"], 0, "Seats are scarce, shared inventory. Use a strongly consistent store with atomic 'reserve if free' (a transaction or conditional update), temporary holds with expiry, and a virtual waiting room to flatten the noon spike. Browsing can be cached; booking cannot.")),
 Sd("Drill 6: a video streaming service",
   "<b>Prompt: design a service where users upload videos and others watch them.</b>",
   None,
   q=QC("Pick the best first clarifying question and the main bottleneck.", ["Ask: 'How many uploads and views per day, what video lengths, and which devices?' Bottleneck: storage and delivery bandwidth, solved with object storage, asynchronous transcoding into several qualities, and a CDN", "Ask: 'What is the comment font?' Bottleneck: comments", "Ask: 'Do we store videos in the SQL database?' Bottleneck: SQL syntax", "Ask: 'Is it free?' Bottleneck: the pricing page"], 0, "Video is huge. Uploads go to object storage, a queue triggers transcoding workers (adaptive bitrate formats), metadata sits in a database, and a CDN serves most views. Reads dominate, so the CDN hit rate is the number to protect.")),
 Sd("Drill 7: payments and wallet transfers",
   "<b>Prompt: design a wallet where users can move money to each other.</b>",
   None,
   q=QC("Pick the best first clarifying question and the main bottleneck.", ["Ask: 'What correctness guarantees do we need, and what happens on retries and partial failures?' Bottleneck: correctness, not raw speed: atomic double-entry updates, idempotency keys so a retry never pays twice, and an auditable ledger", "Ask: 'Can transfers be eventually correct?' Bottleneck: network speed", "Ask: 'How fast is the animation?' Bottleneck: the animation", "Ask: 'Could we keep balances only in a cache?' Bottleneck: cache size"], 0, "Money systems prioritise correctness and traceability over throughput. Use transactions on a relational store, an append-only ledger, idempotency keys on every write, and reconciliation jobs. Throughput is scaled later by partitioning accounts.")),
 Sd("Drill 8: syncing customer databases into a warehouse",
   "<b>Prompt (forward-deployed flavour): 500 customers each have a database. Design a service that copies their data into a warehouse every hour for analytics.</b>",
   None,
   q=QC("Pick the best first clarifying question and the main bottleneck.", ["Ask: 'How big is each customer's data, how fast does it change, what database types, and what freshness is promised?' Bottleneck: isolation between customers (one huge or broken customer must not delay the rest), schema changes, and incremental sync (CDC or timestamps) versus full copies", "Ask: 'Do customers like dashboards?' Bottleneck: chart colours", "Ask: 'Can we copy everything fully every hour?' Bottleneck: the weekend", "Ask: 'What is the project name?' Bottleneck: naming"], 0, "The hard part is operating many different sources reliably: per-tenant queues and quotas (noisy neighbours), incremental extraction, schema drift handling, backfills, retries with idempotent loads, and clear per-customer monitoring.")),
 Sd("The one-page checklist",
   "<b>1 Clarify</b>: who uses it, what must it do, what is out of scope; functional and non-functional (latency, availability, durability, consistency, cost). <b>2 Estimate</b>: QPS (average and peak), reads versus writes, storage per year, bandwidth, servers. <b>3 Interfaces</b>: main API calls and the data model. <b>4 Boxes</b>: clients, load balancer or gateway, stateless services, cache, database, queue, object store. <b>5 Deep-dive</b>: pick the bottleneck (hot key, write rate, fan-out, contention, freshness) and fix it. <b>6 Trade-offs</b>: say what you gave up (consistency, cost, simplicity) and why. <b>7 Failures</b>: single points of failure, retries and idempotency, backpressure, timeouts, backups, deploy safety. <b>8 Operate</b>: metrics, logs, traces, SLOs, alerts, cost. Throughout: think aloud, state assumptions, and ask the interviewer where to go deeper. If you are unsure of a fact, say so and say what you would check.",
   "Clarify -> Estimate -> API/data -> Boxes -> Deep-dive -> Trade-offs -> Failures -> Operate",
   q=QC("You are given a one-line prompt and 45 minutes. Which opening is best?", ["Draw a diagram for ten minutes without speaking", "Spend about five minutes confirming requirements, scale and assumptions out loud, then estimate, then draw", "Pick your favourite database and defend it", "Ask the interviewer to design it for you"], 1, "A short, explicit requirements and estimation phase makes every later choice defensible and shows the interviewer your method.")),
 ])
