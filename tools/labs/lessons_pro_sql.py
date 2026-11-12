# SQL Pro track. Executed inside lessons.py (after lessons_sql.py), so S/Sd/QC/PM/SEED/SEED2/_cell exist.
# Runnable screens are multi-statement scripts: the app runs the whole text on a fresh copy of SEED and shows the LAST
# result, so changes never persist. The helpers below mirror that at build time (every statement but the last is run,
# the last row-producing statement is the answer). Nothing in the Postgres module runs; it is display-only.
import sqlite3 as _sqp

def _sps_split(q):
    out, buf = [], ""
    parts = q.split(";")
    for i, part in enumerate(parts):
        buf += part + (";" if i < len(parts) - 1 else "")
        if i < len(parts) - 1 and _sqp.complete_statement(buf):
            out.append(buf); buf = ""
    if buf.strip():
        out.append(buf)
    return out

def _sps_run(q, seed=None):
    """Run a script like sql.js db.exec: return (columns, rows) of the last statement that returns rows."""
    db = _sqp.connect(":memory:", isolation_level=None)
    db.executescript(seed or SEED)
    last = ([], [])
    try:
        for st in _sps_split(q):
            cur = db.execute(st)
            if cur.description:
                last = ([c[0] for c in cur.description], cur.fetchall())
    finally:
        db.close()
    return last

def _sps_fails(q, seed=None):
    try:
        _sps_run(q, seed)
    except _sqp.Error as e:
        return str(e)
    return None

def _sps_plan(q, seed=None):
    return [r[-1] for r in _sps_run("EXPLAIN QUERY PLAN " + q, seed)[1]]

def _sps_out(q):
    cols, rows = _sps_run(q)
    assert len(rows) <= 8, ("keep lesson results short", q)
    return "\n".join([" | ".join(cols)] + [" | ".join(_cell(x) for x in r) for r in rows])

def PS(h, t, code, q=None, err=False):
    """Runnable SQL script screen. err=True means the script is meant to fail (the learner reads the error)."""
    if err:
        assert _sps_fails(code), ("expected an error", h)
    else:
        _sps_run(code)
    d = dict(h=h, t=t, code=code, run=True, sql=True)
    if q: d["q"] = q
    return d

def PQ(prompt, code, options, why):
    got = _sps_out(code)
    assert options.count(got) == 1, ("answer not among options exactly once", prompt, got, options)
    return dict(k="mc", q=prompt, code=code, o=options, a=options.index(got), why=why)

def PW(task, starter, sol, hint, ordered=False):
    r = _sps_run(sol)
    assert r[1], "solution returns nothing"
    r2 = _sps_run(sol, SEED2)
    assert r2[1], "solution returns nothing on SEED2"
    import re as _re
    assert "VALUES" not in sol.upper() and _re.search(r"\bFROM\s+\w", sol, _re.I)
    try:
        assert _sps_run(starter)[1] != r[1], "starter already solves it"
    except _sqp.Error:
        pass
    return dict(k="write", sql=True, task=task, starter=starter, sol=sol, hint=hint, ordered=ordered, tests=[])

# =========================================================================================================
# 1. Writing data
# =========================================================================================================
PM("sql-write", "SQL Pro", "Writing data safely",
   "Real jobs change data, not just read it: one UPDATE without a WHERE can wreck a table, so you need constraints, transactions and upserts.",
 [
 PS("INSERT adds rows",
    "So far you only <b>read</b> data. <code>INSERT INTO table (columns) VALUES (...)</code> adds a row. Always list the columns by name: if someone later adds a column to the table, an INSERT without a column list silently breaks. Each time you press Run, the app starts from a fresh copy of the practice database, so nothing you change here is kept. A script can have several statements; the app shows the result of the last one.",
    "INSERT INTO customers (id, name, city, email)\nVALUES (6, 'Fern', 'Pune', 'fern@fern.in'),\n       (7, 'Gale', 'Delhi', NULL);\n\nSELECT id, name, city FROM customers WHERE id >= 5 ORDER BY id;",
    q=PQ("What does the script show?",
         "INSERT INTO customers (id, name, city) VALUES (6, 'Fern', 'Pune');\nINSERT INTO customers (id, name, city) VALUES (7, 'Gale', 'Delhi');\nSELECT COUNT(*) AS n FROM customers;",
         ["n\n7", "n\n5", "n\n2"], "Five customers existed, two were added, so 7. The email column was left out of the list, so it is NULL for the new rows.")),
 PS("UPDATE changes existing rows",
    "<code>UPDATE table SET column = value WHERE condition</code> changes the rows that match. The right side can use the old value: <code>salary = salary + 5000</code>. The <b>WHERE</b> decides which rows are touched. Read the script, predict who gets the raise, then run it.",
    "UPDATE employees\nSET salary = salary + 5000\nWHERE dept = 'Support' AND salary IS NOT NULL;\n\nSELECT name, dept, salary FROM employees WHERE dept = 'Support' ORDER BY name;",
    q=PQ("What does the script show?",
         "UPDATE employees SET salary = salary + 5000 WHERE dept = 'Support' AND salary IS NOT NULL;\nSELECT name, salary FROM employees WHERE dept = 'Support' ORDER BY name;",
         ["name | salary\nNina | NULL\nTom | 45000", "name | salary\nNina | 5000\nTom | 45000", "name | salary\nNina | NULL\nTom | 40000"],
         "Tom gets +5000. Nina's salary is NULL and NULL + 5000 is still NULL, so even without the IS NOT NULL test she would stay NULL.")),
 PS("The classic disaster: UPDATE without WHERE",
    "Forget the WHERE and the UPDATE applies to <b>every row</b>. The database does not ask 'are you sure?'. This is how real outages happen. Run it and look at the count of people now earning 0.<br><br><b>Habit:</b> first write the same WHERE in a SELECT and check how many rows come back; only then turn it into an UPDATE.",
    "UPDATE employees SET salary = 0;   -- no WHERE: every row\n\nSELECT COUNT(*) AS paid_zero FROM employees WHERE salary = 0;",
    q=QC("You want to set one person's salary and type <code>UPDATE employees SET salary = 70000</code> by mistake (no WHERE). What happens?",
         ["All 10 employees get 70000, and the database accepts it without complaint", "Nothing: the database refuses a statement without WHERE", "Only the first row changes"], 0,
         "SQL does exactly what is written. Safer habits: run the matching SELECT first, wrap the change in a transaction (two screens ahead) and check the row count before committing.")),
 PS("DELETE removes rows",
    "<code>DELETE FROM table WHERE condition</code> removes matching rows. Same danger as UPDATE: without WHERE the table is emptied (the table itself stays). Many teams prefer a <b>soft delete</b> (an <code>is_deleted</code> flag) so a mistake can be undone. Run it, then think about what would happen to the orders of the removed customer.",
    "DELETE FROM orders WHERE customer_id = 2;\n\nSELECT COUNT(*) AS orders_left FROM orders;",
    q=PQ("What does the script show?",
         "DELETE FROM orders WHERE order_date < '2026-02-01';\nSELECT COUNT(*) AS n FROM orders;",
         ["n\n3", "n\n4", "n\n7"], "Three orders are dated in January (ids 1, 2 and 3) and get deleted, so 7 - 3 = 4 rows remain.")),
 PS("Constraints: rules the database enforces",
    "A <b>constraint</b> is a rule the database checks on every write, so bad data cannot get in even if the application has a bug. <b>PRIMARY KEY</b>: unique and not empty, identifies a row. <b>UNIQUE</b>: no two rows share the value. <b>NOT NULL</b>: a value is required. <b>CHECK (condition)</b>: the condition must hold. Run the script: the third INSERT breaks the CHECK, so you will see an error, which is the point.",
    "CREATE TABLE accounts (\n  id      INTEGER PRIMARY KEY,\n  email   TEXT NOT NULL UNIQUE,\n  balance REAL NOT NULL CHECK (balance >= 0)\n);\nINSERT INTO accounts (id, email, balance) VALUES (1, 'a@x.in', 100);\nINSERT INTO accounts (id, email, balance) VALUES (2, 'b@x.in', -5);\nSELECT * FROM accounts;",
    err=True,
    q=QC("Which INSERT does the table above reject?",
         ["INSERT INTO accounts (id, email, balance) VALUES (3, 'a@x.in', 10) because the email already exists (UNIQUE)", "INSERT INTO accounts (id, email, balance) VALUES (3, 'c@x.in', 0) because 0 is not above zero", "INSERT INTO accounts (id, email, balance) VALUES (3, 'c@x.in', 10) because id 3 was skipped"], 0,
         "UNIQUE rejects the duplicate email. The CHECK is balance &gt;= 0, so 0 is allowed. Ids do not have to be consecutive.")),
 PS("FOREIGN KEY: no orphans",
    "A <b>foreign key</b> says: this column must match a row in another table. Then an order can never point to a customer that does not exist. <code>ON DELETE CASCADE</code> says: if the parent row is deleted, delete its children too. (SQLite only enforces foreign keys after <code>PRAGMA foreign_keys = ON</code>; most other databases enforce them always.) Run it and predict the count before you do.",
    "PRAGMA foreign_keys = ON;\nCREATE TABLE team (id INTEGER PRIMARY KEY, name TEXT NOT NULL);\nCREATE TABLE member (\n  id INTEGER PRIMARY KEY,\n  team_id INTEGER NOT NULL REFERENCES team(id) ON DELETE CASCADE,\n  name TEXT\n);\nINSERT INTO team VALUES (1, 'Data'), (2, 'Infra');\nINSERT INTO member VALUES (1, 1, 'Asha'), (2, 1, 'Ravi'), (3, 2, 'Meera');\nDELETE FROM team WHERE id = 1;\nSELECT COUNT(*) AS members_left FROM member;",
    q=QC("With the foreign key above, what does <code>INSERT INTO member VALUES (4, 9, 'Zed')</code> do when no team has id 9?",
         ["It fails: team 9 does not exist, so the row would be an orphan", "It succeeds and creates team 9 automatically", "It succeeds and stores NULL in team_id"], 0,
         "A foreign key checks that the referenced row exists. It never creates it. team_id is also NOT NULL, so NULL would be rejected too.")),
 PS("Transactions: all or nothing",
    "A <b>transaction</b> groups statements so they succeed or fail <b>together</b>. <code>BEGIN</code> starts one, <code>COMMIT</code> makes it permanent, <code>ROLLBACK</code> throws every change since BEGIN away. Classic example: moving money needs two UPDATEs, and you never want only one to happen. Run it, then change ROLLBACK to COMMIT and run again.",
    "CREATE TABLE wallet (owner TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0));\nINSERT INTO wallet VALUES ('Asha', 100), ('Ravi', 50);\n\nBEGIN;\nUPDATE wallet SET balance = balance - 30 WHERE owner = 'Asha';\nUPDATE wallet SET balance = balance + 30 WHERE owner = 'Ravi';\nROLLBACK;\n\nSELECT owner, balance FROM wallet ORDER BY owner;",
    q=PQ("Same script but the transaction ends with COMMIT. What does it show?",
         "CREATE TABLE wallet (owner TEXT PRIMARY KEY, balance INTEGER NOT NULL);\nINSERT INTO wallet VALUES ('Asha', 100), ('Ravi', 50);\nBEGIN;\nUPDATE wallet SET balance = balance - 30 WHERE owner = 'Asha';\nUPDATE wallet SET balance = balance + 30 WHERE owner = 'Ravi';\nCOMMIT;\nSELECT owner, balance FROM wallet ORDER BY owner;",
         ["owner | balance\nAsha | 70\nRavi | 80", "owner | balance\nAsha | 100\nRavi | 50", "owner | balance\nAsha | 70\nRavi | 50"],
         "COMMIT keeps both updates: 100 - 30 = 70 and 50 + 30 = 80. With ROLLBACK both vanish. Never just one of them: that is atomicity.")),
 PS("Upsert: insert, or update if it exists",
    "Often you want: 'add this row, but if the key is already there, update it instead'. That is an <b>upsert</b>. In SQLite and Postgres it is <code>INSERT ... ON CONFLICT (key) DO UPDATE SET ...</code>. Inside the DO UPDATE, <code>excluded.column</code> means the value you tried to insert. It is one atomic statement, so two programs cannot both decide 'it does not exist' at the same moment.",
    "CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER NOT NULL);\nINSERT INTO stock VALUES ('pen', 10), ('ink', 4);\n\nINSERT INTO stock (sku, qty) VALUES ('pen', 5), ('pad', 7)\nON CONFLICT (sku) DO UPDATE SET qty = stock.qty + excluded.qty;\n\nSELECT sku, qty FROM stock ORDER BY sku;",
    q=PQ("What does the script show?",
         "CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER NOT NULL);\nINSERT INTO stock VALUES ('pen', 10), ('ink', 4);\nINSERT INTO stock (sku, qty) VALUES ('pen', 5), ('pad', 7)\nON CONFLICT (sku) DO UPDATE SET qty = excluded.qty;\nSELECT sku, qty FROM stock ORDER BY sku;",
         ["sku | qty\nink | 4\npad | 7\npen | 5", "sku | qty\nink | 4\npad | 7\npen | 15", "sku | qty\nink | 4\npen | 5"],
         "'pen' conflicts, and this version sets qty to the new value (excluded.qty = 5) instead of adding. 'pad' is new, so it is inserted. 'ink' is untouched.")),
 PS("Your turn: a safe UPDATE",
    "The script below has the classic bug. Fix it, then check the result with the final SELECT. (The checker also runs your script on a second hidden dataset.)",
    "UPDATE employees SET salary = salary + 5000;\nSELECT name, salary FROM employees WHERE dept = 'Sales' ORDER BY name;",
    q=PW("Give a raise of <b>5000</b> to every <code>Sales</code> employee who currently earns <b>less than 60000</b>, using an UPDATE. Then show <code>name</code> and <code>salary</code> of <b>all</b> Sales employees, sorted by name. The starter has the classic bug: it raises everybody.",
         "UPDATE employees\nSET salary = salary + 5000;\n\nSELECT name, salary FROM employees WHERE dept = 'Sales' ORDER BY name;",
         "UPDATE employees SET salary = salary + 5000 WHERE dept = 'Sales' AND salary < 60000;\nSELECT name, salary FROM employees WHERE dept = 'Sales' ORDER BY name;",
         "Add WHERE dept = 'Sales' AND salary < 60000 to the UPDATE. People with a NULL salary fail the test salary &lt; 60000 (unknown), so they are left alone automatically.", ordered=True)),
 ])

# =========================================================================================================
# 2. Indexes and query plans
# =========================================================================================================
def PP(prompt, query, options, a, why, setup="", must=None):
    """Plan question. The right option is checked at build time against the real SQLite plan (must = text the plan contains)."""
    plan = " / ".join(r[-1] for r in _sps_run(setup + "\nEXPLAIN QUERY PLAN " + query)[1])
    assert must is None or must in plan, ("plan check failed", prompt, plan)
    return QC(prompt, options, a, why)

PM("sql-index", "SQL Pro", "Indexes and query plans",
   "A query that takes 2 ms on practice data can take minutes on 50 million rows; indexes and the query plan are how engineers find and fix that.",
 [
 PS("An index is a sorted shortcut",
    "Without help, the database finds <code>customer_id = 3</code> by reading <b>every row</b> of the table and checking each one. An <b>index</b> is a second, sorted copy of one or more columns, with a pointer back to the row, like the index at the back of a book. The database can jump straight to the matches (internally a structure called a B-tree). The practice database already has two indexes, on the events table. List them.",
    "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' ORDER BY name;",
    q=QC("What is the main trade-off of adding an index?",
         ["Reads that filter on that column get faster, but every INSERT, UPDATE and DELETE has extra work and the index takes disk space", "Reads get faster and nothing gets slower", "The table is physically sorted and takes less space"], 0,
         "An index is extra data that must be kept in step with the table on every write. That is why you do not index every column.")),
 PS("EXPLAIN QUERY PLAN: ask the database what it will do",
    "Put <code>EXPLAIN QUERY PLAN</code> in front of a query and the database tells you its plan instead of running it. Read the <b>last column (detail)</b>; the other columns are internal. Two words matter most: <b>SCAN</b> means read the whole table, <b>SEARCH ... USING INDEX</b> means jump in through an index. Run it: orders has no index on customer_id, so you will see a SCAN. Then change <code>orders</code> / <code>customer_id</code> to <code>events</code> / <code>user_id</code>, which is indexed.",
    "EXPLAIN QUERY PLAN\nSELECT * FROM orders WHERE customer_id = 3;",
    q=PP("An index exists on events(user_id). What does the plan for <code>SELECT * FROM events WHERE user_id = 3</code> say?",
         "SELECT * FROM events WHERE user_id = 3",
         ["SEARCH events USING INDEX idx_events_user (user_id=?)", "SCAN events", "SEARCH events USING INDEX idx_events_ts (ts=?)"], 0,
         "The WHERE column matches the index, so the database searches the index instead of scanning the table. The (user_id=?) part shows which column the index is used for.", must="SEARCH events USING INDEX idx_events_user")),
 PS("CREATE INDEX changes the plan",
    "<code>CREATE INDEX name ON table (column)</code> builds the index. Same query, different plan. The script creates the index and then asks for the plan. (Remember: each run starts from a fresh database, so the index disappears afterwards. In real life it stays until you drop it.)",
    "CREATE INDEX idx_orders_customer ON orders (customer_id);\n\nEXPLAIN QUERY PLAN\nSELECT * FROM orders WHERE customer_id = 3;",
    q=QC("You see <b>SCAN orders</b> in the plan of a slow query that filters on one column. What is the first thing to consider?",
         ["Whether an index on the filtered column would help (and whether the table is big enough to matter)", "Rewrite the query with more subqueries", "Add LIMIT 10 to make it read less"], 0,
         "A SCAN on a small table is fine. On a big table it is the classic symptom of a missing index. LIMIT does not stop a scan from reading until it has found enough, and often it needs everything first (for example when sorting).")),
 PS("Covering index: answer from the index alone",
    "If the index contains every column the query needs, the database never touches the table at all. That is a <b>covering index</b> and the plan says <b>COVERING INDEX</b>. Here the index has customer_id <i>and</i> amount, and the query needs only those two.",
    "CREATE INDEX idx_orders_cust_amount ON orders (customer_id, amount);\n\nEXPLAIN QUERY PLAN\nSELECT SUM(amount) FROM orders WHERE customer_id = 3;",
    q=PP("With an index on <code>orders (customer_id, amount)</code>, which query can be answered from the index alone?",
         "SELECT SUM(amount) FROM orders WHERE customer_id = 3",
         ["SELECT SUM(amount) FROM orders WHERE customer_id = 3", "SELECT * FROM orders WHERE customer_id = 3", "SELECT order_date FROM orders WHERE customer_id = 3"], 0,
         "The first needs only customer_id and amount, both in the index. The other two need columns (all of them, or order_date) that the index does not hold, so the table must be visited.",
         setup="CREATE INDEX idx_orders_cust_amount ON orders (customer_id, amount);", must="COVERING INDEX")),
 PS("What defeats an index: functions on the column",
    "The index is sorted by the <i>raw column value</i>. If you wrap the column in a function, the database cannot use the sorted order and must compute the function for every row, so it SCANs. Compare these two ways to ask for January events: the first wraps <code>ts</code> in <code>strftime</code>; the second compares <code>ts</code> itself to a range. (The same trap exists in every database; a LIKE with a leading wildcard, <code>name LIKE '%me'</code>, defeats an index for the same reason: the start of the value is unknown, so sorted order is useless.)",
    "EXPLAIN QUERY PLAN\nSELECT * FROM events WHERE strftime('%Y-%m', ts) = '2026-01';\n-- now replace the WHERE with the range version and run again:\n-- WHERE ts >= '2026-01-01' AND ts < '2026-02-01'",
    q=PP("An index exists on events(ts). Which WHERE can use it?",
         "SELECT * FROM events WHERE ts >= '2026-01-01' AND ts < '2026-02-01'",
         ["WHERE ts >= '2026-01-01' AND ts < '2026-02-01'", "WHERE strftime('%Y-%m', ts) = '2026-01'", "WHERE ts || '' = '2026-01-05'"], 0,
         "Only the range compares the raw column. Wrapping it in a function or concatenating to it forces a SCAN. Rule: keep the column bare on one side, do the calculation on the other side.", must="USING INDEX idx_events_ts")),
 PS("Composite index: column order matters",
    "An index on <code>(customer_id, order_date)</code> is sorted by customer_id first, and by order_date inside each customer, like a phone book sorted by last name then first name. It helps queries that filter on the <b>leftmost</b> column(s). Put equality columns first, then the range or sort column. Run it: both columns are used.",
    "CREATE INDEX idx_orders_cust_date ON orders (customer_id, order_date);\n\nEXPLAIN QUERY PLAN\nSELECT * FROM orders WHERE customer_id = 1 AND order_date >= '2026-02-01';",
    q=PP("With an index on <code>orders (customer_id, order_date)</code>, what does the plan for <code>WHERE order_date = '2026-02-14'</code> (no customer_id) look like?",
         "SELECT * FROM orders WHERE order_date = '2026-02-14'",
         ["A SCAN: the index is sorted by customer_id first, so it cannot find a date directly", "A SEARCH using the index on order_date", "An error, because the leftmost column is missing"], 0,
         "You cannot look up 'Smith, Anna' in a phone book if you only know the first name. Skipping the leftmost column loses the index. If you need that query too, add a separate index on order_date.",
         setup="CREATE INDEX idx_orders_cust_date ON orders (customer_id, order_date);", must="SCAN orders")),
 PS("Indexes are not free, and the N+1 trap",
    "Every index must be updated on every INSERT, UPDATE and DELETE of the indexed columns, and takes disk space. Index the columns you filter, join and sort on in queries that really run often, not everything.<br><br>The other classic slowdown is in application code, not SQL: the <b>N+1 pattern</b>. Code runs 1 query to fetch N customers, then loops and runs 1 query per customer for their orders: N+1 round trips. Each trip costs network time, even when each query is fast. The fix is one query with a JOIN and GROUP BY (below) or one <code>WHERE customer_id IN (...)</code>.<pre><code>customers = db.query(\"SELECT id FROM customers\")      # 1 query\nfor c in customers:                                      # N queries\n    db.query(\"SELECT SUM(amount) FROM orders WHERE customer_id = ?\", c.id)</code></pre>",
    "SELECT c.name, COALESCE(SUM(o.amount), 0) AS total\nFROM customers c LEFT JOIN orders o ON o.customer_id = c.id\nGROUP BY c.id, c.name\nORDER BY c.name;",
    q=QC("A page shows 200 customers and is slow. The code runs one query per customer inside a loop. What is the best fix?",
         ["Fetch all the data in one JOIN / GROUP BY (or one IN query) so there is a single round trip", "Add an index to every column of the customers table", "Run the 200 queries faster by increasing LIMIT"], 0,
         "The cost is the number of round trips, not the speed of each query. Collapsing 201 queries into 1 removes the network and parsing overhead 200 times over.")),
 PS("Your turn: create the index",
    "Create an index with the column order you learned: equality column first, date second. The final SELECT is given; it checks the name, the table and the column order of the index you built.",
    "SELECT name, tbl_name, REPLACE(sql, ' ', '') LIKE '%(customer_id,order_date)' AS cust_then_date\nFROM sqlite_master\nWHERE type = 'index' AND name = 'idx_orders_customer_date';",
    q=PW("Create an index named <code>idx_orders_customer_date</code> on <code>orders</code> over the columns <code>customer_id</code> then <code>order_date</code> (in that order). Keep the SELECT at the bottom; it should come back with one row.",
         "-- write your CREATE INDEX statement here\n\nSELECT name, tbl_name, REPLACE(sql, ' ', '') LIKE '%(customer_id,order_date)' AS cust_then_date\nFROM sqlite_master\nWHERE type = 'index' AND name = 'idx_orders_customer_date';",
         "CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);\nSELECT name, tbl_name, REPLACE(sql, ' ', '') LIKE '%(customer_id,order_date)' AS cust_then_date\nFROM sqlite_master\nWHERE type = 'index' AND name = 'idx_orders_customer_date';",
         "CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date); one statement, ending with a semicolon, placed before the SELECT.")),
 ])

# =========================================================================================================
# 3. Advanced querying
# =========================================================================================================
PM("sql-advanced", "SQL Pro", "Advanced querying",
   "Real reports need conditional logic, dates, text cleaning, set logic and window tricks; this is the toolbox behind most analyst and data-engineer interview questions.",
 [
 PS("CASE: if / else inside a query",
    "<code>CASE WHEN condition THEN value ... ELSE value END</code> is SQL's if/else. It checks the WHEN lines top to bottom and uses the first that is true. Two shortcuts built from it: <code>COALESCE(a, b)</code> returns the first value that is not NULL, and <code>NULLIF(a, b)</code> returns NULL when a equals b (handy to turn 'bad' values into NULL, or to avoid dividing by zero: <code>x / NULLIF(y, 0)</code>). Notice where the NULL case sits: it must come first, because <code>NULL &gt;= 100000</code> is never true.",
    "SELECT name, salary,\n  CASE WHEN salary IS NULL    THEN 'unknown'\n       WHEN salary >= 100000  THEN 'high'\n       WHEN salary >= 60000   THEN 'mid'\n       ELSE 'low' END AS band,\n  COALESCE(salary, 0) AS pay,\n  NULLIF(dept, 'Support') AS dept_or_null\nFROM employees WHERE id >= 8 ORDER BY id;",
    q=PQ("What does this show?",
         "SELECT name, CASE WHEN salary >= 60000 THEN 'mid' ELSE 'low' END AS band FROM employees WHERE dept = 'Support' ORDER BY name",
         ["name | band\nNina | low\nTom | low", "name | band\nNina | NULL\nTom | low", "name | band\nTom | low"],
         "Nina's salary is NULL, so the WHEN test is not true and the ELSE branch runs: 'low'. CASE has no NULL branch unless you write one, which is exactly why Nina is mislabelled here.")),
 PS("Dates in SQLite",
    "SQLite has no real date type: dates are text like <code>'2026-02-14'</code> (ISO format sorts correctly as text). Functions turn text into answers: <code>strftime('%Y-%m', d)</code> extracts the year-month, <code>date(d, '+7 days')</code> adds time, <code>julianday(a) - julianday(b)</code> is the difference in days. This is how you group by month. (Other databases use <code>DATE_TRUNC</code> or <code>EXTRACT</code>; see the Postgres module.) Beware: adding a month to Jan 31 has no Feb 31, so SQLite rolls over; try <code>date('2026-01-31', '+1 month')</code>.",
    "SELECT strftime('%Y-%m', order_date) AS month,\n       COUNT(*) AS orders,\n       SUM(amount) AS revenue\nFROM orders\nGROUP BY month\nORDER BY month;",
    q=PQ("What does this show?",
         "SELECT date('2026-01-31', '+1 month') AS d",
         ["d\n2026-03-03", "d\n2026-02-28", "d\n2026-02-31"], "There is no 31 February, so the extra days spill into March: 2026-02-31 becomes 2026-03-03. Month arithmetic at month ends is a classic source of bugs.")),
 PS("Text functions",
    "Real data is messy text. Handy functions: <code>LENGTH</code>, <code>UPPER</code>/<code>LOWER</code>, <code>TRIM</code>, <code>SUBSTR(s, start, length)</code> (positions start at 1), <code>INSTR(s, find)</code> (position of find, 0 if absent), <code>REPLACE(s, old, new)</code>, and <code>||</code> to join strings. Combine them: everything after the <code>@</code> of an email is the domain.",
    "SELECT name, email,\n       SUBSTR(email, INSTR(email, '@') + 1) AS domain,\n       UPPER(SUBSTR(name, 1, 3)) || '-' || id AS code\nFROM customers\nWHERE email IS NOT NULL\nORDER BY id;",
    q=PQ("What does this show?",
         "SELECT SUBSTR('hello@x.in', 1, INSTR('hello@x.in', '@') - 1) AS user_part",
         ["user_part\nhello", "user_part\nhello@", "user_part\nx.in"], "INSTR finds the @ at position 6. SUBSTR from 1 for 6 - 1 = 5 characters gives 'hello'.")),
 PS("Correlated subquery: a query that depends on the row",
    "A <b>subquery</b> is a query inside a query. A <b>correlated</b> subquery refers to the outer row, so it is re-evaluated for each outer row (conceptually; the optimiser often does better). Here, for each employee <code>e</code> the inner query computes the average salary of <b>that employee's department</b>.",
    "SELECT e.name, e.dept, e.salary\nFROM employees e\nWHERE e.salary > (SELECT AVG(e2.salary)\n                  FROM employees e2\n                  WHERE e2.dept = e.dept)\nORDER BY e.name;",
    q=PQ("What does this show?",
         "SELECT e.name FROM employees e WHERE e.salary > (SELECT AVG(salary) FROM employees x WHERE x.dept = e.dept) AND e.dept = 'Sales' ORDER BY e.name",
         ["name\nAsha", "name\nAsha\nMeera\nRavi", "name\nAsha\nJohn"], "Sales average is (90000 + 60000 + 60000 + 45000) / 4 = 63750. Only Asha (90000) is above it. Ravi and Meera, at 60000, are below.")),
 PS("EXISTS, IN and the NOT IN trap",
    "<code>x IN (subquery)</code> asks 'is x in this list?'. <code>EXISTS (subquery)</code> asks 'does at least one matching row exist?'. They agree, until NULLs arrive. <b>If the list contains a NULL, <code>x NOT IN (list)</code> returns no rows at all</b>, because 'x is different from NULL' is unknown, never true. Here, manager_id has NULLs (the top bosses), so asking for employees who are not anyone's manager with NOT IN silently returns nothing. <code>NOT EXISTS</code> is safe. Run it, then swap in the commented query.",
    "SELECT name FROM employees\nWHERE id NOT IN (SELECT manager_id FROM employees);\n\n-- safe version, try it:\n-- SELECT name FROM employees e\n-- WHERE NOT EXISTS (SELECT 1 FROM employees m WHERE m.manager_id = e.id)",
    q=QC("What is the safest way to find customers who have no orders?",
         ["WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id) (or a LEFT JOIN with IS NULL)", "WHERE c.id NOT IN (SELECT customer_id FROM orders), always safe", "WHERE c.id <> (SELECT customer_id FROM orders)"], 0,
         "NOT IN breaks the moment the subquery column can contain a NULL (and it can, if customer_id is not declared NOT NULL). NOT EXISTS and LEFT JOIN ... IS NULL do not have that problem.")),
 PS("UNION, INTERSECT, EXCEPT",
    "Set operators combine whole result sets that have the same number of columns. <code>UNION</code> merges and <b>removes duplicates</b>; <code>UNION ALL</code> merges and keeps every row (faster, and what you usually want when you know there are no overlaps). <code>INTERSECT</code> keeps rows present in both. <code>EXCEPT</code> keeps rows in the first but not the second. Below: customers who ordered in January but never since.",
    "SELECT customer_id FROM orders WHERE order_date <  '2026-02-01'\nEXCEPT\nSELECT customer_id FROM orders WHERE order_date >= '2026-02-01';",
    q=PQ("What does this show?",
         "SELECT customer_id FROM orders WHERE order_date < '2026-02-01'\nINTERSECT\nSELECT customer_id FROM orders WHERE order_date >= '2026-02-01'",
         ["customer_id\n1", "customer_id\n1\n2\n3\n5", "customer_id\n2"], "Customer 1 ordered in January and again in February. Customer 2 ordered only in January, which is what EXCEPT found; customers 3 and 5 only ordered later.")),
 PS("Conditional aggregation: pivot by hand",
    "Put a <code>CASE</code> <b>inside</b> an aggregate and you count or sum only some rows. Do it once per bucket and you have turned rows into columns, a <b>pivot</b>. This one pattern powers most 'metric by segment' reports and is a favourite interview question.",
    "SELECT customer_id,\n  SUM(CASE WHEN order_date <  '2026-02-01' THEN amount ELSE 0 END) AS jan,\n  SUM(CASE WHEN order_date >= '2026-02-01' AND order_date < '2026-03-01' THEN amount ELSE 0 END) AS feb,\n  SUM(CASE WHEN order_date >= '2026-03-01' THEN amount ELSE 0 END) AS mar\nFROM orders\nGROUP BY customer_id\nORDER BY customer_id;",
    q=PQ("What does this show?",
         "SELECT SUM(CASE WHEN amount >= 100 THEN 1 ELSE 0 END) AS big, COUNT(*) AS total FROM orders",
         ["big | total\n2 | 7", "big | total\n7 | 7", "big | total\n2 | 2"], "Two orders are 100 or more (120 and 300). The CASE gives 1 for those and 0 for the rest, so SUM counts them while COUNT(*) counts every row.")),
 PS("Gaps and islands: consecutive days",
    "Question: 'how long are a user's login streaks?'. Trick: number each user's logins with <code>ROW_NUMBER()</code> and subtract that number of days from the date. Within an unbroken run of consecutive days the result is <b>the same date</b>; after a gap it jumps. Group by that value and each group is one streak (an 'island'). Run it for users 4 and 8, then look at <code>grp</code> by selecting it.",
    "WITH g AS (\n  SELECT user_id, login_date,\n         date(login_date, '-' || ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) || ' days') AS grp\n  FROM logins WHERE user_id IN (4, 8)\n)\nSELECT user_id, MIN(login_date) AS streak_start, MAX(login_date) AS streak_end, COUNT(*) AS days\nFROM g GROUP BY user_id, grp\nORDER BY user_id, streak_start;",
    q=PQ("What does this show for user 1, whose logins are Jan 4, Jan 5, Jan 11, Feb 5?",
         "WITH g AS (SELECT login_date, date(login_date, '-' || ROW_NUMBER() OVER (ORDER BY login_date) || ' days') AS grp FROM logins WHERE user_id = 1)\nSELECT MIN(login_date) AS start, COUNT(*) AS days FROM g GROUP BY grp ORDER BY start",
         ["start | days\n2026-01-04 | 2\n2026-01-11 | 1\n2026-02-05 | 1", "start | days\n2026-01-04 | 4", "start | days\n2026-01-04 | 1\n2026-01-05 | 1\n2026-01-11 | 1\n2026-02-05 | 1"],
         "Only Jan 4 and Jan 5 are on consecutive days, so they form one island of 2 days. Jan 11 and Feb 5 each stand alone.")),
 PS("Deduplicate with ROW_NUMBER",
    "Duplicates are everywhere in real data. To keep exactly one row per key: number the rows inside each key with <code>ROW_NUMBER() OVER (PARTITION BY key ORDER BY what_decides)</code> and keep <code>rn = 1</code>. The ORDER BY decides which copy survives (earliest, latest, highest). Always add a unique tie-breaker such as <code>id</code>, otherwise ties are broken arbitrarily. Example: the first purchase of each user.",
    "WITH ranked AS (\n  SELECT user_id, ts,\n         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ts, id) AS rn\n  FROM events WHERE event = 'purchase'\n)\nSELECT user_id, ts AS first_purchase FROM ranked WHERE rn = 1 ORDER BY user_id;",
    q=PW("Show each customer's <b>most recent order</b>: <code>customer_id</code>, <code>order_date</code>, <code>amount</code>, one row per customer, sorted by <code>customer_id</code>. If a customer has two orders on the same date, keep the one with the higher <code>id</code>.",
         "WITH ranked AS (\n  SELECT customer_id, order_date, amount,\n         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS rn\n  FROM orders\n)\nSELECT customer_id, order_date, amount FROM ranked WHERE rn = 1 ORDER BY customer_id;",
         "WITH ranked AS (\n  SELECT customer_id, order_date, amount,\n         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC, id DESC) AS rn\n  FROM orders\n)\nSELECT customer_id, order_date, amount FROM ranked WHERE rn = 1 ORDER BY customer_id;",
         "The starter keeps the OLDEST order. Sort the window newest first: ORDER BY order_date DESC, id DESC.", ordered=True)),
 ])

# =========================================================================================================
# 4. Data modelling
# =========================================================================================================
_FLAT = "CREATE TABLE sales_flat (sale_id INTEGER, customer_name TEXT, customer_city TEXT, product TEXT, price REAL);\nINSERT INTO sales_flat VALUES (1,'Acme','Hyderabad','Pen',10),(2,'Acme','Hyderabad','Pad',25),(3,'Acme','Hyderabad','Ink',40),(4,'Bolt','Pune','Pen',10),(5,'Bolt','Pune','Ink',40);\n"

PM("sql-model", "SQL Pro", "Data modelling",
   "Good queries start with a good table design; data engineers are hired to design tables that stay correct and fast as data grows.",
 [
 PS("Why one big table goes wrong",
    "A beginner's design puts everything in one wide table. Look at it: Acme's name and city are repeated on every sale. That causes three kinds of trouble, called <b>anomalies</b>: <b>update</b> (change Acme's city and you must fix every row, miss one and the data disagrees with itself), <b>insert</b> (you cannot record a customer who has bought nothing yet) and <b>delete</b> (delete Bolt's last sale and you forget Bolt exists). The cure is to store each fact once, in the table it belongs to.",
    _FLAT + "\nSELECT * FROM sales_flat ORDER BY sale_id;",
    q=PQ("Acme moves to Mumbai. How many rows of the flat table must change?",
         _FLAT + "SELECT COUNT(*) AS rows_to_fix FROM sales_flat WHERE customer_name = 'Acme';",
         ["rows_to_fix\n3", "rows_to_fix\n1", "rows_to_fix\n5"], "One change in the real world becomes 3 edits, and a bug that updates only 2 leaves the data contradicting itself.")),
 PS("Normalisation: 1NF, 2NF, 3NF in plain words",
    "<b>Normalisation</b> is the process of splitting tables so each fact is stored once. In plain words:<ul><li><b>1NF</b>: one value per cell (no 'Pen, Pad' lists in a column) and no repeating column groups (<code>item1, item2, item3</code>).</li><li><b>2NF</b>: every column depends on the <i>whole</i> key, not just part of it (matters when the key has two columns).</li><li><b>3NF</b>: every column depends on <i>the key and nothing but the key</i>; customer city depends on the customer, not on the sale.</li></ul>Run the script: customers move to their own table, sales point to them, and Acme's move is now one UPDATE.",
    _FLAT + "CREATE TABLE customer_n (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);\nINSERT INTO customer_n (name, city) SELECT DISTINCT customer_name, customer_city FROM sales_flat ORDER BY 1;\nCREATE TABLE sale_n (sale_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customer_n(customer_id), product TEXT, price REAL);\nINSERT INTO sale_n SELECT f.sale_id, c.customer_id, f.product, f.price FROM sales_flat f JOIN customer_n c ON c.name = f.customer_name;\n\nUPDATE customer_n SET city = 'Mumbai' WHERE name = 'Acme';   -- one row\n\nSELECT s.sale_id, c.name, c.city, s.product\nFROM sale_n s JOIN customer_n c ON c.customer_id = s.customer_id\nORDER BY s.sale_id;",
    q=QC("A table <code>orders(order_id, customer_id, customer_city, amount)</code> stores the customer's city on every order. Which normal form does that break?",
         ["3NF: customer_city depends on customer_id, not directly on the order key", "1NF: it has more than three columns", "2NF: because amount is a number"], 0,
         "customer_city is a fact about the customer. Move it to a customers table and keep only customer_id in orders.")),
 PS("Keys: primary, foreign, surrogate",
    "A <b>primary key</b> uniquely identifies a row. A <b>foreign key</b> in another table points to it. A <b>natural key</b> comes from the real world (an email, a PAN number) and can change or be reused. A <b>surrogate key</b> is a meaningless number the database hands out (<code>id</code>), which never changes. Most designs use surrogate primary keys and put a UNIQUE constraint on the natural key. In SQLite an <code>INTEGER PRIMARY KEY</code> fills itself in when you omit it. Careful: without <code>AUTOINCREMENT</code> SQLite can <b>reuse</b> the highest id after it is deleted. Predict before running.",
    "CREATE TABLE tag (id INTEGER PRIMARY KEY, label TEXT UNIQUE);\nINSERT INTO tag (label) VALUES ('red'), ('blue');\nINSERT INTO tag (label) VALUES ('green');\nDELETE FROM tag WHERE label = 'green';\nINSERT INTO tag (label) VALUES ('pink');\n\nSELECT id, label FROM tag ORDER BY id;",
    q=PQ("Same script, but the table is declared <code>id INTEGER PRIMARY KEY AUTOINCREMENT</code>. What does it show?",
         "CREATE TABLE tag (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT UNIQUE);\nINSERT INTO tag (label) VALUES ('red'), ('blue');\nINSERT INTO tag (label) VALUES ('green');\nDELETE FROM tag WHERE label = 'green';\nINSERT INTO tag (label) VALUES ('pink');\nSELECT id, label FROM tag ORDER BY id;",
         ["id | label\n1 | red\n2 | blue\n4 | pink", "id | label\n1 | red\n2 | blue\n3 | pink", "id | label\n1 | red\n2 | blue\n3 | green\n4 | pink"],
         "AUTOINCREMENT never reuses an id, so green's 3 stays retired and pink gets 4. Without it (the run above) pink took 3. Other databases do this with SERIAL, IDENTITY or sequences.")),
 PS("One-to-many and many-to-many",
    "<b>One-to-many</b>: one customer, many orders. The 'many' side holds a foreign key (orders.customer_id). <b>Many-to-many</b>: an order has many products and a product is in many orders. You cannot put a foreign key on either side, so you add a <b>junction table</b> (also called bridge or link table) with one row per pair, whose primary key is the pair itself. Below, <code>order_item</code> is the junction and also carries the quantity, because quantity belongs to the pair.",
    "CREATE TABLE product (product_id INTEGER PRIMARY KEY, name TEXT, price REAL);\nINSERT INTO product VALUES (1, 'Pen', 10), (2, 'Pad', 25), (3, 'Ink', 40);\n\nCREATE TABLE order_item (\n  order_id INTEGER, product_id INTEGER, qty INTEGER,\n  PRIMARY KEY (order_id, product_id)\n);\nINSERT INTO order_item SELECT id, 1 + id % 3, 1 + id % 2 FROM orders;\n\nSELECT p.name, COUNT(*) AS orders, SUM(oi.qty) AS units\nFROM product p JOIN order_item oi ON oi.product_id = p.product_id\nGROUP BY p.product_id ORDER BY p.name;",
    q=QC("Students enrol in many courses and each course has many students. How do you model it?",
         ["Three tables: students, courses, and an enrolment table with (student_id, course_id) as its key", "Put a comma-separated list of course ids in a column of students", "Two tables, with a foreign key from each to the other"], 0,
         "A comma-separated list breaks 1NF and cannot be joined or constrained. Mutual foreign keys cannot represent 'many' on both sides. The junction table is the standard answer.")),
 PS("Star schema: facts and dimensions",
    "For analytics, the favourite design is the <b>star schema</b>. A <b>fact table</b> holds the events you measure (one row per order, with numbers like amount) and foreign keys. <b>Dimension tables</b> describe the who/what/when (customer, product, date) and are used to slice and group. Queries become: join the fact to a few dimensions, GROUP BY dimension columns, SUM the facts. It is deliberately less normalised than a transactional design, because reading speed and simplicity matter more than avoiding duplication. The script builds a tiny one from the practice data.",
    "CREATE TABLE dim_customer (customer_key INTEGER PRIMARY KEY, name TEXT, city TEXT);\nINSERT INTO dim_customer (name, city) SELECT name, city FROM customers ORDER BY id;\nCREATE TABLE dim_date (date_key TEXT PRIMARY KEY, month TEXT);\nINSERT INTO dim_date SELECT DISTINCT order_date, strftime('%Y-%m', order_date) FROM orders;\nCREATE TABLE fact_orders (order_id INTEGER PRIMARY KEY, customer_key INTEGER, date_key TEXT, amount REAL);\nINSERT INTO fact_orders SELECT id, customer_id, order_date, amount FROM orders;\n\nSELECT d.month, c.city, SUM(f.amount) AS revenue\nFROM fact_orders f\nJOIN dim_customer c ON c.customer_key = f.customer_key\nJOIN dim_date d     ON d.date_key = f.date_key\nGROUP BY d.month, c.city\nORDER BY d.month, c.city;",
    q=QC("In a star schema for web analytics, which is most likely the fact table?",
         ["page_views: one row per view, with user_key, page_key, date_key and seconds_on_page", "dim_page: one row per page with its title and url", "dim_date: one row per calendar day"], 0,
         "Facts are the measurable events that keep growing (every view). Dimensions are the smaller descriptive lists you filter and group by.")),
 PS("Slowly changing dimensions: type 1",
    "Dimension data changes: a customer moves city. A <b>slowly changing dimension (SCD)</b> is how you decide what to do with the old value. <b>Type 1 overwrites</b>: simple, but history is lost, so last year's sales now look like they came from the new city. Run it, and look at where customer 1's January orders are attributed.",
    "CREATE TABLE dim_cust (cust_id INTEGER PRIMARY KEY, city TEXT);\nINSERT INTO dim_cust VALUES (1, 'Hyderabad');\n\nUPDATE dim_cust SET city = 'Pune' WHERE cust_id = 1;   -- type 1: overwrite\n\nSELECT o.id, o.order_date, d.city\nFROM orders o JOIN dim_cust d ON d.cust_id = o.customer_id\nORDER BY o.id;",
    q=QC("The business needs 'revenue by the city the customer lived in <b>at the time of the order</b>'. Which SCD type?",
         ["Type 2: keep a row per version, with valid_from and valid_to", "Type 1: overwrite the city", "Neither; just store the city in a text file"], 0,
         "Only type 2 remembers old values. Type 1 would report all of the customer's history under the newest city.")),
 PS("Slowly changing dimensions: type 2",
    "<b>Type 2</b> keeps history: a change <b>closes</b> the old row (sets <code>valid_to</code> and <code>is_current = 0</code>) and <b>inserts a new row</b> with a new surrogate key. Because one customer now has several rows, the surrogate key (<code>cust_key</code>) is the primary key and <code>cust_id</code> is the business key. To attach each order to the version valid on its date, join with <code>BETWEEN valid_from AND valid_to</code>. The open-ended current row uses a far-future date such as <code>9999-12-31</code>.",
    "CREATE TABLE dim_cust (cust_key INTEGER PRIMARY KEY, cust_id INTEGER, city TEXT, valid_from TEXT, valid_to TEXT, is_current INTEGER);\nINSERT INTO dim_cust (cust_id, city, valid_from, valid_to, is_current) VALUES (1, 'Hyderabad', '2026-01-01', '9999-12-31', 1);\n\n-- customer 1 moves to Pune on 2026-02-10\nUPDATE dim_cust SET valid_to = '2026-02-09', is_current = 0 WHERE cust_id = 1 AND is_current = 1;\nINSERT INTO dim_cust (cust_id, city, valid_from, valid_to, is_current) VALUES (1, 'Pune', '2026-02-10', '9999-12-31', 1);\n\nSELECT o.id, o.order_date, d.city\nFROM orders o JOIN dim_cust d\n  ON d.cust_id = o.customer_id AND o.order_date BETWEEN d.valid_from AND d.valid_to\nORDER BY o.id;",
    q=QC("In the type 2 table above, how many rows describe customer 1 after the move, and which one has <code>is_current = 1</code>?",
         ["Two rows; the Pune row is current", "One row; it was updated to Pune", "Two rows; both are current"], 0,
         "The old row is kept (closed on 2026-02-09) and a new row is added. Exactly one row per customer should be current, and a query for 'now' filters on is_current = 1.")),
 PS("Your turn: build a dimension with surrogate keys",
    "Here is the pattern for cities: create a small dimension table where the database assigns the surrogate key, fill it from existing data with INSERT ... SELECT, then join back. Run it, then do the same for departments. (The grader rejects typed-in VALUES lists, so you read the data from the tables, as you would in a real pipeline.)",
    "CREATE TABLE city_dim (city_key INTEGER PRIMARY KEY, city TEXT NOT NULL);\nINSERT INTO city_dim (city) SELECT DISTINCT city FROM customers ORDER BY city;\n\nSELECT c.name, d.city_key\nFROM customers c JOIN city_dim d ON d.city = c.city\nORDER BY c.name;",
    q=PW("Create a table <code>dept_dim (dept_key INTEGER PRIMARY KEY, dept TEXT NOT NULL)</code>. Fill it with one row for each distinct <code>dept</code> in <code>employees</code>, inserted in alphabetical order of dept (so the keys 1, 2, 3 ... follow that order), letting the database assign <code>dept_key</code>. Then show each employee's <code>name</code> and <code>dept_key</code>, sorted by <code>name</code>.",
         "-- 1. CREATE TABLE dept_dim ...\n-- 2. INSERT INTO dept_dim (dept) SELECT ...\n\nSELECT e.name, d.dept_key\nFROM employees e JOIN dept_dim d ON d.dept = e.dept\nORDER BY e.name;",
         "CREATE TABLE dept_dim (dept_key INTEGER PRIMARY KEY, dept TEXT NOT NULL);\nINSERT INTO dept_dim (dept) SELECT DISTINCT dept FROM employees ORDER BY dept;\nSELECT e.name, d.dept_key\nFROM employees e JOIN dept_dim d ON d.dept = e.dept\nORDER BY e.name;",
         "INSERT INTO dept_dim (dept) SELECT DISTINCT dept FROM employees ORDER BY dept; leave dept_key out of the column list so SQLite numbers the rows 1, 2, 3 in the order they arrive.", ordered=True)),
 ])

# =========================================================================================================
# 5. From SQLite to Postgres and warehouses (display-only). Syntax checked against postgresql.org/docs,
#    cloud.google.com/bigquery/docs and docs.snowflake.com when this module was written.
# =========================================================================================================
_NORUN = "<p class=\"hint\"><b>Display only:</b> nothing on this screen runs in the browser. Install PostgreSQL (free, postgresql.org/download) or run it in Docker, load a few tables, and type each example into <code>psql</code> yourself. Typing it is how it sticks.</p>"

PM("sql-postgres", "SQL Pro", "From SQLite to Postgres and warehouses",
   "Jobs run on Postgres, BigQuery or Snowflake, not SQLite: this is the short list of differences that trip up people who only practised on a browser database.",
 [
 Sd("Casts and case-insensitive search",
    "<p>You have practised on SQLite, which is forgiving about types. <b>PostgreSQL</b> (Postgres) is strict and has its own conveniences. First, converting types. Standard SQL is <code>CAST(x AS type)</code>; Postgres also accepts the shorthand <code>x::type</code>. Second, <code>LIKE</code> in Postgres is <b>case-sensitive</b>; <code>ILIKE</code> is the Postgres extension that ignores case. (In SQLite, LIKE already ignores case for English letters, so a query can change meaning when you move.)</p>" + _NORUN,
    "-- PostgreSQL\nSELECT '42'::int + 1;                 -- 43, the :: shorthand\nSELECT CAST('42' AS int) + 1;         -- 43, standard SQL, works everywhere\nSELECT name FROM customers WHERE name ILIKE 'a%';   -- matches Acme and acme",
    q=QC("Which Postgres expression does the same as <code>CAST(price AS numeric)</code>?",
         ["price::numeric", "price:numeric", "numeric::price"], 0,
         "The double colon goes between the value and the type name, in that order. CAST(...) is the portable form and is the safer choice in code that must run on several databases.")),
 Sd("Time: date_trunc and generate_series",
    "<p>SQLite uses <code>strftime('%Y-%m', d)</code> to bucket by month. Postgres has real date and timestamp types and <code>date_trunc('month', d)</code>, which rounds a timestamp down to the start of its month (also 'day', 'week', 'year'...). <code>generate_series(start, stop, step)</code> produces a column of consecutive values; with timestamps it builds a <b>calendar</b> you can LEFT JOIN to, so days with no sales show up as 0 instead of vanishing.</p>" + _NORUN,
    "-- PostgreSQL: revenue per month\nSELECT date_trunc('month', order_date) AS month, SUM(amount) AS revenue\nFROM orders\nGROUP BY 1\nORDER BY 1;\n\n-- a calendar of days, then fill the gaps\nSELECT d::date AS day, COALESCE(SUM(o.amount), 0) AS revenue\nFROM generate_series('2026-01-01'::timestamp, '2026-01-07'::timestamp, '1 day') AS d\nLEFT JOIN orders o ON o.order_date = d::date\nGROUP BY 1 ORDER BY 1;",
    q=QC("You have a table of sales with some days missing and need a report with <b>one row for every day</b>, zero where nothing sold. What do you reach for in Postgres?",
         ["generate_series to build every day, LEFT JOIN the sales to it, COALESCE the sum to 0", "date_trunc('day', ...) alone, since it creates the missing days", "An INNER JOIN between sales and itself"], 0,
         "date_trunc only rounds values that exist. To invent the missing days you need a generated series as the left side of a LEFT JOIN.")),
 Sd("FILTER: conditional aggregates, made readable",
    "<p>Last module you wrote <code>SUM(CASE WHEN ... THEN ... END)</code>. Postgres has a cleaner form: put <code>FILTER (WHERE condition)</code> after any aggregate and only the rows that pass are fed into it. Several filtered aggregates in one SELECT are a pivot without CASE.</p>" + _NORUN,
    "-- PostgreSQL\nSELECT\n  COUNT(*)                                  AS orders,\n  COUNT(*) FILTER (WHERE amount >= 100)    AS big_orders,\n  SUM(amount) FILTER (WHERE order_date < '2026-02-01') AS january_revenue\nFROM orders;",
    q=QC("Which is equivalent to <code>SUM(CASE WHEN dept = 'Sales' THEN salary END)</code>?",
         ["SUM(salary) FILTER (WHERE dept = 'Sales')", "SUM(salary) WHERE dept = 'Sales'", "SUM(salary FILTER dept = 'Sales')"], 0,
         "The syntax is aggregate(...) FILTER (WHERE ...). The filter sits outside the aggregate's parentheses and keeps the word WHERE.")),
 Sd("Top row per group: DISTINCT ON, LATERAL, QUALIFY",
    "<p>You know the portable way: <code>ROW_NUMBER()</code> in a CTE, then <code>WHERE rn = 1</code>. Engines add shortcuts for 'best row per group'.</p><ul><li><b>Postgres <code>DISTINCT ON (key)</code></b> keeps the first row of each key. 'First' is whatever your ORDER BY says, and the ORDER BY must <b>start with</b> the DISTINCT ON expressions (documented rule).</li><li><b>Postgres <code>LATERAL</code></b> lets a subquery in FROM refer to columns of tables listed before it, so you can run 'the top 2 orders of <i>this</i> customer' once per customer.</li><li><b>Snowflake and BigQuery <code>QUALIFY</code></b> filters on a window function directly, like HAVING does for aggregates, with no CTE. Support details differ between the two, so check each one's docs for restrictions.</li></ul>" + _NORUN,
    "-- PostgreSQL: latest order per customer\nSELECT DISTINCT ON (customer_id) customer_id, order_date, amount\nFROM orders\nORDER BY customer_id, order_date DESC;\n\n-- PostgreSQL: two latest orders per customer, keeping customers with none\nSELECT c.name, o.order_date, o.amount\nFROM customers c\nLEFT JOIN LATERAL (\n  SELECT order_date, amount FROM orders\n  WHERE customer_id = c.id\n  ORDER BY order_date DESC LIMIT 2\n) o ON true;\n\n-- Snowflake / BigQuery: same as the first one, using QUALIFY\nSELECT customer_id, order_date, amount\nFROM orders\nQUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1;",
    q=QC("In Postgres, <code>SELECT DISTINCT ON (customer_id) ... ORDER BY order_date DESC</code> is rejected or unpredictable. Why?",
         ["The ORDER BY must start with customer_id; it should be ORDER BY customer_id, order_date DESC", "DISTINCT ON cannot be combined with ORDER BY at all", "order_date must be inside the DISTINCT ON parentheses"], 0,
         "DISTINCT ON expressions must match the leftmost ORDER BY expressions. The extra ORDER BY columns after them decide which row of each group is kept.")),
 Sd("RETURNING and ON CONFLICT",
    "<p>Two features that remove a whole class of bugs. <code>INSERT ... ON CONFLICT (key) DO UPDATE ...</code> is the Postgres upsert you met in the first module; <code>EXCLUDED</code> is the row you tried to insert, and the docs say a conflict target is required for DO UPDATE. It is one atomic statement, so two programs cannot both decide the row is missing. <code>RETURNING</code> makes INSERT, UPDATE or DELETE hand back the affected rows, so you get the generated id or the new value in the same round trip instead of running a second SELECT.</p>" + _NORUN,
    "-- PostgreSQL\nINSERT INTO stock (sku, qty) VALUES ('pen', 5)\nON CONFLICT (sku) DO UPDATE SET qty = stock.qty + EXCLUDED.qty\nRETURNING sku, qty;\n\nDELETE FROM orders WHERE id = 7 RETURNING *;   -- shows exactly what was removed",
    q=QC("Your app inserts a row and needs the auto-generated id it received. What is the clean Postgres way?",
         ["Add RETURNING id to the INSERT", "Run SELECT MAX(id) right after the INSERT", "Add ON CONFLICT DO UPDATE"], 0,
         "RETURNING gives the exact rows you just wrote. SELECT MAX(id) can return another session's row if two inserts happen close together.")),
 Sd("JSONB: semi-structured data inside a table",
    "<p>Postgres can store JSON in a column. Use <b>jsonb</b> (a parsed binary form that can be indexed and searched) rather than plain <code>json</code> (which keeps the original text). Operators: <code>-&gt;</code> gets a field and returns <b>jsonb</b>; <code>-&gt;&gt;</code> gets a field and returns <b>text</b>. Both return NULL, not an error, when the key is missing. <code>@&gt;</code> asks 'does this JSON contain that JSON?'. A <b>GIN</b> index speeds up containment searches.</p>" + _NORUN,
    "-- PostgreSQL\nCREATE TABLE event_log (id bigserial PRIMARY KEY, payload jsonb NOT NULL);\n\nSELECT payload ->> 'user'                  AS user_name,   -- text\n       payload -> 'items' -> 0 ->> 'sku'    AS first_sku    -- arrays start at 0\nFROM event_log\nWHERE payload @> '{\"type\": \"purchase\"}';\n\nCREATE INDEX idx_event_payload ON event_log USING gin (payload);",
    q=QC("What is the difference between <code>payload -&gt; 'user'</code> and <code>payload -&gt;&gt; 'user'</code>?",
         ["-> returns the value as jsonb (a string keeps its quotes); ->> returns it as plain text", "-> reads an object, ->> reads an array", "They are identical; the second is an alias"], 0,
         "Use ->> at the end of a path when you want a normal text value to compare, group or cast. Use -> in the middle of a path to keep drilling into nested JSON.")),
 Sd("EXPLAIN (ANALYZE, BUFFERS) and psql basics",
    "<p>In Postgres, plain <code>EXPLAIN</code> shows the planned steps. <code>EXPLAIN ANALYZE</code> <b>really runs the statement</b> and adds actual timings and row counts; <code>BUFFERS</code> adds how many data blocks came from memory cache (<i>hit</i>) versus disk (<i>read</i>). Plan node names: <b>Seq Scan</b> (reads the whole table, like SQLite's SCAN), <b>Index Scan</b>, <b>Index Only Scan</b> (the covering-index case) and <b>Bitmap Heap Scan</b>. Compare the planner's estimated rows to the actual rows: a big gap usually means stale statistics. Because ANALYZE executes the statement, test an UPDATE or DELETE inside a transaction you roll back (the Postgres docs suggest exactly this).</p><p><b>psql</b> is the command-line client: <code>\\dt</code> lists tables, <code>\\d orders</code> describes one, <code>\\l</code> lists databases, <code>\\c name</code> connects to one, <code>\\timing</code> shows how long statements take, <code>\\i file.sql</code> runs a file, <code>\\q</code> quits.</p>" + _NORUN,
    "-- PostgreSQL\nEXPLAIN (ANALYZE, BUFFERS)\nSELECT * FROM orders WHERE customer_id = 3;\n\n-- safe way to measure a write\nBEGIN;\nEXPLAIN ANALYZE UPDATE orders SET amount = amount + 1 WHERE customer_id = 3;\nROLLBACK;",
    q=QC("You want to measure an <code>UPDATE</code> with EXPLAIN ANALYZE on a production-like database without keeping the change. What do you do?",
         ["Wrap it: BEGIN; EXPLAIN ANALYZE UPDATE ...; ROLLBACK;", "Nothing: EXPLAIN never changes data, even with ANALYZE", "Add LIMIT 1 to the UPDATE"], 0,
         "ANALYZE executes the statement, so its side effects happen. The transaction and ROLLBACK undo them while still giving you real timings.")),
 Sd("Under the hood: MVCC, isolation, connection pools",
    "<p><b>MVCC</b> (multiversion concurrency control): an UPDATE or DELETE in Postgres does not erase the old row version at once, because another transaction may still need to see it. Readers do not block writers. Old versions are cleaned up later by <b>VACUUM</b>, which autovacuum normally runs for you; if cleanup falls behind (for example because of very long-running transactions), tables bloat and queries slow down.</p><p><b>Isolation levels</b> decide what a transaction sees while others run. The Postgres default is <b>Read Committed</b>: each statement sees data committed before it started. <b>Repeatable Read</b> gives a transaction one consistent snapshot. <b>Serializable</b> behaves as if transactions ran one at a time, and may abort one with a serialization failure, so the application must <b>retry the whole transaction</b>. (Read Uncommitted exists by name but behaves like Read Committed.)</p><p><b>Connection pooling</b>: opening a database connection is relatively expensive and a server can only handle a limited number, so applications keep a small pool of open connections and reuse them (in the app, or through a pooler such as PgBouncer). Hundreds of web workers opening their own connections is a classic way to knock a database over.</p>" + _NORUN,
    "-- PostgreSQL: choose an isolation level for one transaction\nBEGIN ISOLATION LEVEL REPEATABLE READ;\nSELECT SUM(balance) FROM wallet;\n-- ... other sessions may commit changes now; this transaction still sees its snapshot\nSELECT SUM(balance) FROM wallet;   -- same answer as above\nCOMMIT;",
    q=QC("A Postgres transaction at SERIALIZABLE fails with a serialization failure. What should the application do?",
         ["Retry the whole transaction from BEGIN", "Ignore it; the data was saved anyway", "Switch to Read Uncommitted"], 0,
         "The database aborted it to protect correctness. Nothing was kept. The standard fix is a retry loop around the entire transaction, not just the last statement.")),
 Sd("Warehouses: BigQuery and Snowflake think in bytes",
    "<p>Warehouses store each <b>column</b> separately (columnar storage), so a query reads only the columns it names. That is why <code>SELECT *</code> is an expensive habit there: you pay to read every column. BigQuery on-demand billing is by bytes read, and its docs say a <code>LIMIT</code> on an unclustered table does not reduce the data read. Cut cost by naming columns (BigQuery also has <code>SELECT * EXCEPT (col)</code>), by filtering on the <b>partition</b> column so whole chunks are skipped (BigQuery partitioned tables), and by <b>clustering</b> (sorting data by columns you filter on). Snowflake splits tables into automatic <b>micro-partitions</b> and skips those whose stored value ranges cannot match your filter; you can define clustering keys for large tables. Check the size with a <b>dry run</b> before running a big query.</p><p>Nested data is first-class: BigQuery has <code>ARRAY</code> and <code>STRUCT</code> and <code>UNNEST</code> turns an array into rows; Snowflake stores JSON-like data in a <code>VARIANT</code> column, reached with a colon path and <code>::</code> casts, and <code>LATERAL FLATTEN</code> turns arrays into rows.</p>" + _NORUN,
    "-- BigQuery\nSELECT o.id, item\nFROM orders AS o, UNNEST(o.items) AS item;      -- one row per array element\n\nSELECT * EXCEPT (email) FROM customers;         -- all columns except one\n\n-- Snowflake\nSELECT src:customer.name::string AS customer\nFROM raw_events;\n\nSELECT f.value:sku::string AS sku\nFROM raw_events, LATERAL FLATTEN(input => src:items) f;",
    q=QC("On BigQuery with on-demand pricing you run <code>SELECT * FROM big_events LIMIT 10</code> on an unpartitioned, unclustered table. What is the cost?",
         ["You pay for reading every column of the whole table; LIMIT does not reduce it. Name only the columns you need and filter on the partition column", "Only 10 rows are read, so it is nearly free", "Free: SELECT * is always cached"], 0,
         "Cost follows bytes scanned, and columnar storage makes the number of columns the lever you control. Use a dry run to see the estimate before running.")),
 ])

# =========================================================================================================
# 6. SQL interview patterns
# =========================================================================================================
PM("sql-interview", "SQL Pro", "SQL interview patterns",
   "A handful of query shapes cover most SQL interview rounds; recognise the shape from the wording and you can write the answer in minutes.",
 [
 PS("Pattern: second-highest salary",
    "Wording: 'the second highest salary'. Three traps: <b>ties</b> (two people on the top salary: is the second-highest the same number or the next different one?), <b>NULLs</b>, and <b>no answer</b> (only one distinct salary exists). The usual answer is the second <i>distinct</i> value. A scalar subquery returns NULL, not an error, when no row exists, which is the correct output for 'no second-highest'. Always say aloud how you treat ties; interviewers listen for it.",
    "SELECT (\n  SELECT DISTINCT salary FROM employees\n  WHERE salary IS NOT NULL\n  ORDER BY salary DESC\n  LIMIT 1 OFFSET 1\n) AS second_highest;",
    q=PQ("What does this return?",
         "SELECT (SELECT DISTINCT salary FROM employees WHERE dept = 'Support' AND salary IS NOT NULL ORDER BY salary DESC LIMIT 1 OFFSET 1) AS second_highest",
         ["second_highest\nNULL", "second_highest\n0", "second_highest\n40000"],
         "Support has one non-NULL salary (Tom, 40000), so there is no second distinct value: OFFSET 1 skips it and finds nothing, and the scalar subquery turns 'no rows' into NULL.")),
 PS("Pattern: top N per group",
    "Wording: 'the top 2 earners in each department'. Shape: a window function numbers the rows inside each group, a CTE or subquery wraps it, and the outer query keeps <code>rn &lt;= N</code>. Choose the function on purpose: <code>ROW_NUMBER</code> (exactly N rows, ties broken arbitrarily unless you add a tie-breaker), <code>RANK</code> (ties share a rank and leave gaps), <code>DENSE_RANK</code> (ties share a rank, no gaps). Remember a window function cannot sit in WHERE, hence the wrapper.",
    "WITH r AS (\n  SELECT name, dept, salary,\n         ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, name) AS rn\n  FROM employees WHERE salary IS NOT NULL\n)\nSELECT dept, name, salary FROM r WHERE rn <= 2 ORDER BY dept, rn;",
    q=PW("Combine the two patterns: for each <code>dept</code>, show the <b>second-highest distinct</b> salary as <code>second_salary</code> (columns: <code>dept</code>, <code>second_salary</code>). Ignore NULL salaries. A department with fewer than two distinct salaries must not appear. Sort by <code>dept</code>.",
         "SELECT dept, salary AS second_salary\nFROM (\n  SELECT dept, salary,\n         DENSE_RANK() OVER (PARTITION BY dept ORDER BY ) AS rnk\n  FROM employees\n)\nWHERE rnk = ;",
         "SELECT DISTINCT dept, salary AS second_salary\nFROM (\n  SELECT dept, salary,\n         DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk\n  FROM employees\n  WHERE salary IS NOT NULL\n)\nWHERE rnk = 2\nORDER BY dept;",
         "DENSE_RANK gives tied salaries the same rank, so rank 2 is the second distinct value. Filter NULLs inside the inner query (otherwise a NULL can take rank 2), and use SELECT DISTINCT because two people can share that salary.", ordered=True)),
 PS("Pattern: running total",
    "Wording: 'cumulative revenue by day'. Shape: <code>SUM(x) OVER (ORDER BY day)</code>. Be explicit about the <b>frame</b>, the set of rows the sum covers: <code>ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code> means 'from the first row to this one'. Without a frame, the default treats rows with equal ORDER BY values as peers and adds them together, so a duplicated date gives surprising results. Say that in an interview and you stand out.",
    "SELECT day, revenue,\n  SUM(revenue) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total\nFROM daily\nORDER BY day;",
    q=PQ("What does this show?",
         "SELECT day, SUM(revenue) OVER (ORDER BY day ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS two_day FROM daily WHERE day <= '2026-03-03' ORDER BY day",
         ["day | two_day\n2026-03-01 | 100\n2026-03-02 | 220\n2026-03-03 | 210", "day | two_day\n2026-03-01 | 100\n2026-03-02 | 220\n2026-03-03 | 310", "day | two_day\n2026-03-01 | 220\n2026-03-02 | 210\n2026-03-03 | 90"],
         "The frame is 'the previous row and this row'. Day 3 = 120 + 90 = 210, not the full 310. Changing the frame turns a running total into a moving sum.")),
 PS("Pattern: change versus the previous period",
    "Wording: 'month-over-month growth', 'compare to yesterday'. Shape: aggregate to the period first (a CTE), then <code>LAG(value) OVER (ORDER BY period)</code> to bring the previous period's value onto the same row. Change = value - previous; percent change = 100 * change / previous. The first period has no previous value, so it is NULL: do not turn it into 0 unless the question says so. Beware division by zero (<code>NULLIF(prev, 0)</code>).",
    "WITH m AS (\n  SELECT strftime('%Y-%m', order_date) AS month, SUM(amount) AS revenue\n  FROM orders GROUP BY 1\n)\nSELECT month, revenue,\n       LAG(revenue) OVER (ORDER BY month) AS prev,\n       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month), 1) AS pct_change\nFROM m ORDER BY month;",
    q=PW("From the table <code>daily</code> (<code>day</code>, <code>revenue</code>) show <code>day</code>, <code>revenue</code>, <code>change</code> (revenue minus the previous day's revenue, NULL on the first day) and <code>running_total</code> (cumulative revenue up to and including that day). Sort by <code>day</code>.",
         "SELECT day, revenue,\n       revenue - AS change,\n       SUM(revenue) OVER (ORDER BY day) AS running_total\nFROM daily\nORDER BY day;",
         "SELECT day, revenue,\n       revenue - LAG(revenue) OVER (ORDER BY day) AS change,\n       SUM(revenue) OVER (ORDER BY day) AS running_total\nFROM daily\nORDER BY day;",
         "LAG(revenue) OVER (ORDER BY day) is the previous day's revenue. The first day has no previous row, so change is NULL automatically.", ordered=True)),
 PS("Pattern: duplicate detection",
    "Wording: 'find duplicate emails / repeated events'. Shape: <code>GROUP BY</code> the columns that define 'the same', then <code>HAVING COUNT(*) &gt; 1</code>. To see the actual duplicate rows (not just the keys), join the keys back or use <code>COUNT(*) OVER (PARTITION BY ...)</code>. To delete duplicates and keep one, number them with ROW_NUMBER (see Advanced querying) and delete <code>rn &gt; 1</code>.",
    "SELECT user_id, event, COUNT(*) AS times\nFROM events\nGROUP BY user_id, event\nHAVING COUNT(*) > 1\nORDER BY user_id;",
    q=PQ("What does this show?",
         "SELECT COUNT(*) AS duplicated_pairs FROM (SELECT user_id, event FROM events GROUP BY user_id, event HAVING COUNT(*) > 1)",
         ["duplicated_pairs\n2", "duplicated_pairs\n3", "duplicated_pairs\n25"], "Only two (user, event) pairs repeat: user 4 visited twice and user 8 purchased twice.")),
 PS("Pattern: 'who never did X'",
    "Wording: 'customers with no orders', 'users who signed up but never purchased'. Shape: an <b>anti-join</b>. Three equivalent forms: <code>LEFT JOIN ... WHERE right.id IS NULL</code>, <code>NOT EXISTS (subquery)</code>, and <code>NOT IN</code> (avoid it: the NULL trap). For 'did A but not B', combine <code>EXISTS</code> for A with <code>NOT EXISTS</code> for B. Run the basic version, then do the A-but-not-B version yourself.",
    "SELECT c.name\nFROM customers c\nWHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);",
    q=PW("From <code>users</code> and <code>events</code>: show the <code>name</code> of every user who has a <code>signup</code> event but <b>no</b> <code>purchase</code> event. Sort by <code>name</code>.",
         "SELECT u.name\nFROM users u\nWHERE EXISTS (SELECT 1 FROM events e WHERE e.user_id = u.id AND e.event = 'signup')\n  AND\nORDER BY u.name;",
         "SELECT u.name\nFROM users u\nWHERE EXISTS (SELECT 1 FROM events e WHERE e.user_id = u.id AND e.event = 'signup')\n  AND NOT EXISTS (SELECT 1 FROM events e WHERE e.user_id = u.id AND e.event = 'purchase')\nORDER BY u.name;",
         "Add a second condition: NOT EXISTS (SELECT 1 FROM events e WHERE e.user_id = u.id AND e.event = 'purchase').", ordered=True)),
 PS("Pattern: retention and cohorts",
    "Wording: 'of the users who signed up in January, how many came back in February?'. A <b>cohort</b> is a group defined by when they started (their signup month). <b>Retention</b> is the share of the cohort that is active again after some time. Shape: assign each user a cohort, then count how many have an activity row in the target period. <code>SUM(EXISTS(...))</code> counts users for whom the test is true. Divide by the cohort size for a rate; handle the latest cohort carefully, because its next month may not have happened yet.",
    "SELECT strftime('%Y-%m', u.signup_date) AS cohort,\n       COUNT(*) AS users,\n       SUM(EXISTS (\n         SELECT 1 FROM logins l\n         WHERE l.user_id = u.id\n           AND strftime('%Y-%m', l.login_date) = strftime('%Y-%m', date(u.signup_date, 'start of month', '+1 month'))\n       )) AS back_next_month\nFROM users u\nGROUP BY cohort\nORDER BY cohort;",
    q=PQ("What does this show for the February cohort?",
         "SELECT strftime('%Y-%m', u.signup_date) AS cohort, COUNT(*) AS users, SUM(EXISTS (SELECT 1 FROM logins l WHERE l.user_id = u.id AND strftime('%Y-%m', l.login_date) = strftime('%Y-%m', date(u.signup_date, 'start of month', '+1 month')))) AS back_next_month FROM users u GROUP BY cohort HAVING cohort = '2026-02'",
         ["cohort | users | back_next_month\n2026-02 | 3 | 1", "cohort | users | back_next_month\n2026-02 | 3 | 3", "cohort | users | back_next_month\n2026-02 | 1 | 1"],
         "Three users signed up in February (Divya, Esha, Farhan). Only Divya has a login in March (on 9 March), so one came back.")),
 PS("Pattern: the median",
    "Wording: 'median order value'. SQLite has no MEDIAN. The idea: sort the values, skip to the middle, and average the middle one (odd count) or middle two (even count). With LIMIT/OFFSET: skip <code>(n - 1) / 2</code> rows (whole-number division) and take <code>2 - n % 2</code> rows (1 if n is odd, 2 if even), then AVG them. Postgres offers <code>percentile_cont(0.5) WITHIN GROUP (ORDER BY x)</code> for this. In an interview, state first whether the median of an even count is the average of the two middle values.",
    "SELECT AVG(amount) AS median_amount\nFROM (\n  SELECT amount FROM orders\n  ORDER BY amount\n  LIMIT 2 - (SELECT COUNT(*) FROM orders) % 2\n  OFFSET (SELECT (COUNT(*) - 1) / 2 FROM orders)\n);",
    q=PW("Show the <b>median</b> of <code>amount</code> in the <code>orders</code> table as one column named <code>median_amount</code>. If the number of orders is even, average the two middle values.",
         "SELECT AVG(amount) AS median_amount\nFROM (\n  SELECT amount FROM orders\n  ORDER BY amount\n  LIMIT 1\n  OFFSET 0\n);",
         "SELECT AVG(amount) AS median_amount\nFROM (\n  SELECT amount FROM orders\n  ORDER BY amount\n  LIMIT 2 - (SELECT COUNT(*) FROM orders) % 2\n  OFFSET (SELECT (COUNT(*) - 1) / 2 FROM orders)\n);",
         "n = COUNT(*). OFFSET (n - 1) / 2 skips to the middle; LIMIT 2 - n % 2 takes 1 row for odd n and 2 rows for even n. The hidden data has a different number of orders, so a fixed LIMIT or OFFSET will fail.")),
 ])
