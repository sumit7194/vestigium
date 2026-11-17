#!/bin/zsh
# macOS 27.2 regression (spot checks, as for 27.0.1). GO: Sumit via the Bridge, 2026-11-17. Serial, 1 core, nice 19.
# Stops at the FIRST difference (writes DIFFERS to RESULT.txt and exits). Old binaries are never overwritten for CAPD
# (new builds go to the scratch BIN dir); the Kerr maps are rebuilt in place by kerr_build.sh (old dylibs copied first).
setopt pipefail
Q=/Users/sumit/Github/quantum; HS=$Q/qsim/capd/horseshoe; T=$HS/tests; R=$Q/qsim/capd/horseshoe_results; D=$R/regress_27.2
S=/private/tmp/claude-501/-Users-sumit-Github-quantum/e2f2824e-d2dc-4808-a859-11a2486eda3f/scratchpad/regress272; BIN=$S/bin
PY=$Q/sims/.venv/bin/python; OUT=$D/RESULT.txt
mkdir -p $S $BIN; rm -f $S/*.state $S/kr_* 2>/dev/null
say() { echo "$(date +%H:%M:%S) $*" | tee -a $OUT; }
diffstop() { say "DIFFERS: $* -- stopping here (the Bridge's rule)"; exit 1; }
say "== START macOS $(sw_vers -productVersion) ($(sw_vers -buildVersion)), $(clang --version | head -1), CLT $(pkgutil --pkg-info=com.apple.pkg.CLTools_Executables | sed -n 's/^version: //p'), HEAD $(git -C $Q rev-parse --short HEAD)"

capd_checks() {   # $1 = label, $2 = mn_so binary (plain), $3 = fix binary, $4 = toys_so, $5 = toy_sec, $6 = mn_lift_so
  local L=$1
  # (1) kr_ref: W0 1e-6, t 0 to 0.9 from scratch; the final MPFR state must equal so_mn/kr_ref byte for byte
  (cd $T && $2 1/1000000 $R/mn_smoke/b17_cp_1e-6.txt $S/kr_$L 0.9 > $S/kr_$L.out 2>&1) || diffstop "$L kr_ref run failed"
  cmp -s $S/kr_$L $R/so_mn/kr_ref && say "$L kr_ref final state: IDENTICAL" || diffstop "$L kr_ref final state"
  # (2) SO continuation: the fix test's start state (DIAG grid save t 287.7559), same env, steps 1305..1321; every DIAG line
  #     and the step-1320 line (wall time stripped) must equal the 2026-10-26 record
  cp $R/so_mn/rerun_diag/run2_1e-7.state.t287.7559 $S/fix_$L.state
  (cd $T && SO_FIXED_REDO=1 SO_DIAG_FROM=285 GUARD_RATIO=0.02 $3 1/10000000 $R/mn_smoke/b17_cp_1e-7.txt $S/fix_$L.state 287.93 > $S/fix_$L.out 2>&1) || diffstop "$L continuation run failed"
  pick() { grep -E "^(DIAG step|# step) 13(0[5-9]|1[0-9]|2[01]) " $1 | sed -E 's/ wall [0-9]+ s$//'; }
  pick $S/fix_$L.out > $S/fix_$L.lines; pick $R/so_mn/fix_test/fix_1e-7.out | head -n $(wc -l < $S/fix_$L.lines) > $S/fix_rec.lines
  [ -s $S/fix_$L.lines ] && cmp -s $S/fix_$L.lines $S/fix_rec.lines && say "$L SO continuation steps 1305-1321 ($(wc -l < $S/fix_$L.lines) lines): IDENTICAL" || diffstop "$L SO continuation lines"
  # (3) toys A-E (T 1, w 0.1), the section toy (w 0.1, 0.01, 0.001) and the MN lift (h 1/1000, 1/1000000) against so_gates
  for X in A B C D E; do (cd $T && $4 $X 0.1 1 > $S/toy_${X}_$L.out 2>&1); r=$($PY $D/numcmp.py $S/toy_${X}_$L.out $R/so_gates/toy_$X.out)
    say "$L toy $X vs saved: $r"; [[ $r == DIFFERS* ]] && diffstop "$L toy $X"; done
  for w in 0.1 0.01 0.001; do (cd $T && $5 $w > $S/tsec_${w}_$L.out 2>&1); r=$($PY $D/numcmp.py $S/tsec_${w}_$L.out $R/so_gates/toy_sec_hw2_w$w.out)
    say "$L section toy w $w vs saved: $r"; [[ $r == IDENTICAL ]] || diffstop "$L section toy $w (was bit-identical on 27.0.1)"; done
  for h in 1000 1000000; do (cd $T && $6 1/$h > $S/lift_${h}_$L.out 2>&1); r=$($PY $D/numcmp.py $S/lift_${h}_$L.out $R/so_gates/lift_1_$h.out)
    say "$L MN lift h 1/$h vs saved: $r"; [[ $r == DIFFERS* ]] && diffstop "$L lift $h"; done
}
kerr_checks() {   # $1 = label
  (cd $HS && $PY b15b_orbits.py > $S/orbits_$1.log 2>&1 && $PY b15b_g0.py > $S/g0_$1.log 2>&1) || diffstop "$1 orbits/G0 run failed"
  git -C $Q diff --quiet -- qsim/capd/horseshoe_results/kerr/b15b_gates/orbits.json qsim/capd/horseshoe_results/kerr/b15b_gates/G0.json \
    && say "$1 Kerr orbits.json + G0.json regenerated: IDENTICAL" || diffstop "$1 orbits.json/G0.json"
  $PY $D/dump_compiled.py $S/compiled_$1.json > $S/dump_$1.log 2>&1 || diffstop "$1 compiled dump failed"
}

say "-- A: old binaries (27.0.1 builds) on 27.2"
capd_checks old $T/mn_so $T/mn_so_fix2 $T/toys_so $T/toy_sec $T/mn_lift_so
kerr_checks old
(cd $HS && $PY $D/mnflow_recheck.py > $S/mnflow.out 2>&1); cat $S/mnflow.out >> $OUT
grep -q "^MNFLOW IDENTICAL" $S/mnflow.out && say "MNFlow 6 reference tasks: IDENTICAL" || diffstop "MNFlow reference tasks"

say "-- B: rebuilt with the 27.2 toolchain"
cd $T
for p in mn_so toys_so toy_sec mn_lift_so; do nice -n 19 ./../../tests/guard_build.sh $p.cpp $BIN/$p 2>&1 | tail -1 | tee -a $OUT | grep -q "^BUILT" || diffstop "guarded build of $p failed"; done
capd_checks new $BIN/mn_so $BIN/mn_so $BIN/toys_so $BIN/toy_sec $BIN/mn_lift_so
for X in A B C D E; do cmp -s $S/toy_${X}_old.out $S/toy_${X}_new.out || diffstop "toy $X old vs new build"; done
for h in 1000 1000000; do cmp -s $S/lift_${h}_old.out $S/lift_${h}_new.out || diffstop "lift $h old vs new build"; done
say "toys and lift: old binaries vs new builds IDENTICAL"
cp $HS/kerr_p.dylib $S/kerr_p.dylib.old; cp $HS/kerr_rs/target/release/libkerr_rs.dylib $S/libkerr_rs.dylib.old
(cd $HS && CARGO_NET_OFFLINE=true nice -n 19 ./kerr_build.sh > $S/kerr_build.log 2>&1) || diffstop "kerr_build.sh failed (see $S/kerr_build.log)"
say "Kerr maps rebuilt (kerr_build.sh; provenance updated); dylib sha256 rust $(shasum -a 256 $HS/kerr_rs/target/release/libkerr_rs.dylib | cut -c1-16), c++ $(shasum -a 256 $HS/kerr_p.dylib | cut -c1-16)"
kerr_checks new
cmp -s $S/compiled_old.json $S/compiled_new.json && say "Kerr compiled maps, all 248 B15b tasks x 2 maps: old vs new builds IDENTICAL (bit for bit)" || diffstop "compiled maps old vs new build"

say "-- C: Lean (ZiglinCert, pinned toolchain): lake build"
(cd $Q/lean/ZiglinCert && nice -n 19 lake build > $S/lake.log 2>&1) && say "lake build: OK ($(tail -1 $S/lake.log))" || diffstop "lake build failed (see $S/lake.log)"
say "== ALL CHECKS IDENTICAL / AGREE"
