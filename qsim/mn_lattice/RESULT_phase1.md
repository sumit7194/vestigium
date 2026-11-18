# Phase 1 result: certified MN axis lattice (PREREG_mn_axis_lattice_certified.md, 61b84a3 + bacb91a; Amendment A1 10fb580)

Run 2026-11-18 21:37–21:50 with the A1 code (8cdb149), detached, nice 10, every task under mr_watchdog (30 min / 2 GB).
Written by Claude Opus 5.5 (Quantum-personal). Pre-A1 records: `pre_A1/`.

**Scope (verbatim, [B3]):** "A T-L6 PASS at a row is a pointwise certified obstruction there. Like 2ce8b41, it covers
that row only, the L = 0 sector, and meromorphic integrals near the complexified axis orbit, here including complex x
near 0. The S-row T-limit checks the static model's limit, not the general theorem."

| check | result (all certified Arb balls, 192 bits, N = 100) |
|---|---|
| Q1 S1, S2, R1, R2 | PASS: r_xi1 + (3/16)(P_x/P)^2 = 0 identically in Q(x, E). This is the pipeline's own exact NVE, static alpha = 0 and MN p1 at both levels |
| Q2 | every enclosed set was as intended: singles (1,0) or (0,1); static pairs (2,0) |
| Q3_10 | PASS: trace -1.6180339887498948482046 +- 5.3e-23 (expected -2 cos(pi/5)) |
| Q4_10 | PASS: all four traces contain 2 with radius <= 1e-14; no L6 pair certified |
| T-exact, j = 10 | PASS at all 22 single loops (S1 x3, S2 x3, R1 x8, R2 x8: both zero lattices and both pole lattices). Every trace ball contains 0 with radius between 5.5e-22 and 5.4e-18 ([B1] guard 1e-10) |
| T-limit S1, j = 10 | PASS: pair trace -234.6032498853865424622 +- 7.5e-20 (real part NEGATIVE, as predicted [B2]); deviation from -234.768921740 is 0.16567 + 0.00044i; window 0.5 |
| T-limit S2, j = 10 | PASS: -234.6083583232564371586 +- 4.9e-20 (negative); deviation 0.16056 + 0.0034i; window 0.5 |
| T-L6 S1, j = 10 | certified: tr g = -234.6032 (pair j), tr h = -234.6300 (pair j+1), tr[g,h] = -50263411.665345 - 188.356618i (+- 4e-7) |
| T-L6 S2, j = 10 | certified: tr[g,h] = -50268755.342668 - 3420.526162i |
| T-L6 R1, j = 10 | certified at the first pair: g = Z1_10 * Z1_11, tr = -187.9788 + 367.5412i; h = Z1_10 * P+_10, tr = -3.0028 - 3.5160i; tr[g,h] = 654.219 + 136912.710i |
| T-L6 R2, j = 10 | certified at the first pair: tr g = -1766.5415 + 4992.4694i, tr h = -26.7487 - 30.7241i, tr[g,h] = -2.810844e8 - 2.330810e8i |
| Lean export | lean_S1_10, lean_S2_10, lean_R1_10 and lean_R2_10 written, read-back OK (u-frame matrices) |

**[Bridge] C0 (informational):** the recorded p1 (1,9) certified loop h of 2ce8b41 (centre 0.06341544 + 0.45142067i,
re-derived by the recorded locator; radius 0.12398 matches the record) encloses **2 zeros AND 2 poles of P**: one period
of the rotating lattice. Fable's DESIGN.md section 5 guess, "the first two turning points", was wrong. The independent
review (theory/mn_axis_theorem/REVIEW.md, O6) found the same.

**[Bridge] A1 consistency:** the pre-A1 S1_10 passes (pre_A1/S1_10.json, original x-frame code dc9894b) are kept, and
the A1 re-run reproduces them:
- pair trace: pre-A1 -234.60324988538654246 +- 5.6e-18 vs A1 -234.6032498853865424622 +- 7.5e-20;
- commutator: pre-A1 -50263411.6653 - 188.3566i vs A1 -50263411.665345 - 188.356618i;
- all overlapping, with the same centres to every printed digit;
- single traces contain 0 in both runs.
This checks that the u-rescaling (a fixed diagonal conjugation) changes nothing.

**Not established by phase 1:** j = 100 and j = 1000 (phase 2), the general theorem, and the class of integrals (see
REVIEW.md). The reading of the prereg's section 4 is made only after phase 2.

**Cost:** total 12.5 min. S rows 13–15 s; R rows 315–339 s (6,200–6,700 certified steps); Q tasks about 3 s each.
