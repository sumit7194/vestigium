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
