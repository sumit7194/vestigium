# S2 result: PROVED (within S2's scope). Every registered condition holds; both lemmas read by a non-author (CORRECT); A12 accepted; the v4 rerun is identical and the Tier-1 (Arb) re-check is read CORRECT (A13.1–A13.2)

Runs 2026-11-27, 15:54–19:20 IST, on the Mac mini (≤ 4 single-core jobs, nice 10, 23 MB each). MPFR-128, Taylor order
20, step tolerance 1e-24. Code: `capd/s2_main.cpp` (v3), `capd/s2_l4.cpp`, `s2run.py`, `l4run.py`. Outputs: `s2/`.
Registration: PREREG.md S2 AMENDMENT A1–A12. Written by Claude Opus 5.5 (office "Quantum").

## In plain words
- **What is proved.** For the Manko–Novikov spacetime at β = 3/100, (M, a) = (5, 3), on the registered energy level,
  the computer has proved the existence of a homoclinic orbit to the r ≈ 16 periodic orbit, along which the stable
  and unstable manifolds cross transversally. By the Smale–Birkhoff theorem, the geodesic flow on that level therefore
  contains a horseshoe: it is chaotic, with h_top > 0.
- **What it is not.** This is a qualitative result, at one β and one orbit family. No entropy bound is claimed.
- **The controls behaved as registered.**
  - The same code on Kerr (β = 0) does NOT certify transversality.
  - It certifies that Kerr's homoclinics form a continuous family, as integrability predicts.
  - A field with one β² term removed gives a different certificate.
  - The validator reproduces Capiński–Kepley–Mireles James's published L4 homoclinic proof.
- **Status:**
  - Both cone lemmas (A11, A12.3) have had a non-author read (the Bridge): CORRECT. A12 is accepted, with the
    wording items of A12.7.
  - BUT (A12.9): the MN-side certifying passes ran on v3, which did not finite-check the derivative enclosures as
    the CAPD trust rule requires.
  - **Proved (A13.2):** a computer-assisted proof: every decision was re-evaluated independently from the dumped enclosures (Tier 1, Arb); the flow and derivative enclosures themselves rest on CAPD (an independent integrator re-check, Tier 2, has not been done).
  - "Proved" had been HELD until those passes were rerun on v4.
  - **A13.1 (2026-11-27 21:13):**
    - The v4 rerun of every MN-side pass is byte-identical to v3 apart from wall times (5.67 core-h). Control (iv)
      was already rerun on v4, identical.
    - A second implementation of the decision arithmetic (python-flint/Arb, written from the registered formulas)
      re-derives every verdict from exact dumps and agrees.
    - The Bridge read the checker: CORRECT (A13.2), so its verdict counts. It covers MN and controls (i)–(iii), but
      not (iv), which rests on CAPD alone.
    - (m1) did not fire (the case was mis-designed; the checker behaved correctly). The post-hoc (m1p) fired, and
      the Bridge accepted it as a disclosed substitute.
- **How to read the controls.**
  - The margin is what persuades: MN's v_x/|v| = 3.1e-5 lies ~500× outside 0, compared with Kerr's enclosure
    (half-width ~6e-9 relative, containing 0).
  - Control (iii) shows that the field flows into the certificate. It is not a sensitivity test of transversality.

## Results (all rigorous; every listed inequality is evaluated in MPFR interval arithmetic)
| Stage | MN β = 3/100 | (i) Kerr β = 0 | (iii) sabotaged MN |
|---|---|---|---|
| S2-1 fixed point (Krawczyk) | CERTIFIED, r 1e-19 | CERTIFIED, r 1e-19 (Y 1.2e-21, Z 1.1e-8) | CERTIFIED, r 1e-19 |
| S2-2 cones (A11 lemma) | L 1.203e-2, μ ≥ 26.75, ν ≤ 0.820, δ* 3.735e-11 | L 1.036e-2, δ* 3.721e-11 | L 1.202e-2, δ* 3.735e-11 |
| S2-3 half BVP, m = 9, X ∈ R¹⁷ | CERTIFIED: Y 7.84e-16, Z 3.42e-4, r 1.20e-14 | CERTIFIED: Y 6.62e-16, Z 2.96e-4, r 1.02e-14 | CERTIFIED: Y 7.83e-16, Z 3.42e-4, r 1.20e-14 |
| symmetric point p = (x, p_x) | x ∈ [10.58222772208632, 10.58222772208635] | x ∈ [10.62704435657700, 10.62704435657703] | x ∈ [10.58222642457267, 10.58222642457270] |
| S2-4 v_x (tangent of W^u at p) | [1.12449e7, 1.13004e7]: **EXCLUDES 0** | [−2.24e4, +2.24e4]: **CONTAINS 0** | [1.12425e7, 1.12980e7] |
| v_px | [−3.5882e11, −3.5882e11]: excludes 0 | excludes 0 | excludes 0 |

- **MN:**
  - S2-1 to S2-4 all hold.
  - By the A1 lemma (v_px ≠ 0 and v_x ≠ 0), W^u ⋔ W^s at p.
  - The measured ratio v_x/|v| = 3.13e-5 matches the float prediction (3.1258e-5).
- **(i) must-not-certify: PASS.** The v_x enclosure contains 0, which is Kerr's exact value. S2-3 closes, as expected:
  the symmetric Kerr homoclinic exists.
- **(ii) positive non-isolation: PASS.**
  - The meeting system, with c free plus the phase row (A12.1), m = 9 per chain: Krawczyk CERTIFIED (Y 1.53e-15,
    Z 2.96e-4, r 2.35e-14), uniformly over x̂ ∈ [3.694790070132981, 3.694790070132984].
  - ∇K_r·g ∈ [36.2511, 36.2511] on the meeting hull, which is sign-definite, so α = 0 exactly (Carter: carter_check.py,
    an exact symbolic identity, with must-fire mutations).
  - Hence an arc of Kerr homoclinic points w_u(c(x̂)), c ∈ [5.1321e-12, 5.1791e-12]: not isolated.
- **(iii) sabotage must-fire: PASS.**
  - The sabotaged field (3β²(P3² − P2²)/R⁶ dropped from G) also certifies.
  - Its p-enclosure, x ∈ [10.58222642457267, 10.58222642457270], is DISJOINT from MN's,
    [10.58222772208632, 10.58222772208635] (a gap of 1.3e-6). The certificate changes.
- **(iv) positive control of the validator: PASS.**
  - CKMJ Thm 3 (PCRTBP µ = 1/2, E = 3): our bvp2 (n = 124 segments, X ∈ R⁴⁹⁷) is CERTIFIED (Y 1.24e-11, Z 0.163,
    r 5.91e-11).
  - Cones: L 8.12e-4, δ* 3.76e-8; endpoints |u|, |s| = 2.5e-8.
  - The certified orbit passes within 4.82e-10 of CKMJ's p̄, inside their r = 1.659e-9. It is their homoclinic.
  - Re-certified identically after A12.7 (w3): ρ′ is now included explicitly (s2/l4_iv/*_w3.*).

## Gates, conduct, budget
- **Trust and the field.**
  - Every binary is guard-built under trust rule 1: no double or double-interval CAPD types, and trig only through
    the range-checked functions.
  - S4 domain checks run on every step enclosure, with the crossing rule y(Tstop) < 0 certified and H = −1/2
    contained at every return.
  - The field generator is deterministic: the regenerated true header is byte-identical to gen/mn_field.h.
- **Spend** (by wall time on single cores):
  - S2 used ≈ 11.3–11.5 core-h of the 12 measured cap; the rigorous passes ≈ 10.
  - Of that, control (iv) used ≈ 1.1–1.3 core-h (mostly float set-up), under its 1.5 pause line.
  - Including the stopped v2 passes (≈ 3 core-h), the spike total is S1 ≈ 2 + S2-0 0.65 + S2 ≈ 11.4 ≈ 14 core-h.
    That is within the ≤ ~20 Sumit approved.
- **Kill date** 2026-11-29 15:00 IST: met (finished 2026-11-27 19:20).
- **No caps.** Stopped runs were my own verified PIDs, each disclosed: the fixed-c (ii), the v2 passes certain to
  fail, and an L4 float set-up with a noisy Jacobian. Every superseded run is kept in s2/.
- **The registered decisions never changed** after S2-0. Disclosed changes of method (A12):
  - (ii)'s free-c and phase formulation;
  - the v3 wrapping fix;
  - the L4 bvp2 formulation;
  - all controls rerun in the final code.

## What is NOT claimed
- No entropy value.
- No other β (no continuation).
- No statement about the S1-scale small-β regime beyond β = 3/100.
- Nothing about other orbit families.
- The Kerr items are controls, not new results about Kerr.
- **The field: independently re-derived (Tier 2a, AGREE, 2026-11-27).** A non-author derived it from Gair–Li–Mandel
  2008, and it matches gen/mn_field.h to its 160-bit floor at 97 orbit points × β ∈ {0, ±3/100}. The sabotage must-fail
  fired (tier2a/TIER2A_RESULT.md).
- **No second integrator (Tier 2b).** The flow and derivative enclosures rest on CAPD alone. Tier 1 covers only the
  decision arithmetic. Tier 2b is Sumit's call.
