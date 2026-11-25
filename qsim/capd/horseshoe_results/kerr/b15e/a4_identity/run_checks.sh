#!/bin/zsh
# B15e A4 identity checks (registered in 77a2bd3). (ii) the must-fire first, then (i), serially on one core.
O=${0:A:h}; H=/Users/sumit/Github/quantum/qsim/capd/horseshoe; B=$H/../horseshoe_results/kerr/b15d; cd $H
t0=$(date +%s); HS_WATCHDOG_S=60 nice -n 10 ./hs_cover_b15e $B/kerr_e/N1N2.spec > $O/mustfire.out 2>&1; rc=$?; dt=$(( $(date +%s) - t0 ))
echo "MUSTFIRE exit $rc after $dt s; watchdog line: $(grep -c 'WATCHDOG TIMEOUT' $O/mustfire.out)" > $O/results.txt
for r in r1_MM r1_MN r1_NM r1_NN hh2_N0N0; do
  t0=$(date +%s); nice -n 10 ./hs_cover_b15e $B/gb/$r.spec > $O/$r.out 2>&1; rc=$?
  if cmp -s $O/$r.out $B/gb/$r.out; then v=BYTE-IDENTICAL; else v=DIFFERS; fi
  echo "IDENTITY $r exit $rc $(( $(date +%s) - t0 )) s: $v" >> $O/results.txt
done
echo "ALL DONE" >> $O/results.txt
