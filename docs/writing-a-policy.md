# Writing a policy

Policy is a flat YAML subset (stdlib parser, no dependencies):

```yaml
language: en                 # en | id — message text for hooks and reports
skills: [vdd-workflow, coding-plan, clean-code]
retention: regression-permanent   # or: strict | keep-all
test_globs_allow: [tests/regression/**, tests/contract/**]
```

## Where the file lives

Search order, first hit wins:

1. `$TICKET_POLICY` (environment)
2. `<repo>/.ticket-workflow.yaml`
3. `~/.hermes/ticket-workflow.yaml`
4. the kit default (`policy/default.yaml`, copied on install)

## Retention modes

- `regression-permanent` (default): a test that encodes a real bug, an
  external contract, or a reported regression stays in the suite forever;
  scaffolding written only to drive the feature is deleted once green (its
  runner output is quoted in the report first).
- `strict`: every new test file goes after green — even regression locks.
  Use only on a repo whose owner insists; the guard will block commits until
  each file is deleted or allowlisted.
- `keep-all`: nothing is deleted.

## The allowlist

`test_globs_allow` names paths the commit guard must NOT block (glob style,
`fnmatch`, `*` crosses slashes). Typical use: a regression directory the team
agreed to keep:

```yaml
test_globs_allow: [tests/regression/**]
```

With this in place, `tests/regression/anything.test.ts` may be committed;
`tests/test_new.py` still blocks until deleted or approved.

## Class presets

`policy/profiles.example.yaml` ships three starting points — `money`,
`api-contract`, `ui` — with runners, retention, and allowlists. Copy the
fitting block, adjust, and keep it in the repo so every agent that lands there
reads the same rules.
