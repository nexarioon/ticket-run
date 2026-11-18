# Contributing

## The pipeline applies to this repo too

Every change goes through the kit's own pipeline: requirement, test plan,
coding plan, implementation, full suite, report. The repo should always be an
example of what it ships. Two deliberate deviations, both stated up front:

- **Tests are permanent here.** This is a test suite, not a feature app; the
  `regression-permanent` default exists so regressions stay locked.
- **New test files need the author's explicit approval to commit** wherever a
  commit guard like ours is active. Expect the guard to block your first
  commit that adds a test file; that is it working.

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest tests/ -q     # 33 tests, no network, no services
python3 tools/check_hygiene.py           # personal-token denylist gate
python3 tools/check_frontmatter.py       # name == dir, description <= 60
```

Hooks are stdlib Python only: no pip dependencies, no network at install
time, fail-open on missing git. Keep them that way; the policy loader
parses a flat YAML subset on purpose.

## Hygiene rules

- Zero hits for personal paths, employer/client project names, university
  references, or student IDs. CI greps an assembled-token denylist; run
  `tools/check_hygiene.py` locally before pushing.
- Never paste real denylisted tokens into docs or tests as examples — use
  placeholders like `/home/<you>`, `<company-project>`, `<university>`. (The
  first draft of this repo's own CONTRIBUTING violated that rule and the
  gate caught it in the first commit.)
- If your agent runs a background skill review, expect a second concurrent
  writer on SKILL.md files: re-read before every write, and classify unknown
  diff hunks before reacting to them.

## Conventions

- New hook messages: add the key to BOTH `hooks/messages/en.json` and
  `hooks/messages/id.json`, with a `{placeholder}` for any dynamic part.
- Every new hook behavior gets a regression test that names the exact
  command that motivated it (see IT-16b for the shape).
- Versioning: `VERSION` is the kit version; each skill's frontmatter
  `version` tracks its own content and may bump independently.
- PRs: conventional subject (`feat(scope): …`), phase-sized commits, no
  `git add -A`, no force-push to shared branches.

