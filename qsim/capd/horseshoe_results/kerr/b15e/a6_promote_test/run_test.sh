#!/bin/zsh
# A6 addendum 3: one synthetic test of promote_air.sh before the Air launch (no hs_cover, no process touched).
# Synthetic DONE chunk "N9N9"-free: uses chunk name N2N3 inside this test folder only; source = a5_tests/t3.out + t3.ckpt.
H=${0:A:h}; P=${H:h}/promote_air.sh; R=$H/results.txt; : > $R
export PROMOTE_GOOD=$H/good PROMOTE_DEST=$H/kerr_e PROMOTE_VOID=$H/kerr_e_void_outage PROMOTE_LOG=$H/promote.log PROMOTE_RUNLOG=$H/run.log
mkdir -p $H/good $H/kerr_e
r() { echo "$*" >> $R; }
cp ${H:h}/a5_tests/t3.out $H/good/N2N3.out; cp ${H:h}/a5_tests/t3.ckpt $H/good/N2N3.ckpt
S=$(shasum -a 256 $H/good/N2N3.out | cut -c1-64)
# P1: fresh promote, no destination yet
zsh $P N2N3; e=$?; [[ $e == 0 && $(shasum -a 256 $H/kerr_e/N2N3.out | cut -c1-64) == $S ]] && grep -q "PROMOTE N2N3 DONE-chunk" $H/promote.log && r "P1 PASS fresh promote (exit 0, sha equal, record line)" || r "P1 FAIL ($e)"
# P2: idempotent rerun: no-op, no new record
n=$(wc -l < $H/promote.log); zsh $P N2N3 > /dev/null; e=$?; [[ $e == 0 && $(wc -l < $H/promote.log) == $n ]] && r "P2 PASS rerun is a no-op" || r "P2 FAIL ($e)"
# P3: an outage-era destination is renamed and kept, then the copy lands
echo "PREC 128" > $H/kerr_e/N2N3.out; O=$(shasum -a 256 $H/kerr_e/N2N3.out | cut -c1-64)
zsh $P N2N3; e=$?; [[ $e == 0 && $(shasum -a 256 $H/kerr_e/N2N3.out | cut -c1-64) == $S && $(shasum -a 256 $H/kerr_e_void_outage/N2N3.out | cut -c1-64) == $O ]] && r "P3 PASS old output renamed into kerr_e_void_outage and kept" || r "P3 FAIL ($e)"
# P3b: a second old output when the void name is taken gets a timestamp suffix; nothing overwritten
echo "PREC 128 second" > $H/kerr_e/N2N3.out; zsh $P N2N3; e=$?; m=$(ls $H/kerr_e_void_outage | grep -c '^N2N3.out'); [[ $e == 0 && $m == 2 && $(shasum -a 256 $H/kerr_e_void_outage/N2N3.out | cut -c1-64) == $O ]] && r "P3b PASS name taken -> suffixed copy, first one untouched ($m files)" || r "P3b FAIL ($e, $m)"
# P4: 127 records -> refused, destination untouched
mkdir -p $H/g4; cp $H/good/N2N3.out $H/g4/; sed '$d' $H/good/N2N3.ckpt > $H/g4/N2N3.ckpt; mkdir -p $H/d4
PROMOTE_GOOD=$H/g4 PROMOTE_DEST=$H/d4 zsh $P N2N3; e=$?; [[ $e == 1 && ! -e $H/d4/N2N3.out ]] && r "P4 PASS 127-record checkpoint refused" || r "P4 FAIL ($e)"
# P5: no DONE -> refused
mkdir -p $H/g5; grep -v '^DONE$' $H/good/N2N3.out > $H/g5/N2N3.out; cp $H/good/N2N3.ckpt $H/g5/; mkdir -p $H/d5
PROMOTE_GOOD=$H/g5 PROMOTE_DEST=$H/d5 zsh $P N2N3; e=$?; [[ $e == 1 && ! -e $H/d5/N2N3.out ]] && r "P5 PASS no DONE refused" || r "P5 FAIL ($e)"
# P6: an incomplete inner EP line (marker removed from record 50) -> refused
mkdir -p $H/g6; cp $H/good/N2N3.out $H/g6/; awk 'NR==50 {sub(/ #$/, "")} {print}' $H/good/N2N3.ckpt > $H/g6/N2N3.ckpt; mkdir -p $H/d6
PROMOTE_GOOD=$H/g6 PROMOTE_DEST=$H/d6 zsh $P N2N3; e=$?; [[ $e == 1 && ! -e $H/d6/N2N3.out ]] && r "P6 PASS incomplete inner EP line refused" || r "P6 FAIL ($e)"
r "ALL DONE"
