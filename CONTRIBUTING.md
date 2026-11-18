# Contributing

Short version while the kit is at 0.1.0 (this file is expanded in phase P8):

- Every change goes through the kit's own pipeline: requirement, test plan, coding plan,
  implementation, full suite, report. The repo should always be an example of what it ships.
- Tests in this repo are **permanent** — it is a test suite, not a feature app. The
  `regression-permanent` default exists precisely so regressions stay locked.
- Hygiene gate (CI-enforced): zero hits for personal paths, employer/client project names,
  university references, or student IDs. CI greps a denylist of such tokens; run the same
  check locally before pushing, and never paste real examples of them into docs — use
  placeholders like `/home/<you>`, `<company-project>`, `<university>`, `<student-id>`.
- Skill frontmatter must validate: `name` equals the directory name, `description` at most
  60 characters.
- If your agent runs a background skill review, expect a second concurrent writer on
  `SKILL.md` files: re-read a file before every write, and classify unknown diff hunks before
  reacting to them.
- Hooks are stdlib-Python only. No pip dependencies, no network at install time.
- Versioning: `VERSION` is the kit version; each skill's frontmatter `version` tracks its own
  content and may bump independently.
