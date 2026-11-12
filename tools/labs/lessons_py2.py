# Lessons for Days 12-14 (pandas, PySpark, data pipeline + Week 2 review). Exec'd inside lessons.py.
# pandas and PySpark output can differ between CPython and the browser, so every shown output and every answer
# here is computed by running the code through the same harness the browser uses (see _hout).
import json as _pj, sys as _psys
try:
    import harness as _harness
except ImportError:
    _psys.path.insert(0, _HERE)
    import harness as _harness
try:
    import pandas as _pandas_pre          # load once so tracing the learner's import is cheap
    import pyspark.sql                    # noqa
except ImportError:
    _psys.path.insert(0, _os.path.join(_HERE, "sparklite"))
    import pandas as _pandas_pre
    import pyspark.sql                    # noqa


def _hrun(code, prelude="", stdin=None):
    return _pj.loads(_harness._run(_pj.dumps(dict(code=code, prelude=prelude, tests=[dict(label="run", out="", stdin=stdin or [])], files={}, limit=300000))))[0]

def _hout(code, prelude=""):
    r = _hrun(code, prelude)
    assert not r.get("error"), (r.get("error"), code)
    return r["got"]

def Sh(h, t, code=None, run=False, q=None):
    """Like S, but the example is checked by the browser harness (pandas / PySpark)."""
    d = dict(h=h, t=t)
    if code is not None:
        d["code"] = code
        _hout(code)
    if run:
        d["run"] = True
    if q:
        d["q"] = q
    return d

def Qh(prompt, code, options, why):
    got = _hout(code)
    assert options.count(got) == 1, ("answer not among options exactly once", prompt, got, options)
    return dict(k="mc", q=prompt, code=code, o=options, a=options.index(got), why=why)

def QEh(prompt, code, error, options, a, why):
    r = _hrun(code)
    assert r.get("error") and r["error"].strip().splitlines()[-1].startswith(error), (prompt, r.get("error"), r.get("got"))
    return dict(k="mc", q=prompt, code=code, o=options, a=a, why=why)

def Wh(task, starter, sol, exprs, prelude, hint=""):
    """Write task for pandas / PySpark. Expected values come from running the solution on the real libraries."""
    def _raises(fn, exc=Exception):
        try:
            fn()
        except exc:
            return True
        return False
    ns = {"_raises": _raises}
    exec(prelude + "\n" + sol, ns)
    tests = [dict(label=label, expr=expr, want=repr(eval(expr, ns))) for label, expr in exprs]
    return dict(k="write", task=task, starter=starter, sol=sol, tests=tests, hint=hint, prelude=prelude)


_PD_EMP = ("import pandas as pd\n"
 "EMP = pd.DataFrame({'name': ['Asha', 'Ravi', 'Meera', 'John', 'Priya', 'Karan', 'Sara', 'Tom', 'Nina'],\n"
 "                    'dept': ['Sales', 'Sales', 'Sales', 'Sales', 'Eng', 'Eng', 'Eng', 'Support', 'Support'],\n"
 "                    'salary': [90000, 60000, 60000, 45000, 120000, 95000, 80000, 40000, None]})\n"
 "EMP2 = pd.DataFrame({'name': ['Zed', 'Amy', 'Bob', 'Cat'], 'dept': ['Ops', 'Ops', 'Dev', 'Dev'], 'salary': [30000, 70000, 100000, 55000]})\n")

# ------------------------------------------------------------------ Day 12
LESSONS[12] = [
 Sh("pandas: tables in Python",
   "<b>pandas</b> is the Python library for tables. You load it with <code>import pandas as pd</code> (<code>pd</code> is just a short nickname). It has two main things. A <b>Series</b> is one column of values. A <b>DataFrame</b> is a whole table, made of Series side by side. The easy way to make a DataFrame is from a <b>dict</b>: each key becomes a column name and each list becomes that column's values.",
   "import pandas as pd\n\nemp = pd.DataFrame({\n    'name': ['Asha', 'Ravi', 'Meera', 'John'],\n    'dept': ['Sales', 'Sales', 'Sales', 'Sales'],\n    'salary': [90000, 60000, 60000, 45000],\n})\nprint(emp.to_string())\nprint(emp.shape)", run=True,
   q=Qh("<code>shape</code> is (rows, columns). What does this show?", "import pandas as pd\ndf = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})\nprint(df.shape)", ["(3, 2)", "(2, 3)", "6"], "There are 3 values in each list, so 3 rows, and 2 keys, so 2 columns. shape is always (rows, columns).")),
 Sh("Selecting columns",
   "Square brackets pick columns. <code>emp['salary']</code> (one name) gives a <b>Series</b>. <code>emp[['name', 'salary']]</code> (a list of names, so double brackets) gives a smaller <b>DataFrame</b>. A Series has handy methods: <code>.sum()</code>, <code>.mean()</code>, <code>.max()</code>. Names must match exactly, capital letters included.",
   "import pandas as pd\nemp = pd.DataFrame({'name': ['Asha', 'Ravi', 'Meera'], 'salary': [90000, 60000, 60000]})\nprint(emp['salary'].sum())\nprint(emp[['name', 'salary']].to_string())", run=True,
   q=QEh("What happens here?", "import pandas as pd\nemp = pd.DataFrame({'name': ['Asha'], 'salary': [90000]})\nprint(emp['Salary'])", "KeyError", ["It prints 90000", "A KeyError: there is no column called Salary (capital S)", "It prints an empty table"], 1, "The column is called salary with a small s. A wrong column name is a KeyError, and the message names the missing key.")),
 Sh("Filtering rows with a boolean mask",
   "To keep only some rows, first ask a True/False question about a column: <code>emp['salary'] &gt; 50000</code> gives one True or False <b>per row</b>. That list is called a <b>mask</b>. Put the mask inside square brackets and only the rows marked True are kept: <code>emp[mask]</code>.",
   "import pandas as pd\nemp = pd.DataFrame({'name': ['Asha', 'Ravi', 'John'], 'salary': [90000, 60000, 45000]})\nmask = emp['salary'] > 50000\nprint(mask.tolist())\nprint(emp[mask].to_string())", run=True,
   q=Qh("How many rows does this keep?", "import pandas as pd\ndf = pd.DataFrame({'n': [5, 12, 8, 20]})\nprint(len(df[df['n'] > 7]))", ["3", "2", "4"], "12, 8 and 20 are above 7. len() counts the rows that remain.")),
 Sh("Two conditions: & and |, with parentheses",
   "To combine questions on columns, use <code>&amp;</code> for <b>and</b> and <code>|</code> for <b>or</b>. Do <b>not</b> use the words <code>and</code>/<code>or</code>: they cannot handle a whole column. Also put <b>each</b> question in its own parentheses, because <code>&amp;</code> is worked out before <code>&gt;</code>. Use <code>~</code> for <b>not</b>.",
   "import pandas as pd\nemp = pd.DataFrame({'name': ['Asha', 'Ravi', 'Priya', 'Tom'], 'dept': ['Sales', 'Sales', 'Eng', 'Support'], 'salary': [90000, 60000, 120000, 40000]})\nbig_sales = emp[(emp['dept'] == 'Sales') & (emp['salary'] > 70000)]\nprint(big_sales['name'].tolist())\nother = emp[(emp['dept'] == 'Eng') | (emp['salary'] < 50000)]\nprint(other['name'].tolist())", run=True,
   q=QEh("What happens here?", "import pandas as pd\ndf = pd.DataFrame({'a': [1, 2, 3]})\nprint(df[(df['a'] > 1) and (df['a'] < 3)])", "ValueError", ["It prints the row where a is 2", "A ValueError: the truth value of a Series is ambiguous", "It prints all three rows"], 1, "The word and wants one True/False, but each side is a whole column. Use & between the two parenthesised questions.")),
 Sh("Sorting: sort_values",
   "<code>df.sort_values('salary')</code> sorts small to large. Add <code>ascending=False</code> for large to small. To break ties, give a <b>list</b> of columns. Sorting returns a <b>new</b> table; the original is not changed unless you save the result.",
   "import pandas as pd\nemp = pd.DataFrame({'name': ['Asha', 'Ravi', 'Meera', 'John'], 'salary': [90000, 60000, 60000, 45000]})\nout = emp.sort_values(['salary', 'name'], ascending=[False, True])\nprint(out['name'].tolist())", run=True,
   q=Qh("What does this show?", "import pandas as pd\ndf = pd.DataFrame({'n': ['b', 'c', 'a'], 'v': [2, 3, 1]})\nprint(df.sort_values('v', ascending=False)['n'].tolist())", ["['c', 'b', 'a']", "['a', 'b', 'c']", "['a', 'c', 'b']"], "v from large to small is 3, 2, 1, which belong to c, b, a.")),
 Sh("groupby + agg: totals per group",
   "<code>groupby('dept')</code> splits the rows into one pile per department. <code>.agg(...)</code> then calculates one number per pile. The clear way to write it is <b>named aggregation</b>: <code>new_name=('column', 'function')</code>. The result has the group names as its <b>index</b> (row labels). <code>.reset_index()</code> turns them back into a normal column, which is almost always what you want.",
   "import pandas as pd\nemp = pd.DataFrame({'dept': ['Sales', 'Sales', 'Eng', 'Eng', 'Eng'], 'salary': [90000, 60000, 120000, 95000, 80000]})\nout = emp.groupby('dept').agg(people=('salary', 'count'), avg_salary=('salary', 'mean')).reset_index()\nprint(out.to_string())", run=True,
   q=Qh("What does this show?", "import pandas as pd\ndf = pd.DataFrame({'g': ['x', 'y', 'x'], 'v': [1, 5, 2]})\nprint(df.groupby('g').agg(total=('v', 'sum')).reset_index().values.tolist())", ["[['x', 3], ['y', 5]]", "[['x', 1], ['y', 5]]", "[['x', 8]]"], "The x pile holds 1 and 2, so its total is 3. The y pile holds only 5. Groups come out in alphabetical order.")),
 Sh("merge: join two tables",
   "<code>left.merge(right, on='key')</code> glues two tables together side by side, matching rows that have the same value in the <b>key</b> column. This is the same idea as SQL JOIN. By default only matching rows are kept (<code>how='inner'</code>). With <code>how='left'</code> every row of the left table is kept, and unmatched ones get <b>NaN</b> (pandas' word for missing).",
   "import pandas as pd\norders = pd.DataFrame({'id': [1, 2, 3], 'customer_id': [101, 102, 999], 'amount': [50.0, 20.0, 15.0]})\ncustomers = pd.DataFrame({'customer_id': [101, 102], 'city': ['Pune', 'Delhi']})\nprint(orders.merge(customers, on='customer_id').to_string())\nprint(len(orders.merge(customers, on='customer_id', how='left')))", run=True,
   q=Qh("What does this show?", "import pandas as pd\na = pd.DataFrame({'k': [1, 2, 3], 'x': ['p', 'q', 'r']})\nb = pd.DataFrame({'k': [2, 3, 4], 'y': ['u', 'v', 'w']})\nprint(len(a.merge(b, on='k')))", ["2", "3", "4"], "Only k = 2 and k = 3 exist in both tables. The default merge is inner, so only those two rows remain.")),
 Sh("Missing values and value_counts",
   "Real data has gaps. pandas shows a gap as <b>NaN</b> (\"not a number\"). <code>s.isna()</code> marks the gaps with True. <code>df.dropna()</code> throws away rows that have a gap. <code>s.fillna(0)</code> replaces gaps with a value you choose. Which one is right depends on the question: dropping loses rows, filling invents numbers. Note that <code>.mean()</code> quietly <b>skips</b> NaN. Last tool: <code>df['city'].value_counts()</code> counts how often each value appears, biggest first; add <code>.reset_index()</code> to make it a table. It is the fastest way to explore a new column.",
   "import pandas as pd\ndf = pd.DataFrame({'name': ['Asha', 'Nina', 'Tom'], 'salary': [90000, None, 40000]})\nprint(df['salary'].isna().tolist())\nprint(df['salary'].mean())\nprint(df['salary'].fillna(0).mean())\nprint(len(df.dropna()))\nprint(pd.Series(['Pune', 'Delhi', 'Pune']).value_counts().to_dict())", run=True,
   q=Qh("What does this show?", "import pandas as pd\ns = pd.Series([10, None, 20, None])\nprint(s.isna().sum())", ["2", "4", "30"], "isna() gives True for the two gaps. sum() on True/False counts the Trues, so it counts the gaps.")),
 Sh("Your turn: average salary per department",
   "No example this time. You have all the pieces: filter with a mask, <code>groupby</code>, named <code>agg</code>, <code>reset_index</code> and <code>sort_values</code>. Predict what the answer should look like before you press Check.",
   q=Wh("Write <code>avg_by_dept(df)</code>. <code>df</code> has columns <code>name</code>, <code>dept</code>, <code>salary</code>. Ignore people earning under 50000. Return a DataFrame with the columns <code>dept</code> and <code>avg_salary</code> (the average salary of that department), highest average first. (<code>pd</code> is already imported.)",
       "def avg_by_dept(df):\n    # 1. keep rows with salary of at least 50000\n    # 2. group by dept and take the mean salary as avg_salary\n    # 3. reset_index, then sort highest first\n    return df\n",
       "def avg_by_dept(df):\n    big = df[df['salary'] >= 50000]\n    out = big.groupby('dept').agg(avg_salary=('salary', 'mean')).reset_index()\n    return out.sort_values('avg_salary', ascending=False)\n",
       [("the columns", "list(avg_by_dept(EMP).columns)"), ("the table", "avg_by_dept(EMP).values.tolist()"), ("other data", "avg_by_dept(EMP2).values.tolist()")],
       _PD_EMP, "Mask first, then df.groupby('dept').agg(avg_salary=('salary', 'mean')).reset_index(), then sort_values('avg_salary', ascending=False).")),
]

# ------------------------------------------------------------------ Day 13
_SPD = ("from pyspark.sql import SparkSession, functions as F\n"
 "spark = SparkSession.builder.appName('lab').getOrCreate()\n")
_SPW = (_SPD +
 "SALES = spark.createDataFrame([(1, ' north ', 'pen', 10, 2.5), (2, 'South', 'book', 2, 12.0), (3, 'north', 'book', 5, 12.0), (4, 'EAST', 'pen', 20, 2.5), (5, 'south', 'bag', 1, 30.0), (6, 'North', 'bag', 3, 30.0)], ['id', 'region', 'product', 'qty', 'price'])\n"
 "SALES2 = spark.createDataFrame([(1, 'a', 4, 10.0), (2, 'b', 1, 5.0), (3, 'a', 2, 7.5), (4, 'c', 1, 1.0)], ['id', 'region', 'qty', 'price'])\n"
 "def rows(df):\n    return [tuple(r) for r in df.collect()]\n")

LESSONS[13] = [
 Sd("What Spark is, and why it exists",
   "pandas keeps the whole table in the memory of <b>one</b> computer. What if the data is 500 GB? <b>Apache Spark</b> splits the data into pieces called <b>partitions</b> and spreads them over many computers (a <b>cluster</b>). Each computer works on its piece at the same time, and Spark joins the answers. That is called <b>distributed</b> computing.<br><br>The big idea: you write almost the same code for 10 rows or 10 billion rows. <b>PySpark</b> is Spark used from Python. On this course PySpark runs on a small practice engine inside your browser, with the same method names as the real thing.",
   q=QC("When is Spark the right tool instead of pandas?", ["The data is too big for one computer's memory", "You want to read a very small CSV", "You need to print text"], 0, "Spark is for data that is too big or too slow for one machine. For small data pandas is simpler and faster.")),
 Sh("Start a SparkSession and make a DataFrame",
   "Everything in Spark starts from a <b>SparkSession</b>, the connection to Spark. The line with <code>builder...getOrCreate()</code> is the usual opening spell; learn it as one piece. Then <code>spark.createDataFrame(rows, column_names)</code> builds a table from a list of tuples. <code>df.show()</code> prints it (the practice engine draws a simplified table; real Spark's looks similar). <code>df.columns</code> lists the column names and <code>df.count()</code> counts rows.",
   "from pyspark.sql import SparkSession, functions as F\n\nspark = SparkSession.builder.appName('lesson').getOrCreate()\ndf = spark.createDataFrame([(1, 'Asha', 90000), (2, 'Ravi', 60000), (3, 'John', 45000)], ['id', 'name', 'salary'])\nprint(df.columns)\nprint(df.count())", run=True,
   q=Qh("What does this show?", _SPD + "df = spark.createDataFrame([(1, 'a'), (2, 'b'), (3, 'c'), (4, 'd')], ['id', 'letter'])\nprint(df.count())", ["4", "2", "['id', 'letter']"], "count() returns how many rows the table has. There are four tuples, so four rows.")),
 Sh("select, filter and withColumn",
   "Three moves do most of the work. <code>df.select('a', 'b')</code> keeps columns. <code>df.filter(F.col('x') &gt; 5)</code> keeps rows; <code>F.col('x')</code> means \"the column called x\". <code>df.withColumn('new', expression)</code> adds a column (or replaces one with the same name). <code>F</code> is the nickname for <code>pyspark.sql.functions</code>, the toolbox of column helpers like <code>F.upper</code>. Every call returns a <b>new</b> DataFrame, so you can chain them with dots. Several tests need <code>&amp;</code>, <code>|</code> and parentheses, just like pandas.",
   _SPD + "df = spark.createDataFrame([(1, 'Asha', 90000), (2, 'Ravi', 60000), (3, 'John', 45000)], ['id', 'name', 'salary'])\nout = (df.filter(F.col('salary') > 50000)\n         .withColumn('bonus', F.col('salary') * 0.1)\n         .select('name', 'bonus'))\nprint(out.collect())", run=True,
   q=Qh("What does this show?", _SPD + "df = spark.createDataFrame([('a', 5), ('b', 15), ('c', 25)], ['k', 'v'])\nout = df.filter(F.col('v') > 10).withColumn('double', F.col('v') * 2)\nprint([r['double'] for r in out.collect()])", ["[30, 50]", "[10, 30, 50]", "[15, 25]"], "The filter keeps b (15) and c (25). Then double = v * 2 gives 30 and 50.")),
 Sh("groupBy + agg",
   "<code>groupBy('region')</code> makes one group per region. <code>.agg(...)</code> then computes one number per group using functions such as <code>F.sum</code>, <code>F.count</code>, <code>F.avg</code>, <code>F.max</code>. Always add <code>.alias('name')</code> to give the new column a clean name. <code>orderBy(F.col('x').desc())</code> sorts high to low.",
   _SPD + "df = spark.createDataFrame([('north', 10), ('south', 5), ('north', 7), ('south', 1), ('east', 4)], ['region', 'qty'])\nout = (df.groupBy('region')\n         .agg(F.sum('qty').alias('total'), F.count('*').alias('n'))\n         .orderBy(F.col('total').desc()))\nprint([tuple(r) for r in out.collect()])", run=True,
   q=Qh("What does this show?", _SPD + "df = spark.createDataFrame([('a', 1), ('b', 2), ('a', 3)], ['k', 'v'])\nout = df.groupBy('k').agg(F.sum('v').alias('s')).orderBy('k')\nprint([tuple(r) for r in out.collect()])", ["[('a', 4), ('b', 2)]", "[('a', 1), ('b', 2), ('a', 3)]", "[('a', 2), ('b', 2)]"], "Group a holds 1 and 3, whose sum is 4. Group b holds only 2.")),
 Sh("Lazy evaluation: transformations plan, actions run",
   "Here is Spark's most important habit. <code>select</code>, <code>filter</code>, <code>withColumn</code>, <code>groupBy</code> and <code>join</code> are <b>transformations</b>: they only write a plan and do <b>no work yet</b>. This is called <b>lazy evaluation</b>. Work happens only at an <b>action</b>: <code>show()</code> prints a few rows, <code>collect()</code> brings <b>all</b> rows back to Python as a list of Row objects, <code>count()</code> counts rows. Why wait? Spark can look at the whole plan and choose the cheapest way. Careful: <code>collect()</code> on a huge table can crash your program, so use <code>show()</code> or <code>limit(n)</code> to peek.",
   _SPD + "df = spark.createDataFrame([(1, 'Asha'), (2, 'Ravi')], ['id', 'name'])\nplan = df.filter(F.col('id') > 1)      # nothing runs yet\nrows = plan.collect()                  # this is the action\nprint(rows)\nprint(rows[0]['name'])", run=True,
   q=QC("Which line makes Spark actually start computing?", ["<code>df2 = df.filter(F.col('x') &gt; 1)</code>", "<code>df3 = df2.withColumn('y', F.col('x') * 2)</code>", "<code>n = df3.count()</code>"], 2, "filter and withColumn only build the plan. count() is an action, so that is where Spark does the work.")),
 Sh("Joining two DataFrames",
   "<code>left.join(right, on='customer_id', how='inner')</code> matches rows on a shared column, like SQL JOIN and pandas merge. <code>how</code> can be <code>'inner'</code> (only matches), <code>'left'</code> (keep all left rows), <code>'right'</code> or <code>'outer'</code>. In Spark joins are the expensive step, because rows with the same key have to be moved to the same computer. That moving is called a <b>shuffle</b>.",
   _SPD + "orders = spark.createDataFrame([(1, 101, 50.0), (2, 102, 20.0), (3, 999, 15.0)], ['id', 'customer_id', 'amount'])\ncustomers = spark.createDataFrame([(101, 'Pune'), (102, 'Delhi')], ['customer_id', 'city'])\nprint(orders.join(customers, on='customer_id', how='inner').count())\nprint(orders.join(customers, on='customer_id', how='left').count())", run=True,
   q=Qh("What does this show?", _SPD + "a = spark.createDataFrame([(1, 'x'), (2, 'y'), (3, 'z')], ['k', 'p'])\nb = spark.createDataFrame([(2, 'u'), (3, 'v'), (4, 'w')], ['k', 'q'])\nprint(a.join(b, on='k', how='left').count())", ["3", "2", "4"], "A left join keeps every row of a (3 rows), whether or not b has a match.")),
 Sd("Window functions (idea only)",
   "Sometimes you want a calculation <b>across related rows without collapsing them</b>, such as \"rank each employee inside their department\". groupBy would squash each department into one row. A <b>window</b> keeps every row and adds the answer beside it. You define the window (which rows belong together, in what order) and apply a function over it. <code>partitionBy</code> is like groupBy (the groups), <code>orderBy</code> sorts inside each group, and <code>row_number()</code> numbers the rows 1, 2, 3 in that order. The practice engine in your browser does not run windows, so here you only learn to read them. It is the SQL <code>ROW_NUMBER() OVER (PARTITION BY ...)</code> from Day 11.",
   "from pyspark.sql import Window\nw = Window.partitionBy('dept').orderBy(F.col('salary').desc())\nranked = df.withColumn('rank', F.row_number().over(w))",
   q=QC("A table has 10 employees in 3 departments. After <code>withColumn('rank', F.row_number().over(w))</code> with <code>partitionBy('dept')</code>, how many rows does it have?", ["10: a window adds a column and keeps every row", "3: one row per department", "1"], 0, "That is the difference from groupBy. A window never removes rows; it only adds a column.")),
 Sh("Common errors and how to read them",
   "Spark errors look scary but follow patterns. A <b>wrong column name</b> is the most common: real Spark says <code>AnalysisException: cannot resolve 'Salary'</code> and lists the real columns; the practice engine says <code>KeyError</code> and also lists them. Read that list, and fix capital letters. Another classic: using the word <code>and</code> between two column tests gives <code>ValueError: Cannot convert column into bool</code>. Use <code>&amp;</code> with each test in parentheses. Also remember a DataFrame is never changed in place: <code>df.withColumn(...)</code> on its own line does nothing unless you save the result.",
   _SPD + "df = spark.createDataFrame([(1, 'Asha', 90000)], ['id', 'name', 'salary'])\ntry:\n    df.select('Salary')\nexcept Exception as e:\n    print('failed: wrong column name')\nprint(df.columns)", run=True,
   q=QEh("What happens here?", _SPD + "df = spark.createDataFrame([(1, 5), (2, 9)], ['id', 'v'])\nout = df.filter((F.col('v') > 1) and (F.col('v') < 8))\nprint(out.count())", "ValueError", ["It prints 1", "A ValueError: you cannot use <code>and</code> between columns", "It prints 2"], 1, "Python's and needs one True/False. A Spark column is not one. Write (F.col('v') > 1) &amp; (F.col('v') < 8).")),
 Sh("Your turn: revenue per region",
   "A full small Spark job: filter, add a column, group, aggregate, sort. Plan the chain on paper first, then write it. <code>F</code> and <code>spark</code> are already set up for you.",
   q=Wh("Write <code>region_totals(df)</code>. <code>df</code> has columns <code>id</code>, <code>region</code>, <code>product</code>, <code>qty</code>, <code>price</code>. Keep rows with <code>qty</code> of at least 2, add a column <code>revenue</code> = <code>qty * price</code>, then return one row per <code>region</code> with columns <code>region</code> and <code>total</code> (the sum of revenue), biggest total first.",
       "def region_totals(df):\n    # 1. filter qty >= 2\n    # 2. withColumn revenue\n    # 3. groupBy region, agg sum as total\n    # 4. orderBy total, biggest first\n    return df\n",
       "def region_totals(df):\n    return (df.filter(F.col('qty') >= 2)\n              .withColumn('revenue', F.col('qty') * F.col('price'))\n              .groupBy('region')\n              .agg(F.sum('revenue').alias('total'))\n              .orderBy(F.col('total').desc()))\n",
       [("columns", "region_totals(SALES).columns"), ("the rows", "rows(region_totals(SALES))"), ("other data", "rows(region_totals(SALES2))")],
       _SPW, "df.filter(...).withColumn('revenue', ...).groupBy('region').agg(F.sum('revenue').alias('total')).orderBy(F.col('total').desc())")),
]

# ------------------------------------------------------------------ Day 14
_RAW = '"id,city,amount\\n1, Pune ,100\\n2,Delhi,50\\n2,Delhi,50\\n3,pune,\\n4,Delhi,25"'
_PIPE = ("import io\nimport pandas as pd\n\nRAW = " + _RAW + "\n\n"
 "def read(text):\n    return pd.read_csv(io.StringIO(text))\n\n"
 "def clean(df):\n    df = df.drop_duplicates()\n    df = df.dropna(subset=['amount'])\n    df = df.assign(city=df['city'].str.strip().str.title())\n    return df\n\n"
 "def summarise(df):\n    out = df.groupby('city').agg(total=('amount', 'sum')).reset_index()\n    return out.sort_values('city')\n\n")
_PIPE_PRE = ("import io\nimport pandas as pd\n"
 "RAW = " + _RAW + "\n"
 "RAW2 = \"id,city,amount\\n1,goa,10\\n2, Goa ,5\\n3,Pune,7\\n3,Pune,7\"\n"
 "EMPTY = \"id,city,amount\\n1,Pune,\\n2,Delhi,\"\n")

LESSONS[14] = [
 Sh("A pipeline: read, clean, transform, aggregate, write",
   "A <b>data pipeline</b> is a chain of steps that turns raw data into something useful: <b>read</b> it, <b>clean</b> it, <b>transform</b> it, <b>aggregate</b> it, then <b>write</b> the result somewhere. Real teams run the same pipeline every night. The trick that keeps it manageable: make <b>each step its own small function</b> that takes a DataFrame and returns a DataFrame. Then you can test each step alone. Here is the first step, <b>read</b>, on a messy file (we use text in place of a file so it runs anywhere).",
   "import io\nimport pandas as pd\n\nRAW = \"id,city,amount\\n1, Pune ,100\\n2,Delhi,50\\n2,Delhi,50\\n3,pune,\\n4,Delhi,25\"\n\ndef read(text):\n    return pd.read_csv(io.StringIO(text))\n\ndf = read(RAW)\nprint(df.shape)\nprint(df.to_string())", run=True,
   q=QC("Why write each pipeline step as a small function that takes a DataFrame and returns one?", ["You can test each step on its own and reuse it", "Python forbids code outside functions", "It makes the data smaller"], 0, "Small steps are easy to test, easy to read, and easy to swap. When something breaks you know which step to look at.")),
 Sh("The clean step",
   "Look at the raw data above. Problems: the city has stray spaces (<code>' Pune '</code>) and different capitals (<code>pune</code>); row 2 appears twice; row 3 has no amount. A clean step fixes these: <code>drop_duplicates()</code> removes repeated rows, <code>dropna(subset=['amount'])</code> drops rows where that one column is missing, and <code>.str.strip().str.title()</code> tidies text (<code>.str</code> lets a text method work on a whole column). <code>assign(city=...)</code> returns a copy with that column replaced.",
   _PIPE + "df = clean(read(RAW))\nprint(df.to_string())", run=True,
   q=Qh("What does this show?", "import pandas as pd\ndf = pd.DataFrame({'c': [' a', 'b ', ' a']})\nprint(df['c'].str.strip().drop_duplicates().tolist())", ["['a', 'b']", "['a', 'b', 'a']", "[' a', 'b ']"], "strip() removes the edge spaces, so the first and last become 'a'. Then drop_duplicates() keeps the first of each.")),
 Sh("Chain the steps together",
   "A <b>pipeline function</b> calls the steps in order. Because each step returns a DataFrame, the output of one is the input of the next: <code>summarise(clean(read(text)))</code>. Read it from the inside out. A top-level function like <code>run(text)</code> is the one place that shows the whole story.",
   _PIPE + "def run(text):\n    return summarise(clean(read(text)))\n\nprint(run(RAW).to_string())", run=True,
   q=Qh("The cleaned data has Pune 100, Delhi 50 and Delhi 25. What does this show?", _PIPE + "print(summarise(clean(read(RAW)))['total'].tolist())", ["[75.0, 100.0]", "[100.0, 75.0]", "[175.0]"], "The groups are sorted by city: Delhi (50 + 25 = 75) then Pune (100).")),
 Sh("Idempotency: safe to run twice",
   "A pipeline will be re-run: a retry after a crash, or someone presses the button twice. A step is <b>idempotent</b> if running it twice leaves the data exactly as running it once. Appending rows is <b>not</b> idempotent: run twice and you have duplicates. Writing by key is: <b>overwrite</b> the output, or <b>upsert</b> (update the row if its key exists, insert it if not). Below, a dict plays the part of a database table keyed by <code>id</code>.",
   "def load_append(table, rows):\n    table.extend(rows)\n\ndef load_upsert(table, rows):\n    for r in rows:\n        table[r['id']] = r\n\nbatch = [{'id': 1, 'v': 10}, {'id': 2, 'v': 20}]\nlog = []\nload_append(log, batch)\nload_append(log, batch)\nprint(len(log))\n\ndb = {}\nload_upsert(db, batch)\nload_upsert(db, batch)\nprint(len(db))", run=True,
   q=QC("A job loads yesterday's sales into a table. It crashes halfway and is re-run. Which design is safe?", ["Upsert by order id (or overwrite yesterday's partition)", "Append every row again", "Skip the re-run and hope"], 0, "A safe load gives the same table however many times it runs. Append duplicates the rows that already made it in.")),
 Sh("Validate the data before you trust it",
   "Pipelines fail quietly: no crash, just wrong numbers. So add <b>checks</b> that stop the job loudly. Write a <code>validate(df)</code> function that <b>raises</b> an error with a clear message when something is wrong: no rows left, negative amounts, missing columns. A loud failure at 2 a.m. is better than a wrong report at 9 a.m. <code>raise ValueError(\"message\")</code> stops the program and shows your message.",
   "import pandas as pd\n\ndef validate(df):\n    if len(df) == 0:\n        raise ValueError('no rows after cleaning')\n    if (df['amount'] < 0).any():\n        raise ValueError('negative amount found')\n    return df\n\nok = pd.DataFrame({'amount': [10, 20]})\nprint(len(validate(ok)))\ntry:\n    validate(pd.DataFrame({'amount': [10, -5]}))\nexcept ValueError as e:\n    print('stopped:', e)", run=True,
   q=QEh("What happens here?", "import pandas as pd\n\ndef validate(df):\n    if len(df) == 0:\n        raise ValueError('no rows after cleaning')\n    return df\n\nvalidate(pd.DataFrame({'amount': []}))", "ValueError", ["It returns the empty table quietly", "A ValueError with the message: no rows after cleaning", "A KeyError"], 1, "The table has zero rows, so the check raises a ValueError carrying our message. The pipeline stops instead of reporting nothing.")),
 Sh("Logging: leave a trail",
   "When a job runs unattended, nobody watches it. <b>Logging</b> writes notes about what happened, each with a <b>level</b>: <code>INFO</code> for normal progress, <code>WARNING</code> for something odd, <code>ERROR</code> for a failure. The next morning the log shows e.g. \"read 5 rows, dropped 2\". Unlike <code>print</code>, logs have levels, timestamps and can go to files. The first lines are set-up you copy; after that you call <code>log.info(...)</code>. Use <code>%d</code> / <code>%s</code> placeholders and pass the values after the message.",
   "import logging, sys\n\nlog = logging.getLogger('pipe')\nlog.handlers.clear()\nlog.setLevel(logging.INFO)\nh = logging.StreamHandler(sys.stdout)\nh.setFormatter(logging.Formatter('%(levelname)s %(message)s'))\nlog.addHandler(h)\n\nrows_in, rows_out = 5, 3\nlog.info('read %d rows', rows_in)\nif rows_out < rows_in:\n    log.warning('dropped %d rows', rows_in - rows_out)", run=True,
   q=QC("Which message deserves the level <code>WARNING</code>?", ["Dropped 400 of 1000 rows because amount was missing", "Starting the clean step", "Wrote 600 rows"], 0, "Losing 40 percent of the rows is not a crash, but a human should look at it. Plain progress notes are INFO.")),
 Sh("Week 2 review, part 1: pandas",
   "Quick mixed review of Days 12 to 14. Take your time and predict before you choose. Remember: <code>df[mask]</code> keeps rows, <code>groupby().agg()</code> makes one row per group, <code>reset_index()</code> turns the group names back into a column.",
   "import pandas as pd\ndf = pd.DataFrame({'dept': ['A', 'A', 'B', 'B', 'B'], 'pay': [10, 30, 20, None, 40]})\nprint(df['pay'].mean())\nprint(df.groupby('dept')['pay'].sum().to_dict())", run=True,
   q=Qh("What does this show?", "import pandas as pd\ndf = pd.DataFrame({'dept': ['A', 'A', 'B', 'B', 'B'], 'pay': [10, 30, 20, None, 40]})\nbig = df[(df['pay'] > 15) | (df['dept'] == 'A')]\nprint(len(big))", ["4", "3", "5"], "Rows kept: both A rows (dept is A), and B with 20 and 40 (above 15). The B row with a missing pay is not above 15 and not A, so it is dropped. That is 4 rows.")),
 Sh("Week 2 review, part 2: SQL, Spark and pipelines",
   "One more mixed question across the whole week. Think about what each tool does at its core: SQL asks questions of tables, pandas does it in memory on one machine, Spark does it on many machines, and a pipeline wraps the steps so they can run every day.",
   q=QC("Spark has run <code>df.filter(...).groupBy('k').agg(...)</code> without error, but nothing has been computed yet. Which reasoning is right?", ["Both are transformations (lazy); the work starts at an action such as count() or show()", "filter runs at once; only groupBy waits", "Spark never computes anything until you close the session"], 0, "filter and groupBy/agg are transformations. Spark only builds a plan until an action asks for results.")),
 Sh("Final task: a validated pipeline",
   "Put the week together. You will write one function that reads text, cleans it, checks it, and returns totals. Use <code>read_csv</code> with <code>io.StringIO</code>, <code>drop_duplicates</code>, <code>dropna</code>, <code>.str.strip().str.title()</code>, <code>groupby</code> and <code>raise ValueError</code>. <code>pd</code> and <code>io</code> are already imported.",
   q=Wh("Write <code>pipeline(text)</code>. <code>text</code> is CSV text with columns <code>id</code>, <code>city</code>, <code>amount</code>. (1) Read it with <code>pd.read_csv(io.StringIO(text))</code>. (2) Drop duplicate rows, and rows where <code>amount</code> is missing. (3) Tidy <code>city</code> with <code>.str.strip().str.title()</code>. (4) If no rows are left, <code>raise ValueError('no rows')</code>. (5) Return a dict mapping each city to its total amount, e.g. <code>{'Delhi': 75.0}</code>. Use <code>.groupby('city')['amount'].sum().to_dict()</code>.",
       "def pipeline(text):\n    # 1. read\n    # 2. drop duplicates and missing amounts\n    # 3. tidy the city text\n    # 4. raise ValueError('no rows') if nothing is left\n    # 5. return {city: total}\n    return {}\n",
       "def pipeline(text):\n    df = pd.read_csv(io.StringIO(text))\n    df = df.drop_duplicates().dropna(subset=['amount'])\n    df = df.assign(city=df['city'].str.strip().str.title())\n    if len(df) == 0:\n        raise ValueError('no rows')\n    return df.groupby('city')['amount'].sum().to_dict()\n",
       [("the main data", "pipeline(RAW)"), ("another file", "pipeline(RAW2)"), ("nothing left raises ValueError", "_raises(lambda: pipeline(EMPTY), ValueError)")],
       _PIPE_PRE, "df.drop_duplicates().dropna(subset=['amount']), then df.assign(city=df['city'].str.strip().str.title()), then check len(df) == 0, then groupby('city')['amount'].sum().to_dict().")),
]
