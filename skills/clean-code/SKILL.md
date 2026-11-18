---
name: clean-code
description: "Clean-code bar: SOLID, DRY, KISS, plus review checklist."
version: 1.0.0
author: Fendi Permadi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [clean-code, solid, dry, kiss, review, typescript, react]
    related_skills: [vdd-workflow, coding-plan, requesting-code-review]
---

# Clean Code

This skill defines the quality bar every change must meet, at every task size — from the first line to the final review. Code that "works" but is unreadable, duplicated, over-abstracted, or inconsistent with the existing architecture is not acceptable output. It governs *how* code is written; it does not replace ticket planning.

## When to Use

Apply whenever:

- Writing new code (functions, components, modules, hooks, services, types)
- Editing or extending existing code
- Refactoring for clarity, structure, or performance
- Reviewing a diff, PR, or generated code
- Choosing between candidate implementations

It applies during every implementation, not on request.

## Core Principles

### Readability first

- Code is read far more often than written. Optimize for the next reader with no context.
- **Prefer readable over clever.** A one-liner needing mental decoding loses to three boring clear lines.
- Structure top-down: intent first, details below.
- Avoid deep nesting — flatten with early returns, guard clauses, and extracted functions.

### Simplicity (KISS)

- Solve the problem that exists, not the one that might.
- **No unnecessary abstraction.** A single implementation used once needs no interface, factory, or generic wrapper "for flexibility."
- Prefer the straightforward solution. If two approaches are equally correct, pick the one a mid-level engineer understands fastest.
- Every layer of indirection must earn its cost with a real, current requirement.

### DRY

- **Never duplicate logic.** Same rule, calculation, validation, or transformation in two places → extract it once, well named.
- DRY is about *knowledge*, not text. Look-alike code representing unrelated business rules must **not** be merged — that is false coupling.
- Before writing new logic, search the codebase for an existing utility, hook, or component. Reuse or extend it.

### SOLID (pragmatic, not dogmatic)

- **Single Responsibility** — one reason to change. If the name needs "and", split it.
- **Open/Closed** — extendable without modifying stable internals, but don't pre-build extension points nothing needs.
- **Liskov** — subtypes usable wherever the base type is expected, no surprising behavior.
- **Interface Segregation** — focused prop/interface types; no consumer depends on what it doesn't use.
- **Dependency Inversion** — depend on abstractions at architectural boundaries (API clients, storage, external services).
- These are pressure-tested heuristics, not a checklist. Don't force a strategy pattern onto two `if` branches.

### Separation of concerns

- Distinct responsibilities in distinct places: fetching vs. business logic vs. presentation vs. side effects.
- React: data/state logic in hooks or services, components focused on rendering and composition, pure logic in plain testable functions.
- A function that validates input *and* calls an API *and* formats display text gets split.

## Naming

- Names communicate intent, not type or implementation (`userList` over `arr`, `isLoading` over `flag`).
- Functions are verbs (`calculateTotalPrice`); booleans read as predicates (`isValid`, `hasPermission`).
- No abbreviations unless domain-standard; no `data`, `temp`, `helper`, `util2`.
- Match the codebase's existing conventions (casing, `use`/`is`/`handle` prefixes, file naming) over personal preference.

## Function and Component Size

- One thing, one level of abstraction. "and"/"then" in the description means split.
- Several small named functions beat one long function with section comments — a section comment is a split signal.
- Extract complex conditionals into a named function or variable (`isEligibleForDiscount(user)`).
- **Prefer early returns** over nested `if/else` chains.

### React components

- One clear rendering responsibility. Mixed unrelated concerns → subcomponents.
- Extract repeated JSX into reusable components instead of copy-pasted markup.
- Keep components declarative: derived logic into named variables/hooks above the `return`, not inline in JSX.
- Prefer composition (children, slots) over many boolean props branching internally.
- Focused prop lists; a dozen loosely related props is a decomposition signal.

## Error Handling

- Handle errors at the layer with enough context to respond meaningfully; don't swallow, don't handle the same error at every layer.
- Fail fast and explicitly: validate preconditions early, return or throw clear errors.
- Typed, specific errors over generic `Error` or stringly-typed handling, where conventions allow.
- **No empty `catch` blocks.** If an error is intentionally ignored, comment why.
- Separate user-facing error handling from internal (logging/monitoring) handling; never leak internals to users.
- Handle rejected promises explicitly — no unhandled floating promises.

## TypeScript

- Prefer precise narrow types. No `any`; use `unknown` and narrow explicitly.
- Let inference work; annotate exported function return types where it aids clarity.
- Model domain state with unions/discriminated unions, not boolean flags that can form invalid states (`status: 'idle' | 'loading' | 'success' | 'error'`).
- `interface` for extensible object shapes and public contracts; `type` for unions/utilities — follow the codebase.
- No `as` assertions to silence real mismatches.
- Derive with utility types (`Partial`, `Pick`, `Omit`, `Record`) from one source of truth.
- Shared types live in their canonical location, not redefined locally.

## Refactoring

- Small, safe, verifiable steps. Never mix a refactor with a behavior change in one edit.
- Remove dead code encountered nearby: unused variables, functions, imports, components, files.
- **Delete commented-out code** — version control keeps history.
- Opportunistically fix small local issues in touched code if low-risk and in-scope; flag large unrelated refactors instead of doing them.
- After refactoring, verify behavior unchanged.

### Behaviour-preserving refactor ("clean this repo up")

- **Measure first, then plan.** Turn file sizes, duplicate definition counts, `any` counts and
  decorative-comment counts into a numbered findings list with the evidence next to each item.
  That list is the specification on a cleanup ticket, which has no acceptance criteria.
- **Identity, not just green tests.** For code that moves, hash the block before and after and
  show the hash matches. For generated artifacts (docx, pdf, xlsx, API JSON), snapshot before the
  first edit. Capture the baseline *before* touching anything; afterwards there is nothing to
  compare against.
- **Move, never rewrite.** Cut the block to the new module, add only `export`, leave the body
  byte-identical. Locate blocks by marker text, not remembered line numbers.
- **Root-cause the duplicate count.** After a dedupe pass, the count must be exactly 1; an
  indented copy inside a component survives a line-anchored regex.
- **Same name is not same behaviour.** Diff bodies before merging; a variant with different
  output gets its own honest name instead of being folded into the shared helper.
- **Type the `any` you touch.** Replacing `any` with the real type costs nothing at runtime and
  exposes latent bugs; fix what it surfaces and report it as an intentional change.

Full recipe with the commands and scripts: `references/behaviour-preserving-refactor.md`.

## Performance

- Be cost-aware without premature optimization: no obvious waste (needless re-renders, redundant network calls, O(n²) on growing data, recomputed invariants).
- React: memoize only for demonstrable cost (large lists, expensive renders, referential-equality-sensitive children) — not reflexively.
- Paginate/virtualize/stream large data when the codebase already supports it.
- Move invariant work out of hot paths (render, loops, handlers).
- Never trade readability for unmeasurable micro-optimization.

## Accessibility

- Semantic HTML (`button`, `nav`, `header`, `main`, `label`) over clickable `div`/`span`.
- Interactive elements keyboard-operable with visible focus states.
- Accessible names for interactive/meaningful elements (`aria-label`, `alt`, associated `<label>`) — no unnamed icon-only buttons.
- Logical heading hierarchy and reading order.
- Don't convey state by color alone; respect contrast.
- Manage focus for dynamic UI (modals, route changes).

## Comments

- **Explain WHY, never WHAT.** `// increment i` above `i++` must be omitted.
- Good comments capture non-obvious reasoning: unusual approach, workaround, constraint, guarded edge case, or a ticket/spec link.
- If a comment explains *what*, rewrite the code to be self-explanatory instead.
- Keep comments current; a stale comment is worse than none.

## Architectural Consistency

- **Follow the existing architecture**: folder structure, layering, state management, styling, API/service patterns.
- When new code doesn't fit an existing pattern, extend the pattern rather than introducing a rival — and if the pattern is genuinely unsuitable, flag it explicitly instead of silently diverging.
- One well-understood way of doing things beats several competing "correct" ways.

## Final Review Checklist

**Readability & simplicity**
- [ ] Understandable by a new team member without explanation?
- [ ] Cleverness replaced with the obvious approach?
- [ ] No abstraction that doesn't earn its complexity?

**Duplication & dead code**
- [ ] No logic duplicated that should be extracted?
- [ ] No dead code (unused vars, functions, imports, files)?
- [ ] No commented-out code?

**Structure**
- [ ] Every function does one thing at one abstraction level?
- [ ] Small and focused, early returns instead of deep nesting?
- [ ] Business logic separated from presentation and side effects?
- [ ] SOLID applied where genuinely applicable (no forced patterns)?

**Naming**
- [ ] Names communicate intent without needing a comment?
- [ ] Conventions consistent with the codebase?

**Errors**
- [ ] Handled at the appropriate layer, no empty `catch`, nothing silently swallowed?
- [ ] Edge cases and invalid states guarded explicitly?

**TypeScript**
- [ ] Types precise, no needless `any` or unsafe assertions?
- [ ] Shared types reused from their canonical location?

**React (if applicable)**
- [ ] Components small, composable, single rendering responsibility?
- [ ] Repeated JSX extracted?
- [ ] Memoization/performance techniques only where they pay off?

**Accessibility (if UI)**
- [ ] Semantic elements used?
- [ ] Interactive elements keyboard-operable with accessible names?
- [ ] Focus managed for dynamic UI?

**Comments**
- [ ] Comments explain *why*, not *what*?
- [ ] All comments accurate and current?

**Architecture**
- [ ] Follows the project's architecture and conventions?
- [ ] Any new pattern necessary and explicitly justified?

Only when every applicable item passes is the implementation complete.

## Pitfalls

- **Dogmatic SOLID.** Forcing interfaces and factories onto a 20-line module is a readability regression, not a quality upgrade.
- **Merging look-alike code.** Two similar blocks encoding different business rules become a false abstraction that breaks on the first divergence.
- **Silencing types.** `any`/`as`/`@ts-ignore` moves the failure to runtime; fix the type instead.
- **Refactoring without a baseline.** A cleanup with no before/after numbers (line counts, duplicate counts, artifact hash) cannot show it preserved behaviour, and green tests only cover the paths they touch.
- **Deleting duplicates before extracting the canonical one.** Do the extraction first, then delete copies and let the compiler report the misses.
- **Whole-file formatting as part of a targeted edit.** Running a formatter over a legacy file to format one new method rewrites unrelated lines and turns a small change into an unreviewable diff. Format only files that were already clean, or leave legacy formatting to its own change; check `git diff --stat` before reporting so the file count matches the intended surface.

## Verification

- Every applicable checklist item above is satisfied and gaps are stated, not glossed
- The diff introduces no new dead code or commented-out blocks
- Existing conventions were checked before introducing a new pattern
