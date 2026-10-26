#!/bin/bash
# b15b_critical_guard.sh PID ARGS -- the Bridge's CRITICAL rule (2026-10-26) for ONE running MNFlow worker: if swap free
# < 300 MB or disk free < 2 GB, stop it by verified PID (b15b_verify_kill.sh; its in-progress task is lost) and log it.
# Exits when the worker exits. Log: b15b_gates/hold.log.
P=$1; A=$2; H=/Users/sumit/Github/quantum/qsim/capd/horseshoe; LOG=$H/../horseshoe_results/kerr/b15b_gates/hold.log
echo "$(date '+%F %T') critical guard armed for PID $P ($A)" >> $LOG
while ps -p $P >/dev/null 2>&1; do
  # swap is allocated on demand: right after a boot total = free = 0, which is NOT exhaustion (the first version stopped a
  # worker for exactly that, 2026-10-26 14:00). CRITICAL = swap total >= 1 GB with free < 300 MB, or disk free < 2 GB.
  st=$(sysctl -n vm.swapusage | awk '{print $3}' | tr -d M); sw=$(sysctl -n vm.swapusage | awk '{print $9}' | tr -d M); dk=$(df -g / | tail -1 | awk '{print $4}')
  if { [ $(echo "$st >= 1024" | bc) = 1 ] && [ $(echo "$sw < 300" | bc) = 1 ]; } || [ "$dk" -lt 2 ]; then
    echo "$(date '+%F %T') CRITICAL: swap free ${sw}M, disk free ${dk}G -> EMERGENCY stop of PID $P" >> $LOG
    $H/b15b_verify_kill.sh $P "$A" $LOG; exit 0; fi
  sleep 60
done
echo "$(date '+%F %T') PID $P exited; critical guard done" >> $LOG
