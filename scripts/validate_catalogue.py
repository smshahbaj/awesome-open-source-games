#!/usr/bin/env python3
"""Validate catalogue consistency without requiring network access."""
import json, re, sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
readme=(root/"README.md").read_text(encoding="utf-8")
data=json.loads((root/"data/catalogue.json").read_text(encoding="utf-8"))

errors=[]
all_urls=[]
global_seen={}
for section, entries in data["entries"].items():
    seen=set()
    for e in entries:
        if not e["name"].strip() or not e["url"].startswith(("https://","http://")) or not e["description"].strip():
            errors.append(f"invalid {section} entry: {e}")
        if e["url"] in seen:
            errors.append(f"duplicate URL inside {section}: {e['url']}")
        seen.add(e["url"]); all_urls.append((section,e["url"]))
        if e["url"] in global_seen and global_seen[e["url"]] != section:
            errors.append(f"duplicate URL across sections: {e["url"]} ({global_seen[e["url"]]} / {section})")
        global_seen[e["url"]]=section


# Every local README link should point at a real file.
for target in re.findall(r'\[[^]]+\]\((?!https?://|#)([^)]+)\)',readme):
    path=target.split('#',1)[0]
    if path and not (root/path).exists():
        errors.append(f"missing local link target: {target}")

if errors:
    print("Catalogue validation failed:")
    print("\n".join(f"- {e}" for e in errors))
    sys.exit(1)

print("Catalogue OK:", ", ".join(f"{k}={len(v)}" for k,v in data["entries"].items()))
