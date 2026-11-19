#!/bin/bash
# b15b_claim_switch.sh -- the boundary switch from the single grind worker to 3 claim workers (Sumit's GO via the Bridge,
# 2026-11-19; the claim gate PASSED, 485d857). Waits until mnflow_grind0.jsonl gains a row (the old worker's task just
# finished), stops the old worker by VERIFIED PID (b15b_verify_kill.sh, args "grind 0 1"), waits for it to exit, then
# launches 3 claim workers (nice 15, detached), each with its own guard (b15b_g3_guard.py PID "claim k": sustained rule,
# 1 GB cap). Log: b15b_gates/claim_switch.log.
OLD=$1; Q=/Users/sumit/Github/quantum; HS=$Q/qsim/capd/horseshoe; G=$Q/qsim/capd/horseshoe_results/kerr/b15b_gates
L=$G/claim_switch.log; PY=$Q/sims/.venv/bin/python; log(){ echo "$(date '+%F %T') $*" >> $L; }
n0=$(wc -l < $G/mnflow_grind0.jsonl); log "armed: old worker PID $OLD, grind0 rows $n0; waiting for a new row"
while [ "$(wc -l < $G/mnflow_grind0.jsonl)" -le "$n0" ]; do
  ps -p $OLD > /dev/null || { log "old worker gone before a new row; NOT switching (check why)"; exit 1; }; sleep 5; done
log "new row: $(tail -1 $G/mnflow_grind0.jsonl | cut -c1-40)"
$HS/b15b_verify_kill.sh $OLD "grind 0 1" $L || { log "verification REFUSED; NOT switching"; exit 1; }
for i in $(seq 60); do ps -p $OLD > /dev/null || break; sleep 1; done
ps -p $OLD > /dev/null && { log "old worker still alive after 60 s; NOT switching"; exit 1; }
log "old worker stopped; grind0 rows $(wc -l < $G/mnflow_grind0.jsonl)"
for k in 0 1 2; do
  echo "=== claim worker $k start $(date '+%F %T') ===" >> $G/mnflow_claim$k.log
  W=$(nice -n 15 $Q/tools/detach.sh $G/mnflow_claim$k.log $HS $PY -u b15b_mnflow_worker.py claim $k); sleep 2
  D=$(nice -n 10 $Q/tools/detach.sh $G/g3_guard_claim$k.out $HS $PY -u b15b_g3_guard.py $W "claim $k"); sleep 2
  log "claim worker $k PID $W, guard PID $D"; done
log "DONE"
