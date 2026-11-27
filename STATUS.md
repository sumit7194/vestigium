# Quantum: STATUS (one page; updated only on change)

Last change: 2026-11-27, Claude Opus 5.5 (office "Quantum"). The full record lives in the registrations and write-ups
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

## What is running
- Nothing. No Quantum jobs on the Mac mini or the Air.

## Next decision, and who makes it
- **The Bridge reads the S2 amendment** (`qsim/mn_homoclinic_spike/PREREG.md`, A1–A10) and says go or no.
- On go: a slot request, then S2-0, the cost gate: one rigorous return. It projects S2's total.
- S2 is one rigorous attempt to prove a transverse homoclinic orbit for MN at β = 3/100. That would mean h_top > 0,
  qualitative.

## Kill criteria (S2)
- **STOP** in any of these cases:
  - S2-0 projects more than 5 core-h (×3 outside view ≤ 15) without a re-gate;
  - any stage or control fails: (i) Kerr must not certify, (ii) Kerr non-isolation, (iii) sabotage must fire,
    (iv) the CKMJ L4 reproduction;
  - the total exceeds 15 core-h;
  - it isn't done by **2026-11-30 24:00 IST**, or 2 days after the go, whichever is earlier.
- **Check-in** at 25% of the projected cost: a re-gate if the projection is more than 2×.
- **Good enough:** a certified transverse homoclinic plus all 4 controls. Then write up and stop: no other β and no
  entropy bound.
- **On STOP:** a write-up, and the MN chaos question closes for good unless Sumit opens a new route.

## Parked (Sumit's call to reopen)
- These are listed in the open-threads note: the CHL sub-45° amendment, the MN/TS outreach package, the Lean
  equatorial glue, A8, the corner systematic and H3.
