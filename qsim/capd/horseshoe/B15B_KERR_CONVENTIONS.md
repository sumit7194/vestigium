# B15b / B15b-1: the Kerr convention mapping for G0b-field, G0c and the plunge certificate

Committed BEFORE the first evaluation of G0b-field or G0c (as registered). It introduces no new choices: every
relation below is one that B15's registration already uses, or that B10's gate already established. G0b-field and
G0c test them.

- **If either gate comes out nonzero,** that is reported as a FAIL first.
- A diagnosis of the form "the convention was wrong" would mean that B15's registered level computation (r_s, Q_s,
  x_s) was done in other conventions than the field's. That would itself be a finding, disclosed in its own commit,
  never a silent re-mapping.

## The source at β = 0

mn_codegen.build(), with β = 0:

- ψ = 0 and γ-terms ∝ β vanish, so E2 = e^{2ψ} = 1, e^{G} = 1, a = −α and b = α.
- The field is rational in (x, y, p_x, p_y).
- H = ½(g^xx p_x² + g^yy p_y²) + V.
- The field is (∂H/∂p_x, ∂H/∂p_y, −∂H/∂x, −∂H/∂y).
- The B15 parameters are k = 39, α = −5/8, E = 49/50 and L = 445/2.

## Relation to Kerr in Boyer–Lindquist coordinates

1. **Coordinates.** Kerr's Weyl–Papapetrou form has ρ = √Δ·sin θ and z = (r − M) cos θ. The source has
   ρ = k√((x² − 1)(1 − y²)) and z = kxy (MN_METRIC.md). With Δ = r² − 2Mr + a² = (r − M)² − k², this gives
   **x = (r − M)/k and y = cos θ**. B15's registration uses x_s = (r_s − M)/k.
2. **Parameters.** M = k(1 + α²)/(1 − α²) = 89 and a = −2kα/(1 − α²) = +80, so k² = M² − a². This is the Kerr
   limit of Manko–Novikov in the convention of Gair, Li & Mandel (2008), where α = (−1 + √(1 − χ²))/χ with χ = a/M:
   α < 0 corresponds to a > 0. B15's registration uses (M, a) = (89, 80).
3. **t and φ.** By the B10 gate (mn_field_gate.py, part iii), V is the reduced potential
   V = [f(L − ωE)² − ρ²E²/f]/(2ρ²), with ω = 2kC/(E2·A) − w0 and w0 = 4kα/(1 − α²).
   - The constant w0 makes ω vanish on the axis, and BL's (t, φ) are the axis-regular, asymptotically static
     coordinates.
   - So the source's (t, φ) are BL's. Its p_t = −E is BL's −E, and its L is **BL's L_z = 445/2**, as B15 registered.
   - L' = L + w0·E is B10's rewriting of the same V, not a different L.
4. **Momenta.** r = M + kx gives p_x = k·p_r. y = cos θ gives p_y = −p_θ/sin θ, so p_θ² = (1 − y²)·p_y².
5. **Normalisation and time.** H = ½g^{ab}p_a p_b with p_t and p_φ fixed, so on the section's level H = −½ means
   μ² = 1, and as a phase-space function **μ² = −2H**. The field's time is the affine parameter λ with
   p_a = g_ab dx^b/dλ. G0c tests this.

## The expressions tested

These are textbook (Carter 1968; e.g. Misner, Thorne & Wheeler §33.5), in BL coordinates with G = c = 1, and
written in the source's variables:

- **Carter's constant:**
  Q = p_θ² + cos²θ·[a²(μ² − E²) + L²/sin²θ]
    = (1 − y²)p_y² + y²·[a²(μ² − E²) + L²/(1 − y²)],  with μ² = −2H.
- **The radial function:**
  R(r) = [E(r² + a²) − aL]² − Δ·[μ²r² + (L − aE)² + Q],  with Δ = r² − 2Mr + a².
- **The radial equation:** Σ·dr/dλ = ±√R, with Σ = r² + a²y².
  - dr/dλ = k·ẋ = k·∂H/∂p_x.
  - So G0c's identity is (Σ·k·∂H/∂p_x)² = R(M + kx), with μ² = −2H and Q as above, at every phase-space point.
- **G0b-field:** {Q, H} = Σ over q ∈ {x, y} of (∂Q/∂q·∂H/∂p_q − ∂Q/∂p_q·∂H/∂q) = 0 at every phase-space point.
- **Points:** 20 random rational points with numerators and denominators of ≥ 64 bits, with x > 1, |y| < 1, and p_x,
  p_y free. The seed is recorded. Everything is evaluated exactly in rationals (sympy), at the exact B15 parameters.

## Plunge certificate (B15b-1)

The certificate uses these same R and Q with the call's start constants:

- the doubles x0, px0 and the lifted double py0, as exact rationals, at y = 0;
- μ² = −2H(start);
- Q(start);
- the horizon r₊ = M + k = 128;
- the section-motion bound |dy/dλ| ≤ √(Q + a²·|E² − μ²|).
