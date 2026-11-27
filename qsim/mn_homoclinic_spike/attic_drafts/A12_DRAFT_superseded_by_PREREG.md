## A12. Batched clarifications during S2 (labelled addendum; drafted 2026-11-27, appended to PREREG.md at the end of S2)

- **A11 lemma: non-author read by the Bridge, CORRECT (2026-11-27).** One wording fix, adopted here; the argument is
  unchanged.
  - Step 2's phrase "M⁻¹ maps K^c into K^c" is replaced by this, because mean-value matrices need not be invertible:
    with x_n = P(x_{n+1}), the contrapositive of step 1 gives x_n − x′_n ∉ K ⇒ x_{n+1} − x′_{n+1} ∉ K. On K^c,
    |Δu| < |Δs|/L, so |Δs_n| ≤ ν|Δs_{n+1}|.
  - The eigenvalue bounds that follow from the cone conditions, and the C¹ local unstable manifold of an analytic
    hyperbolic fixed point, are standard facts and are cited as such.
- **A12.1 Control (ii) reformulated** (the Bridge accepted it).
  - The registered meeting system fixed c on an interval. At the depth S2-0 forces (c ≈ 5e-12, m = 9) it is
    ill-conditioned: float cond 2.2e11, ‖A‖∞ 1.1e10. A residual along v_u in the first link cannot be absorbed, so
    it propagates ~λ⁸.
  - That run was stopped by verified PID before any certifying pass, and archived as s2/meet_ii_superseded_fixedc/.
  - **New form:**
    - X = (c, z_1…z_{m−1}, z′_1…z′_{m−1}, c′, α);
    - the links from w_u(c) and from w_u(c′), and the meeting P(z_{m−1}) − R P(z′_{m−1}) − α g = 0;
    - plus the phase condition x(z_{m−1}) = x̂, with x̂ ∈ [x̂₀ ± 1e-15] and uniform contraction over x̂ (van den Berg,
      Breden, Lessard & Murray 2018, Thm 3);
    - float cond 36, ‖A‖∞ 1.7.
  - **Reading:** distinct x̂ give distinct points w_u(c(x̂)) of W^u ∩ W^s. A certificate therefore gives a continuous
    arc, i.e. non-isolation. α ≡ 0 follows from the exact Carter bracket (carter_check.py: {K_r, H} = 0 on
    H = −1/2 with E and L symbolic; two must-fire mutations do not cancel) and the sign-definite ∇K_r·g on the
    meeting hull.
- **A12.2 Binaries.** v1 and v2 differ only in the meet mode (A12.1) and in bvp's choice of the ball radius r (a
  tighter estimate; no decision changes).
  - In-flight point passes used v1. Every certifying pass used v2 (atomic rename; sha256 in s2/binaries.txt).
- **A12.3 Control (iv): the cone lemma in its 2+2 form** (needs a non-author read). It is used for the time-±1 maps
  at L4.
  - *Setting:* the same as A11, with u, s ∈ R², Euclidean norms on each block, [M] = [[A, B], [C, D]] in 2 × 2 blocks;
    m(A) is a lower bound on the smallest singular value of A (≥ 1/‖A⁻¹‖_F), and the other norms are Frobenius upper
    bounds.
  - *Hypotheses:* μ = m(A) − ‖B‖L > 1, ‖C‖ + ‖D‖L ≤ Lμ, and ν = ‖C‖/L + ‖D‖ < 1.
  - *Claim:* W^u(p*) contains the graph over the disc |u − u*| ≤ δ* of a C¹ map h with ‖Dh‖ ≤ L, where
    δ* = (δ − ρ′)/(κ max(1, L)) and κ = ‖A‖ + ‖B‖L.
  - *Proof:* steps 1–3 as in A11, with norms. Step 4: let t₀ be the largest radius with the closed disc in π_u(Γ),
    and suppose t₀ < δ*. On that disc, g(u) = π_u P(u, h(u)) is continuous and injective, with
    |g(u) − g(u′)| ≥ μ|u − u′|, so |g(u) − u*| ≥ μ t₀ on the boundary circle. By Brouwer degree (invariance of
    domain), g(disc) ⊇ the disc of radius μ t₀. As in A11, P(Γ_{t₀}) ⊂ Γ, so π_u(Γ) ⊇ the disc of radius μ t₀ > t₀,
    a contradiction. ∎
  - W^s(L4) is W^u of the time-reversed flow, so the same lemma applies with σ = −1.
- **A12.4 (iv) set-up.**
  - PCRTBP µ = 1/2 (CKMJ eqs. 26–27). E = −(p² + q²) + 2Ω, with E(L4) = 3.
  - Extended field z′ = σT(f + α∇E) on s ∈ [0, 1] (the CKMJ Example 15 / Thm 16 unfolding; T and α are state).
  - Cones at δ = 1e-7; endpoints at radius ρ = 2.5e-8 (< 0.9 δ*). n segments of equal flow time T.
  - Unknowns (θ, x_1…x_{n−1}, φ, T, α).
  - **PASS:** Krawczyk (CKMJ Thm 30) certifies AND a rigorous C⁰ time-shift of the certified node nearest p̄ lies
    within 1.66e-9 (Euclidean) of p̄, CKMJ Table 4. The Euclidean ball is inside any max-norm ball of the same radius.
