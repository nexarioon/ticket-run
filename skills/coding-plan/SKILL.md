---
name: coding-plan
description: "Write an approved coding plan before any implementation."
version: 1.0.0
author: Fendi Permadi, Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, requirements, scope, phases]
    related_skills: [vdd-workflow, vdd, clean-code]
---

# Coding Plan

Always create a Coding Plan before writing code. The plan is a document the human approves, not a step you narrate and skip.

## When to Use

- Starting a new feature, ticket, or bug fix
- Any change touching more than one file
- Don't use for: one-line fixes, exploratory reading, pure questions

## Requirement analysis (before the plan)

Tickets describe the code as their author believed it to be. Verify in ONE batched recon pass before planning:

- **Every "current implementation" claim.** Open the file and line the ticket names (auth dependency, rate limiter, model, endpoint) and check whether it is actually *wired*: `grep -rn "<fn_name>(" app/`. A helper that exists but no endpoint calls is not existing support — it is a starting point that does not meet the requirement, and the plan must say why.
- **Verify against the default branch, not the ticket's prose.** With no local checkout, clone read-only into the scratch dir (`gh repo clone ORG/REPO -- --depth 1`) or read one file via `gh api repos/ORG/REPO/contents/PATH --jq .content | base64 -d`, then grep. Ticket line numbers decay — cite the symbol you grepped and the line you actually saw, never the ticket's.
- **The data shape the contract depends on.** Confirm the exact paths and whether they are guaranteed: timestamp at root vs nested in `metadata`, nullable summary/content, missing publish dates. A fallback expression in existing code (`article.get("updated_at") or metadata.get("updated_at")`) is positive evidence the field is not guaranteed — treat it as backfill + index work, and write the fallback order into the contract instead of picking one silently.
- **What already does part of the job but fails a stated rule** (in-memory limiter vs "shared across processes", env plaintext keys vs "stored hashed", per-IP vs per-partner quota). Name the existing hook and the exact rule it breaks; that is what makes the reuse-vs-new-code decision defensible.
- **Blast radius of the new surface**: router registration point, global auth/premium/rate-limit middleware that would also apply to it, indexes the query needs, and where its tests belong. Cheap to find now, expensive after implementation.

Output the analysis in three blocks, in this order: **verified current state** (file:line evidence, no adjectives) → **blocking decisions** (the ticket's D-n / open questions; any decision that fixes the response contract or needs legal/business sign-off blocks planning — say so instead of picking a default) → **ordered work items** mapped to a concrete file, collection, index, and test location. Then the risks, each anchored to a measured fact rather than speculation.

## The Ten Sections

### 1. Requirements

Summarize the ticket requirements as a numbered list (`R1..Rn`) with acceptance criteria (`AC1..ACn`). Mark inferred criteria as `(inferred)`.

### 2. Existing Architecture

Analyze the current implementation before proposing anything. Identify existing components, services, hooks, utilities, and tests. **Prefer reusing existing code over creating new code** — name the file you will extend, not just the file you will add. Reuse must not inherit a lossy transformation: a UI serializer that truncates or reshapes for display (a summary capped for cards) cannot feed an external contract — map from the source document instead.

### 3. Scope

Two explicit lists: **In Scope** and **Out of Scope**. Out-of-scope items are as important as in-scope ones; they are what stops scope creep later.

### 4. Files

- Files to modify
- Files to create
- Files to remove (if necessary)

Relative paths from the project root.

### 5. Components

Every component created or updated, with one line on what changes.

### 6. APIs

Every API consumed or modified: method, path, payload shape, and whether the contract changes.

### 7. State Management

Required state: where it lives, who owns it, and how it flows. Call out server vs client state explicitly.

### 8. Risks

Implementation risks and their mitigation. Include migration, backward compatibility, and performance where relevant.

### 9. Phase Breakdown

Break the work into small, reviewable phases. Each phase must:

- Have one clear objective
- Be independently testable
- Be small enough for a single commit
- Never depend on a future phase

Number phases `P1..Pn` and map each to the requirements it satisfies.

### 10. Testing Strategy

Per phase: unit tests, integration tests, manual testing checklist. **Do not implement tests yet** — this section states intent only; validation happens per the `vdd` skill.

## Approval Gate

Never start implementation until the Coding Plan is approved. Present the plan, then stop and wait for a yes. If the plan changes materially mid-work, re-present the affected sections.

Deliver it as a standalone markdown file (for example `~/projects/<repo>-<TICKET-ID>-Plan.md`) and keep the chat reply to the phase table, the findings that change scope, and the decisions you need — the user re-opens the file; the transcript is not the document.

## Verification

- Every `R#` maps to at least one phase in section 9
- Every "existing" component cited in section 2 was checked for call sites, not just for existence
- Blocking decisions are listed explicitly; the plan does not silently pick a default for one
- Every listed file exists or is truthfully marked "to create"
- Out of Scope is non-empty (if it is empty, the scope is too broad)
- Nothing in the plan requires a future phase to work
