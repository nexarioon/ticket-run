"""IT-19, IT-20, uninstall, dry-run: install.sh against a fake Hermes root."""

import hashlib
import json
import os
import stat
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, ".."))
INSTALL = os.path.join(KIT, "install.sh")

USER_CONFIG = """model: dummy
hooks:
  pre_llm_call:
    - command: /some/other/hook.py
      timeout: 3
other: value
"""


def run(home, *args):
    proc = subprocess.run(["bash", INSTALL, "--home", str(home), *args],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout


def tree_hash(root):
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            h.update(os.path.relpath(fp, root).encode())
            h.update(open(fp, "rb").read())
    return h.hexdigest()


def test_IT19_fresh_home_full_install(tmp_path):
    home = tmp_path / "hermes"
    out = run(home, "--yes")
    cfg = home / "config.yaml"
    assert cfg.exists()
    text = cfg.read_text()
    assert "ticket-workflow-kit/ticket-rules.py" in text
    assert "ticket-workflow-kit/tests-not-committed.py" in text
    assert "matcher: terminal" in text
    hook = home / "agent-hooks" / "ticket-workflow-kit" / "ticket-rules.py"
    assert hook.exists() and os.stat(hook).st_mode & stat.S_IXUSR
    assert (home / "skills" / "vdd-workflow" / "SKILL.md").exists()
    assert (home / "ticket-workflow" / "default.yaml").exists()
    assert (home / "ticket-workflow" / ".install-stamp.json").exists()
    stamps = json.loads((home / "ticket-workflow" / ".install-stamp.json").read_text())
    assert stamps["backup"] is None  # fresh config, nothing to back up
    assert "consent" in out.lower()


def test_IT19_existing_hooks_merge_keeps_user_entries(tmp_path):
    home = tmp_path / "hermes"
    (home).mkdir()
    (home / "config.yaml").write_text(USER_CONFIG)
    before_user_line = "    - command: /some/other/hook.py"
    run(home, "--yes")
    text = (home / "config.yaml").read_text()
    assert before_user_line in text                       # user entry survived
    assert text.count("ticket-workflow-kit/ticket-rules.py") == 1
    assert "matcher: terminal" in text                    # merged alongside, not replaced
    bak = list(home.glob("config.yaml.bak-ticketworkflow-*"))
    assert len(bak) == 1                                  # backup of the pre-install file


def test_IT20_idempotent_second_run_writes_nothing(tmp_path):
    home = tmp_path / "hermes"
    run(home, "--yes")
    first = (home / "config.yaml").read_text()
    run(home, "--yes")
    assert (home / "config.yaml").read_text() == first


def test_uninstall_restores_config_byte_exact(tmp_path):
    home = tmp_path / "hermes"
    (home).mkdir()
    original = USER_CONFIG
    (home / "config.yaml").write_text(original)
    run(home, "--yes")
    run(home, "--uninstall")
    assert (home / "config.yaml").read_text() == original  # E2E-04 predicate
    assert not (home / "agent-hooks" / "ticket-workflow-kit").exists()
    assert (home / "skills" / "vdd-workflow" / "SKILL.md").exists()  # skills stay


def test_uninstall_fresh_home_leaves_no_dangling_hooks_key(tmp_path):
    home = tmp_path / "hermes"
    run(home, "--yes")
    run(home, "--uninstall")
    text = (home / "config.yaml").read_text()
    assert "ticket-workflow-kit" not in text
    assert "hooks:" not in text
    assert not (home / "agent-hooks" / "ticket-workflow-kit").exists()


def test_dry_run_writes_nothing(tmp_path):
    home = tmp_path / "hermes"
    (home).mkdir()
    (home / "config.yaml").write_text(USER_CONFIG)
    before = tree_hash(home)
    run(home, "--dry-run")
    assert tree_hash(home) == before
    assert not (home / "agent-hooks").exists()
