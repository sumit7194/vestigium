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
