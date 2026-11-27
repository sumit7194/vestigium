# S2-0 (cost and feasibility gate) result: P ≈ 5.1–6.5 core-h, in A10's RE-GATE band (5–14). Not proceeding.

Run 2026-11-27 on the Mac mini (1 core, nice 10, detached; the Bridge's S2-0 slot). Written by Claude Opus 5.5
(office "Quantum").
- Code: `capd/s2_capd.cpp` (guard-built under trust rule 1: GUARD OK, no double or double-interval CAPD types).
- Run logs: `capd/runs/`.
- Binaries:
  - `s2_capd` = the first build (default tolerance), sha256 e2ad2c39…;
  - `s2_capd_t` = plus the tolerance option (b0c1495c…, source `s2_capd_t.cpp`);
  - `s2_capd_t2` = plus the C⁰ point mode (012261ae…, source `s2_capd_t2.cpp` = `s2_capd.cpp`).
  - The ret() path is identical in t and t2.

## What was measured (all rigorous MPFR-128, Taylor order 20)
| Run | β | Set | Step tol | Steps | Wall | Result |
|---|---|---|---|---|---|---|
| smoke | 0 | fp (2.75, 0) ± 1e-10, C¹ | CAPD default (~1e-41) | 847 | 949 s | P(fp) ∋ fp; rt 107.61627; DP trace 26.905 = λ + 1/λ, det ≈ 1; rel DP width 7.4e-5 |
| tol | 0 | same | 1e-24 | 150 | 179 s | widths IDENTICAL to the default (5.3× faster) |
| tol | 0 | fp ± 1e-14, C¹ | 1e-24 | 150 | 184 s | rel DP width 7.4e-9 (linear in the box) |
| (a) cone box | 3/100 | fp ± 1e-7, C¹ | 1e-24 | 155 | 306 s | rel DP width 8.4e-2; P-hull ≈ 660× the box (crossing-time interval) |
| (b) long return | 3/100 | z₆ ± 1e-14, C¹ (τ ≈ 380.9) | 1e-24 | 319 | 593 s | rel DP width 1.15e-7; rt 380.92191 |
| (c) point | 3/100 | fp, a point, C⁰ | 1e-24 | 155 | 110 s | width 2e-21 |

- **Memory:** phys_footprint 23 MB per job (peak 23 MB).
- **Total spent in S2-0:** 2,321 s ≈ 0.65 core-h.

## What S2-0 changes in the design (all forced by the measurements; methods unchanged)
1. **Step tolerance 1e-24** (absolute = relative) for every S2 run. It is step control only, it is a double by CAPD
   design, and it is never a proof value. It is 5.3× faster with identical widths.
2. **Ball sizes.** DP widths scale linearly with the set, so the S2 balls must be ~1e-16 (rel DP width ~1e-9 per
   return; the v_x sign test then has a margin of about 3e3). That needs:
   - **s_u ≈ 2e-12** (two more fundamental domains, so m = 9 nodes), so that the cone-tail endpoint uncertainty
     L·s_u stays below 1e-16;
   - **δ = 1e-10** for the cone box (rel DP width ~8e-5, slope bound L ~ 1e-4);
   - **x̄ refined to ~1e-20** before the C¹ ball pass: one Newton correction from a rigorous C⁰ point pass (its
     midpoint), then a second C⁰ point pass for Y.
3. **Box images through C¹ mean-value forms, not C⁰ hulls.** The hull of P(box) is ~660× the box, dominated by the
   crossing-time interval. The covering edges of the cone step use P(edge centre) + DP(box)·(edge − centre).
4. **The double-interval fallback (A5) is not available.** It conflicts with trust rule 1 (the proof guard refuses
   double-interval CAPD types). It is dropped.

## Projection P (the remaining S2, by the measured unit costs)
- **Unit costs:**
  - β = 3/100: C¹ near-fp return 306 s, C¹ long 593 s, C⁰ point 110 s (long ≈ 213 s).
  - β = 0 (Kerr): ×0.59.
- **Per stage:**

  | Stage | Cost |
  |---|---|
  | MN chain: fp (C⁰ + C¹) + cone box (C¹) + 9 nodes × (C⁰ + C⁰ + C¹) | ≈ 1.65 h |
  | (i) the same at β = 0 | ≈ 0.97 h |
  | (ii) 2 chains × 9 nodes at β = 0, one uniform-contraction box | ≈ 1.7 h |
  | (iii) as registered (a full certificate for the sabotaged field) | ≈ 1.65 h |
  | (iii′) cheaper: F_sab at the true certified x̄, showing Krawczyk fails at every admissible r (9 C⁰ point passes) | ≈ 0.3 h |
  | (iv) L4 front end + CKMJ Thm 3 (PCRTBP; NOT measured) | ≈ 0.5 h (a guess) |

- **P (as registered, with the forced changes 1–3) ≈ 6.5 core-h.** With (iii′), **P ≈ 5.1 core-h**.
- With A10's ×3 outside view: 15–20 core-h.
- **Reading under A10:** P > 5 → the re-gate band (5–14). Report and wait for the Bridge. The (iii′) variant sits at
  the 5 line; whether it counts as the registered must-fire is the Bridge's call.

## What the numbers say about feasibility (apart from cost)
- **The Kerr smoke return is correct** in every check: the fixed point is contained, λ + 1/λ, det ≈ 1, and the return
  time.
- **Widths are linear in the set size**, with no superlinear wrapping over one return, even on the τ ≈ 381
  excursion. That rules out the premortem's main failure mode (MN over-widening blocking the sign test) at ball
  size ~1e-16.
- **Ballpark margins at the S2 ball size:** Krawczyk Z ≈ ‖A‖·(rel DP width) ≈ 1.7 × 1e-9; v_x sign test ≈ 3e-5
  against ≲ 1e-8.

## The audit-sweep +1 (the Bridge asked)
It is PREREG.md:123, "cond(DF) is independent of n", flagged by the "independent" text cue. On triage it is a
false positive: the claim is measured and quantified in the same line (λ^±1 shift, cond within 10% at all four
zeros, β = 1e-2).
**Correction (A13.1, 2026-11-27):** the regenerated artifact (a2_cond_shift.*) gives ≤ 17% at β = 1e-2 (two of
four zeros exceed 10%) and ≤ 7% at β = 3/100. The cue is still a false positive, but the "< 10%" figure was
overstated.
