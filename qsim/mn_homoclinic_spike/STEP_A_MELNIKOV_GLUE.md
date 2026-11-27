# Step A: the Melnikov glue. Chaos for every small β ≠ 0, both signs (registration-style note). PROVED at stated scope (the Bridge, 2026-11-27); (H1) discharged by Tier 2a

> **Note on reviewers.** In this project, "non-author read" and "independent" checks were done by separate AI sessions
> or systems (Claude sessions, Gemini), not by human peer review. No external expert has yet read these proofs.

Written 2026-11-27 22:05 IST by Claude Opus 5.5 (office "Quantum"). Maths only, 0 core-h; it uses existing certificates
and float records. Status: **PROVED at its stated scope**: chaos for all 0 < |β| < β₀, β₀ not explicit, analytic, both signs.
- The Bridge's non-author read (2026-11-27) found it CORRECT.
- C1 (Robinson at source) PASSED, with g1–g4 disclosed. [CR-mel] is not required.
- **(H1) DISCHARGED (Tier 2a, 2026-11-27, AGREE; tier2a/TIER2A_RESULT.md):** the MN field was re-derived independently
  from the published metric (Gair–Li–Mandel 2008) by a non-author. mel_gen's H0 and Hb agree to 1e−55.

Sources:
- fable_work/mn_melnikov/{SETUP, MELNIKOV, THEOREM_DRAFT}.md (Fable 5.2; unreviewed);
- qsim/mn_melnikov/RESULT.md (the Stage 1–2 certificates);
- this folder's PREREG (S1/S2), S1/S2 results and s2f_sym.json.

Labels: SURE (a standard argument, written out) / CHECKED (numerically) / UNSURE / INHERITED (from a source I did not
re-derive).

## 0. The stop-gate check (the Bridge's first condition): PASS
- **The question.** Does Stage 2's closing point cover our R-symmetric zero?
  - The closing point (σ, τ) = (0.13, 0.6) is a contour parameter of the Cauchy estimate for T3 (PREREG §S2-A1). It is
    not a location on the orbit.
  - Stage 2 certifies one ψ-independent inequality: |L2|.lower − 4|L4|.upper − T3.upper = +1.5242e−5 > 0, with
    T3 ≥ Σ_{m≥3} m²|L_{2m}|.
- **Our zero is ψ* = 3π/2 in Melnikov's own convention.**
  - Our reversor R: (x, y, p_x, p_y) ↦ (x, −y, −p_x, p_y), with y = cos θ, is θ ↦ π − θ, p_r ↦ −p_r, p_θ ↦ p_θ. That
    is MELNIKOV.md §3's **R₂**, with Fix R₂ = {θ = π/2, p_r = 0}.
  - So the S2 point p (y = 0, p_x = 0, at the outer turning point r_t) is an R₂-symmetric homoclinic point. By
    Lemma S, R₂ carries the zeros ψ₀ = π/2 and 3π/2.
  - S1 measured ψ₀ in Melnikov's convention (the Mino θ-phase at the outer turning point; PREREG S1 step 2). Its four
    zeros sit at 1.562, 3.133, 4.695 and 6.274 ≈ kπ/2, and S2 used the 4.695 ≈ 3π/2 one.
- **The inequality covers ψ* = 3π/2** (§3 step 5). It also covers every kπ/2, and it rules out any zeros of M other
  than kπ/2 (§3 step 5, remark). So the check PASSES whatever the phase offset.

## 1. Statement (Theorem A_R₂; the R₂ form of THEOREM_DRAFT's Theorem A, with an explicit first-order slope)
Setting, as in PREREG S2:
- MN at (M, a) = (5, 3), k = 4, α = −1/3;
- the level E = 0.93528150456799871854, L = 12.972532035607280691, H = −1/2;
- the section Σ = {y = 0, ẏ > 0}, with coordinates (x, p_x) and r = M + kx;
- the return map P_β, the hyperbolic fixed point w_β (the periodic orbit γ_β, r ≈ 16).

**Claim.** There is a β₀ > 0 (not explicit) such that for every β with 0 < |β| < β₀:
- (i) there is a unique R-symmetric homoclinic point p(β) ∈ W^u(w_β) ∩ Fix R near p₀ = (x_t, 0), analytic in β;
- (ii) the slope t(β) := v_x / v_px of W^u ∩ Σ at p(β) (with v the tangent) is analytic, with t(0) = 0 and
  **t′(0) = Υ_θ² L″(3π/2) / (2 k² F_t²) ≠ 0**, where F_t := ∂_r [½(r² − P(r)²/Δ(r))] at r = r_t > 0;
- (iii) so v_x ≠ 0 and v_px ≠ 0, and by lemma A1, W^u ⋔ W^s at p(β). By Smale–Birkhoff, P_β has a horseshoe and the
  flow on the level has h_top > 0.

Numerically (CHECKED, not certified): Υ_θ = 15.0122754941, F_t = 1.637644, L″(3π/2) = −3.81969e−4, so
t′(0) = −1.00307e−3.

## 2. Hypotheses (each with its status)
- **(H1) MN analyticity.** The MN metric in the fleet transcription is real-analytic in (x, y, β) near the closure of
  the Kerr loop Γ₀. It is even in y; g₀ = Kerr. INHERITED (THEOREM_DRAFT (MN)).
  - **NOTE:** the Stage 1–2 L2 came from mel_gen, which is generated from the SAME mn_codegen as S2's field. A
    codegen error would therefore be SHARED between S2 and Step A. Tier 2a would cover both.
- **(H2) Kerr level.** (E, L) is an unstable, bound, inclined spherical Kerr level: r_u = 16, z_m = 1/2 and the
  (K1)–(K4) conditions. Certified level: Melnikov RESULT G1 (Krawczyk radius 1.6e−35; it contains (E, L, Q)).
  - The S2 PREREG uses the same (E, L) to all printed digits.
- **(H3) Simple outer turning point:** F_t ≠ 0 at r_t.
  - SURE from (K): r_t is a simple root of the radial potential.
  - CHECKED: F_t = 1.6376 at r_t = 47.5082 (x_t = 10.627044356577, which is control (i)'s certified Kerr p).
- **(H4) The first-order Melnikov formula (Robinson).** The displacement K_r(W^u_β) − K_r(W^s_β), on a transversal
  to Γ₀ at the point of phase ψ₀, is β M(ψ₀) + O(β²), with M = Υ_θ L′, analytic in (ψ₀, β).
  - **Thm 3.4 is used as a cited theorem; its hypotheses were checked at source (Quantum, 2026-11-27); Lemma 3.8's
    proof in [CR-mel] was not read.**
    - The read: C. Robinson, "Melnikov method for autonomous Hamiltonians", Contemporary Mathematics 198 (1996)
      45–53, DOI 10.1090/conm/198/02519; arXiv:math/9604239v1, §3, pp. 3–6. The volume, pages and DOI were confirmed
      by the Bridge at Crossref.
    - [CR-mel]: C. Robinson, "Horseshoes for autonomous Hamiltonian systems using the Melnikov integral", Ergodic
      Theory Dynam. Systems 8 (1988) 395–409, DOI 10.1017/S0143385700009500. It is the source of Lemma 3.8, and is
      not read by us.
  - **Matched against our setting:**
    - autonomous H^ε = H₀ + εH₁ + O(ε²) on a 4-dimensional space: our Mino-time K_β = Σ_Kerr(H_β + ½) on
      (r, θ, p_r, p_θ), analytic in β;
    - (A1), X₀ completely integrable with a second independent integral F: F = K_r;
    - (A2), a hyperbolic periodic orbit γ₀ with Γ₀ = comp[W^u∖γ₀] = comp[W^s∖γ₀] of dimension 2: the r_u = 16
      spherical orbit;
    - the energy level is fixed: γ_ε ⊂ (H^ε)⁻¹(h₀). Ours is the K_β = 0 level for every β.
  - **What is used:**
    - The DEFINITION M(z₀, h₀) = ∂_ε[F∘ζ^u − F∘ζ^s]|_{ε=0}, with ζ^σ = N_{z₀} ∩ W^σ(γ_ε, X^ε) and the manifolds
      depending differentiably on ε. This is exactly step 4's first-order displacement.
    - Thm 3.4 with Rem. 3.10: if DF ≡ 0 on γ₀, M is the ordinary improper integral ∫(DF·Y). This holds for us:
      dK_r = 0 at (r_u, p_r = 0), since r_u is a double root.
    - Thm 3.3 (a nondegenerate zero gives a transverse homoclinic orbit) is NOT needed. Step A concludes
      transversality through lemma A1.
  - **Adaptations and gaps, disclosed:**
    - (g1) Robinson's N_{z₀} is a 2-plane "perpendicular" to Γ₀ in the 4-dimensional space. Ours is a curve in Σ
      inside the level. Since W^σ(γ_ε) lie in the level, N ∩ W^σ = (N ∩ level) ∩ W^σ. The first order does not
      depend on the transversal: the Bridge's argument, an O(β²) change. Robinson does not state this.
    - (g2) Robinson does not define "nondegenerate zero" or "transverse"; we do not use them.
    - (g3) No smoothness class is stated; ours is analytic.
    - (g4) Lemma 3.8, which gives Thm 3.4, is proved in [CR-mel] (ETDS 8, 1988; above), which is NOT read by us.
      Thm 3.4 is used as a cited theorem, corroborated numerically (MELNIKOV c2; S1 to +0.014%).
  - Fable's potential form L (MELNIKOV.md §1) is derived from Thm 3.4. It was checked numerically, not by me at
    source.
  - Earlier status, superseded: "INHERITED: THEOREM_DRAFT §3 steps 1–3, citing Robinson, which Fable read.
  - CHECKED: MELNIKOV c2 (the bracket form equals the potential form at 6 phases), and S1 (splitting/β against
    4Υ|L2| to +0.014%).
- **(H5) Certified Fourier data:** L2 = [−4.77482114974644e−5 ± 6.81e−20]; L4 = [−5.31274262510e−10 ± 7.43e−22];
  T3 ≥ Σ_{m≥3} m²|L_{2m}|, with the margin |L2|.lower − 4|L4|.upper − T3.upper = +1.5242e−5.
  - Certified: RESULT.md Stages 1–2, and the mpmath recheck of the closing point.
  - The Melnikov THEOREM glue (Lean-side) is not used here.

## 3. Steps
1. **K_r on Σ (SURE).**
   - K_r = ½[Δ p_r² − P²/Δ + r²], with p_r = p_x/k, depends on (x, p_x) only.
   - At p_x = 0: ∂_{p_x} K_r = Δ p_x / k² = 0, and ∂_x K_r = k ∂_r K_r. So at p₀ = (x_t, 0) the gradient on Σ is
     ∇K_r = (k F_t, 0).
2. **β = 0 geometry (SURE).**
   - K_r is a Kerr integral, so Γ₀ ∩ Σ lies on the level curve {K_r = K_r(γ₀)}. Near p₀ this curve is the graph
     x = x_t + O(p_x²), with tangent (0, 1), by step 1 and (H3).
   - So t(0) = 0, i.e. v_x(0) = 0.
   - It crosses Fix R = {p_x = 0} transversally. That is the regularity of the half-BVP at β = 0 (equivalently
     v_px(0) ≠ 0). Control (i) certifies the same thing computationally: Krawczyk Z 2.96e−4, and v_px excludes 0.
3. **Persistence (SURE).**
   - The fixed point w_β and the analytic local unstable manifold depend analytically on β. The standard unstable
     manifold theorem with parameters applies (hyperbolic, λ_u ≈ 26.8).
   - R is reversing: R P_β R = P_β⁻¹. So R(w_β) is a fixed point of P_β near w₀ = R(w₀). The hyperbolic fixed
     point near w₀ is unique, so R(w_β) = w_β, and hence R(W^u_β) = W^s_β. A point p ∈ W^u_β ∩ Fix R satisfies
     p = Rp ∈ W^s_β, so it is homoclinic. (This wording follows the Bridge's read, replacing "orbit continuation".)
   - The function G(s, β) = p_x(P_β^m(w^u_β(s))) is analytic, with G(s*, 0) = 0 and ∂_s G(s*, 0) ≠ 0 (step 2). The
     IFT gives s(β), and hence p(β) ∈ W^u_β ∩ Fix R; this is claim (i).
   - Near p(β), W^u_β ∩ Σ is a graph x = x_p(β) + t(β) p_x + O(p_x²), with t analytic, by C¹-closeness to Γ₀.
   - Because R maps W^u_β to W^s_β, W^s_β ∩ Σ is the graph x = x_p(β) − t(β) p_x + O(p_x²).
4. **The slope from the Melnikov function (SURE, given (H4)).**
   - **The phase along Γ₀ ∩ Σ.** Take q ∈ Γ₀ ∩ Σ near p₀ with p_r = p_x/k small.
     - In Mino time, K₀ = K_r(r, p_r) + K_θ(θ, p_θ), so dp_r/dλ = −∂_r K_r = −F_t + O(p_r, r − r_t).
     - So q reaches its outer turning point after λ_t = p_x/(k F_t) + O(p_x²), and its phase is
       ψ₀(q) = ψ* + Υ_θ λ_t, i.e. dψ₀/dp_x = Υ_θ / (k F_t) at p₀.
     - The overall sign depends on the direction conventions and is not needed.
   - **The displacement along the horizontal transversal at fixed p_x.** By step 3 and step 1,
     K_r(W^u_β) − K_r(W^s_β) = k F_t · 2 t(β) p_x + O(β p_x², β²).
   - **By (H4)** it also equals β M′(ψ*) (ψ₀ − ψ*) + O(β p_x², β²) = β M′(ψ*) Υ_θ p_x / (k F_t) + ….
   - The displacement is analytic in (β, p_x) and vanishes at β = 0. Matching the β·p_x coefficients gives:

         t′(0) = Υ_θ M′(ψ*) / (2 k² F_t²) = Υ_θ² L″(ψ*) / (2 k² F_t²).

   - The pieces of the constant are: the parametrisation of Γ by the phase, dψ₀/dp_x = Υ_θ/(kF_t); the normal scale
     |∇K_r| = kF_t; and the factor 2, which comes from comparing W^u with its R-image W^s (slopes ±t).
5. **Nondegeneracy, made explicit (SURE, given (H5)).**
   - L″(ψ) = −8 Σ_{m≥1} m² L_{2m} cos(2mψ). At ψ* = 3π/2, cos(3mπ) = (−1)^m, so
     L″(3π/2) = 8L2 − 32L4 − 8 Σ_{m≥3} (−1)^m m² L_{2m}.
   - Hence |L″(3π/2)| ≥ 8(|L2| − 4|L4| − Σ_{m≥3} m²|L_{2m}|) ≥ 8(|L2|.lower − 4|L4|.upper − T3.upper)
     = 8 × 1.5242e−5 = 1.2194e−4 > 0.
   - The same bound holds at every kπ/2, since |cos| = 1 there.
   - **Disclosure:** Stage 2's PREREG named only L″(0). Applying its certified inequality at 3π/2 is a mathematical
     consequence of that inequality, not a rerun, and it introduces no new certified number.
   - **Remark (no other zeros).** M(ψ) = −4Υ_θ Σ m L_{2m} sin 2mψ, and |sin 2mψ| ≤ m|sin 2ψ|. So
     |Σ_{m≥2} m L_{2m} sin 2mψ| ≤ (4|L4| + T3)|sin 2ψ| < |L2||sin 2ψ|. M vanishes only where sin 2ψ = 0, which is
     exactly S1's four zeros.
6. **Conclusion (SURE).**
   - With Υ_θ ≠ 0, F_t finite and nonzero (H3), and step 5, t′(0) ≠ 0. So t(β) = t′(0) β + O(β²) ≠ 0 for
     0 < |β| < β₀, on both sides.
   - v_px(β) ≠ 0 by continuity from step 2, and v_x = t v_px ≠ 0.
   - Lemma A1 (PREREG A1; v and Rv independent) then gives transversality. Smale–Birkhoff gives the horseshoe on
     Σ, and h_top > 0 for the flow; the time change dτ = Σ dλ preserves positivity on a compact invariant set
     (THEOREM_DRAFT step 5).

## 4. Numerical cross-check of the constant (CHECKED; float; not part of the proof)
- **Predicted** t′(0) = −1.00307e−3 (mpmath, 30 digits, from the certified L2 and L4, Υ_θ, and F_t at the Kerr x_t).
- **Float records** (s2f_sym.json, DOP853):
  - t/β = 1.01189e−3 at β = 1e−2, and 1.04194e−3 at β = 3e−2;
  - the linear extrapolation to β = 0 is 0.99686e−3, a 0.6% difference;
  - the β = 0 float run has |t| = 5.2e−8 ≈ 0.5% of t(1e−2), so the agreement is at the noise level.
- **Sign:** S2's certified v_x > 0 and v_px < 0 give t < 0, matching the predicted sign. The sign conventions in step 4
  were not independently fixed, so this is "consistent", not "checked".
- **A rigorous t(β) at β = 3/100**, from S2's enclosures: v_x / v_px ∈ [−3.1494e−5, −3.1338e−5]; t/β ≈ −1.0e−3.

### 4b. A second derivation of the constant (Neon, 2026-11-27; the source is UNVERIFIED maths; it is consistent)
- **Neon's formula.** Neon derived it without seeing this note, using Δx(p_x, β) = x_u(p_x, β) − x_u(−p_x, β), which
  is odd because W^s = R W^u:

      v_x′(0)/v_px(0) = M_K′(ψ₀) / (2 ∂_xK(z₀) γ′_px(ψ₀)).

- **Its hypotheses:**
  - a C² reversible area-preserving family;
  - a C² first integral K with K∘R = K;
  - a hyperbolic fixed point with a symmetric homoclinic loop;
  - ∂_xK(z₀) ≠ 0;
  - M′(ψ₀) ≠ 0.
- **The reference it gives:** Delshams & Ramírez-Ros, Nonlinearity 9 (1996) 1–26, DOI 10.1088/0951-7715/9/1/001.
  The Bridge confirmed the DOI at Crossref; I have NOT read the paper.
- **Agreement.** With ∂_xK = kF_t (step 1) and γ′_px = dp_x/dψ₀ = kF_t/Υ_θ (the inverse of step 4's phase map),
  Neon's formula is t′(0) = Υ_θ M′/(2k²F_t²). That is the same constant and the same factor 2. The Bridge checked
  this mapping.
- **Status.** This is a consistency check, not a proof input.

## 5. What Step A does NOT give
- β₀ is NOT explicit. Nothing at a given β except through S2 (β = 3/100). Step A does not join S2's point, because
  β₀ is unknown.
- Other levels: only through THEOREM_DRAFT's Corollary B, which is open on (r_u, z_m, a/M) and is not part of this note.
- An independent check of the field: (H1) is shared with S2. Tier 2a would cover both.

## 6. For the non-author reader
1. Step 4's matching argument, and the factor 2 (the R-image comparison) in particular.
2. Whether (H4)'s "transversal at phase ψ₀" may be taken as the horizontal line in Σ at fixed p_x. I take the first
   order as independent of the choice of transversal (THEOREM_DRAFT §3 step 3; Robinson not read by me).
3. Step 3's claim R(γ_β) = γ_β, by uniqueness of the hyperbolic continuation.
4. That Stage 2's PREREG named only L″(0); the same certified inequality covers L″(3π/2) (step 5).
