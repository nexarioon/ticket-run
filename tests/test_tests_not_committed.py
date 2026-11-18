"""IT-07..IT-16 + regression: the pre_tool_call commit guard.

Payloads use the wire shape (_serialize_payload output): tool_name "terminal"
and tool_input {command, workdir}. Note for `hermes hooks test --payload-file`
users: that CLI merges a top-level "args" object into tool_input at fire time,
so fixtures for the CLI must use {"args": {...}}, not {"tool_input": {...}}.
"""

import json
import os
import subprocess
import sys

from helpers.repos import repo_with_untracked_test, repo_with_tracked_test, clean_repo

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, ".."))
HOOK = os.path.join(KIT, "hooks", "tests-not-committed.py")


def run(command, workdir, env_extra=None, path=None):
    env = dict(os.environ)
    env.pop("TICKET_POLICY", None)
    if env_extra:
        env.update(env_extra)
    payload = json.dumps({"hook_event_name": "pre_tool_call", "tool_name": "terminal",
                          "tool_input": {"command": command, "workdir": str(workdir)}})
    proc = subprocess.run([sys.executable, path or HOOK], input=payload,
                          capture_output=True, text=True, timeout=20, env=env)
    return proc.returncode, proc.stdout.strip()


def test_IT07_commit_with_untracked_test_blocks(tmp_path):
    repo = repo_with_untracked_test(tmp_path / "r")
    rc, out = run("git commit -m wip", repo)
    assert rc == 0 and out
    data = json.loads(out)
    assert data["action"] == "block"
    assert "tests/test_new.py" in data["message"]


def test_IT08_after_deletion_commit_is_silent(tmp_path):
    repo = repo_with_untracked_test(tmp_path / "r")
    (repo / "tests" / "test_new.py").unlink()
    rc, out = run("git commit -m wip", repo)
    assert rc == 0 and out == ""


def test_IT09_tracked_clean_repo_is_silent(tmp_path):
    repo = repo_with_tracked_test(tmp_path / "r")
    rc, out = run("git commit -m wip", repo)
    assert rc == 0 and out == ""


def test_IT10_dash_C_target_resolved(tmp_path):
    clean = clean_repo(tmp_path / "clean")
    dirty = repo_with_untracked_test(tmp_path / "dirty")
    rc, out = run(f'git -C "{dirty}" commit -m wip', clean)
    assert rc == 0 and out and "tests/test_new.py" in json.loads(out)["message"]


def test_IT11_rm_then_commit_in_one_line_still_blocks(tmp_path):
    # The guard inspects the repo BEFORE the command runs, so deleting the file
    # in the same shell line does not clear the block. Locked as designed.
    repo = repo_with_untracked_test(tmp_path / "r")
    rc, out = run(f'cd "{repo}" && rm tests/test_new.py && git commit -m x', tmp_path)
    assert rc == 0 and out and json.loads(out)["action"] == "block"


def test_IT12_non_git_command_is_silent(tmp_path):
    repo = repo_with_untracked_test(tmp_path / "r")
    rc, out = run("npm test", repo)
    assert rc == 0 and out == ""


def test_IT13_git_status_is_silent(tmp_path):
    repo = repo_with_untracked_test(tmp_path / "r")
    rc, out = run("git status", repo)
    assert rc == 0 and out == ""


def test_IT14_push_with_untracked_test_blocks(tmp_path):
    repo = repo_with_untracked_test(tmp_path / "r")
    rc, out = run("git push origin HEAD", repo)
    assert rc == 0 and out and json.loads(out)["action"] == "block"


def test_IT15_allowlist_glob_is_not_blocked(tmp_path):
    repo = clean_repo(tmp_path / "r")
    allow = tmp_path / "allow.yaml"
    allow.write_text("language: en\ntest_globs_allow: [tests/regression/**]\n")
    (repo / "tests" / "regression").mkdir(parents=True)
    (repo / "tests" / "regression" / "r1.test.ts").write_text("x\n")
    rc, out = run("git commit -m wip", repo, {"TICKET_POLICY": str(allow)})
    assert rc == 0 and out == ""  # the only new test file is allowlisted
    (repo / "tests" / "test_new.py").write_text("def test_x():\n    pass\n")
    rc, out = run("git commit -m wip", repo, {"TICKET_POLICY": str(allow)})
    assert rc == 0 and out and json.loads(out)["action"] == "block"  # non-allowlisted still blocks


def test_IT16_missing_git_fails_open_silently(tmp_path):
    repo = repo_with_untracked_test(tmp_path / "r")
    empty = tmp_path / "emptybin"
    empty.mkdir()
    rc, out = run("git commit -m wip", repo, {"PATH": str(empty)})
    assert rc == 0 and out == ""


def test_IT16b_quoted_dash_c_commit_is_detected(tmp_path):
    # Regression: the machine hook's original regex missed
    # `git -c user.name="A B" commit` (quoted value with a space), letting
    # commits slip past the guard. The kit regex must catch it.
    repo = repo_with_untracked_test(tmp_path / "r")
    rc, out = run('git -c user.name="A B" -c user.email=a@b commit -m x', repo)
    assert rc == 0 and out and json.loads(out)["action"] == "block"


def test_commit_block_message_language_id(tmp_path):
    repo = repo_with_untracked_test(tmp_path / "r")
    pol = tmp_path / "pol.yaml"
    pol.write_text("language: id\n")
    rc, out = run("git commit -m wip", repo, {"TICKET_POLICY": str(pol)})
    assert rc == 0 and out and "Diblokir" in json.loads(out)["message"]
