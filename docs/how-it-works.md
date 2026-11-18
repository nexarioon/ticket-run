# How it works

The kit is one pipeline enforced from three directions, so it still holds when
the agent forgets any single one of them.

## The pipeline

```
1 intake        requirements R1..Rn + acceptance criteria + assumptions
2 test plan     IT-xx / E2E-xx matrices with expected values, fixtures,
               exit criteria, the old tests that pin the bug
3 coding plan  ten sections, phases mapped to test IDs and exact files
4 implement    phase by phase, root-cause fixes only
5 verify+loop  whole suite + typecheck + build; on red, root-cause, smallest
               change, re-run; cap 5 iterations then a dead-end report;
               self-verify on the matching surface (API pair, UI screenshot,
               money numbers row by row)
6 report       what changed, per-ID results, iteration log, evidence,
               what is still manual, commit/push status
```

## The three enforcement layers

1. **Skill text** (`skills/vdd-workflow`): the pipeline itself, loaded when a
   ticket arrives. Works on any harness that reads SKILL.md files.
2. **pre_llm_call hook** (`hooks/ticket-rules.py`): appends the mandatory
   order to the user message whenever it looks like a ticket. Detection is
   keyword-based in both English and Indonesian; the injected text comes from
   `hooks/messages/<language>.json`.
3. **pre_tool_call hook** (`hooks/tests-not-committed.py`): blocks
   `git commit` / `git push` while the target repo holds a new (untracked or
   staged-added) test file, unless its path is allowlisted by policy. It
   resolves the target repo through `-C <path>`, the tool's workdir, and
   preceding `cd` segments, and it inspects the tree *before* the command
   runs — so `rm <test> && git commit` in one line still blocks. Deleting the
   file and committing are deliberately two separate steps.

## The loop rules (stage 5)

- The exit predicate is the test plan itself, restated before the first edit.
- Root-cause, smallest change, re-run the affected suite, whole suite at the end.
- Two consecutive iterations without movement = plateau: pivot or attack the
  shared premise. Five iterations = stop and report a dead end.
- Never relax the predicate to declare victory; never weaken a test.
- Pre-existing failures must be proven against a worktree of the base ref.

## Policy

`policy/default.yaml` and its overrides control language, the skill list the
injection names, retention, and the commit-guard allowlist. Search order:
`$TICKET_POLICY` → `<repo>/.ticket-run.yaml` → `~/.hermes/ticket-run.yaml`
→ the bundled default. See `writing-a-policy.md`.
