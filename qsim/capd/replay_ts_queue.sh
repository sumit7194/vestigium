#!/bin/zsh
# Registered TS replay (MR_REPLAY.md, A1). Two queues in parallel (thread budget); each row: primary run.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
q1() { for r in 0 1 2 3 4 5; do $PY qsim/capd/mr_replay.py run ts2 $r primary > qsim/capd/replay_results/log_ts2_$r.txt 2>&1; echo "ts2 $r done $(date)"; done
       $PY qsim/capd/mr_replay.py run ts2 0 secondary > qsim/capd/replay_results/log_ts2_0_sec.txt 2>&1; echo "ts2 0 secondary done $(date)"; }
q2() { for r in 0 1 2 3 4 5 6 7; do $PY qsim/capd/mr_replay.py run tschaos $r primary > qsim/capd/replay_results/log_tschaos_$r.txt 2>&1; echo "tschaos $r done $(date)"; done
       $PY qsim/capd/mr_replay.py run tschaos 0 secondary > qsim/capd/replay_results/log_tschaos_0_sec.txt 2>&1; echo "tschaos 0 secondary done $(date)"; }
mkdir -p qsim/capd/replay_results
q1 & q2 & wait
echo "TS QUEUE DONE $(date)"
