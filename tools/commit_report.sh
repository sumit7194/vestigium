#!/bin/zsh
# Commit, push, and print ONE line to be quoted verbatim in any report that names a commit:
#   commit <HEAD short> pushed <origin/main short>
# Usage: tools/commit_report.sh <message-file> <path> [<path> ...]
#   <message-file>: the full commit message (including any Co-Authored-By trailer).
#   Only the given paths are staged. The commit gate runs as usual (numpy on PATH from sims/.venv).
# Exits non-zero, and prints NOTHING to quote, if any step fails (gate refusal, push failure, hash mismatch).
# Why: three hand-typed or premature commit ids in reports on 2026-11-27/28 (the Bridge: "make the fix a mechanism").
setopt errexit pipefail
R=$(git rev-parse --show-toplevel); cd $R
export PATH=$R/sims/.venv/bin:$PATH
[ $# -ge 2 ] || { echo "usage: tools/commit_report.sh <message-file> <path>..." >&2; exit 2; }
msg=$1; shift
[ -s "$msg" ] || { echo "message file missing or empty: $msg" >&2; exit 2; }
git add -- "$@"
git commit -q -F "$msg" >&2
git push -q origin HEAD:main >&2
git fetch -q origin
h=$(git rev-parse --short HEAD); o=$(git rev-parse --short origin/main)
[ "$h" = "$o" ] || { echo "HEAD $h != origin/main $o: NOT reporting" >&2; exit 3; }
echo "commit $h pushed $o"
