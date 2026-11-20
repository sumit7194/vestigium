# TS capture edge: C-I1 and C-I2 under Arb (pre-registration)

Status: REGISTERED, 2026-11-20, under the plan of record (TheBridge/recipes/TS_CAPTURE_EDGE_PROOF_RECIPE.md v1.1,
item C-I1/I2). It is committed before any code. Written by Claude Opus 5.5 (session "Quantum").
- **Independence.** The checks are implemented from the STATEMENTS in TheBridge/falsification/V24_ts_capture_edge_lemmas/
  PREREGISTRATION.md, not from the Bridge's code. The Bridge's results are compared only after ours are sealed (committed).
- **Outputs.** By the Bridge's decision (recipe #1, option b), the code is committed here, and the OUTPUTS go to the
  gitignored qsim/scratch/ts_capture/ and to the Bridge only.

## Setup correspondence
The claims are Fable's I1 and I2 for TS δ = 2 at p = 4/5, q = 3/5 (ts45), σ = 1, E = 97/100, L = 41/8, μ = 1, as used
in Lemma L3′. These checks run at exactly that metric and level.

## Object
- **Metric.** quantum's own TS2 package from ansatz: conjecture_machine/data/sealed/TS2_for_quantum/
  ts2_metric_components_t1o3.txt (p = 4/5, q = 3/5), read with sympy as mr_ts2.py does, σ = 1. Only that metric file is
  opened; the sealed prediction file is NOT opened.
- **The potential.** F = g_xx (x² − 1), W = g^{TT} E² − 2 g^{Tφ} E L + g^{φφ} L² (inverse metric), and
  V = ½ F (W + 1), with s = y².
- **Gate S0 (exact).** V(x, y) = V(x, −y), symbolically, so that V is a function of (x, s). Also: the conformal-flat
  identity g_xx (x² − 1) = g_yy (1 − y²), by sympy cancellation.

## Checks (Arb, python-flint 0.9.0, 128 bits; recursive bisection in (x, s), depth limit 24)
- **The Hill test.** The axis s = 1 makes V singular (the g^{φφ} L² term), so a box is OUTSIDE Hill's region if
  G = (1 − s) V has an enclosure > 0. G has the same sign as V for s < 1 and extends through s = 1; this is stated, not
  assumed: G's formula is cancelled symbolically, so it has no (1 − s) denominator.
- **I1.** On [1.5, 9.49] × [0, 1]: every box is decided, either outside (G > 0) or with ∂V/∂x > 0 (enclosure).
- **I2.** On [9.3, 77.1] × [0, 1]: every box is decided, either outside or with ∂V/∂s > 0.
- **PASS:** 0 undecided boxes. We report the box counts and the minimum certified lower bound of the derivative on
  decided Hill boxes.
- **FALSIFIED:** a box whose enclosure proves the wrong sign (derivative < 0) while it is certainly inside Hill's
  region (G < 0).
- **INCONCLUSIVE:** undecided boxes remain at the depth limit, with no proven violation.

## Negative controls (each must show a failure, i.e. undecided or violating boxes, before the target is believed)
- I1 extended to x ≤ 9.6 (V24 reports a failure beyond 9.4995).
- I2 with the sign requirement reversed (∂V/∂s < 0).

## Verdict
- **CONFIRMED-ARB** if S0 holds exactly, I1 and I2 PASS, and both negative controls fail.
- Otherwise the verdict is named as above.
- The comparison with the Bridge's V24 numbers (box counts, minima) is made only after this verdict is committed to the
  Bridge.

## Resources
1 core, nice 10, minutes. No slot is needed (< 30 min).

## Recorded result of the registered run (depth 24), 2026-11-20; outputs in scratch, sent to the Bridge
- **S0:** both identities exact (flat, even in y), and G has no axis pole.
- **I2:** PASS, 0 undecided, 0 violations.
- **I1:** INCONCLUSIVE. 9017 undecided boxes and 0 violations; every undecided box shown lies at x ∈ [9.488, 9.49],
  s < 0.005. The float margin there is small: min ∂V/∂x on Hill is 3.4e-3 at x = 9.49.
- **Both negative controls fail,** as they must.
- **Verdict as registered:** INCONCLUSIVE (I1).

## Amendment A1 (POST-RESULT, 2026-11-20, Opus 5.5; made after seeing the depth-24 outcome above, and labelled as such)
- **What changes:** the depth limit for I1 goes from 24 to 40. Nothing else: the same boxes, split rule, Hill test,
  derivative, sign and PASS rule.
- **Why:** the undecided set is a thin strip at the I1 domain's own edge (x → 9.49, near the equator), where the true
  margin is about 3e-3 and the natural interval extension needs smaller boxes. This only lets the bisection go deeper;
  it cannot turn a violation into a pass.
- **Disclosure:** this is post-result. The registered depth-24 verdict stays INCONCLUSIVE on record, whatever A1 gives.
