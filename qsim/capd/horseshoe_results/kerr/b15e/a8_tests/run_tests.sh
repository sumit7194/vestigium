#!/bin/zsh
# B15e A8 identity tests (registered cf57b17 + correction 1; binary hs_cover_b15e5 3a3c4bbe; the b15e4 run is superseded). NOT COUNTED. Serial, one core;
# the whole script is launched at nice 15 (children inherit it). Results -> results.txt. Every case runs in its OWN new
# folder with RELATIVE checkpoint/subckpt/progress paths, so all cases of one test spec share one spec text (and one
# journal hash). Nothing outside a8_tests/ is written. Written by Claude Opus 5.5 (Quantum-personal).
O=${0:A:h}; H=/Users/sumit/Github/quantum/qsim/capd/horseshoe; B=$H/../horseshoe_results/kerr/b15d; X=$H/hs_cover_b15e5
PY=/Users/sumit/Github/quantum/sims/.venv/bin/python; R=$O/results.txt; NOD='^NEVER-MATCH$'
r() { echo "$(date '+%F %T') $*" >> $R; }
# mk <src spec> <dst spec> <drop regex> <lines to add before the first cover line, '|'-separated>
mk() { awk -v drop="$3" -v add="$4" 'BEGIN{n=split(add,A,"|")} /^cover / && !d {for(i=1;i<=n;i++) print A[i]; d=1} $0 ~ drop {next} {print}' $1 > $2; }
norm() { grep -v '^EDGES RELOADED ' $1 | sed 's/reloaded_pieces=[0-9]*/reloaded_pieces=0/' > $2; }
nj() { [[ -f $1 ]] && awk '/^J /{n++} END{print n+0}' $1 || echo 0; }
fresh() { [[ -e $O/$1 ]] && { r "REFUSED: $O/$1 exists (nothing is overwritten)"; exit 1; }; mkdir -p $O/$1; }
runin() { (cd $O/$1 && $X c.spec > $2 2>&1) }        # runin <case dir> <out name>
fails() { grep '^FAILPIECE' $1 | sort; }
# kill_at <case dir> <K> <out name>: run; SIGTERM once c.jnl holds >= K J records; prints KILLED or ENDED
kill_at() { (cd $O/$1 && { $X c.spec > $3 2>&1 & P=$!
  while kill -0 $P 2>/dev/null && (( $(nj c.jnl) < $2 )); do sleep 0.2; done
  if kill -0 $P 2>/dev/null; then kill -TERM $P; wait $P 2>/dev/null; echo KILLED; else wait $P; echo ENDED; fi }) }
# after a kill: was it mid-piece (no P/EP record yet for the last journal record's key)?
midpiece() { local l=$(grep '^J ' $O/$1/c.jnl | tail -1); local ph=${${(s: :)l}[2]} key=${${(s: :)l}[3]}
  if [[ $ph == A ]]; then grep -q "^P $key " $O/$1/c.ckpt && echo no || echo yes; else grep -q "^EP $key " $O/$1/c.ckpt && echo no || echo yes; fi }
replayed() { sed -n 's/.* replayed=\([0-9]*\) .*/\1/p' $O/$1/c.prog; }
progok() { [[ $(wc -l < $O/$1/c.prog | tr -d ' ') == 1 ]] && grep -qE '^[0-9]+ [0-9-]+ [0-9:]+ phase=[AE] key=[^ ]+ depth=[0-9]+ leaves=[0-9]+ live=[0-9]+ replayed=[0-9]+ nsteps=[0-9]+ last_s=[0-9.]+ mean_s=[0-9.]+ state=end$' $O/$1/c.prog; }
r "START binary $(shasum -a 256 $X | cut -c1-64) nice $(ps -o ni= -p $$ | tr -d ' ')"

SA="depth 8 12|caps 120 4096|arange 6 7|noedges|piececap 330 0"; SADROP='^(checkpoint|depth|caps) '
CK="checkpoint c.ckpt"; SUB="subckpt c.jnl|progress c.prog 50"

# ---------------- T7 (correction 1): HS_WATCHDOG_S parsing and the real timer (HS_WATCHDOG_REPORT=1 reads getitimer)
wd() { HS_WATCHDOG_REPORT=1 $X 2>&1 | sed -n 's/^WATCHDOG //p'; }          # no spec: report, then the usage line
v=$(unset HS_WATCHDOG_S; wd); (( v >= 172790 && v <= 172800 )) && r "T7 unset: WATCHDOG $v (48 h) PASS" || r "T7 unset FAIL ('$v')"
v=$(HS_WATCHDOG_S=100000000 wd); (( v >= 99999990 && v <= 100000000 )) && r "T7 100000000: WATCHDOG $v PASS" || r "T7 100000000 FAIL ('$v')"
fresh t7_off; cp $B/gb/r1_MM.spec $O/t7_off/c.spec; (cd $O/t7_off && HS_WATCHDOG_S=off HS_WATCHDOG_REPORT=1 $X c.spec > c.out 2>&1)
grep -qx 'WATCHDOG none' $O/t7_off/c.out && cmp -s <(grep -v '^WATCHDOG ' $O/t7_off/c.out) $B/gb/r1_MM.out && r "T7 off: WATCHDOG none (no timer); r1_MM output BYTE-IDENTICAL otherwise PASS" || r "T7 off FAIL ($(head -1 $O/t7_off/c.out))"
fresh t7_mf; mk $B/gb/hh2_N0N0.spec $O/t7_mf/c.spec '^checkpoint ' "$CK"; t0s=$(date +%s)
(cd $O/t7_mf && HS_WATCHDOG_S=60 $X c.spec > c.out 2>&1); ec=$?; dt=$(( $(date +%s) - t0s ))
[[ $ec == 124 ]] && grep -q 'WATCHDOG TIMEOUT' $O/t7_mf/c.out && (( dt >= 60 && dt <= 70 )) && r "T7 60 must-fire PASS (exit 124 after $dt s)" || r "T7 60 must-fire FAIL (exit $ec after $dt s)"
fresh t7_bad; cp $B/gb/r1_MM.spec $O/t7_bad/c.spec; nb=0
for b in "" abc 0 -5 10y 100000001 " 60"; do (cd $O/t7_bad && HS_WATCHDOG_S="$b" $X c.spec > "bad_$nb.out" 2>&1); ec=$?
  if [[ $ec == 1 ]] && grep -q "^FATAL HS_WATCHDOG_S='$b'" "$O/t7_bad/bad_$nb.out" && ! grep -q '^PREC' "$O/t7_bad/bad_$nb.out"; then r "T7 bad '$b': FATAL at startup, exit 1, no PREC PASS"; else r "T7 bad '$b' FAIL (exit $ec)"; fi
  nb=$((nb + 1)); done

# ---------------- T0: no new lines -> byte-identical to the stored outputs
for t in r1_MM r1_MN r1_NM r1_NN; do fresh t0_$t; cp $B/gb/$t.spec $O/t0_$t/c.spec; runin t0_$t c.out
  cmp -s $O/t0_$t/c.out $B/gb/$t.out && r "T0 $t BYTE-IDENTICAL" || r "T0 $t DIFFERS"; done
fresh t0_hh2; mk $B/gb/hh2_N0N0.spec $O/t0_hh2/c.spec '^checkpoint ' "$CK"; runin t0_hh2 c.out
cmp -s $O/t0_hh2/c.out $B/gb/hh2_N0N0.out && r "T0 hh2_N0N0 (fresh checkpoint) BYTE-IDENTICAL ($(grep -c '^P ' $O/t0_hh2/c.ckpt) P records)" || r "T0 hh2_N0N0 DIFFERS"
fresh t0_swap; mk $B/twin_e/swap_N0N0.spec $O/t0_swap/c.spec $NOD "$CK"; runin t0_swap c.out
cmp -s $O/t0_swap/c.out $B/twin_e/swap_N0N0.out && r "T0 swap_N0N0 edges (checkpoint) BYTE-IDENTICAL ($(grep -c '^EP ' $O/t0_swap/c.ckpt) EP records)" || r "T0 swap_N0N0 DIFFERS"

# ---------------- T1: subckpt + progress on, uninterrupted
t1() { local c=$1 ref=$2
  if cmp -s $O/$c/c.out $ref && progok $c && [[ $(nj $O/$c/c.jnl) == $(sed -n 's/.* live=\([0-9]*\) .*/\1/p' $O/$c/c.prog) ]] && [[ $(replayed $c) == 0 ]]; then
    r "T1 $c BYTE-IDENTICAL; progress 1 line state=end; journal $(nj $O/$c/c.jnl) records = live evaluations"
  else r "T1 $c FAIL (cmp $(cmp -s $O/$c/c.out $ref && echo same || echo DIFFERS), prog '$(cat $O/$c/c.prog)', journal $(nj $O/$c/c.jnl))"; fi }
fresh t1_hh2; mk $B/gb/hh2_N0N0.spec $O/t1_hh2/c.spec '^checkpoint ' "$CK|$SUB"; runin t1_hh2 c.out; t1 t1_hh2 $B/gb/hh2_N0N0.out
fresh t1_swap; mk $B/twin_e/swap_N0N0.spec $O/t1_swap/c.spec $NOD "$CK|$SUB"; runin t1_swap c.out; t1 t1_swap $B/twin_e/swap_N0N0.out

# ---------------- T2: interrupts inside bisection trees
fresh sa_ref; mk $B/twin/rot90_N0N0.spec $O/sa_ref/c.spec $SADROP "$SA|$CK"; runin sa_ref c.out
r "SA reference: $(grep '^COVER' $O/sa_ref/c.out | cut -c1-160) ($(grep -c '^FAILPIECE' $O/sa_ref/c.out) FAILPIECE)"
fresh sa_full; mk $B/twin/rot90_N0N0.spec $O/sa_full/c.spec $SADROP "$SA|$CK|$SUB"; runin sa_full c.out
cmp -s $O/sa_full/c.out $O/sa_ref/c.out && r "SA with subckpt, uninterrupted: BYTE-IDENTICAL to the SA reference ($(nj $O/sa_full/c.jnl) records)" || r "SA with subckpt DIFFERS from the SA reference"
$PY $O/pick.py SA $O/sa_full/c.jnl 8 > $O/sa_picks.txt; r "SA picks: $(tr '\n' ' ' < $O/sa_picks.txt)"
grep -q '^throw None' $O/sa_picks.txt && { r "SA has no thrown node below the top level: STOP for the registered piececap recalibration (to the Bridge)"; exit 0; }
t2() { local c=$1 K=$2 ref=$3 src=$4; fresh $c; cp $O/$src/c.spec $O/$c/c.spec
  [[ $K == None ]] && { r "T2 $c: no such record in the full journal: NOT RUN"; return; }
  local st=$(kill_at $c $K a.out) n=$(nj $O/$c/c.jnl) last=$(grep '^J ' $O/$c/c.jnl | tail -1 | cut -d' ' -f2-4) mid=$(midpiece $c)
  cp $O/$c/c.jnl $O/$c/at_kill.jnl; cp $O/$c/c.ckpt $O/$c/at_kill.ckpt
  runin $c b.out; norm $O/$c/b.out $O/$c/b.norm; local rp=$(replayed $c)
  if [[ $st == KILLED && $mid == yes ]] && (( rp > 0 )) && cmp -s $O/$c/b.norm $ref; then
    r "T2 $c PASS: SIGTERM at record $n (target $K; last '$last', mid-piece), $rp nodes replayed, restart BYTE-IDENTICAL (normalised)"
  else r "T2 $c FAIL (state $st, record $n, target $K, last '$last', mid-piece $mid, replayed $rp, cmp $(cmp -s $O/$c/b.norm $ref && echo same || echo DIFFERS))"; fi }
while read lab K; do t2 sa_$lab $K $O/sa_ref/c.out sa_full; done < $O/sa_picks.txt
$PY $O/pick.py SE $O/t1_swap/c.jnl > $O/se_picks.txt; r "SE picks: $(tr '\n' ' ' < $O/se_picks.txt)"
while read lab K; do t2 se_$lab $K $B/twin_e/swap_N0N0.out t1_swap; done < $O/se_picks.txt

# ---------------- T4: must-fire (a recorded ok flipped 1 -> 0, fresh checkpoint)
fresh t4; cp $O/sa_full/c.spec $O/t4/c.spec; i=$($PY $O/pick.py flip $O/sa_depth8/at_kill.jnl $O/t4/c.jnl); runin t4 c.out
if [[ $i != None && ( "$(grep '^COVER' $O/t4/c.out)" != "$(grep '^COVER' $O/sa_ref/c.out)" || "$(fails $O/t4/c.out)" != "$(fails $O/sa_ref/c.out)" ) ]]; then
  r "T4 MUST-FIRE PASS: record $i (ok 1 -> 0) changes the COVER line or the FAILPIECE set"
else r "T4 MUST-FIRE FAIL (flipped record '$i'): output unchanged"; fi

# ---------------- T5: torn last record + a NUL line (fresh checkpoint); T5b: another spec's journal
fresh t5; cp $O/sa_full/c.spec $O/t5/c.spec; k=$($PY $O/pick.py torn $O/sa_full/c.jnl $O/t5/c.jnl); runin t5 c.out; norm $O/t5/c.out $O/t5/c.norm
grep -q 'NUL' $O/t5/c.out && r "T5 FAIL: NUL text reached the output" || {
  cmp -s $O/t5/c.norm $O/sa_ref/c.out && (( $(replayed t5) > 0 )) && r "T5 PASS: journal of $k records + NUL line + torn record -> BYTE-IDENTICAL, $(replayed t5) replayed" || r "T5 FAIL (cmp $(cmp -s $O/t5/c.norm $O/sa_ref/c.out && echo same || echo DIFFERS), replayed $(replayed t5))"; }
fresh t5b; cp $O/sa_full/c.spec $O/t5b/c.spec; cp $O/t1_swap/c.jnl $O/t5b/c.jnl; n0=$(nj $O/t5b/c.jnl); runin t5b c.out
grep -q '^FATAL subckpt: journal c.jnl belongs to another spec' $O/t5b/c.out && [[ $(nj $O/t5b/c.jnl) == $n0 ]] && [[ ! -e $O/t5b/c.prog ]] && ! grep -q '^FAILPIECE\|^COVER' $O/t5b/c.out \
  && r "T5b PASS: another spec's journal -> FATAL at startup, no evaluation, journal unchanged" || r "T5b FAIL: $(head -3 $O/t5b/c.out | tr '\n' ' ')"

# ---------------- T3: solver state on Kerr (2 edge pieces, every replay throws at 600 steps, one split each)
KS="depth 16 1|piececap 600 0|$CK"; KDROP='^(cover|depth|checkpoint) '
fresh t3_ref; mk $B/kerr_e/N0N0.spec $O/t3_ref/c.spec $KDROP "$KS|cover N0 N0 16 16 1"; runin t3_ref c.out
r "T3 reference: $(grep '^COVER' $O/t3_ref/c.out | cut -c1-200) ($(grep -c '^FAILPIECE' $O/t3_ref/c.out) FAILPIECE)"
fresh t3_src; mk $B/kerr_e/N0N0.spec $O/t3_src/c.spec $KDROP "$KS|$SUB|cover N0 N0 16 16 1"
t2 t3 2 $O/t3_ref/c.out t3_src
r "ALL DONE"
