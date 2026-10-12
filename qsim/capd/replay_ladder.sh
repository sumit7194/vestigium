#!/bin/zsh
# A7 escalation ladder (MR_REPLAY.md): after the A6 queue, every A5-path TS row whose primary_a5 result is NOT_REPLAYED
# goes through step 1 (escalated_a5) and, only if still NOT_REPLAYED, step 2 (escalated2_a5). Then stop.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
until grep -q "A6 QUEUE DONE" qsim/capd/replay_a6_queue.out; do sleep 120; done
verdict() { python3 -c "import json,glob,sys; f=sorted(glob.glob(sys.argv[1])); print(json.load(open(f[-1])).get('verdict') if f else 'MISSING')" "$1"; }
for f in qsim/capd/replay_results/ts2_*_primary_a5_o30_p128_cg3.json qsim/capd/replay_results/tschaos_*_primary_a5_o30_p128_cg3.json; do
  [ -f "$f" ] || continue
  b=$(basename $f); fam=${b%%_*}; rest=${b#*_}; row=${rest%%_*}
  [ "$(verdict $f)" = "NOT_REPLAYED" ] || continue
  echo "ladder: $fam $row step 1 start $(date)"
  $PY qsim/capd/mr_replay.py run $fam $row escalated_a5 > qsim/capd/replay_results/log_${fam}_${row}_escalated_a5.txt 2>&1
  v=$(verdict "qsim/capd/replay_results/${fam}_${row}_escalated_a5_*.json"); echo "ladder: $fam $row step 1 -> $v $(date)"
  if [ "$v" = "NOT_REPLAYED" ]; then
    $PY qsim/capd/mr_replay.py run $fam $row escalated2_a5 > qsim/capd/replay_results/log_${fam}_${row}_escalated2_a5.txt 2>&1
    v2=$(verdict "qsim/capd/replay_results/${fam}_${row}_escalated2_a5_*.json"); echo "ladder: $fam $row step 2 -> $v2 $(date)"
  fi
done
echo "LADDER DONE $(date)"
