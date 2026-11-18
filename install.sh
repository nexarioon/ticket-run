#!/usr/bin/env bash
# ticket-workflow-kit installer: skills + hooks + policy + config wiring.
# Bash + python3 only, no network. --uninstall restores the pre-install config.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE="" LANG_OPT="" HOME_ARG="" DRY=no UNINSTALL=no
usage() { cat <<'EOF'
usage: ./install.sh [--profile NAME] [--lang en|id] [--home PATH] [--dry-run] [--uninstall] [--yes]
  --profile  install into ~/.hermes/profiles/NAME (created if missing)
  --home     custom Hermes root (default ~/.hermes or $HERMES_HOME)
  --lang     message language written into the policy (default en)
  --dry-run  print actions, write nothing
  --uninstall remove hook files + config entries; skills are left in place
EOF
}
while [[ $# -gt 0 ]]; do case "$1" in
  --profile) PROFILE="${2:?}"; shift 2;;
  --lang) LANG_OPT="${2:?}"; shift 2;;
  --home) HOME_ARG="${2:?}"; shift 2;;
  --dry-run) DRY=yes; shift;;
  --uninstall) UNINSTALL=yes; shift;;
  --yes) shift;;
  -h|--help) usage; exit 0;;
  *) echo "unknown flag: $1" >&2; usage >&2; exit 2;;
esac; done
BASE="${HOME_ARG:-${HERMES_HOME:-$HOME/.hermes}}"
if [[ -n "$PROFILE" ]]; then ROOT="$BASE/profiles/$PROFILE"; else ROOT="$BASE"; fi
HOOKDIR="$ROOT/agent-hooks/ticket-workflow-kit"
STAMP="$ROOT/ticket-workflow/.install-stamp.json"
CONFIG="$ROOT/config.yaml"

if [[ "$UNINSTALL" == yes ]]; then
  if [[ ! -f "$CONFIG" ]]; then echo "no config at $CONFIG"; exit 1; fi
  python3 "$SRC/install/patch_config.py" "$CONFIG" --remove $([[ "$DRY" == yes ]] && echo --dry-run)
  if [[ "$DRY" != yes ]]; then
    rm -rf "$HOOKDIR"
    rm -f "$STAMP" "$ROOT/ticket-workflow/default.yaml" "$ROOT/ticket-workflow/profiles.example.yaml" "$ROOT/ticket-workflow/lang_en.yaml" "$ROOT/ticket-workflow/lang_id.yaml"
    rmdir "$ROOT/ticket-workflow" 2>/dev/null || true
    echo "hooks and config entries removed; skills left in place (delete $ROOT/skills manually if you want)"
  fi
  exit 0
fi

echo "root   : $ROOT"
echo "hooks  : $HOOKDIR"
if [[ "$DRY" == yes ]]; then
  echo "dry-run: would copy skills/, hooks/ (as agent-hooks/ticket-workflow-kit/), policy/, then wire $CONFIG"
  python3 "$SRC/install/patch_config.py" "$CONFIG" --add --hookdir "$HOOKDIR" --dry-run
  exit 0
fi
mkdir -p "$ROOT/skills" "$ROOT/agent-hooks" "$ROOT/ticket-workflow"
cp -r "$SRC/skills/." "$ROOT/skills/"
rm -rf "$HOOKDIR"; mkdir -p "$HOOKDIR"
cp -r "$SRC/hooks/." "$HOOKDIR/"
rm -rf "$HOOKDIR/lib/__pycache__"
find "$HOOKDIR" -name "*.py" -exec chmod +x {} +
[[ -f "$ROOT/ticket-workflow/default.yaml" ]] || cp "$SRC/policy/default.yaml" "$ROOT/ticket-workflow/default.yaml"
cp "$SRC/policy/profiles.example.yaml" "$ROOT/ticket-workflow/profiles.example.yaml" 2>/dev/null || true
if [[ -n "$LANG_OPT" && ! -f "$ROOT/.ticket-workflow.yaml" ]]; then
  printf 'language: %s\n' "$LANG_OPT" > "$ROOT/ticket-workflow/lang_used.yaml"
  printf 'NOTE: set language in %s/ticket-workflow/default.yaml or .ticket-workflow.yaml\n' "$ROOT"
fi
python3 "$SRC/install/patch_config.py" "$CONFIG" --add --hookdir "$HOOKDIR"
cat <<EOF

installed. Next (one-time consent, Hermes refuses unknown hook scripts by design):
  hermes --profile "$PROFILE" hooks doctor          # shows: not allowlisted yet
  hermes --accept-hooks --profile "$PROFILE" hooks doctor   # or approve at the TTY prompt
then verify the injection:
  hermes --profile "$PROFILE" hooks test pre_llm_call --payload-file fixtures/hook_payloads/top_level_msg.json
EOF
