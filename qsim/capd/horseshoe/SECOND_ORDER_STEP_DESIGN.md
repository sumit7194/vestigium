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

## 3. One step: the composed-map formulation (P1–P3; replaces the full 8-D jet version)

**Cost that motivated the change** (planning information only, B16): CAPD's CnOdeSolver jets are taken in all 8
states. One MN step measured 9.6 s at degree 2 and 59 s at degree 3. At ~5,700 steps per return, the degree-3 call alone
is ~94 h per piece per return. Only derivatives in the 2 parameters r are needed.

**The statement** (the Bridge's composed-map form). Let x(r) = x_n + C·r + ½H(r, r) and Ψ(r) = φ_h(x(r)). Then

  Ψ(r) = Ψ(0) + DΨ(0)·r + ∫₀¹ (1−s)·D²Ψ(s·r)[r, r] ds  ∈  Ψ(0) + DΨ(0)·r + ½·[D²Ψ(R₀)][r, r].

- This holds componentwise: the weight (1−s) ≥ 0 integrates to ½, and R₀ is convex and contains s·r.
- The term splits as ½[D²Ψ(R₀)] = ½D²Ψ(0) + ½([D²Ψ(R₀)] − D²Ψ(0)). The first part updates H; the second is boxed
  into E.
- The derivatives are DΨ = Dφ(x(r))·Dx(r) and D²Ψ = D²φ(x(r))[Dx(r), Dx(r)] + Dφ(x(r))·D²x(r), with Dx(r) = C + H(r, ·)
  and D²x(r) = H.

**P1 (thin, orders 0–2).** The second-order variational system along the two directions is integrated as an EXTENDED
ODE by CAPD's ordinary C⁰ solver, with 8 + 16 + 24 = 48 states:

  ẋ = f(x);  Ẋ_i = Df(x)·X_i (i = 1, 2);  Ẋ_ij = Df(x)·X_ij + D²f(x)[X_i, X_j] (ij = 11, 12, 22).

- It starts from the thin data (x_n, X_i = C_i, X_ij = H_ij), which is correct because Dx(0) = C.
- After the step h it gives Ψ(0), DΨ(0) and D²Ψ(0) as validated enclosures:
  x_{n+1} = mid Ψ(0), C_{n+1} = mid DΨ(0), H_{n+1} = mid D²Ψ(0).
- Their radii go into E.

**P2 (hull, the order-2 Lagrange remainder in r).** The same extended system, with the SAME step h, starts from the hull
data:

  x(0) ∈ hull{x(r) : r ∈ R₀},  X_i(0) ∈ [C_i + H(R₀, e_i)],  X_ij(0) = H_ij.

- **The X_i must include the H(r, ·) spread.** With X_i = C_i only, R₃ would be under-enclosed whenever H ≠ 0, i.e.
  from the second step on (negative control, Test 1).
- Running x and X_i uncorrelated over the hull gives a superset, which is still rigorous.
- Then ½([X_ij](hull) − X_ij(thin))[r, r] evaluated over R₀ is boxed into E.

**P3 (the error part e).** φ(x(r) + e) − φ(x(r)) ∈ [Dφ(K)]·e, by the mean value theorem on segments in K: K is convex
and contains x(r) and x(r) + e, with K = the hull of the whole X_n. [Dφ(K)] comes from an 8-D C1 enclosure.
- Dφ(x_n)·e (from P1's thin variational part) is propagated in the Lohner QR frame, with no reorganisation.
- ([Dφ(K)] − Dφ(x_n))·e is boxed into E.

**Total:** X_{n+1} = { x_{n+1} + C_{n+1}r + ½H_{n+1}(r, r) + e' }, with e' ∈ (the QR-framed Dφ(x_n)·e) + (all the boxes).

**Step size:** chosen by CAPD's step control on the P2 (hull) run, then FIXED for P1 and P3. All three use the same h.

**Measured, not assumed** (logged per step):
- the hull-run width ([X_ij](hull) − X_ij(thin)) against (the thin width / L²);
- max|E| against the true thin width.
The 48-D hull run has its own wrapping, and this ratio decides whether the method beats first order.

## 4. Tests specific to the composed-map version

1. **Toy C with a CURVED initial set:** ẋ = −x + y⁴, ẏ = −y, with x₀(r) = r₁ + 0.3·r₂², y₀ = r₂ (so H₀ ≠ 0).
   - The enclosure of D²Ψ over R₀ must contain the exact D²Ψ at the CORNERS of R₀.
   - Negative control: a deliberate hull run with X_i(0) = C_i only must FAIL the corner check.
2. **The D²f gate:** the sympy-generated D²f[u, v] (and Df·v) for the 8-D field is compared against 50-digit finite
   differences of the existing 8-D field at ~100 random points in the MN domain, plus symmetry D²f[u, v] = D²f[v, u].
3. **Cost:** the 48-D extended step's wall time per step, measured against the 59 s of 8-D degree-3 jets.

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
4. **Negative control** on Toy B at large W: drop the P2 remainder box, or scale it by 0.5, and show the containment
   test FAILS.
4a. **Toy C** (non-constant D³: ẋ = −x + y⁴, ẏ = −y, with exact x = e^{−t}x₀ + y₀⁴(e^{−t} − e^{−4t})/3): the
   curved-set corner test of §4, with its negative control.
5. A code review.
6. The containment test (high-precision point images inside every step's enclosure) on MN.
7. B17 at 1e-12, 1e-9, 1e-7 and 1e-6.
8. A registered amendment.
9. The user's OK before any covering use.
