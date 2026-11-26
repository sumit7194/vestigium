#!/bin/zsh
# B15e A6 pause-only guard for OUR chunks on the Air (Sumit's machine). Every 60 s: memory_pressure free% < 25 -> SIGSTOP
# our hs_cover processes (verified by their command line: the bundle binary) + an ALERT line; free >= 35 -> SIGCONT.
# Thermal state is logged (inform only). NEVER kills. Exits when none of our chunks is running. Log: guard.log
ROOT=${0:A:h}; X=$ROOT/bin/hs_cover_b15e2s; G=$ROOT/guard.log; paused=0; k=0
log() { echo "$(date '+%F %T') $*" >> $G; }
ours() { ps -axo pid=,command= | awk -v x="$X" '$2==x {print $1}' }
log "guard armed PID $$: pause < 25% free, resume >= 35%; thermal inform; never kills"
while [[ -n "$(ours)" ]]; do
  mf=$(memory_pressure -Q | sed -n 's/.*percentage: \([0-9]*\)%.*/\1/p'); th=$(pmset -g therm 2>/dev/null | grep -E "Speed_Limit|Thermal" | tr -s ' ' | tr '\n' ';')
  if (( mf < 25 && paused == 0 )); then for p in $(ours); do kill -STOP $p && log "SIGSTOP verified PID $p"; done; paused=1; log "ALERT PAUSE: memory free ${mf}% < 25"; fi
  if (( mf >= 35 && paused == 1 )); then for p in $(ours); do kill -CONT $p && log "SIGCONT verified PID $p"; done; paused=0; log "RESUME: memory free ${mf}%"; fi
  (( k % 10 == 0 )) && log "status: memfree ${mf}% paused=$paused chunks $(ours | wc -l | tr -d ' ') therm[$th]"
  (( k++ )); sleep 60
done
log "no chunk of ours running; guard exits"
