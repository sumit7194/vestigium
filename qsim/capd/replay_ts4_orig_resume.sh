#!/bin/zsh
# (b) TS 4 original path, re-run after the MN queues, nice +19, relaunched from A3 checkpoints on watchdog trips.
cd /Users/sumit/Github/quantum
until grep -q "MN EQ QUEUE DONE" qsim/capd/replay_mn_eq_queue.out && grep -q "MN AX QUEUE DONE" qsim/capd/replay_mn_ax_queue.out; do sleep 300; done
for attempt in 1 2 3 4 5 6 7 8; do
  nice -n 19 sims/.venv/bin/python qsim/capd/mr_replay.py run ts2 4 primary > qsim/capd/replay_results/log_ts2_4_primary_resume$attempt.txt 2>&1
  v=$(python3 -c "import json; print(json.load(open('qsim/capd/replay_results/ts2_4_primary_o30_p256.json')).get('verdict'))")
  w=$(grep -c "WATCHDOG" qsim/capd/tests/gen/ts2_4_primary_o30_p256.err)
  echo "attempt $attempt: verdict $v watchdog $w $(date)"
  [ "$v" = "FAILED-CLOSED" ] && [ "$w" -gt 0 ] && continue
  break
done
echo "TS4 ORIG DONE $(date)"
