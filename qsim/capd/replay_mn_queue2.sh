#!/bin/zsh
# MN queue, continued after the eq-0 resume split (fixed layout; procs from procs_override_mn).
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
run() { $PY qsim/capd/mr_replay.py run $1 $2 $3 > qsim/capd/replay_results/log_$1_$2_$3.txt 2>&1; echo "$1 $2 $3 done $(date)"; }
run mneq 0 secondary
for r in 1 2 3 4 5; do run mneq $r primary; done
for r in 0 1 2 3; do run mnaxv2 $r primary; done
run mnaxv2 0 secondary
echo "MN QUEUE2 DONE $(date)"
