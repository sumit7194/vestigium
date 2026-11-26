#!/bin/zsh
# B15e A6 addendum 3: promote ONE finished Air kerr_e chunk into b15d/kerr_e/, where the registered KERR reading reads it.
#   promote_air.sh <chunk>        (called by pull_air.sh after each pull; safe to call by hand)
# Promotes only if BOTH checks pass on the last good pulled copy (kerr_e_air/good/):
#   - <chunk>.out has a DONE line, exactly one COVER line, and no FATAL line;
#   - <chunk>.ckpt has 128 complete EP records (each ends " #"), and no EP line without the marker except a partial last line.
# Then: an existing kerr_e/<chunk>.out (outage-era) is RENAMED into kerr_e_void_outage/ (kept, never deleted or overwritten;
# a timestamp suffix if the name is taken); the good .out is copied with cp -p; source and copy sha256 must be equal; one
# record line goes to kerr_e_air/promote.log and to b15d/run.log. Idempotent: an identical kerr_e/<chunk>.out is a no-op.
# Never touches a process. Exit 0 = promoted or already promoted; 1 = refused (reason logged); 2 = usage.
# Written by Claude Opus 5.5 (Quantum-personal), 2026-11-26.
t=$1; [[ $t == N[0-5]N[0-5] ]] || { echo "usage: promote_air.sh N?N?" >&2; exit 2; }
K=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15d
GOOD=${PROMOTE_GOOD:-$K/kerr_e_air/good}; DEST=${PROMOTE_DEST:-$K/kerr_e}; VOID=${PROMOTE_VOID:-$K/kerr_e_void_outage}
PL=${PROMOTE_LOG:-$K/kerr_e_air/promote.log}; RL=${PROMOTE_RUNLOG:-$K/run.log}
log() { local l="$(date '+%F %T') $*"; echo "$l" >> $PL; echo "$l" >> $RL; }
src=$GOOD/$t.out; ck=$GOOD/$t.ckpt; dst=$DEST/$t.out
refuse() { log "PROMOTE $t REFUSED: $*"; exit 1; }
[[ -f $src && -f $ck ]] || refuse "missing $src or $ck"
grep -q '^DONE$' $src || refuse "no DONE in $src"
grep -q '^FATAL' $src && refuse "FATAL in $src"
(( $(grep -c '^COVER ' $src) == 1 )) || refuse "$(grep -c '^COVER ' $src) COVER lines in $src"
bad=$(awk 'NR>1 && prev ~ /^EP / && prev !~ / #$/ {b++} {prev=$0} END{print b+0}' $ck); n=$(grep -c '^EP .* #$' $ck)
(( bad == 0 && n == 128 )) || refuse "checkpoint $ck has $n complete EP records (need 128) and $bad incomplete inner EP lines"
s1=$(shasum -a 256 $src | cut -c1-64)
if [[ -f $dst ]]; then
  d0=$(shasum -a 256 $dst | cut -c1-64)
  if [[ $d0 == $s1 ]]; then echo "$t already promoted (sha $s1)"; exit 0; fi
  mkdir -p $VOID; v=$VOID/$t.out; [[ -e $v ]] && v=$VOID/$t.out.$(date +%Y%m%dT%H%M%S)
  [[ -e $v ]] && refuse "cannot find a free name in $VOID for the old $dst"
  mv -n $dst $v; [[ -f $v && ! -e $dst ]] || refuse "rename of the old $dst to $v did not happen"
  log "PROMOTE $t: old $dst (sha $d0) renamed to $v (kept)"
fi
cp -p $src $dst; s2=$(shasum -a 256 $dst | cut -c1-64)
[[ $s1 == $s2 ]] || refuse "copy sha $s2 != source sha $s1"
log "PROMOTE $t DONE-chunk from MacBook Air (ssh air, via pull_air.sh): src $src sha $s1 -> $dst sha $s2; checkpoint 128 EP records"
exit 0
