# Pre-registration: certified monodromy on the MN axis lattice near x = 0 (certified C3, C0)

**Status: REGISTERED. The Bridge agreed on 2026-11-18 with three additions, folded in below (marked [B1], [B2],
[B3]). Nothing below has been run.** Branch `mn-axis-theorem` (worktree
`quantum-mnthm`), not main. Written by Claude Opus 5.5 (Quantum-personal session). It tests Fable 5.2's design
`fable_work/mn_general_theorem/DESIGN.md` (Theorem 1, sections 6.4–6.5 and 7). The Bridge's float check V21
(30231db) passed C1 and C2 and the static C3 limit. This run is the certified version, and adds a rotating row and C0.

## 0. What is being tested, and what is not

**Under test:**
- **T-exact.** At every simple zero or simple pole of `P = E^2 - mu^2 f(x,1)` (one lattice point), the local exponents
  of the axis normal form are 1/4 and 3/4. So the monodromy of a small loop around one lattice point has trace
  **exactly 0** in the normal form, at every j. This is an exact prediction of Lemmas 1–3, for both the static and
  the rotating case.
- **T-limit (static only).** For a loop around two consecutive lattice points, the trace tends to
  `-(4 + 2 cosh(pi sqrt 3)) = -234.768921740...` as j grows (Lemmas 4(e) and 6).
- **T-L6.** At large j, two certified loop matrices `G, H` near x = 0 satisfy the hypotheses of `L6_gl2`:
  `tr^2/det` outside [0, 4] for both, and `tr[G, H] != 2`.
  - Through the Lean theorem `L6_gl2` and Morales–Ramis Theorem 7, this is a pointwise certified OBSTRUCTION near
    x = 0 at that row. It does not depend on Lemma 6 or on the model. It is the certificate that DESIGN.md calls C6.
  - In the rotating case, where the six-point model has no closed-form trace, T-L6 is the test.

[B3] The S-row T-limit checks the static model's limit (Lemmas 4(e) and 6 in the static case), not the general
theorem.

**Not under test:**
- Lemmas 4(a)–(d) and 5 in general, and the claim "for all beta, E, mu".
- The Morales–Ramis step and the class of integrals. Those are for the review.
- A finite run proves nothing at other parameter values.

**Setup correspondence.** The claims tested are about the axis normal form of the MN geodesic flow at the stated
rows. The R rows run at that exact condition: the same metric package, the same exact r_xi1 builder, the same ia_hub
settings as 2ce8b41, with only the loops moved to the lattice near x = 0. The S rows run at the static condition
alpha = 0, which the general claim includes. Gate Q1 checks there, symbolically, that the equation used is the axis
normal form of that metric. So each row runs at the condition its claim names.

## 1. Rows

| row | metric on the axis | (beta, E, mu^2) | lattices near x = 0 (sigma = 2 beta/x^3) |
|---|---|---|---|
| S1 | static: `f0 = W (x-1)/(x+1)`, `W = exp(2 beta/x^3)` | (1/5, 1, 4) | zeros of P: `sigma ~ ln(E^2/mu^2) + i pi (2j+1)` |
| S2 | static, as S1 | (-1/3, 1, 9) | same form |
| R1 | MN p1 (M, a, beta) = (5, 3, 1/5), the package `mn_metric_components_p1.txt` | E = 1, mu^2 = 9 | zeros: `9W^2 + 144W + 25 = 0` (W ~ -0.1756, -15.82); poles: `W = +- 5i/3` |
| R2 | MN p1 | E = 1, mu^2 = 4 | zeros: `9W^2 + 64W + 25 = 0` (W ~ -0.415, -6.70); poles: `W = +- 5i/3` |

(The R-row lattice equations are the x -> 0 limits, used only to place loops. Rigour never depends on them.)

**The equation, per row:**
- **S rows:** the normal form `y'' = r y` with `r = -(3/16)(P_x/P)^2`, built exactly as P/Q with polynomials in x and
  `exp(2 beta/x^3)` (`ia_hub.RationalFn`, bad points 0 and -1). This is Fable's equation (2). V21 C2 checked it
  against the exact axis NVE for MN p1/p2, not for alpha = 0. For alpha = 0 an exact symbolic check is gate Q1 below.
- **R rows:** the existing certified pipeline's exact `r_xi1` from `qsim/mr_mn_axis.py` (`axial_nve` ->
  `reduced_forms_QxE`, built from the metric package). This is the same NVE that certified the four axial rows in
  2ce8b41, and it is independent of Fable's Lemma 1.

## 2. Loops (deterministic; all defined in the sigma-plane, then mapped)

Lattice points are located in floats: initial `sigma_j` from the table, `x = (2 beta/sigma)^{1/3}` (principal cube
root), then Newton on the numerator (or denominator) of P in mpmath at 50 digits. They are used only to place loops.

A loop is a circle in the sigma-plane: centre `s_c`, radius `rho`, 64 vertices `s_c + rho e^{2 pi i k/64}`, each mapped
to x by the same principal cube root. The loop in x is the closed polyline through the 64 images. Base points and the
paths to the loop entry points are likewise straight segments in sigma, sampled at spacing 0.25 and mapped.

**Enclosure is certified, not assumed.** For every loop, the zeros and poles of P inside the x-polyline are counted by
a certified argument principle (section 3, Q2). A loop whose certified count differs from the intended set is
reported and not used.

Loop types, at j in {10, 100, 1000}:
- **single(p):** centre at lattice point p, radius = 0.25 x the sigma-distance from p to the nearest other lattice point.
- **pair(p, q)** (static only): consecutive points of one lattice. Centre at the sigma-midpoint, radius 3 pi/2 (the
  points are pi from the centre, the neighbours 3 pi).
- **Base point (static):** `s_b = c_1 + i pi + 6`, with c_1 the centre of pair(x_j, x_{j+1}). It lies outside both
  pair circles, which have radius 4.71 and are at distance 6.77 from it.
- **Base point and paths (R rows).** In sigma the zeros lie on the lines Im = (2j+1) pi, and the poles at
  Im = (2j+1) pi +- pi/2.
  - Base point: `s_b = (max Re over the 8 points of cells j, j+1) + 3 + i ((2j+1) pi + pi/4)`.
  - Path to a target point t: vertical from s_b to Im = Im(t) + pi/4, then horizontal to Re(t), then straight to the
    entry point of t's circle. The pi/4 corridor keeps at least 0.78 from every lattice point.
  - Any path or loop that `ia_hub.transport` cannot certify (step-size underflow) is reported, and that element is not
    used.

## 3. Certified computations (Arb via python-flint 0.9.0, `qsim/ia_hub.py` unchanged)

Settings: ctx.prec 192 bits, Taylor N = 100, `MRHO2_MAX = 4`. Transport is `ia_hub.transport` along the mapped
polyline. Every accepted step is certified analytic, exactly as in 2ce8b41.

**Gates before any target number.** Each is all-or-nothing; a failure stops the run and is reported.
- **Q1 (equation, S rows).** The S-row r equals the axis normal form derived from the static MN metric. Build the
  alpha = 0 metric (`f = e^{2 psi}(x-1)/(x+1)` with omega = 0 and the static gamma), and run `axial_nve` ->
  `reduced_forms` on it, as for the R rows. Then check that `r_xi1 + (3/16)(P_x/P)^2` is identically 0 as an element
  of Q(x, E).
- **Q2 (argument principle).**
  - Along a polyline, the winding of an analytic g is certified by enclosing g on each segment's box.
  - Each enclosure must exclude 0, and must lie in an open half-plane through 0. A segment is bisected up to 12 times
    until this holds; if it cannot be made to hold, that loop is reported and not used.
  - The arg increments are summed with interval arithmetic and rounded to the integer they certainly determine.
  - Applied to the numerator and to the denominator of P separately, this gives #zeros and #poles inside.
- **Q3 (positive control at small x).** The axis prereg's G0(b) known-answer equation, a Riemann P equation pulled
  back by `exp(2/x^3)`. A loop around one root of `exp(2/x^3) = 1` at j = 10, 100, 1000 must give a certified trace
  ball containing `-2 cos(pi/5)`.
- **Q4 (negative control).** `y'' = r_0 y` with `r_0 = sigma_x^2/4 - (1/2){sigma, x} = 9 beta^2/x^8 + 2/x^2` (beta = 1/5).
  Its solutions are `exp(+- sigma/2) sigma_x^{-1/2}`, and `sigma_x^{-1/2}` is proportional to x^2, so every solution is
  single-valued and every monodromy is the identity. Its |r| near the lattice is of the same size as the S rows'.
  - Same loops as S1. Every loop's trace ball must contain 2, and no L6 pair may be certified.

**Targets.**
- **T-exact (S1, S2, R1, R2).** For every single(p) loop used at j in {10, 100, 1000}, the certified trace ball must
  contain 0.
  - Static rows: the points x_j, x_{j+1}, x_{j+2}.
  - R rows: both zeros and both poles in cells j and j+1.
  - **A ball that excludes 0 is a FALSIFICATION of Lemmas 1–3.**
  - **[B1] Vacuity guard.** A ball containing 0 passes only if its radius (the larger of the real and imaginary
    radii) is <= 1e-10. A larger ball containing 0 means the loop is NOT TESTED, which is neither PASS nor FAIL, and
    it is reported as such. The same guard applies to Q4 (target 2) and Q3 (target -2 cos(pi/5)).
- **T-limit (S1, S2).** For pair(x_j, x_{j+1}) the certified trace ball tr_j is reported.
  - **[B2] Signed prediction.** In this normalisation (the normal form y'' = r y, the same as V21's v-normalisation)
    the predicted limit is NEGATIVE: tr_j -> -(4 + 2 cosh(pi sqrt 3)) = -234.768921740. The window below is for the
    signed value. Each ball's centre and radius are reported, and so is the sign of its real part.
  - **PASS** if `|tr_j + 234.768921740| <= 50/j^2`, with the whole ball inside that window, at all three j.
  - V21's float deviations were 0.166, 1.9e-3 and 2.0e-5 at j = 10, 10^2, 10^3, so the window has a margin of 2.5 to 3.
    (V21's j index may be offset from this one by O(1), which moves the deviation by O(1/j^3).)
  - A ball outside the window at j = 1000 is a FALSIFICATION of the static model or of Lemma 6.
  - The window is not monotone-dependent; V21's VOID came from a monotonicity clause, and none is used here.
- **T-L6 (S1, S2, R1, R2), at j = 100 and j = 1000.**
  - Static rows: G = pair(x_j, x_{j+1}) and H = pair(x_{j+1}, x_{j+2}), with the common base s_b.
  - **R rows:** a fixed, ordered candidate list. From the 8 single loops of cells j and j+1 (order: Z1_j, Z1_{j+1},
    P+_j, P-_j, Z2_j, P+_{j+1}, P-_{j+1}, Z2_{j+1}), form all products of two distinct singles, in that order
    (28 elements). Test pairs in lexicographic order with `ia_hub.certificate` (SL2 form: both traces outside
    [-2, 2], commutator trace != 2). The first certified pair is the result. Products only: every single has trace 0
    by T-exact, so a single can never be loxodromic.
  - **PASS** at a row if a certified pair is found at both j = 100 and j = 1000.
  - Also exported in the Lean box format and checked with `lean/ZiglinCert` (`check BG BH`), as for the existing 52
    certificates.

**C0 (informational, no verdict).**
- Certified counts (Q2) of the zeros and poles of P inside the existing certified loop h of row p1, (E, mu^2) = (1, 9).
- That loop is in `qsim/mr_mn_row_7.json`: `g[0.0634+0.4514j, rad 0.1240]`, the 16-gon of `ia_hub.loop_points` with
  base 2.27485090742338 + 2.3598263413024894i, and the centre taken from that run's located list at full precision.
  If the full-precision centre cannot be recovered, the run re-derives it with the same deterministic locator.
- Also reported: the lattice labels (j, lattice) of the enclosed points, from their sigma-values.
- Expected, as an observation and not a test: the first two points of the W ~ -0.18 zero lattice.

## 4. Readings (fixed now)

| Outcome | Condition |
|---|---|
| **PASS** | Q1–Q4 pass; T-exact holds at every single loop; T-limit passes at S1 and S2; T-L6 passes at S1, S2, R1, R2 |
| **FALSIFIED** | T-exact fails at any loop (a certified trace ball excluding 0), or T-limit fails at j = 1000 with Q1–Q4 passing |
| **PARTIAL** | Gates pass and nothing is falsified, but some T-L6 row finds no certified pair, or T-limit fails only at j = 10. Reported per row with the certified balls; no further run on this reading alone |
| **INVALID** | Any gate fails, or the watchdog kills a task (a killed task is never a verdict) |

[B3] The result file states this scope line verbatim:
"A T-L6 PASS at a row is a pointwise certified obstruction there. Like 2ce8b41, it covers that row only, the L = 0
sector, and meromorphic integrals near the complexified axis orbit, here including complex x near 0. The S-row
T-limit checks the static model's limit, not the general theorem."

A T-L6 PASS at a row is a pointwise certified obstruction there. Like 2ce8b41, it covers that row only, the L = 0
sector, and meromorphic integrals near the complexified axis orbit. Here that orbit includes complex positions near
x = 0.

## 5. Resources and conduct

- One core, nice 10. Every task runs under `mr_watchdog.run_guarded` with a 30-min time limit per task and a
  2048 MB memory limit; there are 4 rows × 3 j-values plus gates and controls.
- **Run in two phases.**
  - Phase 1: the gates, plus j = 10 for all rows. Phase 1 is also the timing measurement.
  - If its projected total for phase 2 exceeds 30 min, a slot request with the measured cost goes to the Bridge
    before phase 2.
- Nothing touches the Z-sym run (PID 37679) or G3. Detached launch (tools/detach.sh) for anything over 10 minutes.
- Code: `qsim/mr_mn_axis_lattice.py` (new), reusing `ia_hub.py` and `mr_mn_axis.py` unchanged. Outputs go to
  `qsim/mn_lattice/`. The prereg, the code and any amendment are committed on this branch before the phase they
  govern runs.
- Amendments: at most two, each committed before the outputs it governs, with the reason. Anything after a failure is
  labelled post-failure.

## Amendment A1 (2026-11-18 ~21:45, Opus 5.5). POST-FAILURE: made after phase 1 (dc9894b) failed to test S2, R1, R2

**What phase 1 did, before this amendment.** Recorded in `qsim/mn_lattice/` and kept:
- **PASS:** Q1 at all four rows (the exact identity r_xi1 + (3/16)(P_x/P)^2 = 0 in Q(x, E), including MN p1);
  Q3_10 (trace -1.6180339887... radius 5e-21); Q4_10 (all traces 2, no L6 pair).
- **S1_10:**
  - T-exact PASS on Z_10, Z_11, Z_12 (radius at most 5e-18).
  - T-limit: pair trace -234.6032499 +- 6e-18, deviation 0.1657 within 0.5: PASS.
  - T-L6 certified (commutator trace -5.026e7).
- **C0:** 2 zeros and 2 poles of P lie inside the recorded p1 (1,9) loop h. That is NOT "the first two turning
  points" as DESIGN.md section 5 guessed. Informational.
- **S2_10:** crashed in the float locator (Newton in x diverged), before any number.
- **R1_10, R2_10:** no element certified. Two causes, found by diagnosis on one failure point (no target number
  was produced):
  - (i) The float locator (Newton in x) sent the R1 Z2 lattice to the real points x = -1.025 and 1.293. The base
    point was therefore placed on the true Z2_10, and every R1 path ran through it.
  - (ii) `ia_hub.upper()` turns ball bounds into Python floats. Near x = 0.16 the Taylor coefficients of
    exp(2 beta/x^3)-type terms of the R-row r_xi1 exceed 1e308 at order 100. So `upper` returns inf, and every step
    is refused, even where the denominator is far from zero: there Q(x) = 1.69 + 13.95i, and sup_bound succeeds at
    radius <= 1e-5. The S rows have lower powers of W and stayed under the limit at j = 10; at j = 100 and 1000
    every row would hit it.

**Changes. These are implementation changes only; tests, rows, loops, windows and readings are unchanged.**
- **A1.1 Locator.** Newton in sigma instead of x. The function is the same (the numerator or denominator of P at
  x(sigma), x(sigma) = principal cube root of 2 beta/sigma), at 50 digits. It is still float-only and places loops
  only. The Q2 counts still certify every enclosed set.
- **A1.2 Local rescaling.** Every transport, including Q3 and Q4, runs in a local variable `u = (x - x_c)/eps`, where
  x_c (complex) and eps > 0 are exact rationals fixed once per task:
  - x_c = x(sigma_c), with sigma_c the mean sigma of the task's lattice points;
  - eps = |x_c|/(3|sigma_c|), the length over which sigma changes by about 1.
  The equation becomes `y_uu = eps^2 r(x_c + eps u) y`, exact, built by symbolic substitution into the same P/Q.
  The u-monodromy of a loop equals `D^{-1} M_x D` with `D = diag(1, 1/eps)`, a conjugation that is the same for
  every loop of the task. So traces, determinants, commutator traces, the L6 hypotheses and every ball test are
  unchanged in meaning. Lean exports carry the u-frame matrices: a conjugate representation, so `L6_gl2` yields the
  same group statement.
- **Re-run.** All of phase 1 is re-run with A1 code, gates included. Both the pre-A1 phase-1 records above and the
  A1 records are kept and reported. A1 counts as the first of the two allowed amendments.
