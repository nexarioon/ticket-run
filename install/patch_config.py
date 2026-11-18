#!/usr/bin/env python3
"""Merge or remove the kit's hook entries in a Hermes config.yaml.

Line-based and stdlib-only: the entries this kit owns are inserted after the
existing sub-keys, so a user's own hooks survive untouched. Adding is
idempotent (a second run writes nothing); removing is the exact inverse of
adding, so an uninstall restores the pre-install file byte for byte.
"""

import argparse
import json
import os
import shutil
import sys
import time

PRE_LLM = "ticket-rules.py"
GUARD = "tests-not-committed.py"


def _entry_llm(hookdir):
    return [f"    - command: {hookdir}/{PRE_LLM}", "      timeout: 5"]


def _entry_guard(hookdir):
    return ["    - matcher: terminal", f"      command: {hookdir}/{GUARD}", "      timeout: 15"]


def _section_span(lines, key):
    """(start, end) of a top-level `key:` block, or (None, None)."""
    start = None
    for i, line in enumerate(lines):
        if line.rstrip() == f"{key}:":
            start = i
            break
    if start is None:
        return None, None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        if lines[j] and not lines[j][0].isspace() and stripped and not stripped.startswith("#"):
            end = j
            break
    return start, end


def _sub_key(lines, start, end, name):
    for i in range(start + 1, end):
        if lines[i].rstrip() == f"  {name}:":
            return i
    return None


def _owned(lines):
    return sum(1 for l in lines if PRE_LLM in l or GUARD in l)


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return fh.read().splitlines(keepends=False)


def save(path, lines):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + ("\n" if lines else ""))


def add_entries(config_path, hookdir, dry_run=False):
    lines = load(config_path)
    if _owned(lines):
        print("kit entries already present; nothing to do")
        return 0
    backup = None
    if lines and not dry_run:
        backup = f"{config_path}.bak-ticketworkflow-{int(time.time())}"
        shutil.copy2(config_path, backup)
    start, end = _section_span(lines, "hooks")
    if start is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines += ["hooks:", "  pre_llm_call:"] + _entry_llm(hookdir)
        lines += ["  pre_tool_call:"] + _entry_guard(hookdir)
    else:
        i = _sub_key(lines, start, end, "pre_llm_call")
        if i is None:
            lines[start + 1:start + 1] = ["  pre_llm_call:"] + _entry_llm(hookdir)
            start += 2
        else:
            lines[i + 1:i + 1] = _entry_llm(hookdir)
        _, end = _section_span(lines, "hooks")
        j = _sub_key(lines, start, end, "pre_tool_call")
        if j is None:
            lines[start + 1:start + 1] = ["  pre_tool_call:"] + _entry_guard(hookdir)
        else:
            lines[j + 1:j + 1] = _entry_guard(hookdir)
    if dry_run:
        print("dry-run: would write", len(lines), "lines to", config_path)
        return 0
    save(config_path, lines)
    stamp_dir = os.path.join(os.path.dirname(config_path), "ticket-workflow")
    os.makedirs(stamp_dir, exist_ok=True)
    with open(os.path.join(stamp_dir, ".install-stamp.json"), "w", encoding="utf-8") as fh:
        json.dump({"backup": backup, "hookdir": hookdir,
                   "at": time.strftime("%Y-%m-%dT%H:%M:%S")}, fh, indent=1)
    print("added kit entries to", config_path)
    if backup:
        print("backup:", backup)
    return 0


def remove_entries(config_path, dry_run=False):
    lines = load(config_path)
    if not _owned(lines):
        print("no kit entries present")
        return 0
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("- command:") and (PRE_LLM in line or GUARD in line):
            i += 1
            while i < len(lines) and lines[i].strip().startswith("timeout:"):
                i += 1
            continue
        if line.strip() == "- matcher: terminal" and i + 1 < len(lines) and GUARD in lines[i + 1]:
            i += 2
            while i < len(lines) and lines[i].strip().startswith("timeout:"):
                i += 1
            continue
        out.append(line)
        i += 1
    # drop now-empty sub-keys: a two-space key whose next line is not a list
    # item (four spaces) owns nothing we (or the user) added
    trimmed, i = [], 0
    while i < len(out):
        line = out[i]
        if line.startswith("  ") and not line.startswith("    ") and line.rstrip().endswith(":"):
            nxt = out[i + 1] if i + 1 < len(out) else ""
            if not nxt.startswith("    "):
                i += 1
                continue
        trimmed.append(line)
        i += 1
    out = trimmed
    # drop a top-level "hooks:" that now owns nothing (only ever happens in a
    # config we created ourselves; a user's hooks: block always has children)
    cleaned, i = [], 0
    while i < len(out):
        line = out[i]
        if line.rstrip() == "hooks:":
            nxt = out[i + 1] if i + 1 < len(out) else ""
            if not nxt.startswith("  "):
                i += 1
                continue
        cleaned.append(line)
        i += 1
    out = cleaned
    if dry_run:
        print("dry-run: would rewrite", config_path)
        return 0
    save(config_path, out)
    print("removed kit entries from", config_path)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--hookdir", required="--add" in sys.argv)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.add:
        sys.exit(add_entries(args.config, args.hookdir, args.dry_run))
    if args.remove:
        sys.exit(remove_entries(args.config, args.dry_run))
    sys.exit(1 if _owned(load(args.config)) else 0)


if __name__ == "__main__":
    main()
