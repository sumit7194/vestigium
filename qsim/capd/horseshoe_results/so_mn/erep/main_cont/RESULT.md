# A3 (main_cont) RESULT: FAIL (controls hold), as registered

Registered in `qsim/capd/horseshoe/E_REP_PREREG.md`, Amendment A3. Read mechanically on 2026-11-24 20:27 by `read_result.sh`
(run with zsh). The output is in `read_result_2026-11-24_after_R3.txt`. The Bridge graded it on 2026-11-24.

**Verdict: FAIL (controls hold).** PASS needed all five time checkpoints, and one failed.

| Checkpoint | t | u1 | u2 | fake / ref | Line |
|---|---|---|---|---|---|
| R1  | 295.8852 | 1.00 | 1.06 | 3.9e-7 / 7.9e-6 | PASS |
| R3a | 793.2346 | 1.01 | **8.77** | 8.4e-7 / 7.2e-6 | **FAIL** (u2 > K = 5) |
| R3b | 800.0941 | 1.01 | 2.83 | 1.0e-7 / 4.5e-6 | PASS |
| R3c | 801.2346 | 1.01 | 2.76 | 3.2e-7 / 6.6e-6 | PASS |
| R3d | 805.2346 | 1.01 | 2.26 | 2.1e-6 / 3.0e-6 | PASS |

**Controls, all held:**
- the RESUMED line is OK ("next checkpoint 3");
- C-floor containment PASS: 120 point-projections, 0 not contained, no reference checkpoint missing;
- HARNESS-ERROR 0, BUG 0, THREW 0.

**Descriptive only.** The single failure is an isolated u2 spike at R3a, not monotone growth. The three later checkpoints,
within 12 t-units, are back within K. No interpretation is made beyond this.

**Not measured by A3:**
- sec_down (581.77) is DEFERRED: only the set is saved.
- R4 sec_return (1018.70) will only save `st.pre_sec_return` with its sha.

The run (PID 40882) continues to R4 on Sumit's word ("let it continue", relayed by the Bridge on 2026-11-24). That does
not change this verdict.

- Run facts at grading: step 5760, t 805.34, wall 269748 s.
- The 3400-step / 62 h estimate was exceeded. That is a budget note, not a criterion.

Written by Claude Opus 5.5 (Quantum).

## FACTUAL CORRECTION (2026-11-24, labelled; the Bridge approved the wording)

The "descriptive only" line above ("an isolated u2 spike at R3a, not monotone growth") is wrong as a description of the
enclosure. The verdict does not change: it stays FAIL (controls hold).

- **The enclosure's u2 width grew smoothly** across the four late checkpoints: W2 = 1.663e-6 (793.23), 2.358e-6 (800.09),
  2.420e-6 (801.23), 2.717e-6 (805.23).
- **The ratio spiked because the TRUE u2 width dipped**: tu2 = 1.895e-7 at 793.23, against 8.33e-7, 8.76e-7 and 1.20e-6 at
  the three later checkpoints (`mn_smoke/b17_cp_1e-7.txt`). 793.23 is 7 time-units before the second periapsis. The first
  passage's pre-periapsis widths were of the same size: 2.83e-7 at 283.89 and 1.96e-7 at 291.89.
- So what is "isolated" is the ratio u2 = W2/tu2, not the enclosure. Cause checks are planned separately (the Bridge's
  GO, 2026-11-24); none of them changes this verdict.

## Run end (2026-11-26 11:29; recorded)
- **R4 reached.** sec_return t = 1018.6988 is DEFERRED as registered. The set before the return is saved at
  t = 1018.198783: `st.pre_sec_return`, sha256 4ec8d41e…, recorded in section_sets.sha256 and format-verified.
- **Run history.** Steps 7190 in all. The run resumed once from a verified state after the 2026-11-26 06:52 power loss
  (t 965.818); see OUTAGE_2026-11-26_quantum.md.
- **The final "MN-SO PASS (… informational)" line is NOT a reading.** mn_so's informational pass flag covers only the
  checkpoints seen by its own process, and the resumed process saw none. A3's registered verdict is unchanged:
  **FAIL (controls hold)**, as read by read_result.sh above.
