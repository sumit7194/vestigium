#!/bin/zsh
# Mechanical reading of the registered main_redo run (E_REP_PREREG.md sections 5-6 and Amendment A2). Usage: read_result.sh [run.out]
O=${0:A:h}; R=${1:-$O/run.out}; T=/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests; C=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/so_mn/contain
PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
echo "== run: $R"; grep -E "^CHECKPOINT t" $R
p=$(grep -E "^CHECKPOINT t t= *291\.8852" $R | tail -1); s=$(grep -E "^CHECKPOINT t t= *290\.8497" $R | tail -1)
threw=$(grep -c "^THREW" $R); bug=$(grep -c "BUG" $R)
cont=$($PY $T/b17_containment.py $R $C/ref_1e-7_{mm,mp,pm,pp,zm,zp,mz,pz}.out | tail -2)
echo "$cont"
harn=$(grep -c "HARNESS-ERROR" $R)
valid=1; [[ $cont == *"CONTAINMENT PASS"* ]] || valid=0; [[ $harn == 0 ]] || valid=0; [[ $bug == 0 ]] || valid=0
echo "controls: C-floor containment $([[ $cont == *"CONTAINMENT PASS"* ]] && echo PASS || echo FAIL), HARNESS-ERROR lines $harn, BUG lines $bug, THREW lines $threw"
# Fixed forward (the Bridge's ruling, 2026-11-19, on the main run): the prereg's section 6 governs. INVALID only when a
# control fails; when the controls hold but the 291.8852 checkpoint was not reached, the verdict is FAIL.
if [[ $valid == 0 ]]; then echo "VERDICT: INVALID (a control failed)"; exit 0; fi
if [[ -z $p ]]; then echo "primary   291.8852: NOT REACHED"; echo "secondary 290.8497: ${s:-NOT REACHED}"; echo "VERDICT: FAIL (controls hold; the primary checkpoint 291.8852 was not reached; THREW lines $threw)"; exit 0; fi
echo "primary   291.8852: $p"; echo "secondary 290.8497: $s"
if [[ $p == *" PASS" && $threw == 0 ]]; then echo "VERDICT: PASS"; else echo "VERDICT: FAIL"; fi
