#!/usr/bin/env python3
"""ticket-workflow-kit pre_llm_call hook: keep the pipeline in force.

Reads the hook payload on stdin and prints {"context": "..."} only when the
user's message looks like development work. Anything else is a silent no-op so
those turns stay clean. Message text comes from hooks/messages/<language>.json;
skill names come from the policy file (see hooks/lib/policies.py).
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from payload import message_text        # noqa: E402
from detect import classify             # noqa: E402
from policies import load               # noqa: E402

MESSAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "messages")


def _message(lang: str, kind: str, skills: list) -> str:
    for candidate in (lang, "en"):
        try:
            with open(os.path.join(MESSAGES_DIR, candidate + ".json"), encoding="utf-8") as fh:
                texts = json.load(fh)
        except OSError:
            continue
        if kind in texts:
            return texts[kind].replace("{skills}", ", ".join("`" + s + "`" for s in skills))
    return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict):
        return 0
    if payload.get("hook_event_name") not in (None, "pre_llm_call"):
        return 0

    message = message_text(payload).strip().lower()
    if len(message) < 8:
        return 0

    kind = classify(message)
    if kind is None:
        return 0

    policy = load(os.environ.get("TICKET_CWD") or ".")
    text = _message(str(policy.get("language", "en")), kind, policy.get("skills", []))
    if not text:
        return 0
    print(json.dumps({"context": text}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
