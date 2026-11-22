# B15e DRAFT (2026-11-22): B15d's Kerr test with a twin negative control that can decide

**Status: REGISTERED as B15e (c3b7c8f), with the Bridge's choice (i): a ONE-VARIANT twin (swap). §4–5 below are the draft; the registered text in PREREG_chaos_horseshoe_phase2.md governs.** Requested by the Bridge after B15d's TWIN-EARLY (2fcdeb1) and
B15d-4 (2dc1926). Drafted by Claude Opus 5.5 (session "Quantum"). If Sumit objects, it stops here.

B15d's own record stands. Its twin reading is expected to be "control not decided" and B15d holds; that line is logged
by B15d's runner and is never rewritten by B15e. The Bridge records the rot90 clause as slip 12.

## 1. Why B15d's twin could not decide
- In hs_cover only (b), the edges, and the orientation check can certify a failure; (a) can only fail to certify.
- On HH the return map stretches every direction that has a component along the unstable direction. A set's u-edges sit
  at ±(u-vector). If the u-vector has any unstable component, their images are pushed out of the target on opposite
  sides, so (b) and the orientation PASS. That is what rot90 showed in all 6 coverings (b = 1, orient LR/RL, fail_b = 0).
- Only a u-vector along the STABLE direction is contracted. Its edges then land inside the target, or on the same side,
  and the failure can be certified. That is the swap variant (u = S), which was edge-fixed CERTIFIED-FAIL in all 6.
- **So a frame negative control on HH can decide through (b)/orientation only if its u-direction is (close to) stable.**
  Any other misaligned frame can end at best UNDECIDED. This is a float argument plus the B15d-2 records, not a proof.

## 2. The B15e twin
- **swap: reused from B15d, not rerun.** Its 6 required coverings are edge-fixed CERTIFIED-FAIL (twin_e/*.out, 2fcdeb1;
  binary sha fb5fcbfc, spec sha256 in run.log). Under B15d-2 that class is final. Its (a) chunks finish in B15d's queue
  for the record. A HARNESS-ERROR in any swap merge would void the B15e twin (§4).
- **stab: one new variant, fixed here before any pre-check.** For each hh2 set (c, U, S), the frame is the recipe's
  orthonormal construction applied to the stable tangent instead of the unstable one, keeping the certified set's sizes:
  - u-vector = |U|·Ŝ, s-vector = |S|·rot₊₉₀(Ŝ), with Ŝ = S/|S|; centre c unchanged.
  - Components rounded to rationals at 1e−10 (D.R10), as in hh2. S8 must hold exactly and the exact frame must be
    nonsingular, or the draft stops at "stab: S8" / "stab: singular" and goes back to the Bridge.
  - Coverings: the same 6 required (N0N0, N0N3, N3N4, N4N5, N5N6, N6N0), same binary, caps, depth, precision and
    `cover x y 16 16 64`, split edges-first exactly as B15d-2.
  - Why stab and not something else: it shares the decisive mechanism (u along stable) but differs from swap in BOTH the
    s-direction (Ŝ⊥, not U) and the side lengths. So a second, independent frame shows the same failure route, and it
    is also the "wrong eigendirection" version of the very recipe used on Kerr.

## 3. The pre-check (NOT COUNTED), with its rule fixed before it runs
- **What runs:** stab's 6 edge chunks only (`arange 0 0`, no checkpoint), on HH, 1 slot (the 4th; B15d's runner keeps 3),
  nice 10, guarded at 1 GB per process plus the box rules. Outputs go to horseshoe_results/kerr/b15e/precheck/.
- **Rule:** stab enters B15e only if ≥ 1 required covering is edge-fixed CERTIFIED-FAIL in the pre-check and no chunk
  is a HARNESS-ERROR (check_e). Otherwise the draft goes back to the Bridge as "no decidable second variant". There is
  no second candidate and no retuning of sizes or angles after the result.
- **Pre-check result (2026-11-22 06:5x): stab STOPS at "stab: S8"; no hs_cover run happened.**
  - `b15e_precheck.py build` found the exact stab sets pairwise disjoint except **N0|N6** (S8 false;
    horseshoe_results/kerr/b15e/precheck/build.json). Under the rule, stab does not enter B15e. This goes back to the
    Bridge as "no decidable second variant". There is no retuning here.
  - Why (float reading, not a proof): the chain returns to N0 along W^s, and N6 is the last set on that approach.
    stab puts N0's LONG side (|U| = a0 = 0.03) along the stable direction, so N0 reaches N6. Swap avoids this only
    because its side along S is the short one (|S| = 0.015).
  - **Disclosure:** this S8 gate ran a few minutes before this draft was first committed. The rule text was already
    written (above) but not yet committed. S8 is a geometry gate on the exact sets, not an hs_cover result, and nothing
    was changed after it.
  - So §4 is open until the Bridge decides how B15e's twin should be formed (§5).

## 4. B15e: what would be registered
- **Twin PASS** = swap (reused, edge-fixed) AND stab with ≥ 1 required covering edge-fixed CERTIFIED-FAIL in its
  COUNTED edge chunks. The counted stab edge chunks are a fresh run; each COVER line must equal its pre-check line byte for
  byte, or that covering is HARNESS-ERROR (a free determinism check). Both variants' (a) chunks run to completion for the
  record. All coverings are read with the B15d-2 merge rule and the B15c/B15c-1 classifier, unchanged.
- **Recipe:** B15d's RECIPE line from the B15d-4 queue, read before any Kerr covering result is read. B15e adds nothing
  to it.
- **Kerr:** the B15d §3 chain and sets and the B15d-3 split, unchanged (kerr_e/ and kerr_a/ specs as committed). The
  prediction and the §5 readings are B15d's, word for word. The headline must say that this is B15e, re-registered after
  B15d's twin slip, and that the stab variant was pre-checked (so the twin shows capability, it is not a blind test).
- **When Kerr runs.** After all three hold: (1) B15e is registered; (2) the counted stab edge chunks give twin PASS;
  (3) the RECIPE line is logged. Then the 8 Kerr edge chunks, KERR-EARLY, the 8 Kerr (a) chunks, KERR.
  - The remaining twin (a) chunks and Kerr share the slots. Proposed order: Kerr edge chunks first, then the remaining
    twin (a) chunks interleaved with the Kerr (a) chunks in registered order. This is the Bridge's call.
  - The KERR reading is final only once every twin merged class is complete with no HARNESS-ERROR. If one appears, the
    Kerr reading is withheld and goes back to the Bridge.
- **Unchanged:** F7 (any ρ > 1 STOPS), embargoes and the TS rules, the slots, the Cuspis night rule, and nothing
  loosened anywhere.

## 5. Open for the Bridge (after the stab S8 stop)
- **(i) A one-variant twin.** swap alone (edge-fixed CERTIFIED-FAIL in all 6, final), registered openly as one variant,
  with rot90 recorded in B15d as "control not decided" and stab as "S8 stop".
- **(ii) A new second candidate, chosen by the Bridge.** For example stab with swap's side lengths (u = |S|·Ŝ,
  s = |U|·Ŝ⊥), which keeps N0's side along S short. It would get its own pre-check rule, committed before its S8 gate
  or any edge chunk runs. I have NOT computed its S8 or anything else.
- Either way, Kerr waits for B15e's registration, as §4 says.
