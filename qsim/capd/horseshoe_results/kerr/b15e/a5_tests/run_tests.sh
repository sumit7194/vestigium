#!/bin/zsh
# B15e A5 identity tests (registered in 751923d, 38a1364, d77d21b). Serial, one core, nice 10. Results -> results.txt
O=${0:A:h}; H=/Users/sumit/Github/quantum/qsim/capd/horseshoe; B=$H/../horseshoe_results/kerr/b15d; X=$H/hs_cover_b15e2
REF=$B/twin_e/swap_N0N0.out; R=$O/results.txt; cd $H
r() { echo "$*" >> $R; }
r "binary $(shasum -a 256 $X | cut -c1-64)"
# T1: no checkpoint line -> byte-identical to the stored outputs
for t in r1_MM r1_MN r1_NM r1_NN; do nice -n 10 $X $B/gb/$t.spec > $O/t1_$t.out 2>&1; cmp -s $O/t1_$t.out $B/gb/$t.out && r "T1 $t BYTE-IDENTICAL" || r "T1 $t DIFFERS"; done
mk() { awk -v c="checkpoint $2" '{print} /^arange /{print c}' $B/twin_e/swap_N0N0.spec > $1; }
# T3: fresh checkpoint, uninterrupted
mk $O/t3.spec $O/t3.ckpt; nice -n 10 $X $O/t3.spec > $O/t3.out 2>&1
cmp -s $O/t3.out $REF && r "T3 BYTE-IDENTICAL to the stored swap_N0N0.out ($(grep -c '^EP ' $O/t3.ckpt) EP records)" || r "T3 DIFFERS"
# T4: deliberate SIGTERM once >= 32 EP lines, then restart
mk $O/t4.spec $O/t4.ckpt; nice -n 10 $X $O/t4.spec > $O/t4a.out 2>&1 & P=$!
while kill -0 $P 2>/dev/null && [[ $(grep -c '^EP ' $O/t4.ckpt 2>/dev/null || echo 0) -lt 32 ]]; do sleep 2; done
kill -TERM $P; wait $P 2>/dev/null; k0=$(grep -c '^EP ' $O/t4.ckpt); r "T4 interrupted by SIGTERM with $k0 EP records"
nice -n 10 $X $O/t4.spec > $O/t4b.out 2>&1
k=$(sed -n 's/^EDGES RELOADED //p' $O/t4b.out); grep -v '^EDGES RELOADED ' $O/t4b.out > $O/t4b_stripped.out
if cmp -s $O/t4b_stripped.out $REF && [[ -n $k && $k -gt 0 && $k -lt 128 ]]; then r "T4 BYTE-IDENTICAL after restart (EDGES RELOADED $k)"; else r "T4 FAIL (EDGES RELOADED '$k')"; fi
# T5: must-fire: tamper one EP line (dL + 1) -> the COVER line must differ
awk 'BEGIN{d=0} /^EP / && !d {$3=$3+1; d=1} {print}' $O/t3.ckpt > $O/t5.ckpt; mk $O/t5.spec $O/t5.ckpt
nice -n 10 $X $O/t5.spec > $O/t5.out 2>&1
[[ "$(grep '^COVER' $O/t5.out)" != "$(grep '^COVER' $REF)" ]] && r "T5 MUST-FIRE PASS: tampered checkpoint -> COVER line differs" || r "T5 MUST-FIRE FAIL: COVER identical despite tampering"
# T6: truncate mid-way through the 100th EP line, with an orphan EF line before the cut; then T6b: a second restart
n=$(grep -n '^EP ' $O/t3.ckpt | sed -n 100p | cut -d: -f1); head -n $((n - 1)) $O/t3.ckpt > $O/t6.ckpt
echo "EF N0>N0/E/1/63 FAILPIECE ORPHAN-RECORD-MUST-NOT-APPEAR" >> $O/t6.ckpt
L=$(sed -n ${n}p $O/t3.ckpt); printf '%s' "${L[1,$(( ${#L} / 2 ))]}" >> $O/t6.ckpt
mk $O/t6.spec $O/t6.ckpt; nice -n 10 $X $O/t6.spec > $O/t6.out 2>&1
k=$(sed -n 's/^EDGES RELOADED //p' $O/t6.out); grep -v '^EDGES RELOADED ' $O/t6.out > $O/t6_stripped.out
cmp -s $O/t6_stripped.out $REF && ! grep -q ORPHAN $O/t6.out && r "T6 BYTE-IDENTICAL from a truncated + orphan-EF checkpoint (EDGES RELOADED $k)" || r "T6 FAIL"
nice -n 10 $X $O/t6.spec > $O/t6b.out 2>&1
k=$(sed -n 's/^EDGES RELOADED //p' $O/t6b.out); grep -v '^EDGES RELOADED ' $O/t6b.out > $O/t6b_stripped.out
cmp -s $O/t6b_stripped.out $REF && [[ $k == 128 ]] && r "T6b BYTE-IDENTICAL on a second restart (all 128 reloaded)" || r "T6b FAIL (EDGES RELOADED '$k')"
r "ALL DONE"
