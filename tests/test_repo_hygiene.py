"""P7 gates: repo stays free of personal tokens; frontmatter and exec bits valid."""

import os
import re
import stat
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(KIT, "tools"))

from check_hygiene import DENYLIST_TOKENS, find_violations  # noqa: E402


def test_IT18_no_personal_tokens_anywhere():
    assert find_violations(KIT) == []


def test_IT17_frontmatter_all_skills():
    skills = os.path.join(KIT, "skills")
    for name in sorted(os.listdir(skills)):
        text = open(os.path.join(skills, name, "SKILL.md"), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        assert m, name
        kv = dict(re.findall(r"^([a-z_]+):\s*(.+)$", m.group(1), re.M))
        assert kv.get("name") == name
        assert len(kv.get("description", "").strip().strip('"')) <= 60


def test_hooks_are_executable():
    for fn in ("ticket-rules.py", "tests-not-committed.py"):
        path = os.path.join(KIT, "hooks", fn)
        assert os.stat(path).st_mode & stat.S_IXUSR, fn
    assert os.stat(os.path.join(KIT, "install.sh")).st_mode & stat.S_IXUSR
