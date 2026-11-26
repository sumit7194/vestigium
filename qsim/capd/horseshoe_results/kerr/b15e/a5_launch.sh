#!/bin/zsh
# B15e A5 kerr_e relaunch (PREREG B15e A5; run only after the A5 tests pass AND on the Bridge's word). Run detached.
# For each chunk in order N1N2 N2N3 N3N4 N4N5 N5N0 N5N1, when my compute-job count < a5_mycap.txt and memory >= 50%:
#   1. the spec gains exactly ONE line "checkpoint <b15d>/ckpt/kerr/<chunk>.ckpt" after its arange line (old/new sha logged);
#   2. the old output is MOVED to kerr_e_void_outage/ (never deleted);
#   3. HS_WATCHDOG_S=2592000 nice -n 10 stdbuf -oL hs_cover_b15e2 <spec> > kerr_e/<chunk>.out, plus a kerr_guard.
# Refuses a binary sha mismatch, an existing checkpoint file, or a live process on the spec. Never kills. Log: a5_launch.log.
O=${0:A:h}; Q=/Users/sumit/Github/quantum; H=$Q/qsim/capd/horseshoe; B=$Q/qsim/capd/horseshoe_results/kerr/b15d; PY=$Q/sims/.venv/bin/python
SHA=77eb34a6a3cf9df54b6e678449b58b971e40d96a11c16314a287517933a42940
log() { echo "$(date '+%F %T') $*" >> $O/a5_launch.log; }
memfree() { memory_pressure -Q | sed -n 's/.*percentage: \([0-9]*\)%.*/\1/p' }
mycap() { local c=$(cat $O/a5_mycap.txt 2>/dev/null); [[ $c == <-> ]] && echo $c || echo 7 }
myjobs() { ps -axo user=,command= | awk '$1=="sumit"' | grep -cE "^sumit +($H/hs_cover|\./mn_so_|\./b17_check_pt)" }
live_spec() { ps -axo command= | grep -q "^$H/hs_cover[_a-z0-9]* $B/kerr_e/$1.spec" }
CH=(N1N2 N2N3 N3N4 N4N5 N5N0 N5N1); n=1
log "A5 launcher start PID $$ (cap $(mycap), my jobs $(myjobs))"
mkdir -p $B/ckpt/kerr $B/kerr_e_void_outage
while (( n <= ${#CH} )); do
  t=${CH[$n]}
  if (( $(myjobs) >= $(mycap) )) || (( $(memfree) < 50 )); then sleep 60; continue; fi
  [[ $(shasum -a 256 $H/hs_cover_b15e2 | cut -c1-64) == $SHA ]] || { log "REFUSED $t: binary sha mismatch"; (( n++ )); continue; }
  [[ -e $B/ckpt/kerr/$t.ckpt ]] && { log "REFUSED $t: checkpoint file exists"; (( n++ )); continue; }
  live_spec $t && { log "REFUSED $t: a live process runs this spec"; (( n++ )); continue; }
  old=$(shasum -a 256 $B/kerr_e/$t.spec | cut -c1-64)
  if ! grep -q "^checkpoint " $B/kerr_e/$t.spec; then
    awk -v c="checkpoint $B/ckpt/kerr/$t.ckpt" '{print} /^arange /{print c}' $B/kerr_e/$t.spec > $B/kerr_e/$t.spec.new && mv $B/kerr_e/$t.spec.new $B/kerr_e/$t.spec
  fi
  new=$(shasum -a 256 $B/kerr_e/$t.spec | cut -c1-64)
  [[ $(grep -c "^checkpoint " $B/kerr_e/$t.spec) == 1 && $(grep -c "^param level -1/2$" $B/kerr_e/$t.spec) == 1 ]] || { log "REFUSED $t: spec gate"; (( n++ )); continue; }
  [[ -e $B/kerr_e/$t.out ]] && mv $B/kerr_e/$t.out $B/kerr_e_void_outage/$t.out
  P=$(HS_WATCHDOG_S=2592000 _STDBUF_O=L $Q/tools/detach.sh $B/kerr_e/$t.out $H nice -n 10 /usr/bin/stdbuf -oL $H/hs_cover_b15e2 $B/kerr_e/$t.spec)
  sleep 3; G=$($Q/tools/detach.sh $B/kerr_guard_$t.out $H $PY $H/kerr_guard.py $P)
  log "START kerr_e/$t PID $P (hs_cover_b15e2, HS_WATCHDOG_S=2592000, checkpoint ckpt/kerr/$t.ckpt; spec sha $old -> $new; old output -> kerr_e_void_outage/), kerr_guard $G, memfree $(memfree)%"
  (( n++ )); sleep 60
done
log "A5 launcher done: all 6 handled"
