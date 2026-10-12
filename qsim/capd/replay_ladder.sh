#!/bin/zsh
# A7 escalation ladder (MR_REPLAY.md): after the A6 queue, every A5-path TS row whose primary_a5 result is NOT_REPLAYED
# goes through step 1 (escalated_a5) and, only if still NOT_REPLAYED, step 2 (escalated2_a5). Then stop.
cd /Users/sumit/Github/quantum
PY=sims/.venv/bin/python
export REPLAY_PROCS=2      # scheduling: the ladder runs at 2 per-loop processes (bridge core plan)
ladder_pass() {
verdict() { python3 -c "import json,glob,sys; f=sorted(glob.glob(sys.argv[1])); print(json.load(open(f[-1])).get('verdict') if f else 'MISSING')" "$1"; }
for f in qsim/capd/replay_results/ts2_*_primary_a5_o30_p128_cg3.json qsim/capd/replay_results/tschaos_*_primary_a5_o30_p128_cg3.json qsim/capd/replay_results/ts2_*_xpath_a5_o30_p128_cg3.json qsim/capd/replay_results/tschaos_*_xpath_a5_o30_p128_cg3.json; do
  [ -f "$f" ] || continue
  b=$(basename $f); fam=${b%%_*}; rest=${b#*_}; row=${rest%%_*}
  [ "$(verdict $f)" = "NOT_REPLAYED" ] || continue
  ls qsim/capd/replay_results/${fam}_${row}_escalated_a5_*.json >/dev/null 2>&1 && continue   # already laddered
  echo "ladder: $fam $row step 1 start $(date)"
  $PY qsim/capd/mr_replay.py run $fam $row escalated_a5 > qsim/capd/replay_results/log_${fam}_${row}_escalated_a5.txt 2>&1
  v=$(verdict "qsim/capd/replay_results/${fam}_${row}_escalated_a5_*.json"); echo "ladder: $fam $row step 1 -> $v $(date)"
  if [ "$v" = "NOT_REPLAYED" ]; then
    $PY qsim/capd/mr_replay.py run $fam $row escalated2_a5 > qsim/capd/replay_results/log_${fam}_${row}_escalated2_a5.txt 2>&1
    v2=$(verdict "qsim/capd/replay_results/${fam}_${row}_escalated2_a5_*.json"); echo "ladder: $fam $row step 2 -> $v2 $(date)"
  fi
done
# A8: C rows that STARTED at step-1 settings (o40_p256) go directly to step 2 if undecided
for f in qsim/capd/replay_results/tschaos_*_primary_a5_o40_p256_cg3.json qsim/capd/replay_results/tschaos_*_xpath_a5_o40_p256_cg3.json; do
  [ -f "$f" ] || continue
  b=$(basename $f); rest=${b#*_}; row=${rest%%_*}
  [ "$(verdict $f)" = "NOT_REPLAYED" ] || continue
  ls qsim/capd/replay_results/tschaos_${row}_escalated2_a5_*.json >/dev/null 2>&1 && continue
  echo "ladder (A8): tschaos $row started at step 1, undecided -> step 2 $(date)"
  $PY qsim/capd/mr_replay.py run tschaos $row escalated2_a5 > qsim/capd/replay_results/log_tschaos_${row}_escalated2_a5.txt 2>&1
  echo "ladder (A8): tschaos $row step 2 -> $(verdict "qsim/capd/replay_results/tschaos_${row}_escalated2_a5_*.json") $(date)"
done
}
ladder_pass                                   # now: rows already undecided (C6, C7)
until grep -q "A6 QUEUE DONE" qsim/capd/replay_a6_queue.out; do sleep 120; done
ladder_pass                                   # after A6: any further undecided rows
echo "LADDER DONE $(date)"
