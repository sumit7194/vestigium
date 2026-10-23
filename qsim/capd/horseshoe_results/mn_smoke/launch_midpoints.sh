#!/bin/zsh
# detached launcher: start the 4 edge-midpoint containment reference runs once 2 corner runs have finished
cd /Users/sumit/Github/quantum/qsim/capd/horseshoe/tests
O=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/mn_smoke; h=1/1000000000000; m=-1/1000000000000
until [ $(grep -l "^B17 " $O/b17_contain_mm.out $O/b17_contain_mp.out $O/b17_contain_pm.out $O/b17_contain_pp.out 2>/dev/null | wc -l) -ge 2 ]; do sleep 60; done
for c in "zm 0/1 $m" "zp 0/1 $h" "mz $m 0/1" "pz $h 0/1"; do set -- ${=c}; CENTRE_OFFSET="$2 $3" nohup ./b17_check_pt 0/1 $O/b17_cp_1e-12.txt > $O/b17_contain_$1.out 2>&1 & done
echo "midpoints launched $(date)" >> $O/launch_midpoints.log
