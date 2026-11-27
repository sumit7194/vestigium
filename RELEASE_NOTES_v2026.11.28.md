# vestigium v2026.11.28: chaotic geodesics in the Manko–Novikov spacetime (computer-assisted proofs; AI-assisted)

This release archives the repository with two mathematical results on timelike geodesics of the Manko–Novikov (MN)
spacetime, the Kerr metric deformed by an anomalous quadrupole β. Both are restricted to one energy level, described
below.

## Results

**Setting.**
- The MN metric in the form of Gair, Li & Mandel (PRD 77, 024035, 2008), with mass M = 5 and spin a = 3.
- Timelike geodesics with energy E = 0.93528150456799871854 and angular momentum L = 12.972532035607280691.
- This level contains a hyperbolic (unstable) periodic orbit near r ≈ 16 (the continuation of an inclined spherical
  Kerr orbit).
- Poincaré section: the equatorial crossing y = cos θ = 0, upward.

**(i) β = 3/100: a computer-assisted proof of chaos.**
- The stable and unstable manifolds of the r ≈ 16 periodic orbit intersect transversally along a homoclinic orbit.
- By the Smale–Birkhoff homoclinic theorem, the return map has a horseshoe, and the geodesic flow on this level has
  positive topological entropy.
- The proof uses interval arithmetic throughout (CAPD with 128-bit MPFR, Taylor order 20) and a Newton–Krawczyk
  argument for an R-symmetric boundary-value problem with 9 shooting nodes.
- **The transversality signal:** the unstable tangent at the symmetric point has v_x/|v| ≈ 3.1 × 10⁻⁵, rigorously
  excluded from 0.
- **The Kerr control** (β = 0, same code): the enclosure of the same quantity contains 0, as the integrable Kerr flow
  requires. MN's value lies ~500 times outside Kerr's enclosure.

**(ii) All small β: chaos for every 0 < |β| < β₀, both signs** (β₀ > 0 exists but is not computed).
- This is a Melnikov-type argument. Its key input is a certified (interval-arithmetic) evaluation of the first-order
  Melnikov function's Fourier coefficients for the MN quadrupole along Kerr's homoclinic loop. That evaluation shows
  the relevant zero is nondegenerate.
- An exact formula links that coefficient to the transversality signal used in (i):
  t′(0) = Υ_θ² L″(3π/2) / (2k²F_t²) ≈ −1.003 × 10⁻³. It agrees with floating-point runs at β = 10⁻² and 3 × 10⁻² to
  0.6%, and was derived a second time by a separate AI system (Gemini).

## What the results rest on
- **Interval arithmetic: the CAPD library** (commit 2f06098, MPFR 4.2.2), built under a guard that rejects any
  non-MPFR interval type.
  - Every derivative enclosure is checked finite before use.
  - A gap was found and fixed during the work: interval multiplication can silently absorb a NaN. The affected runs
    were repeated with the check in place, and gave identical results.
- **Decision arithmetic re-evaluated in a second arithmetic library.** Every inequality the proof decides was
  recomputed from exact dumps of the enclosures in python-flint/Arb (0.9.0, 256-bit), with exact rational coverage
  checks. That checker was written from the stated formulas, not from the C++ code, by the same AI session that
  wrote the C++ code. A separate AI session read it for correctness, and it rejected deliberately corrupted inputs.
- **An independent re-derivation of the field.**
  - A separate implementation of the MN Hamiltonian was written from Gair–Li–Mandel's published equations, by a
    separate AI agent instance that had not seen our code (isolated by instruction). It agrees with the field used in both proofs to the latter's 160-bit precision, at
    97 orbit points and β ∈ {0, ±3/100}. A deliberately sabotaged field was rejected.
  - In passing, both sides resolved a typesetting ambiguity in GLM eq. (3h) the same way. The resolution was checked
    against the vacuum Einstein equations.
- **Cited theorem.** (ii) uses C. Robinson, "Melnikov method for autonomous Hamiltonians", Contemp. Math. 198 (1996)
  45–53, Theorem 3.4 with Remark 3.10. Its hypotheses were checked against our setting at source. The proof of its
  supporting Lemma 3.8, in Robinson, ETDS 8 (1988) 395–409, was not re-read by us.
- **Two analysis lemmas written for this work**, on cone conditions for local stable and unstable manifolds. Each was
  read for correctness by a separate AI session that did not write it (not human peer review).
- **Predictions fixed before the computation:** the decision rules, controls and expected outcomes were written down,
  and committed, before each run.
- **Controls:**
  - Kerr (β = 0) must not certify transversality, and it does not.
  - Kerr's homoclinics are certified to form a continuous family.
  - A field with one β² term removed gives a measurably different certificate.
  - The validator reproduces Capiński–Kepley–Mireles James's published homoclinic proof in the restricted three-body
    problem.

## What is NOT claimed
- No value or lower bound for the topological entropy.
- No other energy levels, spins or orbit families.
- No explicit β₀ in (ii). In particular, (ii) does not reach β = 3/100; (i) covers that value separately.
- Nothing about Kerr itself beyond the controls.

## What still rests on a single implementation
- The flow and derivative enclosures computed by CAPD. A second validated integrator has not been run.
- The interval evaluation of the Melnikov coefficients (python-flint/Arb).

## Novelty, to our knowledge
- Earlier MN chaos results that we found are numerical: Poincaré sections, rotation numbers and ergodicity, in Gair,
  Li & Mandel 2008 and in Apostolatos, Lukes-Gerakopoulos and Contopoulos, 2009–2014.
- Rigorous perturbative chaos results exist for other perturbed black-hole geodesic problems: Moeckel, CMP 150 (1992)
  415–430, doi:10.1007/BF02096667; Bombelli & Calzetta, CQG 9 (1992) 2573–2599, doi:10.1088/0264-9381/9/12/004;
  Letelier & Vieira, CQG 14 (1997), doi:10.1088/0264-9381/14/5/026; Polcar & Semerák, PRD 100, 103013 (2019),
  doi:10.1103/PhysRevD.100.103013. These are Melnikov-type arguments.
- We found no computer-assisted proof of chaos for any relativistic geodesic flow, and no rigorous chaos proof for MN.
- The searches and sources are listed in qsim/mn_homoclinic_spike/NOVELTY_CHECK.md. This is "to our knowledge", not a
  literature survey.

## Where to look
- qsim/mn_homoclinic_spike/S2_RESULT.md: result (i), the controls and the margins.
- qsim/mn_homoclinic_spike/STEP_A_MELNIKOV_GLUE.md: result (ii), with every hypothesis and step.
- qsim/mn_homoclinic_spike/tier2a/TIER2A_RESULT.md: the independent field re-derivation.
- qsim/mn_homoclinic_spike/FIELD_CHECKLIST_MN_CHAOS.md: what a referee would check first, and its status.
- qsim/mn_melnikov/RESULT.md: the certified Melnikov coefficients.
- STATUS.md: the current state.

## AI assistance
This work was carried out with substantial assistance from AI systems: Claude (Anthropic) and Gemini (Google). They
were used for writing and running code, deriving and checking mathematics, literature searches, and drafting text,
under the direction of the repository owner. The proofs' reliance on AI-written code is the reason for the
independent re-checks listed above.
- **All checks described here as independent were done by separate AI sessions or systems; none is human peer
  review. No external expert has yet read the proofs.**
- The project history is unchanged.
