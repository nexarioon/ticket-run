# One-line install (no npm, no git)

```bash
curl -fsSL https://raw.githubusercontent.com/nexarioon/ticket-workflow-kit/main/bootstrap.sh | bash
```

What that does, in order:

1. downloads the release tarball from GitHub (codeload — no git required),
2. extracts it to a temporary directory,
3. runs the bundled `install.sh` with any flags you passed,
4. deletes the temporary directory.

## Pin a release and verify the hash

```bash
curl -fsSL .../main/bootstrap.sh | bash -s -- --tag v0.3.0 --sha256 <hex>
```

`--sha256` refuses to install on a mismatch — the hash of each release tarball
is published in the release notes. Pinning matters: `main` moves.

## Useful flags (all passed through to install.sh)

| Flag | Effect |
|---|---|
| `--profile NAME` | install into `~/.hermes/profiles/NAME` (created if missing) |
| `--home PATH` | custom Hermes root |
| `--lang en\|id` | message language |
| `--dry-run` | print the plan, write nothing |
| `--uninstall` | remove hooks + config entries (skills stay) |
| `--yes` | non-interactive |

## Read before you pipe

Piping a URL into `bash` executes whatever the server sends. The script is ~90
lines in the repo root; read it once, or download it, check it, and run it:

```bash
curl -fsSL .../main/bootstrap.sh -o bootstrap.sh
less bootstrap.sh && bash bootstrap.sh --tag v0.3.0
```

The hook consent step is unchanged: after install, approve the two hooks once
at the TTY prompt of your first session (see `install-hermes.md`).
