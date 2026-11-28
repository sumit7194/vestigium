# Route-1 pilot: development log (development only; NO compute claims; no certifying runs)

## D1 (2026-11-28): β carried as a state variable, and the C² jet checked against floating point
- **Code:** capd/r1_dev.cpp, guard-built (GUARD OK).
  - The field is gen/mn_field.h with c[2] fed from state component 4. β′ = par[4] = exact 0.
  - Map: MpIMap(mn_vf5, 5, 5, 5). C² via MpIC2OdeSolver, MpIC2TimeMap and MpC2Rect2Set. Order 20, MPFR-128, step
    tolerance 1e−24.
- **Test:**
  - a thin point (x, y, p_x, p_y) = (2.76, 0, 0.01, p_y lifted at β = 0.01), with β = 1/100;
  - time map over T = 1; 29 s on one core.
- **Comparison:** float DOP853 finite differences (rtol 1e−13), with the initial state held fixed.

| quantity | CAPD (mid) | float FD |
|---|---|---|
| ∂_β x(T) | −1.21768156e−3 | −1.21768e−3 |
| ∂_β p_x(T) | −9.42264999e−2 | −9.42265e−2 |
| ∂²x/∂x₀∂β | 2.00187854e−3 | 2.00188e−3 |
| ∂²p_x/∂x₀∂β | 1.87953867e−1 | 1.879541e−1 |
| CAPD H(i, β, β), x | −1.47490e−5 | FD ∂²x/∂β² = −2.94968e−5 |
| CAPD H(i, β, β), p_x | −3.38128e−3 | FD ∂²p_x/∂β² = −6.76257e−3 |

- **Convention (IMPORTANT for the lemma's second partials):** CAPD's C² Hessian set(i, j, c) holds the second-order
  Taylor coefficients.
  - For j ≠ c it is the FULL mixed derivative ∂²f_i/∂x_j∂x_c.
  - For j = c it is ½ ∂²f_i/∂x_j².
  - So F_uu = 2·H(·, u, u), F_ss = 2·H(·, s, s), F_ββ = 2·H(·, β, β), while F_us = H(·, u, s) and F_uβ = H(·, u, β).
- The enclosure widths at a thin point over T = 1 are ~1e−22 to 1e−25.

## D2 (2026-11-28): the C² section return in reduced coordinates (x, p_x, β), with the β-dependent lift
- **Code:** capd/r1_dev.cpp, mode `ret`, guard-built (GUARD OK).
  - The lift L(x, p_x, β) = (x, 0, p_x, p_y, β) on H = −½ is its own CAPD C² map: p_y comes from the header's mn_lift,
    with β as a variable.
  - Then the flow runs to T_stop, with y(T_stop) < 0 certified.
  - Then the CAPD C² Poincaré map (MinusPlus) and computeDP give the Taylor coefficients.
  - The chain rule then gives d²(P∘L) = d²P(DL, DL) + DP·d²L, converting coefficients to true derivatives (diagonal ×2).
- **Test:** u = (2.76, 0.01, β = 0.01), T_stop = 106, at DEV settings (order 15, tolerance 1e−14, MPFR-128).
  **610 s on one core.**
- **Against float finite differences** (DOP853, rtol 1e−13; h = 1e−5 for D, H = 1e−3 for D²):
  - P agrees to 1e−8 and D to 1e−7.
  - All 12 second derivatives agree within the FD's own truncation error (~1e−4 relative). For example:
    - d²x/dx² 13.92750 (FD 13.92747);
    - d²p_x/dβ² −313.277 (FD −313.290);
    - d²p_x/dx dβ 303.592 (FD 303.650).
  - **So the lift's β-dependence and both Hessian conventions (Map and PoincareMap) are composed correctly.**
- **COST FINDING (premortem (c)):**
  - At the production settings (order 20, tolerance 1e−24), D1's C², 5-variable jet cost 29 s per flow-time unit, about
    10× S2's C¹, 4-variable passes.
  - That gives ≈ 52 min per near-fixed-point return, and ≈ 9 core-h for one 9-return C² chain at a single point.
  - At dev settings: ≈ 10 min per return, ≈ 1.7 core-h per chain.
  - The 12 core-h pilot cap therefore cannot hold the production settings for more than ~1 pass. The settings must be
    fixed by an amendment before any pass.
  - Widths at dev settings, at a thin point: relative D-width ~5e−9, relative D²-width ~5e−7, per return. That is far
    below the 1% bar on [t′].

## D3 (2026-11-28): the fixed point uniformly over a β-interval (parametric Krawczyk), and c′(β)
- **Code:** capd/r1_dev.cpp, mode `fpw`, guard-built.
  - G(z, β) = P(L(z, β)) − z, with z = (x, p_x).
  - C¹ passes over lifted boxes: the mean-value lift enclosure, with D(P∘L) = DP·DL(U).
  - Dev settings (order 15, tolerance 1e−14).
- **First attempt: FAIL (Kerr end, β ∈ [0, 1e−8], r = 3e−8).**
  - Y = 2.3e−7 > r.
  - The cause: G(z̄, B) evaluated over the whole β-box varies by ∂_βG·w ≈ 1.4e−7, and A·G loses the correlation with
    the moving fixed point (c′ ≈ 1.16). This is the β-wrapping blocker on a small scale.
- **Fix: a parametric centre** ẑ(β) = z̄ + c̃(β − β̄), with c̃ the float c′ = (1.15924840, 0).
  - Y = |A G(z̄, β̄)| + |A D_τG|·w/2, where D_τG = D_zG c̃ + ∂_βG − c̃ is evaluated over (z̄ + [−R, R]²) × B,
    with R = r + |c̃|w/2.
  - **Result: CERTIFIED.**
    - Y = 2.59e−10, Z = 0.0263, margin −2.90e−8.
    - For every β ∈ [0, 1e−8] there is a unique fixed point in ẑ(β) + [−3e−8, 3e−8]².
    - 253 s on one core.
  - c′ ∈ x: 1.1608 ± 0.064; p_x: (−0.3 ± 97)e−3. It contains the float FD value (1.15925, ~0).
- **Width structure (a development observation, NOT a pilot result):**
  - Over the 3.6e−8 derivative box, DP's enclosure has relative width ≈ 1e−3: DPz width 1.3e−2 on 13.45. That is
    ≈ 3e4 × the set size.
  - The genuine curvature ratio |D²P|/|DP| from D2 is only ≈ 2–20. So ≈ 99.9% of the width is box wrapping in the C¹
    variational evaluation over the hull box, not real variation.
  - A naive extrapolation to a 1e−4 set gives O(1) relative derivative widths.
  - **Remedy to develop (D3b; registered remedy R-b):** mean-value forms. DP(set) ⊂ DP(centre, thin C², tight) +
    [D²P(set)]·Δ.
    - The D² enclosure over the set is itself wrapped, but it multiplies Δ.
    - Which form is tighter at w = 1e−6 and 1e−4 is exactly what the pilot measures. Both are built before any pass.
