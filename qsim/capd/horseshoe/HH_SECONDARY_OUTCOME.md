# HH-SECONDARY outcome: Hénon–Heiles at E = 1/6 on the B14 constructor's own sets (2026-10-19). **PASS**

**Registration and code:**
- registration: `PREREG_chaos_horseshoe_phase2.md` §6.2 SECONDARY and B14;
- constructor `hs_construct.py`, frozen at 1da283c;
- binary `hs_cover_v4` (source at e1f728a);
- B13 settings: adaptive bisection, depth caps 16 and 12, leaf caps 2¹⁶ and 2¹², checkpoints. MPFR 128 bits, order
  20, with the S9 in-flow energy check on.

**The sets** (exact rationals, rounded to 1e−10; `hh2_exact_checks.json`):
- N0 at Π₄ = (−0.24979, 0);
- N3 … N6 on the constructor's Π₄ homoclinic orbit (k_u + k_s = 8, angle 0.98).
- S8: all 10 pairs are exactly disjoint.

| Covering | Required? | Result | (a) leaves, max depth | Orientation | Return time |
|---|---|---|---|---|---|
| N0⟹N0 | yes | **certified** | 337, 2 | LR | [6.838, 7.436] |
| N0⟹N3 | yes | **certified** | 515, 5 | RL | [6.838, 7.436] |
| N3⟹N4 | yes | **certified** | 808, 4 | LR | [8.641, 8.912] |
| N4⟹N5 | yes | **certified** | 684, 5 | LR | [7.822, 8.353] |
| N5⟹N6 | yes | **certified** | 276, 1 | LR | [6.750, 6.956] |
| N6⟹N0 | yes | **certified** | 256, 0 | RL | [6.915, 7.111] |
| N6⟹N3 | optional | not a covering: a certified orientation failure in (b), as the sampled pre-check predicted | 256, 0 | — | — |

**Totals:** 4.4 core-hours. No piece failed in any required covering, and no box came near the depth caps.

**Consequence:**
- The required graph has cycles of lengths 1 (N0) and 5 (N0→N3→N4→N5→N6→N0) through N0.
- Its characteristic polynomial is x⁵ − x⁴ − 1 = (x² − x + 1)(x³ − x − 1).
- So ρ(A) is the plastic number 1.324717957…, and **h_top(P₁ | Inv) ≥ ln ρ = 0.2811996…**

**Wording (§6.2 SECONDARY):** "consistent with the published existence result" (AZ 2001, symbolic dynamics at
E = 1/6). The bound is weaker than AZ's ln 1.38028 = 0.3223 because the chain is shorter, with no N6⟹N3. This is the
expected direction, not a discrepancy.

**What it shows about the constructor.** From the system alone, the constructor found AZ's saddles exactly, and a
chain whose points sit next to AZ's M1 and M4. It then produced sets that certify rigorously on the first registered
ladder entry. This is the test the constructor needed before Kerr and MN.

**Caveat:** the ladder values and the required/optional split were fixed after non-rigorous exploration on HH
(disclosed in B14). The rigorous run came after that registration.
