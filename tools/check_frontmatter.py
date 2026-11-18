#!/usr/bin/env python3
"""CI gate: every skill's frontmatter is valid (name == dir, description <= 60)."""

import os
import re
import sys

KIT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SKILLS = os.path.join(KIT, "skills")
fail = 0
for name in sorted(os.listdir(SKILLS)):
    path = os.path.join(SKILLS, name, "SKILL.md")
    if not os.path.isfile(path):
        continue
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        print(f"FAIL {name}: no frontmatter"); fail += 1; continue
    kv = dict(re.findall(r"^([a-z_]+):\s*(.+)$", m.group(1), re.M))
    desc = kv.get("description", "").strip().strip('"')
    if kv.get("name") != name:
        print(f"FAIL {name}: frontmatter name={kv.get('name')!r} != dir"); fail += 1
    if len(desc) > 60:
        print(f"FAIL {name}: description {len(desc)} > 60 chars"); fail += 1
    if not desc:
        print(f"FAIL {name}: empty description"); fail += 1
print("frontmatter:", "OK" if not fail else f"{fail} problem(s)")
sys.exit(1 if fail else 0)
