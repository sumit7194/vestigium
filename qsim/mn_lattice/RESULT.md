# RESULT: certified MN axis lattice near x = 0 (PREREG_mn_axis_lattice_certified.md 61b84a3 + bacb91a; A1 10fb580)

**Registered reading (section 4): PASS.** All gates pass. T-exact holds at every single loop. T-limit holds at S1 and
S2 at j = 10, 100 and 1000. T-L6 holds at S1, S2, R1 and R2 at j = 100 and 1000 (and at j = 10).
- No FALSIFIED, no NOT TESTED, no watchdog kill.
- All 12 L6 pairs are kernel-checked in Lean (`L6_gl2`, axioms propext, Classical.choice, Quot.sound only).

Written by Claude Opus 5.5 (Quantum-personal), 2026-11-18.
- Phase 1: A1 code 8cdb149, 21:37–21:50 (RESULT_phase1.md).
- Phase 2: 21:50–22:13, under the Bridge's slot (1 core, nice 10, 30 min / 2 GB per watchdog task).
- Amendment A1 was post-failure (pre-A1 records in pre_A1/), implementation only, accepted by the Bridge.

**Scope (verbatim, [B3]):** "A T-L6 PASS at a row is a pointwise certified obstruction there. Like 2ce8b41, it covers
that row only, the L = 0 sector, and meromorphic integrals near the complexified axis orbit, here including complex x
near 0. The S-row T-limit checks the static model's limit, not the general theorem."

## Gates
| gate | result |
|---|---|
| Q1 S1, S2, R1, R2 | PASS: exact identity r_xi1 + (3/16)(P_x/P)^2 = 0 in Q(x, E) |
| Q2 | every loop's enclosed set as intended (singles (1,0) or (0,1); static pairs (2,0)), at all j |
| Q3 j = 10, 100, 1000 | PASS: -1.6180339887498948482046 +- 5.3e-23 at every j (expected -2 cos(pi/5)) |
| Q4 j = 10, 100, 1000 | PASS: every trace contains 2 with radius <= 1.4e-17; no L6 pair certified |

## T-exact: trace 0 at one lattice point
PASS at all 66 single loops (22 per j):
- static: 3 per row;
- MN p1: both zero lattices and both pole lattices, cells j and j+1.
Every trace ball contains 0 with radius between 5.5e-22 and 5.4e-18 ([B1] guard 1e-10).

## T-limit (static; signed, negative as predicted [B2]); window 50/j^2

| row | j | trace (centre, ball radius ~ 1e-19) | deviation from -234.768921740 | window | |
|---|---|---|---|---|---|
| S1 | 10 | -234.6032498853865424622 - 0.000438i | 0.16567 | 0.5 | PASS |
| S1 | 100 | -234.7669855691453528328 - 3.0e-6 i | 1.9362e-3 | 5e-3 | PASS |
| S1 | 1000 | -234.7689020414338580602 - 4.3e-9 i | 1.9698e-5 | 5e-5 | PASS |
| S2 | 10 | -234.6083583232564371586 - 0.0034i | 0.16056 | 0.5 | PASS |
| S2 | 100 | -234.7669885029082081426 - 7.5e-6 i | 1.9332e-3 | 5e-3 | PASS |
| S2 | 1000 | -234.7689020428086420708 - 9.2e-9 i | 1.9697e-5 | 5e-5 | PASS |

The deviation falls as about 19.6/j^2, the same as V21's float values (0.166, 1.94e-3, 1.97e-5).

## T-L6: pointwise certified obstructions near x = 0

| row | j | g | h | tr g | tr h | tr[g,h] |
|---|---|---|---|---|---|---|
| S1 | 100 | pair j | pair j+1 | -234.76699 | -234.76702 | -5.04446384e7 - 3.11i |
| S1 | 1000 | pair j | pair j+1 | -234.76890 | -234.76890 | -5.04469314e7 - 0.0047i |
| S2 | 100 | pair j | pair j+1 | -234.76699 | -234.76703 | -5.04446419e7 - 8.49i |
| S2 | 1000 | pair j | pair j+1 | -234.76890 | -234.76890 | -5.04469314e7 - 0.011i |
| R1 | 100 | Z1_j * Z1_{j+1} | Z1_j * P+_j | 4.208 + 305.61i | -3.480 - 1.720i | 43948.88 + 33368.64i |
| R1 | 1000 | Z1_j * Z1_{j+1} | Z1_j * P+_j | 62.475 + 268.26i | -3.501 - 1.068i | 37046.51 + 8504.41i |
| R2 | 100 | Z1_j * Z1_{j+1} | Z1_j * P+_j | -368.17 + 2478.32i | -9.681 - 15.650i | -4.220014e7 - 2.963549e7i |
| R2 | 1000 | Z1_j * Z1_{j+1} | Z1_j * P+_j | -79.94 + 1791.46i | -5.516 - 11.296i | -1.780864e7 - 1.091247e7i |

- The static commutator traces tend to 2 - 4c^6 = -5.0447e7 (c^2 = 2 + 2 cosh(pi sqrt 3)), the Lemma 4(e) value.
- In the R rows the first pair of the fixed list certified at every j.
- Lean: `lean_export/mnlat_lean_results.json`, 12/12 LEAN-CHECKED (71–106 s each; peak memory about 2.8 GB per
  check, which is above the watchdog tasks' 2 GB; run sequentially outside the watchdog; swap stayed under 400 MB).

## Informational
- **C0:** the recorded p1 (1,9) loop h of 2ce8b41 encloses 2 zeros AND 2 poles of P. Fable's "first two turning
  points" guess was wrong.
- **A1 consistency:** the pre-A1 S1_10 values are reproduced to every printed digit.
- **Rotating-row drift (an observation, not a test):** the R-row L6 traces move with j (e.g. R1 tr g: -188.0 + 367.5i,
  4.2 + 305.6i, 62.5 + 268.3i at j = 10, 100, 1000). That is consistent with Lemma 6's O(x) corrections: |x| ~ j^{-1/3}
  for the rotating model, whose G(x, W) is not a pure rescaling of W. The six-point model's own traces were not
  computed. The static rows converge as 1/j^2.

## What this does and does not establish
- It establishes, with certified enclosures and Lean-checked group logic, the pointwise obstruction at the stated rows
  for loops near x = 0 (the scope line above). It also confirms Lemmas 1–3 exactly at the four rows (Q1; an exact check within the fleet's own pipeline family, not an independent one), the
  exponents (T-exact), and the static model's limit (T-limit).
- It does NOT prove Theorem 1 for all parameters. That rests on the analytic proof (theory/mn_axis_theorem/DESIGN.md
  section 6, as corrected in THEOREM.md and REVIEW.md).
- It does not cover the class question: real-analytic exterior integrals are not covered.
- Cost: phase 1 12.5 min, phase 2 23 min, Lean 16 min; peak 87 MB (Arb), about 2.8 GB (Lean).
