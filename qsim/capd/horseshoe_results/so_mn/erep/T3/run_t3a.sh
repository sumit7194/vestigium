#!/bin/zsh
# T3a (E_REP_PREREG.md Amendment A1): MN W0 = 1e-7 from t = 0 under box and zsym, in parallel, nice 10, every step
# logged (LOG_EVERY=1), stopped after the first step ending at or past t = 0.04 (~40 steps; STOP_AFTER_T does not change
# the step sizes). Timing only: the fallback decision reads the "wall" columns, nothing else.
T=/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests; O=${0:A:h}; CP=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/mn_smoke
cd $T; rm -f $O/st_box $O/st_zsym
(LOG_EVERY=1 STOP_AFTER_T=0.04 SO_EREP=box  nice -n 10 ./mn_so_erep 1/10000000 $CP/b17_cp_1e-7.txt $O/st_box  1e300 > $O/T3a_box.out  2>&1) &
(LOG_EVERY=1 STOP_AFTER_T=0.04 SO_EREP=zsym nice -n 10 ./mn_so_erep 1/10000000 $CP/b17_cp_1e-7.txt $O/st_zsym 1e300 > $O/T3a_zsym.out 2>&1) &
wait; echo "T3a DONE $(date)"
