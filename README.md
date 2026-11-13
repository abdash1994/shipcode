# ShipCode — 30-day coding trainer

A single-file web app (`index.html`) for moving from non-coder toward writing real Python and SQL, with interview practice for AI, data and solutions roles (a 30-day sprint, or a slower plan that fits your week). Tagline: **Break it into steps. Code it. Ship it.** It is built around one idea: freezing at a blank file is a breakdown problem, not a syntax problem. Every lab trains the same method, with help that fades week by week.

- **Live site:** https://shipcode-30.vercel.app (deployed from this repo on every push to main; progress is saved in your browser)
- **claude.ai version:** https://claude.ai/artifact/WZKB783PseCFNLfgnafibM (private; syncs progress across your devices)
- **Run it locally:** double-click `index.html` to open it in Chrome. It needs internet the first time a lab runs, to download Python and SQLite. Locally, progress is saved in that browser only.

## How a day works

1. **Warm-up** (10–20 min): drills you got wrong or are due for recall, plus up to two *redos from scratch* of labs you passed earlier (they come back after 2, 5, 12 and 30 days).
2. **Concept** (10 min): one short lesson and an example to type out.
3. **Drills** (10 min): syntax recall and error reading.
4. **Code labs** (60–90 min): real Python or SQL, run in the browser against tests, with real tracebacks. A day can't be completed until every lab passes.
5. **Hands-on** (2–3 hrs): LeetCode/HackerRank and build tasks, plus the "Done when" gate.

## Designed to keep you going

| Moment | What the app does |
|---|---|
| First open | A welcome that lists what is inside and sets honest expectations, then three choices: destination (SQL preselected, because it fits a 30-minute day), rhythm and time, and a start screen with an optional *why* and calendar reminder. Strict or flexible and days a week live on the time step; everything can be changed later at `#plan`. Test: `tests/e2e40.js`. |
| Every day | Opens on "After today you can…" and why it matters for an FDE, then a session card with one next action, time per part and a progress bar. |
| Short on time | Suggests a 20-minute minimum day that still counts. |
| Missed a day | One missed day a week doesn't break the streak. If you fall behind, it says that's normal and offers **Re-plan from here**, with no shaming. |
| Stuck in a lab | After 2 failed runs: a nudge on how to get unstuck, plus your own *why*. |
| Lab passed | Shows the time, a running count, and a special note for your first ever pass. |
| Day complete | A celebration screen: what you can now do, streak, days and labs, progress to the next level, a preview of tomorrow. |
| Week complete | A level-up (Python writer → Data wrangler → Problem solver → Interview-ready) and optional post-ready text to share your progress. |
| Path tab | Your level, stats, a 5-week practice heatmap, and every skill you've unlocked. |

## Updates reach installed users

`sw.js` carries a cache version stamped from the hash of `index.html`, `qa.json` and the manifest. `tools/release.py` does the stamping; run `sh tools/install-hooks.sh` once per clone so git does it before every commit. When a new version deploys, open tabs and installed copies check for it on return to the app, every 10 minutes and when back online, then show a "new version available, Refresh" bar. Progress lives in the browser and is not lost. Without the stamp a deploy would not trigger the bar, so do not commit with the hook off.

## AI-PM Q&A

A separate section (home tile, menu entry **AI-PM Q&A**, `#qa`) with 464 AI, system-design, technical and product interview questions and model answers, loaded on demand from `qa.json`. Search, topic and ★ filters, random question, and a private "I can answer this" tracker. It is optional and never blocks a day. A quiet footer on every page links to starring the repo and following on LinkedIn.

## Know where you stand: readiness, interview reps, error journal

- **Interview readiness** (Path tab): a score for each of 11 skill areas, built from evidence. Passing a lab is worth 40; passing without help +20; needing 2 or fewer failed runs +10; each redo from scratch +15 (up to 2). It's an estimate, not a guarantee. A "Practise weakest" button opens a rep in your weakest area.
- **Interview reps** (from Day 4): an unlabelled problem, with no title, no day and no technique hints, weighted toward weak areas. Name the pattern, explain your approach in 12+ words, then code from a blank editor against a target time (20 minutes for weeks 1–2, 35 after). Passing counts as a redo from scratch.
- **Error journal** (Errors tab): every error you hit is logged automatically, with a one-tap practice lab for the common ones.
- **Rebuild from scrambled lines**: after 2 failed runs, rebuild the solution from shuffled lines before the full solution unlocks (after 4 fails). Using a hint, the rebuild or the solution counts as help: the lab comes back sooner and scores lower until you redo it cleanly.

## See it, then watch your own code run

- **Watch it run** (every Python lab): step through your own code line by line, with the current line highlighted, every variable's value, changed values marked, and printed output. Pick which test to watch. Failing tests have a one-tap shortcut. Infinite loops are recorded up to 300 steps so you can see the repeat.
- **Quiz me**: inside Watch it run, the app pauses at key moments and asks what a variable will be next. Predicting before seeing is what makes it stick.
- **8 pattern diagrams** (Think tab, and on the matching days): hash map lookup, two pointers, sliding window, binary search, stack, recursion tree, BFS on a grid, SQL LEFT JOIN with IS NULL. Each is generated by running the real algorithm, step by step, with Play, Back and arrow keys.

## The method (Think tab)

Understand → solve one example by hand → write the steps as comments → code one comment at a time → test and debug.

| Weeks | Help in each lab |
|---|---|
| 1–2 (guided) | Predict the answer by hand, put the given steps in order, name the pattern. The editor opens with your plan as comments. |
| SQL days | Predict the row count from the tables, then fill in the clause recipe. |
| 3 | Name the pattern and write your own steps; code won't run until there are at least 3. |
| 4 and mocks | Solo: steps as comments, then code. A model breakdown appears after you pass. |

## The Gyms (the `Gyms` tab, `#gyms`)

Six gyms, each five levels that grow the way a job does: **write it, shape the data, make it correct, make it fast or scalable, decide and design**. Every level has a short lesson (all syntax and ideas shown first), graded labs, and a concept check. Routes: `#sql`, `#py`, `#spark`, `#sys`, `#dep`, `#ai`, and `#py-3` style for a level.

| Gym | Labs | What is real and what is simulated |
|---|---|---|
| SQL | 37 | Runs on SQLite in the browser; Level 4 plans are SQLite's, not a warehouse's. |
| Python | 31 | Real Python (Pyodide). Random-input tests against a reference on most labs. |
| PySpark | 21 | Levels 1 to 3 use real PySpark syntax on a pandas-based stand-in, not a cluster. Level 4 teaches partitions, shuffles, skew and broadcast by having you write the logic in plain Python. |
| System design | 17 | Levels 1 to 4 are code (sizing arithmetic, hash ring, idempotency, circuit breaker); Level 5 is three interview-style design exercises with keyword feedback and a model answer. |
| Deployment | 18 | Docker and cloud cannot run in a browser. You write parsers, linters, planners and decision rules, and practise design exercises. Real proof = deploy your own project (steps in Level 5). |
| AI engineering | 25 | The model is a function you pass in, so every behaviour is testable without an API key. Prices and provider syntax change: the labs say to check current docs. |

Content lives in `gym_py.py`, `gym_spark.py`, `gym_sys.py`, `gym_dep.py`, `gym_ai.py` (built on `gymlib.py`; expected values are computed from the reference solution), executed from `labs.py`. `check_g.py` runs every solution and starter, with the fuzz tests, in CPython.

## SQL Gym (the `SQL` tab, `#sql`)

Five levels, each with a short lesson, labs graded against a hidden second data set, and a concept quiz:
1. **Writing**: SELECT, WHERE, JOIN, GROUP BY. 2. **Analysing**: window functions, CTEs, subqueries, date truncation, CASE, rolling averages, ranking. 3. **Optimising**: NULL handling, UNION, execution order. 4. **Scaling**: indexes, EXPLAIN, partitions, cutting scan size and cost. 5. **Deciding**: funnels, cohorts, retention curves, experiment results.

Limits: Level 4 EXPLAIN labs run on SQLite, so they teach reading a plan, not a warehouse's. Partitioning and warehouse cost are a concept quiz and a written exercise, not runnable.

## Teach before testing

Each day's lesson shows the syntax its labs need (a "new today" card), and first-use drills are marked **new** with the syntax shown; recall drills come later. Day 28's terms are defined in the lesson. Worked examples differ from the labs, so copying the example does not pass. Drills run on several random inputs, so a fragile answer fails. Design answers credit plain-English wording.

## Phone path and the mini capstone

Day 1 can be done on a phone. Day 29 offers a smaller capstone with a starter project (a `.zip` with README, tests, Dockerfile and three TODOs). The Docker image has not been built or run by us; the tests were run with pytest.

## Tracks and the exam (`#exam`)

"Pro" is defined as a test. The exam is 12 problems you have never seen (4 SQL, 8 Python, half easier and half harder), 100 minutes, a blank editor and no hints. Pass: 9 of 12 solved without help. Three tracks are earned by parts of it, not by the calendar:

| Track | Planning estimate | Earned by |
|---|---|---|
| SQL, interview-strong | about 3 weeks | 3 of the 4 SQL problems |
| Python fundamentals | 30 days | 3 of the 4 easier Python problems |
| Python interview bar | 45 to 60 days | 9 of 12 overall and 3 of the 4 harder Python problems |

The durations are estimates, not measured on learners. The unseen bank is 39 problems; 24 are reserved for two exam forms (A and B) and never appear in interview reps, 6 are the before/after checks, and 9 feed the reps. From the third attempt, exam problems repeat. It is an honour-system self-test: the reference answers are readable in the page source.

## More practice, daily reps, dense days

- **14 optional Python labs on Days 15 to 21** (marked "Optional"): they never block a day, do not lower your readiness if skipped, and appear in the mixed reps.
- **Daily mixed reps**: a card on Today with a goal of three unlabelled problems a day, from Day 4.
- **Dense and survey days**: Days 12 and 13 are marked as two-sitting days. Days 23 to 27 are marked as survey days: the aim is one working example and a one-sentence explanation, not building from a blank file. The days are labelled, not split.

## A person and something to show

- **Weekly review** (`#review`): prepares a one-page sheet and a checklist for a friend, colleague or mentor. It cannot make the meeting happen; "I did the review" is an honour-system log.
- **Portfolio** (`#portfolio`): one card per finished day (what you can do, plus the code that passed), as copyable Markdown or a `.zip`. Code is kept on this device only.

## Measuring whether it works

`#report` shows your own numbers and exports a JSON file with no name or email. `PILOT-KIT.md` is a two-week, five-person pilot and `LEARNER-STUDY.md` the longer protocol and `tools/study_summary.py` computes the four measures from their files. **No real learner has used it yet.**

## What's inside `index.html`

| Part | Where to find it | What it holds |
|---|---|---|
| Styles | `<style>` at the top; tokens on `:root` | Light and dark colours, fonts, lab styles |
| Course content | `const DAYS = [...]` | 30 days: lesson, example, build, solve list, gate, drills |
| Code labs | `const LABS = {...}` | 65 labs keyed by day: task, starter, solution, hint, tests, and for Python labs the `pat` (pattern) and `steps` (breakdown) |
| Lab database | `const SEED` | The employees / customers / orders tables used by SQL labs |
| Test runner | `const HARNESS` | The Python code that runs your solution against the tests, formats tracebacks, stops infinite loops, and records each step for Watch it run (`_trace`) |
| Runtimes | `getPy()`, `getSql()` | Pyodide 0.29.4 and sql.js 1.13.0, loaded on first use. On the live link they load from the page's own `rt/` folder, because claude.ai only lets the page download from its own address. Opened as a local file, they load from cdn.jsdelivr.net. Open `#diag` on the live link to check the runner. |
| Progress and sync | `blank()`, `save()`, `merge()`, `connectCloud()` | Saved locally and to the claude.ai account; the newest change wins across devices |
| Screens | `renderToday`, `renderPath`, `renderThink`, `renderErrors`, `renderRef` | The five tabs |
| Lab player | `openLab`, `renderLab`, `runLab` | The by-hand → steps → pattern → code flow |
| Watch it run | `startTrace`, `stepperHTML`, `checkpoints` | The step-through view and the predict-the-value quiz |
| Readiness and reps | `AREAS`, `labScore`, `readinessCard`, `pickMixed`, `mixTask` | Skill areas, scoring, and unlabelled interview reps |
| Error journal and rebuild | `logErrors`, `journalCard`, `pzStart` | Automatic error log and the scrambled-lines step |
| Pattern diagrams | `const VIZ`, `openViz` | The 8 diagrams; each `build()` runs the algorithm to make its frames |

## Common changes

**Add a drill.** Add it at the **end** of a day's `drills` list. Drill IDs come from their position, so inserting in the middle shifts IDs and scrambles saved progress.

**Add a lab.** Add it at the end of that day's list in `LABS` (IDs are `L<day>-<index>`). A Python lab needs `tests` like `{"label": "...", "expr": "two_sum([3, 3], 6)", "want": "[0, 1]"}`, where `want` is a Python literal. A program that reads `input()` uses `{"label": "...", "stdin": ["3", "5"], "out": "8"}`. SQL labs need only a correct `solution`; learners' results are compared with its output. Before publishing, check that the solution passes every test and the starter fails at least one.

**Typed drill answers** are compared with all spaces removed, `"` treated as `'`, and a trailing `;` dropped. SQL answers are case-insensitive, and `LEFT OUTER JOIN` is treated as `LEFT JOIN`. A leading `return` or `name =` is also accepted unless the question asks for that name.

## Publishing changes to the live link

Ask Claude to update the app. For the live site, the change is pushed to `main` on GitHub and Vercel redeploys automatically. For the claude.ai version, the page is republished to https://claude.ai/artifact/WZKB783PseCFNLfgnafibM. Both keep their links, and saved progress carries over. The runtime files already published under `rt/` stay in place as long as the publish doesn't remove them. Python's standard library is published as `rt/pyodide/python_stdlib.wasm`, because the host doesn't serve `.zip` files.

## What changed on 11 Nov 2026

- **Typed drills are graded by running them.** 87 of the 95 "write the code" drills run your answer and a model answer on the same data and compare the result, so any correct way of writing it passes. The other 8 (git, docker, first-line-only answers) are still matched as text.
- **62 new recall drills** across Python, SQL, pandas and PySpark, so syntax gets practised daily and comes back in the warm-up.
- **pandas runs for real** in the browser (about 8 MB, loaded the first time a pandas lab or drill needs it). Three pandas labs on Day 12.
- **PySpark labs and drills run on a practice engine** (`pyspark` stand-in built on pandas) that accepts real PySpark syntax for filter, select, withColumn, groupBy/agg, join, orderBy, when/otherwise, fillna/dropna and friends. It is not Spark: no cluster and no lazy evaluation. Three labs on Day 13.
- **60-day plan** (2–3 hours a day) next to the 30-day plan and the 15-day sprint.
- Week 3 gate reworded to a target a learner can hit; LC 185 marked as a stretch.

## Added later on 11 Nov 2026

- **Unseen problems.** 13 problems (11 Python, 2 SQL) that never appear in a day's lab list. They only come up in interview reps, and unsolved ones are picked first, so a rep is usually a problem you have not met.
- **Proof of work.** On Days 22, 23, 27 and 29, paste your public GitHub link (and deployed URL where asked). The app checks the real repository through GitHub's public API: commits, README, `fastapi` in requirements, tests, a Dockerfile. The deployed-URL check only confirms that something answers at that address. Private repos can't be checked, and the check doesn't work inside claude.ai (outside requests are blocked there): use the live site.
- **Comeback mode.** After 3 or more missed days, Today opens with a small restart: 5 recall drills, one redo, a one-tap re-plan with the new finish date, and an option to switch to the 60-day plan. The backlog is spread over later days, oldest first.

## Your habit, your timeline (installable, any device)

The old problem: one big countdown ("2 years at 10 minutes a day") is a deal breaker before you start. The plan now bends **scope**, not just time.

- **Destination first.** Pick where to get first: SQL interview-strong (Days 8 to 11 plus the SQL Gym), Python you can write without help (Days 1 to 7), Python + SQL + pandas + PySpark (Days 1 to 14), Interview problem solver (Days 1 to 21), or Everything (30 days). You can extend the destination when you arrive; the plan only commits to the next stop. For SQL the order puts Days 8 to 11 first, and interview reps only use labs you have met.
- **Depth.** Core is everything the app grades (about 125 min per lesson, my estimate). Full adds about 150 min of editor and LeetCode-style practice (about 275 min). Completing a day never required the extra practice; the exam decides when you are done.
- **Rhythm.** Flexible (2 to 7 days a week, a missed day never resets the streak, dates just move) or strict (every day, daily streak, firm dates). Optional weekend deep block (1 to 4 hours, Saturday or Sunday) on top of small weekdays.
- **Dates, not durations.** The plan shows dated wins: first program passing, each quarter of the destination, the destination. Over 120 days the app says so, tells you not to plan the whole road, and offers Core depth, a closer destination or a weekend block.
- **Deadline mode.** Enter an interview date and the plan tells you what fits, or what to change.
- **Forecast from your real pace** appears after a week and compares with the plan.
- **Minutes plan on Today** for budgets under 4 hours: the next required parts that fit; an oversized part is time-boxed.
- **Reminders:** calendar file (.ics, with a second weekly event for the weekend block) or a Google Calendar link; browser notifications are not relied on.
- **Install:** `manifest.webmanifest` and `sw.js` (installable, offline shell; the Python and SQL engines are cached after first use).
- Change the plan any time at `#plan`. All minute figures (125, 275, SQL Gym 225, first win 45) are estimates, not measured with learners.

Examples (estimates): SQL, Core, 30 min on 5 days = 34 days; SQL, Core, 10 min on weekdays + a 2 h weekend block = 30 days; Everything, Full, 275 min every day = 30 days.

## The 30-day sprint

The default plan runs every track in parallel: each step is one course lesson plus one Gym level. SQL and Python run side by side from step 1; system design starts at step 5, AI engineering at step 10, PySpark at step 12 (after Python Level 2), deployment at step 22 (after Python Level 3). Soft warnings appear when a prerequisite level is under half done. `#sprint` shows the 30-step map, pace and week gates; `#capstone` is a milestone and enterprise-grade checklist.

Honest limits: time estimates (about 5,250 minutes at Core depth, roughly 3 hours a day) are my estimates, not measured with learners. Frontend is not taught, and Docker/cloud cannot run in the browser, so the capstone must be built in a real editor. Whether this reaches enterprise grade in 30 days depends on hours and prior experience.

## Interactive explainers

118 step-through explainers (about 100 new) cover almost every concept in the course days and the six Gyms: loops, references, joins, window functions, shuffles, call stacks, caching, queues, RAG, Docker layers and more. Each opens from the lesson's Concept card or the Gym level page, uses tiny worked examples computed in code, and asks you to **predict the next step first** before the answer shows. Numbers are labelled examples; tokenisers, hashes and vectors are toy stand-ins and say so on screen. They are for understanding; the labs are what build the skill of writing code from a blank editor.

## The Field Gym

A seventh gym for the work around the code that forward-deployed engineers do: understand a vague ask, read messy customer data and logs, debug a system you did not build, build integration glue (normalise, idempotent upsert, retries, reconcile), and communicate (incident updates, saying no, handover runbooks). 27 labs: code labs graded on real tests, plus written scenarios checked against a rubric and a model answer. In the sprint it adds one level on days 7, 14, 21, 28 and 30. Honest limit: scenarios are written; real customer practice has to happen with real people.

## Habit additions

Today now shows a **minimum day** card (5 minutes counts as a practice day), and strict mode gets **streak freezes**: one missed day is bridged automatically, you earn one per 7 practice days, and you can hold two. Flexible mode keeps its existing weekly rest day. There is no guilt messaging, no fake peers and no invented social proof by design.

## Updates reach installed copies

`sw.js` is rebuilt with a per-build hash, so browsers detect each new deploy and purge the old cache. Pages are fetched network-first; when a new version activates, a small "A new version is ready. Reload" bar appears (it never reloads on its own, so unsaved code is safe).

## Commitments (`#commit`)

All of these are the learner's own choices and stay on the device (they sync with progress):
- **If-then plan:** "After I ... I do my 5-minute minimum", shown on Today.
- **Own stake:** a promise written by the learner ("If I miss 2 days I will ..."). Nothing is enforced; the app shows the learner's own words back after the missed stretch.
- **Pause (up to 14 days):** streak is held, plan dates slide forward by the paused days, no comeback or behind-pace messaging while paused.
- **Milestone cards:** labs passed, streak, lessons, capstone items and each gym level, with real numbers; dismissible.

Deliberately not built: invented peers or fake social proof, escalating guilt messages, gaslighting copy and reverse-psychology prompts.

## Interface refresh

Adapted from a UI/UX review (Gemini), rebuilt in plain CSS/JS because the app is one static file, so the suggested React libraries (shadcn, Magic UI, Origin UI) don't apply.

- Bottom bar is 5 tabs (Today, Path, Gyms, Think, Errors). Reference moved to a book icon in the header that opens a slide-over with search and the cheat sheet. Inside a lab it opens on top without touching the editor. Ctrl/Cmd+K opens it too. The desktop sidebar still lists Reference.
- Streak pill shows this week as 7 dots (filled = practised, dashed = rest day used, ring = today). Tap it for the rule in words; the text follows flexible or strict mode.
- Header counters count up when they change (skipped with reduced motion).
- Today opens with a bento row: today's next lab with one Start button, this week, and the error to review.
- Path starts with a 30-day map. Nothing is locked.
- Errors: "Diagnose it first" (hint, root cause, fix open one at a time), the error list as accordions, "Drill this pattern" on rows that have a matching lab. Think's worked example opens step by step.
- Lab panes use hairline borders; passing all tests pulses the result once. Copy buttons on code blocks in Think and Errors.
- Fonts are self-hosted (Inter for text, JetBrains Mono for code, both SIL OFL; licences in `fonts/`), cached by the service worker, so they work offline. The old build loaded fonts from Google at run time.
- Optional colour-coded editor (CodeMirror 6): turn it on under Reference > Settings. It loads `cm/editor.js` (about 390 KB, about 137 KB gzipped) the first time a code lab opens, then works offline. The plain textarea stays the default, and the app falls back to it if the file fails to load. Rebuild steps are in `tools/cm/package.json`. Tested in Chromium with phone emulation only, not on real phone keyboards.
- Every row in the Errors list now has a drill button. The new labs are at the end of Python Gym level 3 (10 labs), PySpark Gym level 3 (1) and SQL Gym level 3 (1). Two differences from real life, stated in the labs: ShipCode's PySpark stand-in raises a KeyError listing the real columns instead of an AnalysisException, and SQLite does not raise the GROUP BY error, so that lab teaches the fix by wrong result.
- Not done: a full dark-surface re-skin, and Geist (one text font is enough).

## Your data
Progress lives only in the browser (localStorage). Reference > Settings has **Back up my progress** (downloads a JSON file), **Restore from backup** (asks before overwriting) and **Copy problem report** (browser info and the last 20 errors; no progress or code). Errors are kept in a local log (`shipcode.errlog`); nothing is sent to any server.

## Build-from-blank labs
`gym_build.py` appends 8 labs that ask for a whole small thing from a blank file, with only a behaviour spec and tests against fake dependencies that fail on purpose: a resilient LLM client, a mini RAG pipeline, a guarded tool-using agent, an eval harness (AI gym, levels 3 to 5); a small orders API with idempotency keys and a paginated rate-limit-aware fetcher (Field gym, level 4); a Dockerfile generator that must pass the Deployment gym's own linter (level 2); a pandas report from a messy export (Python gym, level 5). They run in the browser with fakes. Nothing here starts a real server, container or model call. Each was mutation-checked: a plausible wrong solution fails at least one test.

## Capstone contract check
Capstone studio (`#capstone`) has a **Contract check**: paste the address of your running FastAPI orders service (a deployed `https://` address, or `http://localhost:8000` while testing) and ShipCode calls it from your browser with 8 requests (health, create, two validation failures, get one, 404, idempotency key, list) and names the exact behaviours that fail. Your service must allow CORS. Days 27 and 29 repository checks also look inside the Dockerfile for a pinned base image, a non-root USER and a HEALTHCHECK. `tests/e2e30.js` runs the checker against a reference service in `tests/capapi/` (and three deliberately broken variants) in a real browser. Limits: the check needs a network path from the browser to your service, so it does not work inside claude.ai's artifact sandbox, and it checks behaviour, not code quality.

## Interview practice (`#interview`)
Three timed loops (60 minutes, four rounds each: scope a vague request, debug code you did not write, a business SQL question, a design talk) built on 12 problems that appear nowhere else (`tools/labs/iv.py`, checked by `check_iv.py`). Each round can be attempted once; hints and shown answers count as help. Below it, a peer mock interview: an interviewer script per loop, a five-line rubric scored 1 to 4, a copyable feedback message and a personal log. ShipCode cannot match partners or verify that a mock happened. The design rounds are checked by key ideas in a written summary, which is a rough check.

## What the app promises
Onboarding now states: SQL strong enough for interviews in about 3 weeks and Python fundamentals with easy-to-medium problems in 30 days, at 4 to 5 hours a day, as an estimate not yet measured with learners. Labels that implied an outcome ("Interview-ready", "forward-deployed-ready") were renamed.

## Accounts, sync, proof page, usage counts
Optional accounts (avatar in the header > Settings, or `#signup`, `#signin`, `#forgot`, `#reset`): email + password or an emailed sign-in link, password reset and change, and account deletion. Signing in syncs progress to a Supabase database; see `supabase/README.md` for the schema, the rules and the one-time dashboard setup. `#proof` publishes a public page (`#p-<code>`) with the learner's chosen name and progress numbers; it is labelled as a self-reported practice record, not a certificate. Usage counts are opt-in, asked once on Today and once more at the first error if declined. `tests/e2e32.js` covers all of it against an in-memory fake of the Supabase endpoints.

## Beginner sequence (lesson player)
Today shows one next step in order: lesson, drills, labs, hands-on, check. All 30 days have authored step-by-step lessons (`tools/labs/lessons.py` and `lessons_sql.py`, `lessons_py2.py`, `lessons_dsa.py`, `lessons_eng.py` (every SQL result is computed by running the query), verified by `check_lessons.py`): concept, runnable example, check question, then a write-it-yourself task graded by the real Python harness. Other days use a screen sequence generated from existing notes. Drills and labs stay locked until the earlier steps are done; "I already know this" unlocks them. Test: `tests/e2e33.js`.

## Pro track (after the 30 days)
31 modules in five tracks, opened from `#pro`: SQL Pro (writing data, indexes and plans, advanced querying, modelling, Postgres and warehouse differences, interview patterns), Python Pro (testing, real-project code, async, performance, statistics and ML basics for data scientists), Data Engineering Pro (Redis, batch pipelines, orchestration, Kafka-style streaming, warehouses, data quality), AI Engineering Pro (deep RAG, evals, MCP, production agents, LLM in production, FDE playbook), System Design Pro (framework, building blocks, data stores, queues, case studies, data/AI systems, drills). Source: `tools/labs/lessons_pro_*.py`; checked by `check_lessons.py` and `tests/e2e36.js`. Postgres, Redis, Kafka, Airflow, dbt and MCP cannot run in a browser: those modules teach the real commands as display-only text and practise the logic on pure-Python or SQLite models. Verify every real-tool example against current docs.

## App shell (settings, accounts, journey)
`#settings` holds profile, plan, theme (auto/light/dark), code-editor toggle, privacy and data, backup/restore and the danger zone. `#path` is a Duolingo-style journey: four units for Days 1-30 plus the Pro track, with a node sheet per day. Tests: `tests/e2e37.js` (uses an in-memory fake of the Supabase auth endpoints; no real accounts are created).

## Maker credit
A small "Built by" card (photo, LinkedIn, GitHub star, email) sits in Settings and at the end of the Path; a "Star" pill shows in the header from 700px up; one dismissible star request appears on Today after the first finished day and never returns after either choice. Visit `#owner` on your own device to switch the request off. Test: `tests/e2e38.js`. The photo is embedded as a 200px JPEG data URI.
