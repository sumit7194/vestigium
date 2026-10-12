#!/bin/zsh
# MN equatorial rows 1-5 (fixed layout; procs from procs_override_mn). Parallel with the axial queue.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
run() { $PY qsim/capd/mr_replay.py run $1 $2 $3 > qsim/capd/replay_results/log_$1_$2_$3.txt 2>&1; echo "$1 $2 $3 done $(date)"; }
for r in 1 2 3 4 5; do run mneq $r primary; done
echo "MN EQ QUEUE DONE $(date)"
