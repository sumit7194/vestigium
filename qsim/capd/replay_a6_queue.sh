#!/bin/zsh
# A6 queue (MR_REPLAY.md): TS rows with no output -> A5 path; then secondaries; then cross-path re-runs. 3 per-loop procs.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
run() { $PY qsim/capd/mr_replay.py run $1 $2 $3 > qsim/capd/replay_results/log_$1_$2_$3.txt 2>&1; echo "$1 $2 $3 done $(date)"; }
run ts2 1 primary_a5; run ts2 5 primary_a5
for r in 3 4 5 6 7; do run tschaos $r primary_a5; done
run ts2 4 primary_a5; run tschaos 2 primary_a5
run ts2 0 secondary_a5; run tschaos 0 secondary_a5
run ts2 2 xpath_a5; run ts2 3 xpath_a5; run tschaos 0 xpath_a5; run tschaos 1 xpath_a5
echo "A6 QUEUE DONE $(date)"
