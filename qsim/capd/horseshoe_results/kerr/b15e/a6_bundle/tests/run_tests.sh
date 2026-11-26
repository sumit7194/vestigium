#!/bin/zsh
# B15e A6 identity tests, path-independent (the bundle root = two levels up). The same files run on the Mac mini (stage i)
# and on the Air (stage ii). T1, T3, T4, T5, T6, T6b as in A5; references = the bundle's ref/ (from the Mac mini's b15d).
ROOT=${0:A:h:h}; X=$ROOT/bin/hs_cover_b15e2s; O=$ROOT/tests/out_$(hostname -s); mkdir -p $O; R=$O/results.txt; REF=$ROOT/ref/swap_N0N0.out; cd $ROOT
r() { echo "$*" >> $R; }
r "host $(hostname -s) $(sysctl -n machdep.cpu.brand_string) macOS $(sw_vers -productVersion); binary $(shasum -a 256 $X | cut -c1-64)"
for t in r1_MM r1_MN r1_NM r1_NN; do nice -n 10 $X $ROOT/ref/$t.spec > $O/t1_$t.out 2>&1; cmp -s $O/t1_$t.out $ROOT/ref/$t.out && r "T1 $t BYTE-IDENTICAL" || r "T1 $t DIFFERS"; done
mk() { awk -v c="checkpoint $2" '{print} /^arange /{print c}' $ROOT/ref/swap_N0N0.spec > $1; }
mk $O/t3.spec $O/t3.ckpt; nice -n 10 $X $O/t3.spec > $O/t3.out 2>&1
cmp -s $O/t3.out $REF && r "T3 BYTE-IDENTICAL ($(grep -c '^EP ' $O/t3.ckpt) EP records)" || r "T3 DIFFERS"
mk $O/t4.spec $O/t4.ckpt; nice -n 10 $X $O/t4.spec > $O/t4a.out 2>&1 & P=$!
while kill -0 $P 2>/dev/null && [[ $(grep -c '^EP ' $O/t4.ckpt 2>/dev/null || echo 0) -lt 32 ]]; do sleep 2; done
kill -TERM $P; wait $P 2>/dev/null; r "T4 interrupted by SIGTERM with $(grep -c '^EP ' $O/t4.ckpt) EP records"
nice -n 10 $X $O/t4.spec > $O/t4b.out 2>&1; k=$(sed -n 's/^EDGES RELOADED //p' $O/t4b.out); grep -v '^EDGES RELOADED ' $O/t4b.out > $O/t4b_s.out
cmp -s $O/t4b_s.out $REF && [[ -n $k && $k -gt 0 && $k -lt 128 ]] && r "T4 BYTE-IDENTICAL after restart (EDGES RELOADED $k)" || r "T4 FAIL ('$k')"
awk 'BEGIN{d=0} /^EP / && !d {$3=$3+1; d=1} {print}' $O/t3.ckpt > $O/t5.ckpt; mk $O/t5.spec $O/t5.ckpt; nice -n 10 $X $O/t5.spec > $O/t5.out 2>&1
[[ "$(grep '^COVER' $O/t5.out)" != "$(grep '^COVER' $REF)" ]] && r "T5 MUST-FIRE PASS" || r "T5 MUST-FIRE FAIL"
n=$(grep -n '^EP ' $O/t3.ckpt | sed -n 100p | cut -d: -f1); head -n $((n - 1)) $O/t3.ckpt > $O/t6.ckpt
echo "EF N0>N0/E/1/63 FAILPIECE ORPHAN-RECORD-MUST-NOT-APPEAR" >> $O/t6.ckpt; L=$(sed -n ${n}p $O/t3.ckpt); printf '%s' "${L[1,$(( ${#L} / 2 ))]}" >> $O/t6.ckpt
mk $O/t6.spec $O/t6.ckpt; nice -n 10 $X $O/t6.spec > $O/t6.out 2>&1; grep -v '^EDGES RELOADED ' $O/t6.out > $O/t6_s.out
cmp -s $O/t6_s.out $REF && ! grep -q ORPHAN $O/t6.out && r "T6 BYTE-IDENTICAL" || r "T6 FAIL"
nice -n 10 $X $O/t6.spec > $O/t6b.out 2>&1; k=$(sed -n 's/^EDGES RELOADED //p' $O/t6b.out); grep -v '^EDGES RELOADED ' $O/t6b.out > $O/t6b_s.out
cmp -s $O/t6b_s.out $REF && [[ $k == 128 ]] && ! grep -q ORPHAN $O/t6b.out && r "T6b BYTE-IDENTICAL (all 128 reloaded)" || r "T6b FAIL ('$k')"
r "ALL DONE"
