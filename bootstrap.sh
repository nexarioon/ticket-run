#!/usr/bin/env bash
# ticket-workflow-kit bootstrap: install with one command, no git and no npm.
#
#   curl -fsSL https://raw.githubusercontent.com/nexarioon/ticket-workflow-kit/main/bootstrap.sh | bash
#   curl -fsSL .../bootstrap.sh | bash -s -- --tag v0.3.0            # pinned release
#   curl -fsSL .../bootstrap.sh | bash -s -- --tag v0.3.0 --sha256 <hex>
#
# Read this file before piping it to bash: it downloads a tarball from GitHub,
# extracts it to a temp directory, runs the bundled install.sh with the flags you
# pass through, and removes the temp directory. Nothing else touches your machine.
set -euo pipefail

REPO="nexarioon/ticket-workflow-kit"
TAG="main"
SHA=""
URL=""
PASS=()

usage() {
  cat <<'EOF'
usage: bootstrap.sh [--tag REF] [--sha256 HEX] [--url TGZ] [install.sh flags...]
  --tag     release tag (vX.Y.Z) or branch (default: main)
  --sha256  expected tarball hash; refuse to install on mismatch
  --url     override download source (tgz path, file:// or https://) — advanced/testing
  also accepted: --profile NAME --home PATH --lang en|id --dry-run --uninstall --yes
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="${2:?--tag needs a value}"; shift 2;;
    --sha256) SHA="${2:?--sha256 needs a value}"; shift 2;;
    --url) URL="${2:?--url needs a value}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) PASS+=("$1"); shift;;
  esac
done

if [[ -z "$URL" ]]; then
  if [[ "$TAG" == v* ]]; then
    URL="https://codeload.github.com/$REPO/tar.gz/refs/tags/$TAG"
  else
    URL="https://codeload.github.com/$REPO/tar.gz/refs/heads/$TAG"
  fi
fi

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

printf 'download: %s\n' "$URL"
if ! curl -fsSL -o "$TMP/pkg.tgz" "$URL"; then
  echo "bootstrap: download failed: $URL" >&2
  exit 1
fi

if [[ -n "$SHA" && "$SHA" != "-" ]]; then
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s  %s\n' "$SHA" "$TMP/pkg.tgz" | sha256sum -c - >/dev/null || {
      echo "bootstrap: checksum mismatch — refusing to install" >&2; exit 1; }
  else
    ACTUAL="$(shasum -a 256 "$TMP/pkg.tgz" | awk '{print $1}')"
    [[ "$ACTUAL" == "$SHA" ]] || { echo "bootstrap: checksum mismatch — refusing to install" >&2; exit 1; }
  fi
fi

mkdir -p "$TMP/src"
tar -xzf "$TMP/pkg.tgz" -C "$TMP/src" --strip-components=1
bash "$TMP/src/install.sh" ${PASS[@]+"${PASS[@]}"}
