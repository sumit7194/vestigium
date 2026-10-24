# B15b G6: decision-margin wrapper, design (for the Bridge's review; implementation follows the agreed design)

Registered G6 (B15b): decisions get margin ≥ 10 × (map error × local gain). A thin margin is recomputed at 1e-14; a
decision that changes is flagged and reported, and the 1e-14 decision is used. A decision that is thin at 1e-14 too
is UNRESOLVED. This note puts the Bridge's six review points into a concrete design, from a reading of the frozen
constructor (hs_construct.py) and of b15_kerr_ck.py.

## Where the decisions are (from the code)

| # | Decision | Where | Data the wrapper re-derives it from |
|---|---|---|---|
| D1 | Newton converged: ‖P(w) − w‖ < tol (tol = 1e-10 at the B15 call site) | hs_construct.find_periodic (internal) | the journalled P(w, 1, jac) calls of step 1, in order |
| D2 | Saddle: no complex eigenvalue (\|Im\| > 1e-12), \|λ_u\| > 1 + 1e-6, \|λ_s\| < 1 − 1e-6 | hs_construct.saddle_info | DP at z (journalled) |
| D3 | Arc point dropped: the image is None (no return) | manifold_arcs (internal) | journalled P/Pinv results: None, with its plunge certificate (B15b-1 P5) |
| D4 | **Crossing exists:** segments intersect, i.e. t, u ∈ [0, 1] and \|den\| > 1e-18 | hs_construct.crossings | the saved arcs (b15_ck_arcs.npz); crossings() is deterministic on them |
| D5 | Crossing near z* skipped (distance < 1e-3) | crossings(skip_near) | the arcs |
| D6 | Angle ≥ 0.01 (accepted crossing) | b15_kerr_ck.py | the crossing record |
| D7 | Red flag: angle > 10·θ_floor | b15_kerr_ck.py | the crossing record and the arcs (floor_at) |
| D8 | Connection accept/reject: any D6-accepted crossing → steps 3–4 | b15_kerr_ck.py | the count of D6 accepts |

- **D4 is new**, beyond the agreed five. A crossing missed because t or u falls just outside [0, 1] is a decision map
  error can flip. B15's prediction is precisely "no crossing above the red-flag level", so a missed one matters.
  - The wrapper scans every segment pair, as crossings() does. For pairs whose (t, u) lie OUTSIDE [0, 1] by less
    than the error-normalised margin, it reports a near-miss, with the margin in length units: the distance of the
    intersection from the segment ends, in the plane.
- **The refinement test** ‖img_{i+1} − img_i‖ > dmax is a data comparison, but registered as a construction parameter
  with no margin. A flip only changes the sampling density, and its effect reaches θ_floor. It is counted and logged,
  with no margin, as registered.

## The Bridge's points, applied

1. **Completeness, with a count check.**
   - The call-boundary log is pcache's journal: every P/Pinv call and result, in order, crash-safe. It is the
     counted run's own checkpoint, so it is not a second mechanism.
   - The wrapper re-derives D1–D8 from the journal plus the saved arcs.
   - COUNT checks: D1 iterations equals the number of step-1 jac calls up to convergence; D4 equals
     len(crossings(...)) as the run recorded; D6 and D7 equal n_at_or_above_0p01 and n_red_flags; D3 equals the
     number of journalled None results within manifold_arcs.
   - Any mismatch makes G6 INCOMPLETE, never PASS.
2. **All decision types are in:** D1–D8, including connection accept/reject (D8). D8's margin is the minimum D6
   margin over the crossings near 0.01, plus the D4 near-miss margins: a connection that could appear through a missed
   crossing counts.
3. **The map error is an envelope.**
   - e_map(T) = 3 × max(the G4 cross-implementation differences in the T-bin, the G4c convergence estimate where it
     exists).
   - T-bins are decades. A return with T beyond the largest G4-compared T (70,183) gets "error unmeasured" and is
     flagged, never extrapolated.
   - An arc point at level k carries e_k = e_map·Σ_{j<k} ‖DP^{k−j}‖, with DP^{k−j} composed from fresh kerr_rs
     Jacobians along that point's orbit, computed by the wrapper only for points that feed a decision.
4. **Margins, each in its own units.**
   - D6 and D7 (angles): δangle = (e_u/ℓ_u + e_s/ℓ_s), where ℓ is the segment length; short segments amplify.
   - D7 also propagates θ_floor's own error, the same e through κ̂ and ℓ, and takes the margin against the worst case
     of both.
   - D4: the intersection's distance from the segment ends, against e_u + e_s.
   - D2: the eigenvalues of [DP ± δDP], computed with mpmath interval arithmetic on the 2×2, against the distances to
     1 ± 1e-6 and to the 1e-12 imaginary cut. δDP comes from G4's DP differences.
   - D1: the final residual against tol, with e_map as the floor. If tol < 10·e_map, the decision is flagged.
   - D3: the certificate's slack (B15b-1).
5. **Toys, one per decision type.** For each type, two synthetic inputs:
   - one built with a known thin margin, which must be flagged;
   - one with a large margin, which must NOT be flagged.
   This runs as tests before the wrapper sees any run data. A wrapper that never flags is indistinguishable from a
   broken one.
6. **For the findings:** G0's rust margin is 2.7×, and G5 validates λ_u only, since dz = 0 is trivial.

## A gap found while reading the code (flagged for the user, not designed here)

b15_kerr_ck.py stops at step 2 with "steps 3–4 required" if any crossing is accepted. It does not implement steps 3–4.
The registered prediction is that this does not happen. If it does, steps 3–4 need code and an amendment before they
run. This was so already under B15 with MNFlow; the compiled map does not change it.
