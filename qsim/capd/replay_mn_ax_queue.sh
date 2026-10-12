#!/bin/zsh
# MN axial VREPRO rows 0-3 + axial-0 secondary (fixed layout; procs from procs_override_mn). Parallel with the eq queue.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
run() { $PY qsim/capd/mr_replay.py run $1 $2 $3 > qsim/capd/replay_results/log_$1_$2_$3.txt 2>&1; echo "$1 $2 $3 done $(date)"; }
for r in 0 1 2 3; do run mnaxv2 $r primary; done
run mnaxv2 0 secondary
echo "MN AX QUEUE DONE $(date)"
