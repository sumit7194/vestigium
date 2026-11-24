#!/bin/zsh
# Branch-S C-floor reference runs (PRELAUNCH.md), SERIAL on one core: refs_plan.txt lines "piece q du dp".
# Each is a W0 = 0 point run, b17_check_pt, against the PIECE's checkpoint file. A run whose output already ends with a
# "B17 " summary line is skipped, so this resumes safely. Logs to refs.log. Started by launch_retry.sh.
O=${0:A:h}; T=/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests
mkdir -p $O/refs; cd $T
while read p q du dp; do
  out=$O/refs/ref_${p}_${q}.out
  if [[ -f $out ]] && grep -q "^B17 " $out; then echo "$(date '+%F %T') skip $p/$q (complete)" >> $O/refs.log; continue; fi
  echo "$(date '+%F %T') start $p/$q offset $du $dp" >> $O/refs.log
  CENTRE_OFFSET="$du $dp" nice -n 10 ./b17_check_pt 0/1 $O/cp/b17_cp_5e-8_$p.txt > $out 2>&1
  echo "$(date '+%F %T') end $p/$q exit $? : $(tail -1 $out | cut -c1-120)" >> $O/refs.log
done < $O/refs_plan.txt
echo "$(date '+%F %T') ALL REFS DONE" >> $O/refs.log
