# An explicit β* after Step A: routes 1 and 2 re-scoped (DRAFT ONLY; nothing runs; Sumit's budget)

Written 2026-11-27 22:20 IST by Claude Opus 5.5 (office "Quantum"), at the Bridge's request. Sumit: "a new tool install
shouldn't be a reason to not do something". So new installs and new integrators are treated as allowed. Local,
uncommitted.

**Correction, stated up front:** my earlier route-1 estimate of "20–300 core-h" (in messages only, never in a committed
file) is WITHDRAWN. Box wrapping on the long return (below) makes the cost unknown, ~10¹–10⁵ core-h, until the pilot.

## The value
- Step A (if read CORRECT) gives chaos for 0 < |β| < β₀, with β₀ unknown.
- An explicit β* ≥ 3/100 would join S2's point, giving **chaos for every 0 < |β| ≤ 0.03 (both signs)**: one clean
  interval statement.
  - Physics readers (EMRI bumpy-Kerr tests) want explicit ranges.
  - Experts value it as "explicit, non-perturbative to the certified point".
  - It is moderately high value; it is not a new mechanism.

## The blocker both routes share (I missed it in my earlier estimate; correcting it here)
- **The measurement.** S2-0 found that derivative widths are linear in the set size, with relative DP width about
  1.15e7 × (set size) on the long τ ≈ 381 return (and 7.4e5 × on Kerr).
- **Why it matters.** Any certificate that is uniform over a β-interval of width w encloses the nodes over a set of
  size about |dz/dβ|·w ≈ 1.5w. So the chain's relative widths become ≈ 1.7e7·w.
- **The requirements:**
  - Route 1 needs the slope derivative t′ ≈ 1e−3 enclosed away from 0, so w ≲ 6e−11.
  - Route 2 needs t on each circle ball to about ½|a₁|R, so a ball radius of ≲ 3e−13 at R = 1e−2.
- **Done naively, both are infeasible:** about 5e8 β-intervals, or about 2e11 balls.
- **The genuine dependence on β is mild.** t/β varies only 3% over [0.01, 0.03], λ_u by 0.4%, and v_px by 3.6% over
  [0, 0.03]. The widths come from box wrapping inside the long, strongly stretching return.
- **The remedies, which BOTH routes need:**
  - **(R-a)** Split every return, and above all the long excursion, into many time segments, as control (iv)'s bvp2
    did (n = 124). Each segment's stretching, and so its width per unit set, drops by orders of magnitude.
  - **(R-b)** Carry the β-dependence as a polynomial along the branch rather than as a box: Taylor models in β, or
    high-order CAPD jets in β. This avoids wrapping in the β-direction.
- **How much (R-a) + (R-b) recover is UNMEASURED.** My earlier "20–300 core-h" for route 1 is withdrawn. The honest
  range before a pilot is ~10¹–10⁵ core-h.

## Route 1: the mean value theorem on t′(β), real arithmetic
- **What is proved and what is certified.**
  - t(0) = 0 exactly (Step A §3 step 2). On a partition of [−β*, β*], certify 0 ∉ [t′] on each piece, with one
    common sign. Then t(β) = β t′(ξ) ≠ 0.
  - It needs C² in (state, β): v′ needs D²P and ∂_β DP.
  - It needs a parametric Krawczyk, uniform over each β-piece (the same pattern as control (ii)'s x̂-uniform one).
- **The engine, as Sumit's rule allows.**
  - **(1a) CAPD:** C^r Poincaré maps (CnPoincareMap), with β as a state variable (β′ = 0). Native and guard-buildable
    (MPFR, trust rule 1).
  - **(1b) Julia TaylorModels.jl / TaylorIntegration.jl** (install allowed). Taylor models in (state, β) are remedy
    (R-b) in native form.
    - It is a SECOND integrator, so it shares the build with Tier 2b. One development effort would serve both the
      independent re-check and the β-family.
- **The trust surface.**
  - **New maths:** a parameter-dependent local-manifold lemma (bounds on ∂_β of the W^u_loc slope), or a validated
    parametrisation method in (u, β). The cone lemma gives no β-derivative. It needs a non-author read.
  - **New code:** the C² chain and the parametric Krawczyk. This needs a Tier-1-style Arb re-check of the decision
    arithmetic, as for S2.
  - **The field:** shared with S2. Tier 2a covers it.
  - **If (1b):** TaylorModels' own validation is another trust base; the Bridge's S6 used it on Hénon–Heiles.
- **Development:** 1–2 weeks with (1a); 2–3 weeks with (1b), of which about half overlaps Tier 2b.
- **The pilot, which decides everything:**
  - Kerr end, β ∈ [0, w] for w ∈ {1e−8, 1e−6, 1e−4}, with the excursion split into about 20 segments.
  - Measure the width of [t′] against w. About 3–10 core-h.
  - It gives the partition size, and hence the projection.

## Route 2: a complex-β disc with Rouché (or the Cauchy form)
- **What is proved and what is certified.**
  - t is holomorphic on D(0, R), with t(0) = 0 and t′(0) = a₁ (Step A gives a₁ ≈ −1.003e−3 to first order).
  - Certify |t(β) − a₁β| < |a₁| R on |β| = R. Then β = 0 is the only zero in the disc. a₁ needs only an enclosure;
    use the Cauchy form |t − a₁β| ≤ M|β|²/(R(R − |β|)) when a₁ is not exact.
  - It needs only C¹ data per ball (no C²).
- **The upside.** One disc could reach far.
  - The quadratic term is small: t/β changes only 3% between β = 0.01 and 0.03, i.e. |t − a₁β| ≈ 0.04|a₁β| at
    β = 0.03.
  - So Rouché holds out to R ~ O(0.1–0.5), if t stays holomorphic there. That would beat route 1's [−0.03, 0.03] in
    reach.
- **The engine.**
  - **The complexified field:** a new codegen of the MN functions in complex arithmetic (exp, sqrt, Legendre
    polynomials), with branch tracking for R = √(x² + y² − 1).
  - **Complex time: CAPD CAN do it.** Integrate dx/ds = e^{iφ} f(x) as a real 8-D ODE in s, to reach a complex
    crossing time. (This corrects my earlier "CAPD cannot".) An acb Taylor integrator is the alternative.
  - **Holomorphy:** certify in Arb that every metric denominator is nonzero and that the sqrt stays off its cut on the
    complex tube.
- **The trust surface (larger than route 1).**
  - **New code:** the complex codegen. It needs a second-implementation check against the real field on the real
    axis, plus a Cauchy–Riemann must-fail.
  - **New maths:** a holomorphic local-manifold (graph) lemma, or a validated parametrisation method. It needs a
    non-author read.
  - **New code:** the complex section crossing (Krawczyk in complex t).
  - The holomorphy certificate.
  - A Tier-1 re-check of the Rouché arithmetic.
- **Development:** 2–4 weeks.
- **Compute:** limited by the same blocker, with each circle ball needing remedies (R-a)/(R-b). UNMEASURED,
  ~10²–10⁵ core-h. The cost scales with the circle length 2πR, but the reward also grows with R.

## The pick, for an explicit β* after Step A
1. **Route 1 pilot first** (3–10 core-h, about 1 week of preparation), real arithmetic, at the Kerr end. Four reasons:
   - It measures the shared blocker cheaply, with the smallest new trust surface.
   - It needs one new lemma, versus three new components for route 2.
   - Its result also prices route 2, since they share the blocker.
   - With engine (1b) it doubles as the Tier 2b build.
2. **Then:**
   - If the pilot shows the wrapping is tamed, finish route 1 for [−0.03, 0.03] and join S2.
   - **Only if a wider range (|β| up to 0.1+) is wanted,** build route 2 on the same remedies.
3. **Not before Step A's read**, and not before Sumit sets a budget.

## Folded in: Neon's card-2 follow-up (2026-11-27; the Bridge checked the citations at source; the maths is UNVERIFIED)
- **The missing piece for route 1.** Neon gives a parameter-dependent C² graph-transform lemma.
  - Fixed (u, s) axes at the Kerr eigenvectors.
  - Four interval-checkable inequalities:
    1. the C¹ cone/expansion condition;
    2. h_β contraction by 1 − κ;
    3. h_uu with factor κ/μ²;
    4. h_uβ with factor κ/μ (≈ λ_u⁻²).
  - It encloses ∂_β of the local-manifold slope, which is exactly what the cone lemma (A11) cannot give.
  - Refs (DOIs checked by the Bridge; NOT read by me):
    - Capiński–Zgliczyński, arXiv:1603.07131;
    - Zgliczyński, JDE 246 (2009) 1774–1819, DOI 10.1016/j.jde.2008.12.019. This is the paper A11 replaced with a
      self-contained lemma because I could not read it; it exists;
    - Cabré–Fontich–de la Llave II, IUMJ 52 (2003);
    - Castelli–Lessard–Mireles James, SIADS 14 (2015) and JDDE 30 (2018).
  - **It needs a non-author read before any use.** It would be written up as our own lemma with proof, as A11 was.
- **Route 2 without complex time.**
  - Rescale t = Tτ, with τ ∈ [0, 1] real and T ∈ ℂ, on the last segment and for the period only.
  - The parametrisation method (natively holomorphic) replaces the cone lemma. Ref: arXiv:2509.03655 (Kumar).
  - This is simpler than my rotated-time idea.
  - **Correction to my route-2 count (Neon's catch):** Schwarz or Rouché need t holomorphic on the CLOSED disc.
    That means certifying the half-BVP solution (existence, uniqueness, analyticity) over a 2-D cover of the disc, not
    just on the circle. So ~300–400 complex balls (Neon's estimate), not ~60, unless a Taylor-in-β (Wiener-algebra)
    method is used. That is route 3 in ℂ, and it is my remedy (R-b).
- **Neon's costs.**
  - Route 1 + lemma: β\* ~1e−4 to 1e−3, 15–80 core-h, 3–5 days.
  - Route 3 (Chebyshev or Taylor model in β): β\* 0.03–0.1, 20–100 core-h, 2–3 weeks.
  - **Both ignore the chain-wrapping blocker above** (~1.7e7 × the β-width on the long return). Neon was not told
    about it.
  - Its β\* ~1e−4 to 1e−3 for route 1 is worth noting: an explicit β\* that small would NOT join S2's 3/100.
- **The pick is unchanged:** the route-1 pilot first (3–10 core-h), which measures the blocker. Neon's lemma B
  becomes the planned local-manifold piece, after a non-author read. Route 3/(R-b) is the natural engine if the pilot
  shows that box wrapping dominates.

## Standing condition (the Bridge, 2026-11-28)
- **Before any route-1 PRODUCTION result is called proved, CFdlL Part II** (IUMJ 52 (2003) 329–360; the joint
  (u, β) regularity of the local manifold, used in ROUTE1_LEMMA_DRAFT (0)) **must be read at source.**
- For the pilot, which is a measurement, the present handling is enough: Part I read at source (Thm 1.1 for each β);
  Part II cited, not read; the uniform-contraction sketch.
- The Bridge will fetch Part II once the Chrome extension is reconnected.
