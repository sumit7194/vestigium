# B15c DRAFT (2026-11-21): steps 3–4 for B15's candidate connections (sets, then rigorous coverings)

**Status: DRAFT for the Bridge's review. Nothing below has run, and nothing will until this text, as finally agreed, is
registered in PREREG_chaos_horseshoe_phase2.md.** Drafted by Claude Opus 5.5 (session "Quantum").

**What already governs this, unchanged:**
- **B14:** the frozen constructor, `hs_construct.py`, unedited. That covers its steps 3–4 text, the ladder, S8, and the
  required/optional split.
- **B15:** steps 3–4 run only if step 2 returns an accepted connection (angle ≥ 0.01). Sets that get built go to rigorous
  hs_cover with the B13 settings. The prediction: no rigorous ρ > 1.
- **F7:** any rigorous ρ > 1 on Kerr STOPS the MN claim.
- **B15b / B15b-1 / B15b-2:** the compiled rust map, the plunge certificates, and the chord rule.
- **B16:** no wall-time cap.

This amendment only supplies the implementation and the order that step 2's outcome now requires (B15_FINDINGS.md:
147 accepts; "steps 3-4 required"). No threshold, ladder value or prediction changes.

## 1. Which candidates, in what order
B14 builds ONE chain, from the connection that minimises |k_u| + |k_s|, ties broken by the largest angle. On the
recorded step 2 (b15_kerr_rust.json), that is crossing **#4155**: k_u = k_s = −3, angle 0.045861, point
(104.50074766, −1.1e−10). It is one of the 81 measured-error accepts. The 147 accepts split as follows:
- 81 at (k_u, k_s) = (−3, −3), all measured;
- 33 at (−4, −3) and 33 at (−3, −4), all with extrapolated error.

The tiers:
- **T1 (the registered B15 path, COUNTED):** steps 3–4 on #4155 exactly as B14 specifies. This is the B15 outcome.
- **T2 (the Bridge, 2026-11-20: "the 81 measured-error accepts first"):** the other 80 measured accepts, each as its own
  chain through the identical steps 3–4, in B14 order (|k_u| + |k_s|, then −angle, then crossing index). These are
  extra attempts at a negative control, so every chain counts for F7: **any rigorous ρ > 1 on any Kerr chain, T1, T2 or
  T3, STOPS the MN claim.**
- **T3 (proposed; the Bridge decides whether it runs):** the 66 extrapolated-error accepts, after T2, in the same order
  and under the same rules. They are labelled separately.
- **Duplicates.** If two chains produce byte-identical exact-rational specs, only the first is covered. The later one
  is recorded as a duplicate of it.

## 2. Step 3: refine, orbit, frames
The new driver `b15_steps34.py` calls only the frozen `hs_construct` functions, through `mn_numerics.plug_into_constructor`
with the compiled map, as b15_kerr_ck.py does:
- B15_MAP = rust;
- the same kerr_rs library, with its sha256 checked against the step 1–2 run (42ea6c3c…);
- delta_floor and the plunge log as in that run;
- a NEW journal name. Journal keys do not name the map or the stage, so no step 1–2 journal is ever replayed into it.

A MapCheckFailed stops the run as a HARNESS-ERROR. It is never recorded as a rejection.

For each candidate c:
1. **Signs.** k_u, k_s = |c.k_u|, |c.k_s|. s_u = sign(c.k_u), or +1 if it is 0; s_s likewise. This is the HH driver's
   handling (hs_construct_hh_chain.py), which HH-SECONDARY used.
2. **Refine.** `refine_connection(z, s_u e_u, z, s_s e_s, k_u, k_s, c.point)`.
   - If it returns None, the chain stops at **"step 3: refinement failed"** and that is recorded.
   - Recorded as DATA: t, τ, the residual, and the 2×2 FD Jacobian at the solution (recomputed by the same formula in
     the driver, with its condition number).
3. **Orbit and frames.** m = k_u + k_s. Then X_j = tangent_fwd(z, s_u e_u, t, j)[0], U_j likewise, and
   S_j = tangent_back(z, s_s e_s, τ, m − j)[1], for j = 0…m. Recorded: ‖X_m − (z + τ s_s e_s)‖.

**Two disclosures that bear on reading step 3:**
- **A frozen HH constant.** refine_connection's coarse start scans |t|, |τ| ∈ geomspace(1e−4, 7.3e−4). The 7.3 is HH's
  λ_u, hard-coded. Kerr's fundamental segment is [1e−4, 6.26e−3] (λ_u = 62.62). So a candidate whose arc parameter
  lies above 7.3e−4 starts Newton from a poor guess. This is NOT changed, because the constructor is frozen. If T1 fails
  at refinement, the failure is recorded as it is. §4 proposes a non-counted diagnostic arm for that case.
- **Expected degeneracy.** Kerr is integrable. On the section, both manifolds lie on the separatrix level
  {Q = Q_s}, whose only singular point is the saddle. So W^u and W^s coincide as curves, and the Newton system for
  (t, τ) is singular: a one-parameter family of solutions, up to integration noise. Refinement may therefore fail,
  wander, or converge with an ill-conditioned Jacobian. Whichever happens is the recorded outcome. The condition
  number is recorded so that this can be read.

## 3. Step 4: the ladder
This is B14's text, implemented as in hs_construct_hh_chain2.py:
- Ladder order: a0 ∈ (0.03, 0.02, 0.015, 0.01), a ∈ (0.01, 0.005, 0.0025), b0/a0 ∈ (0.5, 0.25, 0.1) and
  b/a ∈ (0.5, 0.25, 0.1).
- N0 = (z, a0 e_u, (b0/a0)·a0·e_s). The chain is the contiguous run j₁…j₂ of orbit points whose sets are disjoint from N0
  and from each other.
- Sampled checks use `sampled_cover(…, n_edge=12, n_int=8)`.
- **Acceptance is the FIRST entry where every REQUIRED covering passes.** The required coverings are N0⇒N0, N0⇒N_{j₁},
  N_j⇒N_{j+1} and N_{j₂}⇒N0. The optional N_{j₂}⇒N_{j₁} is recorded but not required.
  - Disclosure: hs_construct_hh_chain2.py stopped only on a pass that also included the optional edge. B14's text
    (required only) governs, and HH-SECONDARY used it: the first entry, (0.03, 0.01, 0.5, 0.5), passes only the
    required coverings.
- A None from sampled_cover (a sample with no return, i.e. a certified plunge) means that covering FAILS.
- If no entry passes, the chain stops at **"step 4: no ladder entry"**. Recorded per entry: n_ok/n and the failing
  edges.

## 4. Rigorous stage (only for chains with an accepted ladder entry)
**Spec.** Exactly as hs_run.hh2:
- Sets become exact rationals rounded to 1e−10.
- **Gate:** S8 must hold exactly (convex_disjoint). If it fails, the chain stops at "S8" and nothing is launched.
- Header: `system mn`, `prec 128`, `order 20`, `iter 1`, and the params k = 39, alpha = −5/8, beta = 0, E = 49/50,
  L = 445/2. These are the B15 level; the codegen gate's B15_KERR case passed at it.
- Then `caps 65536 4096`, `depth 16 12`, `cover x y 16 16 64`, one checkpoint per covering. S4 and S9 are on.
- No piececap (B16).

**Binary.** Built with the guard (proof_guard.h) from hs_cover.cpp at the registration commit. Its sha256 is recorded
before any run. **Gate GB:** before the counted coverings, it must reproduce these exactly:
- the R1 generic Rössler COVER lines;
- the HH-SECONDARY N0⇒N0 COVER line.

**Outcome classes per covering,** taken from hs_cover's own output:
- **CERTIFIED:** `COVERS=1`.
- **CERTIFIED-FAIL:** at least one `FAILPIECE … CERTIFIED` line (a certified edge or orientation failure).
- **UNDECIDED:** anything else. That means only cap or depth failures, an S4/S9 fail-closed, an exception, `FATAL`, or
  no `DONE`.

**Per chain:**
- **ρ > 1:** every required covering is CERTIFIED. This means **F7 STOP**.
- **CERTIFIED-FAIL:** some required covering is CERTIFIED-FAIL. This is informative and supports the prediction.
- **UNDECIDED:** otherwise. This is a tool limit, NOT support for the prediction. The chain's prediction is "not
  tested", stated as in B15b-2's scope note.

**Why UNDECIDED is a real possibility.** The Kerr homoclinic swings out to r = 46.8M. Rigorous returns through long
swings are exactly what the E_REP line is working on for MN (wrapping through periapsis). So the report states, per
chain, how many of its required coverings were decided at all.

**Proposed diagnostic arm, NOT counted (the Bridge decides).** If T1 stops at "step 3: refinement failed", re-run T1's
refinement with the coarse scan scaled to Kerr's fundamental segment, geomspace(1e−4, 1e−4·|λ_u|), and everything else
identical. It is labelled UNFROZEN and NOT COUNTED. **F7 still applies:** a rigorous ρ > 1 on Kerr is a fact about the
tool, whichever arm produced it.

## 5. Controls (non-counted). Each one exercises a clause and can fail.
Scorer: `b15c_controls.py`. All must PASS before T1 runs.
1. **Selection.** On the recorded step-2 list, the T1 selector returns #4155.
   - On a shuffled copy it still returns #4155.
   - On a toy list with a tie in |k_u| + |k_s|, it returns the larger angle.
   - The T2 order equals the B14 sort of the 80 others.
2. **Positive control: the driver reproduces HH-SECONDARY.** With the HH map plugged in, the driver applied to HH's
   recorded Π4 crossing must reproduce:
   - hh_chain_explore.json's X, U and S (to 1e−12);
   - the ladder entry (0.03, 0.01, 0.5, 0.5) with chain [3, 4, 5, 6];
   - **byte-identical** hh2 exact sets.
   This shows the sign handling, the frames, the ladder and the rationalisation all match the pipeline that certified HH.
3. **Planted reject among the measured accepts** (the Bridge's request).
   - One synthetic candidate is inserted into the T2 list at a position drawn from a seed. The seed is sealed in
     scratch and only the scorer reads it.
   - It is a copy of #4155 whose chain frames are exchanged (U_j ↔ S_j, R1's W1) after step 3.
   - Expected: "step 4: no ladder entry". **FAIL** if any ladder entry passes for it.
   - Its rigorous twin: T1's chain with U ↔ S (and separately with U rotated by 90°, as W2) must be CERTIFIED-FAIL in
     at least one required covering under hs_cover. UNDECIDED does not pass this control; it is reported as "control
     not decided".
4. **Plunge clause.** On the toy flow (b15b_toyflow) with a planted None at one sample, sampled_cover must return
   None, the covering must FAIL, and the run must continue.
5. **MapCheckFailed clause.** A toy map that raises MapCheckFailed must stop the driver with a HARNESS-ERROR, and no
   rejection may be recorded.
6. **S8 clause.** A planted overlapping pair must trip the exact S8 gate, and no hs_cover process may start.
7. **Outcome classifier.** Canned hs_cover outputs, one per class (COVERS=1; a FAILPIECE…CERTIFIED; cap-only;
   FATAL; no DONE), must classify as CERTIFIED / CERTIFIED-FAIL / UNDECIDED / UNDECIDED / UNDECIDED.
   - A canned all-CERTIFIED Kerr chain must write the F7 STOP flag.
   - A chain with one UNDECIDED required covering must NOT give ρ > 1.
8. **Duplicates.** Two identical candidates: the second is marked as a duplicate, and only one hs_cover spec is
   written.

## 6. Order, resources, reporting
- **When.** After the Melnikov stage-2 verdict is committed and A3 is launched. A3 uses one core and about 200 MB.
- **Constructor stage.** First the controls, then T1 steps 3–4, then the T2 constructor stage. It is one Python
  process at nice 10, with an RSS guard at 1 GB and a disk guard.
- **Rigorous stage.** Gate GB, then T1's rigorous coverings. It needs a slot request to the Bridge, up to 4 cores
  (within the 8-core fleet limit), nice ≥ 10, and a guard on every process.
  - T2's rigorous coverings start only after T1's result is reported and the Bridge confirms the slot.
- **Reporting.**
  - Per chain: the stage where it stopped, the data recorded in §2–3, and per covering its class with leaf and fail
    counts.
  - Every UNDECIDED is counted separately and is never merged into "fails".
- **Unchanged:** the frozen constructor, every B13, B14 and B15 threshold, the prediction, F7 and B16.

## 7. A post-result finding about B15's red-flag record (NOT registered; it does not change the steps 3–4 trigger)
This is recorded in B15_FINDINGS.md §4.
- **Duplicate points.** In the frozen manifold_arcs, a point is appended before the refinement check, and the `continue`
  revisits it. So every refinement leaves a duplicate point. For example, 2192 of the 4423 segments of u_−3 have zero
  length.
- **Effect on the red-flag rule.** B15's floor_at measures the turn between neighbouring segments, which are often of
  zero length. So θ_floor = 0 at **9437 of the 10081** crossings, and the red-flag rule (angle > 10·θ_floor) is
  degenerate there.
  - With duplicates removed (a diagnostic only), all 147 accepts have angle / θ_floor between 0.16 and 0.82 (#4155:
    0.59). None would be a red flag; they sit at the discretisation-noise level.
  - The arcs that carry them also exceed dmax: u_−3 has 2178 segments longer than 0.01, the longest 0.146, because the
    maxpts cap is reached.
- **Crossing detection is not affected.** Zero-length segments are skipped (den ≈ 0), and the polyline is unchanged.
- **The steps 3–4 trigger is B14's angle ≥ 0.01,** not the red flag. So T1 must still run.
