# Installing on Hermes

```bash
git clone <this repo> && cd ticket-run
./install.sh --yes                 # default profile (~/.hermes)
./install.sh --profile work --yes  # or a named profile (created if missing)
hermes hooks doctor               # expect: scripts OK, not allowlisted yet
```

## The one human step: hook consent

Hermes refuses to run shell-hook scripts it has never seen. After install,
`hermes hooks doctor` reports `not allowlisted — hook will NOT fire at
runtime`. That is the feature working, not an installer bug. Approve once:

- **interactive:** start any session; the TTY consent prompt asks about the
  two new hooks — answer yes.
- **non-interactive:** launch the first session with the environment variable
  `HERMES_ACCEPT_HOOKS=1` (or the `--accept-hooks` launch flag).

Verified subtlety, do not lose time on it: `hermes --accept-hooks hooks doctor`
does **not** approve anything — the flag rides session creation only. A bare
`hermes -p X --accept-hooks hooks doctor` run does nothing to the allowlist,
and a profile whose config.yaml only contains hooks (no model settings) cannot
even boot a session to approve them. Use the TTY prompt.

## Verify the injection

```bash
hermes hooks test pre_llm_call --payload-file fixtures/hook_payloads/top_level_msg.json
# expected: parsed {"context": "[Ticket workflow active] ... TEST PLAN ..."}
```

Payload shape, verified against the dispatcher: `--payload-file` JSON is
merged into the synthetic payload, and non-top-level keys are swept into
`extra`. Put the message at the TOP level (`{"user_message": "..."}`);
wrapping it in `{"extra": {...}}` nests twice and the hook silently no-ops.
For `pre_tool_call`, the CLI fixture key is `args` (mapped to `tool_input`
on the wire), not `tool_input`.

## Uninstall

```bash
./install.sh --uninstall               # default profile
./install.sh --profile work --uninstall
```

Removes the hook directory and the config entries (a pre-install backup is
kept as `config.yaml.bak-ticketworkflow-<ts>`). **Skills are left in place** —
they may carry your edits; delete `~/.hermes/skills/<name>` by hand if you
really want them gone.

## Re-approval after edits

Editing a hook script changes its mtime and invalidates consent: `hermes hooks
doctor` will flag drift. Re-approve via the TTY prompt (or
`HERMES_ACCEPT_HOOKS=1` at the next session start), then re-run doctor.
