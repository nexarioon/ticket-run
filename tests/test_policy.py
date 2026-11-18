"""P6 gates: policy parser, fallback order, allowlist globs, example presets."""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(KIT, "hooks", "lib"))

import policies  # noqa: E402


def test_defaults_when_no_policy_exists(tmp_path, monkeypatch):
    monkeypatch.delenv("TICKET_POLICY", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    pol = policies.load(str(tmp_path))
    assert pol["language"] == "en"
    assert "vdd-workflow" in pol["skills"]
    assert pol["retention"] == "regression-permanent"


def test_env_var_wins_over_repo_file(tmp_path, monkeypatch):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / ".ticket-run.yaml").write_text("language: id\n")
    env_pol = tmp_path / "env.yaml"; env_pol.write_text("language: en\nskills: [a, b]\n")
    monkeypatch.setenv("TICKET_POLICY", str(env_pol))
    monkeypatch.setenv("HOME", str(tmp_path))
    pol = policies.load(str(repo))
    assert pol["language"] == "en" and pol["skills"] == ["a", "b"]


def test_repo_file_used_when_no_env(tmp_path, monkeypatch):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / ".ticket-run.yaml").write_text("language: id\ntest_globs_allow: [tests/regression/**]\n")
    monkeypatch.delenv("TICKET_POLICY", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    pol = policies.load(str(repo))
    assert pol["language"] == "id"
    assert "tests/regression/**" in policies.allowlist(pol)


def test_example_profiles_parse(tmp_path, monkeypatch):
    src = open(os.path.join(KIT, "policy", "profiles.example.yaml"), encoding="utf-8").read()
    blocks, current = {}, None
    for line in src.splitlines():
        m = re.match(r"^  ([\w-]+):", line)
        if m:
            current = m.group(1)
            blocks[current] = []
            continue
        if current and line.startswith("    "):
            blocks[current].append(line[4:])
    assert set(blocks) == {"money", "api-contract", "ui"}
    for name, lines in blocks.items():
        parsed = policies._parse("\n".join(lines))
        assert parsed["language"] == "en", name
        assert parsed["retention"] == "regression-permanent", name
        assert isinstance(parsed["runners"], list) and parsed["runners"], name
    assert "pytest -q" in policies._parse("\n".join(blocks["api-contract"]))["runners"]


def test_allowlist_globs_match_regression_only():
    import fnmatch
    allow = ["tests/regression/**", "tests/contract/**"]
    assert any(fnmatch.fnmatch("tests/regression/r1.test.ts", g) for g in allow)
    assert any(fnmatch.fnmatch("tests/contract/test_api.py", g) for g in allow)
    assert not any(fnmatch.fnmatch("tests/test_new.py", g) for g in allow)
