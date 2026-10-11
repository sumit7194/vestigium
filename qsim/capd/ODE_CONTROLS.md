# CAPD ODE controls: rigorous enclosures against exact solutions

**Registered 2026-10-11.**
- **Timing disclosure:** this file was committed while the run was already in progress. At that point the real
  tests R1–R4 had finished, and I had run the checker on them: all contained. No complex monodromy result (M1–M5,
  control ii) existed yet.
- The rules below were written before any result and were not changed afterwards.

**Scope (user, via the bridge):** for paper v1, CAPD's job is (1) these ODE controls and (2) the third, Arb-free
replay of the Morales–Ramis certificates. The chaos-proof controls (Hénon–Heiles, Kerr) are phase 2, so they are
deferred, not dropped. The controls below are therefore chosen to exercise exactly what the replay needs:
- complex linear ODEs transported around circular loops, with the loops written as exact rational (stereographic)
  parametrisations, since trig is banned in proof formulas;
- composition of loop matrices;
- the trace and determinant invariants.

They also cover plain real C0 and C1 (variational) enclosures.

## Setup

- **Engine:**
  - CAPD 2f06098 `MpIOdeSolver` + `MpITimeMap` on MPFR, under the proof guard (`tests/guard_build.sh`, watchdog,
    `require_finite_all` on every output).
  - Vector fields are C++ functors (`capd::autodiff::Node`), so there are no formula strings. Non-representable
    constants enter as interval parameters (e.g. 11/12 as `MpInterval(11)/12`).
  - Precision 256 bits, Taylor order 30, CAPD's own step control.
- **Output:** every enclosure endpoint, exact (%Ra hex).
- **Checker:** `ode_controls.py` with python-flint/Arb at 1024 bits. It encloses each exact value and requires
  CAPD's enclosure to contain it **certainly**.

## The tests

**Real C0 and C1.**
- **R1, harmonic oscillator** x′ = y, y′ = −x. Initial box (1, 0) ± 10⁻²⁰, times t = 1, 10 and 100. The exact flow
  is a rotation, which is linear, so the image of the box is the hull of the images of its 4 corners. All 4 corner
  images plus 16 random interior points must be contained.
- **R2, x′ = x²**, x₀ ∈ [1/2, 1/2 + 10⁻²⁰], t = 1.5 (blow-up at t = 2). The exact solution x₀/(1 − x₀t) is
  monotone in x₀. Check:
  - both endpoint images are contained;
  - C1: the CAPD derivative enclosure contains ∂x/∂x₀ = 1/(1 − x₀t)² at both endpoints and at 8 interior points.
- **R3, Hopf normal form** x′ = x − y − x(x² + y²), y′ = x + y − y(x² + y²), box (1/2, 0) ± 10⁻²⁰, t = 2. Exactly,
  r(t) = (1 + (r₀⁻² − 1)e⁻²ᵗ)^(−1/2) and θ(t) = θ₀ + t. The 4 corner images and 16 interior images must be
  contained (a necessary condition).
- **R4, C1 of the harmonic oscillator** at t = 1 and 10: the enclosure must contain the rotation matrix
  [[cos t, sin t], [−sin t, cos t]].

**Complex monodromy (the replay's job).** The state is the complex 2×2 fundamental matrix Φ, written as 8 reals,
with Φ(base) = I and Φ′ = t′(s)·A(t(s))·Φ.
- **Loop parametrisation.** A loop of centre c and radius r runs counterclockwise from the base point c + r, in
  three charts:
  - t = c + r·((1 − s²) + 2is)/(1 + s²) for s ∈ [0, 1];
  - t = c − r·((1 − u²) + 2iu)/(1 + u²) for u ∈ [−1, 1];
  - the first chart again for s ∈ [−1, 0].
  The chart joints c ± ir are exact.
- **M1, Euler equation** y″ + (p/t) y′ + (q/t²) y = 0 with exponents r₁ = 1/3, r₂ = −1/4, so p = 1 − r₁ − r₂ = 11/12
  and q = r₁r₂ = −1/12. Exactly:
  - tr M = e^{2πi/3} + e^{−iπ/2};
  - det M = e^{2πi(r₁+r₂)} = e^{iπ/6};
  - tr² / det is checked too (the certificate's quantity).
  - Loops: (c, r) = (0, 1) based at 1, and (1/4, 3/4) based at 1.
- **M2, homotopy invariance.** The two M1 loops both encircle 0 once from the same base point 1, so they are
  homotopic. Their matrices must have overlapping enclosures, and the commutator [M_A, M_B] must enclose I
  (tr = 2).
- **M3, the double loop** (0, 1) twice: tr(M²) = e^{4πi/3} + e^{−iπ} exactly.
- **M4, a loop with no singularity inside**, (c, r) = (2, 1/2) based at 5/2, for the M1 equation: M = I exactly.
- **M5, Airy** y″ = t y (entire) around (0, 3) based at 3: M = I exactly. This tests transport with large growth.

**What counts as correct.** Every exact value (an Arb ball at 1024 bits, refined to 4096 on ambiguity) lies certainly
inside the CAPD enclosure; for a matrix, every entry. A single failure **FAILS** the controls.

**Fired controls, which the checker must reject:**
- **(i) Collapse:** each CAPD result interval is collapsed to its upper endpoint, and the collapsed results must
  fail. In each test at least one value must be rejected, and in total at least 90% of the values that CAPD did
  not enclose exactly.
- **(ii) Wrong equation:** M1 is integrated with p perturbed by 10⁻²⁰. Its trace enclosure must certainly EXCLUDE
  the exact trace of the unperturbed equation. The shift is about 10⁻²⁰ against widths of about 10⁻⁶⁰.

Outcome: to be appended below after the run, unchanged rules.
