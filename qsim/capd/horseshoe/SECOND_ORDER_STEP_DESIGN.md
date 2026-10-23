# Design note: a second-order C⁰ set step for the MN swing (derivation only; no code, no runs)

Status: REVISED after the Bridge's review (2026-10-24). The derivation is approved in principle, on condition that:
- the flow-derivative formulation is consistent, with no separate Rem (§3, §4);
- the lift formulas are explicit, with a lift containment test (§2a);
- there are two toys (quadratic and cubic) plus a negative control (§7).

Code is written only after the revised §2a, §3 and §4 are re-reviewed. This is option (i) of the swing discussion.

**Summary of the review.**
- (a) Convexity is fine. The preconditions are 0 ∈ R₀ (symmetric), 0 ∈ E_n, the field C³ on K, and K = hull of the
  WHOLE X_n including E.
- (b) There is no hidden W² seed, provided |E| stays third order: log max|E| per step against the thin width.
- (c) The lifts need their own check.
- (4) Mixing the Taylor map's jets with CAPD's flow remainder can double-count or under-count. Use the flow's own
  derivative enclosures, with no separate Rem.
- (5) The quadratic toy has D³ ≡ 0, so a cubic toy is also needed.
- (6) A negative control: dropping R₃ must make the containment test FAIL.

## 1. Why first order cannot do it

CAPD's C⁰ step encloses the numerical map T (the Taylor method in time) on a set X with centre x̄ and δ = x − x̄ as

  φ_h(X) ⊂ T(x̄) + [DT(X)]·δ + Rem.

The excess over the true image is rad([DT(X)])·|δ|, roughly |D²T|·W·W.

The true image's own quadratic part, ½ D²T(x̄)[δ, δ], has the same order. A first-order set can only hold it as a BOX.
On a needle (long length L along u₁, thin along u₂), that box has size ~|D²T|·L² in every direction, including the thin
one. That is the second-order seed measured by the W-scan (relative excess ∝ W).

**Conclusion:** evaluating D²T better does not help. The SET must carry the quadratic term as a polynomial in the
initial parameters, so that it is never boxed. Second-order sets lower the boxed part to third order, |D³T|·L³.

## 2. The set (preconditions: R₀ symmetric about 0, so x_n ∈ X_n; 0 ∈ E_n; the field C³ (analytic) on K)

The set is a quadratic Taylor model in the fixed initial parameters r ∈ R₀ (the initial box, after the lifts):

  X_n = { x_n + C_n·r + ½·H_n(r, r) + e : r ∈ R₀, e ∈ E_n }.

- x_n is a thin centre.
- C_n is a point matrix.
- H_n is a vector of point symmetric matrices, one per state component.
- E_n is an error set, held as now (Lohner QR frame: B·r_e, with no reorganisation).

r = (u, s) ∈ R₀ = [−1, 1]² is TWO-dimensional: the section coordinates of the piece. Everything else (the momentum lift,
the augmented states, every remainder) is a function of r, or lives in E.

## 2a. The lift, written out (explicit, NOT implicit)

The lift is L : R₀ → ℝ⁸, with

  x = c_x + u·h,  y = 0,  p_x = c_p + s·h,  p_y = √(rad(x, p_x)),  rad = (−1 − g^xx(x, 0)·p_x² − 2V(x, 0)) / g^yy(x, 0),
  (a, b, E2, eG) = aux(x, 0),

where aux holds the original exponential formulas. Every component is an explicit composition: no Newton step, no
implicit function.
- **Square-root branch:** rad > 0 is certified on hull(L(R₀)), as now (S9 lift check).
- **Coefficients:**
  - x₀ = L(0), C₀ = DL(0), H₀ = D²L(0) (point parts; radii into E₀);
  - E₀ ∋ (1/6)·[D³L(R₀)][r]³, the integral-remainder enclosure on the convex box R₀.
- **How they are computed:** all by CAPD AD on L written as a Node map R² → R⁸ (degree-3 jets), at the thin point 0 for
  degrees 0–2 and over the box R₀ for degree 3. For p_y, the derivatives come from the sqrt chain rule automatically;
  nothing is written by hand.
- **Lift containment test** (before the toys): sample 10³ points r ∈ R₀ and compute L(r) at 50 digits (mpmath, from the
  original formulas). Each must lie in x₀ + C₀r + ½H₀(r, r) + E₀. Plus a negative control: with E₀'s cubic part
  removed, the test must FAIL at a large h.

## 3. One step (the flow formulation: no separate Rem)

With δ(r, e) = C·r + ½H(r, r) + e and φ_h the exact time-h flow, Taylor's theorem with integral remainder on K (the
convex hull of the WHOLE X_n, E included) gives

  φ_h(x_n + δ) ∈ [φ_h(x_n)] + [Dφ_h(x_n)]·δ + ½·[D²φ_h(x_n)][δ, δ] + (1/6)·[D³φ_h(K)][δ, δ, δ].

- The remainder is R₃ = ∫₀¹ (1−s)²/2 · D³φ_h(x_n + sδ)[δ]³ ds.
- Its enclosure is valid componentwise: the weights are positive and integrate to 1/6, and every segment x_n + sδ
  lies in K because x_n ∈ X_n and K is convex.
- The four bracketed enclosures are CAPD's validated enclosures of the FLOW and its derivatives. Each already includes
  CAPD's time-truncation remainder, so NO separate Rem term is added.
- Degrees 0–2 are taken over the thin initial set {x_n}; degree 3 over K. As a result, nothing first-order in L enters
  through a remainder evaluated over the whole set.

Expanding δ and collecting powers of r gives the updates.

| Order in r | Update | Where the radius goes |
|---|---|---|
| 0 | x_{n+1} = mid[φ_h(x_n)] | the radius (rounding plus remainder, both tiny for a thin x_n) goes into E |
| 1 | C_{n+1} = mid([Dφ_h(x_n)]·C_n) | radius into E (as rad(·)·\|R₀\|) |
| 2 | H_{n+1} = mid([Dφ_h(x_n)]·H_n + [D²φ_h(x_n)][C_n ·, C_n ·]) | radius into E |
| ≥ 3 | boxed into E | — |

The order ≥ 3 terms are:
- [D²φ_h(x_n)][C r, H(r, r)];
- ¼·[D²φ_h(x_n)][H(r, r), H(r, r)];
- R₃;
- the error cross terms [Dφ_h(x_n)]·e (propagated in the Lohner QR frame, no reorganisation),
  [D²φ_h(x_n)][C r + ½H(r, r), e] and ½·[D²φ_h(x_n)][e, e].

**Logged per step** (data, not criteria): max|E|, the true thin width at that time, and their ratio. If |E| stops being
≪ the thin width, the cross terms are the first thing to look at. Possible bonus, not to be claimed until measured:
C·r is now exact, so the first-order wrapping only acts on E, and the ~8× floor may shrink.

## 4. Where the enclosures come from (CAPD, MPFR)

CAPD's CnOdeSolver::encloseCnMap(t, x, xx, phi, rem, enc) returns:
- the Taylor jets phi, computed with initial condition xx (the hull) for the derivatives, and with the value at the
  centre x;
- the remainder jets rem.

CnRect2Set adds them ("Phi += Rem"). The enclosure of the flow's derivatives over the initial set is therefore
phi + rem. Two calls are used:
- **Degrees 0–2:** x = xx = {x_n} (thin), degree-2 jets. Take phi + rem.
- **Degree 3:** x = x_n, xx = K, degree-3 jets. Take the degree-3 coefficients of phi + rem.

**Empirical check before use:** for a thin x inside a hull K, the thin call's degree-1 and degree-2 enclosures must lie
inside the hull call's. They must also contain finite-difference values of the high-precision flow (mpmath) at the
centre.

**Confirmation from the source** (to be quoted in the code review): that phi + rem is the documented enclosure of
Dᵏφ_h over xx, and that the value part uses x.
## 5. What stays the same

- The 8-D augmented field.
- S4 (B18/B18a) and S9 on the enclosure of X_n, and the consistency check, all on every step.
- Reorganisation OFF.
- Projected section rows. The section enclosure needs the quadratic set too: CAPD's formula is applied with
  affineTransformation replaced by the polynomial set's A·(X − c) = A·(x − c) + (A·C)·r + ½ (A·H)(r, r) + A·E. The
  quadratic part in r is enclosed per component; a 2-D r is all that is needed after the lifts.

## 6. Expected gain, to be checked against the W-scan

If the excess at the swing is E(W) ≈ κ·W now, the second-order set gives E₂(W) ≈ κ₂·W². The scan's fitted κ fixes the
first-order survivable W_s. A crude estimate puts W_s,2 ~ √(W_s / κ₂-scale). This is only plausible, not established; the
toy control and B17 runs decide.

## 7. Gates, as agreed with the Bridge

1. This derivation is reviewed first.
2. The lift containment test (§2a), with its negative control.
3. **Toy A** (quadratic, D³ ≡ 0): ẋ = −x + λy + y², ẏ = −y, with exact flow
   x(t) = e^{−t}(x₀ + λy₀t) + y₀²(e^{−t} − e^{−2t}), y(t) = y₀e^{−t}. It tests the quadratic bookkeeping.
   **Toy B** (cubic, D³ ≠ 0): ẋ = −x + λy + y³, ẏ = −y, with exact flow
   x(t) = e^{−t}(x₀ + λy₀t + y₀³(1 − e^{−2t})/2), y(t) = y₀e^{−t}. It tests R₃.
   In both, the second-order set must contain the exact image and be tight to ~1 (the first-order tripleton shows the
   W-proportional excess).
4. **Negative control** on Toy B at large W: drop R₃, or scale it by 0.5, and show the containment test FAILS.
5. A code review.
6. The containment test (high-precision point images inside every step's enclosure) on MN.
7. B17 at 1e-12, 1e-9, 1e-7 and 1e-6.
8. A registered amendment.
9. The user's OK before any covering use.
