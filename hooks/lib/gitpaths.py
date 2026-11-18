"""Resolve which repo a shell command's git segments act on, and list the new
(untracked or staged-added) test files inside it. Stdlib only.

The GIT_WRITE regex accepts quoted `-c`/`-C` values: a commit issued as
`git -c user.name="A B" -c user.email=x@y commit` is a git write. The original
machine hook this kit ports missed that case (a quoted value containing a
space made the whole segment unmatched), which let commits slip past the
guard; tests/test_tests_not_committed.py locks the fix.
"""

import fnmatch
import os
import re
import subprocess

GIT_WRITE = re.compile(
    r"^(?:\w+=\S*\s+)*(?:(?:sudo|env|time|command|exec)\s+(?:\w+=\S*\s+)*)?"
    r"git(?:\s+-[cC]\s+(?:(?:[^\s=]+=)?(?:\"[^\"]*\"|'[^']*'|\S+)))*"
    r"\s+(?:commit|push)\b"
)
_SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\n|\|")
_CD = re.compile(r"^cd\s+(?:--\s+)?(.+)$")
_C_FLAG = re.compile(r"-C\s+(?:\"([^\"]+)\"|'([^']+)'|(\S+))")

TEST_PATH = re.compile(
    r"(?:^|/)(?:tests?|__tests__|__mocks__|spec|specs|e2e)/"
    r"|\.(?:test|spec|e2e)\.[cm]?[jt]sx?$"
    r"|(?:^|/)test_[^/]*\.py$"
    r"|_test\.py$"
    r"|\.feature$"
)


def _join(base: str, path: str) -> str:
    return os.path.normpath(os.path.join(base, os.path.expanduser(path)))


def _cd_target(segment: str, base: str) -> str:
    match = _CD.match(segment)
    argument = (match.group(1).strip().split() or [""])[0].strip("'\"") if match else ""
    return _join(base, argument) if argument and not argument.startswith("$") else base


def _git_target(segment: str, base: str) -> str:
    match = _C_FLAG.search(segment)
    if not match:
        return base
    path = next(group for group in match.groups() if group)
    return _join(base, path)


def git_targets(command: str, base: str) -> list:
    """Every directory a git commit/push segment in the command acts on."""
    targets = []
    for segment in (part.strip() for part in _SEGMENT_SPLIT.split(command)):
        if not segment:
            continue
        if _CD.match(segment):
            base = _cd_target(segment, base)
        elif GIT_WRITE.match(segment):
            target = _git_target(segment, base)
            if target not in targets:
                targets.append(target)
    return targets


def new_test_files(directory: str, allowlist) -> list:
    """Untracked or staged-added paths that look like test files, minus allowlisted ones."""
    try:
        result = subprocess.run(
            ["git", "-C", directory or ".", "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, timeout=8,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    found = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        status, path = line[:2], line[3:].strip()
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if (status == "??" or "A" in status) and TEST_PATH.search(path):
            if not any(fnmatch.fnmatch(path, glob) for glob in allowlist):
                found.append(path)
    return sorted(set(found))
