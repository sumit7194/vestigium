#!/bin/zsh
# A2 pre-run tests (E_REP_PREREG.md Amendment A2, REGISTERED 858234f), binary tests/mn_so_erep (sha256 recorded below).
# T1r: SO_EREP=box SO_FIXED_REDO=1 replays wrap-test segment C01 (start fix_1e-7.state.t287.7668, the wrap_run.py env
#      minus WRAP_DUMP, which is log-only: K00/K01) and must save st.t288.0099 byte-identical to fix_test's.
# T4r: SO_EREP=zsym SO_FIXED_REDO=1 from t = 0, T_end 291.9 (as main_redo): U = uninterrupted to STOP_AFTER_T 0.04;
#      P1 stop after 0.02; P2 resumes P1's state and stops after 0.04. P2's final state must equal U's byte for byte.
T=/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests; O=${0:A:h}; CP=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/mn_smoke
FT=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/so_mn/fix_test
cd $T; shasum -a 256 mn_so_erep > $O/binary.sha256; rm -f $O/T1r/* $O/T4r/*; mkdir -p $O/T1r $O/T4r; cp $FT/fix_1e-7.state.t287.7668 $O/T1r/st
(SO_EREP=box SO_FIXED_REDO=1 SO_DIAG_FROM=285 GUARD_RATIO=0.02 SAVE_FROM=287.5 SAVE_DT=0.25 CKPT_SEC=1e9 STOP_AFTER_T=288.0 \
  nice -n 10 ./mn_so_erep 1/10000000 $CP/b17_cp_1e-7.txt $O/T1r/st 291.9 > $O/T1r/out 2>&1) &
(SO_EREP=zsym SO_FIXED_REDO=1 STOP_AFTER_T=0.04 nice -n 10 ./mn_so_erep 1/10000000 $CP/b17_cp_1e-7.txt $O/T4r/st_U 291.9 > $O/T4r/U.out 2>&1) &
(SO_EREP=zsym SO_FIXED_REDO=1 STOP_AFTER_T=0.02 nice -n 10 ./mn_so_erep 1/10000000 $CP/b17_cp_1e-7.txt $O/T4r/st 291.9 > $O/T4r/P1.out 2>&1 && \
 SO_EREP=zsym SO_FIXED_REDO=1 STOP_AFTER_T=0.04 nice -n 10 ./mn_so_erep 1/10000000 $CP/b17_cp_1e-7.txt $O/T4r/st 291.9 > $O/T4r/P2.out 2>&1) &
wait
{ echo "A2 pre-run tests, $(date '+%F %T'), binary $(cat $O/binary.sha256 | cut -c1-16)"
  if cmp -s $O/T1r/st.t288.0099 $FT/fix_1e-7.state.t288.0099; then echo "T1r: st.t288.0099 BYTE-IDENTICAL to fix_test -> PASS"; else echo "T1r: st.t288.0099 DIFFERS or missing -> FAIL"; fi
  grep -h -E "STOP_AFTER_T|THREW|BUG|SO_FIXED" $O/T1r/out | head -3
  if cmp -s $O/T4r/st $O/T4r/st_U; then echo "T4r: resumed final state BYTE-IDENTICAL to the uninterrupted run -> PASS"; else echo "T4r: DIFFERS -> FAIL"; fi
  grep -h "STOP_AFTER_T\|RESUMED" $O/T4r/*.out | head -4; } > $O/RESULT.txt
echo DONE >> $O/RESULT.txt
