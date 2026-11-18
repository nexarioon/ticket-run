# Using the kit on other harnesses

The five skills are plain SKILL.md files and load on any harness that reads the
Agent Skills tree (Claude Code, Cursor, Codex CLI, OpenCode, ...). Copy
`skills/*` into your harness's skills directory and the pipeline text arrives
with every ticket — that is the portable half.

The two hooks are the half that needs translating:

| Kit hook | Claude Code | Cursor | generic harness |
|---|---|---|---|
| `pre_llm_call` injection | SessionStart / UserPromptSubmit hook writing context | rules file pinned at session start | any "inject context before the model runs" facility |
| `pre_tool_call` commit guard | PreToolUse hook matching Bash | command-blocker / preflight rule | any "intercept tool call, allow/deny" facility |

Porting rules:

1. Keep the contracts: the injection prints `{"context": "..."}`-equivalent
   for ticket-looking messages; the guard blocks commit/push while a NEW test
   file is untracked or staged-added, unless policy-allowlisted.
2. Keep the guard's inspection-before-execution semantics: `rm <test> && git
   commit` in one line still blocks. Deleting then committing as two steps is
   the intended workflow, not friction.
3. The regexes and policy loader (`hooks/lib/`) are stdlib Python — reuse them
   verbatim; only the I/O shim differs per harness.
4. Without any hook facility, the kit degrades honestly to skill text: the
   pipeline still reads, but nothing enforces it mechanically.

What we deliberately do not ship: playbooks that push, force-push,
squash-merge, or install watchers. A stack that does should be bound to this
pipeline instead — see `docs/third-party-stacks.md`.
