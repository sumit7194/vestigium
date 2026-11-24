#!/bin/zsh
# Mechanical reading of the branch-S retry (RETRY_S_REGISTRATION.md + its pre-launch amendment PRELAUNCH.md).
# Per piece (mm mp pm pp): controls = C-floor containment against that piece's 8 reference runs, HARNESS-ERROR 0, BUG 0,
# THREW 0, the "# centre offset" line equal to the registered offset; criteria = every time checkpoint of the piece's file
# with t <= 805.3 (8 of them) reads PASS. Overall: PASS if all 4 pieces pass; INVALID if any control fails; FAIL otherwise.
O=${0:A:h}; T=/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
typeset -A OFF; OFF=(mm "-1/20000000 -1/20000000" mp "-1/20000000 1/20000000" pm "1/20000000 -1/20000000" pp "1/20000000 1/20000000")
TIMES=(283.8852 290.8497 291.8852 295.8852 793.2346 800.0941 801.2346 805.2346)
invalid=0; allpass=1
for p in mm mp pm pp; do
  R=$O/$p/run.out; echo "== piece $p: $R"
  [[ -f $R ]] || { echo "piece $p: NO RUN"; invalid=1; continue; }
  offl=$(grep -m1 "^# centre offset" $R); [[ $offl == "# centre offset ${OFF[$p]}" ]] && offok=OK || { offok=BAD; invalid=1; }
  harn=$(grep -c "HARNESS-ERROR" $R); bug=$(grep -c "BUG" $R); threw=$(grep -c "^THREW" $R)
  cont=$($PY $T/b17_containment.py $R $O/refs/ref_${p}_{mm,mp,pm,pp,zm,zp,mz,pz}.out | tail -2); echo "$cont"
  [[ $cont == *"CONTAINMENT PASS"* ]] || invalid=1; [[ $harn == 0 && $bug == 0 ]] || invalid=1
  echo "controls: offset $offok, containment $([[ $cont == *"CONTAINMENT PASS"* ]] && echo PASS || echo FAIL), HARNESS-ERROR $harn, BUG $bug, THREW $threw"
  pp_=1
  for t in $TIMES; do l=$(grep -E "^CHECKPOINT t t= *$t" $R | tail -1)
    if [[ -z $l ]]; then echo "checkpoint $t: NOT REACHED"; pp_=0; else echo "checkpoint $t: $l"; [[ $l == *" PASS" ]] || pp_=0; fi; done
  [[ $threw == 0 ]] || pp_=0
  echo "piece $p: $([[ $pp_ == 1 ]] && echo PASS || echo FAIL)"; [[ $pp_ == 1 ]] || allpass=0
done
if [[ $invalid == 1 ]]; then echo "VERDICT: INVALID (a control failed)"; elif [[ $allpass == 1 ]]; then echo "VERDICT: PASS (all 4 pieces)"; else echo "VERDICT: FAIL (controls hold; see the per-piece lines)"; fi
