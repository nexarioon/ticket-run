"""Tiny policy loader: flat YAML subset (key: value, key: [a, b]) — stdlib only.

Search order: $TICKET_POLICY, <cwd>/.ticket-workflow.yaml,
~/.hermes/ticket-workflow.yaml, then the kit default at policy/default.yaml.
First file that exists wins; a missing key falls back to the default below.
"""

import os
import re
from typing import Any, Dict, List

DEFAULTS: Dict[str, Any] = {
    "language": "en",
    "skills": ["vdd-workflow", "coding-plan", "clean-code"],
    "retention": "regression-permanent",
    "test_globs_allow": [],
}

_LIST_LINE = re.compile(r"^([a-z_]+):\s*\[(.*)\]\s*$")
_KV_LINE = re.compile(r"^([a-z_]+):\s*(.*?)\s*$")


def _parse(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _LIST_LINE.match(line)
        if m:
            out[m.group(1)] = [v.strip().strip("'\"") for v in m.group(2).split(",") if v.strip()]
            continue
        m = _KV_LINE.match(line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip("'\"")
    return out


def _kit_default_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "policy", "default.yaml"))


def load(cwd: str = ".") -> Dict[str, Any]:
    candidates = []
    env = os.environ.get("TICKET_POLICY")
    if env:
        candidates.append(env)
    candidates.append(os.path.join(cwd or ".", ".ticket-workflow.yaml"))
    candidates.append(os.path.expanduser("~/.hermes/ticket-workflow.yaml"))
    candidates.append(_kit_default_path())
    merged = dict(DEFAULTS)
    for path in candidates:
        try:
            with open(path, encoding="utf-8") as fh:
                merged.update(_parse(fh.read()))
            break
        except OSError:
            continue
    if not isinstance(merged.get("skills"), list):
        merged["skills"] = [s.strip() for s in str(merged["skills"]).split(",") if s.strip()]
    return merged


def allowlist(policy: Dict[str, Any]) -> List[str]:
    """Test-path globs the retention hook must not block."""
    raw = policy.get("test_globs_allow") or []
    return [str(g) for g in raw]
