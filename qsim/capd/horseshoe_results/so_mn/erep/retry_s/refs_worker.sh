#!/bin/zsh
# Branch-S C-floor reference worker WITH an atomic per-ref claim (replaces refs_serial.sh; the Bridge, 2026-11-26).
# Usage: refs_worker.sh <plan> <fwd|rev> [refs_dir]. Several workers may run at once on the same plan:
#  - a ref whose output already ends with a "B17 " summary line is skipped;
#  - otherwise the worker claims it with `mkdir <refs>/locks/<p>_<q>` (atomic), writing its PID into the lock's owner file;
#  - an existing lock whose owner PID is dead, on an incomplete output, is STALE: it is taken over (the output is redone);
#  - a lock with a live owner is skipped.
# DRY=1 replaces the b17_check_pt call with a 1-3 s fake that writes "B17 DRY" (for the lock test only).
PLAN=$1; ORDER=${2:-fwd}; R=${3:-${0:A:h}/refs}; T=/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests; CP=${0:A:h}/cp
mkdir -p $R/locks; L=$R/../refs.log; [[ -n $DRY ]] && L=$R/dry.log
log() { echo "$(date '+%F %T') [worker $$ $ORDER] $*" >> $L; }
lines=("${(@f)$(cat $PLAN)}"); [[ $ORDER == rev ]] && lines=("${(@Oa)lines}")
for ln in $lines; do
  set -- ${=ln}; p=$1; q=$2; du=$3; dp=$4; out=$R/ref_${p}_${q}.out; lk=$R/locks/${p}_${q}
  [[ -f $out ]] && grep -q "^B17 " $out && continue
  if ! mkdir $lk 2>/dev/null; then
    o=$(cat $lk/owner 2>/dev/null); if [[ -n $o ]] && kill -0 $o 2>/dev/null; then continue; fi
    log "STALE lock $p/$q (owner '$o' gone, output incomplete): taking over"
  fi
  echo $$ > $lk/owner
  log "start $p/$q offset $du $dp"
  if [[ -n $DRY ]]; then sleep $(( RANDOM % 3 + 1 )); echo "B17 DRY $p $q by $$" > $out
  else ( cd $T && CENTRE_OFFSET="$du $dp" nice -n 10 ./b17_check_pt 0/1 $CP/b17_cp_5e-8_$p.txt > $out 2>&1 ); fi
  log "end $p/$q : $(tail -1 $out | cut -c1-100)"
done
log "worker done"
