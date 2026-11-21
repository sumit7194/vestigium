# B15 (Kerr, rust map) counted run and G6: FINDINGS

Written by Claude Opus 5.5 (session "Quantum"), 2026-11-20, from the run's own records. Nothing below has been
re-tuned; it reads the registered outputs. The Bridge rules on the next step.

## The run
- **Launcher:** b15_launch.sh, PID 78628, detached, nice 10. It ran from 08:39:52 to 22:33:04.
  - Steps 1–2 (b15_kerr_ck.py, B15_MAP=rust, kerr_rs sha256 42ea6c3c…): 1076 s, exit 0.
  - G6 (b15b_g6_run.py): about 13.6 h, exit 0. Peak tree footprint 2134 MB.
- **Guard (b15_run_guard.py):** first armed at 2048 MB; earlier re-armed at 4096. At 19:58 it was re-armed at 6144 MB
  (a new guard first, then the old one retired by verified PID), per the Bridge's memory relaxation from Sumit. The
  guard never tripped. The full record is in b15_rust_guard.log.
- **Outputs:**
  - b15_kerr_rust.json, b15_rust.journal, b15_rust_arcs.npz, b15_rust_plunges.jsonl, b15_rust_run.out,
    b15_rust_launch.log.
  - b15_g6.json is 931 MB, sha256 00ffe9a6dc3a8e49ccf2ce2c54631fb02e011e1c78e6fdce1fb90b68c792b75b. It is kept on disk and
    gitignored, because it exceeds the git host limit.
  - b15_g6_summary.json comes from b15_g6_summary.py, a read-only streaming tally of b15_g6.json.

## Constructor verdict (steps 1–2)
- **Step 1:** saddle z = (1.84118843978127, 0), λ_u = 62.6203, λ_s = 0.0159693. D2 is robust: λ_u enclosed in
  [62.62026849, 62.62026867].
- **Step 2:**
  - 10081 crossings;
  - 147 with angle ≥ 0.01 (range up to 0.04586);
  - 9625 red flags;
  - 7942 plunges, each certified (P5: 7942 records, the same as the journal's 7942 None results).
- **The constructor's verdict:** "candidate connections: steps 3-4 required (prediction: rigorous coverings give no
  ρ > 1)".
- **B15b-2 scope note:** the registered prediction is NOT CONFIRMED because of an implementation scope limit (steps
  3-4 are not implemented). This is not a negative result.

## G6 details
- **Completeness:**
  - complete = true;
  - replica bit-identical;
  - journal misses 0;
  - chord segments 0;
  - the D4/D6/D7 counts equal the run's (10081 / 147 / 9625).
- **Every crossing was thin at the run tolerance.** D1 already notes "tol < 10 e_map", so all 10081 were recomputed at
  1e-14.
  - **6023 crossings are still thin at 1e-14, so UNRESOLVED.** None of them is an accept: all are rejects or red-flag
    decisions below 0.01.
  - 2150 crossings carry the flag "error unmeasured (a return beyond the G4 range)".
- **Near-miss scan (the Bridge's choice 3):**
  - 1,639,912 segment pairs could become a crossing at the red-flag level. All were recomputed at 1e-14.
  - **203,299 are still thin, so UNRESOLVED.**
  - 238 near-misses EXIST at 1e-14, with angles 8.3e-7 to 4.6e-6. **211 of them are red flags the run did not
    record.** None is an accept.
- **D3 / P5:** 7942 plunge records against 7942 None results. The minimum y-slack is 1.07e-4; no R-slack value is
  recorded.
- **Note carried from the Bridge:** the 1e-14 error is a self-convergence ESTIMATE (1e-14 vs 1e-13, × 3), not a bound.

## 1. Step 2: UNRESOLVED (registered rule)
This is the headline, under the registered G6 rule.
- 6023 of the 10081 crossings are still thin at 1e-14.
- 203,299 of the 1,639,912 near-misses are still thin at 1e-14.
- 211 near-misses are red flags that the run did not record. They exist at 1e-14, with angles 8.3e-7 to 4.6e-6.
- 2150 crossings carry "error unmeasured" (a return beyond the G4 range).

Step 2 is not decided either way. D8 = CONNECTION (n_accept 147, n_chord_accept 0). D8's thin = true comes from the thin
rejects in its input list.

## 2. Post-result reading (NOT registered): the outcome is separable by decision type
This reading was added after the result, at the Bridge's instruction (2026-11-20). It sits under the registered outcome
and does not replace it.
- **The ACCEPT side is robust.**
  - 147/147 accepts are re-accepted at 1e-14; none is thin at 1e-14 and none is on a chord.
  - Angles run from 0.010017 to 0.04586. The minimum margin above 0.01 is 1.70e-5; the maximum angle shift between the
    run and 1e-14 is 7.6e-9.
  - Crossing indices run from 4091 to 8913.
- **The 147 split by how their error is known:**
  - **81 have measured error.** These are the strongest candidates.
  - **66 rest on an extrapolated error,** because their returns lie beyond the G4 range. They are WEAKER: their
    robustness is only as good as the extrapolation.
- **Every unresolved item is a reject or a red flag** (the 6023 crossings, the 203,299 near-misses and the 211
  unrecorded red flags). None is an accept. These bear on the B15 red-flag prediction, not on the candidate
  connections.

## 3. What "robust" means here
**Every 1e-14 error is an ESTIMATE (self-convergence, 1e-14 vs 1e-13, × 3), not a bound. "Robust" means numerically
stable, not certified. The candidate connections become a result only through steps 3–4 (rigorous coverings), which
are not yet implemented. Nothing here says whether ρ > 1.**

## Next (the Bridge, 2026-11-20)
- Register steps 3–4 after the Melnikov stage-2 counted run finishes, which frees the box's memory.
- Cover the 81 measured-error accepts first.

## 4. Post-result finding (2026-11-21, NOT registered): the red-flag record is degenerate at most crossings
Found by Quantum while drafting steps 3–4 (B15C_STEPS34_DRAFT.md §7). It reads saved outputs only; nothing was re-run.
- **Duplicate points in the arcs.** The frozen `manifold_arcs` appends point i before its refinement check; when it
  refines, `continue` revisits i and appends it again. Every refinement therefore leaves a duplicate.
  - In b15_rust_arcs.npz, for example, u_−3 has 2192 zero-length segments out of 4423, and u_2 has 3931 out of 7901.
  - Detection of crossings is unaffected: a zero-length segment has den = 0 and is skipped, and the polyline is the
    same set of points.
- **θ_floor = 0 at 9437 of the 10081 crossings.** b15_kerr_ck.py's `floor_at` takes the turn between the neighbouring
  segments, which are often zero-length. So the red-flag rule (angle > 10·θ_floor) is degenerate there: most of the
  9625 red flags, and 139 of the 147 accepts, have θ_floor = 0.
- **Diagnostic, with duplicates removed (the same floor_at formula on the de-duplicated arcs).** All 147 accepts have
  angle / θ_floor in [0.16, 0.82]; #4155 has 0.59. None would be a red flag, so they sit at the polyline-discretisation
  level.
  - This is consistent with Kerr's integrability: the manifolds coincide on the separatrix {Q = Q_s}.
  - The arcs carrying them are also coarser than dmax: u_−3 has 2178 segments longer than 0.01, the longest 0.146,
    because the maxpts cap is reached.
- **Status of the red-flag clause (B15c §5, registered 2026-11-21): NOT TESTED, degenerate as implemented
  (θ_floor = 0 at 9437/10081).** The de-duplicated ratios above are a post-result DIAGNOSTIC only, not the red-flag
  test passing.
- **What this does NOT change.** The registered outcome (§1) stands as recorded. The steps 3–4 trigger is B14's angle
  ≥ 0.01, so steps 3–4 still run (B15c).
