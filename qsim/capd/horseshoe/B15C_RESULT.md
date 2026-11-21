# B15c (steps 3–4 for B15's candidate connections): RESULT, constructor stage

Written 2026-11-21 by Claude Opus 5.5 (session "Quantum"), from the registered run's records in
`horseshoe_results/kerr/b15c/`. Registered: B15c (a126a6b) and B15c-1 (7ca093d). Controls: e837011.

## Headline (B15c §5)
```
T1: step 3: refinement failed 1 / step 4: no ladder entry 0 / S8 0 / UNDECIDED 0 / CERTIFIED-FAIL 0 / RHO>1 0 / duplicate 0
T2: step 3: refinement failed 80 / step 4: no ladder entry 0 / S8 0 / UNDECIDED 0 / CERTIFIED-FAIL 0 / RHO>1 0 / duplicate 0
T3: step 3: refinement failed 58 / step 4: no ladder entry 8 / S8 0 / UNDECIDED 0 / CERTIFIED-FAIL 0 / RHO>1 0 / duplicate 0
B15 prediction: NOT TESTED (T1: step 3: refinement failed)
```
- **No chain reached the rigorous stage, so no hs_cover run happened.** F7 was not triggered, but that is not because a
  rigorous test was passed: the prediction was never tested.
- **The 147 candidates are 13 distinct attempts, not 147.** This comes from the NOT COUNTED post-hoc pass,
  `paths_NOTCOUNTED.out`, which ran with 0 new map calls.
  - The frozen Newton path is fixed by (k_u, k_s, signs, coarse start).
  - **T1 and T2 share ONE refinement path:** all 81 measured accepts sit near (104.5, 0) with k = (−3, −3), so they get the
    same coarse start (7.3e−4, 7.3e−4).
  - **T3's 66 candidates form 12 paths:** 11 fail at refinement, and 1 (k = (3, 4), 8 candidates) refines to one identical
    chain with no ladder entry.
- **The red-flag sub-prediction is NOT TESTED:** it is degenerate as implemented (B15_FINDINGS §4).
- **The diagnostic arm is UNFROZEN / NOT COUNTED.** It is reported below, outside the headline.

## The run
- **Controls:** PASS (controls.json; run 1's test-design FAIL is kept, e837011).
- **T2 seal:** sealed before launch (seal_record.txt).
- **Launch:** b15c_launch.sh, PID 24572, at nice 10, detached. It ran from 18:24:37 to 18:35:02 on 2026-11-21.
- **Guard:** b15_run_guard at a 1 GB cap; peak 107 MB, never tripped.
- **Driver:** sha256 c7737918…
- **Map:** kerr_rs with sha checked as 42ea6c3c…. B15 step 1 was recomputed bit-identically before any candidate (z matched).

## Per tier
**T1, #4155 (k −3/−3, angle 0.045861): "step 3: refinement failed".**
- Why, from the NOT COUNTED replay `T1_refine_diag_NOTCOUNTED.out` (same deterministic map, own journal):
  - Newton reaches |r| ≈ 1e−9 by iteration 4, then sits in a noise band, |r| ≈ 1e−11 to 1e−9, with **cond(J) between 3e6
    and 9e8**, drifting along a line.
  - After 30 iterations the final residual is 1.16e−10, which is above the 1e−10 acceptance, so the function returns None.
- This is the registered expected degeneracy (§2: W^u = W^s, a one-parameter solution family) at the integration-noise
  floor. It is not the hard-coded HH constant: the Kerr-scaled start converges to the same t ≈ τ ≈ 3.973e−3.
- **Acceptance at this line is effectively a coin-flip on noise.** T1 ends at 1.16e−10 and the arm at 8.9e−11.

**T2, the 80 other measured accepts:** all "step 3: refinement failed", on T1's single path.

**T3, the 66 extrapolated-error accepts:**
- 58 "step 3: refinement failed".
- 8 "step 4: no ladder entry", all one identical chain:
  - k = (3, 4), t = 4.652271e−4, τ = 5.419545e−4;
  - residual 3.4e−11, cond(J) 1.4e8;
  - |h − z| = 27.65, max_j |Q(X_j) − Q_s| = 9.9e−9;
  - at most 1 of 7 required coverings passes, over all 108 ladder entries.

**Planted entries (sealed in T2, scored after the run):**
- **hh_swap** (deciding, control 3): "step 4: no ladder entry". **CONTROL 3 PASS.**
- **kerr_t1_swap** (extra): "not constructible (T1 stopped at step 3)", as anticipated in §6.

## Diagnostic arm (UNFROZEN / NOT COUNTED; F7 applies): "step 4: no ladder entry"
- **Refinement:** it ended at residual 8.9e−11, with cond(J) 6.5e7, |h − z| = 102.66, t = 3.97389e−3, τ = 3.97282e−3
  and m = 6.
- **|Q(X_j) − Q_s| ≤ 1.66e−6, i.e. 2.8e−10 relative to Q_s = 5867.6.** The "connection" lies on the separatrix level
  set, which is the coinciding-manifold family, not a transversal point.
- **Ladder:** 108 entries. At most 1 of the 7 required coverings passed (N0⇒N0). The coverings 0>1, 1>2, 2>3, 3>4, 4>5
  and 5>0 failed at every entry.

## Reading
- **Every chain stopped before the rigorous stage.** In each case the stop shows Kerr's integrable structure:
  - a singular refinement (cond(J) 1e6–1e9);
  - or, where refinement scraped under 1e−10, a "connection" on the {Q = Q_s} level set whose sampled coverings fail
    along the chain.
- **This is what integrability predicts, but it is NOT a test of the B15 prediction.** The B15 prediction is about
  rigorous coverings, and none was attempted. That is what the vacuous-pass guard is for. B15d (proposed, to be
  registered separately) would test the rigorous stage on the arm's chain with fixed sets.
- **Everything in the "why" lines is float and non-rigorous.**
