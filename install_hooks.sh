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
#
# THE FIRST VERSION OF THIS CONTROL WAS ITSELF DECORATION (2026-09-22). It
# APPENDED a failing line to verify.py -- which ends in sys.exit(0), so the
# planted failure was DEAD CODE, never ran, the gate passed, and the control
# reported "HOOK DID NOT BLOCK". A true observation with a wrong diagnosis: the
# hook was fine and the control was broken. Exactly the fault this installer
# exists to guard against, one level up. Now the file is REPLACED, not appended.
echo "verifying the hook actually blocks..."
mv verify.py .verify.py.bak
printf 'import sys\nprint("PLANTED FAILURE -- known-fail control")\nsys.exit(1)\n' > verify.py
if .githooks/pre-commit >/dev/null 2>&1; then
  mv .verify.py.bak verify.py
  echo "*** HOOK DID NOT BLOCK ON A RED GATE -- it is decoration. NOT installed. ***" >&2
  exit 1
fi
mv .verify.py.bak verify.py
# and confirm the restore worked, or the next commit runs against a stub
python3 -c "import sys; sys.exit(0 if 'PLANTED FAILURE' not in open('verify.py').read() else 1)" \
  || { echo "*** RESTORE FAILED -- verify.py is still the stub ***" >&2; exit 1; }
echo "hook refused a planted red gate, and verify.py restored -- gate is live"
