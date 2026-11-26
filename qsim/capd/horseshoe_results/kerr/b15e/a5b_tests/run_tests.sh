#!/bin/zsh
# B15e A5b tests (registered in dcca6bc). Waits for the A5 tests (PID given as $1) to end, then runs serially, nice 10.
O=${0:A:h}; H=/Users/sumit/Github/quantum/qsim/capd/horseshoe; B=$H/../horseshoe_results/kerr/b15d; X=$H/hs_cover_b15e2
REF=$B/gb/hh2_N0N0.out; R=$O/results.txt; cd $H
while kill -0 $1 2>/dev/null; do sleep 30; done
r() { echo "$*" >> $R; }
norm() { grep -v '^EDGES RELOADED ' $1 | sed 's/reloaded_pieces=[0-9]*/reloaded_pieces=0/' > $2; }
mk() { sed "s#^checkpoint .*#checkpoint $2#" $B/gb/hh2_N0N0.spec > $1; }
r "binary $(shasum -a 256 $X | cut -c1-64)"
mk $O/b1.spec $O/b1.ckpt; nice -n 10 $X $O/b1.spec > $O/b1.out 2>&1
cmp -s $O/b1.out $REF && r "B1 BYTE-IDENTICAL ($(grep -c '^P ' $O/b1.ckpt) P records)" || r "B1 DIFFERS"
mk $O/b2.spec $O/b2.ckpt; nice -n 10 $X $O/b2.spec > $O/b2a.out 2>&1 & P=$!
while kill -0 $P 2>/dev/null && [[ $(grep -c '^P ' $O/b2.ckpt 2>/dev/null || echo 0) -lt 64 ]]; do sleep 2; done
kill -TERM $P; wait $P 2>/dev/null; r "B2 interrupted by SIGTERM with $(grep -c '^P ' $O/b2.ckpt) P records"
nice -n 10 $X $O/b2.spec > $O/b2b.out 2>&1; k=$(sed -n 's/.*reloaded_pieces=\([0-9]*\).*/\1/p' $O/b2b.out); norm $O/b2b.out $O/b2b.norm
cmp -s $O/b2b.norm $REF && (( k > 0 && k < 256 )) && r "B2 BYTE-IDENTICAL (normalised) after restart (reloaded_pieces $k)" || r "B2 FAIL (k '$k')"
cp $B/ckpt/gb/hh2_N0N0.ckpt $O/b3.ckpt; mk $O/b3.spec $O/b3.ckpt; nice -n 10 $X $O/b3.spec > $O/b3.out 2>&1
cmp -s $O/b3.out ../horseshoe_results/kerr/b15e/a4_identity/hh2_N0N0.out && r "B3 BYTE-IDENTICAL to a4_identity/hh2_N0N0.out (old-format checkpoint, $(sed -n 's/.*reloaded_pieces=\([0-9]*\).*/\1/p' $O/b3.out) reloaded)" || r "B3 DIFFERS"
n=$(grep -n '^P ' $O/b1.ckpt | sed -n 200p | cut -d: -f1); head -n $((n - 1)) $O/b1.ckpt > $O/b4.ckpt
echo "F N0>N0/15/15 FAILPIECE ORPHAN-RECORD-MUST-NOT-APPEAR" >> $O/b4.ckpt; L=$(sed -n ${n}p $O/b1.ckpt); printf '%s' "${L[1,$(( ${#L} / 2 ))]}" >> $O/b4.ckpt
mk $O/b4.spec $O/b4.ckpt; nice -n 10 $X $O/b4.spec > $O/b4.out 2>&1; norm $O/b4.out $O/b4.norm
cmp -s $O/b4.norm $REF && ! grep -q ORPHAN $O/b4.out && r "B4 BYTE-IDENTICAL (normalised) from a truncated + orphan-F checkpoint" || r "B4 FAIL"
nice -n 10 $X $O/b4.spec > $O/b4b.out 2>&1; norm $O/b4b.out $O/b4b.norm
cmp -s $O/b4b.norm $REF && ! grep -q ORPHAN $O/b4b.out && r "B4b BYTE-IDENTICAL (normalised) on a second restart" || r "B4b FAIL"
awk 'BEGIN{d=0} /^P / && !d {$4=$4+1; d=1} {print}' $O/b1.ckpt > $O/b5.ckpt; mk $O/b5.spec $O/b5.ckpt; nice -n 10 $X $O/b5.spec > $O/b5.out 2>&1
[[ "$(grep '^COVER' $O/b5.out | sed 's/reloaded_pieces=[0-9]*//')" != "$(grep '^COVER' $REF | sed 's/reloaded_pieces=[0-9]*//')" ]] && r "B5 MUST-FIRE PASS: tampered P record -> COVER differs" || r "B5 MUST-FIRE FAIL"
r "ALL DONE"
