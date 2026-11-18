"""IT-01..IT-06: the pre_llm_call hook fires exactly when it should.

Each test pipes a fixture payload into hooks/ticket-rules.py and asserts on the
real stdout/exit code. Language behaviour is asserted through policy overrides
(TICKET_POLICY) so the default file stays untouched.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, ".."))
HOOK = os.path.join(KIT, "hooks", "ticket-rules.py")
FIX = os.path.join(KIT, "fixtures", "hook_payloads")

LANG_ID_POLICY = os.path.join(KIT, "tests", "lang_id_policy.yaml")


def run(payload, env_extra=None, raw_stdin=False):
    env = dict(os.environ)
    env.pop("TICKET_POLICY", None)
    if env_extra:
        env.update(env_extra)
    stdin = payload if raw_stdin else json.dumps(payload)
    proc = subprocess.run(
        [sys.executable, HOOK], input=stdin, capture_output=True, text=True, timeout=15, env=env
    )
    return proc.returncode, proc.stdout.strip()


def parsed(stdout):
    return json.loads(stdout)


def test_IT01_strong_code_message_gets_full_workflow():
    payload = json.load(open(os.path.join(FIX, "ticket_id.json")))
    rc, out = run(payload)
    assert rc == 0 and out
    ctx = parsed(out)["context"]
    assert "TEST PLAN" in ctx and "IT-xx" in ctx and "Mandatory order" in ctx


def test_IT02_weak_plus_document_gets_short_reminder():
    payload = json.load(open(os.path.join(FIX, "doc_weak.json")))
    rc, out = run(payload)
    assert rc == 0 and out
    ctx = parsed(out)["context"]
    assert "test plan first" in ctx
    assert "IT-xx" not in ctx  # short reminder never carries the full matrix order


def test_IT03_plain_chat_is_silent():
    payload = json.load(open(os.path.join(FIX, "chat.json")))
    rc, out = run(payload)
    assert rc == 0 and out == ""


def test_IT04_broken_payload_is_silent_nop():
    rc, out = run("bukan json", raw_stdin=True)
    assert rc == 0 and out == ""


def test_IT05_short_message_is_silent_nop():
    rc, out = run({"hook_event_name": "pre_llm_call", "extra": {"user_message": "ok fix"}})
    assert rc == 0 and out == ""


def test_IT06_language_id_policy_switches_message():
    policy = "language: id\nskills: [vdd-workflow]\n"
    path = os.path.join(KIT, "tests", "_tmp_lang_id.yaml")
    open(path, "w").write(policy)
    try:
        payload = json.load(open(os.path.join(FIX, "ticket_id.json")))
        rc, out = run(payload, {"TICKET_POLICY": path})
        assert rc == 0 and out
        ctx = parsed(out)["context"]
        assert "wajib" in ctx and "Mandatory" not in ctx
    finally:
        os.remove(path)


def test_IT06b_non_llm_event_is_silent_nop():
    rc, out = run({"hook_event_name": "post_tool_call", "extra": {"user_message": "fix bug endpoint"}})
    assert rc == 0 and out == ""
