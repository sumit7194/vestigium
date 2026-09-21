#!/bin/bash
# Activate the pre-commit gate, and PROVE it blocks before claiming it is installed.
#
# The fault this exists for: `core.hooksPath` lives in .git/config, which is NOT
# cloned. A fresh clone gets .githooks/pre-commit -- tracked, reviewable, in the
# diff -- and no gate. That passes any review consisting of reading the repository.
# thebridge's taxonomy: TRACKED, not ACTIVATED.
set -e
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
echo "core.hooksPath = $(git config core.hooksPath)"

# KNOWN-FAIL CONTROL: a hook that has only ever been seen to pass has not been
# tested. Plant a red gate and confirm the hook REFUSES, then restore.
echo "verifying the hook actually blocks..."
cp verify.py .verify.py.bak
printf '\nimport sys; print("PLANTED FAILURE"); sys.exit(1)\n' >> verify.py
if .githooks/pre-commit >/dev/null 2>&1; then
  mv .verify.py.bak verify.py
  echo "*** HOOK DID NOT BLOCK ON A RED GATE -- it is decoration. NOT installed. ***" >&2
  exit 1
fi
mv .verify.py.bak verify.py
echo "hook refused a planted red gate -- gate is live"
