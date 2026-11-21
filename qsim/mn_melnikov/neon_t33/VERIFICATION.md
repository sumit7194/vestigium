# Neon T33 (the β* zero crossing of the MN splitting): Quantum's verification

Written by Claude Opus 5.5 (session "Quantum"), 2026-11-21.
- **What was checked:** Neon (Gemini, via the Bridge) did a blind second look at the β* finding in
  `../neon_t29/VERIFICATION.md`. Its summary is `/Users/sumit/Github/neon_work/mn/T33_summary.md`.
- **The code:** the updated `/Users/sumit/Github/neon_work/mn/T33_code/mn_splitting_scout.py`, 576 lines, sha256
  e5d7ab09a50b83e5…. It is not copied here.
- **Not seen:** the companion scripts `mn_zero_crossing_scout.py` and `mn_mpmath_spotcheck.py`, which stayed in Gemini's
  Canvas. Neon's 30-digit spot check is therefore not reproduced here.
- **Everything below is non-rigorous floating point.**

## What I did
1. **Read the whole script.**
   - Against T29, the metric, K_β, the Hamiltonian flow, the γ_β shooting, the manifold growth and the section are
     unchanged. The only exception is the brentq tolerance for r0, which went from 1e-12 to 1e-13.
   - New: a trigonometric least-squares fit (`TrigPoly`) in place of the cubic spline; two more phase conventions,
     `geom_angle` and `arclength`; and a zero finder (a 720-point sign scan plus brentq, with the slopes taken from
     the fit).
   - It imports only numpy, scipy and mpmath, and does no file or network I/O.
2. **Ran its `__main__` unchanged.** Isolated (python -I), nice 10, 1 thread. Output: `t33_main.out`.
   - C1: max|ΔK_r| = 1.5e−13.
   - C2: A1 = 1.4e−13.
   - Both are at the floor.
3. **`verify.py`.** It imports the module read-only and computes the section once per (β, n).
   - It then fits it with the spectral fit at every K satisfying 2K+1 ≤ 2n/3. This avoids underdetermined fits; Neon's
     own default allows K = 16 or 20 at n = 32.
   - It also fits with the cubic spline, and repeats the analysis in the other two phase conventions.
   - Outputs: `bstar.out` and `window.out`.
4. **`edges.py`.**
   - Tests the sensitivity of A2 to eps_init, rtol and n.
   - Root-finds β* (A1 = 0) and the two **convention-invariant** window edges, where the slope of ΔK_r at the symmetric
     zeros vanishes. Output: `edges.out`.

## Verdicts
- **The spline problem: CONFIRMED, and worse than Neon says.**
  - At β*, the cubic spline finds 30 zeros at n = 32, 62 at n = 64 and still 16 at n = 128. All are spurious.
  - The spectral fit is converged:
    - A2 at β* is +7.8012e−9 (n = 64, K = 12/16/20) and +7.8015e−9 (n = 128, K = 12…40);
    - forbidden terms are ≤ 2.5e−13, and the fit residual is ~1e−12.
  - **This corrects my T29 report.** Its "A2 ≈ +1.1e−8 at β*" was a spline artefact (n = 64 spline: +1.02e−8). Its
    "within ~3e−6" was inflated by the same error. See the correction appended to `../neon_t29/VERIFICATION.md`.
- **β\* = −0.206224720 ± 3e−9: CONFIRMED** in the Kerr-angle convention.
  - My root is −0.2062247195 (n = 128, K = 30), 5e−10 from Neon's.
  - β* is the zero of a convention-dependent harmonic: in geom_angle, A1(β*_Neon) = +5.0e−10, which moves the root by
    about 7e−8. So the 1e−9 precision is a statement about the Kerr-angle convention only.
- **A2(β\*) ≈ +7.80e−9: CONFIRMED to the float systematics.**
  - Varying eps_init over (2.5e−7, 2e−6), rtol down to 5e−13, and n up to 256 moves A2 within +7.8012 … +7.8098e−9.
    That is about a 1e−3 relative systematic.
  - Neon's 30-digit +7.8088e−9 lies inside this band.
- **A3 ≈ +2.7e−11: order of magnitude only.** Across n and eps_init it ranges over +2.2 … +2.9e−11.
- **Four simple transverse zeros at β\*: CONFIRMED.**
  - Zeros at 0, 0.2497π, π/2 and 0.7503π, with slopes +3.14e−8, −3.12e−8, +3.10e−8 and −3.12e−8.
  - Every n, K, eps_init and rtol tried gives 4. The geom_angle and arclength conventions also give 4 (their
    non-symmetric pair sits at 0.26π and 0.74π).
- **The pitchfork window: CONFIRMED, and pinned in convention-invariant terms.**
  - The symmetric zero at π/2 has zero slope at β_a = −0.2062270334 (Kerr angle), or −0.2062270324 (geom_angle).
  - The symmetric zero at 0 has zero slope at β_b = −0.2062223948 (Kerr angle), or −0.2062223955 (geom_angle).
  - The two conventions agree to about 1e−12. That is expected, because tangency of W^u and W^s does not depend on
    coordinates.
  - The window is β* − 2.313e−6 … β* + 2.325e−6, a width of 4.64e−6. Neon's "about 2.3e−6" is confirmed.
  - Zero counts (n = 64 and 128, both conventions):
    - 2 at β* − 4, −3 and −2.4 (×1e−6);
    - 4 at −2.2, −1, 0, +1 and +2.2;
    - 2 at +2.4, +3 and +4.
  - Inside the window, the non-symmetric pair moves:
    - from π/2 ± 0.05π at β* − 2.2e−6 (born from the π/2 zero);
    - to 0 ± 0.05π at β* + 2.2e−6 (dying into the 0 zero).
    - So there is a homoclinic pitchfork at each edge.
- **"A2 changes sign near −0.20553": TRUE ONLY IN THE KERR-ANGLE CONVENTION. It is not physical.**
  - Kerr angle: A2 = −1.29e−10 at −0.20553 and +6.63e−10 at −0.2056, so the root is near −0.205541.
  - geom_angle: A2 = +1.57e−7 at −0.20553, with no sign change nearby.
  - Outside the window, the harmonics' amplitudes depend on the measuring function and the phase map. Only zeros and
    their simplicity are invariant.
  - This sign change plays no part in the window, which needs only A2 ≠ 0 at β*.
- **γ hyperbolic through the window: CONFIRMED** (λ_u = 27.031 to 27.035).

## What this gives and does not give
- **It gives:**
  - two independent float computations of one picture. A1 crosses zero transversally at β* ≈ −0.2062247 (with
    dA1/dβ ≈ −6.7e−3). For β outside [β_a, β_b] there are 2 transverse symmetric homoclinics. Inside, there are 4.
    Exactly at β_a and β_b one symmetric homoclinic is tangent: a pitchfork.
  - At every β tested, at least two zeros are simple, β* included. At exactly β_a or β_b, one symmetric zero is
    degenerate and the other stays simple (e.g. at β_a, the slope at 0 is about +6.4e−8).
  - That is numerical evidence that transverse homoclinics persist through β*.
- **It does not give:**
  - a bound or a proof;
  - an argument through the window. First-order (Melnikov) theory cannot reach β*, and neither can a uniform argument
    at the symmetric homoclinics. A fixed-β certification would be needed at any point near the window.
