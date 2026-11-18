---
name: vdd-workflow
description: "Ticket to report: test plan, coding plan, build, verify."
version: 2.2.1
author: Fendi Permadi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, ticket, test-plan, planning, validation, e2e, gates]
    related_skills: [coding-plan, clean-code, e2e-browser-test-automation, test-driven-development, vdd]
---

# Ticket Workflow (mandatory order)

Every ticket, bug report, feature request or "kerjakan ini" instruction goes through
this exact pipeline. No stage may be skipped, and the order is not negotiable:

```
1. Tiket / perintah
2. TEST PLAN      (integration tests always; E2E when the work is a big feature)
3. CODING PLAN    (phases mapped to test IDs)
4. Implementasi   (phase by phase)
5. Jalankan test plan (integration + E2E) until green
6. Laporan        (what changed, evidence, what is left)
```

The test plan comes BEFORE the coding plan. Writing the coding plan first produces
tests that are reverse-engineered from the implementation and therefore cannot
fail — those are decoration, not verification.

## When to Use

- **Any ticket, issue, PRD, bug report, or imperative instruction to change code**
- Work spanning more than one file or more than one commit
- **Non-code tickets** (install a package, update a suite, change machine/desktop config, run a
  build for the user): the pipeline collapses to *intake → verification matrix → report*, and the
  matrix is executed against the real machine. There is no coding plan, no test file, and nothing
  to commit; the "base ref" is a snapshot of the state before the change (`dpkg -L`, the relevant
  `gsettings`/config values, `git rev-parse HEAD`, file hashes). Every row still needs an expected
  value and real command output — "sudah saya pasang" is not a result.
- Not for: single-line typo/format fixes, read-only questions, code review of someone else's branch

## Stage 1 — Ticket intake

1. Read the ticket end to end; quote it back if it arrived outside the repo.
2. Extract requirements `R1..Rn` — one requirement = one verifiable statement of behaviour.
3. Extract acceptance criteria `AC1..ACn`; label inferred ones `(inferred)`.
4. List ambiguities. Ask only if the answer changes what you build; otherwise state the assumption.
5. Locate the code: components, routes, helpers, and existing tests this ticket touches.
6. When the ticket spans repos, prove the base branch contains the code each side will edit:
   `git ls-tree -r origin/<base> --name-only | grep -i "<feature-dir>"`. Branch names are
   case-sensitive — `staging` and `Staging` can both exist and only one carries the feature, and a
   paginated branch listing (`gh api .../branches`, `git branch -r`) may show only one variant.
   Enumerate with `git ls-remote --heads origin | grep -i <base>`, then run the tree check on the
   exact ref you intend to base on. A branch named as the integration base can be stale or missing
   the feature entirely; never conclude "the base lacks it" from one listing. If it truly is
   missing, branch from the ref that has it and state the deviation before editing — never merge a
   whole feature into a stale branch to satisfy the wording literally.

**Done when:** requirements, ACs, assumptions, and touched modules are visible in the reply.

## Stage 2 — Test plan (before any coding plan)

Produce a written plan with, at minimum:

| Part | Content |
|---|---|
| Scope | in scope / out of scope, one line each |
| Exit criteria | what must be green before the work counts as done |
| Environment | servers, ports, DB copy, user/token, settings |
| Fixtures | exact data used by the tests (amounts, dates, tenor, expected angsuran) |
| **Integration matrix** | `IT-01…IT-nn`: ID, scenario, steps/payload, expected result |
| **E2E matrix** | `E2E-01…`: ID, UI steps, selectors, expected result |
| Regression list | existing behaviours that must not change |
| Tooling | which runner, which command, where the files live |
| Risks | data pollution, flaky waits, ports already in use |

Rules for the plan itself:

- **Integration tests are always required** for anything touching an API, query, schema, money math, or a business rule.
- **E2E is required when** the change is a large/user-facing feature, spans several pages, or a user-visible flow can silently break (money, installments, printing/export, multi-step forms). For a small internal fix, state explicitly that E2E is out of scope and why.
- Every test row needs an **expected value**, not "works correctly". Numbers, status codes, row counts, absence of a cash row.
- Include the **tests that currently encode the bug**. A bug fix is not done until the test asserting the old behaviour is rewritten — grep the suite for the exact assertion first.
- **Behaviour-preserving work** (refactor, cleanup, file moves) needs an identity check, not only green tests: hash or snapshot the artifact before the first edit (moved block, generated docx/pdf, API JSON) and compare after. Plan the snapshot capture as step one of the phase. Full recipe: `references/behaviour-preserving-refactor.md`.
- State which cases stay manual (docx/print/download verification, visual layout) instead of pretending they are automated.
- **Test retention follows the repo policy** (`policy/*.yaml`; default `regression-permanent`): a test that encodes a real bug, a contract, or a reported regression is permanent and stays in the suite; scaffolding written only to drive the feature is deleted once green and never committed. Plan the test IDs around *what you will run and report*. Existing suite files may always be edited. `retention: strict` deletes every new test file after green; `retention: keep-all` keeps everything. Ask the user before keeping a scaffolding file.

**Done when:** the matrices exist with IDs, and the user can read the plan without opening the code.

## Stage 3 — Coding plan

Load the `coding-plan` skill and produce its 10 sections. When the user asks only for a plan ("buatkan plan"), ship ONE markdown document: Stage 2's matrices first, then the ten sections with phases mapped to the test IDs — not two separate files, and never the coding plan without the matrix. Additionally:

- Map every phase to the `IT-#`/`E2E-#` IDs it will satisfy.
- Name the exact files to be touched.
- Call out the test files that must be updated, not only added.
- Choose the smallest behaviour-preserving refactor when the fix spans duplicated logic.

**Done when:** every phase is independently testable, one-commit sized, and depends on no later phase.

## Stage 4 — Implementation

Load the `clean-code` skill and apply it continuously. Touch only files in the approved
plan; if reality contradicts the plan, say so and re-plan instead of silently widening scope.

- Fix the root cause, not the symptom.
- Keep business math in one reusable helper instead of re-deriving it in SQL, a component, or a migration script.
- Add `data-testid` (or the repo's equivalent stable hook) to any control the E2E plan names, so selectors survive refactors.
- Comments in English, user-facing copy in the product's language, unless the repo says otherwise. Translating comments never licenses touching a string literal, a test title or a data value.
- Before merging duplicated helpers, diff their bodies: identical ones collapse into the shared module, while a variant with different output keeps its behaviour under a distinct name (`formatRupiah` vs `formatRupiahShort`). Unifying by name alone changes what users see.
- If the base turns out wrong mid-implementation, move the work instead of restarting:
  `git stash push -u`, `git switch -C <branch> origin/<correct-base>`, `git stash pop`, resolve
  conflicts by keeping the base's newer form plus your intent, then re-run the gates. Afterwards
  prove the move was clean: expected additive diffs stay additive, and files the stash dragged in
  that this ticket does not touch are restored out of the index (`git restore --staged --worktree`).

## Stage 5 — Run the test plan (self-verify, then revise until green)

The exit predicate is the Stage 2 plan itself, restated before the first edit:

> **Predicate:** every `IT-#`/`E2E-#` row green with the runner's real counts, typecheck silent, build succeeding, the regression list unchanged, and zero new `any` / `@ts-ignore` / `eslint-disable` / skipped tests.

Run every automated case from Stage 2 and report real output:

1. Integration suite (whole suite, not only the new file).
2. E2E suite (whole spec dir).
3. Typecheck + build.
4. Refactor / comment-only work: `node scripts/ast-equivalence.mjs <base-ref>` must print `OK: AST identical` for every changed file, and moved blocks must hash equal to the block you lifted out.
5. Manual cases that the plan marked as manual (and say they were manual).
6. **Self-verify on the matching surface — "inconclusive" or wrong-surface is not a pass.** API change → paste a real request+response pair; UI change → drive the app on a dedicated port (`strictPort`) and capture before/after screenshots, video when the flow moves; money math → the exact fixture numbers, row by row, from the app's own output.

### Loop rules (when anything is red or inconclusive)

- **Root-cause, then the smallest change the evidence justifies.** Grep the suite for the assertion that encodes the old behaviour first. Never adjust a test to match a buggy implementation. Re-run the affected suite — and after the loop ends, the whole suite again. Never report green from a partial run, and never report green from a run you did not execute.
- **Iteration cap: 5, then a dead-end report.** Two consecutive iterations without the predicate moving is a plateau: pivot the approach, or write the shared premise down and test *it* directly before writing a third fix that assumes it. At the cap, stop and report what was tried, the ranked hypotheses left, and the evidence that would unblock it. Never relax the predicate to declare victory, and never call a phase complete while a known failure exists.
- **Pre-existing failures must be proven, not assumed:** run the same failing subset in a worktree of the base ref and report both counts (see Pitfalls). A proven pre-existing failure does not count against the predicate but must be named in the report.
- **Log every iteration:** one line — what changed, the hypothesis, the runner's real counts, and whether the predicate moved. The log becomes a table in the Stage 6 report whenever the loop ran more than once.
- **Evidence before deletion:** TDD scaffolding files are deleted only after the green full-suite run is captured in the report — then deleted in their own call, never riding into a commit.

## Stage 6 — Report

Answer in the user's language, in this shape:

1. **Apa yang berubah** — per file/area, plus the behaviour change in one sentence.
2. **Hasil test plan** — table: suite, command, result (`162/162`, `8/8`), duration. Bila loop berjalan lebih dari sekali, tambahkan log iterasinya (perubahan, hipotesis, hasil runner, predicate bergerak/tidak).
3. **Bukti kasus asli** — before/after payload+response untuk bug yang dilaporkan, plus artefak verifikasi mandiri (screenshot/video) untuk pekerjaan UI.
4. **Yang masih manual / belum** — explicit, never hidden.
5. **Commit & push** — hashes, remote state (`lokal == remote`), or plainly "belum di-push".
6. **Catatan lingkungan** — DB restored, servers stopped, ports used.

### Commit discipline (only when the user asks for commits)

- Split changes into small commits **by concern**, ordered so each commit still imports/runs:
  refactor → new module → domain/schema → wiring/endpoint. Each commit carries a conventional
  subject (`feat(scope): …`) and a short body saying why.
- Prefer whole-file commits over hunk-splitting. When one file mixes two concerns (e.g. an endpoint
  file that holds both a new route and wiring for a new schema), commit it with the last concern
  that makes it coherent and say which — a commit that imports a module added only in the next
  commit is worse than a slightly larger one.
- Stage paths by name, never `git add -A`.
- Stop after the commit unless push/PR/merge was explicitly requested; report the hashes,
  `git status -sb` (`[ahead N]`), and the unchanged remote head.
- Untracked files have no git recovery. Before deleting any at the user's request, copy them outside
  the repo first (`cp --parents <paths> ~/.hermes/cache/scratch/<name>-backup/`) and report the
  backup path in the reply.

## Enforcement

`hooks/ticket-rules.py` is registered as a `pre_llm_call` shell hook (`hooks.pre_llm_call` in
`config.yaml`, allowlisted via the first-use consent prompt). It appends the pipeline above to
the user message when the message looks like a ticket (strong/weak code keywords; see
`hooks/lib/detect.py`). Document-writing keywords get at most a short reminder; plain chat gets
nothing. Hooks register per session open, so a session started before the hook was added will
not fire it.

- Verify: `hermes hooks doctor` and `hermes hooks test pre_llm_call`
- Payload shape for `hooks test`: put the message at the TOP level, `{"user_message": "fix bug login endpoint di repo"}` — `_payload_fields` (agent/shell_hooks.py) sweeps non-top-level keys into `extra`, so a fixture already wrapped in `extra` nests twice (`extra.extra`) and the hook silently no-ops. The direct pipe `echo '{"hook_event_name":"pre_llm_call","extra":{"user_message":"…"}}' | <hook>` is the fallback proof.
- Revoke: `hermes hooks revoke "hooks/ticket-rules.py"` (the command path as declared in `config.yaml`)
- The reminder hook cannot stop coding from starting; the gates below stay model-enforced, so the plan still has to be written before edits.
- If your agent runs a background skill review (Hermes logs it as `origin=background_review` in `~/.hermes/logs/agent.log`), skill files have a second concurrent writer that merges lessons and bumps versions mid-flight. Read a skill file fresh before every write, and when a diff shows hunks you did not write, classify each hunk against your own edits before reacting — a version bump or bullet you did not author is that writer, not a scope violation; report it as a second author rather than reverting it.

A second hook enforces the retention rule mechanically: `hooks/tests-not-committed.py`
(`pre_tool_call`, matcher `terminal`) blocks `git commit`/`git push` whenever the target repo holds
a new test file — untracked or staged-added — matching `tests/`, `__tests__/`, `*.test.*`,
`*.spec.*`, `test_*.py`, `*_test.py`, `*.feature`, unless its path matches the policy allowlist.
It resolves the target repo through `-C <path>`, the tool's `workdir`, and preceding `cd` segments.
Rewriting the script changes its mtime and invalidates consent — re-approve via the consent prompt,
then run `hermes hooks doctor`.
- Revoke the guard: `hermes hooks revoke "hooks/tests-not-committed.py"`

## Gates (non-negotiable)

- No coding before the test plan and coding plan exist.
- No "done" without having executed the test plan; a written plan is not a result.
- No git push, merge, PR, `reset --hard`, or `clean -fd` without an explicit instruction.
- No `any`, `@ts-ignore`, `eslint-disable`, skipped build, or skipped test to make a check pass.
- No temporary validation files left behind; delete scratch specs you created. Per the retention policy, scaffolding test files go once green — capture the runner output for the report BEFORE deleting.
- Never commit or push a scaffolding test file: the `pre_tool_call` hook blocks `git commit`/`git push` while one is untracked, staged, and not allowlisted. That block is the rule working, not a bug to work around.
- Never call a phase complete while a known failure exists — state it.

## Third-party playbook stacks

An agent-style stack installed alongside this kit does not replace this pipeline. When the user
asks to run a ticket through one, bind it to this order:

- **The gate wins.** Test plan, then coding plan, then code. A playbook that jumps straight to
  architecture and delegation may run only inside Stages 3–4, after the matrices exist.
- **Never let a playbook reach its shipping tail** — opening a PR, shipping, babysit, autopilot —
  unless the user asked for push/PR/merge by name; those steps push, force-push and squash-merge.
- **A stack in another profile has none of this kit's enforcement** and none of your project
  memory. Paste the gate rules into the prompt there, or run the gate here and hand the approved
  plan over.
- **Translate port instructions instead of obeying them verbatim.** Another harness's tool and
  model names may not exist here; leave model roles unset so subagents inherit the session model.

More detail: `docs/third-party-stacks.md` (repo-level).

## Pitfalls

- **Tests written after the code they test.** They only mirror the implementation. Write the matrix from the ticket first, then make it green.
- **A test that asserts the bug.** Grep the suite for the exact old output (the number, status code, or column value the bug produces) before coding; the fix is incomplete until that assertion changes in the same commit.
- **Green from a partial run.** Running only the new test file hides breakage elsewhere; the report must show the full suite.
- **Loop spinning on an unchanged fix.** Re-running the same fix hoping for a different result burns the iteration cap. Each iteration must change something the evidence names; on a plateau, pivot the approach or attack the shared premise instead of repeating the fix.
- **Test plan without numbers.** "Denda tidak muncul" is not a test; "`denda_rp` 0 di 3 baris, 0 baris kas denda" is.
- **E2E reusing someone else's dev server.** `reuseExistingServer: true` will happily drive a different project that owns the port; use a dedicated port with `strictPort`.
- **Fake evidence.** Never write a result table from memory; paste what the runner printed.
- **A red check that is your own harness's bug.** When a verification script you wrote fails, prove the failure is the artifact's before "fixing" the artifact: run the checker against the untouched backup first. A validator that rejects valid shapes (a parent key whose value is nested below it, a payload wrapped one level too deep) fails a green artifact and sends the loop chasing the wrong side. Fix the checker openly and re-run — never loosen the expected value to make a broken check pass.
- **Removed tests reported as coverage.** If the user asks to delete tests you added, delete them
  only after copying them outside the repo, report the backup path, and then quote the suite counts
  as *existing-suite* numbers. Saying "463 passed" after removing the new tests implies the feature
  is covered when it is not.
- **Pre-existing failures reported as yours.** "467 passed, 3 failed" is indistinguishable from a
  regression you caused. Run the same failing subset in a worktree of the base branch
  (`git worktree add /tmp/base origin/staging`, cd there, same runner), report the baseline counts,
  then `git worktree remove /tmp/base --force`. Say "pre-existing, fails on <base> too" only after
  that comparison.
- **A single failure that never reproduces is flaky, not a build break.** Before blaming the code,
  run that one test alone (`cargo test <name>`, `pytest <file>::<test>`, `--test-name-pattern`), then
  the full suite again, and report all three runs. Common cause in suites that pass in isolation:
  two tests in the same process sharing a temp path keyed only by PID, so one's `remove_dir_all`
  hits the other's freshly written files and fails with `DirectoryNotEmpty`/`EBUSY`. Say "flaky by
  design of the test, isolated run and full rerun green" — never "the build is broken" on one red.
- **One uncollectable file aborts the whole run.** A stray manual/scratch test with a module-level
  `NameError` stops collection before any test executes, which reads as "the suite is broken".
  Exclude it explicitly (`pytest --ignore=tests/manual`), name it in the report, and never present
  the excluded path as covered.
- **"Clean this up" treated as an instruction to start editing.** A cleanup ticket arrives with no acceptance criteria, so the measured findings list (file sizes, duplicate counts, `any` count, comment noise with evidence) is the specification. Measure, list, get the scope approved, then edit — otherwise the report cannot say what improved.
- **Same-name duplicates treated as identical.** Diff the bodies before consolidating; a shorthand variant merged into the canonical formatter silently changes numbers on screen.
- **`any` replaced quietly.** Typing an `any` with the real library type exposes latently invalid values (`docx.VerticalAlign.MIDDLE`, a member that never existed, sat there as `undefined`). Fix and disclose it as the one intended behaviour change — do not report the whole refactor as no-op.
- **Deleting the test file before capturing evidence.** The runner output *is* the deliverable once the file is gone — paste the real counts into the report first, then delete, then confirm `git status` shows the file gone.
- **Keeping scaffolding "because tests are good practice".** Retention is a policy decision, not a per-ticket whim: under the default policy scaffolding goes after green and regression tests stay. Say which policy a kept or deleted file follows.
- **A hand-rolled comment stripper as refactor proof.** Regex/state-machine strippers desync on `//` inside strings, regex literals and template literals, and report false failures. Use the AST.
- **Deleting a scratch test and committing in one shell line.** The `tests-not-committed.py` guard inspects the repo *before* the command runs, so `rm tests/test_x.py && git commit ...` still blocks even though the file would be gone by commit time. Delete the file in its own call, confirm `git status --porcelain` no longer lists it, then stage and commit in a second call.
- **Switching ticket branches with another ticket's work in the tree.** Commit (when authorized) or `git stash push -u -m <ticket>-fixes` before `git switch`; uncommitted changes otherwise ride into the other ticket's base and make its test counts and diff unreadable. Return to the original branch and `git stash pop` before reporting.
- **A fix commit that silently contains the whole uncommitted feature.** On a branch whose feature work was never committed, the first "fix" commit necessarily includes it. Split by concern when possible and state the true diff in the report instead of presenting it as a fix-only change.
- **Replacing a store/limiter protocol without updating its test doubles.** When production starts calling `consume_token()` but a test subclass still overrides `incr()`, the failure-path test no longer exercises the failure. Grep the test tree for the old method name and update every double in the same change; run the failure-path test to confirm it still fails for the intended reason.

## Verification

- Every `R#` appears in the final report with PASS/FAIL
- Every `IT-#`/`E2E-#` from the plan appears in the result table
- Working tree free of scratch artifacts
- Every remaining red is classified: caused by this change (fix it) or proven pre-existing by
  running the same subset on the base ref
- Remote state verified with `git fetch` + `rev-parse`, not assumed
- Refactors: AST equivalence reported, moved blocks hashed, before/after metrics in a table
- When Stage 5 looped: the iteration log is in the report, and the closing run is the full suite, not only the affected subset

## Bundled files

- `references/cross-repo-continuation.md` — finishing a ticket whose work landed on another branch/repo.
- `references/behaviour-preserving-refactor.md` — measure, dedupe, move-and-hash, prove comments-only.
- `docs/third-party-stacks.md` (repo-level) — binding an external agent-style stack to these gates:
  which skills are safe at which stage, the dangerous tail, the runtime mismatches to translate.
- `scripts/ast-equivalence.mjs` — AST diff against a git base; prints OK when only comments changed.
