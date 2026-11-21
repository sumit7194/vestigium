# Brief: direct numerical measurement of separatrix splitting in Manko–Novikov geodesics vs the quadrupole β

For an outside model (Gemini, "Neon"), sent via the Bridge. Written by Claude Opus 5.5 (session "Quantum"), 2026-11-21.
Everything you produce is a non-rigorous floating-point SCOUT. It will be checked independently. Label every number with
how it was computed, and never call anything "proved" or "certified".

## 0. Goal in one paragraph
- **The system.** Geodesics of the Manko–Novikov (MN) spacetime: Kerr plus an extra "anomalous" mass quadrupole β.
  For fixed energy E and angular momentum L they reduce to a 2-degree-of-freedom Hamiltonian system in (r, θ).
- **At β = 0 (Kerr)** the system is integrable. An unstable inclined spherical orbit γ₀ has stable and unstable manifolds
  that COINCIDE: a homoclinic cylinder.
- **For small β ≠ 0** first-order (Melnikov) theory predicts that they split, by a definite amount. We have a certified
  value of the first-order coefficient.
- **We want** a direct numerical measurement of the splitting as a function of β:
  - small β, to confirm the first-order coefficient independently;
  - larger β up to the physically interesting β = 1/5 and β = −1/3, to see how far the first-order prediction holds and
    whether the splitting persists.

## 1. The metric (use exactly this transcription)
- **Constants.** Mass M > 0, spin a with 0 < a < M, k = sqrt(M² − a²), χ = a/M, α = (−1 + sqrt(1 − χ²))/χ.
- **Coordinates.** Prolate spheroidal (x, y), with r = M + k x and y = cos θ. The exterior is x > 1, |y| < 1.
- **Building blocks.** R = sqrt(x² + y² − 1) (equal to x on the axis), u = x y / R, and the Legendre polynomials
  P0 = 1, P1 = u, P2 = (3u² − 1)/2, P3 = (5u³ − 3u)/2.

```
psi  = beta * P2 / R^3
A    = -alpha * exp( -2 beta * ( -1 + sum_{l=0..2} (x - y) P_l / R^(l+1) ) )
B    =  alpha * exp(  2 beta * (  1 + sum_{l=0..2} (-1)^(3-l) (x + y) P_l / R^(l+1) ) )
Am   = (x^2-1)(1 + A B)^2 - (1-y^2)(B - A)^2
Bm   = (x + 1 + (x-1) A B)^2 + ((1+y) A + (1-y) B)^2
Cm   = (x^2-1)(1 + A B)(B - A - y(A + B)) + (1-y^2)(B - A)(1 + A B + x(1 - A B))
f    = exp(2 psi) Am / Bm
omega = 2 k exp(-2 psi) Cm / Am - 4 k alpha / (1 - alpha^2)
e2g  = (x^2-1)/(x^2-y^2) * exp( 3 beta^2 (P3^2 - P2^2)/R^6
         + 2 beta * sum_{l=0..2} [ (x - y + (-1)^l (x + y)) P_l / R^(l+1) - 2 ] + 8 beta ) * Am / ((x^2-1)(1-alpha^2)^2)
```

- **Line element (Weyl–Papapetrou):**
  `ds² = −f (dt − ω dφ)² + f⁻¹ [ k² e2g (x² − y²) ( dx²/(x² − 1) + dy²/(1 − y²) ) + k² (x² − 1)(1 − y²) dφ² ]`.
- **CONTROL M0 (do this first).** At β = 0 the metric must equal Kerr in Boyer–Lindquist coordinates with r = M + k x,
  cos θ = y, and spin +a. Check g_tt, g_tφ, g_φφ, g_rr and g_θθ at 10 random exterior points to ~1e-13 relative.
  - If g_tφ comes out with the opposite sign, flip the sign of ω, report it, and continue.
  - Also check that every metric function is even in y.

## 2. The reduced Hamiltonian and the time variable
- **Integrals.** p_t = −E and p_φ = L are conserved, and the mass shell is H_β = ½ g^{ab} p_a p_b = −½.
- **Mino time λ.** Integrate in Mino time, using the Hamiltonian
  `K_β(r, θ, p_r, p_θ) = Σ · (H_β + ½)` on the level K_β = 0, with Σ = r² + a² cos²θ the KERR function at every β.
  - The orbits are the geodesics, run in time λ with dτ = Σ dλ.
  - Use canonical (r, θ, p_r, p_θ). The (x, y) block of g is diagonal, so convert with dr = k dx and dy = −sin θ dθ.
- **The function that measures splitting.** It is Kerr's radial function, written in terms of
  Δ = r² − 2Mr + a² and P(r) = E(r² + a²) − aL:
  `K_r(r, p_r) = ½ [ Δ p_r² − P(r)²/Δ + r² ]`.
  - At β = 0, K_0 = K_r + K_θ exactly, with K_θ = ½[p_θ² + (aE sin θ − L/sin θ)² + a² cos²θ]. K_r is then a second
    integral.
  - At β ≠ 0, K_r is just a fixed function on phase space that we evaluate on the two manifolds.

## 3. The base orbit (all numbers below are from 30-digit computations)
- **Parameters.** (M, a) = (5, 3) and k = 4. The unstable spherical orbit has r_u = 16 and inclination z_m = 1/2: θ
  librates with |cos θ| ≤ 1/2.
- **Values:**
  - E = 0.935281504567998718539, L = 12.9725320356072806907, Carter Q = 56.3773;
  - outer turning point r_t = 47.5081774263, other root r_4 = 0.3330935199;
  - Lyapunov exponent in Mino time κ = 7.86302299765;
  - θ-frequency in Mino time Υ_θ = 15.0122754941.
- **The Kerr homoclinic orbit,** with λ = 0 at r = r_t, A = r_t − r_u and B = r_u − r_4:
  `r_h(λ) = r_u + 2AB / [ (B − A) + (A + B) cosh(κ λ) ]`.
- **The θ-motion,** with phase ψ and ψ = 0 at z = cos θ = +z_m:
  `z(ψ) = z_m · cd( 2K(k_z) ψ/π ; k_z )`, where k_z = z_m/z₊ and z₊² = Q/(a²(1 − E²) z_m²), and ψ = ψ₀ + Υ_θ λ.
- **The homoclinic cylinder** is labelled by ψ₀, the θ-phase at the moment the orbit is at r = r_t.

## 4. The first-order prediction (what you are testing)
On a section Σ_t = {p_r = 0, r near r_t} (the outer turning point), measure

`ΔK_r(ψ₀) := K_r(W^u-point at phase ψ₀) − K_r(W^s-point at phase ψ₀)`.

Here W^u is the unstable manifold of the continued periodic orbit γ_β, followed forward to its first outer turning
point, and W^s is the stable manifold followed backward to its last one.

- **Prediction:** `ΔK_r(ψ₀) = β · A₁ · sin(2ψ₀) + β · A₂ · sin(4ψ₀) + O(β²)`.
  - |A₁| = 4 Υ_θ |L₂| = **2.86726e-3**, from the certified coefficient L₂ = −4.77482114974644e−5 (enclosure radius
    7e−20). Equivalently, A₁ = 2.8672e−3 in the convention M = d/dβ [F(W^u) − F(W^s)]. Our sign convention is UNCHECKED
    against direct integration, so report the sign you find together with your conventions.
  - |A₂| = 8 Υ_θ |L₄| ≈ 6.4e−8 (L₄ = −5.31274e−10). This is negligible, and you are not required to resolve it.
  - Parity forces EVERY cos(nψ₀) term and every odd harmonic to vanish at every β.
- **Matching points on Σ_t.** You must decide what "the same phase ψ₀" means at finite β. Recommended: compute ψ for
  each point from (θ, p_θ) using the Kerr θ-angle variable of that point's own K_θ value (invert the cd form; the sign
  of p_θ picks the branch). Any consistent choice gives the same first-order term. Document your choice.

## 5. What to compute
1. **Continue γ_β.** Find the periodic orbit γ_β for each β. It is symmetric under (p_r, p_θ) → (−p_r, −p_θ), so shoot
   from a point with p_r = p_θ = 0 and solve one equation.
   - Report its Floquet multiplier and whether it stays hyperbolic and outside the horizon (r > M + k).
2. **Grow the manifolds.** Get the unstable and stable directions from the monodromy matrix, start at about 1e−6 along
   them, and integrate to Σ_t.
   - About 30/κ of Mino time is needed per pass. Use high-order integration (DOP853 or Taylor) at rtol ≲ 1e−12, or
     mpmath for the smallest β.
   - Sample ψ₀ at 16–32 points per period π.
3. **Fit** ΔK_r(ψ₀) to the even harmonics sin(2nψ₀) and cos(2nψ₀) with n = 1, 2, 3, and also check the odd ones.
4. **The β grid:**
   - **controls:** β = 0, and the Kerr-deformation control C2 below;
   - **first order:** β = ±1e−3, ±2e−3, ±5e−3;
   - **scaling:** β = 0.01, 0.02, 0.05, 0.1;
   - **physical:** β = 0.2 (= 1/5) and β = −1/3.
   - **If γ_β or the loop is lost** at some β (bifurcation, plunge, or loss of hyperbolicity), stop there, report where
     and why, and do not force it.

## 6. Known-answer controls (all must pass, or say which failed)
- **M0:** the metric equals Kerr at β = 0 (section 1).
- **C1, β = 0:** |ΔK_r| ≤ about 100 × your integration error at every ψ₀. This also gives the noise floor.
- **C2, Kerr deformation (the splitting must vanish):** set β = 0 and perturb the spin, a → 3.003 at fixed (E, L, M).
  - Redo the γ continuation and the manifolds, still measuring with the ORIGINAL a = 3 function K_r.
  - The manifolds still coincide, so the sin(2ψ₀) amplitude must sit at the noise floor, ≪ 1e−3 × 2.87e−3.
  - Any ψ₀-independent offset is allowed; it comes from using the old K_r.
- **C3, linearity:** A₁(β)/β must agree at β = ±1e−3 and ±2e−3 to a few %, and A₁ must flip sign with β.
- **C4, parity:** the cos terms and odd harmonics must sit at the noise floor at every β.
- **C5, step halving:** halve the tolerance (or double the mpmath digits) at β = 1e−3 and at β = 0.2. A₁ must agree to
  the digits you report.

## 7. The exact claims wanted (numerical, labelled as such)
- **(a)** The measured A₁(β)/β at small β, with its error, and its agreement with 2.86726e−3 in magnitude, plus the
  sign and your convention.
- **(b)** The function A₁(β)/β over the whole grid, and the β at which it deviates from the first-order value by 10%
  and by 50%. This is an empirical, NON-rigorous "β₀ scale".
- **(c)** At β = 1/5 and −1/3:
  - whether γ_β exists and is hyperbolic;
  - whether ΔK_r(ψ₀) has simple zeros at ψ₀ = 0 and π/2 (the symmetric homoclinic orbits). Give the slope there, with
    its error.
- **(d)** A table with one row per β. Columns: the noise floor, A₁, A₂, the largest cos or odd-harmonic term, and the
  step-halving difference.
- **(e)** The code, runnable, in one file, with the versions of every library used.

## 8. Out of scope
- No rigorous or interval claims.
- Nothing about other spacetimes.
- No changes to the metric transcription beyond the single sign fix allowed in M0.
- If a definition here looks wrong or ambiguous, say so and state what you used. Do not silently fix it.
