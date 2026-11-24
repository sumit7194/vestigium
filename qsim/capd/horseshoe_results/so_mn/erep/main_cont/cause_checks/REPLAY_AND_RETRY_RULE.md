# A3 R3a: logged injection replay and the BRANCHED retry rule

Registered before the replay or any must-fire runs, and before any injection split is seen. The Bridge's GO (2026-11-24)
covers the replay. The retry itself comes back to the Bridge, and its scale needs Sumit's go. Diagnostic only: A3's
verdict is unchanged. Written by Claude Opus 5.5 (Quantum).

## Binary
- `tests/mn_so_inj`, built from `tests/mn_so_inj.cpp` by `qsim/capd/tests/guard_build.sh` (proof_guard passed).
- It is mn_so.cpp plus log-only hooks (see its header):
  - **INJ_LOG.** Keeps the per-step injected parts p0, p1, p2 and dDe (so_set.h's SO_WRAP copies, which the run's own
    s = p0 + p1 + p2 + dDe is built from) as four tagged generator lists, propagated by the same D1c as X.G.
  - **INJ lines.** At each time checkpoint they print the u1/u2 projection widths 2 Σ|u·g| of:
    - the inherited columns X.G[0, N0);
    - the new columns X.G[N0, end);
    - each tagged list.
  - Must-fire knobs INJ_ESCALE and INJ_P2SCALE are used only in the must-fire runs.

## Replay (counted as the diagnostic)
- **Inputs.** A byte copy of `main_cont/st.t792.0198` (cp, then cmp) to `cause_checks/replay/st`.
- **Environment.** `SO_EREP=zsym SO_FIXED_REDO=1 INJ_LOG=1`, as in A3 (no SAVE_FROM).
- **Command.** `nice -n 10 ./mn_so_inj 1/10000000 mn_smoke/b17_cp_1e-7.txt replay/st 793.3`, detached, 1 core.
- **Cost.** About 50 steps at ~90 s, so ~75 min, a little more than the 45 min first quoted. RSS is about 0.25 GB (A3:
  213 MB); 0.5 GB is declared.
- **I1 identity (must hold, else VOID).** The replay's three `PROJ t t=793.2346306025` lines and its `CHECKPOINT t`
  line are byte-identical to main_cont/run.out lines 335–338.
- **I2 consistency (must hold, else VOID).** Every INJ line ends `new<=sum OK`.
- **Reading.** Read from the u2 INJ line at 793.2346. Shares are the tagged widths over their sum. The window covers
  792.02 → 793.23, about 1.2 t-units.
- **Stated limit.** This window samples the injection mix during the last 1.2 t-units. It does not measure what built the
  E inherited at 792.02. The INJ line reports `inherited` against `new` along u2, so the window's weight is visible.

## Must-fires (from the same state; separate copies; STOP_AFTER_T = 792.14, about 5 steps)
- **M0 (baseline, no knob).** It gives the 5-step shares; it is not a test.
- **M1: `INJ_ESCALE=1000`** (e inflated, so dDe ∝ e must dominate). The u2 `end` INJ line must show a dDe share ≥ 0.9.
- **M2: `INJ_P2SCALE=1000`** (the p2 remainder inflated). The u2 `end` INJ line must show a p2 share ≥ 0.9.
- A must-fire counts only if M0's share of the same part is < 0.9. Otherwise it is reported as uninformative.
- If M1 or M2 is informative and misses ≥ 0.9, the split measurement is BROKEN and the replay's split is not read.
- If a must-fire run THROWs (e.g. an S4/S9 check under the inflated set), that must-fire is VOID and reported. The replay
  can still be read only if the other must-fire passed.

## Branched retry rule (fixed now; applied to the replay's u2 shares)
The four parts scale differently with the piece size W0:
- p0, the centre's Taylor remainder, does not depend on W0;
- p1, the remainder of the linear part, scales like W0, the same as the true width;
- p2 (the second-derivative spread over the box) and dDe ((D1K − D1c)·e, which grows with the hull and with E) grow
  faster than the true width as W0 grows.

So subdividing from t = 0 helps the ratio only if p2 and dDe dominate. The Bridge's example ("dDe" / "P2") is grouped
accordingly:

| Branch | Condition (u2 shares in the replay window) | Retry, drafted after the reading; its scale goes to the Bridge and Sumit |
|---|---|---|
| **S** (subdivide) | p2 + dDe ≥ 0.6 | 4 pieces from t = 0 at W0 = 5e-8 (2 × 2 split of the W0 = 1e-7 box), zsym + REDO, everything else as A3. Same B17 criteria at the same checkpoints. PASS needs all 4 pieces. ~4 × 3 days ≈ 300 core-h. |
| **T** (tighter step) | p0 + p1 ≥ 0.6 | Same W0 = 1e-7, from t = 0, with a smaller step cap or a higher Taylor order (the choice is made by a short timing test, registered separately). Subdivision would not help. |
| **N** (neither) | both < 0.6 | No retry. The split is reported, and a longer windowed replay (e.g. from st.t692 … st.t772) is proposed instead. |

- The 0.6 threshold leaves a 0.4–0.6 band as "neither", on purpose.
- The rule reads the shares only. It does not use any width ratio, so it cannot be tuned to a hoped-for PASS.
- Binary sha256 at registration: `c43c049a67b192a7580453c01a8d823b227e3ec4dc2254e84437fcf127421cd7`.
