#!/bin/zsh
# A13 rerun: v4 (NaN rule) certifying passes from the committed refined specs, with Tier-1 dumps
S=/Users/sumit/Github/quantum/qsim/mn_homoclinic_spike; lab=$1; bin=$2; mkdir -p $S/s2v4/$lab
for st in fp cone bvp; do echo "== $lab $st $(date '+%T')"; $S/capd/$bin $st $S/s2/$lab/$st.spec $S/s2v4/$lab/$st.dump > $S/s2v4/$lab/$st.out 2>&1; echo "   rc $? $(grep -E '^RESULT' $S/s2v4/$lab/$st.out)"; done
echo "DONE $lab $(date '+%T')"
