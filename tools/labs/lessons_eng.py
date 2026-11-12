# Lessons for Days 22-30 (engineering track). Exec'd inside lessons.py after helpers exist.

# ------------------------------------------------------------------ Day 22
LESSONS[22] = [
 Sd("Git remembers every version of your project",
   "<b>Git</b> is a tool that saves snapshots of your project folder. Each saved snapshot is a <b>commit</b>: the files as they were, plus a short message saying why. You can go back to any commit, and teams use it so many people can change the same project without overwriting each other. Run these in a terminal inside your project folder.",
   "git init      # start tracking this folder\ngit status    # what has changed since the last snapshot?",
   q=QC("What is a commit?", ["A saved snapshot of your project with a message", "A copy of your project on GitHub", "A command that deletes old files"], 0, "A commit is a snapshot in your own history. Putting a copy on GitHub is a separate step called push.")),
 S("Three places a change can live",
   "A change moves through three places. Your <b>folder</b> (where you edit), the <b>staging area</b> (a waiting room for what goes into the next commit) and the <b>history</b> (saved commits). <code>git add</code> moves a file into the waiting room. <code>git commit</code> saves everything waiting as one snapshot. This pure-Python model behaves the same way.",
   r'''files = {"app.py": "print(1)", "notes.txt": "todo"}   # your folder
staged = []                                            # the waiting room
history = []                                           # saved commits

def add(name):
    staged.append(name)

def commit(message):
    snapshot = {n: files[n] for n in staged}
    history.append((message, snapshot))
    staged.clear()

add("app.py")
commit("first version")
print(len(history), staged)
print(list(history[0][1]))''', run=True,
   q=Q("What does this show?", r'''files = {"a": 1, "b": 2}
staged = []
history = []
staged.append("a")
staged.append("b")
history.append({n: files[n] for n in staged})
staged.clear()
print(len(history[0]))''', ["2", "1", "0"], "Both files were waiting, so the snapshot holds two files.")),
 Sd("The four commands you use every day",
   "Check what changed, choose what to save, save it with a message, read the history. Write messages that say what and why, such as <i>Add login check</i>, not <i>stuff</i>.",
   "git status\ngit add app.py\ngit commit -m \"Add login check\"\ngit log --oneline",
   q=QC("You edited two files but only ran <code>git add app.py</code> before committing. What does the commit contain?", ["Only the change to app.py: only staged changes are saved", "Both files, because they are in the same folder", "Nothing, commit needs a second add"], 0, "Commit saves what is in the waiting room, nothing else. The other file stays changed but unsaved.")),
 S("Reading git status --porcelain",
   "<code>git status</code> is written for people. <code>git status --porcelain</code> prints one short line per changed file, made for programs to read. The first two characters are a code, then a space, then the file path. <code>M</code> means modified, <code>A</code> added, <code>D</code> deleted, and <code>??</code> means new and not yet tracked. Slicing a line gives you the pieces.",
   r'''text = " M app.py\nA  new.py\n?? notes.txt"
for line in text.splitlines():
    code = line[:2]
    path = line[3:]
    print(repr(code), path)''', run=True,
   q=Q("What does this show?", r'''line = "A  lib.py"
print(line[3:])''', ["lib.py", "A  lib.py", "A"], "The first three characters are the two-letter code and the space. From position 3 on is the path.")),
 S("A branch is just a movable label",
   "A <b>branch</b> is a name that points at a commit. <code>main</code> is the usual default. To try an idea safely you make a new branch, commit on it, and later <b>merge</b> it back. The real commands are <code>git switch -c idea</code> (make and move to a branch) and <code>git merge idea</code>. Modelled with a dict:",
   r'''branches = {"main": "c3"}
branches["idea"] = branches["main"]   # new branch starts at the same commit
branches["idea"] = "c4"               # you commit on idea
print(branches)''', run=True,
   q=Q("What does this show?", r'''b = {"main": "c1"}
b["fix"] = b["main"]
b["fix"] = "c2"
print(b["main"], b["fix"])''', ["c1 c2", "c2 c2", "c1 c1"], "Committing on fix moved only the fix label. main stayed where it was.")),
 Sd("Merge conflicts are not scary",
   "If two branches changed the same lines, git cannot choose and marks the file. You open it, keep the right version, delete the marker lines, then <code>git add</code> and <code>git commit</code>. The markers look like this:",
   "<<<<<<< HEAD\nprice = 10\n=======\nprice = 12\n>>>>>>> idea",
   q=QC("What do you do with the marker lines <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code>, <code>=======</code> and <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code>?", ["Edit the file to the version you want and delete the markers", "Leave them, git removes them later", "Rename the file"], 0, "The markers are only there to show you both versions. The file must contain just your final code before you commit.")),
 Sd("Remote, GitHub, push and pull",
   "A <b>remote</b> is a copy of your repository on another computer. <b>GitHub</b> is a website that hosts remotes. <code>git clone</code> downloads one. <code>git push</code> uploads your new commits. <code>git pull</code> downloads other people's commits. A <b>pull request</b> is a GitHub page asking to merge your branch into main, where teammates review it.",
   "git clone https://github.com/your-name/your-repo.git\ngit push origin main\ngit pull",
   q=QC("A teammate pushed new commits. How do you get them?", ["git pull", "git push", "git init"], 0, "Pull downloads others' commits. Push uploads yours.")),
 Sd("Terminal basics",
   "The terminal is a text window where you type commands. You are always \"in\" a folder. <code>pwd</code> prints which one, <code>ls</code> lists files, <code>cd name</code> goes into a folder, <code>cd ..</code> goes up one, <code>mkdir name</code> makes a folder. On Windows PowerShell, <code>pwd</code>, <code>ls</code>, <code>cd</code> and <code>mkdir</code> work too.",
   "pwd\nls\nmkdir demo\ncd demo\ncd ..",
   q=QC("You are in /home/asha/demo. What does <code>cd ..</code> do?", ["Moves you to /home/asha", "Deletes the demo folder", "Lists the files in demo"], 0, "Two dots mean the parent folder, one level up.")),
 S("Your turn: parse git status",
   "A real tool reads git output exactly like this. Use the slicing you saw.",
   q=W("Write <code>parse_status(text)</code>. <code>text</code> is the output of <code>git status --porcelain</code>, one change per line (code of two characters, a space, then the path). Return a dict with the four keys <code>modified</code>, <code>added</code>, <code>deleted</code>, <code>untracked</code>, each a list of paths in the order they appear. Code <code>??</code> is untracked; otherwise a code containing <code>A</code> is added, <code>M</code> modified, <code>D</code> deleted. Ignore blank lines.",
       "def parse_status(text):\n    out = {\"modified\": [], \"added\": [], \"deleted\": [], \"untracked\": []}\n    # for each line: code = line[:2], path = line[3:]\n    pass\n",
       "def parse_status(text):\n    out = {\"modified\": [], \"added\": [], \"deleted\": [], \"untracked\": []}\n    for line in text.splitlines():\n        if len(line) < 4:\n            continue\n        code, path = line[:2], line[3:]\n        if code == \"??\":\n            out[\"untracked\"].append(path)\n        elif \"A\" in code:\n            out[\"added\"].append(path)\n        elif \"M\" in code:\n            out[\"modified\"].append(path)\n        elif \"D\" in code:\n            out[\"deleted\"].append(path)\n    return out",
       exprs=["parse_status('')", "parse_status(' M app.py')", "parse_status('A  new.py\\n?? notes.txt\\n D old.py')", "parse_status('M  a.py\\n M b.py\\n\\n?? c.py\\n?? d.py')", "parse_status('AM x.py')['added']"],
       hint="Loop over text.splitlines(). If code == '??' append to untracked; elif 'A' in code ... and so on. Return out at the end.")),
]

# ------------------------------------------------------------------ Day 23
LESSONS[23] = [
 Sd("A request goes out, a response comes back",
   "When your phone loads a page or an app, a <b>client</b> sends a <b>request</b> to a <b>server</b>, and the server sends back a <b>response</b>. This is <b>HTTP</b>. A request has a method, a path and sometimes a body. A response has a status code and usually a body. An <b>API</b> is a server designed for programs, not people, to talk to.",
   "GET /users/7 HTTP/1.1\nHost: example.com\n\n---- response ----\nHTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"id\": 7, \"name\": \"Asha\"}",
   q=QC("In a web request, who is the client?", ["The program that sends the request, such as a browser or your script", "The computer that stores the data", "The database"], 0, "The client asks. The server answers.")),
 Sd("Methods say what you want to do",
   "<code>GET</code> reads data and changes nothing. <code>POST</code> creates something. <code>PUT</code> or <code>PATCH</code> changes it. <code>DELETE</code> removes it. The path, such as <code>/users/7</code>, says which thing.",
   "GET    /users/7      # read user 7\nPOST   /users        # create a user\nDELETE /users/7      # delete user 7",
   q=QC("Which method fits \"add a new order\"?", ["POST", "GET", "DELETE"], 0, "POST creates a new thing. GET only reads.")),
 S("Status codes are the server's one-number answer",
   "<code>2xx</code> means success (200 OK, 201 Created). <code>4xx</code> means the client made a mistake (400 bad request, 404 not found, 422 invalid data). <code>5xx</code> means the server failed (500). Knowing the first digit tells you whose fault it is.",
   r'''def who_is_at_fault(code):
    if code < 300:
        return "nobody, it worked"
    if code < 500:
        return "the client"
    return "the server"

for c in [200, 404, 500]:
    print(c, who_is_at_fault(c))''', run=True,
   q=Q("What does this show?", r'''code = 422
print("client" if 400 <= code < 500 else "other")''', ["client", "other", "422"], "422 is in the 4xx range, which means the request was wrong.")),
 S("JSON is the language of APIs",
   "Requests and responses carry text in <b>JSON</b> format. You met it on Day 6: <code>json.dumps</code> turns Python data into text, <code>json.loads</code> turns it back. A body that is not valid JSON, or that lacks a field you need, is the most common cause of a 4xx.",
   r'''import json
body = json.dumps({"name": "Pen", "price": 12.5})
print(body)
back = json.loads(body)
print(back["price"] + 1)''', run=True,
   q=Q("What does this show?", r'''import json
data = json.loads('{"a": {"b": [5, 6]}}')
print(data["a"]["b"][1])''', ["6", "5", "b"], "data[\"a\"] is the inner dict, [\"b\"] is the list, and index 1 is 6.")),
 Sd("Your first FastAPI route",
   "FastAPI is a Python library for building APIs. A <b>route</b> (also called an <b>endpoint</b>) connects a method and path to a function. The line starting with <code>@</code> is a <b>decorator</b>: it registers the function below it. Whatever the function returns is turned into JSON. Install with <code>pip install fastapi uvicorn</code> and start the server with the terminal command <code>uvicorn main:app --reload</code>. This runs on your computer, not in this page.",
   "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\"}",
   q=QC("A browser visits <code>/health</code> with the code above. What does it receive?", ["The JSON {\"status\": \"ok\"} with status 200", "A 404 error", "Python source code"], 0, "A GET to /health calls the function and sends its returned dict as JSON.")),
 Sd("Path and query parameters",
   "Part of the path can be a variable: <code>{item_id}</code> in the route becomes a function argument. Adding a type such as <code>int</code> makes FastAPI convert it, and answer 422 if it cannot (for example <code>/items/abc</code>). Arguments not in the path are <b>query parameters</b>, written after a question mark: <code>/items/3?verbose=true</code>.",
   "@app.get(\"/items/{item_id}\")\ndef get_item(item_id: int, verbose: bool = False):\n    return {\"id\": item_id, \"verbose\": verbose}",
   q=QC("What happens for <code>GET /items/abc</code> with the route above?", ["FastAPI answers 422 because abc is not an int", "It returns item abc", "The server crashes with 500"], 0, "The type hint is a promise FastAPI checks for you. A value that does not fit is rejected before your function runs.")),
 Sd("Validating a body with a model",
   "For POST you describe the expected body with a <b>pydantic model</b>: a class listing field names and types. FastAPI checks every incoming body against it and answers 422 with details when it does not match. <code>status_code=201</code> sets what a success returns.",
   "from pydantic import BaseModel\n\nclass Item(BaseModel):\n    name: str\n    price: float\n\n@app.post(\"/items\", status_code=201)\ndef create_item(item: Item):\n    return {\"name\": item.name, \"price\": item.price}",
   q=QC("A client POSTs <code>{\"name\": \"Pen\"}</code> (no price). What does FastAPI answer?", ["422, because the required field price is missing", "201 with price 0", "200 with an empty body"], 0, "price has no default, so it is required. Missing required data is a client mistake, 4xx.")),
 S("Modelling the validation yourself",
   "The real library hides the checking. Doing it by hand once shows what is going on: a function takes the body and returns a status code with a body. Note that <code>bool</code> is secretly a number in Python, so careful validators exclude it.",
   r'''def check(body):
    if not isinstance(body, dict) or "name" not in body:
        return 422, {"detail": "name is required"}
    return 201, {"name": body["name"]}

print(check({"name": "Pen"}))
print(check({}))''', run=True,
   q=Q("What does this show?", r'''print(isinstance(True, int), isinstance("5", int))''', ["True False", "False False", "True True"], "In Python True counts as the int 1, which is why a price check must exclude booleans.")),
 S("Your turn: a route function",
   "Write the logic of a POST route as a plain function that returns a status code and a body, the way FastAPI would.",
   q=W("Write <code>create_item(body)</code> returning a dict <code>{\"status\": ..., \"body\": ...}</code>. Rules in this order: if <code>body</code> is not a dict, or <code>name</code> is not a non-empty string (ignoring spaces), return status 422 with body <code>{\"detail\": \"name must be a non-empty string\"}</code>. If <code>price</code> is missing, not a number (ints and floats only, not True/False) or not above 0, return 422 with <code>{\"detail\": \"price must be a number above 0\"}</code>. Otherwise return status 201 with body <code>{\"name\": name stripped of spaces, \"price\": price}</code>.",
       "def create_item(body):\n    # check name, then price, then build the 201 answer\n    pass\n",
       "def create_item(body):\n    if not isinstance(body, dict):\n        return {\"status\": 422, \"body\": {\"detail\": \"name must be a non-empty string\"}}\n    name = body.get(\"name\")\n    if not isinstance(name, str) or not name.strip():\n        return {\"status\": 422, \"body\": {\"detail\": \"name must be a non-empty string\"}}\n    price = body.get(\"price\")\n    if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:\n        return {\"status\": 422, \"body\": {\"detail\": \"price must be a number above 0\"}}\n    return {\"status\": 201, \"body\": {\"name\": name.strip(), \"price\": price}}",
       exprs=["create_item({'name': 'Pen', 'price': 12.5})", "create_item({'name': '  Pen  ', 'price': 3})", "create_item({'price': 3})", "create_item({'name': '   ', 'price': 3})", "create_item({'name': 'Pen'})", "create_item({'name': 'Pen', 'price': '5'})", "create_item({'name': 'Pen', 'price': True})", "create_item({'name': 'Pen', 'price': 0})", "create_item([1, 2])"],
       hint="Check name first, then price. isinstance(price, bool) must be tested before isinstance(price, (int, float)).")),
]

# ------------------------------------------------------------------ Day 24
LESSONS[24] = [
 S("What an LLM API is",
   "An <b>LLM</b> (large language model) is a program that continues text. An <b>LLM API</b> lets your code send it text over the internet and get text back. You pay by the <b>token</b>: a small chunk of text, very roughly four characters or three quarters of a word in English. Exact counts depend on the model, so this is only an estimate.",
   r'''def rough_tokens(text):
    return max(1, len(text) // 4)

print(rough_tokens("Explain what an API is in one sentence."))''', run=True,
   q=Q("What does this show?", r'''def rough_tokens(text):
    return max(1, len(text) // 4)
print(rough_tokens("a" * 40))''', ["10", "4", "40"], "40 characters divided by 4 is about 10 tokens.")),
 S("A conversation is a list of messages",
   "The model remembers nothing between calls. Every call sends the <b>whole conversation</b> as a list of messages. Each message has a <b>role</b>: <code>system</code> (standing instructions), <code>user</code> (the person) or <code>assistant</code> (the model's earlier replies). To continue a chat, you append and send the list again.",
   r'''messages = [
    {"role": "system", "content": "You are a concise tutor."},
    {"role": "user", "content": "What is a list?"},
]
messages.append({"role": "assistant", "content": "An ordered collection."})
messages.append({"role": "user", "content": "Give an example."})
for m in messages:
    print(m["role"])''', run=True,
   q=Q("What does this show?", r'''msgs = [{"role": "user", "content": "hi"}]
msgs.append({"role": "assistant", "content": "hello"})
msgs.append({"role": "user", "content": "bye"})
print(len(msgs))''', ["3", "2", "1"], "One message to start, two appended.")),
 Sd("What a real call looks like",
   "With Anthropic's Python library the shape is roughly the code below. Other providers differ in small details (for example, where the system text goes), so always check the provider's docs for the current model names and fields. The key comes from an environment variable, never typed into code you share. This course uses a pure-Python fake model for practice, because the real call needs a key and internet.",
   "import anthropic\n\nclient = anthropic.Anthropic()   # reads the key from the ANTHROPIC_API_KEY environment variable\nreply = client.messages.create(\n    model=\"MODEL-NAME-FROM-DOCS\",\n    max_tokens=300,\n    system=\"You are a concise tutor.\",\n    messages=[{\"role\": \"user\", \"content\": \"What is a list?\"}],\n)\nprint(reply.content[0].text)",
   q=QC("Where should an API key live?", ["In an environment variable or secrets store, not in code you commit", "Hard-coded in the source so it never gets lost", "In the README"], 0, "A key committed to GitHub can be found and abused within minutes. Keep it out of code.")),
 S("A fake model makes your code testable",
   "Real calls cost money, are slow and give different answers each time. So professionals write their code to accept <b>any function that takes messages and returns text</b>, then test with a fake one. Swapping in the real client later changes one line.",
   r'''def fake_llm(messages):
    last = messages[-1]["content"]
    return "You said: " + last

def ask(llm, question):
    return llm([{"role": "user", "content": question}])

print(ask(fake_llm, "hello"))''', run=True,
   q=Q("What does this show?", r'''def fake_llm(messages):
    return str(len(messages))
print(fake_llm([{"role": "user", "content": "a"}, {"role": "user", "content": "b"}]))''', ["2", "1", "ab"], "The fake returns how many messages it was given: two.")),
 S("Tokens are money, so do the sums",
   "Providers list a price per million tokens, one for input and usually a higher one for output. Cost = tokens divided by one million, times the price. The prices below are made up for practice; look up the real ones.",
   r'''def cost(input_tokens, output_tokens, in_price, out_price):
    return input_tokens / 1_000_000 * in_price + output_tokens / 1_000_000 * out_price

print(cost(2000, 500, 3.0, 15.0))''', run=True,
   q=Q("What does this show?", r'''def cost(i, o, ip, op):
    return i / 1_000_000 * ip + o / 1_000_000 * op
print(round(cost(1_000_000, 0, 2.0, 10.0), 2))''', ["2.0", "12.0", "10.0"], "One million input tokens at 2.0 per million is 2.0. No output tokens, so no output cost.")),
 S("Ask for JSON, then parse it safely",
   "When your program needs the answer as data, tell the model to reply with JSON only. But models sometimes wrap it in a ```json fence or add chatter, so <b>never trust the reply</b>: strip the fence, parse inside <code>try/except</code>, and handle failure.",
   r'''import json

def parse_reply(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.startswith("json"):
            t = t[4:]
    try:
        return json.loads(t.strip())
    except ValueError:
        return None

print(parse_reply('{"a": 1}'))
print(parse_reply('```json\n{"a": 2}\n```'))
print(parse_reply("Sure! Here you go"))''', run=True,
   q=Q("What does this show?", r'''import json
def parse(t):
    try:
        return json.loads(t)
    except ValueError:
        return None
print(parse("not json"))''', ["None", "not json", "{}"], "json.loads fails with ValueError, the except branch runs, and the function returns None.")),
 S("Retry when the reply is bad",
   "If the reply cannot be parsed, add the bad reply and a correction to the conversation and ask again, a few times at most. Always cap the tries so a stubborn model cannot loop forever and burn money.",
   r'''import json

def ask_json(llm, question, max_tries=3):
    messages = [{"role": "user", "content": question}]
    for attempt in range(max_tries):
        reply = llm(messages)
        try:
            return json.loads(reply)
        except ValueError:
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "Return only valid JSON."})
    return None

replies = iter(["oops", '{"ok": true}'])
print(ask_json(lambda m: next(replies), "status?"))''', run=True,
   q=Q("What does this show?", r'''import json
def ask(llm, max_tries):
    for i in range(max_tries):
        try:
            return json.loads(llm())
        except ValueError:
            pass
    return "gave up"
print(ask(lambda: "bad", 2))''', ["gave up", "None", "bad"], "Every try failed, the loop ended, and the function returned the fallback text.")),
 S("The context window has a limit",
   "A model can only read so many tokens at once (its <b>context window</b>). A long chat must be trimmed: keep the system message and the most recent turns, drop the middle. Models also follow instructions better when the history is short and relevant.",
   r'''def trim(messages, keep_last):
    system = [m for m in messages if m["role"] == "system"]
    rest = [m for m in messages if m["role"] != "system"]
    return system + rest[-keep_last:]

msgs = [{"role": "system", "content": "s"}] + [{"role": "user", "content": str(i)} for i in range(5)]
print([m["content"] for m in trim(msgs, 2)])''', run=True,
   q=Q("What does this show?", r'''xs = [1, 2, 3, 4, 5]
print(xs[-2:])''', ["[4, 5]", "[1, 2]", "[2, 3]"], "A slice from -2 takes the last two items. Trim uses the same idea.")),
 S("Your turn: ask for JSON with retries",
   "Combine messages, fence stripping and the capped retry loop. The model is passed in as a function, exactly like the fake above, so your code is testable.",
   q=W("Write <code>ask_json(llm, question, max_tries=3)</code>. Start with messages: a system message <code>{\"role\": \"system\", \"content\": \"Reply with JSON only.\"}</code> then a user message with the question. Call <code>llm(messages)</code>, which returns text. Strip spaces and any ``` fence (and a leading word json) from the reply, then parse it with <code>json.loads</code>. Success means it parses to a <b>dict</b>: return it. Otherwise append the bad reply as an assistant message and a user message <code>\"Return only valid JSON.\"</code> and try again. After <code>max_tries</code> failures return <code>None</code>.",
       "import json\n\ndef ask_json(llm, question, max_tries=3):\n    messages = []\n    # build messages, loop up to max_tries, parse safely\n    pass\n",
       "import json\n\ndef ask_json(llm, question, max_tries=3):\n    messages = [{\"role\": \"system\", \"content\": \"Reply with JSON only.\"}, {\"role\": \"user\", \"content\": question}]\n    for _ in range(max_tries):\n        reply = llm(messages)\n        t = reply.strip()\n        if t.startswith(\"```\"):\n            t = t.strip(\"`\")\n            if t.startswith(\"json\"):\n                t = t[4:]\n        try:\n            data = json.loads(t.strip())\n            if isinstance(data, dict):\n                return data\n        except ValueError:\n            pass\n        messages.append({\"role\": \"assistant\", \"content\": reply})\n        messages.append({\"role\": \"user\", \"content\": \"Return only valid JSON.\"})\n    return None",
       prelude="def make_llm(replies):\n    state = {'i': 0, 'seen': []}\n    def llm(messages):\n        state['seen'].append(len(messages))\n        r = replies[min(state['i'], len(replies) - 1)]\n        state['i'] += 1\n        return r\n    llm.state = state\n    return llm\n\ndef _go(replies):\n    llm = make_llm(replies)\n    res = ask_json(llm, 'q')\n    return [res, llm.state['seen']]\n",
       exprs=[("first reply is good", "_go(['{\"a\": 1}'])"), ("fenced reply", "_go(['```json\\n{\"a\": 2}\\n```'])"), ("one bad reply then good: messages grow by two", "_go(['nope', '{\"ok\": true}'])"), ("always bad stops after 3 tries", "_go(['x'])"), ("max_tries is respected", "ask_json(make_llm(['x']), 'q', max_tries=1)"), ("a JSON list is not a dict, so retry", "_go(['[1, 2]', '{\"b\": 3}'])")],
       hint="Loop for _ in range(max_tries). Inside: reply = llm(messages); clean it; try json.loads; if it is a dict return it. On failure append the two messages (the bad reply as assistant, then the correction as user).")),
]

# ------------------------------------------------------------------ Day 25
LESSONS[25] = [
 S("The problem RAG solves",
   "A model only knows what it was trained on. It has never read your company's PDFs. <b>RAG</b> (retrieval-augmented generation) fixes that in three steps: <b>retrieve</b> the few pieces of your documents most related to the question, paste them into the <b>prompt</b> (the text you send the model), and let the model <b>generate</b> an answer from them. You do not retrain anything.",
   r'''steps = ["1. split documents into chunks",
         "2. turn each chunk into numbers (embedding)",
         "3. find the chunks closest to the question",
         "4. put them in the prompt",
         "5. the model answers from them"]
for s in steps:
    print(s)''', run=True,
   q=QC("Why not paste the whole 500-page manual into every prompt?", ["It is too long and costly, and finding the relevant part helps the answer", "Models cannot read text", "It would change the model permanently"], 0, "Prompts have a size limit and every token costs money. Retrieval sends only what matters.")),
 S("Step 1: chunking",
   "A <b>chunk</b> is a small piece of a document, a paragraph or a few sentences. Too big and the retrieved text is mostly noise; too small and it loses its meaning. A simple method: take a fixed number of words per chunk, starting each next chunk where the last ended.",
   r'''def chunk_words(text, size):
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]

print(chunk_words("one two three four five six seven", 3))''', run=True,
   q=Q("What does this show?", r'''words = "a b c d e".split()
print([" ".join(words[i:i + 2]) for i in range(0, len(words), 2)])''', ["['a b', 'c d', 'e']", "['a b', 'c d']", "['a', 'b', 'c', 'd', 'e']"], "range(0, 5, 2) gives starts 0, 2, 4. The last chunk has one word left.")),
 S("Step 2: embeddings are meaning as numbers",
   "An <b>embedding</b> is a list of numbers that represents a piece of text, built so that texts with similar meaning get similar numbers. Real embeddings come from a model and have hundreds of numbers. To learn the logic we use a toy version: count how often each word of a small vocabulary appears. The real library call looks different; check the provider's docs.",
   r'''vocab = ["refund", "shipping", "days", "password"]

def embed(text):
    words = text.lower().split()
    return [words.count(v) for v in vocab]

print(embed("refund in 5 days"))
print(embed("reset your password"))''', run=True,
   q=Q("What does this show?", r'''vocab = ["a", "b"]
def embed(t):
    w = t.split()
    return [w.count(v) for v in vocab]
print(embed("a b a a"))''', ["[3, 1]", "[1, 3]", "[4]"], "a appears three times and b once, in vocabulary order.")),
 S("Step 3a: cosine similarity",
   "To compare two embeddings we use <b>cosine similarity</b>: it is 1 when they point the same way, 0 when they share nothing. The formula: the dot product (multiply matching numbers, add up) divided by the two lengths multiplied together. Lengths ignore how long the text is, only direction matters.",
   r'''import math

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

print(round(cosine([1, 2], [2, 4]), 3))
print(round(cosine([1, 0], [0, 1]), 3))''', run=True,
   q=Q("What does this show?", r'''import math
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return round(dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))), 3)
print(cosine([3, 0], [5, 0]))''', ["1.0", "0.0", "15.0"], "Both point along the same axis, so the angle is zero and the similarity is 1.")),
 S("Step 3b: top-k retrieval",
   "Embed the question, score every chunk against it, sort best first and keep the top <b>k</b>. Sorting is stable, so ties keep their original order.",
   r'''import math
vocab = ["refund", "shipping", "days", "password"]
def embed(t):
    w = t.lower().split()
    return [w.count(v) for v in vocab]
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)

chunks = ["refund takes 5 days", "shipping takes 2 days", "reset your password here"]
q = embed("how many days for refund")
ranked = sorted(chunks, key=lambda c: -cosine(q, embed(c)))
print(ranked[:2])''', run=True,
   q=Q("What does this show?", r'''scores = {"x": 0.2, "y": 0.9, "z": 0.5}
ranked = sorted(scores, key=lambda k: -scores[k])
print(ranked[:2])''', ["['y', 'z']", "['y', 'x']", "['x', 'y']"], "Sorting by negative score puts the highest first: y, z, x. Keep two.")),
 S("Step 4: building the prompt",
   "The prompt has three parts: an instruction, the retrieved chunks (numbered so the model can cite them), and the question. Telling the model to say it does not know when the context lacks the answer reduces made-up answers (called <b>hallucinations</b>).",
   r'''def build_prompt(question, chunks):
    lines = ["Answer using only the context. If the answer is not there, say \"I don't know\".", "", "Context:"]
    for i, c in enumerate(chunks, 1):
        lines.append("[" + str(i) + "] " + c)
    lines.append("")
    lines.append("Question: " + question)
    return "\n".join(lines)

print(build_prompt("When do refunds arrive?", ["Refunds take 5 days."]))''', run=True,
   q=Q("What does this show?", r'''chunks = ["a", "b", "c"]
print(len([f"[{i}] {c}" for i, c in enumerate(chunks, 1)]))''', ["3", "2", "4"], "One numbered line per chunk.")),
 Sd("Why RAG answers go wrong",
   "Check retrieval before blaming the model. Print the chunks that were retrieved. If the right chunk is not among them, the model never had a chance. Common causes: chunks cut in the middle of an idea, a poor embedding, k too small, or the answer simply is not in your documents. A good prompt tells the model what to do then.",
   "Question : What is the refund window?\nRetrieved: [1] Shipping takes 2 days.   <- wrong chunk\nAnswer   : \"I don't know\"      <- correct behaviour given the context",
   q=QC("The answer is wrong. What do you check first?", ["Whether the retrieved chunks contain the answer", "Whether the model is too small", "The colour of the user interface"], 0, "Garbage in, garbage out: if retrieval missed, no prompt can fix it.")),
 S("Your turn: a mini RAG pipeline",
   "Four small functions that together are the retrieval half of a real RAG system. The function <code>embed(text)</code> is provided: it returns a dict that counts each lowercase word (punctuation removed), such as {'refund': 1, 'days': 2}.",
   q=W("Write four functions. (1) <code>chunk_words(text, size)</code>: split on whitespace and return chunks of <code>size</code> words joined by one space. (2) <code>cosine(a, b)</code> for two count-dicts: sum of products over shared keys, divided by (length of a times length of b), where length is the square root of the sum of squared values; return <code>0.0</code> if either is empty. (3) <code>top_k(question, chunks, k)</code>: the k chunks most similar to the question using <code>embed</code> and <code>cosine</code>, best first, ties keep original order. (4) <code>build_prompt(question, chunks)</code> returning exactly these lines joined by newlines: <code>Answer using only the context. If the answer is not there, say \"I don't know\".</code>, an empty line, <code>Context:</code>, one line <code>[1] first chunk</code> and so on, an empty line, <code>Question: </code> followed by the question.",
       "import math\n\ndef chunk_words(text, size):\n    pass\n\ndef cosine(a, b):\n    pass\n\ndef top_k(question, chunks, k):\n    pass\n\ndef build_prompt(question, chunks):\n    pass\n",
       "import math\n\ndef chunk_words(text, size):\n    words = text.split()\n    return [\" \".join(words[i:i + size]) for i in range(0, len(words), size)]\n\ndef cosine(a, b):\n    dot = sum(v * b[k] for k, v in a.items() if k in b)\n    na = math.sqrt(sum(v * v for v in a.values()))\n    nb = math.sqrt(sum(v * v for v in b.values()))\n    if na == 0 or nb == 0:\n        return 0.0\n    return dot / (na * nb)\n\ndef top_k(question, chunks, k):\n    q = embed(question)\n    return sorted(chunks, key=lambda c: -cosine(q, embed(c)))[:k]\n\ndef build_prompt(question, chunks):\n    lines = [\"Answer using only the context. If the answer is not there, say \\\"I don't know\\\".\", \"\", \"Context:\"]\n    for i, c in enumerate(chunks, 1):\n        lines.append(\"[\" + str(i) + \"] \" + c)\n    lines.append(\"\")\n    lines.append(\"Question: \" + question)\n    return \"\\n\".join(lines)",
       prelude="def embed(text):\n    out = {}\n    for w in text.lower().split():\n        w = w.strip('.,?!\"')\n        if w:\n            out[w] = out.get(w, 0) + 1\n    return out\n\nDOCS = ['Refunds take 5 days.', 'Shipping takes 2 days.', 'Reset your password in settings.']\n",
       exprs=["chunk_words('a b c d e', 2)", "chunk_words('', 3)", "round(cosine({'a': 1, 'b': 2}, {'a': 2, 'b': 4}), 3)", "cosine({}, {'a': 1})", "round(cosine({'a': 1}, {'b': 1}), 3)", "top_k('how long do refunds take', DOCS, 1)", "top_k('reset password', DOCS, 2)[0]", "top_k('anything', DOCS, 0)", "build_prompt('When?', ['Refunds take 5 days.', 'Ships in 2 days.'])"],
       hint="chunk_words: slice words[i:i+size] for i in range(0, len(words), size). cosine: loop over keys of a that are also in b. top_k: sorted(chunks, key=lambda c: -cosine(embed(question), embed(c)))[:k].")),
]

# ------------------------------------------------------------------ Day 26
LESSONS[26] = [
 S("A tool is a function the model may ask for",
   "A model can only produce text. To let it act (look up an order, do arithmetic, search), you give it <b>tools</b>: ordinary functions you wrote. The model does not run them. It replies with a <b>tool call</b>: a request saying <i>please run this tool with these arguments</i>. Your code runs the function and sends the result back.",
   r'''def add(a, b):
    return a + b

def word_count(text):
    return len(text.split())

tools = {"add": add, "word_count": word_count}

call = {"name": "add", "args": {"a": 2, "b": 3}}      # what the model asked for
result = tools[call["name"]](**call["args"])
print(result)''', run=True,
   q=Q("What does this show?", r'''tools = {"wc": lambda text: len(text.split())}
call = {"name": "wc", "args": {"text": "one two three"}}
print(tools[call["name"]](**call["args"]))''', ["3", "13", "wc"], "The dict lookup finds the function and ** spreads the args into keyword arguments.")),
 Sd("Telling the model what tools exist",
   "The model needs a description of each tool: its name, what it does, and its parameters as a JSON schema. The names of the fields differ between providers. With Anthropic's API, one tool looks like this (check the docs for the current format). The description matters: it is how the model decides when to use the tool.",
   "{\n  \"name\": \"get_order_status\",\n  \"description\": \"Look up the status of an order by its id.\",\n  \"input_schema\": {\n    \"type\": \"object\",\n    \"properties\": {\"order_id\": {\"type\": \"string\"}},\n    \"required\": [\"order_id\"]\n  }\n}",
   q=QC("Which part tells the model WHEN to use a tool?", ["The description", "The file name", "The tool's return value"], 0, "The model reads the name and description to decide whether a tool fits the question.")),
 S("The agent loop",
   "An <b>agent</b> is a loop: ask the model; if it answers with text, stop; if it asks for a tool, run the tool, add the result to the conversation, and ask again. Below the model is a scripted fake so the loop is easy to follow.",
   r'''script = [
    {"type": "tool", "name": "add", "args": {"a": 2, "b": 3}},
    {"type": "text", "text": "The answer is 5"},
]
def fake_model(messages):
    return script[len([m for m in messages if m["role"] == "tool"])]

tools = {"add": lambda a, b: a + b}
messages = [{"role": "user", "content": "What is 2 + 3?"}]
while True:
    reply = fake_model(messages)
    if reply["type"] == "text":
        print(reply["text"])
        break
    result = tools[reply["name"]](**reply["args"])
    messages.append({"role": "tool", "name": reply["name"], "content": str(result)})
print(len(messages))''', run=True,
   q=Q("What does this show?", r'''messages = ["user question"]
for step in range(3):
    messages.append("tool result")
print(len(messages))''', ["4", "3", "1"], "One starting message and three appended tool results.")),
 S("The result goes back into the conversation",
   "After running a tool, you append its result as a message so the model sees it on the next call. Without that, the model would ask again forever. Convert the result to text with <code>str(...)</code>, since messages carry text.",
   r'''messages = [{"role": "user", "content": "Weather in Pune?"}]
tool_result = {"temp_c": 31}
messages.append({"role": "tool", "name": "get_weather", "content": str(tool_result)})
print(messages[-1]["content"])''', run=True,
   q=Q("What does this show?", r'''print(str({"a": 1}) + "!")''', ["{'a': 1}!", "a1!", "{\"a\": 1}!"], "str() of a dict uses Python's own notation, with single quotes.")),
 S("Tools fail, so catch it",
   "The model may ask for a tool that does not exist, or pass bad arguments, or the function may raise an error. Do not crash: return an error text as the tool result. The model usually reads it and corrects itself.",
   r'''def run_tool(tools, name, args):
    if name not in tools:
        return "error: unknown tool"
    try:
        return str(tools[name](**args))
    except Exception:
        return "error: tool failed"

tools = {"div": lambda a, b: a / b}
print(run_tool(tools, "div", {"a": 6, "b": 3}))
print(run_tool(tools, "div", {"a": 1, "b": 0}))
print(run_tool(tools, "nope", {}))''', run=True,
   q=Q("What does this show?", r'''def run_tool(tools, name, args):
    try:
        return str(tools[name](**args))
    except Exception:
        return "error"
print(run_tool({"f": lambda x: x * 2}, "f", {}))''', ["error", "None", "0"], "Calling f with no argument raises TypeError, which the broad except turns into the text error.")),
 S("Always cap the steps",
   "A model can get stuck asking for the same tool forever, and every loop costs tokens and time. Always set a <b>max steps</b> limit and decide what to return when it is hit.",
   r'''def stubborn_model(messages):
    return {"type": "tool", "name": "ping", "args": {}}

calls = 0
for step in range(4):               # max_steps = 4
    reply = stubborn_model([])
    calls += 1
print("stopped after", calls)''', run=True,
   q=QC("Why does an agent loop need a maximum number of steps?", ["So a confused model cannot loop forever and burn money", "Because Python can only loop 4 times", "So the answer is shorter"], 0, "Models are not guaranteed to stop on their own. The cap is your safety net.")),
 S("Be careful what tools can do",
   "A tool that deletes files or sends email is dangerous: the model can be wrong, or text it reads (a web page, an email) can trick it into calling the tool. Give an agent the least power it needs, prefer read-only tools, and ask a human to approve actions that cannot be undone.",
   r'''SAFE = {"search", "read_file"}
NEEDS_APPROVAL = {"send_email", "delete_file"}

def allowed(name, approved=False):
    if name in SAFE:
        return True
    return name in NEEDS_APPROVAL and approved

print(allowed("search"), allowed("delete_file"), allowed("delete_file", True), allowed("format_disk", True))''', run=True,
   q=Q("What does this show?", r'''SAFE = {"read"}
RISKY = {"delete"}
def allowed(n, ok=False):
    return n in SAFE or (n in RISKY and ok)
print(allowed("delete"), allowed("delete", True))''', ["False True", "True True", "False False"], "delete needs approval: refused without it, allowed with it.")),
 S("Your turn: write the agent loop",
   "This is the heart of every agent framework, in about a dozen lines.",
   q=W("Write <code>run_agent(model, tools, question, max_steps=5)</code>. Start with <code>messages = [{\"role\": \"user\", \"content\": question}]</code>. Repeat up to <code>max_steps</code> times: call <code>model(messages)</code>, which returns either <code>{\"type\": \"text\", \"text\": ...}</code> or <code>{\"type\": \"tool\", \"name\": ..., \"args\": {...}}</code>. For text, return <code>{\"answer\": text, \"steps\": tool_calls_made}</code>. For a tool call, the result is <code>\"error: unknown tool\"</code> if the name is not in <code>tools</code>, <code>\"error: tool failed\"</code> if the function raises any exception, otherwise <code>str(result)</code>; append <code>{\"role\": \"tool\", \"name\": name, \"content\": result}</code> and loop. If the steps run out, return <code>{\"answer\": None, \"steps\": max_steps}</code>.",
       "def run_agent(model, tools, question, max_steps=5):\n    messages = [{\"role\": \"user\", \"content\": question}]\n    # loop up to max_steps times\n    pass\n",
       "def run_agent(model, tools, question, max_steps=5):\n    messages = [{\"role\": \"user\", \"content\": question}]\n    for step in range(max_steps):\n        reply = model(messages)\n        if reply[\"type\"] == \"text\":\n            return {\"answer\": reply[\"text\"], \"steps\": step}\n        name = reply[\"name\"]\n        if name not in tools:\n            result = \"error: unknown tool\"\n        else:\n            try:\n                result = str(tools[name](**reply[\"args\"]))\n            except Exception:\n                result = \"error: tool failed\"\n        messages.append({\"role\": \"tool\", \"name\": name, \"content\": result})\n    return {\"answer\": None, \"steps\": max_steps}",
       prelude="def make_model(call):\n    def m(messages):\n        if messages[-1]['role'] == 'user':\n            return call\n        return {'type': 'text', 'text': 'got: ' + messages[-1]['content']}\n    return m\n\ndef loop_model(messages):\n    return {'type': 'tool', 'name': 'add', 'args': {'a': 1, 'b': 1}}\n\nTOOLS = {'add': lambda a, b: a + b, 'div': lambda a, b: a / b}\n",
       exprs=[("answers directly with no tool", "run_agent(lambda m: {'type': 'text', 'text': 'hi'}, {}, 'q')"), ("one tool call then answer", "run_agent(make_model({'type': 'tool', 'name': 'add', 'args': {'a': 2, 'b': 3}}), TOOLS, 'q')"), ("unknown tool is reported", "run_agent(make_model({'type': 'tool', 'name': 'nope', 'args': {}}), TOOLS, 'q')"), ("a failing tool is reported", "run_agent(make_model({'type': 'tool', 'name': 'div', 'args': {'a': 1, 'b': 0}}), TOOLS, 'q')"), ("a model that never stops is cut off", "run_agent(loop_model, TOOLS, 'q', max_steps=3)"), ("max_steps=1 and a tool request", "run_agent(loop_model, TOOLS, 'q', max_steps=1)")],
       hint="for step in range(max_steps): reply = model(messages). If reply['type'] == 'text', return the dict with steps=step. Otherwise work out result (check the name, then try/except), append the tool message, and the loop continues.")),
]

# ------------------------------------------------------------------ Day 27
LESSONS[27] = [
 Sd("The problem: it works on my machine",
   "Your code depends on a Python version, installed libraries and settings. On another computer something differs and it breaks. <b>Docker</b> fixes this by packaging your app and everything it needs. An <b>image</b> is that package (a frozen recipe plus ingredients). A <b>container</b> is a running copy of an image. One image can run as many containers as you like. These are terminal commands; they run on a computer with Docker installed, not in this page.",
   "docker build -t myapp .              # make an image named myapp from the Dockerfile in this folder\ndocker run -p 8000:8000 myapp        # start a container, port 8000 outside -> 8000 inside",
   q=QC("What is the difference between an image and a container?", ["An image is the packaged recipe; a container is a running copy of it", "They are the same thing", "A container is a file on GitHub"], 0, "Build once to get an image, run it many times to get containers.")),
 Sd("A Dockerfile is the recipe",
   "A <b>Dockerfile</b> is a text file of instructions. <code>FROM</code> picks the base image to start with. <code>WORKDIR</code> chooses the folder inside. <code>COPY</code> copies files in. <code>RUN</code> runs a command while building (installing libraries). <code>CMD</code> is what runs when the container starts. This one packages a FastAPI app:",
   "FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]",
   q=QC("Which line installs your libraries?", ["RUN pip install ...", "FROM python:3.12-slim", "CMD [...]"], 0, "RUN executes a command at build time. CMD only runs when a container starts.")),
 S("Layers and the build cache",
   "Each instruction becomes a <b>layer</b>. Docker reuses (caches) a layer if that line and everything above it are unchanged, and rebuilds from the first changed line downward. Your code changes often; your requirements rarely. So copy <code>requirements.txt</code> and install <b>before</b> copying the code. Then a code edit skips the slow install. The model below counts how many layers get rebuilt.",
   r'''def rebuilt(old, new):
    """Layers from the first difference downward are rebuilt."""
    for i in range(len(new)):
        if i >= len(old) or old[i] != new[i]:
            return len(new) - i
    return 0

good = ["from", "copy reqs", "pip install", "copy code"]
print(rebuilt(good, ["from", "copy reqs", "pip install", "copy NEW code"]))''', run=True,
   q=Q("What does this show?", r'''def rebuilt(old, new):
    for i in range(len(new)):
        if i >= len(old) or old[i] != new[i]:
            return len(new) - i
    return 0
bad = ["from", "copy ALL", "pip install"]
print(rebuilt(bad, ["from", "copy ALL v2", "pip install"]))''', ["2", "1", "0"], "The change is at position 1, so layers 1 and 2 are rebuilt, including the slow install.")),
 Sd("Pin the version, drop root, add a health check",
   "Three habits of a good image. <b>Pin the version</b>: <code>python:3.12-slim</code>, never <code>latest</code>, so a rebuild next month does not silently change. <b>Do not run as root</b>: create a user and switch with <code>USER</code>, so a hacked app has little power. <b>HEALTHCHECK</b> lets Docker test whether the app really responds. The user is created and libraries installed before <code>USER</code>, because installing needs root.",
   "RUN useradd -m app\nUSER app\nHEALTHCHECK CMD python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\"",
   q=QC("Why add <code>USER app</code>?", ["If the app is attacked, it runs with limited rights instead of as root", "It makes the build faster", "It is required for Python to start"], 0, "Least privilege: a compromised process can only do what its user can.")),
 Sd("Secrets never go in the image",
   "Anything you <code>COPY</code> or write with <code>ENV</code> into an image can be read by anyone who gets the image. So API keys are passed when the container starts, from outside. Also add a <code>.dockerignore</code> file listing things not to copy (like <code>.env</code> and <code>.git</code>).",
   "docker run -p 8000:8000 -e API_KEY=your-key-here myapp\ndocker run -p 8000:8000 --env-file .env myapp",
   q=QC("Where should an API key be supplied?", ["When the container starts, for example with -e or --env-file", "Hard-coded in the Dockerfile", "Inside main.py"], 0, "Images get shared and stored in registries. Keys must stay outside them.")),
 S("Reading docker ps",
   "<code>docker ps</code> lists running containers as a table. Columns are separated by two or more spaces, but single spaces also appear inside a value (like <i>Up 5 minutes</i>), so a plain split would cut values apart. Splitting on two-or-more spaces with <code>re.split</code> works.",
   r'''import re
text = """CONTAINER ID   IMAGE        COMMAND   STATUS         NAMES
a1b2c3d4e5f6   myapp:1.0    "uvicorn" Up 5 minutes   api
f6e5d4c3b2a1   redis:7      "redis"   Exited (0)     cache"""
for line in text.splitlines()[1:]:
    parts = re.split(r"\s{2,}", line.strip())
    print(parts[-1], "|", parts[-2])''', run=True,
   q=Q("What does this show?", r'''import re
print(re.split(r"\s{2,}", "api   Up 5 minutes   web"))''', ["['api', 'Up 5 minutes', 'web']", "['api', 'Up', '5', 'minutes', 'web']", "['api   Up 5 minutes   web']"], "Only runs of two or more spaces separate; the single spaces in Up 5 minutes stay.")),
 Sd("Shipping it: registry and logs",
   "To run your image on a server you push it to a <b>registry</b> (a store for images, like Docker Hub), then the server pulls and runs it. Cloud services such as Render, Railway, Fly.io or AWS can run a container for you. When something fails, <code>docker logs</code> shows the app's output, which is where the Python error will be.",
   "docker tag myapp your-user/myapp:1.0\ndocker push your-user/myapp:1.0\ndocker logs api",
   q=QC("A container starts and instantly stops. What do you run first?", ["docker logs on the container, to read the error", "Delete Docker and reinstall", "Rewrite the app in another language"], 0, "Logs show the traceback, the same kind you learned to read on Day 5.")),
 S("Your turn: generate a Dockerfile and read docker ps",
   "Tools often generate Dockerfiles. Write one function that builds a correct Dockerfile string, and one that parses the table.",
   q=W("Write <code>make_dockerfile(version, port, module)</code> returning a string of these lines joined with newlines, in order: <code>FROM python:{version}-slim</code>, <code>WORKDIR /app</code>, <code>COPY requirements.txt .</code>, <code>RUN pip install --no-cache-dir -r requirements.txt</code>, <code>COPY . .</code>, <code>RUN useradd -m app</code>, <code>USER app</code>, <code>EXPOSE {port}</code>, a HEALTHCHECK line that is <code>HEALTHCHECK CMD python -c \"import urllib.request; urllib.request.urlopen('http://localhost:{port}/health')\"</code>, and last <code>CMD [\"uvicorn\", \"{module}\", \"--host\", \"0.0.0.0\", \"--port\", \"{port}\"]</code>. Also write <code>parse_ps(text)</code>: skip the header line, split each row on two or more spaces, and return a list of dicts <code>{\"name\": last column, \"image\": second column, \"up\": True if the fifth column starts with Up}</code>.",
       "import re\n\ndef make_dockerfile(version, port, module):\n    pass\n\ndef parse_ps(text):\n    pass\n",
       "import re\n\ndef make_dockerfile(version, port, module):\n    lines = [\n        \"FROM python:\" + version + \"-slim\",\n        \"WORKDIR /app\",\n        \"COPY requirements.txt .\",\n        \"RUN pip install --no-cache-dir -r requirements.txt\",\n        \"COPY . .\",\n        \"RUN useradd -m app\",\n        \"USER app\",\n        \"EXPOSE \" + str(port),\n        \"HEALTHCHECK CMD python -c \\\"import urllib.request; urllib.request.urlopen('http://localhost:\" + str(port) + \"/health')\\\"\",\n        \"CMD [\\\"uvicorn\\\", \\\"\" + module + \"\\\", \\\"--host\\\", \\\"0.0.0.0\\\", \\\"--port\\\", \\\"\" + str(port) + \"\\\"]\",\n    ]\n    return \"\\n\".join(lines)\n\ndef parse_ps(text):\n    out = []\n    for line in text.splitlines()[1:]:\n        if not line.strip():\n            continue\n        parts = re.split(r\"\\s{2,}\", line.strip())\n        out.append({\"name\": parts[-1], \"image\": parts[1], \"up\": parts[4].startswith(\"Up\")})\n    return out",
       prelude="PS = 'CONTAINER ID   IMAGE       COMMAND     CREATED          STATUS          PORTS                    NAMES\\na1b2c3d4e5f6   myapp:1.0   \"uvicorn\"   5 minutes ago    Up 5 minutes    0.0.0.0:8000->8000/tcp   api\\nf6e5d4c3b2a1   redis:7     \"redis\"     2 hours ago      Exited (0)      6379/tcp                 cache'\n",
       exprs=[("first line is the pinned base image", "make_dockerfile('3.12', 8000, 'main:app').splitlines()[0]"), ("runs as non-root, after the install", "(lambda d: d.index('USER app') > d.index('RUN pip install'))(make_dockerfile('3.12', 8000, 'main:app'))"), ("requirements are copied before the code", "(lambda d: d.index('COPY requirements.txt') < d.index('COPY . .'))(make_dockerfile('3.11', 80, 'a:b'))"), ("has a health check on the chosen port", "'localhost:9000/health' in make_dockerfile('3.12', 9000, 'main:app')"), ("never latest", "'latest' not in make_dockerfile('3.12', 8000, 'main:app')"), ("last line", "make_dockerfile('3.12', 8000, 'api:app').splitlines()[-1]"), ("total lines", "len(make_dockerfile('3.12', 8000, 'api:app').splitlines())"), ("parse_ps rows", "parse_ps(PS)"), ("parse_ps with only a header", "parse_ps('CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES')")],
       hint="Build a list of lines with string concatenation and join with chr(10) or backslash n. For parse_ps use re.split(r'\\s{2,}', line.strip()) on every line after the first.")),
]

# ------------------------------------------------------------------ Day 28
LESSONS[28] = [
 Sd("System design is a conversation with a method",
   "An interviewer says <i>design a URL shortener</i>. There is no single right answer; they want to see you think. Use the same six steps every time: (1) <b>requirements</b>: what must it do, and how many users? (2) <b>estimates</b>: rough numbers for traffic and storage. (3) <b>API</b>: the endpoints. (4) <b>data</b>: what you store and where. (5) <b>high-level design</b>: boxes and arrows. (6) <b>bottlenecks</b>: what breaks first, and how you fix it.",
   "1. Requirements   what must it do? how many users?\n2. Estimates      requests per second, storage\n3. API            POST /shorten, GET /{code}\n4. Data           code -> long url\n5. Design         client -> load balancer -> servers -> cache -> database\n6. Bottlenecks    reads are 100x writes, so cache them",
   q=QC("What should you do first when given a system design question?", ["Ask questions to pin down requirements and scale", "Draw the database schema", "Name the technologies you will use"], 0, "Designing before knowing the requirements is the most common way to fail this round.")),
 S("Back-of-envelope: requests per second",
   "A day has 86,400 seconds, call it about 100,000. So requests per second (<b>QPS</b>) is requests per day divided by 86,400. Traffic is not flat, so designs plan for a <b>peak</b> of 2 to 3 times the average.",
   r'''daily_users = 10_000_000
requests_per_user = 5
per_day = daily_users * requests_per_user
qps = per_day / 86_400
print(round(qps))
print(round(qps * 3))        # peak''', run=True,
   q=Q("What does this show?", r'''per_day = 8_640_000
print(per_day // 86_400)''', ["100", "10", "1000"], "8,640,000 divided by 86,400 is exactly 100 requests per second.")),
 S("Back-of-envelope: storage",
   "Storage = number of items times size of each item, then times how long you keep them. Convert units carefully: 1 KB is about 1,000 bytes, 1 MB about a million, 1 GB about a billion, 1 TB about a trillion.",
   r'''new_links_per_day = 1_000_000
bytes_each = 500
years = 5
total_bytes = new_links_per_day * bytes_each * 365 * years
print(total_bytes / 1e9, "GB")''', run=True,
   q=Q("What does this show?", r'''print(2_000_000 * 1_000 / 1e9)''', ["2.0", "2000.0", "0.2"], "Two million items of 1,000 bytes is 2 billion bytes, which is 2 GB.")),
 S("A cache makes repeated reads cheap",
   "A <b>cache</b> is a small, fast store in front of a slow one, such as memory in front of a database. On a read: look in the cache; a <b>hit</b> returns at once; a <b>miss</b> fetches from the database and saves the answer for next time. The hit rate decides how much load the database sees. Watch out for stale data: cached values can be old, so entries usually get a time limit.",
   r'''database = {"a": 1, "b": 2}
cache = {}
hits = 0
misses = 0

def read(key):
    global hits, misses
    if key in cache:
        hits += 1
        return cache[key]
    misses += 1
    cache[key] = database[key]
    return cache[key]

for k in ["a", "a", "b", "a"]:
    read(k)
print(hits, misses)''', run=True,
   q=Q("What does this show?", r'''cache = {}
hits = 0
for k in ["x", "y", "x", "x", "y"]:
    if k in cache:
        hits += 1
    else:
        cache[k] = 1
print(hits)''', ["3", "2", "5"], "x and y are misses the first time. The other three reads are hits.")),
 S("Load balancer: many servers, one front door",
   "One server cannot handle unlimited traffic, and if it dies the site is down. A <b>load balancer</b> receives every request and spreads them over several identical servers. This works best when servers are <b>stateless</b> (they keep nothing between requests; data lives in the database or cache), because any server can then handle any request. The simplest policy is round-robin: take turns.",
   r'''servers = ["s1", "s2", "s3"]
for i in range(7):
    print("request", i, "->", servers[i % len(servers)])''', run=True,
   q=Q("What does this show?", r'''servers = ["a", "b"]
print(servers[5 % len(servers)])''', ["b", "a", "5"], "5 % 2 is 1, and position 1 is b.")),
 S("Scaling the database: replicas and shards",
   "Most apps read far more than they write. A <b>read replica</b> is a copy of the database that serves reads, leaving the main one for writes. When even that is too big, <b>sharding</b> splits the data across several databases by a rule, such as user id modulo the number of shards. A good rule spreads data evenly and lets you find any record's shard instantly.",
   r'''shards = 3
for user_id in [10, 11, 12, 13, 14]:
    print(user_id, "-> shard", user_id % shards)''', run=True,
   q=Q("What does this show?", r'''print(100 % 7)''', ["2", "14", "7"], "100 = 14 * 7 + 2, so the remainder is 2.")),
 S("Rate limiting: protect the server",
   "A <b>rate limiter</b> refuses a user who sends too many requests, so one client (or attacker) cannot hog the service. The simple fixed-window version counts requests per user per time window. Its weakness: a user can send the full allowance at the end of one window and again at the start of the next. A <b>sliding window</b> counts only requests from the last N seconds and avoids that.",
   r'''class FixedWindow:
    def __init__(self, limit, window):
        self.limit, self.window, self.counts = limit, window, {}

    def allow(self, user, now):
        key = (user, now // self.window)
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key] <= self.limit

r = FixedWindow(2, 10)
print([r.allow("u", t) for t in [0, 1, 2, 9, 10]])''', run=True,
   q=QC("A fixed window allows 100 requests per minute. A client sends 100 at 0:59 and 100 at 1:00. What happened?", ["200 requests in two seconds were allowed, a burst the limit meant to stop", "The second batch was blocked", "Nothing, 200 per minute is the limit"], 0, "Two different windows, each under its own limit. That edge burst is why sliding windows exist.")),
 S("Your turn: a sliding-window rate limiter",
   "Build the better limiter as a class, the way interviewers ask for it.",
   q=W("Write a class <code>RateLimiter</code> with <code>__init__(self, limit, window)</code> and <code>allow(self, user, now)</code>. <code>allow</code> returns True if the user has made fewer than <code>limit</code> accepted requests in the last <code>window</code> seconds (a request at time t counts if <code>now - t &lt; window</code>), and then records this request. If the answer is False, the request is not recorded. Each user is counted separately.",
       "class RateLimiter:\n    def __init__(self, limit, window):\n        pass\n\n    def allow(self, user, now):\n        pass\n",
       "class RateLimiter:\n    def __init__(self, limit, window):\n        self.limit = limit\n        self.window = window\n        self.log = {}\n\n    def allow(self, user, now):\n        times = [t for t in self.log.get(user, []) if now - t < self.window]\n        if len(times) >= self.limit:\n            self.log[user] = times\n            return False\n        times.append(now)\n        self.log[user] = times\n        return True",
       prelude="def _seq(limit, window, calls):\n    r = RateLimiter(limit, window)\n    return [r.allow(u, t) for u, t in calls]\n",
       exprs=[("three quick requests, limit 2", "_seq(2, 10, [('u', 0), ('u', 1), ('u', 2)])"), ("old requests expire", "_seq(2, 10, [('u', 0), ('u', 1), ('u', 2), ('u', 10)])"), ("rejected requests are not counted", "_seq(1, 10, [('u', 0), ('u', 5), ('u', 9), ('u', 10)])"), ("users are separate", "_seq(1, 10, [('a', 0), ('b', 0), ('a', 1), ('b', 1)])"), ("no burst at the window edge", "_seq(2, 10, [('u', 8), ('u', 9), ('u', 10), ('u', 11)])"), ("limit of zero blocks all", "_seq(0, 10, [('u', 0)])")],
       hint="Keep self.log as a dict from user to a list of accepted times. In allow, first keep only times where now - t < window. If the count has reached the limit, return False. Otherwise append now and return True.")),
]

# ------------------------------------------------------------------ Day 29
LESSONS[29] = [
 Sd("Pick a project small enough to finish",
   "Today you build something you can show. The rule: <b>one user, one job</b>. Finishing a small project beats half-finishing a big one. A good capstone for this course: <b>Document Q&amp;A API</b>, a web service where someone sends a question and gets an answer found in your own documents, with the sources shown. It uses almost everything from this course: Python, files, FastAPI, retrieval, a model call, tests, Docker and git.",
   "Project : Document Q&A API\nUser    : someone who has a folder of notes\nJob     : ask a question, get an answer plus where it came from\nNot now : login, a fancy web page, multiple users",
   q=QC("Which is the better first scope?", ["Answer questions from one folder of text files, nothing else", "A chatbot with login, payments and voice", "A search engine for the whole internet"], 0, "A narrow first version can actually be finished and demonstrated.")),
 Sd("The shape of the system",
   "Four pieces. A <b>loader</b> reads your text files and chunks them. A <b>retriever</b> finds the best chunks for a question. An <b>answerer</b> builds the prompt and calls the model (a fake one while testing). An <b>API</b> wraps it all: <code>POST /ask</code> with a question, returning an answer and sources. Keep each piece a separate small function so you can test it alone.",
   "files -> loader -> chunks\nquestion -> retriever -> best chunks -> answerer (prompt + model) -> answer\n                                           ^\n                                POST /ask  (FastAPI)",
   q=QC("Why keep the loader, retriever and answerer as separate functions?", ["Each can be tested and fixed alone", "Python forbids long functions", "It makes the model smarter"], 0, "When one piece breaks you know where to look, and you can replace one piece (a better retriever) without touching the rest.")),
 Sd("Build in thin slices",
   "Never build all of one layer and then the next. Build the smallest version that works from start to end, then improve it. Commit to git after every working step.",
   "Step 1  fixed text in code -> function returns the best chunk          (commit)\nStep 2  load .txt files from a folder, chunk them                      (commit)\nStep 3  fake model builds an answer from the chunks                    (commit)\nStep 4  wrap in FastAPI: POST /ask returns JSON                        (commit)\nStep 5  tests for the retriever and for bad input                      (commit)\nStep 6  Dockerfile, README, push to GitHub                             (commit)",
   q=QC("What should the very first working version do?", ["Run end to end in the simplest possible way, even with fixed data", "Handle every edge case", "Use the most advanced model available"], 0, "A working skeleton shows you where the real problems are. Polish comes after.")),
 S("Decide the JSON contract first",
   "The <b>contract</b> is the exact shape of what the API receives and returns. Writing it first lets you build the API, a test and a client at the same time without arguing later. For our project the response has a non-empty <code>answer</code> and a list of <code>sources</code>, each with the document name and a similarity score between 0 and 1.",
   r'''import json
response = {
    "answer": "Refunds take 5 working days.",
    "sources": [
        {"doc": "refunds.txt", "score": 0.82},
        {"doc": "shipping.txt", "score": 0.31},
    ],
}
print(json.dumps(response, indent=2))''', run=True,
   q=Q("What does this show?", r'''response = {"answer": "x", "sources": [{"doc": "a.txt", "score": 0.5}]}
print(response["sources"][0]["doc"])''', ["a.txt", "x", "0.5"], "sources is a list; the first item is a dict; its doc key holds the name.")),
 S("Test the unhappy paths",
   "Anyone can test the happy path. Real users send an empty question, a huge one, or wrong JSON. Decide what each case returns (a clear 4xx message, not a crash), and write a test with <code>assert</code> for it. An <code>assert</code> stops with an error when its condition is False, and is silent when True. In a real project you put these in a file and run them with <code>pytest</code>.",
   r'''def validate_question(q):
    if not isinstance(q, str) or not q.strip():
        return "question must be a non-empty string"
    if len(q) > 500:
        return "question is too long"
    return None

assert validate_question("") == "question must be a non-empty string"
assert validate_question("ok?") is None
assert validate_question("x" * 501) == "question is too long"
print("all tests passed")''', run=True,
   q=Q("What does this show?", r'''def f(n):
    return n * 2
assert f(2) == 4
print("fine")''', ["fine", "Error", "4"], "The assert is True, so nothing happens and the next line prints.")),
 Sd("A README is part of the product",
   "A recruiter or interviewer often reads only the README. It must answer, in under a minute: what is this, how do I run it, what does it look like, how does it work. Put a short example request and response near the top.",
   "# Document Q&A API\n\n## Overview\nOne sentence: what it does and for whom.\n\n## Setup\npip install -r requirements.txt\n\n## Usage\ncurl example request and the JSON response\n\n## Architecture\nloader -> retriever -> answerer -> API (a small diagram)\n\n## Tests\nHow to run them\n\n## Limits and next steps\nHonest list of what it does not do",
   q=QC("Which README line is most helpful to a first-time reader?", ["An example request and response", "A list of every library version", "The history of how you chose the project name"], 0, "Seeing it work on the page proves that it works and how to use it.")),
 Sd("Show it, do not just describe it",
   "Prepare a two-minute demo. Say the problem in one sentence, run one real request, point to the sources in the answer, and name one thing that went wrong and how you fixed it. That last part shows engineering judgement. Be ready for three questions: why this design, what would break at 100 times the users (use Day 28), and what you would improve next.",
   "Demo script (2 minutes)\n1. The problem, one sentence\n2. Run: curl a question, show the JSON answer with sources\n3. Show a wrong or empty case and how it is handled\n4. One bug you hit and how you found it\n5. What you would do with another week",
   q=QC("What makes a project demo convincing?", ["A live working request plus an honest account of a problem you solved", "A long list of buzzwords", "Showing only the code, never running it"], 0, "Working output builds trust; a solved problem shows you can debug.")),
 S("Your turn: validate the contract",
   "Your API's tests should check every response against the contract. Write that checker.",
   q=W("Write <code>validate_contract(resp)</code> returning a list of problem strings (an empty list means valid). If <code>resp</code> is not a dict return <code>[\"response must be an object\"]</code> and stop. Otherwise: if <code>answer</code> is missing or not a non-empty string (ignoring spaces) add <code>\"answer must be a non-empty string\"</code>. If <code>sources</code> is missing or not a list add <code>\"sources must be a list\"</code>; otherwise for each source with zero-based position <code>i</code> that is not a dict with a string <code>doc</code> and a <code>score</code> that is an int or float (not bool) between 0 and 1 inclusive, add <code>\"source i is invalid\"</code> (with the number in place of i). Problems are listed in the order found.",
       "def validate_contract(resp):\n    problems = []\n    # check the type, then answer, then sources\n    return problems\n",
       "def validate_contract(resp):\n    if not isinstance(resp, dict):\n        return [\"response must be an object\"]\n    problems = []\n    ans = resp.get(\"answer\")\n    if not isinstance(ans, str) or not ans.strip():\n        problems.append(\"answer must be a non-empty string\")\n    src = resp.get(\"sources\")\n    if not isinstance(src, list):\n        problems.append(\"sources must be a list\")\n    else:\n        for i, s in enumerate(src):\n            ok = isinstance(s, dict) and isinstance(s.get(\"doc\"), str)\n            if ok:\n                sc = s.get(\"score\")\n                ok = (not isinstance(sc, bool)) and isinstance(sc, (int, float)) and 0 <= sc <= 1\n            if not ok:\n                problems.append(\"source \" + str(i) + \" is invalid\")\n    return problems",
       exprs=["validate_contract({'answer': 'Yes', 'sources': [{'doc': 'a.txt', 'score': 0.5}]})", "validate_contract({'answer': 'Yes', 'sources': []})", "validate_contract([1])", "validate_contract({})", "validate_contract({'answer': '  ', 'sources': 'a.txt'})", "validate_contract({'answer': 'x', 'sources': [{'doc': 'a', 'score': 1.5}, {'doc': 'b', 'score': 0}, {'score': 0.2}, {'doc': 'c', 'score': True}]})"],
       hint="Return early for a non-dict. Build problems in order: answer first, then sources. For each source use enumerate(sources) and a single ok flag.")),
]

# ------------------------------------------------------------------ Day 30
LESSONS[30] = [
 Sd("What an interview day looks like",
   "Rounds vary, but for engineering roles expect: a <b>coding round</b> (solve a problem live while talking), a <b>system design or AI-system round</b> (Day 28 method), a <b>project deep dive</b> (your capstone), and a <b>behavioural round</b> (stories about how you work). Today you practise the habits that apply to all of them.",
   "Round 1  coding        30-45 min  one or two problems, talk while you type\nRound 2  design        45 min     whiteboard-style conversation\nRound 3  project dive  30 min     explain your capstone, trade-offs\nRound 4  behavioural   30 min     stories: conflict, failure, impact",
   q=QC("In a live coding round, what are the interviewers mostly judging?", ["How you think, communicate and test, not only the final answer", "How fast you type", "Whether you remember every library function"], 0, "Looking things up is normal. Clear thinking out loud is the skill being measured.")),
 Sd("The six moves for any coding question",
   "Do these in order, every time. (1) <b>Restate</b> the problem in your own words. (2) <b>Clarify</b>: input sizes, empty input, duplicates, negative numbers. (3) Say the <b>brute force</b> solution, even if slow. (4) <b>Optimise</b>: which Day 4 to Day 18 pattern fits (set, dict count, two pointers, sort)? (5) <b>Test</b> with a small example and edge cases, by hand. (6) <b>Communicate</b> the time and space cost. A slow correct answer said clearly beats silence.",
   "1 Restate    \"So I get a list and a target, and return two positions that add up to it?\"\n2 Clarify    \"Can the list be empty? Can I reuse the same element?\"\n3 Brute      \"Check every pair: O(n squared).\"\n4 Optimise   \"Keep a dict of numbers seen so far: O(n).\"\n5 Test       \"[2,7,11], target 9 -> [0,1]. Empty list -> no answer.\"\n6 Complexity \"Time O(n), extra space O(n).\"",
   q=QC("You are handed a problem you have never seen. What is the best first move?", ["Restate it and ask clarifying questions", "Start typing code at once", "Say you do not know it"], 0, "Restating catches misunderstandings early and buys thinking time.")),
 S("Brute force first, then improve",
   "Both versions below solve the same problem: do two numbers in a list add to the target? The brute force checks every pair. The faster one remembers numbers already seen. Saying both, and why the second is faster, is the interview answer.",
   r'''def pair_slow(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False

def pair_fast(nums, target):
    seen = set()
    for n in nums:
        if target - n in seen:
            return True
        seen.add(n)
    return False

print(pair_slow([2, 7, 11], 9), pair_fast([2, 7, 11], 9))
print(pair_slow([1, 2], 10), pair_fast([1, 2], 10))''', run=True,
   q=Q("What does this show?", r'''def pair_fast(nums, target):
    seen = set()
    for n in nums:
        if target - n in seen:
            return True
        seen.add(n)
    return False
print(pair_fast([5], 10))''', ["False", "True", "5"], "A single 5 is not paired with itself: when 5 is checked, seen is still empty.")),
 S("Count the work",
   "To state complexity, count how the number of steps grows with the input size n. One loop over n items is O(n). A loop inside a loop is O(n squared). A set or dict lookup is about O(1). Halving each step (binary search) is O(log n). Counting steps in code confirms your reasoning.",
   r'''def steps_nested(n):
    count = 0
    for i in range(n):
        for j in range(n):
            count += 1
    return count

print(steps_nested(10), steps_nested(20))''', run=True,
   q=Q("What does this show?", r'''count = 0
for i in range(5):
    for j in range(i):
        count += 1
print(count)''', ["10", "25", "5"], "The inner loop runs 0, 1, 2, 3, 4 times, which adds up to 10.")),
 S("Test your own code before they do",
   "Before saying done, run your function on: the normal case, the <b>empty</b> input, a <b>single</b> item, <b>duplicates</b>, and the extreme (very large, very small, negative). Say them aloud. Interviewers love it when you find the bug first.",
   r'''def second_largest(nums):
    unique = sorted(set(nums))
    return unique[-2] if len(unique) >= 2 else None

tests = [([3, 1, 2], 2), ([5, 5, 5], None), ([], None), ([7], None), ([1, 9, 9], 1)]
for nums, want in tests:
    print(nums, second_largest(nums) == want)''', run=True,
   q=Q("What does this show?", r'''def second_largest(nums):
    unique = sorted(set(nums))
    return unique[-2] if len(unique) >= 2 else None
print(second_largest([4, 4, 9]))''', ["4", "9", "None"], "The distinct values are 4 and 9, so the second largest is 4.")),
 Sd("When you are stuck or get an error",
   "Silence feels like failure, but narrating helps. If you get an error, read the <b>last line first</b> (Day 5), say what it means, and point to the line. If you are stuck, go back a step: restate, try a tiny example by hand, or solve an easier version. Ask for a hint if you have tried for a few minutes; asking well is a skill too.",
   "\"I see a KeyError on line 6, so that key was not in the dict.\n I'll use .get with a default of 0.\"\n\n\"I'm stuck on the optimise step. Let me try the example\n [3, 1, 2] by hand and see what I would remember.\"",
   q=QC("Your code raises an error in the interview. What helps most?", ["Read the last line aloud, explain what it means, and fix that line", "Delete everything and restart", "Stay silent until you find it"], 0, "Reading the error calmly and narrating shows exactly the skill the job needs.")),
 Sd("Behavioural questions: tell a story with the STAR shape",
   "Questions like <i>tell me about a time something went wrong</i> want a short story: <b>Situation</b> (one sentence of context), <b>Task</b> (what you had to do), <b>Action</b> (what YOU did, the longest part), <b>Result</b> (the outcome, with a number if possible, and what you learned). Prepare four stories in advance and reuse them: a conflict, a failure, a time you led, and a project you are proud of.",
   "S  \"Our release scanner flagged false alarms and engineers stopped trusting it.\"\nT  \"I owned the fix as the product manager.\"\nA  \"I sorted 200 alerts by cause, found three that made up most of the noise, and wrote the rules to remove them with the team.\"\nR  \"False alarms fell by about half, and adoption went up. I learned to start with the data.\"",
   q=QC("Which part of a STAR answer should be the longest?", ["Action: what you personally did", "Situation: the background", "Result: the thank-you"], 0, "Interviewers hire you for what you do, so spend most of the time there.")),
 S("Your turn: check a README",
   "Last task. Tools that review portfolios do simple checks like this one, and so should you, before sending a link.",
   q=W("Write <code>missing_sections(readme)</code>. The README is a string. A section exists if some line, after removing spaces at both ends, starts with <code>##</code> and its heading text (the rest of the line after the <code>#</code> marks, stripped and lowercased) equals the name. The required sections, in this order, are <code>overview</code>, <code>setup</code>, <code>usage</code>, <code>architecture</code>, <code>tests</code>. Return a list of the required names that are missing, in that order.",
       "def missing_sections(readme):\n    required = [\"overview\", \"setup\", \"usage\", \"architecture\", \"tests\"]\n    # collect the headings that are present, then return the missing ones\n    pass\n",
       "def missing_sections(readme):\n    required = [\"overview\", \"setup\", \"usage\", \"architecture\", \"tests\"]\n    found = set()\n    for line in readme.splitlines():\n        line = line.strip()\n        if line.startswith(\"##\"):\n            found.add(line.lstrip(\"#\").strip().lower())\n    return [r for r in required if r not in found]",
       exprs=["missing_sections('')", "missing_sections('## Overview\\n## Setup\\n## Usage\\n## Architecture\\n## Tests')", "missing_sections('# Title\\n## overview\\ntext\\n  ## SETUP  \\n## Usage')", "missing_sections('Overview\\nSetup')", "missing_sections('## Overview and goals\\n## Tests')"],
       hint="Make a set of headings: for each line, strip it, and if it starts with '##' take line.lstrip('#').strip().lower(). Then keep the required names not in the set.")),
]
