# Neon T29 (MN separatrix-splitting scout): Quantum's verification

Written by Claude Opus 5.5 (session "Quantum"), 2026-11-21.
- **What was checked:** the outside model "Neon" (Gemini, via the Bridge) wrote a float scout from our brief,
  `../NEON_BRIEF_splitting_scout.md`.
- **The code:** `/Users/sumit/Github/neon_work/mn/T29_code/mn_splitting_scout.py`, sha256 ecddf3b071fa668e…. It is
  not copied here.
- **Everything below is non-rigorous floating point.** Nothing here is certified.

## What I did
1. **Read the whole script (480 lines) before running it.**
   - It imports only numpy, scipy and mpmath, and does no file or network I/O.
   - The metric is the brief's transcription verbatim.
   - The derivatives are complex-step (h = 1e-30), and every function on that path is complex-analytic.
   - W^u runs forward and W^s backward, with the outward branch on both. Crossings are taken on Σ_t = {p_r = 0, r > r0 + 4}.
   - The phase is the Kerr θ-angle from the point's own K_θ, with ψ = 0 at z = +z_m and p_θ > 0 on (0, π). The cd
     inversion is correct.
   - The harmonics come from periodic cubic splines of each manifold's K_r(ψ), differenced on a 128-point grid.
2. **Reran it unchanged.** Isolated (python -I), nice 10, 1 thread, on Python 3.13.12 / NumPy 2.5.0 / SciPy 1.18.0
   (Neon used 3.11 / 2.1 / 1.15). Output: `t29_rerun.out`. Every number in Neon's summary reproduces to the printed
   digits.
3. **Ran the β values the summary reports but the delivered grid does not contain.** These are −0.05 … −0.25 and
   0.3 … 0.5. Drivers: `scan.py` and `grid64.py`; outputs: `t29_neg.out`, `grid_pos.out`, `grid_neg.out`. They import
   the delivered module read-only.
4. **Tested convergence in the sampling** (`nsamp.py` → `nsamp.out`), not just in the tolerance. Neon's C5 halved only
   the tolerance.

## Verdicts
- **Controls: all reproduce PASS.**
  - M0: the metric equals Kerr BL with spin +a, rel ≤ 1e-14, no ω flip.
  - C1: max|ΔK_r| = 9.4e−13 at β = 0, and λ_u = 26.8687 = e^{κT}.
  - C2: at a = 3.003, A1 = 1.2e−13, at the floor.
  - C3: linear, with the sign flip.
  - C4: forbidden harmonics ≤ 1e−11 at n = 32, and ≤ 1e−11 at 64–128.
- **(a) First order: CONFIRMED, more tightly than Neon showed.**
  - At β = ±1e−6 (n = 64), A1/β ÷ 4Υ_θ|L₂| = 1.00003 and 1.00001.
  - So the direct integration agrees with the Arb-certified L₂ = −4.77482114974644e−5 to about 2e−5 relative. The
    noise floor is about 1e−13 on A1 ≈ 2.9e−9.
  - Sign: positive in the stated convention, ΔK_r = K_r(W^u) − K_r(W^s), so M(ψ₀) = +2.867e−3 sin 2ψ₀ to first order.
    This settles the sign we had marked UNSURE.
- **(b) The empirical β₀ scales: CONFIRMED** (n = 64). The 10% / 50% deviations sit at:
  - β ≈ +0.195 (0.8999) and +0.484 (0.4990 at 0.485);
  - β ≈ −0.061 (0.9058 at −0.060, 0.9008 at −0.062) and −0.151 (0.5064 at −0.150, 0.4925 at −0.152).
  - On the positive side, A1 itself peaks near β ≈ 0.4.
- **The zero crossing of A1: CONFIRMED.**
  - A1 = −1.67e−7 at β = −0.2062 and +5.25e−6 at −0.2070, so **β\* ≈ −0.2062** (float).
  - There the second harmonic is clearly nonzero: A2 ≈ +1.1e−8 against a forbidden-harmonic floor ≤ 1e−11.
  - **Reading.** The harmonic amplitudes at finite β depend on the chosen measuring function (K_r) and on the phase
    map, but tangency is coordinate-free.
    - The slope of ΔK_r at the symmetric point ψ₀ = 0 is about 2A1 + 4A2, and at π/2 it is about −2A1 + 4A2.
    - Each vanishes within about 3e−6 of β\*: the two symmetric homoclinic orbits lose transversality at two nearby
      β (float), with A2 deciding the local picture there.
  - Chaos is not excluded there. Other, non-symmetric homoclinics are expected to stay transverse. But neither the
    Melnikov route nor the symmetric-orbit route certifies that point.
- **(c) The physical points: CONFIRMED qualitatively; Neon's slopes are off in the 3rd digit.**
  - γ_β exists and is hyperbolic at β = 1/5 (r0 16.780, λ_u 25.99) and at β = −1/3 (r0 14.024, λ_u 25.17).
  - The zeros at ψ₀ = 0 and π/2 are simple at both.
  - **Correction.** Neon's slopes come from spline derivatives with 32 samples, and they carry about 1e−5 absolute
    error. Neon's "step_diff" (1e−9) only varied the tolerance and missed this.
  - Converged values (n = 128, with the spline and Fourier forms agreeing to ~2e−7): at β = 0.2 the slopes are
    +1.0206e−3 and −1.0290e−3, against Neon's +1.0145e−3 and −1.0253e−3.
  - At β = −0.205 the n = 32 spline slope at π/2 even has the WRONG sign (−2.2e−6 against the converged +1.63e−5).
  - The A2 values at n = 32 are also unconverged near β\*.
  - The A1 values are robust: they change < 2e−6 relative between n = 32 and 128.

## What this does and does not give
- **It gives:**
  - an independent direct-integration check of the certified first-order coefficient and its sign;
  - numerical evidence that W^u ≠ W^s with transverse symmetric homoclinics at β = 1/5 and −1/3;
  - an empirical picture of where first order fails: about 10% off by β ≈ +0.2 / −0.06, and a degenerate point at
    β\* ≈ −0.206.
- **It does not give:**
  - any bound;
  - an explicit β₀;
  - a proof at β = 1/5 or −1/3.
  - Theorem A covers only 0 < |β| < β₀ (not explicit). The β\* observation says that a uniform first-order argument
    cannot reach β = −1/3: on the negative side the first harmonic vanishes before −1/3. A fixed-β route (C, or a CAPD
    horseshoe) would be needed there.
