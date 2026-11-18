---
name: e2e-browser-test-automation
description: Use when automating E2E tests of a live site (WDIO, BDD).
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, e2e, webdriverio, cucumber, bdd, page-object]
    related_skills: [dogfood, test-driven-development, live-app-data-seeding]
---

# E2E Browser Test Automation

## When to use

- A take-home / hiring assignment asks for an automation script against a public site.
- Building or extending a WebdriverIO/Playwright + Cucumber suite where the app is only reachable as a running UI (no API, no fixtures).

Not for unit-level TDD (see `test-driven-development`) or exploratory bug hunting (see `dogfood`).

## Procedure

**1. Flatten the brief into acceptance steps.** Every bullet becomes one step; for each, name what the step must *prove*, not only what it clicks. Keep the brief's own domain words (Reksa Dana, Pasar Uang, Syariah) in feature files — they make the suite readable to the person grading it.

**2. Recon the live site before writing tests or a plan.** Drive the real browser through the exact flow once and record, per step: the resulting URL, which element actually had to be clicked (and what was blocking it), and the text/DOM that proves success. This is mandatory — briefs and screenshots go stale, and example numbers in them are snapshots of live data.

Per step: `page_info()` for the real URL, then `js(...)` to dump candidate elements (`aria-label`, `href`, `placeholder`, `data-*`, semantic class names) and the surrounding text. Fall back to CDP `DOM.getBoxModel` + `click_at_xy` only for controls with no addressable selector.

**3. Pick selectors that survive a deploy.** Priority: `aria-label` / `placeholder` / role / link `href` > domain-semantic class (`product-item-card`, `product-name`) > visible text > `nth-child`. Never ship hashed CSS-module class names (`SearchBox_search-box__TeZqR`, `Header_header__gtmFw`, `btn_SSfdi`) — the hash changes on the next build, so the suite goes red with no app change.

**4. Scaffold POM + BDD.** `features/` one per scenario; `step-definitions/` thin — call a page object, then assert; `pageobjects/` one per page with intent-named methods (`applySyariahFilter()`, not `clickBtn2()`); `utils/` for parsing, aggregation, formatters. Arithmetic or text parsing inside a step definition is the single clearest design smell a reviewer will find — move it to `utils/`.

**5. At least one assertion per step, on that step's outcome.** Strength order: relational assertion (sum of parts equals parsed total) > presence/absence contrast (filtered-out item gone, filtered-in item present) > URL/title/heading > "list is not empty". If a step has nothing to assert, delete the step.

**6. README: setup, run, assumptions, findings.** Findings matter as much as code — record what was hidden behind a trigger, what the counts actually mean, what was excluded and why.

**7. Deliver via the channel named by the LATEST instruction.** A brief's PDF and the accompanying email routinely contradict each other (one allows a zip, the other forbids it). The newest message wins; when in doubt, submit a view-permission link rather than an archive. Keep a real local git repo with history, add no public remote when the brief forbids publishing, and verify by cloning/running from a clean copy.

## WebdriverIO 10 specifics

- **Strict selectors are on by default.** `$('.product-item-card')` throws `StrictSelectorError` when several elements match. Use `$$(sel)[0]` for "first match" and reserve `$` for genuinely unique elements.
- **`await $$()` does not hand back a plain array.** Calling `.map()` on it returns another chainable, so `Promise.all(names.map(el => el.getText()))` fails with "object is not iterable". For list text, one `browser.execute` over `querySelectorAll` is both correct and cheaper than N round trips.
- **Cucumber globals are not injected under ESM.** Every step file needs `import { Given, When, Then } from '@wdio/cucumber-framework'`.
- **One definition per step text.** A shared `Given` duplicated in two step files makes every scenario referencing it "pending" with a `Multiple step definitions match` reason, which reads like a broken runner.
- **Driver management is automatic.** A Chromium build whose version string is not a released Chrome (Brave reports `149.1.91.168`) logs "Chromedriver ... don't exist" and then resolves a compatible driver anyway. Do not pin a driver package to the local browser version; the reviewer's Chrome will differ.

## Always-on pitfalls

- **Set the desktop viewport before anything else.** Below the desktop breakpoint nav items and menus collapse into a mobile bottom-nav, so a flow described in the brief simply does not exist at default window sizes.
- **Custom controls are not real inputs.** Design-system checkboxes/toggles usually hide the `<input>` (`label.checkbox-kit > input[type=checkbox]` + a styled `<span>`). Click the visible label/span; assert state through `input.checked` or the resulting UI change.
- **Panels hide their controls.** Filters, sort and compare live behind a "Filter"/"Urutkan" trigger. Click it, then wait for the option group before querying options — a query before that returns an empty list that looks like a wrong selector.
- **A clamped panel still reports visible.** A collapsible held at `max-height: 0` keeps `isDisplayed() === true` for its children, so an expand-if-collapsed branch silently skips the click. Check `isClickable()` on the control inside the panel instead.
- **Checkbox state may live only in the DOM event.** Some design-system checkboxes never reflect state in `input.checked`; confirm the real signal (a summary sheet slot, a URL query, a row count) and assert that, not the input property.
- **Wait on the target element only** (`waitForDisplayed`, `waitForClickable`, `waitUntil(predicate)`). No sleeps and no wait-on-page-load: these UIs are client-rendered and hydrate after load fires.
- **Never hardcode a number the brief shows as an example.** Assert the invariant (the categories sum to the reported total) and parse everything else from the page.
- **Parse locale numbers before comparing.** Indonesian pages use `.` for thousands and `,` for decimals (`+5,45%`, `Rp 10.000`) plus magnitude suffixes (`1,35T`, `510,61M`). One parser in `utils/`, unit-tested.
- **Do not assert values that move with the market or the deploy date** — returns, AUM, promo periods, total result counts. Assert structure, relations, and stable contrasts.
- **A grouping label may render no number.** Sum only nodes that actually carry a count; an "Semua/All" row is typically count-free and must be excluded.
- **Duplicate CTAs are normal.** Multi-card layouts repeat the same button ("Buka" on every card) — scope to the card (`[data-item="X"] button`) instead of indexing into the page-wide list.
- **Note the brief's integrity clause and act on it.** If it asks for the candidate's own work, deliver code the user can defend line by line: explain each non-obvious decision, and offer to have them rewrite/talk through a block rather than handing over opaque generated files.

## Output shape for "analyze this assignment" requests

Reply in the user's language, keep code/identifiers in English. Include: (1) deliverables checklist; (2) stack recommendation tied to what the hiring team says they use; (3) per-step table — step, real URL/selector verified by recon; (4) the assertion to use for each step; (5) pitfalls found during recon; (6) proposed repo tree; (7) day-by-day plan sized to the deadline. Label anything not yet verified as unverified instead of smoothing it over, then offer to scaffold.

## References

- `references/cermati-recon.md` — verified route map, selectors, and count semantics for the cermati.com SEIT/Indodana take-home (Skenario 1 & 2).
