#!/bin/zsh
# detached launcher: containment reference point runs (W0 = 0 at 8 offsets) for the 1e-6 box, then the 1e-7 box,
# 8 at a time. Each writes PROJ lines at the B17 checkpoints (outward-rounded) for b17_containment.py.
cd /Users/sumit/Github/quantum/qsim/capd/horseshoe/tests
O=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/so_mn/contain
C=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/mn_smoke
for W in "6 1/1000000 -1/1000000" "7 1/10000000 -1/10000000"; do
  set -- ${=W}; e=$1; h=$2; m=$3
  for c in "mm $m $m" "mp $m $h" "pm $h $m" "pp $h $h" "zm 0/1 $m" "zp 0/1 $h" "mz $m 0/1" "pz $h 0/1"; do
    set -- ${=c}
    CENTRE_OFFSET="$2 $3" ./b17_check_pt 0/1 $C/b17_cp_1e-$e.txt > $O/ref_1e-${e}_$1.out 2>&1 &
  done
  wait
  echo "batch 1e-$e done $(date)" >> $O/launch_refs.log
done
