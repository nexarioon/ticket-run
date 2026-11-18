# FAQ

**The local hook blocks my commit because of a new test file. Bug?**
The rule working. A test file created to drive the feature is scaffolding:
delete it (after capturing the runner output for your report) and re-run the
git command. If the test is genuinely permanent, get the user's explicit
approval first — on the kit author's machine that approval is also what lets
the commit through, because the guard cannot read intentions.

**`hermes hooks test` says the hook "contributed nothing".**
Your payload file wraps the message in `{"extra": {...}}`. The dispatcher
sweeps non-top-level keys into `extra` at fire time, so a fixture that already
wraps it nests twice. Put `user_message` at the top level. For `pre_tool_call`
fixtures the CLI key is `args`, mapped to `tool_input` on the wire.

**`hermes --accept-hooks hooks doctor` did not approve the hooks.**
Correct, it cannot: the flag rides session creation only. Approve at the TTY
prompt of a real session, or launch the first session with
`HERMES_ACCEPT_HOOKS=1`.

**A skill file changed while I was editing it.**
If your agent runs a background skill review (Hermes: turns logged with
`origin=background_review`), the skill library has a second concurrent writer
that merges lessons and bumps versions mid-flight. Re-read a skill file before
every write, and when a diff shows hunks you did not write, classify them
against your own edits before reacting — report a second author, do not
revert blindly.

**Why are the kit's own tests permanent?**
The kit is a test suite, not a feature app. Its `regression-permanent` default
exists precisely so regressions stay locked; shipping a repo that deletes its
own regression tests would contradict the policy it preaches.

**CI has not actually run yet.**
The workflow file is in place (`.github/workflows/ci.yml`) but only executes
once the repo has a remote — push, and the matrix (Python 3.11/3.12 + hygiene
+ frontmatter gates) runs on GitHub's runners.
