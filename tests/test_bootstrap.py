"""P6 gates: bootstrap.sh installs from a tarball with one command.

No network: tests pack the working tree into a local tarball and pass it via
--url file://...  TMPDIR is pointed at a private dir so the cleanup trap is
observable.
"""

import hashlib
import os
import re
import subprocess
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, ".."))
BOOTSTRAP = os.path.join(KIT, "bootstrap.sh")
INCLUDE = ["skills", "hooks", "policy", "install", "install.sh", "VERSION", "README.md"]


def build_tarball(dest):
    with tarfile.open(dest, "w:gz") as tar:
        for name in INCLUDE:
            src = os.path.join(KIT, name)
            if os.path.isfile(src):
                tar.add(src, arcname=f"pkg/{name}")
                continue
            for root, dirs, files in os.walk(src):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for fn in files:
                    fp = os.path.join(root, fn)
                    tar.add(fp, arcname="pkg/" + os.path.relpath(fp, KIT))
    return dest


def run(args, tmpdir):
    os.makedirs(tmpdir, exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = str(tmpdir)
    proc = subprocess.run(["bash", BOOTSTRAP, *args], capture_output=True, text=True,
                          timeout=120, env=env)
    return proc.returncode, proc.stdout + proc.stderr


def home_tree(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            out.append(os.path.relpath(os.path.join(dirpath, fn), root))
    return out


def test_IT01_dry_run_writes_nothing(tmp_path):
    tgz = build_tarball(tmp_path / "pkg.tgz")
    home = tmp_path / "home"
    tmpd = tmp_path / "tmpd"
    tmpd.mkdir()
    rc, out = run(["--url", f"file://{tgz}", "--dry-run", "--home", str(home)], tmpd)
    assert rc == 0, out
    assert "dry-run" in out
    assert home_tree(home) == [], home_tree(home)


def test_IT02_full_install_and_cleanup(tmp_path):
    tgz = build_tarball(tmp_path / "pkg.tgz")
    home = tmp_path / "home"
    tmpd = tmp_path / "tmpd"
    tmpd.mkdir()
    rc, out = run(["--url", f"file://{tgz}", "--home", str(home), "--yes"], tmpd)
    assert rc == 0, out
    assert (home / "agent-hooks" / "ticket-workflow-kit" / "ticket-rules.py").exists()
    cfg = (home / "config.yaml").read_text()
    assert "ticket-rules.py" in cfg and "tests-not-committed.py" in cfg
    assert (home / "skills" / "vdd-workflow" / "SKILL.md").exists()
    assert os.listdir(tmpd) == []          # cleanup trap removed the temp tree


def test_IT03_bad_url_fails_clean(tmp_path):
    home = tmp_path / "home"
    tmpd = tmp_path / "tmpd"
    tmpd.mkdir()
    rc, out = run(["--url", "file:///nonexistent/nope.tgz", "--home", str(home), "--yes"], tmpd)
    assert rc != 0
    assert "download failed" in out
    assert home_tree(home) == []


def test_IT04_checksum_enforced(tmp_path):
    tgz = build_tarball(tmp_path / "pkg.tgz")
    good = hashlib.sha256(open(tgz, "rb").read()).hexdigest()
    home_bad = tmp_path / "hb"
    rc, out = run(["--url", f"file://{tgz}", "--sha256", "0" * 64, "--home", str(home_bad), "--yes"],
                  tmp_path / "t")
    assert rc != 0 and "checksum mismatch" in out
    assert home_tree(home_bad) == []
    home_ok = tmp_path / "hok"
    rc, out = run(["--url", f"file://{tgz}", "--sha256", good, "--home", str(home_ok), "--yes"],
                  tmp_path / "t")
    assert rc == 0, out
    assert (home_ok / "config.yaml").exists()


def test_IT05_flags_passthrough_profile_and_uninstall(tmp_path):
    tgz = build_tarball(tmp_path / "pkg.tgz")
    base = tmp_path / "hroot"
    rc, out = run(["--url", f"file://{tgz}", "--home", str(base), "--profile", "try1", "--yes"],
                  tmp_path / "t")
    assert rc == 0, out
    prof = base / "profiles" / "try1"
    assert (prof / "config.yaml").read_text().count("ticket-workflow-kit") >= 2
    assert (prof / "agent-hooks" / "ticket-workflow-kit" / "ticket-rules.py").exists()
    rc, out = run(["--url", f"file://{tgz}", "--home", str(base), "--profile", "try1", "--uninstall"],
                  tmp_path / "t")
    assert rc == 0, out
    assert not (prof / "agent-hooks" / "ticket-workflow-kit").exists()


def test_IT06_no_git_dependency():
    text = open(BOOTSTRAP, encoding="utf-8").read()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert not re.search(r"git", stripped), line
