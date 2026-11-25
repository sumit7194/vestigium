#!/bin/zsh
# B15e A4 + branch-S launcher (replaces retry_s/launch_retry.sh, which was paused). Run detached, AFTER the A4 identity
# checks pass. Priority (the Bridge, 2026-11-25): kerr_e reruns FIRST, then branch-S pieces pm, pp, then the ref worker.
#  - A kerr_e chunk is eligible for a rerun when its output holds "WATCHDOG TIMEOUT" and no live process runs its spec.
#    N5N1 becomes eligible only that way (it stays on the old binary until then).
#  - Rerun: the old output is MOVED to kerr_e_void_watchdog/, never deleted; the spec gate is checked; then
#    HS_WATCHDOG_S=432000 nice -n 10 stdbuf -oL hs_cover_b15e <spec> > kerr_e/<chunk>.out.
#  - Cap: my compute jobs (hs_cover*, ./mn_so_*, the refs worker counted once) stay <= the number in a4_mycap.txt.
#  - Memory gate: launch only at >= 50% free. Never kills anything. Logs to a4_launch.log.
O=${0:A:h}; Q=/Users/sumit/Github/quantum; H=$Q/qsim/capd/horseshoe; B=$Q/qsim/capd/horseshoe_results/kerr/b15d
RS=$Q/qsim/capd/horseshoe_results/so_mn/erep/retry_s; T=$H/tests; PY=$Q/sims/.venv/bin/python
SHA_HS=c924b03bf3328a4960673879b61ab3c0679bdae685270a9145da80f155f7b903; SHA_PC=491fb0a1d2e0c91df04efc07db3e1826a2a352c2cc91a055527fc19b1b9b6510
typeset -A OFF; OFF=(pm "1/20000000 -1/20000000" pp "1/20000000 1/20000000")
log() { echo "$(date '+%F %T') $*" >> $O/a4_launch.log; }
memfree() { memory_pressure -Q | sed -n 's/.*percentage: \([0-9]*\)%.*/\1/p' }
mycap() { local c=$(cat $O/a4_mycap.txt 2>/dev/null); [[ $c == <-> ]] && echo $c || echo 8 }
myjobs() { local a=$(ps -axo user=,command= | awk '$1=="sumit"' | grep -cE "^sumit +($H/hs_cover|\./mn_so_)")
           local r=$(ps -axo user=,command= | awk '$1=="sumit"' | grep -c "refs_serial.sh"); echo $(( a + (r > 0 ? 1 : 0) )) }
live_spec() { ps -axo command= | grep -q "^$H/hs_cover[_a-z0-9]* $B/kerr_e/$1.spec" }
KE=(N1N2 N2N3 N3N4 N4N5 N5N0 N5N1); typeset -A DONE_KE; PIECES=(pm pp refs); np=1
eligible() { local t=$1; [[ -z ${DONE_KE[$t]} ]] && grep -q "WATCHDOG TIMEOUT" $B/kerr_e/$t.out 2>/dev/null && ! live_spec $t }
rerun() { local t=$1
  [[ $(shasum -a 256 $H/hs_cover_b15e | cut -c1-64) == $SHA_HS ]] || { log "REFUSED rerun $t: binary sha mismatch"; DONE_KE[$t]=refused; return }
  [[ $(grep -c "^param level -1/2$" $B/kerr_e/$t.spec) == 1 && $(grep -c "^system mn$" $B/kerr_e/$t.spec) == 1 ]] || { log "REFUSED rerun $t: spec gate"; DONE_KE[$t]=refused; return }
  mkdir -p $B/kerr_e_void_watchdog; mv $B/kerr_e/$t.out $B/kerr_e_void_watchdog/$t.out
  local P=$(HS_WATCHDOG_S=432000 _STDBUF_O=L $Q/tools/detach.sh $B/kerr_e/$t.out $H nice -n 10 /usr/bin/stdbuf -oL $H/hs_cover_b15e $B/kerr_e/$t.spec)
  DONE_KE[$t]=$P; log "RERUN kerr_e/$t PID $P (hs_cover_b15e, HS_WATCHDOG_S=432000; old output -> kerr_e_void_watchdog/), memfree $(memfree)%" }
piece() { local p=$1
  [[ -e $RS/$p/st ]] && { log "REFUSED piece $p: state exists"; return }
  [[ $(shasum -a 256 $T/mn_so_piece | cut -c1-64) == $SHA_PC ]] || { log "REFUSED piece $p: binary sha mismatch"; return }
  mkdir -p $RS/$p; cd $T
  local P=$(CENTRE_OFFSET="${OFF[$p]}" SO_EREP=zsym SO_FIXED_REDO=1 SAVE_FROM=292 SAVE_DT=100 $Q/tools/detach.sh $RS/$p/run.out $T nice -n 10 ./mn_so_piece 1/20000000 $RS/cp/b17_cp_5e-8_$p.txt $RS/$p/st 805.3)
  sleep 5; local G=$($Q/tools/detach.sh $RS/$p/guard.out $T nice -n 10 $PY $H/erep_guard.py $P $RS/$p/guard.log 500 --inform)
  log "start piece $p PID $P (offset ${OFF[$p]}), guard $G, memfree $(memfree)%" }
log "A4 launcher start PID $$ (cap $(mycap), my jobs $(myjobs))"
while :; do
  n5=$(grep -c "^DONE" $B/kerr_e/N5N1.out 2>/dev/null)
  pending=0; for t in $KE; do [[ -z ${DONE_KE[$t]} ]] && ! { [[ $t == N5N1 ]] && (( n5 > 0 )) } && pending=1; done
  (( np > ${#PIECES} && pending == 0 )) && break
  if (( $(myjobs) < $(mycap) )); then
    if (( $(memfree) < 50 )); then sleep 300; continue; fi
    next=""; for t in $KE; do eligible $t && { next=$t; break }; done
    if [[ -n $next ]]; then rerun $next
    elif (( np <= ${#PIECES} )); then
      if [[ ${PIECES[$np]} == refs ]]; then R=$($Q/tools/detach.sh $RS/refs_serial.out $RS zsh $RS/refs_serial.sh); log "start refs worker PID $R, memfree $(memfree)%"
      else piece ${PIECES[$np]}; fi; (( np++ ))
    fi
  fi
  sleep 60
done
log "A4 launcher done"
