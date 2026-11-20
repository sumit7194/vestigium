# B15b gates G1, G3, G4 and G4c: result (b15b_gates_eval.py, 2026-11-20)

Run by Claude Opus 5.5 (session "Quantum") on the Bridge's go. The full output is G1_G3_G4.json; the console output is gates_eval_20261120.log.

## Verdicts
- **G1: PASS.** Worst 2.161e-11, against the bar 1e-10; 0 return mismatches.
- **G3: PASS.** Worst |det DP - 1| is 2.655e-11 over 663 points, against the bar 1e-8.
- **G4: PASS.** Worst 2.030e-11, against 1e-10; 0 mismatches.
- **G4c: ACCEPTED, so the reference converged.** At the 3 longest-T points, MNFlow's 1e-13 values lie within 9.05e-13,
  7.54e-13 and 2.47e-13 relative of its 1e-12 values, against the bar 1e-11. So no point is REFERENCE-UNCONVERGED, and G4
  is not held open.
  - The script prints no separate G4c word. It turns an unaccepted reference into "G4 OPEN"; an accepted one lets G4 be
    judged.

## Provenance of the eval script
- It was committed in a84e06f (2026-10-24 13:20), "committed before its first run".
- One later change, 3f8668f (2026-10-24 16:09): the reference glob widened from `mnflow_w*.jsonl` to `mnflow_*.jsonl`, so that
  the fast/grind scheduling files are read. Criteria, bars and None-route rules are untouched.
- That change came after the original-mode workers had started (rows may have existed), but before any gate was evaluated:
  this is the first run of the script; G1_G3_G4.json did not exist.
- It has not changed since.

## The reference rows
- All 248 tasks have a row.
- **30 ids appear twice**, in mnflow_fast0.jsonl and in mnflow_w2.jsonl (October), with values identical 30/30. No claim
  file is involved.
- The eval keeps the LAST row it reads for an id. glob order in this run listed w2 after fast0, so w2's copy was used. The
  values are identical, so the choice does not matter.
- **Status -1 annotation, carried in:** many reference rows have solve_ivp status -1. Every row written after the t_eval=[]
  fix (grind0 rows 21 onward and all claim rows) logs the final t as the max event-evaluation t. That is the **validated
  path** (d81ecb9, accepted by the Bridge); see mnflow_grind0_ANNOTATIONS.md.
  - The gate values come from y_events and do not use the logged t.
