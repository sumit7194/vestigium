#!/bin/zsh
# B15e A6: start (or resume) the Air's kerr_e chunks. Idempotent: a chunk that is alive, or whose output holds DONE, is
# skipped; otherwise it starts, or RESUMES from its checkpoint (a previous partial output is kept as <chunk>.out.prev).
# At most 5 of our processes (Air budget: Quantum 5, Cuspis 3), nice 10, caffeinate -i -w <pid>, HS_WATCHDOG_S 30 d. Never kills. Log: launch.log
ROOT=${0:A:h}; X=$ROOT/bin/hs_cover_b15e2s; mkdir -p $ROOT/ckpt $ROOT/out; L=$ROOT/launch.log; cd $ROOT
log() { echo "$(date '+%F %T') $*" >> $L; }
alive() { ps -axo command= | grep -q "^$X $ROOT/specs/$1.spec" }
for t in N2N3 N3N4 N4N5 N5N0 N5N1; do
  if alive $t; then log "$t alive, skipped"; continue; fi
  if grep -q "^DONE" out/$t.out 2>/dev/null; then log "$t DONE, skipped"; continue; fi
  (( $(ps -axo command= | grep -c "^$X ") >= 5 )) && { log "cap 5 reached; $t waits"; continue; }
  [[ -s out/$t.out ]] && mv out/$t.out out/$t.out.prev.$(date +%s)
  P=$(HS_WATCHDOG_S=2592000 _STDBUF_O=L $ROOT/bin/detach.sh $ROOT/out/$t.out $ROOT nice -n 10 /usr/bin/stdbuf -oL $X $ROOT/specs/$t.spec)
  C=$($ROOT/bin/detach.sh /dev/null $ROOT caffeinate -i -w $P)
  log "START $t PID $P (resume from ckpt/$t.ckpt if present: $(grep -c '^EP ' ckpt/$t.ckpt 2>/dev/null || echo 0) records), caffeinate $C"
done
ps -axo command= | grep -q "^zsh $ROOT/air_guard.sh" || { G=$($ROOT/bin/detach.sh $ROOT/guard.out $ROOT zsh $ROOT/air_guard.sh); log "guard PID $G"; }
