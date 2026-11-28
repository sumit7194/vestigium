# Route-1 pilot: registration (written BEFORE any pilot code computes a target number)

Written 2026-11-28 by Claude Opus 5.5 (office "Quantum").
- GO: Sumit via the Bridge, 2026-11-27 ("the route-1 pilot, as you scoped it").
- Inputs:
  - EXPLICIT_BETA_ROUTES_DRAFT.md (route 1 and "the blocker");
  - ROUTE1_LEMMA_DRAFT.md: read CORRECT after F1. **Its use here is CONDITIONAL on F2**, a read at source of the
    parameter-dependence citation in (0). No certifying claim may rest on it until F2 closes.
- **This file is for the Bridge's read. No run starts before that read.**

**SETUP CORRESPONDENCE.** The pilot runs at the conditions of the S2 claim, at its Kerr end:
- M = 5, a = 3 (k = 4, α = −1/3); S2's E and L; H = −½;
- section y = 0, upward;
- S2's R-symmetric half BVP at the 3π/2 zero, with m = 9;
- the same header gen/mn_field.h (4c1c7b57), whose field Tier 2a re-derived (AGREE);
- β ∈ [0, w], at the Kerr end of the interval an explicit β* would cover.

## Gate paragraph (fleet practice)
- **What it decides.** Whether route 1 (an explicit β* reaching S2's 3/100, giving chaos for every 0 < |β| ≤ 0.03) is
  affordable.
- **Why measure first.** Its cost is unknown over four orders of magnitude (10¹–10⁵ core-h), because the long return
  wraps enclosures by ~1.15e7 × the set size (S2-0).
- **What the pilot measures:** how the width of the enclosure of t′ over a β-interval grows with the interval's width
  w, once the remedies are in (segmented returns, β carried affinely).
- **Cost:** ≤ 12 core-h measured, the cap.
- **Premortem:**
  - (a) Segmentation doesn't remove the wrapping, so the widths stay ~1e7 × set size → BLOCKED.
  - (b) The lemma's hypotheses (K1, K2) fail at w = 1e−4, because the frame box Z drags with c′ ≈ 1.1 → PARTIAL.
  - (c) The C² cost per pass is ≥ 10× C¹ → the projection explodes.
  - (d) Code bugs: caught by the controls below.

## What is computed (one "pass" per w)
- **Engine.** CAPD C² (Taylor order 20, MPFR-128, step tolerance 1e−24), guard-built (trust rule 1), with the NaN rule
  (v4 helpers).
  - β is carried as a 5th state variable (β′ = 0), so ∂_β is part of the C² jet. No codegen change: the header's c[2]
    is fed from the state.
- **The initial sets carry β affinely.** Each node set is the parallelepiped {z̄_i + z_i′ (β − β̄) + ball} × {β}, with
  z_i′ from the float continuation, not a box in (z, β).
- **Segmentation.** Every return, and above all the long excursion (bvp_pt8, ~319 steps), is split into n_seg time
  segments, with segment nodes as extra BVP unknowns (as control (iv)'s bvp2 did).
  - The pilot runs **n_seg ∈ {1, 20}** on the long return (n_seg = 1 is today's S2 form, and is the comparison).
- **The parametric fixed point.** w_β and c′(β), uniformly over [0, w], by a parametric Krawczyk.
- **Lemma hypotheses (K1)–(K4)** over Z = B × [0, w], with B centred at the true w_β and δ as in S2.
  - This gives H_β, H_uu and H_uβ.
- **The parametric half BVP.** Krawczyk uniform over β ∈ [0, w] (the pattern of control (ii)'s x̂-uniform form), and
  s′(β) by the implicit function theorem.
- **[t′] over [0, w].** From v′ (ROUTE1_LEMMA_DRAFT §4), with interval arithmetic throughout.
- **Values of w:** 1e−8, 1e−6 and 1e−4, in that order. If a smaller w already fails, stop going up.

## Registered outcomes (fixed now)
For each w and n_seg, record:
- rel_width(w) = width([t′]) / |mid([t′])|;
- whether 0 ∉ [t′];
- whether (K1)–(K4) hold;
- core-h.

Readings:
- **TAMED.** With n_seg = 20 at w = 1e−4: 0 ∉ [t′] and (K1)–(K4) hold, and the projection to [0, 0.03] is
  ≤ 120 core-h.
  - Projection = (0.03 / w_max_ok) × (core-h per pass) × 1.5, where w_max_ok is the largest w that certifies.
  - Then a full route-1 registration is drafted for the Bridge and Sumit. That is a new budget; nothing more is
    included here.
- **PARTIAL.** It certifies at a smaller w but not at 1e−4, or the projection is 120–1200 core-h.
  - Report it, with the measured scaling of rel_width(w).
  - Route 3 / Taylor models in β (with Julia TaylorModels allowed by Sumit's rule) become the next design question.
- **BLOCKED.** No w ≥ 1e−8 certifies with n_seg = 20, or rel_width grows like the naive ~1.7e7·w.
  - Route 1 by box enclosures is dead. That is written up, and Step A's non-explicit β₀ stands as the small-β result.
- **INVALID.** Any control below fails.

## Controls (each must behave as stated)
- **(c1) Consistency with Step A.** On the smallest interval, [0, 1e−8], [t′] must CONTAIN Step A's analytic constant
  t′(0) = −1.00307e−3 (the float value). Its interval is [−1.0036e−3, −1.0025e−3], a ±0.05% band.
  - The value uses L″ ≈ 8L₂ − 32L₄. The higher harmonics (L₆ ~ 1e−14, from the observed decay) are negligible but
    NOT rigorously bounded tightly: the certified T₃ bound is loose, at 68% of |L₂|.
  - So this is a consistency control, not a proof input.
  - If [t′] excludes that band → INVALID (a bug on one side or the other).
- **(c2) The S2 point check.** The pass's t at β̄ = w/2 must agree with S2's certified slope at β = 0 (Kerr, control
  (i)), with t(0) ∋ 0, to within |t′|·w plus the enclosure widths.
- **(c3) Sabotage.** With the 3β²(P3² − P2²)/R⁶ G term removed (gen_sab), [t′] on [0, 1e−8] must still contain
  t′(0). The β² term cannot affect the first derivative at β = 0.
  - This is a must-NOT-fire. A change in t′(0) beyond the widths would expose a β-ordering bug.
- **(c4) Lemma self-check.** At w = 1e−8, H_β must be consistent with the float drift of the eigen-slope:
  |h_β| ≲ |d(eigen-slope)/dβ| · δ*-scale, checked in float. This is a sanity check only; it is not a decision.

## Conduct, caps and kill criteria
- **Mac mini:** ≤ 4 single-core jobs at nice 10, detached (setsid/launchd), checkpointed per pass.
  - Pause-only guards: nothing kills a job.
  - A slot request goes to the Bridge before any compute over 30 min.
- **Spend cap: 12 core-h measured.** On reaching it, pause my own PIDs and report. Never kill.
- **25% check-in at 3 core-h:** a status line to the Bridge (core-h only, plus whether the controls passed).
- **Kill criteria (state + date):** STOP and write up if, by **2026-12-06 18:00 IST**, the pilot has not produced
  rel_width for w = 1e−8 with n_seg = 20, or if any control is INVALID twice after fixes.
- **Development before any run** (no compute claims):
  - the C² chain with β as a state variable;
  - segmentation;
  - the parametric fixed point and BVP;
  - the lemma hypothesis checks;
  - a Tier-1-style Arb re-check of the pilot's decision arithmetic, which counts only after a read by a separate AI
    session.
  - Estimated ~1 week of development (not compute).
- **Order:** this registration → the Bridge's read → development → a smoke test on one segment (< 30 min, Kerr) → the
  pilot passes.
- Each step's result is reported. Deviations are disclosed as amendments, appended.

## What this pilot does NOT decide or claim
- No chaos claim for any new β. Even TAMED at w = 1e−4 certifies only [0, 1e−4], and only conditional on F2.
- No claim about route 2 or route 3, beyond the scaling measurement that prices them.

## A1. Control fixes from the Bridge's read (2026-11-28; appended before any pilot code computes a target number)
The Bridge's read accepts the registration once these are folded in.

- **(A1.1) No vacuous passes.**
  - c1 counts as PASS only if rel_width([t′] on [0, 1e−8]) ≤ **1%**. If it is wider, c1 is **UNINFORMATIVE**: reported,
    but neither a pass nor a fail.
  - The same rule applies to c3: the sab field's [t′] must have rel_width ≤ 1% to count.
  - If c1 is UNINFORMATIVE at w = 1e−8, that is itself a finding about the widths, recorded in the outcome reading.
- **(A1.2) (c5): a must-FIRE sensitivity control for the β-linear term.**
  - **The mutation:** feed the field β′ = (1 + ε)β in place of β (the header's c[2]).
    - Then t_mut(β) = t((1 + ε)β), so t′_mut(0) = (1 + ε) t′(0) EXACTLY.
    - This scales the O(β) part of the deformation by (1 + ε). The O(β²) part is also scaled, but it does not reach
      the derivative at 0.
  - **Choosing ε (rule fixed now):**
    - Before any certifying pass, estimate in floating point the expected half-width W of [t′] on [0, 1e−8] with
      n_seg = 20, from a float run of the same chain with interval-like perturbations (finite-difference spread).
    - Set ε := max(0.01, 5W/|t′(0)|), so the predicted shift ε|t′(0)| ≥ 5W.
    - Record W, ε and the float method in an appended note BEFORE the first certifying pass.
  - **Must fire:** on [0, 1e−8], [t′_mut] must EXCLUDE Step A's band [−1.0036e−3, −1.0025e−3] and CONTAIN
    (1 + ε)·t′(0) ± 0.05%.
    - If it does not → **INVALID** (the pipeline cannot see the β-linear term).
  - If ε > 1 is needed, the widths are too large for any β-linear test at this w. c5 is then UNINFORMATIVE and the
    pilot reads at best PARTIAL.
- **Order of runs, updated:** the float estimate of W, then ε recorded, then the smoke test (< 30 min), then the passes
  c1, c5 and c3, then the w-ladder.

## A2. Integration settings, cost calibration and drop order (2026-11-28; the Bridge APPROVED; registered before any pass)
- **Disclosure (g): what was known when A2 was fixed.** The settings below were chosen AFTER seeing development runs:
  - per-return widths at one thin point at dev settings: D ≈ 5e−9 and D² ≈ 5e−7 relative (ROUTE1_DEV_LOG D2);
  - the C² cost: ≈ 10× C¹ per step, ≈ 52 min per near-fixed-point return at production settings, ≈ 10 min at dev
    settings.
  - **[t′] itself has not been computed at any w.** No pass has run.
- **(a) Pilot integration settings:** Taylor order 15, step tolerance 1e−14, MPFR-128, with the same guard
  (trust rule 1) and the same NaN rule (every enclosure checked finite).
  - CAPD enclosures are rigorous at any tolerance; the tolerance changes only the widths. So dev settings can only make
    [t′] WIDER than production would. A PASS at dev settings is conservative.
- **(b) The c1 width bar** (rel_width([t′]) ≤ 1%, A1.1) stays the arbiter.
  - If [t′] is UNINFORMATIVE at w = 1e−8 at these settings, I STOP and report.
  - There is no rescue by raising the settings within the pilot. An UNINFORMATIVE result is itself reportable.
- **(c) and (e): cost calibration, MEASURED.**
  - At the w that decides the reading, run one return at dev settings and ONE at production settings (order 20,
    tolerance 1e−24), from the same start point. That is ≈ 1 core-h.
  - Record the core-h ratio ρ_cost and the width ratio.
  - The projection on line 60 becomes: (0.03 / w_max_ok) × (dev core-h per pass) × ρ_cost × 1.5.
  - If (e) cannot be run inside the spend, the projection is stated as "dev-measured × assumed 5×, uncalibrated", and
    the reading is graded **no higher than PARTIAL**.
- **(d) The ladder is unchanged:** w ∈ {1e−8, 1e−6, 1e−4}, with n_seg ∈ {1, 20}. n_seg = 1 runs only at w = 1e−8 and
  at the w that decides.
- **(f) The drop order, fixed now.**
  - The planned passes are, in order:
    1. w = 1e−8, n_seg = 20: the main pass (c1, c2, c4), the c5 mutated-field pass, and the c3 sab pass;
    2. w = 1e−8, n_seg = 1 (the segmentation comparison);
    3. w = 1e−6, n_seg = 20;
    4. w = 1e−4, n_seg = 20;
    5. at the deciding w, n_seg = 1;
    6. the (e) calibration pair.
  - If the projected cumulative spend would exceed 12 core-h, these are dropped, in this order and only these:
    - **(f1)** item 5 (n_seg = 1 at the deciding w);
    - **(f2)** item 3 (w = 1e−6; the ladder goes from 1e−8 straight to 1e−4);
    - **(f3)** item 2 (n_seg = 1 at w = 1e−8).
  - **Never dropped:** the main pass, the controls c1–c5, and the (e) calibration pair. If (e) itself would not fit,
    the rule in (e) applies.
  - **12 core-h stays pause-and-report:** on reaching it, pause my own PIDs and tell the Bridge. Never kill.
  - If the pilot is still short after (f1)–(f3), the Bridge decides on more spend. Nothing is cut silently beyond this
    list (Sumit's rule: ask, don't ration).
- **Unchanged:** the 25% check-in at 3 core-h, and the kill date 2026-12-06 18:00 IST.
