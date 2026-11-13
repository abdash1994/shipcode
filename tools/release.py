#!/usr/bin/env python3
"""Stamp the service-worker cache version from the shipped files, so every deploy that changes
index.html, qa.json or the fonts makes browsers fetch a new sw.js and show the 'new version' banner.
Run before every commit (the pre-commit hook installed by tools/install-hooks.sh does it)."""
import hashlib,re,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
h=hashlib.sha1()
for f in ["index.html","qa.json","manifest.webmanifest"]:
    h.update((root/f).read_bytes())
v="shipcode-"+h.hexdigest()[:10]
sw=root/"sw.js";t=sw.read_text()
n=re.sub(r'const V="shipcode-[0-9a-f]+"','const V="%s"'%v,t,count=1)
if n!=t:sw.write_text(n)
print(v,"(changed)" if n!=t else "(unchanged)")
