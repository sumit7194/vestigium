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

## A11. The re-gate decision after S2-0, and the parameters S2-0 forced (labelled addendum, 2026-11-27)
- **The Bridge's decision (local_5890ca6a, 2026-11-27): option (A), as registered.**
  - It keeps the stronger control (iii): the sabotaged field is re-certified, and its enclosures must be DISJOINT
    from the true-field ones.
  - Reasons: (A) and (B) differ by ~1.4 core-h on otherwise idle Mac mini cores; rigour wins over the cheaper variant;
    and the spike as Sumit approved it was "≤ ~20 core-h with stop rules" in total. S1 ≈ 2 + S2-0 0.65 + S2 ≈ 6.5
    projected makes ≈ 9.
- **Budget mechanics.** These replace A10's "×3 must be ≤ 15":
  - The ACTUAL spend cap for the rest of S2 is **12 core-h measured**. If it is reached, pause my own verified PIDs
    and report. Never kill.
  - **25% check-in:** re-gate if the projection exceeds 2 × 6.5 = 13 core-h.
  - **(iv) L4** (unmeasured): pause and report if it passes 1.5 core-h.
  - **Kill date: 2026-11-29 15:00 IST.**
- **Measured basis** (S2_0_RESULT.md, 6797c1f; all MPFR-128, order 20):
  - unit costs: C¹ near-fp return 306 s, C¹ τ ≈ 381 return 593 s, C⁰ point 110 s;
  - Kerr ≈ 0.59× that;
  - 23 MB per job;
  - widths linear in the set size.
- **Parameters forced by S2-0** (methods unchanged):
  - **Step tolerance 1e-24** (absolute = relative) for EVERY S2 run. It is step control only.
  - **Krawczyk balls** r ≈ 4·Y, expected ~1e-16 to 1e-17.
  - **Nodes:** s_u ≈ 2e-12 (two more fundamental domains), so m = 9: X ∈ R¹⁷ for the half BVP.
  - **Cone box δ = 1e-9** (not 1e-10), so that the reach δ* of the lemma below exceeds |ū| + r with margin.
  - **x̄ refinement:** one quasi-Newton correction from a rigorous C⁰ point pass, then the certifying point pass.
  - **Mean-value forms:** all F(x̄) and box images use P(point) + DP(box)·(offset). No C⁰ hulls of boxes.
  - **Each node's map** is "the first upward crossing of y = 0 after t = Tstop_i". The program fails closed unless
    y(Tstop_i) < 0 is certified. Every step enclosure gets the S4 domain checks.
  - **The A5 double-interval fallback is dropped** (trust rule 1).
- **Local unstable manifold: a self-contained lemma replaces the Zgliczyński 2009 citation.** I could not read that
  paper at source: ScienceDirect refuses automated access, and it is not on arXiv. The lemma below is elementary and
  needs a NON-AUTHOR READ before any claim.
  - *Setting:*
    - affine eigen-coordinates (u, s) centred at the float fixed point, with an exact decimal frame;
    - B = {|u| ≤ δ, |s| ≤ δ};
    - P is C¹ (analytic) near B;
    - [M] = [[a, b], [c, d]] is an interval matrix containing DP(ξ) for all ξ ∈ B, hence also every mean-value matrix
      ∫DP along segments in B (B and [M] are convex);
    - p* = (u*, s*) ∈ B is the fixed point (S2-1), |u*|, |s*| ≤ ρ′;
    - K = {|Δs| ≤ L|Δu|}.
  - *Hypotheses* (interval-checked): with μ := a_min − |b|_max L and ν := |c|_max/L + |d|_max,
    - (H1) μ > 1 and |c|_max + |d|_max L ≤ L μ;
    - (H2) ν < 1.
  - *Claim:* W^u(p*) contains the graph Γ = {(u, h(u)) : |u − u*| ≤ δ*} of a C¹ function with |h′| ≤ L and
    h(u*) = s*. Here δ* = (δ − ρ′)/(κ max(1, L)) with κ = a_max + |b|_max L. So every point and every tangent of Γ
    lies in p* + K and in K respectively.
  - *Proof:*
    1. **(H1) makes K forward-invariant and u-expanding** under every M ∈ [M].
       - For Δ = (Δu, Δs) ∈ K: |(MΔ)_u| ≥ (a − |b|L)|Δu| ≥ μ|Δu|.
       - And |(MΔ)_s| ≤ (|c| + |d|L)|Δu| ≤ Lμ|Δu| ≤ L|(MΔ)_u|.
    2. **(H2) gives backward s-expansion on K^c.**
       - Contrapositive of step 1: if MΔ ∉ K then Δ ∉ K. So M⁻¹ maps K^c into K^c.
       - For Δ ∈ K^c: |(MΔ)_s| ≤ (|c|/L + |d|)|Δs| = ν|Δs|.
    3. **Let A = the points of B with a full backward P-orbit inside B.** For x, x′ ∈ A with backward orbits (x_n),
       (x′_n) ⊂ B, the mean value theorem on the convex B gives x_n − x′_n = M̃_n (x_{n+1} − x′_{n+1}) with
       M̃_n ∈ [M].
       - If x − x′ ∈ K^c, then by step 2 every x_n − x′_n ∈ K^c, with |Δs| growing by ≥ 1/ν at each step.
       - That contradicts |Δs| ≤ 2δ (an element of K^c has Δs ≠ 0).
       - Hence x − x′ ∈ K, and A lies in an L-Lipschitz graph over u.
    4. **The classical local unstable manifold W of the hyperbolic fixed point p*** is a C¹ curve. Hyperbolicity
       follows from steps 1–2 (eigenvalues |λ_u| ≥ μ > 1 and |λ_s| ≤ ν < 1). Points of W near p* lie in A.
       - Let Γ be the connected component of W ∩ A containing p*.
       - Suppose Γ ended at e with t := |e_u − u*| < δ*.
       - P⁻¹ maps arcs of Γ from p* into Γ (A is backward-invariant).
       - P maps the arc [p*, e] onto an arc of W from p* to P(e). By the cone bound, each of its points y = P(x)
         satisfies |y_u − u*| ≤ κt and |y_s − s*| ≤ Lκt, so y ∈ B by the choice of δ*.
       - And y has the backward orbit x, … in B, so y ∈ A. Hence P([p*, e]) ⊂ Γ.
       - But it reaches u-distance ≥ μt > t, contradicting the choice of e.
       - So Γ covers |u − u*| ≤ δ* on both sides. W is C¹, so h is C¹, with |h′| ≤ L from step 3. ∎
- **How the lemma is used.** The BVP's first node is w_u(u) = c + u ũ + h(u) s̃.
  - Its enclosure: h(u) ∈ s* + L|u − u*|·[−1, 1] and h′(u) ∈ [−L, L].
  - The node's u-range must satisfy |ū − u*| + r ≤ δ* (checked).
- **Control (ii)'s α ≡ 0 step** uses Kerr's Carter function K_r as an exact first integral. S2 checks this
  symbolically before (ii) is read: the Poisson bracket {K_r, H} vanishes on the shell H = −1/2.
## A12. Batched clarifications during S2 (labelled addendum, appended at the end of S2, 2026-11-27)

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
- **A12.5 The interval-wrapping fix (v3), disclosed.** All certifying passes ran on v3.
  - v2 applied an interval DP to a vector that was already a box, in three places: the η correction, the s_u
    (or c, c′) column, and the tangent v. That loses the stable-direction cancellation (|DP s̃| ≈ 0.03 against
    |DP||s̃| ≈ 21).
  - The v2 Kerr pass therefore had Y 4.8e-13 > r 1e-13: a FAIL, archived in s2/superseded_v2_wrapping/.
  - The MN, sabotage and (ii) v2 passes had the same ≥ 27η term in Y, which already exceeded their r, so their
    failure was certain. They were stopped by verified PID before finishing (~3 core-h saved).
  - **v3:** DP acts on ũ and s̃ as thin vectors, and the [−L, L] and [−η, η] factors are applied after. v carries
    two thin chains, v = vU + [−L, L]·vS. The r estimate uses η/10 (it only chooses r; no decision depends on it).
- **A12.6 Control (iv): the L4 front end needed several float set-up repairs before a well-posed rigorous pass.**
  All decisions were made only by s2_l4, and each superseded attempt is archived as s2/superseded_l4_*.
  - **Repairs, in order:**
    1. The cone L-ladder start formula (it divided by a negative number).
    2. A noisy finite-difference Jacobian replaced by the analytic one.
    3. A float Newton convergence check added.
    4. The guess anchored to p̄ (the W^u half to 3.9e-10), with the W^s seam built in the linear regime near L4.
    5. Scaled unknowns, structured uncertainties, and adaptive segment lengths (each ‖Dφ‖ ≤ 8).
  - **The decisive change: mode bvp2.** The fixed-radius endpoint conditions left the orbit's time-phase weakly fixed:
    σ_min ≈ ρ ≈ 6e-10, with a singular vector along the flow. bvp2 instead uses:
    - Cartesian endpoints u, s ∈ R² on W^{u,s}_loc;
    - fixed segment times;
    - a phase row ⟨f(x̄_k), x_k − x̄_k⟩ = 0 at a node with fast flow;
    - X = (u, x_1…x_{n−1}, s, α), dim 4n + 1.
    That gives float cond 2.3e6 and ‖A‖∞ 2.8e3.
  - **Unchanged:** the unfolding argument (CKMJ Thm 16; α ≡ 0 since both endpoints lie in {E = 3}), Thm 30, the cone
    lemma (A12.3), and the PASS rule.
  - **Reach** is checked rigorously: |u|, |s| + √2 r ≤ δ*.
