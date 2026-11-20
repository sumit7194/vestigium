# MN Melnikov second harmonic: interval certification (pre-registration)

Status: REGISTERED, 2026-11-20. The Bridge AGREED to the proposal with one correction (stage 2 added: Theorem A needs a
nondegenerate zero). Sumit's go is standing, relayed by the Bridge. Committed before any code that computes a target number.
Written by Claude Opus 5.5 (session "Quantum"). Theory: Claude Fable 5.2 (fable_work/mn_melnikov). Independent float
reproduction: the Bridge, V23 (TheBridge falsification/V23_mn_melnikov_check).

## Target and claims
- The point: (M, a, r_u, z_m) = (5, 3, 16, 1/2), on the Kerr level with an unstable spherical orbit at r_u and θ amplitude z_m.
- L(ψ0) = L0 + 2 Σ_{m≥1} L_{2m} cos(2m ψ0), with
  L_n = ∫_{-∞}^{∞} [v_n(r_h(λ)) − v_n(r_u)] cos(nΥλ) dλ and v_n(r) = (1/2π) ∫_0^{2π} F(r, z(χ)) e^{−inψ(χ)} ψ'(χ) dχ.
- **Stage 1** gives Theorem A' (no real-analytic integral near the tangle). It certifies L2 ≠ 0: the Arb enclosure of L2
  excludes 0. Pass word: **CERTIFIED-NONZERO**. The predicted value is −4.774821150e−5 (V23).
- **Stage 2** gives Theorem A (transversality, horseshoe). It needs a nondegenerate zero: L''(0) = −8 Σ_{m≥1} m² L_{2m} ≠ 0.
  It certifies L4 (same pipeline, cos 4ψ) and a rigorous bound T3 ≥ Σ_{m≥3} m² |L_{2m}|, such that |L2| > 4|L4| + T3.
  Pass word: **CERTIFIED-NONDEGENERATE**. If the bound does not close, stage 2 is reported **OPEN**; nothing is loosened.

## Setup correspondence
The claim is "the MN quadrupole's Melnikov second harmonic L2 is nonzero (and the zero is nondegenerate) at
(M, a, r_u, z_m) = (5, 3, 16, 1/2)", which Theorem A' / A (fable_work/mn_melnikov/THEOREM_DRAFT.md) use at exactly this
orbit. The computation runs at that condition: the same (M, a, r_u, z_m), the same level (E, L, Q), and the same definitions of
r_h, ψ and F as SETUP.md / CERTIFY.md and V23. It is the first-order (small-β) statement, not a fixed-β one.

## Independence
- F is built from quantum's own MN transcription, `qsim/capd/horseshoe/mn_codegen.build()`: the symbolic H in
  (x, y, p_x, p_y; k, α, β, E, L).
- F = Σ · ∂H/∂β at β = 0, with p_t = −E, p_φ = L, p_x² = k²R(r)/Δ², p_y² = Z(z)/(1 − z²)², r = M + kx, y = z,
  Σ = r² + a²z². Then k = 4 and α = −1/3 (α = −a/(M + k)).
- **Convention (a construction choice, settled by gate G2 before any target number):** if the mass shell fails with
  α = −1/3, mn_codegen's rotation sense is the opposite of the orbit's +a. Then α = +1/3 is used, and both runs are recorded.
- Kerr controls: ∂/∂M and ∂/∂a of H(k(M, a), α(M, a), β = 0) at (5, 3), in the same (x, y) chart and with the same orbit.
- V23's numbers are used only for comparison (G1, G3, and the predicted value), never as inputs.

## Method (python-flint 0.9.0 / Arb, 128 bits; 256 if a radius is too large)
1. **Level.** An Arb Krawczyk step on the 3 equations R(16) = R'(16) = 0 and the z_m relation, around V23's values. Then
   r_t and r_4 come from the deflated quadratic, A = r_t − 16, B = 16 − r_4, κ = √((1 − E²)AB),
   z₊² = Q/(a²(1 − E²) z_m²), m = z_m²/z₊² and Υ = π a √(1 − E²) z₊ / (2K(m)).
2. **θ motion.** ψ(χ) = Υ [F(π/2 | m) − F(π/2 − χ | m)] / (a √(1 − E²) z₊) and
   ψ'(χ) = Υ / (a √(1 − E²) √(z₊² − z_m² cos²χ)), with z = z_m cos χ; F(φ|m) is acb.elliptic_f.
   By the symmetries (z(χ + π) = −z, ψ(π − χ) = π − ψ, F even in z; the Bridge checked the reduction),
   v_n(r) = (2/π) ∫_0^{π/2} F(r, z(χ)) cos(nψ(χ)) ψ'(χ) dχ for even n.
3. **Outer integral.** L_n = 2 ∫_0^T [v_n(r_h(λ)) − v_n(16)] cos(nΥλ) dλ + tail, with
   r_h(λ) = 16 + 2AB / [(B − A) + (A + B) cosh κλ] and T = 75/κ. Both integrals use acb.integral, nested.
4. **Tail, λ > T.** 0 < r_h − 16 ≤ 8AB e^{−κλ}/(A + B) once e^{κλ} ≥ 1.34. The bound is
   |tail| ≤ 2 S ∫_T^∞ 8AB e^{−κλ}/(A + B) dλ, where S bounds |∂_r v_n| on r ∈ [16, r_h(T)] by an interval evaluation of
   ∂_r F over the box (times the χ-integral of ψ' and 2/π). It is added as a ± ball.
5. **Stage 2 bound T3 (a two-contour Cauchy estimate).** Write cos(nΥλ) = Re e^{inΥλ}. Then L_n = Re ∫∫ G e^{−in(ψ(χ) − Υλ)} with
   G = (1/2π) ΔF(r_h(λ), z(χ)) ψ'(χ) and ΔF = F(r_h, z) − F(16, z).
   - Shift λ → λ + iσ (0 < σ < 0.156/…, inside the strip where r_h is holomorphic) and χ → χ − iτ (with z_m cosh τ < 1, so
     z stays away from ±1). The integrand is 2π-periodic in χ and decays exponentially in λ, so the shift is legitimate.
   - The result: |L_n| ≤ e^{−n(Υσ + b)} C, where b = min over χ of (−Im ψ(χ − iτ)) > 0 (interval-certified), and
     C = (1/2π) ∫_ℝ ∫_0^{2π} |ΔF(r_h(λ + iσ), z_m cos(χ − iτ))| |ψ'(χ − iτ)| dχ dλ.
   - C is bounded by interval evaluation on a box partition, plus the exponential λ-tail.
   - Then T3 ≤ C Σ_{m≥3} m² e^{−2m(Υσ + b)} (closed form). (σ, τ) are chosen on a small grid before evaluating stage 2;
     the best certified bound is used, and every grid point tried is reported.
   - Stage 2 needs F on complex (r, z) boxes away from the real axis. Its validity rests on the holomorphy domain stated
     here: r_h has no pole for |Im λ| < 0.156 (pole at cosh κλ = (A − B)/(A + B)), and F is holomorphic for |z| < 1 and
     Δ(r) ≠ 0, R ≠ ∞. A box on which F's interval evaluation returns a non-finite value FAILS the bound (OPEN), never skipped.

## Gates (any failure: INVALID, no reading)
- **G1 level:** the enclosure contains V23's 30-digit (E, L, Q); R(16) and R'(16) contain 0; the Krawczyk radius is < 1e-25.
- **G2 orbit:** (dr_h/dλ)² − R(r_h) contains 0 at 20 points, and H0 = −1/2 (mass shell) is contained at 20 orbit points.
  This settles the α sign.
- **G3 integrand:** the Arb F at 10 random real (r, z) points agrees with V23's F_vals (float64) to 1e-12 relative.
- **G4 parity:** the L1 enclosure (cos ψ) contains 0.
- **G5 elliptic:** acb.elliptic_f(φ|m) agrees with mpmath ellipf at 10 points, real and complex φ, as used in stage 2.
- **C-Kerr:** L2 for ∂/∂M and for ∂/∂a. Each enclosure CONTAINS 0, with radius ≤ 1e-6 |L2|.
- **C-positive (cheap):** V23's sabotage (x·y added in the tt slot of G1): its L1 excludes 0 (≈ 210.19).

## Reading
- **Stage 1:** CERTIFIED-NONZERO if every gate holds and L2's enclosure excludes 0. If it contains 0 with the gates
  holding: INCONCLUSIVE (raise the precision; never called zero). A gate failure: INVALID.
- The midpoint against −4.774821150e−5: a disagreement beyond the radius plus 1e-9 relative is a FINDING, reported; it does
  not change a sign certificate.
- **Stage 2:** CERTIFIED-NONDEGENERATE if |L2| − 4|L4| − T3 > 0 as an interval (lower bound > 0). Otherwise OPEN.

## Resources
1 core, nice 10, detached, with the usual guard; ≤ 3 h (if longer, the Bridge is told; nothing is loosened). Memory < 1 GB.
Outputs in qsim/mn_melnikov/ (code, RESULT.md, CHECKS.json). Model provenance in every commit.

## Amendment S2-A1 (stage 2 construction; REGISTERED 2026-11-20, before any stage-2 code computes a number)
Proposed by Claude Opus 5.5 (session "Quantum"). The Bridge reviewed it and APPROVED it with additions 1–3 below, which are
included. Stage 1 is unchanged. This makes step 5 concrete; nothing in it loosens step 5.

**Setup**
- L_n = Re (1/2π) ∫_ℝ ∫_0^{2π} ΔF(r_h(λ), z(χ)) ψ'(χ) e^{−inψ(χ)} e^{inΥλ} dχ dλ. The sin·sin part vanishes because r_h is
  even in λ.
- On a valid contour (below), |L_{2m}| ≤ C q^m, with q = e^{−2(Υσ + b)} and
  C = (1/2π) ∫_ℝ ∫_0^{2π} |ΔF(r_h(λ + iσ), z_m cos(χ − iτ))| |ψ'(χ − iτ)| dχ dλ, which is independent of n.
- Then T3 = C [q(1+q)/(1−q)³ − q − 4q²] ≥ Σ_{m≥3} m² |L_{2m}|. It is evaluated in Arb with upper bounds; it is increasing
  in q and in C.

**Validity of the contour shift (the tube certificate)**
- **The tube:** P(σ, τ) = {λ : Im λ ∈ [0, σ]} × {χ : Im χ ∈ [−τ, 0]}. The integrand must be holomorphic on all of it: F at
  (r_h(λ), z_m cos χ), F at (16, z_m cos χ), r_h, and ψ'.
- **Core region:** Re λ ∈ [−Λ, Λ], Re χ ∈ [0, 2π], with Λ = 1. It is covered by 4-D boxes (Re λ, Im λ, Re χ, Im χ), split by
  adaptive bisection. Every box must evaluate FINITE (sqrt with analytic=True; divisions by enclosures that contain 0 are
  non-finite).
  - A box still non-finite after 40 bisections makes the point INVALID-POINT.
- **Outer region:** |Re λ| ≥ Λ. There |cosh κλ| ≥ sinh κ|Re λ|, so |r_h − 16| ≤ d(Λ) = 2AB / ((A + B) sinh κΛ − |B − A|),
  certified d(Λ) < ρ = 1/2.
  - The disc |r − 16| ≤ ρ is covered by a 10×10 grid of boxes, crossed with χ boxes covering the χ tube. Every one must be
    finite. This also gives Fmax = sup |F| over the disc × the tube.
- **The vertical sides vanish.** In the outer region, |ΔF| ≤ Fmax |r_h − 16| / (ρ − d) ≤ Fmax d(|Re λ|) / (ρ − d).
  - This holds uniformly in Im λ ∈ [0, σ] and in χ, and it tends to 0 as |Re λ| → ∞, so the λ shift's vertical sides
    vanish.
  - The χ shift is valid by 2π-periodicity: ψ(χ + 2π) = ψ + 2π, n is an integer, and the integrand is 2π-periodic in χ.

**b (addition 1)**
- b is certified, never set to τ.
- −Im ψ(χ − iτ) = ∫_0^τ Re ψ'(χ − it) dt. Hence b = Σ_j h_j · min Re ψ'(box_j), over a partition of t ∈ [0, τ] into 64
  pieces, each crossed with Re χ ∈ [0, 2π] covered by 64 boxes. That is a full period; ψ' is in fact π-periodic.
- ψ' = (π/2K) / √(1 − m cos²χ), with sqrt analytic=True.

**C, using symmetries**
- By (λ, χ) → (−λ, −χ) and χ → χ + π, C = (2/π) ∫_0^∞ ∫_0^π I dχ dλ.
  - The Bridge checked both. They are valid on counted points, whose tube certificate excludes the principal-cut failure of
    conj √w = √(conj w).
- **Inner part, Re λ ∈ [0, Λ]:** Σ over boxes of sup I × area, on the shifted contour.
  - Start from a 16×16 grid over [0, Λ] × [0, π].
  - Refine the box with the largest (sup − inf) × area, bisecting the larger of κ·Δ(Re λ) and Δ(Re χ).
  - Stop when Σ(sup − inf) × area ≤ 0.05 · Σ inf × area, or when 20,000 boxes are reached. Every stopping state is a
    rigorous upper bound.
- **Tail, Re λ ≥ Λ:** (2/π) · π · max|ψ'| · Fmax / (ρ − d) · ∫_Λ^∞ d(u) du, with
  ∫_Λ^∞ d(u) du ≤ 2AB e^{−κΛ} / (κ D0) and D0 = (A + B)(1 − e^{−2κΛ})/2 − |B − A| e^{−κΛ} > 0 (certified).

**Grid, controls and gates**
- **The counted grid, fixed now:** σ ∈ {0.04, 0.07, 0.10, 0.13} × τ ∈ {0.3, 0.6, 0.9, 1.2}, 16 points.
- **A point COUNTS** if its tube certificate passes and every C box and tail quantity is finite. Otherwise it is
  INVALID-POINT, and every point is reported.
- **Must-fail controls (addition 3):** (σ, τ) = (0.17, 0.6), past the r_h pole at Im λ ≈ 0.156, and (0.07, 1.35), where
  z_m cosh τ > 1. Both must come out INVALID-POINT. If either does not, the tube certificate is not detecting
  singularities, and stage 2 is INVALID. They are never counted.
- **Consistency gates (additions 2):** at every counted point, C e^{−2(Υσ + b)} ≥ |L2|.upper and
  C e^{−4(Υσ + b)} ≥ |L4|.upper. Any violation makes stage 2 INVALID, not just the point.
- **L4:** the stage-1 pipeline with n = 4 (`mel_cert.py --only L4`), gates included. It is compared with V23's float
  L4 = −5.31274e−10; a disagreement beyond the radius plus 1e−6 relative is a FINDING.

**Pass rule**
- CERTIFIED-NONDEGENERATE if AT LEAST ONE counted point gives (|L2|.lower − 4|L4|.upper − T3.upper) > 0.
- One point suffices because each counted point is a theorem S3 ≤ T3(σ, τ) about the same fixed S3, and a minimum of valid
  upper bounds is a valid upper bound. L2 and L4 come from single, grid-independent enclosures.
- Otherwise OPEN. If it does not close, the remedy is a finer C box rule (a new amendment), not a wider grid.

**Debugging before the counted run:** only at the two must-fail controls and at one off-grid point, (0.02, 0.1), each at a
reduced box budget. These are reported as debug runs, never counted. Resources are 1 core at nice 10 under the existing
slot (the Bridge, 2026-11-20).
