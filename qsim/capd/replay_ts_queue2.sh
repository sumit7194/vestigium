#!/bin/zsh
# A2 re-queue of the C rows (tschaos 0-7) + C1 secondary, single-process layout, 24 h watchdog.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
for r in 0 1 2 3 4 5 6 7; do $PY qsim/capd/mr_replay.py run tschaos $r primary > qsim/capd/replay_results/log_tschaos_$r.txt 2>&1; echo "tschaos $r done $(date)"; done
$PY qsim/capd/mr_replay.py run tschaos 0 secondary > qsim/capd/replay_results/log_tschaos_0_sec.txt 2>&1; echo "tschaos 0 secondary done $(date)"
echo "C QUEUE DONE $(date)"
