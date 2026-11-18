"""Build disposable git repos for the guard tests — no fixture blobs in the repo."""

import os
import subprocess


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, timeout=15)


def _init(repo):
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True, timeout=15)
    _git(repo, "config", "user.name", "Kit Test")
    _git(repo, "config", "user.email", "kit@test")


def repo_with_untracked_test(repo):
    _init(repo)
    os.makedirs(repo / "tests")
    (repo / "README.md").write_text("hi\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "init")
    (repo / "tests" / "test_new.py").write_text("def test_x():\n    pass\n")
    return repo


def repo_with_tracked_test(repo):
    _init(repo)
    os.makedirs(repo / "tests")
    (repo / "tests" / "test_new.py").write_text("def test_x():\n    pass\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init")
    return repo


def clean_repo(repo):
    _init(repo)
    (repo / "README.md").write_text("hi\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "init")
    return repo
