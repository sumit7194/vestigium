# Quantum: STATUS (one page; updated only on change)

Last change: 2026-11-27 19:30 IST (S2 done), Claude Opus 5.5 (office "Quantum"). The full record lives in the registrations and write-ups
named below. This page is the plain summary (fleet practice 3, 2026-11-27).

## What we know (with grades)
- **Hénon–Heiles horseshoe: CERTIFIED** (CAPD, MPFR intervals).
  - HH-PRIMARY: 7/7 coverings, h_top ≥ 0.3222846.
  - HH-SECONDARY: 6/6, h_top ≥ 0.2811996.
  - This reproduces Arioli & Zgliczyński 2001, and it is the positive control of the pipeline.
- **MN (bumpy Kerr) chaos.**
  - First-order Melnikov in β: CERTIFIED non-zero and non-degenerate (Arb). L2 = −4.775e-5 at (M, a) = (5, 3),
    r_u = 16.
  - Morales–Ramis/Ziglin obstructions (non-integrability): CERTIFIED on the axis and the equator.
  - **No fixed-β chaos certificate yet.** The covering route was STOPPED (d9f9ad9): about 18,000× over budget.
- **Kerr negative control (covering route): UNDECIDED, ended.** 7 edge records, all with 0 fails, are kept. The
  remaining chunks were projected at 21–61+ days each and ended after the MN STOP.
- **The chaos thread was CLOSED 2026-11-27** with a write-up: `qsim/capd/horseshoe/CHAOS_PHASE2_WRITEUP.md` (c67126e).
  It is reopened ONLY for the spike below.
- **MN transversal-homoclinic spike, S1 (float): GO** (cc25e62).
  - The splitting matches the Melnikov prediction to +0.014% at β = 1e-4, and is linear in β.
  - The BVP is well enough conditioned to attempt (`qsim/mn_homoclinic_spike/S1_RESULT.md`).
  - Float only, not a proof.
- **MN chaos at β = 3/100: PROVED (within S2's scope)** (`qsim/mn_homoclinic_spike/S2_RESULT.md`,
  PREREG A13.1–A13.2).
  - A transverse homoclinic orbit to the r ≈ 16 periodic orbit, so the flow on that level is chaotic (h_top > 0,
    Smale–Birkhoff). Qualitative only: one β, no entropy value.
  - All four controls PASS:
    - Kerr does not certify;
    - Kerr's homoclinics form a family;
    - the sabotaged field changes the certificate;
    - the CKMJ L4 proof is reproduced.
  - **GRADE:** both lemmas read by a non-author (CORRECT) and A12 accepted.
  - A computer-assisted proof: every decision was re-evaluated independently from the dumped enclosures (Tier 1, Arb); the flow and derivative enclosures themselves rest on CAPD (an independent integrator re-check, Tier 2, has not been done).
  - The A12.9 hold is LIFTED (the Bridge, A13.2). The v4 rerun is identical to v3, and the Tier-1 checker was read
    CORRECT. Tier 1 does not cover (iv).
  - Must-fail: (m2), (m3) and (m5) fired; (m4) changed the margin; (m1) was mis-designed and did not fire; the
    post-hoc (m1p) fired and was accepted.
  - **Correction:** A2's "< 10%" cond-vs-n figure is ≤ 17% at β = 1e-2 (no decision depends on it).
- **MN chaos for ALL small β ≠ 0 (Step A): PROVED at its stated scope** (`qsim/mn_homoclinic_spike/STEP_A_MELNIKOV_GLUE.md`;
  maths only, 0 core-h).
  - The statement: for every 0 < |β| < β₀, β₀ not explicit, both signs, the R-symmetric homoclinic at ψ* = 3π/2 is
    transverse, so there is a horseshoe and h_top > 0.
  - What it rests on:
    - the certified Melnikov Stage 1–2 inequality: |L″(3π/2)| ≥ 1.22e-4;
    - the exact constant t′(0) = Υ²L″/(2k²F_t²) ≈ −1.003e-3, which matches the float data to 0.6% and was derived
      independently by Neon;
    - Robinson's Thm 3.4 (Contemp. Math. 198, 1996), with its hypotheses checked at source.
  - The Bridge read it (non-author): CORRECT. C1 passed with gaps g1–g4 disclosed; [CR-mel], the source of Lemma 3.8,
    was not read.
  - **Standing caveat (H1):** the MN field code (mn_codegen) is shared by S2 and by the Melnikov L2, until Tier 2a.
  - **Not given:** an explicit β₀. Step A does not reach S2's β = 3/100. Draft routes are in EXPLICIT_BETA_ROUTES_DRAFT.md.

## What is running
- Nothing.

## Next decision, and who makes it
- **Sumit:**
  - the push (local commits only);
  - **Tier 2a** (≈ 1 day, minutes of compute): an independent re-derivation of the MN field by a non-author, which
    removes the (H1) caveat from S2 and Step A at once. The Bridge recommends it;
  - **the route-1 pilot** for an explicit β* (≈ 3–10 core-h, ≈ 1 week of preparation; it measures the
    chain-wrapping blocker);
  - Tier 2b (a second integrator; Kerr pilot first);
  - any compute beyond the spike, which is CLOSED at ≈ 19.7 of ≈ 20 core-h;
  - whether this goes into the chaos write-up (c67126e) and the outreach.

## Kill criteria (S2)
- Met: finished 2026-11-27 19:20 IST, before the 2026-11-29 15:00 kill date, at ≈ 11.4 of the 12 core-h cap.
- The A13 rerun was 5.67 of 7 core-h, finished 21:13.
- No further runs are planned.

## Parked (Sumit's call to reopen)
- These are listed in the open-threads note: the CHL sub-45° amendment, the MN/TS outreach package, the Lean
  equatorial glue, A8, the corner systematic and H3.
