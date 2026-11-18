#!/usr/bin/env python3
"""Hygiene gate: the repo must carry no personal tokens.

Tokens are assembled from pieces so this file itself (and any file that
mentions the mechanism) can never match the pattern. Used by CI and by
tests/test_repo_hygiene.py.
"""

import os
import re
import sys

KIT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SELF = os.path.abspath(__file__)

# assembled at runtime — the literals never appear joined in this file
DENYLIST_TOKENS = [
    "/home/" + "fendi",
    "koper" + "asi",
    "ifc" + "news",
    "skrip" + "si",
    "UP" + "NVJ",
    "pot" + "eto",
    "pst" + "ack",
]
EXTS = (".md", ".py", ".yaml", ".yml", ".json", ".sh", ".mjs", ".txt")
PATTERN = re.compile("|".join(re.escape(t) for t in DENYLIST_TOKENS), re.I)


def find_violations(root: str):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", ".venv", "node_modules")]
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            if not fn.endswith(EXTS) or os.path.abspath(fp) == SELF:
                continue
            text = open(fp, encoding="utf-8", errors="ignore").read()
            for m in PATTERN.finditer(text):
                hits.append((os.path.relpath(fp, root), text[m.start():m.end()]))
    return hits


def main():
    hits = find_violations(KIT)
    for path, token in hits:
        print(f"FAIL {path}: {token!r}")
    print("hygiene:", "OK" if not hits else f"{len(hits)} violation(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
