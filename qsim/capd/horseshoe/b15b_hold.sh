#!/bin/bash
# b15b_hold.sh -- the Bridge's hold (2026-10-26, disk/swap pressure): stop each MNFlow grinder BETWEEN tasks, i.e. right
# after its current task's result line is written, by verified PID (b15b_verify_kill.sh); nothing in progress is lost.
# Leaves them stopped (resume later from the JSONL). Also logs CRITICAL when swap free < 300 MB or disk free < 2 GB.
G=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15b_gates; H=/Users/sumit/Github/quantum/qsim/capd/horseshoe; LOG=$G/hold.log
declare -A F=([11976]="$G/mnflow_w2.jsonl" [61777]="$G/mnflow_grind0.jsonl") A=([11976]="2 4" [61777]="grind 0 1") N
for p in "${!F[@]}"; do N[$p]=$(wc -l < "${F[$p]}"); done
echo "$(date '+%F %T') hold armed: PIDs ${!F[*]} at ${N[*]} results" >> $LOG
while true; do
  alive=0
  for p in "${!F[@]}"; do
    ps -p $p >/dev/null 2>&1 || continue; alive=1
    if [ $(wc -l < "${F[$p]}") -gt ${N[$p]} ]; then
      echo "$(date '+%F %T') PID $p finished a task: $(tail -1 "${F[$p]}" | cut -c1-60)" >> $LOG
      $H/b15b_verify_kill.sh $p "${A[$p]}" $LOG || echo "$(date '+%F %T') PID $p NOT stopped (verification refused)" >> $LOG
      N[$p]=999999999
    fi
  done
  sw=$(sysctl -n vm.swapusage | awk '{print $9}' | tr -d M); dk=$(df -g / | tail -1 | awk '{print $4}')
  if [ $(echo "$sw < 300" | bc) = 1 ] || [ "$dk" -lt 2 ]; then echo "$(date '+%F %T') CRITICAL: swap free ${sw}M, disk free ${dk}G" >> $LOG; fi
  [ $alive = 0 ] && { echo "$(date '+%F %T') both grinders stopped; hold done" >> $LOG; exit 0; }
  sleep 60
done
