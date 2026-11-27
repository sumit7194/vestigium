#!/bin/zsh
S=/Users/sumit/Github/quantum/qsim/mn_homoclinic_spike; mkdir -p $S/s2v4/meet_ii
echo "== meet $(date '+%T')"; $S/capd/s2_main_v4 meet $S/s2/meet_ii/meet.spec $S/s2v4/meet_ii/meet.dump > $S/s2v4/meet_ii/meet.out 2>&1; echo "   rc $? $(grep -E '^RESULT' $S/s2v4/meet_ii/meet.out)"; echo "DONE meet $(date '+%T')"
