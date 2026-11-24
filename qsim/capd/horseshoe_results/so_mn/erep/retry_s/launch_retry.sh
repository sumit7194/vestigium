#!/bin/zsh
# Branch-S launcher (PRELAUNCH.md; slots approved by the Bridge on 2026-11-25 as option (a)). Run detached.
# Each time one of the kerr_e chunks running at start ends, the next job in the queue starts:
#   piece mm, mp, pm, pp (mn_so_piece, each with erep_guard --inform), then the serial reference worker.
# Memory gate: launch only when the system-wide free percentage is >= 50; otherwise wait. Never kills anything.
# Refuses a piece whose state file already exists (no double launch). Logs to launch.log.
O=${0:A:h}; Q=/Users/sumit/Github/quantum; T=$Q/qsim/capd/horseshoe/tests; PY=$Q/sims/.venv/bin/python
SHA=491fb0a1d2e0c91df04efc07db3e1826a2a352c2cc91a055527fc19b1b9b6510
typeset -A OFF; OFF=(mm "-1/20000000 -1/20000000" mp "-1/20000000 1/20000000" pm "1/20000000 -1/20000000" pp "1/20000000 1/20000000")
log() { echo "$(date '+%F %T') $*" >> $O/launch.log; }
kcount() { ps -axo command= | grep -c "^$Q/qsim/capd/horseshoe/hs_cover_b15d .*kerr_e/" }
memfree() { memory_pressure -Q | sed -n 's/.*percentage: \([0-9]*\)%.*/\1/p' }
launch_piece() {
  local p=$1
  [[ -e $O/$p/st ]] && { log "REFUSED piece $p: $O/$p/st exists"; return }
  [[ $(shasum -a 256 $T/mn_so_piece | cut -c1-64) == $SHA ]] || { log "REFUSED piece $p: binary sha mismatch"; return }
  mkdir -p $O/$p; cd $T
  local PID=$(CENTRE_OFFSET="${OFF[$p]}" SO_EREP=zsym SO_FIXED_REDO=1 SAVE_FROM=292 SAVE_DT=100 \
              $Q/tools/detach.sh $O/$p/run.out $T nice -n 10 ./mn_so_piece 1/20000000 $O/cp/b17_cp_5e-8_$p.txt $O/$p/st 805.3)
  sleep 5
  local GPID=$($Q/tools/detach.sh $O/$p/guard.out $T nice -n 10 $PY $Q/qsim/capd/horseshoe/erep_guard.py $PID $O/$p/guard.log 500 --inform)
  log "start piece $p PID $PID (offset ${OFF[$p]}), guard PID $GPID, memfree $(memfree)%"
}
K0=$(kcount); queue=(mm mp pm pp refs); n=1
log "launcher start PID $$: $K0 kerr_e chunks running; queue $queue"
while (( n <= ${#queue} )); do
  freed=$(( K0 - $(kcount) ))
  if (( freed >= n )); then
    mf=$(memfree)
    if (( mf < 50 )); then log "WAIT: memfree ${mf}% < 50 (next: ${queue[$n]})"; sleep 300; continue; fi
    if [[ ${queue[$n]} == refs ]]; then
      RP=$($Q/tools/detach.sh $O/refs_serial.out $O zsh $O/refs_serial.sh); log "start refs worker PID $RP, memfree ${mf}%"
    else launch_piece ${queue[$n]}; fi
    (( n++ ))
  fi
  sleep 60
done
log "launcher done: all 5 jobs started"
