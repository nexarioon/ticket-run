# ticket-workflow-kit

A portable ticket discipline for coding agents: **plan first, test plan before code,
self-verify on the real surface, revise until green — never ship on a claim.**

This kit packages a working agent workflow (skills + enforcement hooks + policy) that turns
every ticket, bug report, or feature request into a verifiable pipeline:

```
1. Ticket intake        R1..Rn + acceptance criteria + assumptions
2. TEST PLAN            IT-xx / E2E-xx matrices with expected values, fixtures, exit criteria
3. CODING PLAN          phases mapped to test IDs, exact files
4. Implementation       phase by phase, root-cause fixes only
5. Verification loop    run the whole suite + typecheck + build; on red, revise (cap 5
                        iterations, then a dead-end report); self-verify on the matching
                        surface (API pair / UI screenshot / money numbers)
6. Report               what changed, per-ID results, evidence, what is still manual
```

Two shell hooks keep it honest when the agent forgets:

- `ticket-rules.py` (`pre_llm_call`) injects the pipeline into messages that look like tickets.
- `tests-not-committed.py` (`pre_tool_call`) blocks `git commit` / `git push` while a
  scaffolding test file is still in the tree, unless the path is allowlisted by policy.

## Quickstart (Hermes)

```bash
git clone https://github.com/<you>/ticket-workflow-kit
cd ticket-workflow-kit
./install.sh --yes          # copies skills + hooks, wires config.yaml
hermes hooks doctor          # both hooks must report healthy + allowlisted
hermes hooks test pre_llm_call --payload-file fixtures/hook_payloads/top_level_msg.json
./install.sh --uninstall     # restores config.yaml to its pre-install hash
```

Then just send a ticket. The pipeline arrives on its own.

## What is inside

| Path | What it is |
|---|---|
| `skills/vdd-workflow` | The pipeline itself: six stages, loop rules, gates, pitfalls |
| `skills/coding-plan` | The ten-section coding plan an agent writes before code |
| `skills/clean-code` | Continuous code-quality rules applied during implementation |
| `skills/vdd` | Requirement validation before phases may advance |
| `skills/e2e-browser-test-automation` | Browser E2E for user-facing flows |
| `hooks/` | The two enforcement hooks (stdlib Python, no dependencies) |
| `policy/` | Per-repo policy: runners, language, test retention, allowlists |

## Test retention policy (the one opinionated default)

The default is `regression-permanent`:

- a test that encodes a real bug, an external contract, or a reported regression is
  **permanent** — the next ticket must not re-break it;
- scaffolding written only to drive the feature is **deleted once green** (its runner output
  is quoted in the report first);
- `strict` deletes every new test file after green; `keep-all` keeps everything.

Set it per repo in `policy/*.yaml`. The commit guard hook reads the same allowlist.

## Status

**0.1.0 — work in progress.** Skills are ported and sanitized; hooks, installer, policy
files, tests, and CI land in the next phases (see `CONTRIBUTING.md`). Do not advertise this
repo until the `1.0.0` tag.

## Compatibility

Hermes Agent first (hooks + installer). The skills are plain SKILL.md and load in any
agent harness that supports the Agent Skills tree; see `docs/other-harnesses.md` for the
Claude Code / Cursor / Codex mapping and what the hooks translate to there.

## License

MIT — see `LICENSE`. The workflow is authored by Fendi Permadi.
