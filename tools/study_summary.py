#!/usr/bin/env python3
"""Summarise ShipCode learning reports (the .json files learners download from #report).

    python3 tools/study_summary.py reports/        # a folder of shipcode-report.json files

Prints the four measures from LEARNER-STUDY.md with the number of learners behind each one.
With fewer than about 10 learners these are anecdotes, not evidence."""
import json, sys, glob, os, statistics as st
from datetime import date

def load(path):
    files = sorted(glob.glob(os.path.join(path, "*.json"))) if os.path.isdir(path) else [path]
    out = []
    for f in files:
        try:
            r = json.load(open(f, encoding="utf-8"))
            if r.get("app") == "shipcode": out.append(r)
        except Exception as e:
            print("skipped", f, e, file=sys.stderr)
    return out

def d(s): return date.fromisoformat(s)

def main(path):
    R = load(path); n = len(R)
    print(f"Learners: {n}" + ("   (too few to conclude anything; treat as anecdotes)" if n < 10 else ""))
    if not n: return
    print("\n1. Completion")
    for day in (1, 7, 14, 30):
        k = sum(1 for r in R if day in r.get("done", []))
        print(f"   completed Day {day}: {k} of {n} ({round(100*k/n)}%)")
    gaps = []
    for r in R:
        if r.get("start") and "7" in r.get("doneOn", {}): gaps.append((d(r["doneOn"]["7"]) - d(r["start"])).days)
    if gaps: print(f"   calendar days from start to finishing Day 7: median {st.median(gaps)} (n={len(gaps)}); the plan assumes 7")

    print("\n2. Blank-file redo about a week later (the retention signal)")
    att = suc = 0
    for r in R:
        log = r.get("log", []); first = {}
        for e in log:
            if e["ev"] == "pass" and not e.get("redo") and e["id"] not in first: first[e["id"]] = e["d"]
        for e in log:
            if e["ev"] == "redo_open" and e["id"] in first:
                gap = (d(e["d"]) - d(first[e["id"]])).days
                if 6 <= gap <= 10:
                    att += 1
                    if any(p["ev"] == "pass" and p["id"] == e["id"] and p.get("blank") and p["d"] == e["d"] for p in log): suc += 1
    print(f"   attempts 6-10 days after first pass: {att}; passed from a blank editor without help: {suc}" + (f" ({round(100*suc/att)}%)" if att else ""))

    print("\n3. Before / after on problems never seen (3 each, no help)")
    pairs = [(r["checks"]["pre"], r["checks"]["post"]) for r in R if r.get("checks", {}).get("pre", {}).get("done") and r.get("checks", {}).get("post", {}).get("done")]
    sc = lambda c: sum(1 for v in c["res"].values() if v["ok"])
    if pairs:
        pre = [sc(a) for a, _ in pairs]; post = [sc(b) for _, b in pairs]
        print(f"   learners with both checks: {len(pairs)}; mean solved unaided before {st.mean(pre):.1f}/3, after {st.mean(post):.1f}/3, change {st.mean(post)-st.mean(pre):+.1f}")
        print("   Note: the two sets are different problems of similar type, not proven equal in difficulty.")
    else: print("   no learner has both checks yet")

    print("\n4. 'How would you feel if you could no longer use ShipCode?'")
    for k in ("d7", "d30"):
        a = [r["survey"][k]["fit"] for r in R if k in r.get("survey", {})]
        if a:
            v = sum(1 for x in a if x == "very")
            print(f"   {k}: very disappointed {v} of {len(a)} ({round(100*v/len(a))}%). A common rule of thumb treats about 40% as a sign of fit; it is a heuristic, not a verdict.")
        else: print(f"   {k}: no answers")
    hrs = {}
    for r in R:
        for k in ("d7", "d30"):
            h = r.get("survey", {}).get(k, {}).get("hrs")
            if h: hrs[h] = hrs.get(h, 0) + 1
    if hrs: print("   hours a day reported:", dict(sorted(hrs.items())), "(more hours is the biggest confound in any result)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
