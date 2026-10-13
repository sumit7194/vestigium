#!/bin/zsh
# Remaining MN eq rows 3-5 in parallel (2 procs each via procs_override_mn), after the eq queue shell was stopped with
# eq 2 still running (its python PID given as $1). Writes the marker the TS-4 original-path chain waits for.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
run() { $PY qsim/capd/mr_replay.py run $1 $2 $3 > qsim/capd/replay_results/log_$1_$2_$3.txt 2>&1; echo "$1 $2 $3 done $(date)" >> qsim/capd/replay_mn_eq_queue.out; }
( run mneq 3 primary; run mneq 5 primary ) &
( run mneq 4 primary ) &
wait
while ps -p $1 >/dev/null 2>&1; do sleep 60; done
echo "MN EQ QUEUE DONE $(date)" >> qsim/capd/replay_mn_eq_queue.out
