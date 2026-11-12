# Step-by-step lessons for the first week: one small idea per screen, an example to run, then a question.
# Every answer here is computed by running the code at build time (see _out), so an answer cannot be wrong
# unless the code is. Executed inside labs.py.
import io as _io, contextlib as _ctx, builtins as _bi

def _out(code, stdin=None):
    lines = list(stdin or [])
    def _input(prompt=""):
        return lines.pop(0)
    buf = _io.StringIO()
    ns = {"__name__": "__main__", "input": _input}
    with _ctx.redirect_stdout(buf):
        exec(compile(code, "lesson.py", "exec"), ns)
    return "\n".join(l.rstrip() for l in buf.getvalue().strip().splitlines())

def S(h, t, code=None, run=False, stdin=None, q=None):
    d = dict(h=h, t=t)
    if code is not None:
        d["code"] = code
        _out(code, stdin)          # every example must run
    if run:
        d["run"] = True
    if stdin:
        d["stdin"] = stdin
    if q:
        d["q"] = q
    return d

def Q(prompt, code, options, why, stdin=None):
    """Multiple choice where the right option is whatever the code really prints."""
    got = _out(code, stdin)
    assert options.count(got) == 1, ("answer not among options exactly once", prompt, got, options)
    return dict(k="mc", q=prompt, code=code, o=options, a=options.index(got), why=why)

def QE(prompt, code, error, options, a, why):
    """Multiple choice about code that fails: checked that it raises the named error."""
    try:
        _out(code)
    except Exception as e:
        assert type(e).__name__ == error, (prompt, type(e).__name__)
    else:
        raise AssertionError("expected an error: " + prompt)
    assert error in options[a] or "rror" in options[a], prompt
    return dict(k="mc", q=prompt, code=code, o=options, a=a, why=why)

def QC(prompt, options, a, why):
    return dict(k="mc", q=prompt, o=options, a=a, why=why)

def W(task, starter, sol, runs=None, exprs=None, hint="", prelude=""):
    """A small write-it-yourself task. Expected results come from running the solution."""
    tests = []
    for i, st in enumerate(runs or []):
        tests.append(dict(label="Run %d: typed input %s" % (i + 1, ", ".join(st)), stdin=st, out=_out(sol, st)))
    if exprs:
        ns = {}
        exec(prelude + "\n" + sol, ns)
        for e in exprs:
            label, expr = e if isinstance(e, tuple) else (e, e)
            tests.append(dict(label=label, expr=expr, want=repr(eval(expr, ns))))
    assert tests
    d = dict(k="write", task=task, starter=starter, sol=sol, tests=tests, hint=hint)
    if prelude:
        d["prelude"] = prelude
    return d

LESSONS = {}

# ------------------------------------------------------------------ Day 1
LESSONS[1] = [
 S("A program is a list of instructions",
   "Python reads your file from the top and does one line at a time. <code>print(...)</code> shows something on the screen. Press <b>Run</b> to see it, then change the words and run it again.",
   'print("Hello")\nprint("I am learning Python")', run=True,
   q=Q("What does this show?", 'print("Hi")\nprint("there")', ["Hi\nthere", "Hi there", "there\nHi"], "Each print() writes its own line, in the order the lines are written.")),
 S("Text goes inside quotes",
   "Text is called a <b>string</b>. Quotes tell Python: this is text, do not try to calculate it. Without quotes, Python treats what you typed as numbers or names.",
   'print("2 + 2")\nprint(2 + 2)', run=True,
   q=Q("What does this show?", 'print("10 - 3")', ["10 - 3", "7", "Error"], "It is inside quotes, so Python prints the characters exactly and does no maths.")),
 S("A variable is a name for a value",
   "<code>age = 30</code> means: remember the value 30 under the name <code>age</code>. The single <code>=</code> stores; it is not asking a question. You can store a new value later and the old one is replaced.",
   'age = 30\nprint(age)\nage = age + 1\nprint(age)', run=True,
   q=Q("What does this show?", 'x = 5\nx = x + 2\nprint(x)', ["7", "5", "x + 2"], "The right side is worked out first (5 + 2), then stored back into x.")),
 S("Numbers and maths",
   "<code>+ - *</code> work as you expect. <code>/</code> divides and always gives a decimal. <code>//</code> divides and drops the remainder. <code>%</code> gives only the remainder. <code>**</code> is power.",
   'print(7 / 2)\nprint(7 // 2)\nprint(7 % 2)\nprint(2 ** 3)', run=True,
   q=Q("What does this show?", 'print(17 % 5)', ["2", "3", "3.4"], "17 divided by 5 is 3 with 2 left over. % gives the leftover.")),
 S("Every value has a type",
   "Whole numbers are <code>int</code>, decimals are <code>float</code>, text is <code>str</code>. The type decides what <code>+</code> does: numbers are added, strings are joined end to end.",
   'print(3 + 4)\nprint("3" + "4")\nprint(type(3), type("3"))', run=True,
   q=Q("What does this show?", 'print("5" + "5")', ["55", "10", "Error"], "Both are strings, so + joins them.")),
 S("Converting between types",
   "<code>int(\"5\")</code> turns the text 5 into the number 5. <code>float(\"2.5\")</code> gives a decimal. <code>str(5)</code> turns a number into text. You need this whenever a number arrives as text.",
   'print(int("3") + 4)\nprint(float("2.5") * 2)\nprint(str(3) + "4")', run=True,
   q=Q("What does this show?", 'a = "6"\nprint(int(a) * 2)', ["12", "66", "Error"], "int(a) is the number 6, and 6 * 2 is 12. Without int(), \"6\" * 2 would repeat the text: 66.")),
 S("Putting values into text: f-strings",
   "Put <code>f</code> before the opening quote, and anything inside <code>{ }</code> is replaced by its value. This is the normal way to build a message.",
   'name = "Asha"\nitems = 3\nprint(f"Hello, {name}")\nprint(f"{name} has {items * 2} items")', run=True,
   q=Q("What does this show?", 'price = 20\nprint(f"Total: {price * 2}")', ["Total: 40", "Total: {price * 2}", "Total: price * 2"], "Inside the braces Python works out price * 2 and puts the result into the text.")),
 S("Asking the user: input()",
   "<code>input(\"...\")</code> shows a question, waits, and gives back what the person typed. <b>It always gives back text</b>, even if they type digits. In this box, the answers <code>Asha</code> and <code>30</code> are typed for you.",
   'name = input("Name: ")\nage = input("Age: ")\nprint(f"{name} will be {int(age) + 1} next year")', run=True, stdin=["Asha", "30"],
   q=QE("The person types 20. What happens?", 'age = "20"   # what input() gives back\nprint(age + 1)', "TypeError", ["It shows 21", "It shows 201", "An error: you cannot add text and a number"], 2, "input() gave back the text \"20\". Text plus a number is a TypeError. Fix: int(age) + 1.")),
 S("Your turn: write a whole program",
   "No example this time. You have every piece you need: <code>input()</code>, <code>int()</code>, <code>+</code> and <code>print()</code>.",
   q=W("Ask for two whole numbers with <code>input()</code> (two separate lines), then print their sum. Print only the number.",
       "# 1. read the first number\n# 2. read the second number\n# 3. print the sum\n",
       "a = int(input())\nb = int(input())\nprint(a + b)", runs=[["3", "4"], ["10", "5"]],
       hint="input() gives text. Wrap each one: a = int(input())")),
]

# ------------------------------------------------------------------ Day 2
LESSONS[2] = [
 S("Questions that answer True or False",
   "A comparison asks a yes/no question. <code>==</code> means \"is equal to\" (two equals signs; one would store). <code>!=</code> means \"is not equal to\". The answer is <code>True</code> or <code>False</code>.",
   'print(5 > 3)\nprint(5 == 5)\nprint(5 != 5)\nprint(2 <= 1)', run=True,
   q=Q("What does this show?", 'print(10 >= 10)', ["True", "False", "10"], ">= means greater than or equal to, and 10 equals 10.")),
 S("if: run something only when it is true",
   "After <code>if</code> comes a question and a colon. The lines <b>indented</b> underneath run only when the answer is True. A line that is not indented is back outside the if and always runs.",
   'temp = 35\nif temp > 30:\n    print("Hot")\nprint("Done")', run=True,
   q=Q("What does this show?", 'temp = 20\nif temp > 30:\n    print("Hot")\nprint("Done")', ["Done", "Hot\nDone", "Hot"], "20 > 30 is False, so the indented line is skipped. \"Done\" is outside the if.")),
 S("The colon and the indent are the grammar",
   "Python uses the indent (4 spaces) to know which lines belong to the <code>if</code>. Forget the colon and you get a SyntaxError. Indent wrongly and you get an IndentationError, or code that runs at the wrong time.",
   'x = 5\nif x > 3:\n    print("big")\n    print("still inside the if")\nprint("outside")', run=True,
   q=QC("What is missing here?<pre>if x > 3\n    print(\"big\")</pre>", ["The colon after x > 3", "Quotes around x", "A second equals sign"], 0, "Every if line ends with a colon.")),
 S("else and elif: exactly one branch runs",
   "<code>else</code> is what happens when the if is False. <code>elif</code> asks another question first. Python checks from the top and runs only the <b>first</b> branch that is True.",
   'score = 95\nif score >= 90:\n    print("A")\nelif score >= 60:\n    print("B")\nelse:\n    print("C")', run=True,
   q=Q("What does this show?", 'score = 70\nif score >= 90:\n    print("A")\nelif score >= 60:\n    print("B")\nelse:\n    print("C")', ["B", "A", "C", "B\nC"], "70 >= 90 is False, 70 >= 60 is True, so B runs and the rest is skipped.")),
 S("Combining questions: and, or, not",
   "<code>and</code> is True only when both sides are True. <code>or</code> is True when at least one side is. <code>not</code> flips True and False.",
   'age = 25\nhas_ticket = True\nprint(age >= 18 and has_ticket)\nprint(age < 18 or has_ticket)\nprint(not has_ticket)', run=True,
   q=Q("What does this show?", 'age = 25\nhas_id = False\nprint(age >= 18 and has_id)', ["False", "True", "25"], "and needs both sides True. has_id is False.")),
 S("for: do something for each item",
   "A <code>for</code> loop takes the items one at a time. Each time round, the variable (here <code>name</code>) holds the next item, and the indented lines run.",
   'for name in ["Asha", "Ravi", "Meera"]:\n    print("Hello", name)\nprint("Finished")', run=True,
   q=Q("What does this show?", 'for x in [10, 20, 30]:\n    print("hi")', ["hi\nhi\nhi", "hi", "10\n20\n30"], "The list has three items, so the indented line runs three times.")),
 S("range: counting",
   "<code>range(5)</code> gives 0, 1, 2, 3, 4: it starts at 0 and <b>stops before</b> the number you give. <code>range(1, 6)</code> gives 1 to 5.",
   'for i in range(5):\n    print(i)\nprint("---")\nfor i in range(1, 4):\n    print(i)', run=True,
   q=Q("What does this show?", 'for i in range(3):\n    print(i)', ["0\n1\n2", "1\n2\n3", "0\n1\n2\n3"], "range(3) starts at 0 and stops before 3.")),
 S("Building up an answer inside a loop",
   "The most common loop pattern: start a variable before the loop, change it inside, use it after. Here <code>total</code> collects the sum.",
   'total = 0\nfor n in [4, 5, 6]:\n    total = total + n\nprint(total)', run=True,
   q=Q("What does this show?", 'total = 0\nfor n in range(1, 5):\n    total = total + n\nprint(total)', ["10", "15", "4"], "range(1, 5) is 1, 2, 3, 4, and they add up to 10.")),
 S("while: repeat as long as something is true",
   "A <code>while</code> loop checks its question, runs the indented lines, and checks again. Something inside must change, or it never stops.",
   'n = 3\nwhile n > 0:\n    print(n)\n    n = n - 1\nprint("Go")', run=True,
   q=Q("What does this show?", 'count = 0\nwhile count < 3:\n    count = count + 1\nprint(count)', ["3", "2", "0\n1\n2"], "The loop stops when count < 3 is False, which is when count reaches 3. The print is outside the loop.")),
 S("Your turn: a loop that adds",
   "Use what you just saw: read a number, loop with <code>range</code>, build up a total, print it.",
   q=W("Read a whole number <code>n</code> with <code>input()</code>. Print the sum of all whole numbers from 1 to n. For 4 the answer is 10.",
       "n = int(input())\n# start a total at 0\n# loop from 1 to n (remember range stops before its end)\n# print the total\n",
       "n = int(input())\ntotal = 0\nfor i in range(1, n + 1):\n    total = total + i\nprint(total)", runs=[["4"], ["10"], ["1"]],
       hint="range(1, n + 1) gives 1 up to n.")),
]

# ------------------------------------------------------------------ Day 3
LESSONS[3] = [
 S("A list holds many values in order",
   "Square brackets make a list. <code>len(...)</code> tells you how many items it has.",
   'prices = [30, 12, 45]\nprint(prices)\nprint(len(prices))', run=True,
   q=Q("What does this show?", 'print(len([4, 5, 6, 7]))', ["4", "3", "7"], "There are four items.")),
 S("Positions start at 0",
   "<code>xs[0]</code> is the first item, <code>xs[1]</code> the second. <code>xs[-1]</code> is the last one. Asking for a position that does not exist gives an IndexError.",
   'names = ["Asha", "Ravi", "Meera"]\nprint(names[0])\nprint(names[2])\nprint(names[-1])', run=True,
   q=Q("What does this show?", 'xs = ["a", "b", "c"]\nprint(xs[1])', ["b", "a", "c"], "Position 1 is the second item, because counting starts at 0.")),
 S("Slices: taking a part",
   "<code>xs[1:3]</code> takes from position 1 up to, but not including, position 3. Leave a side empty to mean \"from the start\" or \"to the end\".",
   'nums = [10, 20, 30, 40, 50]\nprint(nums[1:3])\nprint(nums[:2])\nprint(nums[3:])', run=True,
   q=Q("What does this show?", 'nums = [10, 20, 30, 40, 50]\nprint(nums[2:4])', ["[30, 40]", "[20, 30, 40]", "[30, 40, 50]"], "Positions 2 and 3. The stop position, 4, is left out.")),
 S("Changing a list",
   "<code>append</code> adds to the end. Assigning to a position replaces that item. <code>in</code> asks whether a value is in the list.",
   'xs = [1, 2]\nxs.append(3)\nxs[0] = 99\nprint(xs)\nprint(2 in xs, 7 in xs)', run=True,
   q=Q("What does this show?", 'xs = [5]\nxs.append(6)\nxs.append(7)\nprint(len(xs))', ["3", "2", "7"], "It started with one item and two were added.")),
 S("A string works like a list of characters",
   "Positions, <code>len</code> and slices all work on text too. One difference: you cannot change a character in place. You build a new string instead.",
   's = "python"\nprint(s[0], s[-1])\nprint(len(s))\nprint(s[0:2])', run=True,
   q=Q("What does this show?", 's = "hello"\nprint(s[1:3])', ["el", "he", "ell"], "Positions 1 and 2: e and l.")),
 S("String methods give you a new string",
   "<code>.lower()</code>, <code>.upper()</code>, <code>.strip()</code> (removes spaces at both ends) and <code>.replace(a, b)</code> do not change the original. They hand back a new string, which you must store or use.",
   's = "  Hello  "\nclean = s.strip().lower()\nprint(clean)\nprint(len(s), len(clean))', run=True,
   q=Q("What does this show?", 's = "  Hi  "\ns.strip()\nprint(len(s))', ["6", "2", "4"], "s.strip() made a new string, but nothing stored it. s still has its 6 characters.")),
 S("split and join",
   "<code>.split()</code> cuts text into a list of words. <code>\" \".join(words)</code> glues a list back into one string, with a space between items.",
   'line = "red green blue"\nwords = line.split()\nprint(words)\nprint("-".join(words))', run=True,
   q=Q("What does this show?", 'print("a,b,c".split(","))', ["['a', 'b', 'c']", "['a,b,c']", "a b c"], "split(\",\") cuts at each comma and gives a list of the pieces.")),
 S("sort() changes the list; sorted() makes a new one",
   "<code>xs.sort()</code> reorders <code>xs</code> itself and gives back <code>None</code>. <code>sorted(xs)</code> leaves <code>xs</code> alone and gives back a new sorted list. Mixing them up is a very common bug.",
   'xs = [3, 1, 2]\nys = sorted(xs)\nprint(xs, ys)\nxs.sort()\nprint(xs)', run=True,
   q=Q("What does this show?", 'xs = [3, 1, 2]\nys = xs.sort()\nprint(ys)', ["None", "[1, 2, 3]", "[3, 1, 2]"], "sort() changes xs in place and returns None, so ys is None.")),
 S("Making a list from a list",
   "A list comprehension is a loop written inside brackets: <code>[what_to_keep for item in items if condition]</code>. The <code>if</code> part is optional.",
   'nums = [1, 2, 3, 4]\nprint([n * 10 for n in nums])\nprint([n for n in nums if n > 2])', run=True,
   q=Q("What does this show?", 'print([x for x in range(6) if x % 2 == 0])', ["[0, 2, 4]", "[1, 3, 5]", "[0, 1, 2, 3, 4, 5]"], "range(6) is 0 to 5, and the if keeps the even ones.")),
 S("Your turn: reverse the words",
   "You need three things from this lesson: <code>split</code>, a slice that reverses (<code>[::-1]</code> walks backwards), and <code>join</code>.",
   'print([1, 2, 3][::-1])', run=True,
   q=W("Read one line of words with <code>input()</code>. Print the words in reverse order, separated by single spaces. <code>hello big world</code> becomes <code>world big hello</code>.",
       "line = input()\n# 1. split the line into words\n# 2. reverse the list\n# 3. join with spaces and print\n",
       'line = input()\nwords = line.split()\nprint(" ".join(words[::-1]))', runs=[["hello big world"], ["a b"], ["one"]],
       hint='words[::-1] is the list backwards. " ".join(...) glues it.')),
]

# ------------------------------------------------------------------ Day 4
LESSONS[4] = [
 S("A dict looks things up by name",
   "A list finds items by position. A <b>dict</b> finds them by a <b>key</b> you choose. Curly braces, and <code>key: value</code> pairs.",
   'prices = {"tea": 10, "coffee": 25}\nprint(prices["tea"])\nprint(len(prices))', run=True,
   q=Q("What does this show?", 'ages = {"asha": 30, "ravi": 41}\nprint(ages["ravi"])', ["41", "30", "ravi"], "The key \"ravi\" leads to the value 41.")),
 S("Adding and changing",
   "<code>d[key] = value</code> adds the key if it is new, or replaces its value if it already exists.",
   'd = {"a": 1}\nd["b"] = 2\nd["a"] = 5\nprint(d)', run=True,
   q=Q("What does this show?", 'stock = {"pen": 3}\nstock["pen"] = stock["pen"] + 2\nstock["cup"] = 1\nprint(stock)', ["{'pen': 5, 'cup': 1}", "{'pen': 3, 'cup': 1}", "{'pen': 2, 'cup': 1}"], "pen was 3 and 2 was added; cup is a new key.")),
 S("A key that is not there",
   "<code>d[\"z\"]</code> on a missing key stops the program with a KeyError. Two safe ways: ask first with <code>in</code>, or use <code>d.get(key, default)</code>, which gives the default instead of failing.",
   'd = {"a": 1}\nprint("a" in d, "z" in d)\nprint(d.get("a", 0))\nprint(d.get("z", 0))', run=True,
   q=Q("What does this show?", 'd = {"a": 1}\nprint(d.get("z", 0) + 1)', ["1", "0", "Error"], "\"z\" is missing, so get gives the default 0, and 0 + 1 is 1.")),
 S("The counting pattern",
   "To count things: for each item, take its count so far (0 if never seen) and add 1. This one line is used constantly in interviews and real work.",
   'counts = {}\nfor ch in "aab":\n    counts[ch] = counts.get(ch, 0) + 1\nprint(counts)', run=True,
   q=Q("What does this show?", 'counts = {}\nfor w in ["x", "y", "x", "x"]:\n    counts[w] = counts.get(w, 0) + 1\nprint(counts["x"])', ["3", "1", "4"], "\"x\" appears three times.")),
 S("Walking through a dict",
   "<code>for key, value in d.items():</code> gives you each pair in turn, in the order the keys were added.",
   'd = {"x": 1, "y": 2}\nfor key, value in d.items():\n    print(key, value)', run=True,
   q=Q("What does this show?", 'd = {"a": 10, "b": 20}\ntotal = 0\nfor k, v in d.items():\n    total = total + v\nprint(total)', ["30", "20", "ab"], "The loop adds the values 10 and 20.")),
 S("A set keeps only different values",
   "A set is like a dict with keys and no values. It never holds the same thing twice, and asking <code>x in my_set</code> is very fast.",
   'seen = set()\nseen.add(3)\nseen.add(3)\nseen.add(5)\nprint(len(seen))\nprint(3 in seen, 9 in seen)', run=True,
   q=Q("What does this show?", 'print(len(set([1, 1, 2, 3, 3])))', ["3", "5", "2"], "Only the different values are kept: 1, 2 and 3.")),
 S("Your first pattern: \"have I seen this before?\"",
   "Keep a set of what you have met. For each new item, ask whether it is already in the set. One pass through the data, however long it is. This idea solves a whole family of problems.",
   'def first_repeat(items):\n    seen = set()\n    for x in items:\n        if x in seen:\n            return x\n        seen.add(x)\n    return None\n\nprint(first_repeat([3, 5, 3, 5]))\nprint(first_repeat([1, 2, 3]))', run=True,
   q=QC("You must check whether each of a million ids has appeared before. What should hold the ids you have met?", ["A set", "A list", "One long string"], 0, "A set answers \"is it in here?\" almost instantly. A list has to look at its items one by one, which gets slow.")),
 S("Your turn: count the words",
   "Use the counting pattern from this lesson, then walk through the dict to print.",
   q=W("Read one line of words with <code>input()</code>. Print each different word with its count, in the order the words first appear, like <code>a 2</code>, one per line.",
       "line = input()\ncounts = {}\n# 1. for each word, add 1 to its count\n# 2. for each word and count, print them\n",
       "line = input()\ncounts = {}\nfor w in line.split():\n    counts[w] = counts.get(w, 0) + 1\nfor w, c in counts.items():\n    print(w, c)", runs=[["a b a"], ["x"], ["to be or not to be"]],
       hint="counts[w] = counts.get(w, 0) + 1, then loop over counts.items().")),
]

# ------------------------------------------------------------------ Day 5
LESSONS[5] = [
 S("A function is a named piece of code",
   "<code>def</code> defines it. Nothing runs until you <b>call</b> it by writing its name with brackets. You can call it as many times as you like.",
   'def greet():\n    print("Hi")\n\ngreet()\ngreet()', run=True,
   q=Q("What does this show?", 'def cheer():\n    print("Go")\n\nprint("Start")\ncheer()', ["Start\nGo", "Go\nStart", "Start"], "Defining the function prints nothing. It runs when called, after \"Start\".")),
 S("Giving a function inputs",
   "Names in the brackets are <b>parameters</b>: values the caller hands in.",
   'def greet(name):\n    print(f"Hello, {name}")\n\ngreet("Asha")\ngreet("Ravi")', run=True,
   q=Q("What does this show?", 'def double(n):\n    print(n * 2)\n\ndouble(4)', ["8", "4", "n * 2"], "n is 4 inside the function, so it prints 8.")),
 S("return hands a value back",
   "<code>print</code> only shows something. <code>return</code> gives the result back to the code that called the function, so it can be stored or used in more maths. Most functions you write should return.",
   'def add(a, b):\n    return a + b\n\ntotal = add(2, 3)\nprint(total * 10)', run=True,
   q=Q("What does this show?", 'def area(w, h):\n    return w * h\n\nprint(area(3, 4) + 1)', ["13", "12", "Error"], "area(3, 4) becomes 12, and 12 + 1 is 13.")),
 S("No return means None",
   "If a function reaches its end without a <code>return</code>, the caller gets <code>None</code>. Forgetting <code>return</code> is one of the most common beginner bugs.",
   'def no_return(x):\n    x + 1\n\nresult = no_return(2)\nprint(result)', run=True,
   q=Q("What does this show?", 'def plus_one(x):\n    y = x + 1\n\nprint(plus_one(5))', ["None", "6", "5"], "The function worked out 6 but never returned it.")),
 S("return ends the function at once",
   "As soon as a <code>return</code> runs, the function stops. That is how \"find the first...\" functions work: return inside the loop when you find it, and return a fallback after the loop.",
   'def first_even(xs):\n    for x in xs:\n        if x % 2 == 0:\n            return x\n    return None\n\nprint(first_even([3, 8, 6]))\nprint(first_even([1, 3]))', run=True,
   q=Q("What does this show?", 'def first_big(xs):\n    for x in xs:\n        if x > 10:\n            return x\n    return -1\n\nprint(first_big([4, 15, 30]))', ["15", "30", "-1"], "15 is the first value above 10, and return stops the loop there.")),
 S("Default values",
   "A parameter can have a default, used when the caller leaves it out.",
   'def power(n, p=2):\n    return n ** p\n\nprint(power(3))\nprint(power(2, 3))', run=True,
   q=Q("What does this show?", 'def greet(name, word="Hello"):\n    return f"{word}, {name}"\n\nprint(greet("Asha"))', ["Hello, Asha", "Asha, Hello", "Error"], "word was not given, so its default \"Hello\" is used.")),
 S("Reading an error message",
   "When code crashes Python prints a <b>traceback</b>. Read the <b>last line first</b>: it names the error type and says what went wrong. Then look just above it for the line number in your file.<pre>Traceback (most recent call last):\n  File \"main.py\", line 3, in &lt;module&gt;\n    print(totl)\nNameError: name 'totl' is not defined</pre>",
   q=QC("What does that last line tell you?", ["Line 3 uses a name, totl, that was never created (probably a typo for total)", "The file main.py is missing", "Python is not installed correctly"], 0, "NameError means a name does not exist. The line above shows where: line 3.")),
 S("try / except: plan for the error",
   "Put risky code under <code>try</code>. If the named error happens, Python jumps to <code>except</code> instead of crashing.",
   'def safe_int(text, default=0):\n    try:\n        return int(text)\n    except ValueError:\n        return default\n\nprint(safe_int("42"))\nprint(safe_int("abc"))', run=True,
   q=Q("What does this show?", 'def safe_int(text, default=-1):\n    try:\n        return int(text)\n    except ValueError:\n        return default\n\nprint(safe_int("7"), safe_int("x"))', ["7 -1", "7 x", "Error"], "\"7\" converts. \"x\" raises ValueError, so the default -1 is returned.")),
 S("Your turn: write a function",
   "This is the shape every code lab uses: you write a function, and tests call it with different inputs.",
   q=W("Write <code>average(nums)</code> that returns the average of a list of numbers. For an empty list return <code>0</code>. <code>sum(nums)</code> adds a list and <code>len(nums)</code> counts it.",
       "def average(nums):\n    # 1. if the list is empty, return 0\n    # 2. otherwise return the sum divided by the count\n    pass\n",
       "def average(nums):\n    if len(nums) == 0:\n        return 0\n    return sum(nums) / len(nums)", exprs=["average([2, 4])", "average([5])", "average([])", "average([1, 2, 3, 4])"],
       hint="Check len(nums) == 0 first, then return sum(nums) / len(nums).")),
]

# ------------------------------------------------------------------ Day 6
LESSONS[6] = [
 S("Borrowing code: import",
   "Python comes with ready-made tools called <b>modules</b>. <code>import math</code> loads one; then you use its functions with a dot.",
   'import math\nprint(math.sqrt(16))\nprint(math.floor(3.7))', run=True,
   q=Q("What does this show?", 'import math\nprint(math.ceil(2.1))', ["3", "2", "2.1"], "ceil rounds up to the next whole number.")),
 S("Importing just one thing",
   "<code>from module import name</code> brings in a single tool, so you can use it without the module name in front.",
   'from collections import Counter\nprint(Counter("aab"))', run=True,
   q=Q("What does this show?", 'from collections import Counter\nc = Counter(["x", "y", "x"])\nprint(c["x"])', ["2", "1", "3"], "Counter does the counting pattern from Day 4 for you. \"x\" appears twice.")),
 S("JSON: data as text",
   "Programs send data to each other as JSON text. <code>json.loads(text)</code> turns that text into dicts and lists. <code>json.dumps(data)</code> turns your data into text.",
   'import json\ntext = \'{"name": "Asha", "skills": ["sql", "python"]}\'\ndata = json.loads(text)\nprint(data["name"])\nprint(data["skills"][1])\nprint(json.dumps({"ok": True}))', run=True,
   q=Q("What does this show?", 'import json\ndata = json.loads(\'{"a": 1, "b": [10, 20]}\')\nprint(data["b"][0] + data["a"])', ["11", "21", "Error"], "data[\"b\"][0] is 10 and data[\"a\"] is 1.")),
 S("Writing and reading a file",
   "<code>with open(name, \"w\") as f:</code> opens a file for writing; plain <code>open(name)</code> opens it for reading. The <code>with</code> block closes the file for you when it ends.",
   'with open("notes.txt", "w") as f:\n    f.write("first line\\nsecond line")\n\nwith open("notes.txt") as f:\n    for line in f:\n        print(line.strip())', run=True,
   q=Q("What does this show?", 'with open("n.txt", "w") as f:\n    f.write("a\\nb\\nc")\nwith open("n.txt") as f:\n    lines = f.read().split("\\n")\nprint(len(lines))', ["3", "1", "5"], "The file has three lines, and split cuts at each line break.")),
 S("Other people's code: pip and virtual environments",
   "Tools that do not come with Python are installed from the terminal with <code>pip install name</code>. Each project should get its own <b>virtual environment</b>, a private folder of installed tools, so projects do not break each other. You will do this on a laptop:<pre>python -m venv .venv\nsource .venv/bin/activate     # Windows: .venv\\Scripts\\activate\npip install requests</pre>This cannot run in the browser, so there is nothing to press here.",
   q=QC("Why give each project its own virtual environment?", ["So each project keeps its own versions of installed tools", "It makes Python run faster", "It is required to use print()"], 0, "Two projects may need different versions of the same tool. Separate environments stop them clashing.")),
 S("Your turn: read JSON",
   "Combine <code>input()</code>, <code>json.loads</code> and <code>len</code>.",
   q=W("Read one line of JSON text with <code>input()</code>. It is always an object (a dict). Print how many keys it has.",
       "import json\ntext = input()\n# 1. turn the text into a dict\n# 2. print how many keys it has\n",
       "import json\ntext = input()\ndata = json.loads(text)\nprint(len(data))", runs=[['{"a": 1, "b": 2}'], ['{}'], ['{"x": [1, 2, 3]}']],
       hint="data = json.loads(text), then len(data).")),
]

# ------------------------------------------------------------------ Day 7
LESSONS[7] = [
 S("A class is a blueprint for your own kind of thing",
   "A dict can hold a task's title and whether it is done. A <b>class</b> does the same and also keeps the functions that work on it in one place. <code>__init__</code> runs when you make a new one, and <code>self</code> is the one being made.",
   'class Task:\n    def __init__(self, title):\n        self.title = title\n        self.done = False\n\nt = Task("Learn classes")\nprint(t.title, t.done)', run=True,
   q=Q("What does this show?", 'class Dog:\n    def __init__(self, name):\n        self.name = name\n        self.legs = 4\n\nd = Dog("Rex")\nprint(d.name, d.legs)', ["Rex 4", "name 4", "Error"], "__init__ stored \"Rex\" as name and 4 as legs on this dog.")),
 S("Methods: functions that belong to the object",
   "A function inside a class is a <b>method</b>. Its first parameter is always <code>self</code>, the object it was called on. You call it with a dot.",
   'class Task:\n    def __init__(self, title):\n        self.title = title\n        self.done = False\n    def finish(self):\n        self.done = True\n\nt = Task("Write tests")\nt.finish()\nprint(t.done)', run=True,
   q=Q("What does this show?", 'class Counter:\n    def __init__(self):\n        self.n = 0\n    def bump(self):\n        self.n = self.n + 1\n\nc = Counter()\nc.bump()\nc.bump()\nprint(c.n)', ["2", "0", "1"], "Each bump() adds 1 to this counter's n.")),
 S("Each object has its own data",
   "Two objects made from the same class do not share their values.",
   'class Counter:\n    def __init__(self):\n        self.n = 0\n    def bump(self):\n        self.n = self.n + 1\n\na = Counter()\nb = Counter()\na.bump()\nprint(a.n, b.n)', run=True,
   q=Q("What does this show?", 'class Box:\n    def __init__(self, size):\n        self.size = size\n\nx = Box(1)\ny = Box(5)\nx.size = 9\nprint(y.size)', ["5", "9", "1"], "Changing x does not touch y.")),
 S("@dataclass: less typing",
   "For classes that mostly hold data, <code>@dataclass</code> writes <code>__init__</code> for you from the list of fields, and gives a readable print.",
   'from dataclasses import dataclass\n\n@dataclass\nclass Task:\n    title: str\n    done: bool = False\n\nt = Task("Learn classes")\nt.done = True\nprint(t)', run=True,
   q=Q("What does this show?", 'from dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: int\n    y: int = 0\n\np = Point(3)\nprint(p.x + p.y)', ["3", "0", "Error"], "y was not given, so it is its default 0. 3 + 0 is 3.")),
 S("Your turn: write a class",
   "Write the <code>__init__</code> and one method, the same shape as the Counter above.",
   q=W("Write a class <code>Tally</code>. A new Tally starts with <code>total</code> equal to 0. Its method <code>add(n)</code> adds <code>n</code> to <code>total</code>.",
       "class Tally:\n    def __init__(self):\n        pass\n\n    def add(self, n):\n        pass\n",
       "class Tally:\n    def __init__(self):\n        self.total = 0\n\n    def add(self, n):\n        self.total = self.total + n",
       exprs=[("a new Tally has total 0", "Tally().total"), ("after add(5) and add(2)", "_after([5, 2])"), ("after add(10), add(-3), add(1)", "_after([10, -3, 1])"), ("two tallies do not share a total", "_two()")],
       prelude="def _after(nums):\n    t = Tally()\n    for n in nums:\n        t.add(n)\n    return t.total\ndef _two():\n    a = Tally()\n    b = Tally()\n    a.add(3)\n    return b.total\n",
       hint="In __init__: self.total = 0. In add: self.total = self.total + n.")),
]

for _n, _ls in LESSONS.items():
    assert _ls[-1]["q"]["k"] == "write", _n
    for _s in _ls:
        assert "q" in _s, (_n, _s["h"])
exec(open(_os.path.join(_HERE, 'lessons_sql.py'), encoding='utf-8').read())
