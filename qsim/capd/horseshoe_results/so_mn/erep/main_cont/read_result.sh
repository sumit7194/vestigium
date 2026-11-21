#!/bin/zsh
# Mechanical reading of the registered main_cont run (E_REP_PREREG.md Amendment A3; criteria = §5/§6 at the 5 time checkpoints).
# Usage: read_result.sh [run.out]. Per-checkpoint lines are always printed, so a partial outcome stays visible.
O=${0:A:h}; R=${1:-$O/run.out}; T=/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests; C=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/so_mn/contain
PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
echo "== run: $R"; grep -E "^# RESUMED" $R | head -1
res=$(grep -E "^# RESUMED" $R | head -1); harn=$(grep -c "HARNESS-ERROR" $R); bug=$(grep -c "BUG" $R); threw=$(grep -c "^THREW" $R)
cont=$($PY $T/b17_containment.py $R $C/ref_1e-7_{mm,mp,pm,pp,zm,zp,mz,pz}.out | tail -2); echo "$cont"
valid=1; [[ $res == *"next checkpoint 3"* ]] || valid=0; [[ $cont == *"CONTAINMENT PASS"* ]] || valid=0; [[ $harn == 0 ]] || valid=0; [[ $bug == 0 ]] || valid=0
echo "controls: RESUMED line $([[ $res == *"next checkpoint 3"* ]] && echo OK || echo BAD), C-floor containment $([[ $cont == *"CONTAINMENT PASS"* ]] && echo PASS || echo FAIL), HARNESS-ERROR $harn, BUG $bug, THREW $threw"
grep -E "^CHECKPOINT sec_" $R | sed 's/^/deferred (not measured by A3): /'
allpass=1
for t in 295.8852 793.2346 800.0941 801.2346 805.2346; do
  l=$(grep -E "^CHECKPOINT t t= *$t" $R | tail -1)
  if [[ -z $l ]]; then echo "checkpoint $t: NOT REACHED"; allpass=0; else echo "checkpoint $t: $l"; [[ $l == *" PASS" ]] || allpass=0; fi
done
if [[ $valid == 0 ]]; then echo "VERDICT: INVALID (a control failed)"; exit 0; fi
if [[ $allpass == 1 && $threw == 0 ]]; then echo "VERDICT: PASS"; else echo "VERDICT: FAIL (controls hold; see the per-checkpoint lines; THREW $threw)"; fi
