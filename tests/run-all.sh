#!/bin/sh
# Runs every browser test in turn and prints one line per file (several minutes).
# Needs node + playwright (NODE_PATH), python3, and for e2e30 `pip install fastapi uvicorn`.
# e2e33-36 need the offline Python runtime at $SHIPCODE_RT (default /tmp/shipcode-rt, containing pyodide/ and sqljs/).
cd "$(dirname "$0")/.."
for t in tests/e2e*.js; do
  if ! grep -q "spawn(" "$t"; then python3 tests/serve.py & srv=$!; sleep 1; else srv=""; fi
  r=$(timeout 900 node "$t" 2>&1 | tail -1)
  [ -n "$srv" ] && kill $srv 2>/dev/null; pkill -f tests/serve.py 2>/dev/null
  echo "$t: $r"
done
