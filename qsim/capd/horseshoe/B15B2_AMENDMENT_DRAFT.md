# B15b-2 DRAFT (2026-10-24): crossings on chords across dropped arc points

**Status: REGISTERED as B15b-2 in PREREG_chaos_horseshoe_phase2.md (2026-10-24, the user's OK). This file is
the drafting history; the prereg text governs.** Previously: Found while designing G6 (B15B_G6_DESIGN.md), and agreed in substance with the
Bridge. It goes to the user for registration before any counted B15 run.

## The finding

- **What the code does:** hs_construct.manifold_arcs drops an arc point whose image is None (no return) and joins its
  surviving neighbours directly. Under the compiled maps (B15b-1), every None is a certified plunge (or tmax).
- **The consequence:** across a plunge cut, the polyline contains a CHORD, a straight segment where the true manifold
  falls into the black hole. hs_construct.crossings treats a chord like any other segment.
- **So:** a crossing of W^u and W^s found ON a chord is a polyline artefact, not a manifold crossing. If the only
  accepted crossings (D6, angle ≥ 0.01) lie on chords, B15's step 2 would report a connection that is an artefact.

## The rule (fixed before any counted run)

1. **Chords** are identified by G6's replica of manifold_arcs' bookkeeping (original parameters and drops). The
   replica must reproduce the saved arcs bit for bit (B15b G6, completeness).
   - A segment at level k is a chord if any point whose original parameter lies strictly between its two endpoints'
     parameters was dropped at any level ≤ k.
2. **A D6-accepted crossing on a chord** (on either curve) is UNRESOLVED, not a connection. It is reported and
   flagged to the user.
3. **D8 (connection accepted)** counts only crossings that are not on chords.
   - If the only D6 accepts are on chords, the step-2 outcome is UNRESOLVED.
   - If at least one non-chord crossing is accepted, D8 holds as registered, and the chord accepts are still reported.
4. **Chord crossings that D6 rejected** (angle < 0.01) are recorded as data. They do not change the outcome.
5. **If the replica does NOT reproduce the arcs,** chords cannot be identified. G6 is then INCOMPLETE, and any D8
   accept is UNRESOLVED (the conservative reading), with no exception.

## Also recorded

- **A limitation of the old Python B15 run** (MNFlow; stopped at the macOS update and not relaunched): its arcs had
  the same drop-and-join behaviour. Its Nones also include scipy failures, not only plunges (B15b-1). That run's
  in-memory arcs cannot be audited.
- **The scope limit of steps 3–4:** b15_kerr_ck.py stops with "steps 3–4 required" if a connection is accepted, and
  implements neither step.
  - If that happens, the run ends with that status (not an exception), and the findings say: "registered prediction
    NOT CONFIRMED because of an implementation scope limit (steps 3–4 not implemented); this is not a negative
    result."
  - Steps 3–4 would need code and their own amendment before running.

## What it does not change

The frozen constructor, every B14 and B15 threshold, and the registered prediction. The rule only governs how the
run's step-2 output is classified.
