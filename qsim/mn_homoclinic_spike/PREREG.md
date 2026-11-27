# MN transversal-homoclinic spike: pre-registration (S1 and S2)

Status: REGISTERED before any spike code or number exists. Sumit said yes to the small tests, relayed by the Bridge on
2026-11-27. The chaos thread is reopened ONLY for this spike, under its own stop rules. Written by Claude Opus 5.5
(office "Quantum"). Sources: the Neon T61 review (qsim/capd/horseshoe/NEON_T61_REVIEW_2026-11-27.md) and the Melnikov
record (qsim/mn_melnikov/RESULT.md; fable_work/mn_melnikov/{SETUP,MELNIKOV,THEOREM_DRAFT}.md).

## Value (why this is worth ≤ 20 core-h)
- **What it could prove.** A computer-assisted proof of a transversal homoclinic orbit for the MN geodesic flow at one
  fixed β gives positive topological entropy (chaos) by Smale–Birkhoff, with no box covering.
- **Why here.** Our certified Melnikov result (L2 ≠ 0) already says that small β breaks Kerr's homoclinic loop
  transversally, and it fixes where to look.
- **Why a spike.** The risk is conditioning: the splitting is ~β·|M| with |M| ≈ 2.9e-3. S1 measures that risk in
  floating point for ~1–3 core-h. S2 makes one rigorous attempt only if S1 says GO.
- **On STOP.** The thread closes again with a write-up.

## Setting (fixed)
- **Base point.** The Melnikov point (M, a, r_u, z_m) = (5, 3, 16, 1/2): MN `mine(5, 3, β, E, L)` (qsim/capd/horseshoe/
  mn_s5_gate.py), chart (x, y) with r = M + kx and k = 4.
- **Level.** E = 0.93528150456799871854, L = 12.972532035607280691 (RESULT.md G1), mass shell H = −1/2, the same (E, L)
  for every β.
- **Constants.** Υ_θ = 15.0122754941206972, L2 = −4.77482114974644e-5 (certified), L4 = −5.31e-10.
- **K_r** = ½[Δ p_r² − P(r)²/Δ + r²], with p_r = p_x/k, Δ = r² − 2Mr + a², P = E(r² + a²) − aL (SETUP.md §1).
- **Mino time:** dλ = dτ/Σ, Σ = r² + a²y².
- **Prediction** (MELNIKOV.md §0.2–3, §7): ΔK_r(ψ0) := K_r(W^u) − K_r(W^s) at the outer turning point with θ-phase ψ0,
  = β·(−4Υ_θ Σ m L_2m sin 2mψ0) + O(β²) ≈ β·2.8672e-3·sin 2ψ0. The overall sign is UNSURE in the source.

## S1: float only (budget ≤ 3 core-h; time box: 2026-11-27)
- **Method** (`s1.py`, DOP853 at rtol = atol = 1e-13, float64).
  1. The periodic orbit γ_β is a fixed point of the y = 0, ẏ > 0 return map P on the shell. Newton from (x, p_x) =
     (2.75, 0); eigenvalues λ_u and 1/λ_u.
  2. W^u: 64 points across one fundamental domain, fp + s·v_u with s ∈ [s0, λ_u s0) and s0 = 1e-7 on the outward
     branch. Each is integrated forward to the first outer turning point (p_x: + → −, with x well above x_u). There I
     record K_r and ψ0, the Mino θ-phase measured from the last z = +z_m turning point (ψ = 0 there).
  3. W^s: the same by backward integration from fp + s·v_s. As a cross-check only (not a criterion), the reversor
     (x, y, p_x, p_y) ↦ (x, −y, −p_x, p_y).
  4. ΔK_r(ψ0) on a common ψ0 grid by periodic interpolation, then a least-squares fit c0 + Σ_{n≤4}(a_n sin nψ0 +
     b_n cos nψ0). The measured amplitude A(β) is the sin 2ψ0 coefficient after aligning phase to the turning-point
     definition.
  5. **cond(DF).** At a transverse zero of ΔK_r, take the section-map multiple-shooting operator (the CKMJ Lemma-19
     structure on the energy-eliminated section). Unknowns: (s_u, z_1, …, z_{n−1}, s_s). Equations: z_1 = P(w_u(s_u)),
     z_{i+1} = P(z_i), w_s(s_s) = P(z_{n−1}), with w_{u,s}(s) = fp + s·v_{u,s} (unit vectors) and n the number of section
     returns. DF is its 2n × 2n Jacobian, and cond(DF) is the 2-norm condition number.
- **β values:** 1e-4, 3e-4, 1e-3, 3e-3, 1e-2 and 3e-2, plus the β = 0 control.
- **Gates** (any failure = INVALID, no reading):
  - **G-norm:** at 8 on-shell points, mine's H at β = 0 equals mel_gen.H0, and its central β-difference (h = 1e-6)
    equals mel_gen.Hb, both to 1e-6 relative. This confirms that our β is the Melnikov β.
  - **G-Kerr:** at β = 0, |ΔK_r| ≤ 1e-9 at every sample, and K_r is conserved along a W^u orbit to 1e-9.
  - **G-fp:** |P(fp) − fp| ≤ 1e-11 at every β.
- **S1 reading (fixed now):**
  - **GO** iff BOTH of these hold:
    - (a) |A(β_min)/β_min| is within 10% of 2.8672e-3 at the smallest β (1e-4), with |A/β| varying by ≤ 20% from 1e-4
      to 1e-3, so the β-scaling is linear. The sign is reported, not a criterion.
    - (b) cond(DF) ≤ 1e8 at some β ≥ 1e-2.
  - **Otherwise STOP:** write it up and close the thread.
  - "Splitting/β within 10% of L2" (the Bridge's wording) is (a), with the Melnikov amplitude 4Υ_θ|L2| = 2.8672e-3 as
    the operational target.

## S2: one rigorous attempt (budget ≤ 15 core-h; time box ≤ 2 days after the Bridge's go; only after S1 = GO)
- **Method.** At the best β from S1 (smallest cond(DF) with β ≥ 1e-2), CAPD C¹ with MPFR:
  - a rigorous hyperbolic periodic orbit (Krawczyk on P);
  - rigorous local manifolds (cone conditions or a parameterisation-method bound);
  - then Capiński–Kepley–Mireles James (arXiv:2205.03922) Thm 16 + Lemma 19 + §7.1 Newton–Krawczyk.
  - The design is detailed in an S2 amendment before any S2 code runs.
- **S2 GO (a certificate)** iff the Krawczyk contraction is certified AND the Kerr control items (i) and (ii) pass.
  Otherwise STOP.
- **Kerr control (symmetric; the same code and settings, only β = 0):**
  - **(i) Must-not-certify.** A transversality certificate at β = 0 STOPS the MN claim (an F7 analogue).
  - **(ii) Positive non-isolation.** Free the homoclinic's section coordinate as a parameter and validate two distinct
    zeros. That rigorously exhibits a 1-parameter family of connections (W^u ∩ W^s not isolated), so the control reads
    "supported", not "undecided".
  - **(iii) Sabotage must-fire.** Drop one β term from the field: the certificate must change or fail.
  - **(iv) Positive control of the validator.** Reproduce one published transverse homoclinic (CKMJ Thm 3, the PCRTBP
    L4 homoclinic) with our code.
- **What a GO would give.** A qualitative chaos proof (h_top > 0) for MN at that one β and orbit family. No entropy
  bound is claimed.

## Budget and conduct
- **Budget.** ≤ 20 core-h total (S1 ≤ 3, S2 ≤ 15, controls included). Overruns are reported, never silently extended.
- **Conduct.**
  - Mac mini, 1 core, nice 10, detached. No caps (Sumit's rule). Anything over ~10 min checkpoints its per-β results.
  - Memory is declared as footprint (S1: ≤ 300 MB).
  - Neon's cost numbers carry zero weight.
  - S2 starts only on the Bridge's go after it has seen S1.

**Setup correspondence (labelled addendum; the commit gate's request, before any code).**
- The claim tested is "the MN quadrupole breaks Kerr's r_u = 16 homoclinic loop transversally, with splitting
  amplitude 4Υ_θ|L2| per unit β, and the BVP for one transverse homoclinic is well enough conditioned to certify".
- S1 runs at exactly the Melnikov condition: (M, a) = (5, 3), r_u = 16, z_m = 1/2, (E, L) as certified in RESULT.md G1,
  and the same MN β-family, which G-norm checks.
- Only β takes the listed small values. S2 would run at one β chosen by S1, at the same (M, a, E, L).

---

# S2 AMENDMENT (written 2026-11-27 after S1 = GO, cc25e62; before any S2 code; S2 runs only on the Bridge's word)

Written by Claude Opus 5.5 (office "Quantum"). The float design numbers and the float pre-run of every control are in
`s2f.py` (outputs `s2f_*.json` / `s2f_*.out`) and `ckmj_l4_float.py` (`ckmj_l4_float.json`). Superseded pre-run
variants are kept (`*_superseded.*`). Nothing in this section is rigorous.

## A1. What changed from the S2 sketch above, and why
- **Formulation: the R-symmetric half BVP.** It replaces the two-ended multiple shooting.
  - R: (x, y, p_x, p_y) ↦ (x, −y, −p_x, p_y) is an exact reversor of the field. H is even in p, and g^xx, g^yy, V
    are even in y. Checked at β = 3/100 at 20 random points at 50 digits: max relative difference 5e-51. S2-1
    re-checks this symbolically. It maps the section
    Σ = {y = 0, ẏ > 0} to itself as (x, p_x) ↦ (x, −p_x), and conjugates P to P⁻¹.
  - fp ∈ Fix R (p_x(fp) ≈ 1e-14), and R v_u = v_s (float), so W^s(fp) = R W^u(fp).
  - The ψ0 ≈ 3π/2 homoclinic has its outer turning point ON Σ ∩ Fix R = {p_x = 0}, so it is R-symmetric.
- **Lemma (proved here; elementary).** Let p ∈ W^u ∩ Fix R on Σ, and let v = (v_x, v_px) be the tangent of W^u at p.
  - The tangent of W^s = R W^u at p is Rv = (v_x, −v_px), and det[v, Rv] = −2 v_x v_px.
  - So W^u ⋔ W^s at p (within the energy level) ⟺ v_px ≠ 0 AND v_x ≠ 0.
  - v_px ≠ 0 is exactly the isolation of p as a zero of the half BVP. v_x ≠ 0 is a separate sign test.
  - At β = 0 (Kerr), W^u = W^s forces v ∥ Rv, so v_x = 0 EXACTLY. The half BVP still isolates p there: the Kerr loop
    crosses Fix R perpendicularly.
- **Why this is better.** The small quantity (transversality ~ β·|M|) no longer sits inside the Krawczyk operator
  (two-ended form: σ_min 3.7e-5, ‖A‖∞ 4.3e4). It becomes a sign test on v_x, and the half BVP is well conditioned at
  every β (cond 31, ‖A‖∞ 1.7).
- **Unchanged:** β, the orbit, (M, a, E, L), the budget, CKMJ Lemma 19 (the multiple-shooting structure) and Thm 30
  (Newton–Krawczyk). CKMJ Thm 16 (the unfolding) is not needed for the MN claim: the energy is eliminated on Σ, and
  transversality on Σ is transversality in the level set. The unfolding returns in control (ii).

## A2. The ψ0 ≈ 3π/2 conditioning (the Bridge's question): explained as a section artifact
- **cond(DF) is independent of n.** Shifting s_u by λ^±1 changes n by 1 and cond by < 10% at all four zeros.
- **The field's exact symmetry S** (x, y, p_x, p_y) ↦ (x, −y, p_x, −p_y) maps the π/2 homoclinic onto the 3π/2 one
  (z → −z), so the two are equally transverse.
  - S swaps Σ↑ = {ẏ > 0} and Σ↓ = {ẏ < 0}.
  - Measured at β = 1e-2: the π/2 orbit has cond 2.2e7 on Σ↑ and 2.3e6 on Σ↓; the 3π/2 orbit has 2.3e6 on Σ↑.
- **So the 10× belongs to the (orbit, section) pair, not the orbit.**
- **Mechanism, a hypothesis:** the 3π/2 orbit crosses Σ↑ at its outer turning point, where W^u and W^s separate most.
  That is also what makes the symmetric reduction possible on Σ↑. With the A1 formulation, the asymmetry no longer
  matters for conditioning (cond 31 for the half BVP).

## A3. Fixed S2 setting
- **β = 3/100 exactly**, at the S1 zero ψ0 ≈ 4.695 (≈ 3π/2), on Σ↑. (M, a) = (5, 3).
- **(E, L):** the decimal strings in "Setting", as exact rationals. Mass shell H = −1/2.
- **Float target:** m = 7 section returns from w_u(s_u), s_u ≈ 1.6405e-9 (two fundamental domains before the S1
  point), to p ≈ (10.582227722087, 0). The transversality ratio |v_x|/|v| is 3.1258e-5 (1.0119e-5 at β = 1e-2:
  linear in β).
- **Unknowns:** X = (s_u, z_1, …, z_6) ∈ R¹³.
  - Equations: z_1 = P(w_u(s_u)), z_{i+1} = P(z_i), and p_x(P(z_6)) = 0 (13 equations).
  - Shooting nodes: the 7 section returns (one segment per return). Each return is integrated adaptively inside CAPD.

## A4. Local manifold and its order
- **Cone conditions** (Zgliczyński, "Covering relations, cone conditions and the stable manifold theorem",
  JDE 246(5) (2009) 1774–1819; venue matched on Crossref in the T61 review) for P at fp, on a box of
  half-width δ = 1e-7 in eigen-coordinates. This needs C¹ only.
- **W^u_loc** is a graph over the v_u direction with slope |h′| ≤ L. The endpoint is w_u(s_u) ∈ fp + s_u v_u + [−L s_u, L s_u] v_s,
  and its tangent lies in the cone.
- **Float estimate:** L ~ (‖D²P‖/λ) δ ≈ 3e-6, so the endpoint enclosure width is ≈ 5e-15. That is far below the
  Krawczyk ball (§A6).
- **Errors in the initial tangent direction** along v_s are contracted by λ^−7 ≈ 1e-10 relative to the v_u part.
- **This is parameterisation order 1** (linear + Lipschitz cone tail). No higher order is needed because s_u ≤ δ/50.
  - If S2-0 shows the cones fail at δ = 1e-7, the registered fallback is δ = 1e-8 with s_u shifted one more
    fundamental domain (m = 8).

## A5. Precision: MPFR (CAPD multiprecision intervals, 128-bit mantissa), Taylor order 20, for EVERY run (MN and controls)
- **My estimate from S1, two-ended form at β = 3e-2.** Radii-polynomial closure needs ε_res < (1 − Z)²/(4‖A‖²‖D²F‖)
  = 1.6–1.8e-13 (‖A‖∞ 4.3e4, ‖D²F‖∞ 7–8e2). Double stalls at ‖F‖ 3–5e-13. So that form needs better than double,
  but only by ~3×. Neon's 1e-15–1e-17 was for β = 1e-2 with guessed ‖D²F‖.
- **The half BVP needs nothing beyond double** for Krawczyk (cond 31). The precision now matters in two places:
  1. **The sign test.** v_x/|v| = 3.1e-5 against a float noise floor of 5.2e-8 (the β = 0 value, where the truth is
     0). The margin is 600× in float. Interval wrapping of the 7-matrix tangent product could eat an unknown part of
     that in double intervals. MPFR removes the doubt.
  2. **Control (ii)'s meeting system.** It needs ε_res < 1/(4‖A‖²‖D²F‖) ≈ 6e-13 with ‖A‖∞ ≈ 2e4, which is beyond
     double.
- **The same precision runs everywhere** (the same-method rule).
- **Fallback, decided only by S2-0's measured numbers:** double intervals (CAPD DInterval) are allowed for ALL runs if
  BOTH of these hold:
  - MPFR projects over budget;
  - S2-0's double-interval width of v_x at β = 3e-2 is ≤ 1/100 of |v_x|.

## A6. S2 stages, PASS/FAIL (all rigorous, CAPD C¹; checkpoint after each stage; no caps)
- **S2-0, the cost and feasibility gate (first, before anything else).**
  - Steps: one rigorous MPFR C¹ return at β = 3e-2 of (a) the cone box at fp, and (b) a point-sized set on the
    longest homoclinic return (the outer excursion, τ ≈ 540).
  - Measured: wall time, and the widths of P and DP.
  - Projection: (measured cost per return) × (the ~40 returns listed in A8).
  - **GO iff** the projection is ≤ 14 core-h (the 15 minus S2-0 itself) AND the DP width is ≤ 1e-8 (relative).
  - **Otherwise STOP and report.** Budget changes are Sumit's.
  - The F5-R figure (≥ 122 core-h per 1e-7 box per return) is NOT assumed to transfer: that orbit has two close
    periapsis passages, and this one stays at r ≥ 16. It is measured.
- **S2-1, the periodic orbit:** Krawczyk for P(w) − w on a ball around fp. It must close.
- **S2-2, the cone conditions** at fp (A4). They must verify.
- **S2-3, the half BVP:** CKMJ Thm 30 on X ∈ R¹³, with the radius r chosen per the radii polynomial. It must close.
- **S2-4, the transversality sign test:** the interval enclosure of v_x (tangent of W^u at p, from the C¹ data of
  S2-2/S2-3) must EXCLUDE 0. v_px ≠ 0 is already implied by S2-3.
- **MN GO (a certificate)** iff S2-0 … S2-4 all pass AND controls (i)–(iv) pass. Anything else = STOP.
- **What a GO proves:** a transverse homoclinic point of P (MN, β = 3/100, at that level). Smale–Birkhoff then gives
  a horseshoe for P, so h_top > 0 for the flow on that level. It is qualitative, at one β and one orbit family.

## A7. Symmetric Kerr control (the same code and settings; only the field or β changes), with float pre-runs done
- **(i) Must-not-certify (an F7 analogue).** At β = 0, run S2-1 … S2-4 identically.
  - S2-3 is EXPECTED to close (Kerr's symmetric homoclinic exists). It is reported, and it is not a failure.
  - **PASS iff** the v_x enclosure CONTAINS 0 (the exact value is 0).
  - An enclosure excluding 0 at β = 0 is a bug: STOP the MN claim.
  - *Float pre-run:* |v_x|/|v| = 5.18e-8 at β = 0 (noise), against 3.13e-5 at β = 3e-2. K_r(p) − K_r(fp) = 5e-13 at
    β = 0 (Carter conserved). The two-ended form at β = 0 has cond 1.7e9 to 9.3e9 and a radii-polynomial
    discriminant ≈ −4e8 to −1.7e9: it cannot close (`s2f_ctl_i.json`).
- **(ii) Positive non-isolation.** At β = 0, with c = s_u FIXED on a small interval I = [c1, c1(1 + 1e-6)], solve the
  meeting system.
  - The system: a forward chain from w_u(c) (m = 5 returns) meets the R-image of a forward chain from w_u(c′), via
    P(z_4) = R P(z′_4) + α g, with g = ∇K_r/|∇K_r| at the meeting point.
  - Unknowns: (z's, z′'s, c′, α). The meeting is at the outer crossing, where |∇K_r| = O(1).
  - **The proof:**
    - a uniform contraction over c ∈ I (van den Berg, Breden, Lessard & Murray, JDE 264 (2018) 3086–3130,
      arXiv:1702.07412, Thm 3/Thm 4; checked at source) gives a continuous branch of zeros;
    - Carter conservation (exact in Kerr; K_r is R-invariant, and K_r = K_r(fp) on W^u) plus a rigorous lower bound
      on ∇K_r·g over the ball give α ≡ 0;
    - so an ARC of homoclinic points exists: W^u ∩ W^s is not isolated. **PASS iff** certified.
  - *Float pre-run (`s2f_ctl_ii.json`):*
    - at β = 0, |α| ≤ 2.0e-13 at 8 values of c across one fundamental domain, with cond 2.0e5 to 6.2e5 and
      ‖A‖∞ ≈ 1e4 to 2e4;
    - at β = 3e-2, the same system gives α(c) up to 1.6e-5, with 4 sign changes per domain (the four zeros of
      sin 2ψ0). That is the required transition.
    - Three superseded variants are kept (a shallow end with linear-W^s error; a deep end where ∇K → 0 at fp; a
      narrow c′ grid).
- **(iii) Sabotage must-fire.** At β = 3e-2, with the field minus ONE β term (the 3β²(P3² − P2²)/R⁶ term of G):
  - **PASS iff** the certified enclosure of p (or of v_x) is DISJOINT from the true-field one ("the certificate
    changes"). It does not matter whether the sabotaged field also certifies.
  - *Float pre-run (`s2f_ctl_iii.json`):* p moves 1.30e-6 and v_x/|v| by 0.47%, against an expected ball ≲ 1e-10.
    A gross sabotage (ψ = 0) moves p by 4.2e-2.
- **(iv) Positive control of the validator.** With the same Krawczyk core, C¹ integrator, precision and cone code,
  reproduce CKMJ Thm 3 (arXiv:2205.03922v2 §7.4: PCRTBP, µ = 1/2, c = 3, the L4 homoclinic, p̄ from Table 4,
  r = 1.659e-9).
  - An L4 front end is needed: the local 2-D W^{u,s}(L4) by cone conditions, then a two-ended BVP. This is the one new
    code path.
  - **PASS iff** our certified point's orbit passes through B(p̄, 1.66e-9), or our certified ball intersects it.
  - *Float pre-run (`ckmj_l4_float.json`):*
    - E(p̄) = 3 + 2.6e-11 (p̄ is printed to 15 digits);
    - integrated backward, the orbit reaches 9.2e-6 of L4 at t ≈ 14.7;
    - integrated forward, it passes m2 at 0.043 and reaches 9.3e-6 of L4 at t ≈ 25.2.
    - So p̄ is on an L4 homoclinic in our coordinates (CKMJ eqs. 26–27).
- **Pre-run status (control-clause rule 1):** each control has been pre-run once in float, and each transitions as
  required. The rigorous versions run inside S2, on the Bridge's word.

## A8. Budget, time, stop rule, remaining limits
- **Budget:** ≤ 15 core-h for all of S2, the controls included.
- **Rough return count:**
  - MN: fp 1 + cones 1 + half BVP 7 ≈ 9;
  - (i): 9;
  - (ii): 2 × 5 per uniform-contraction box, a few boxes;
  - (iii): 9;
  - (iv): small (CKMJ report < 1 min in CAPD).
  - Total ≈ 40 returns.
- **Time box:** ≤ 2 days from the Bridge's go.
- **Stop rule:**
  - S2-0 projection > 14 core-h → STOP.
  - Any stage or control FAIL → STOP.
  - Overruns are reported, never silently extended. Budget changes are Sumit's.
  - On STOP, a write-up and the thread closes.
- **Conduct.** Mac mini, 1 core, nice 10, detached, checkpoint per stage. Memory footprint declared at S2-0
  (expected ≤ 1 GB). A slot request goes to the Bridge first.
- **Remaining limits:**
  - NO wall-clock watchdog, alarm or iteration cap ends a job.
  - The plunge guard (x < 1.5, r < 11) is a domain guard and returns "left the domain". It is not a time cap.
  - The only stops are the registered FAILs above.

## A9. T61b, checked at source on 2026-11-27 (arXiv abs/PDF and Crossref)
- **CKMJ (arXiv:2205.03922v2): all correct.**
  - Thm 16, Lemma 19, Thm 30 (§7.1 Newton–Krawczyk, Zr − r + Y ≤ 0).
  - §7.4 Thm 3: r = 1.659e-9, ‖AF‖ ≤ 1.643e-9, Z ≤ 0.0098.
  - App. B: N = 12, tail ≤ 1.4e-13.
  - §7.2: 50 + 200 + 50 = 300 IntLab steps, T ≈ 2.427.
  - §7.5: m = 8.
- **Murray & Mireles James (arXiv:2212.00930).**
  - Thm 2.11 (the radii polynomial, as quoted), Lemma 3.4 (the βu unfolding BVP), §5 Thms 5.1–5.2 (K = 30, N_t = 6,
    r_P̄ 1.076e-12 to 2.154e-12, M = 4–9 Chebyshev domains), App. A eqs. 45–47: all exist.
  - Slip: the smallest C⁰ bound is 1.626e-9 (Thm 5.1), not 1.89e-9.
- **van den Berg, Breden, Lessard & Murray.** arXiv:1702.07412 = JDE 264 (2018) 3086–3130.
  - Thm 3 (uniform contraction), Thm 4, Props 6/13/22, Lemma 14 and eq. (4.31) exist, and the 7,960 proofs are real.
  - BUT they cover β ∈ [0.5, 1.9] of the suspension-bridge equation, driven by Chebyshev decay. They are not "near
    a singular point" (Neon's framing is wrong).
- **Breden, Lessard & Vanicat (arXiv:1511.01414):** Thm 3 exists (in their pseudo-arclength set-up).
- **arXiv:2609.22689:** real. Breden & Hénot, "Efficient Rigorous Continuation via Chebyshev Series Expansion I"
  (2026-09-19).
- **doi:10.1137/25M1748275:** real. Church, Dai, Hénot, Lappicy & Vassena, "Global Continuation of Stable Periodic
  Orbits in Systems of Competing Predators", SIADS 25(3) 1697–1725 (2026). Neon gave no authors, and it is only
  generally relevant.
- **doi:10.3934/dcds.2024086:** real and on topic (L3 homoclinic breakdown, the Stokes constant). The AUTHORS ARE
  WRONG: it is Baldomá, Capiński, Giralt & Guardia, DCDS 45(1) 56–88 (2025), not "Capiński, Guardia, Martín, Seara &
  Zgliczyński 2024".
- **The Δ² argument is sound for the two-ended form.** It is the radii-polynomial discriminant with ‖A‖ ~ 1/σ_min.
  The measured requirement at β = 3e-2 is 1.6–1.8e-13 (A5). It does not apply to the half BVP (A1).

## A10. Gate paragraph, kill criteria and operations (labelled addendum, 2026-11-27)
This applies the fleet practices adopted 2026-11-27 (TheBridge/fleet/PRACTICES_2026-11-27.md). S2 can exceed 12 h on
one core, so it needs the gate. Where A10 is stricter than A6/A8, A10 wins. Nothing above is edited.

- **What it decides.**
  - **GO:** MN at β = 3/100, (M, a) = (5, 3), at the Melnikov level, has a rigorous chaos certificate (a transverse
    homoclinic point, so h_top > 0). The chaos write-up (c67126e) then changes from "MN covering STOP, no MN chaos
    certificate" to "MN chaos proved (qualitative, one β)". That also decides whether the parked MN outreach has
    a result to carry.
  - **STOP:** the MN chaos question closes for good with a write-up. No further routes are opened without Sumit.
- **Cost.**
  - The pilot is S2-0. It measures time and true memory (phys_footprint of the process tree) per rigorous return,
    then projects P over the ~40 returns in A8.
  - Outside view from our own record:
    - S1 planned 1–3 core-h and used ≈ 2 (×1), but needed 3 bug reruns.
    - kerr_e was planned at 48 h and projected after launch at 21–61 days per covering (×10–30). That was a cost
      that GREW with the run, through bisection depth.
  - S2 is a fixed list of returns with no bisection, so kerr_e's growth mode doesn't apply. The
    bug-and-rerun mode does. **I use ×3.**
  - **S2-0 GO therefore needs P ≤ 5 core-h** (×3 ≤ 15). This replaces A6's "≤ 14". If P is 5–14, I report to the
    Bridge and do not proceed without a re-gate.
- **Premortem.** "If S2 is wasted, the most likely reason is that MN interval over-widening (10–1700× on F5-R)
  makes the C¹ enclosure of the long excursion return too wide, so the v_x sign test or the Krawczyk ball cannot
  close." That is exactly what S2-0 (b) measures first, for under ~1 core-h.
  - Second most likely: the new L4 front end for control (iv) grows into its own project. Its stop rule: if (iv) is
    not certified within 3 core-h or by the S2 date below, S2 STOPS (no MN claim without (iv)).
- **Dependencies.** Three pieces are NOT yet shown to work:
  1. **The cone-condition code is new.** Self-test before use: at β = 0, the certified W^u_loc enclosure must contain
     the exact Kerr curve {K_r = K_r(fp)} ∩ (box). Must-fire: with the slope bound L halved below the true slope,
     the cone check must fail.
  2. **The half-BVP Krawczyk is new.** Tested by controls (i) and (iv) and by sabotage (iii).
  3. **The L4 front end is new.** Tested by (iv) itself.
  - Already tested: CAPD MPFR-128 C¹ integration on the Mac mini (the horseshoe work; the CAPD trust replays).
- **Kill criteria: a state AND a date.**
  - **Good enough:** S2-1 … S2-4 PASS and controls (i)–(iv) PASS. Then write it up and stop: no other β, no entropy
    bound, no other orbit.
  - **Stop:** if by **2026-11-30 24:00 IST**, or 2 days after the Bridge's go (whichever is earlier), that state is not
    reached, S2 STOPS with a write-up (or a fresh short plan goes to Sumit).
  - Also STOP on:
    - S2-0 P > 5 core-h without a re-gate;
    - any stage or control FAIL;
    - a total over 15 core-h.
- **Per-stage "good enough / stop".**

  | Stage | Good enough | Stop |
  |---|---|---|
  | S2-0 | Cost, widths and footprint measured, P ≤ 5 | P > 5, or relative DP width > 1e-8 |
  | S2-1 | The fp ball certified | Krawczyk does not close at 3 radii |
  | S2-2 | Cones verified at δ = 1e-7, or 1e-8 (the A4 fallback) | Both fail |
  | S2-3 | Zr − r + Y < 0 certified | Not at any r of the radii polynomial |
  | S2-4 | 0 ∉ [v_x] | 0 ∈ [v_x] |
  | (i) | 0 ∈ [v_x] at β = 0 | 0 ∉ [v_x] → STOP the MN claim |
  | (ii) | Arc certified | Not certified |
  | (iii) | Enclosures disjoint | Not disjoint |
  | (iv) | CKMJ ball met | Not met |

- **Check-in at ~25%.** After S2-0 gives P, when 0.25·P core-h have been spent, compare the actual cost per return
  with S2-0's. If the projection now exceeds 2P, pause my own verified PIDs and re-gate with the Bridge before
  continuing.
- **Operations.**
  - Mac mini only, not the Air: the libraries are tested here and the cores are faster (the Bridge, 2026-11-27).
  - A slot request to the Bridge before S2-0 and again before the parallel stage.
  - S2-0 runs on 1 core. After it, up to 4 single-core jobs may run concurrently (the MN chain, (i), (iii), (iv)),
    within the fleet's 8-core limit and the ~5 spare cores.
  - Everything at nice 10, detached (tools/detach.sh) and checkpointed per stage.
  - Pause-only guards, no caps. Memory declared from S2-0's phys_footprint.
