# Registered Z-sym main run (E_REP_PREREG.md, REDO OFF): outcome

Recorded 2026-11-19 by Claude Opus 5.5 (session "Quantum").

## What happened
- The run THREW at step 1478, t 289.123816: `S4: x - 1 < 0.05 possible`. Its last line is `MN-SO FAIL (time checkpoints only;
  informational) W0 1/10000000 steps 1478 resteps 0 wall 57565 s`.
- The process ended at about 08:45 on 2026-11-19. The run's guard logged "run PID 37679 gone" at 08:45:29.
- This was BEFORE the memory squeeze of 09:19–09:57; the guard never fired. The outcome is the run's own.
- Checkpoints reached: only 283.8852, which PASSED with u2 ratio 1.00. The 290.8497 and 291.8852 checkpoints were never reached.

## The mechanical reading (read_result.sh, committed before the result, 96a65dd), verbatim in READING.txt
- C-floor containment PASS: 24 point projections, 0 not contained.
- HARNESS-ERROR 0, BUG 0, THREW 1.
- Script verdict: **INVALID**, "(a control failed, or the 291.8852 checkpoint was not reached)". Here it is the second
  branch: no control failed.

**A discrepancy, for the Bridge to rule on.**
- The script maps "291.8852 not reached" to INVALID.
- E_REP_PREREG.md §6 defines INVALID as "any control fails". Here every control holds: C-floor, C-identity and C-steps
  (no BUG).
- The primary is not met (no 291.8852 line) and the secondary fails (a THREW before 291.8852). Read by the §6 table,
  that is **FAIL**.
- The script was registered as the mechanical reading, and the prereg text as the criteria. They disagree on this case,
  and the reading is left to the Bridge. Nothing is relabelled here.

## The likely cause, stated plainly (A2)
- The run had SO_FIXED_REDO OFF. §3's setup-correspondence line wrongly said the wrap-test runs did too; they ran with it ON.
- The REDO-off box run (so_mn/run_1e-7.out) THREW the same way at step 1465, t 289.0486.
- This run tracked it: maxE 8.86e-6 against 1.29e-5 at step 1400, and 1.21e-2 against 2.57e-2 at step 1460. It threw 13
  steps later.
- So the outcome mainly re-measures the known REDO-off swing failure, not the E representation.
- The corrected run is main_redo, E_REP_PREREG.md Amendment A2 (REGISTERED 858234f; pre-run tests PASS 00fb184).
