# SQL lessons for Days 8-11. Every shown result is computed by running the query on the practice database
# (SEED) with sqlite3 at build time, so answers cannot drift from the real engine. Executed inside lessons.py.
import sqlite3 as _sq

def _cell(x):
    if x is None: return "NULL"
    if isinstance(x, float): return str(int(x)) if x == int(x) else repr(x)
    return str(x)

def _sqlrun(q, seed=None):
    db = _sq.connect(":memory:"); db.executescript(seed or SEED)
    cur = db.execute(q); cols = [c[0] for c in cur.description]; rows = cur.fetchall(); db.close()
    return cols, rows

def _sqlout(q):
    cols, rows = _sqlrun(q)
    assert len(rows) <= 8, ("keep lesson results short", q)
    return "\n".join([" | ".join(cols)] + [" | ".join(_cell(x) for x in r) for r in rows])

def SS(h, t, code, q=None):
    """SQL screen: an editable query the learner can run."""
    _sqlrun(code)
    d = dict(h=h, t=t, code=code, run=True, sql=True)
    if q: d["q"] = q
    return d

def SQ(prompt, code, options, why):
    got = _sqlout(code)
    assert options.count(got) == 1, ("answer not among options exactly once", prompt, got, options)
    return dict(k="mc", q=prompt, code=code, o=options, a=options.index(got), why=why)

def SW(task, starter, sol, hint, ordered=False):
    _sqlrun(sol)
    try:
        r = _sqlrun(starter); assert r[1] != _sqlrun(sol)[1], "starter already solves it"
    except _sq.Error:
        pass
    seed2 = _sqlrun(sol, SEED2)   # the hidden data must also accept the solution
    return dict(k="write", sql=True, task=task, starter=starter, sol=sol, hint=hint, ordered=ordered, tests=[])

def _opts(*qs):
    return list(qs)

LESSONS[8] = [
 SS("A table is rows and columns",
    "A database stores data in <b>tables</b>, like sheets. Each <b>row</b> is one thing (one customer) and each <b>column</b> is one fact about it (name, city). <code>SELECT * FROM customers</code> means: show every column from the table called customers. Press <b>Run</b>.",
    "SELECT * FROM customers",
    q=SQ("What comes back?", "SELECT name FROM customers WHERE id = 2",
         ["name\nBolt", "name\nAcme", "id\n2"], "WHERE id = 2 keeps only the row whose id is 2 (Bolt). SELECT name shows only that column.")),
 SS("SELECT picks columns",
    "Instead of <code>*</code>, name the columns you want, separated by commas. Order in the query is the order of the output. Change the columns and run it again.",
    "SELECT name, city FROM customers",
    q=SQ("What comes back?", "SELECT city FROM customers WHERE name = 'Dune'",
         ["city\nDelhi", "city\nPune", "name\nDune"], "Dune is the row, city is the column you asked for. Text in SQL goes in single quotes.")),
 SS("WHERE keeps only matching rows",
    "<code>WHERE</code> goes after the table name and keeps only rows where the condition is true. Compare with <code>=</code>, <code>&gt;</code>, <code>&lt;</code>, <code>&gt;=</code>, <code>&lt;=</code>, <code>&lt;&gt;</code> (not equal). Join conditions with <code>AND</code> and <code>OR</code>.",
    "SELECT name, salary FROM employees WHERE salary > 90000",
    q=SQ("What comes back?", "SELECT name FROM employees WHERE dept = 'Sales' AND salary < 50000",
         ["name\nJohn", "name\nJohn\nRavi", "name\nAsha\nRavi\nMeera\nJohn"], "Only John is in Sales and under 50000. AND needs both parts to be true.")),
 SS("IN, LIKE and ORDER BY",
    "<code>IN ('Pune','Delhi')</code> matches any in the list. <code>LIKE 'A%'</code> matches text that starts with A (<code>%</code> means any characters). <code>ORDER BY</code> sorts: <code>ASC</code> small to large (the default), <code>DESC</code> large to small.",
    "SELECT name, city FROM customers WHERE city IN ('Pune', 'Delhi') ORDER BY name",
    q=SQ("What comes back?", "SELECT name FROM customers WHERE city IN ('Pune', 'Delhi') ORDER BY name",
         ["name\nBolt\nDune\nEcho", "name\nAcme\nCora", "name\nEcho\nDune\nBolt"], "Bolt and Echo are in Pune, Dune is in Delhi, then sorted A to Z.")),
 SS("LIMIT: only the first few rows",
    "<code>LIMIT 3</code> stops after three rows. With <code>ORDER BY salary DESC</code> it gives the top 3. Order first, then limit: the order of the words in a query is fixed.",
    "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3",
    q=SQ("What comes back?", "SELECT name, salary FROM employees WHERE salary IS NOT NULL ORDER BY salary ASC LIMIT 2",
         ["name | salary\nTom | 40000\nJohn | 45000", "name | salary\nNina | NULL\nTom | 40000", "name | salary\nPriya | 120000\nAsha | 90000"], "Smallest first: Tom 40000 then John 45000. We removed the missing salary so it did not interfere.")),
 SS("NULL means unknown, not zero",
    "A <b>NULL</b> is a missing value. It is never equal to anything, not even to another NULL, so <code>= NULL</code> finds nothing. Use <code>IS NULL</code> or <code>IS NOT NULL</code>. Run both versions below and compare.",
    "SELECT name FROM customers WHERE email = NULL;\n-- run this one too:\n-- SELECT name FROM customers WHERE email IS NULL",
    q=SQ("Nina's salary is NULL. What comes back?", "SELECT name FROM employees WHERE dept = 'Support' AND salary <> 60000",
         ["name\nTom", "name\nTom\nNina", "name\nNina"], "NULL <> 60000 is not true, it is unknown, so Nina is left out. This silent loss of rows is the most common SQL surprise.")),
 SS("Calculated columns and aliases",
    "You can calculate in the SELECT list and rename the result with <code>AS</code>. The alias is just a label for the output column.",
    "SELECT name, salary * 12 AS yearly FROM employees WHERE id <= 2",
    q=SQ("What comes back?", "SELECT name, salary / 1000 AS k FROM employees WHERE id = 2",
         ["name | k\nRavi | 60", "name | k\nRavi | 60000", "name | k\nRavi | 6"], "60000 divided by 1000 is 60. The alias k names the column.")),
 SS("Your turn: write a whole query",
    "You have every piece: SELECT, FROM, WHERE with AND, ORDER BY. Write it in the box below. The checker runs your query on the practice data <i>and</i> on a second hidden set of data, so it has to be genuinely right, not just match what you see.",
    "SELECT name FROM customers",
    q=SW("Show <code>name</code> and <code>salary</code> of everyone in the <code>Engineering</code> department earning more than 90000. Highest salary first; if two have the same salary, sort those by name A to Z.",
         "SELECT \nFROM employees\n",
         "SELECT name, salary FROM employees WHERE dept = 'Engineering' AND salary > 90000 ORDER BY salary DESC, name",
         "Order of words: SELECT columns FROM table WHERE conditions ORDER BY first, second. Two sort keys are separated by a comma.", ordered=True)),
]

LESSONS[9] = [
 SS("Count the rows",
    "<code>COUNT(*)</code> counts rows. Aggregate functions squash many rows into one answer. Run it, then change the table name.",
    "SELECT COUNT(*) AS orders_total FROM orders",
    q=SQ("What comes back?", "SELECT COUNT(email) AS n FROM customers",
         ["n\n3", "n\n5", "n\n2"], "COUNT(column) skips NULLs. Only 3 customers have an email. COUNT(*) would say 5.")),
 SS("SUM, AVG, MIN, MAX",
    "The other four aggregates work on one column. They also skip NULLs. Use <code>ROUND(x, 2)</code> to tidy decimals.",
    "SELECT SUM(amount) AS total, MIN(amount) AS smallest, MAX(amount) AS biggest, ROUND(AVG(amount), 2) AS average FROM orders",
    q=SQ("What comes back?", "SELECT MAX(salary) AS top FROM employees WHERE dept = 'Sales'",
         ["top\n90000", "top\n60000", "top\n120000"], "WHERE runs first and keeps only Sales. Then MAX takes the biggest of what is left.")),
 SS("GROUP BY: one answer per group",
    "<code>GROUP BY dept</code> makes one bucket per department and the aggregate is worked out inside each bucket. Without GROUP BY you get one answer for the whole table; with it you get one per group.",
    "SELECT dept, COUNT(*) AS people FROM employees GROUP BY dept",
    q=SQ("What comes back?", "SELECT city, COUNT(*) AS n FROM customers GROUP BY city ORDER BY city",
         ["city | n\nDelhi | 1\nHyderabad | 2\nPune | 2", "city | n\nHyderabad | 5", "city | n\nDelhi | 1\nHyderabad | 1\nPune | 1"], "Two customers are in Hyderabad, two in Pune, one in Delhi.")),
 SS("The rule: every plain column must be grouped",
    "In a grouped query, each column in SELECT is either inside an aggregate (<code>SUM(...)</code>) or listed in GROUP BY. Otherwise the database does not know which row's value to show. Think of it as: the column before the aggregate is how you cut the table.",
    "SELECT dept, SUM(salary) AS payroll FROM employees GROUP BY dept ORDER BY payroll DESC",
    q=QC("You want total salary per department <i>and</i> the person's name. Why is <code>SELECT dept, name, SUM(salary) FROM employees GROUP BY dept</code> wrong?",
         ["name is neither grouped nor aggregated, so one department has many names and the query cannot pick one", "SUM cannot be used with dept", "GROUP BY must list every column in the table"], 0,
         "Each group has several names. Show a per-person detail and a per-group total in separate queries, or use a window function (Day 11).")),
 SS("HAVING filters groups",
    "<code>WHERE</code> filters rows <i>before</i> grouping. <code>HAVING</code> filters groups <i>after</i> they are built, so it can use aggregates. Run it, then change 100 to 300.",
    "SELECT customer_id, SUM(amount) AS total FROM orders GROUP BY customer_id HAVING SUM(amount) > 100 ORDER BY customer_id",
    q=SQ("What comes back?", "SELECT customer_id, SUM(amount) AS total FROM orders GROUP BY customer_id HAVING SUM(amount) > 100 ORDER BY customer_id",
         ["customer_id | total\n1 | 255.5\n3 | 320", "customer_id | total\n1 | 255.5\n2 | 40\n3 | 320\n5 | 75", "customer_id | total\n3 | 320"], "Customer 1: 120+80+55.5 = 255.5. Customer 3: 300+20 = 320. Customers 2 and 5 total under 100.")),
 SS("WHERE or HAVING?",
    "A quick test: if the condition is about a single row (<code>salary &gt; 50000</code>), use WHERE. If it is about a group's aggregate (<code>COUNT(*) &gt; 2</code>), use HAVING. You can use both in one query: WHERE trims rows, GROUP BY builds groups, HAVING trims groups.",
    "SELECT dept, COUNT(*) AS people FROM employees WHERE salary > 50000 GROUP BY dept HAVING COUNT(*) >= 2",
    q=QC("Which keeps only departments with more than 3 people?",
         ["GROUP BY dept HAVING COUNT(*) > 3", "WHERE COUNT(*) > 3 GROUP BY dept", "GROUP BY dept WHERE COUNT(*) > 3"], 0,
         "The count only exists after grouping, so it must be tested in HAVING.")),
 SS("Aggregates and NULL",
    "AVG, SUM, MIN and MAX ignore NULLs. That can change an average: Nina's missing salary is not counted as 0, she is simply left out. Run this and notice the answer is 40000, not 20000.",
    "SELECT AVG(salary) AS avg_salary, COUNT(*) AS rows_in_group, COUNT(salary) AS with_salary FROM employees WHERE dept = 'Support'",
    q=SQ("What comes back?", "SELECT COUNT(*) AS a, COUNT(salary) AS b FROM employees WHERE dept = 'Support'",
         ["a | b\n2 | 1", "a | b\n2 | 2", "a | b\n1 | 1"], "Two rows (Tom, Nina), but only one has a salary.")),
 SS("Your turn: grouped report",
    "Put it together: group, aggregate, then filter the groups.",
    "SELECT customer_id FROM orders",
    q=SW("For each <code>customer_id</code> in <code>orders</code> who has placed <b>more than one</b> order, show <code>customer_id</code> and the sum of their amounts as <code>total</code>.",
         "SELECT \nFROM orders\n",
         "SELECT customer_id, SUM(amount) AS total FROM orders GROUP BY customer_id HAVING COUNT(*) > 1",
         "Group by customer_id, then HAVING COUNT(*) > 1. SUM(amount) AS total gives the second column.")),
]

LESSONS[10] = [
 SS("Data lives in separate tables",
    "Customers are stored once in <code>customers</code>. Orders point to them with <code>customer_id</code>. That avoids copying names everywhere. To see names next to amounts you <b>join</b> the tables. First look at the raw orders: the number in customer_id is the customer's id.",
    "SELECT * FROM orders",
    q=QC("What does <code>customer_id = 3</code> in an order row mean?", ["That order belongs to the customer whose id is 3", "The order has 3 items", "The order is the third one"], 0, "customer_id is a link (a foreign key) to customers.id.")),
 SS("JOIN ... ON matches rows",
    "<code>JOIN customers c ON o.customer_id = c.id</code> means: for each order, find the customer row whose id equals that order's customer_id, and put them side by side. <code>o</code> and <code>c</code> are short names for the tables.",
    "SELECT c.name, o.amount FROM orders o JOIN customers c ON o.customer_id = c.id",
    q=SQ("What comes back?", "SELECT c.name FROM customers c JOIN orders o ON o.customer_id = c.id WHERE o.amount > 100 ORDER BY c.name",
         ["name\nAcme\nCora", "name\nAcme\nAcme\nCora", "name\nCora"], "Order 1 (Acme, 120) and order 4 (Cora, 300) are over 100.")),
 SS("Plain JOIN drops unmatched rows",
    "A plain JOIN (inner join) keeps only rows that match on both sides. Dune has no orders, so Dune vanishes from the result. Run it and look: no Dune.",
    "SELECT c.name, o.amount FROM customers c JOIN orders o ON o.customer_id = c.id ORDER BY c.name, o.amount",
    q=QC("Which customers disappear from a plain JOIN of customers and orders?", ["Customers with no orders", "Orders with no customer is always empty", "Customers with more than one order"], 0, "Inner join needs a match. No match, no row.")),
 SS("LEFT JOIN keeps everything on the left",
    "<code>LEFT JOIN</code> keeps every row from the left table. Where there is no match, the right-side columns come back as <b>NULL</b>. Use it when 'also show the ones with nothing' matters.",
    "SELECT c.name, o.amount FROM customers c LEFT JOIN orders o ON o.customer_id = c.id ORDER BY c.name, o.amount",
    q=SQ("What comes back?", "SELECT c.name, o.amount FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE c.id = 4",
         ["name | amount\nDune | NULL", "name | amount\nDune | 0", "name | amount"], "Dune has no orders, so amount is NULL, not 0.")),
 SS("Find what is missing",
    "A classic question: who has <i>no</i> orders? LEFT JOIN, then keep the rows where the right side is NULL.",
    "SELECT c.name FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE o.id IS NULL",
    q=SQ("What comes back?", "SELECT c.name FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE o.id IS NULL",
         ["name\nDune", "name\nBolt\nDune", "name\nAcme\nBolt\nCora\nEcho"], "Only Dune has no matching order. Bolt has one.")),
 SS("Join, then group",
    "Joining multiplies rows (one per order), and then GROUP BY collapses them again. Count a column from the right-hand table, not <code>*</code>, otherwise a customer with no orders still counts as 1 (their own single row).",
    "SELECT c.name, COUNT(o.id) AS orders FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.name ORDER BY c.name",
    q=SQ("What comes back?", "SELECT COUNT(o.id) AS n FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE c.id = 4",
         ["n\n0", "n\n1", "n\nNULL"], "COUNT(o.id) skips NULL, and Dune's o.id is NULL. COUNT(*) would have said 1.")),
 SS("A table joined to itself",
    "Employees have a <code>manager_id</code> that points to another employee. Join the table to itself under two different names to put each person next to their manager.",
    "SELECT e.name AS employee, m.name AS manager FROM employees e JOIN employees m ON e.manager_id = m.id ORDER BY e.id",
    q=SQ("What comes back?", "SELECT e.name AS employee, m.name AS manager FROM employees e JOIN employees m ON e.manager_id = m.id WHERE e.name = 'Sara'",
         ["employee | manager\nSara | Karan", "employee | manager\nKaran | Sara", "employee | manager\nSara | Priya"], "Sara's manager_id is 6, and employee 6 is Karan.")),
 SS("COALESCE: replace NULL",
    "<code>COALESCE(x, 0)</code> gives x, or 0 if x is NULL. It is how you turn 'no orders' into a clean 0 in a report.",
    "SELECT c.name, COALESCE(SUM(o.amount), 0) AS total FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.name ORDER BY c.name",
    q=SQ("What comes back?", "SELECT COALESCE(email, 'none') AS contact FROM customers WHERE id = 4",
         ["contact\nnone", "contact\nNULL", "contact\n"], "Dune's email is NULL, so COALESCE returns the second value.")),
 SS("Your turn: join, group, fill the gaps",
    "Every customer should appear, even with no orders.",
    "SELECT name FROM customers",
    q=SW("Show every customer's <code>name</code> and the total of their order amounts as <code>total</code> (use 0 if they have no orders). Sort by name A to Z.",
         "SELECT \nFROM customers c\n",
         "SELECT c.name, COALESCE(SUM(o.amount), 0) AS total FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.name ORDER BY c.name",
         "LEFT JOIN orders so customers without orders stay, SUM(o.amount) per customer, COALESCE(..., 0) for the gaps, ORDER BY c.name.", ordered=True)),
]

LESSONS[11] = [
 SS("A CTE gives a step a name",
    "<code>WITH totals AS (...)</code> runs a query and lets the next query use its result as if it were a table. Read it top to bottom: first build <code>totals</code>, then query it. It is the same as nesting, but readable.",
    "WITH totals AS (\n  SELECT customer_id, SUM(amount) AS total\n  FROM orders GROUP BY customer_id\n)\nSELECT * FROM totals WHERE total > 100 ORDER BY customer_id",
    q=SQ("What comes back?", "WITH totals AS (SELECT customer_id, SUM(amount) AS total FROM orders GROUP BY customer_id)\nSELECT customer_id FROM totals WHERE total < 100 ORDER BY customer_id",
         ["customer_id\n2\n5", "customer_id\n1\n3", "customer_id\n2"], "Customer 2 totals 40 and customer 5 totals 75. Customers 1 and 3 are over 100.")),
 SS("Use the CTE in a join",
    "Because the CTE is a named result, you can join it to other tables. Here: add the customer's name to each total.",
    "WITH totals AS (\n  SELECT customer_id, SUM(amount) AS total\n  FROM orders GROUP BY customer_id\n)\nSELECT c.name, t.total FROM totals t JOIN customers c ON c.id = t.customer_id ORDER BY t.total DESC",
    q=SQ("What comes back?", "WITH totals AS (SELECT customer_id, SUM(amount) AS total FROM orders GROUP BY customer_id)\nSELECT c.name, t.total FROM totals t JOIN customers c ON c.id = t.customer_id ORDER BY t.total DESC LIMIT 1",
         ["name | total\nCora | 320", "name | total\nAcme | 255.5", "name | total\nCora | 300"], "Cora's orders: 300 + 20 = 320, the biggest total.")),
 SS("Window functions: keep the rows, add a calculation",
    "GROUP BY collapses rows. A <b>window function</b> keeps every row and adds a column computed over a group of rows. <code>OVER (PARTITION BY dept)</code> means: do it separately for each department.",
    "SELECT name, dept, salary, MAX(salary) OVER (PARTITION BY dept) AS dept_top FROM employees ORDER BY dept, name",
    q=SQ("What comes back?", "SELECT name, COUNT(*) OVER (PARTITION BY dept) AS team FROM employees WHERE name IN ('Tom', 'Nina') ORDER BY name",
         ["name | team\nNina | 2\nTom | 2", "name | team\nNina | 1\nTom | 1", "name | team\nTom | 2"], "Both are in Support, a team of 2, and each row keeps its own line.")),
 SS("RANK: position inside a group",
    "<code>RANK() OVER (PARTITION BY dept ORDER BY salary DESC)</code> numbers people from highest salary down inside each department. Ties get the same rank and the next rank is skipped. <code>ROW_NUMBER()</code> never ties.",
    "SELECT name, dept, salary, RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk FROM employees ORDER BY dept, rnk, name",
    q=SQ("What comes back?", "WITH r AS (SELECT name, RANK() OVER (ORDER BY salary DESC) AS rnk FROM employees WHERE dept = 'Engineering')\nSELECT name, rnk FROM r ORDER BY rnk, name",
         ["name | rnk\nPriya | 1\nKaran | 2\nLi | 2\nSara | 4", "name | rnk\nPriya | 1\nKaran | 2\nLi | 3\nSara | 4", "name | rnk\nPriya | 1\nKaran | 2\nLi | 2\nSara | 3"], "Karan and Li tie for second. RANK gives both 2 and skips 3, so Sara is 4. DENSE_RANK would give Sara 3.")),
 SS("The top-N-per-group pattern",
    "You cannot put a window function in WHERE. So: compute the number in a CTE, then filter in the next query. This 'best one per group' shape appears in a large share of SQL interviews.",
    "WITH ranked AS (\n  SELECT name, dept, salary,\n         ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn\n  FROM employees\n)\nSELECT dept, name, salary FROM ranked WHERE rn = 1 ORDER BY dept",
    q=SQ("What comes back?", "WITH ranked AS (SELECT name, dept, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn FROM employees)\nSELECT dept, name FROM ranked WHERE rn = 1 ORDER BY dept",
         ["dept | name\nEngineering | Priya\nSales | Asha\nSupport | Tom", "dept | name\nEngineering | Priya\nSales | Asha\nSupport | Nina", "dept | name\nEngineering | Sara\nSales | John\nSupport | Tom"], "Each department's rn = 1 is its highest salary. In SQLite NULL sorts last in DESC, so Tom (40000) beats Nina (NULL).")),
 SS("Running totals and the row before",
    "Add <code>ORDER BY</code> inside OVER to make the calculation walk down the rows. <code>SUM(x) OVER (ORDER BY d)</code> is a running total. <code>LAG(x)</code> is the previous row's value (NULL for the first).",
    "SELECT order_date, amount, SUM(amount) OVER (ORDER BY order_date) AS running, LAG(amount) OVER (ORDER BY order_date) AS prev FROM orders WHERE customer_id = 1",
    q=SQ("What comes back?", "SELECT amount, LAG(amount) OVER (ORDER BY order_date) AS prev FROM orders WHERE customer_id = 1 ORDER BY order_date",
         ["amount | prev\n120 | NULL\n80 | 120\n55.5 | 80", "amount | prev\n120 | 80\n80 | 55.5\n55.5 | NULL", "amount | prev\n120 | 0\n80 | 120\n55.5 | 80"], "Each row looks one row back in date order. The first has nothing before it, so NULL.")),
 SS("Order of work inside a query",
    "SQL runs in this order, not the order you write it: FROM and JOIN, then WHERE, then GROUP BY, then HAVING, then window functions, then SELECT, ORDER BY and LIMIT. That is why WHERE cannot see an alias or a window result, and why a window function only sees rows that survived WHERE.",
    "SELECT name, COUNT(*) OVER (PARTITION BY dept) AS team FROM employees WHERE name = 'Tom'",
    q=SQ("Tom's team is Support (Tom and Nina). What comes back?", "SELECT name, COUNT(*) OVER (PARTITION BY dept) AS team FROM employees WHERE name = 'Tom'",
         ["name | team\nTom | 1", "name | team\nTom | 2", "name | team\nTom | NULL"], "WHERE runs before the window, so Nina is already gone and only one row is counted. Use a CTE if you need the full team first.")),
 SS("Your turn: window function",
    "Keep every order and add the customer's total next to it.",
    "SELECT id FROM orders",
    q=SW("Show <code>id</code>, <code>amount</code>, and <code>customer_total</code> (the sum of all amounts for that order's customer) for every row in <code>orders</code>. Sort by <code>id</code>.",
         "SELECT \nFROM orders\n",
         "SELECT id, amount, SUM(amount) OVER (PARTITION BY customer_id) AS customer_total FROM orders ORDER BY id",
         "SUM(amount) OVER (PARTITION BY customer_id) keeps every row. Do not use GROUP BY here.", ordered=True)),
]
