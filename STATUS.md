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
- **MN chaos at β = 3/100: certified; v4 rerun identical; awaiting the Bridge** (`qsim/mn_homoclinic_spike/S2_RESULT.md`,
  PREREG A13.1).
  - A transverse homoclinic orbit to the r ≈ 16 periodic orbit, so the flow on that level is chaotic (h_top > 0,
    Smale–Birkhoff). Qualitative only: one β, no entropy value.
  - All four controls PASS:
    - Kerr does not certify;
    - Kerr's homoclinics form a family;
    - the sabotaged field changes the certificate;
    - the CKMJ L4 proof is reproduced.
  - **GRADE:** both lemmas read by a non-author (CORRECT) and A12 accepted.
  - **A12.9 hold:** its condition is met. The v4 (NaN-rule) rerun of every MN-side pass is identical to v3
    (2026-11-27 21:13, 5.67 core-h). Lifting "held" is the Bridge's call.
  - **Tier 1:** the Arb re-check of the decision arithmetic agrees on every verdict.
    - It counts only after the Bridge's non-author read.
    - Must-fail (m2), (m3) and (m5) fired, (m4) changed the margin, and (m1) did NOT fire: a case-design flaw,
      disclosed, with a post-hoc (m1p) that fires.
  - **Correction:** A2's "< 10%" cond-vs-n figure is ≤ 17% at β = 1e-2 (no decision depends on it).

## What is running
- Nothing.

## Next decision, and who makes it
- **The Bridge:**
  - the non-author read of tier1_check.py;
  - whether (m1p) stands in for (m1);
  - lifting the A12.9 hold.
- **Sumit:**
  - the push (local commits only);
  - Tier 2 (a second integrator; Kerr pilot first);
  - any compute beyond the spike's ≈ 20 core-h (now ≈ 19.7 used);
  - whether this goes into the chaos write-up (c67126e) and the outreach.

## Kill criteria (S2)
- Met: finished 2026-11-27 19:20 IST, before the 2026-11-29 15:00 kill date, at ≈ 11.4 of the 12 core-h cap.
- The A13 rerun was 5.67 of 7 core-h, finished 21:13.
- No further runs are planned.

## Parked (Sumit's call to reopen)
- These are listed in the open-threads note: the CHL sub-45° amendment, the MN/TS outreach package, the Lean
  equatorial glue, A8, the corner systematic and H3.
