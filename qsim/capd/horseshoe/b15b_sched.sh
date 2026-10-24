#!/bin/bash
# B15b MNFlow scheduling supervisor (GATE_LOG.md, 2026-10-24). Hands the 3 in-flight workers' slots over to the
# fast/grind workers. An old worker is stopped (explicit PID, SIGTERM) only after its jsonl gains a line, i.e. its
# current task is written; the seconds of the next task it started are lost. Slot 1 -> fast worker. The single grind
# worker starts only when ALL old workers have stopped (no task can run twice). Events -> sched.log. Every stop goes
# through b15b_verify_kill.sh (exact command, owner and cwd verified and logged first; the Bridge's no-pkill guard).
D=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15b_gates; H=/Users/sumit/Github/quantum/qsim/capd/horseshoe
PY=/Users/sumit/Github/quantum/sims/.venv/bin/python; LOG=$D/sched.log
declare -a PIDS=(11972 11974 11976) N0
for i in 0 1 2; do N0[$i]=$(wc -l < $D/mnflow_w$i.jsonl); done
echo "$(date '+%F %T') supervisor start: old workers ${PIDS[*]} at ${N0[*]} results" >> $LOG
fast_started=0; grind_started=0
while true; do
  alive=0
  for i in 0 1 2; do
    p=${PIDS[$i]}; [ "$p" = 0 ] && continue
    if ! ps -o command= -p $p 2>/dev/null | grep -q "b15b_mnflow_worker.py $i 4"; then echo "$(date '+%F %T') old worker $i (PID $p) gone" >> $LOG; PIDS[$i]=0; continue; fi
    if [ $(wc -l < $D/mnflow_w$i.jsonl) -gt ${N0[$i]} ]; then
      echo "$(date '+%F %T') old worker $i (PID $p) finished its task ($(tail -1 $D/mnflow_w$i.jsonl | cut -c1-40))" >> $LOG
      $H/b15b_verify_kill.sh $p "$i 4" $LOG || echo "$(date '+%F %T') NOT stopped (verification refused); leaving it" >> $LOG; PIDS[$i]=0; continue
    fi
    alive=$((alive+1))
  done
  if [ $alive -lt 3 ] && [ $fast_started = 0 ]; then
    cd $H && nohup $PY -u b15b_mnflow_worker.py fast 0 1 >> $D/mnflow_fast0.log 2>&1 & echo "$(date '+%F %T') started fast worker PID $!" >> $LOG; fast_started=1
  fi
  if [ $alive = 0 ] && [ $grind_started = 0 ]; then
    cd $H && nohup $PY -u b15b_mnflow_worker.py grind 0 1 >> $D/mnflow_grind0.log 2>&1 & echo "$(date '+%F %T') started grind worker PID $! (serial)" >> $LOG; grind_started=1
  fi
  [ $grind_started = 1 ] && { echo "$(date '+%F %T') supervisor done" >> $LOG; exit 0; }
  sleep 30
done
