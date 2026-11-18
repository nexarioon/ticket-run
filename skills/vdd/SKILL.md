---
name: vdd
description: "Validate every ticket requirement before moving phases."
version: 1.0.0
author: Fendi Permadi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [validation, vdd, requirements, acceptance, quality-gates]
    related_skills: [vdd-workflow, coding-plan, test-driven-development]
---

# Validation-Driven Development (VDD)

Every requirement from the ticket must be shown to work before the phase is called done. Unlike TDD, VDD does **not** require permanent test files: validation is derived from ticket requirements using existing tooling plus temporary, throwaway checks.

## When to Use

- After an approved Coding Plan, before and after every implementation phase
- Any ticket work where acceptance criteria exist
- Don't use to audit an already-built branch ("what's done vs not done on this ticket"): no implementation phase is being validated — use the ticket-scoped audit in `git-change-explanation`
- Don't use for: exploratory spikes with no acceptance criteria (use `spike`), or repos that mandate real test files (use `test-driven-development`)

## Requirement First

Before implementing anything:

1. Read the ticket carefully.
2. Identify every requirement.
3. Identify acceptance criteria.
4. Infer missing acceptance criteria if necessary, and mark them `(inferred)`.
5. Read the approved Coding Plan.
6. Work only on the current phase. Never implement future phases.

## Validation Planning

Before writing code for the current phase, define:

- **Requirement** — what is being implemented (`R#`)
- **Validation** — how it will be verified
- **Expected Result** — what proves it is satisfied

Example:

```
Requirement: Display booth pricing cards.
Validation:
  - Render the component
  - Three booth cards exist
  - Price is visible
  - Facilities are displayed
  - CTA button exists
Expected Result: all cards render correctly.
```

Implementation must not begin until the Validation Plan is defined.

## Validation Strategy (priority order)

1. Existing automated tests
2. Temporary validation script
3. Manual functional verification
4. Lint
5. Type checking
6. Build verification

Validation is requirement-driven. Lint and build success alone never prove a requirement works.

## Temporary Validation

If existing tests don't cover the requirement, create a temporary check: `node -e`, `tsx` inline, a heredoc, or a scratch script. **Remove it immediately after execution.**

Never create `*.test.ts`, `*.spec.ts`, or `__tests__` unless explicitly requested.

## Existing Tests

If tests already cover the requirement: run only the relevant tests, fix failures, re-run. Do not duplicate existing coverage.

## Manual Verification

When automation isn't possible, verify by hand and say exactly what you checked.

Frontend: component renders, layout correct, responsive behavior, button interaction, form validation, API request succeeds, no console errors.

Backend: endpoint responds correctly, validation behaves, database operations succeed, authorization behaves.

## Execution Order

1. Requirement validation
2. Existing tests (if available)
3. Lint
4. Type check
5. Build
6. Manual verification

If any step fails: read the actual error, fix the root cause, re-run. Never continue with known failures.

## Forbidden Shortcuts

Never pass validation by using `any`, `@ts-ignore`, `eslint-disable`, skipping the build, or skipping validation — unless explicitly instructed. Fix the underlying problem.

## Phase Completion Criteria

A phase is complete only when all hold:

- Current phase matches the approved plan
- Every requirement for the phase is validated
- Existing tests pass (if applicable)
- Lint passes
- Type checking passes
- Build succeeds
- Manual verification done where needed
- No temporary validation files remain

Only then may a commit be suggested.

## Validation Summary (required output)

```
## Requirements Verified
R1 — <requirement> — PASS

## Validation Methods
<how each was checked>

## Commands Executed
- npm run lint
- npm run typecheck
- npm run build
- npm run test

## Results
Lint ✅  Type Check ✅  Build ✅  Tests ✅  Manual ✅

## Known Limitations
<what could not be validated — never hide these>
```

## Commit Gate

After validation: generate the summary, suggest a Conventional Commit message, list modified files, then **wait for developer approval**.

Never push, merge, create a PR, or continue to the next phase automatically.

## Final Checklist

- [ ] Ticket requirements reviewed
- [ ] Current phase identified
- [ ] Validation Plan created
- [ ] Requirement validation completed
- [ ] Existing tests run when available
- [ ] Lint run
- [ ] Type check run
- [ ] Build run
- [ ] Manual verification completed
- [ ] Temporary validation removed
- [ ] Validation Summary written
- [ ] Conventional Commit suggested
- [ ] Waiting for developer approval

## Pitfalls

- **Green build bias.** Treating `npm run build` succeeding as validation; it proves compilation, not behavior.
- **Leaving scratch files.** A leftover `tmp-check.ts` pollutes the diff and gets committed. Delete in the same turn you create it.
- **Validating the phase you wish you built.** Check against the plan's `R#`, not against what you ended up writing.
