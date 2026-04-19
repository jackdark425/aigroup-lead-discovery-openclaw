#!/usr/bin/env bash
# preflight.sh — verify macmini runtime deps for aigroup-lead-discovery-openclaw.
# Exit 0 → usable; exit 1 → missing deps listed on stderr.

set -u
FAIL=0
MISSING=()

need_cmd() {
  local bin="$1" name="$2" hint="$3"
  if ! command -v "$bin" >/dev/null 2>&1; then
    MISSING+=("$name — $hint")
    FAIL=1
  else
    echo "  ok  $name ($(command -v "$bin"))"
  fi
}

echo "aigroup-lead-discovery-openclaw preflight on $(uname -s)/$(uname -m)"
echo
echo "[required binaries]"
need_cmd python3 "python3 (>= 3.9)" "built-in on macOS 11+, or 'brew install python@3.11'"
need_cmd node   "node (>= 18)"       "brew install node"
echo
if [ "$FAIL" -ne 0 ]; then
  echo "FAIL: $(printf '%d' "${#MISSING[@]}") dependency issue(s):" >&2
  for m in "${MISSING[@]}"; do
    echo "  - $m" >&2
  done
  exit 1
fi
echo "PASS: all required runtime deps reachable."
exit 0
