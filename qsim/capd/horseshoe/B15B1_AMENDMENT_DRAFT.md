# B15b-1 DRAFT, revision 2 (2026-10-24): plunging orbits and step-size collapse in the compiled B15 maps

**Status: DRAFT. Not registered.** Revision 2 takes in the Bridge's review of revision 1, which proposed certifying
plunges with Kerr's radial quartic. A correction to that review is marked "Correction". The draft goes to the user
for an OK. No B15b gate except G2 has run; G2 is unaffected, because all its points return.

## What was found

A development check of two returns (kerr_rs_cross.py, 100 points, n = 2, tmax 4000; not a registered gate) hung
for over an hour.

- **The point:** index 44 of that sample, w = (1.84065670, 5.39481249e-4). The first return is fine (T = 696.8). Its
  second return plunges toward the horizon.
- **Diagnosis:** scipy DOP853 with MNFlow's own field and tolerances:
  - x falls to 1.000000 and p_x to −6.9e10;
  - the step size collapses to 1.5e-12 at t ≈ 617;
  - solve_ivp stops with status −1, "Required step size is less than spacing between numbers".
- **Why it hangs:** x = 1 is a coordinate singularity of this chart. The integration cannot pass it, so t never
  reaches tmax, the h < 1e-300 guard never triggers, and both compiled maps loop.
- **What MNFlow does:** it returns None ("no return") for this orbit, and it gets there through an integrator
  FAILURE (t_events is empty after status −1).

**Finding about the registered reference, and a limitation of the running Python B15.** MNFlow maps EVERY scipy
failure to None, which is the geometric statement "no return", plunge or not. The Python B15 run (b15_kerr.py,
PID 24176, non-checkpointed, to be stopped at the macOS update) therefore treats any non-plunge integrator failure
as geometry, silently. Its in-memory state cannot be audited. This is stated as a limitation of that run's results.
MNFlow itself is not changed, since B15 registered it.

## Semantics: unchanged from MNFlow, except for WHY "no return" is given

The registered semantics stay as they are: integrate until the next upward crossing of y = 0, or until the
integration cannot continue.

**Correction to revision 1 and to the review's (a).** A trigger at x − 1 < 0.05 would CHANGE the semantics:

- an orbit inside x < 1.05 can still cross y = 0 upward before it reaches the horizon;
- MNFlow counts such a crossing as a genuine return;
- a 0.05 trigger would turn it into "no return".

So there is no domain threshold. The trigger is the step-size collapse, which is the same point at which MNFlow
gives up. The certificate then justifies "no return" for that orbit, or the call fails.

**P1. Step-size collapse.**

- If an accepted step has h < 1e-14·max(1, |t|), the library stops and returns −2 ("collapsed"), together with the
  state at the collapse.
- −1 keeps its registered meaning: an E2 or E5 check failed.
- The h < 1e-300 guard stays as a backstop and returns −1.

**P2. The plunge certificate (Kerr only; exact rational arithmetic).** It is run by the adapter on every −2.

- **Constants from the START of the call, exactly.** The integrated orbit starts at the doubles (x0, 0, px0, py0),
  with py0 being the lifted double the integration actually used. Its constants are exact rationals of those
  doubles: E and L (the B15 parameters), μ² = −2H(start) and Q(start). There is no dependence on integration drift.
- **The orbit's position from the collapse state.**
  - r_c = M + k·x_c, and the margin is r₁ = M + k·(x_c + δ), where M + k = r₊ = 128 exactly, since k = 39.
  - δ = max(1e-6, 100 × the largest G4-measured state error) covers the integration error of the non-rigorous
    map. It is derived from G4, not chosen, and fixed before the run.
  - A fixed 0.01 margin was considered and rejected. In (ii) it would fail every plunge with |y_c| < 0.01, which is
    about 1% of them, each as a run-stopping HARNESS-ERROR, for an error that is really around 1e-10.
- **(i) No turning point.** R(r) > 0 on [r₊, r₁], where
  R(r) = [E(r² + a²) − aL]² − Δ[μ²r² + (L − aE)² + Q].
  - It is certified twice, independently, and both must certify:
    - a Sturm root count of 0 on [r₊, r₁] (sympy, exact rationals);
    - an interval evaluation by bisection (mpmath.iv), down to 2⁻⁴⁰ of the interval.
  - With ṙ < 0 at the collapse (the sign of p_x), the orbit reaches r₊ without turning.
- **(ii) No section crossing before the horizon.** The certificate in (i) proves a plunge, not "no return": the θ
  motion could still cross y = 0 between r_c and r₊. In Mino time λ the motions separate, so this is bounded:
  - the remaining Mino time is Λ ≤ (r₁ − r₊) / min over [r₊, r₁] of √R (interval bound);
  - |dy/dλ| ≤ √(Q + a²·|E² − μ²|).
  - Certified "no return" requires |y_c| > Λ·√(Q + a²|E² − μ²|) + δ, with the same δ for the state's error.
- **(iii) The certifier's dependencies.** The certifier uses the convention mapping of G0b-field (x ↔ r, y ↔ cos θ,
  p_x = k·p_r, the source's (E, L) and the w0 shift ↔ Kerr's (E, L_z), and the SIGN of a). R depends on a·L and
  a·E, so the sign matters here, whereas G0b-field's Q only sees a². Hence a new gate:
  - **G0c (exact):** at 20 random rational points, as in G0b-field, (Σ·k·ẋ)² = R(r) exactly, with
    Σ = r² + a²y² and ẋ from the source's field. This validates the E/L/a mapping, the sign of a, and that the
    field's time is the one R refers to: if the field's time were regularised, the identity would fail.
  - The certifier may be used only after G0b-field and G0c pass.
- **Outcome:**
  - Both certifiers succeed on (i) and (ii): the adapter returns None (no return) to the frozen constructor, and
    logs the reason 'plunge-certified' with the start, the collapse state and the certificate data.
  - Anything else: MapCheckFailed (HARNESS-ERROR).

**P3. Diagnostics: every certified plunge seen in G1, G2 or G4, and in the run.**

- MNFlow from the same start, with its None ROUTE recorded.
- Optionally, the compiled orbit continued (diagnostic switch) to show x − 1 < 1e-3.

**P4. Reference None routes, in G1 and G4 (the review's (c), adopted).**

- Every MNFlow None is labelled by route: 'tmax' (sol.t reached tmax with no event), 'status −1', or 'other'.
- **Agreement:** MNFlow None via status −1 and compiled 'plunge-certified'. This agrees, with the reason logged.
  So does MNFlow None via 'tmax' and compiled 0 (tmax).
- **Every other combination** with a None on one side is a mismatch, and therefore a FAIL, as registered.

**P5. In the counted run.**

- The summary counts certified plunges and −1/−2 failures by kind. The expectation for uncertified collapses is 0.
- G6 gains a decision, "no return (certified plunge)", with the certificate's slack as its margin: the minimum of R
  over [r₊, r₁], and |y_c| minus the bound. A slack below its registered margins is already a −1, so G6 logs it for
  completeness.

## What it does not change

- MNFlow, and the frozen constructor's reading of None.
- Every registered B15b gate and criterion. G0c is added.
- **For the later MN work**, which is non-integrable and has no radial certificate: a threshold-plus-MNFlow fallback
  would need its own amendment then.
