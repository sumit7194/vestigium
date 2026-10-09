# TS δ=2 equatorial real-motion check (2026-10-10), `qsim/ts_bound_orbits.py`

This is a pre-registration aid for the TS obstruction-at-chaos-levels stage. It is not a verdict.
Method: on y = 0, xdot² = g^xx·(−μ² − V₀), from ansatz's WP components at σ = 1. Real roots are isolated
exactly, factor by factor over ℚ. Allowed intervals are classified as BOUND, PLUNGE (reaches the ring) or ESCAPE.

**Control (Kerr-WP, p = 4/5, m = 5/4).** At E = 0.97, L = −5 (= −4m) there is a BOUND interval x ∈ (10.42, 27.05)
plus an inner plunge region. At L = +5 there is a plunge only. At E = 0.95 the motion is plunge-only, as expected,
because that energy is below the well's minimum (≈ 0.962 for the Schwarzschild analogue).

**Mass normalisation, which is easy to get wrong.** The asymptotic g_TT of the TS δ=2 files gives M = 2σ/p:
**10/3 at P1 and 5/2 at P2** (σ = 1). That is twice the Kerr m = σ/p.

**The 6 registered levels of the TS v2 stage** ((1,0,4), (1,0,9), (1,1,4) at P1 and P2) are **PLUNGE-only**:
real motion runs from the ring out to a single turning point (x = 2.3–4.9), and none is a bound orbit. The
OBSTRUCTION verdicts are unaffected, since Morales–Ramis needs only the complex phase curve, but those rows say
nothing specific about bound orbits.

**Dubeibe et al. 2007 level** (E = 0.94, L = −3.12 at m = 1, p = 4/5) maps to L = −3.12·M = −39/5 at σ = 1. It
gives a **BOUND interval x ∈ (9.956, 21.923)**, consistent with their Fig. 1 range x ≈ 8–20, plus a plunge
region (ring, 3.428). With L = +39/5 the motion is plunge-only, so in this file convention the sign is
L = −39/5.
