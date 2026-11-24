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
