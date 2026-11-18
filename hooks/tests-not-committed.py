#!/usr/bin/env python3
"""ticket-workflow-kit pre_tool_call hook: keep scaffolding tests out of git.

Blocks the terminal tool call when one of its git commit/push segments would
run in a repo whose working tree holds a NEW (untracked or staged-added) test
file that the retention policy does not allowlist. Everything else is a silent
no-op. Message text comes from hooks/messages/<language>.json; the allowlist
comes from the policy file (see hooks/lib/policies.py).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.payload import tool_input as read_tool_input   # noqa: E402
from lib.gitpaths import git_targets, new_test_files   # noqa: E402
from lib.policies import load, allowlist as policy_allowlist  # noqa: E402

MESSAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "messages")


def _message(lang: str, files: list) -> str:
    listed = ", ".join(files[:8]) + (f" (+{len(files) - 8} more)" if len(files) > 8 else "")
    for candidate in (lang, "en"):
        try:
            with open(os.path.join(MESSAGES_DIR, candidate + ".json"), encoding="utf-8") as fh:
                texts = json.load(fh)
        except OSError:
            continue
        if "commit_block" in texts:
            return texts["commit_block"].replace("{files}", listed)
    return f"Blocked: new test file(s) present: {listed}"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "terminal":
        return 0

    inp = read_tool_input(payload)
    command = str(inp.get("command") or "")
    base = str(inp.get("workdir") or payload.get("cwd") or ".") or "."
    base = os.path.abspath(os.path.expanduser(base))

    targets = git_targets(command, base)
    if not targets:
        return 0

    policy = load(base)
    files = sorted({p for t in targets for p in new_test_files(t, policy_allowlist(policy))})
    if not files:
        return 0

    print(json.dumps({"action": "block", "message": _message(str(policy.get("language", "en")), files)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
