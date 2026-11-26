#!/bin/zsh
# B15e A8 T2-SA7 (the personal Bridge's request, 2026-11-26): one more SA interrupt at a DIFFERENT sub-top-level throw
# than the throw/depth1 pick (record 2). All 4 sub-top-level throws in the 310/60 reference are at depth 1; record 84
# (piece N0>N0/6/1, path 1) is used: another piece and another path, so the resume reloads 6/0's P record and replays
# 6/1's journal. It runs once T2's SE set is logged: the main run (PID $1) and its b15e5 child are PAUSED (SIGSTOP; a test
# process only; results do not depend on time), SA7 runs on the same single core, then both are resumed (SIGCONT).
# Same binary, same spec (sa_full/c.spec), judged against sa_ref/c.out only. Written by Claude Opus 5.5 (Quantum-personal).
O=${0:A:h}; H=/Users/sumit/Github/quantum/qsim/capd/horseshoe; X=$H/hs_cover_b15e5; R=$O/results.txt; M=$1; K=84; c=sa7
r() { echo "$(date '+%F %T') $*" >> $R; }
nj() { [[ -f $1 ]] && awk '/^J /{n++} END{print n+0}' $1 || echo 0; }
norm() { grep -v '^EDGES RELOADED ' $1 | sed 's/reloaded_pieces=[0-9]*/reloaded_pieces=0/' > $2; }
until grep -qE '^.{20}T2 se_certfail|^.{20}T4 |STOP|ALL DONE' $R; do kill -0 $M 2>/dev/null || break; sleep 20; done
kids=($(pgrep -f "^$X c.spec"))
kill -STOP $M $kids 2>/dev/null; r "T2-SA7: main run $M and child(ren) ${kids[*]} PAUSED (SIGSTOP) for SA7"
[[ -e $O/$c ]] && { r "T2-SA7 REFUSED: $O/$c exists"; kill -CONT $kids $M; exit 1; }
mkdir $O/$c; cp $O/sa_full/c.spec $O/$c/c.spec
st=$(cd $O/$c && { $X c.spec > a.out 2>&1 & P=$!
  while kill -0 $P 2>/dev/null && (( $(nj c.jnl) < K )); do sleep 0.2; done
  if kill -0 $P 2>/dev/null; then kill -TERM $P; wait $P 2>/dev/null; echo KILLED; else wait $P; echo ENDED; fi })
n=$(nj $O/$c/c.jnl); l=$(grep '^J ' $O/$c/c.jnl | tail -1); last=$(echo $l | cut -d' ' -f2-4); key=$(echo $l | cut -d' ' -f3)
grep -q "^P $key " $O/$c/c.ckpt && mid=no || mid=yes
cp $O/$c/c.jnl $O/$c/at_kill.jnl; cp $O/$c/c.ckpt $O/$c/at_kill.ckpt
(cd $O/$c && $X c.spec > b.out 2>&1); norm $O/$c/b.out $O/$c/b.norm
rp=$(sed -n 's/.* replayed=\([0-9]*\) .*/\1/p' $O/$c/c.prog); rl=$(sed -n 's/.*reloaded_pieces=\([0-9]*\).*/\1/p' $O/$c/b.out)
if [[ $st == KILLED && $mid == yes ]] && (( rp > 0 )) && cmp -s $O/$c/b.norm $O/sa_ref/c.out; then
  r "T2-SA7 PASS: SIGTERM at record $n (target $K, a depth-1 throw in 6/1; last '$last', mid-piece), $rl piece(s) reloaded, $rp nodes replayed, restart BYTE-IDENTICAL (normalised)"
else r "T2-SA7 FAIL (state $st, record $n, target $K, last '$last', mid-piece $mid, replayed $rp, cmp $(cmp -s $O/$c/b.norm $O/sa_ref/c.out && echo same || echo DIFFERS))"; fi
kill -CONT $kids $M 2>/dev/null; r "T2-SA7: main run $M and child(ren) ${kids[*]} RESUMED (SIGCONT)"
