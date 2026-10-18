#!/bin/zsh
# MN replay queue (MR_REPLAY.md, A1-A5; MN rows: codegen 3 local re-expansion, 3 per-loop processes): eq row 0 (+secondary), eq 1-5, axial VREPRO 0-3 (+secondary on 0). One slot.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
run() { $PY qsim/capd/mr_replay.py run $1 $2 $3 > qsim/capd/replay_results/log_$1_$2_$3.txt 2>&1; echo "$1 $2 $3 done $(date)"; }
run mneq 0 primary; run mneq 0 secondary
for r in 1 2 3 4 5; do run mneq $r primary; done
for r in 0 1 2 3; do run mnaxv2 $r primary; done
run mnaxv2 0 secondary
echo "MN QUEUE DONE $(date)"
