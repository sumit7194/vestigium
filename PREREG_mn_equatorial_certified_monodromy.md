# Pre-registration — Manko–Novikov on the EQUATORIAL solution: certified-monodromy obstruction (new stage)

**Committed before any code for this stage.** The user approved it overnight; the bridge relayed that on
2026-09-28.

**Why this stage exists.** The axial MN verdict (`PREREG_mn_axis_certified_monodromy.md`, 2ce8b41, V9-corroborated)
has two main caveats: its positive control (ZV δ=2) is equatorial while the target was axial, and the axis forces
L = 0. On the equator both disappear: the known-answer control is on the **same solution type**, and **L ≠ 0** is
allowed.

**Frozen inherited machinery (not re-tuned).** `qsim/ia_hub.py` as of 2ce8b41, with G0-validated settings:
- the A2 majorant and the A4 centred sup-bound (`RationalFn`);
- N = 100, Mρ² ≤ 4, h ≤ 0.2 dist, 192 bits;
- the A5 search policy: ξ₁ first, then ξ₂; incremental nearest-first testing; first certified pair.

The candidate classes (generators and pairwise products) and the certificate rule with its proof are unchanged:
certified tr g, tr h ∉ [−2, 2] and tr[g, h] ≠ 2, which is invariant under scalars and under squaring.

**Independence (unchanged).** Ansatz's sealed MN file stays unopened. No MN integrability literature beyond what
the committed axial verdict already released. Nothing from tabula.

## The route

**Particular solution.** Γ is the plane y = 0, p_y = 0, at the levels below. It is invariant iff ∂_y g_ab|_{y=0} ≡ 0
for every component. That is checked **exactly** (gate Q1).

**Coefficient field and uniformisation.** On y = 0, the NVE coefficients lie in ℚ(x, R, E₁, E₂, E₃), with
R = √(x² − 1) and three exponentials. The feasibility look found:
- g₁ = β/R³;
- g₂ = β(2 − 2x/R + x/R³);
- g₃ = −3β²/(4R⁶).

The evaluator refuses non-integer powers, because of branch cuts. So R is **uniformised**:

    x = (t + 1/t)/2,   R = (t − 1/t)/2 = (t² − 1)/(2t),

applied as one consistent branch for every occurrence of √(x² − 1). Every g_i is then rational in t, and the
coefficient field is ℚ(t, E₁, E₂, E₃) with E_i = exp(g_i(t)).
- **Decomposition.** Every exp atom must be `E₁^{c₁} E₂^{c₂} E₃^{c₃}` with rational c_i. This is found by exact
  linear solve and checked. A failure means the stage is NOT FEASIBLE as registered.
- **t as the orbit parameter.** For any parameter s along Γ, ξ₁′ = (A/ṡ) ξ₂ and ξ₂′ = −(B/ṡ) ξ₁. So the reduced
  forms are built in t with ṫ² = ẋ²/x′(t)², where x′(t) = (t² − 1)/(2t²). This is exactly the construction used
  on the x-axis, applied to t.
- **The exact algebra is A3-style, generalised:** polynomials in (t, E₁, E₂, E₃) over ℚ, coprime by polynomial
  gcd, with the exact derivation `D = ∂_t + Σ_i g_i′(t) E_i ∂_{E_i}`.
- **Essential singularities.** They sit at t = ±1 (R = 0, i.e. x = ±1). They are declared as `bad` points: no step
  disk may reach them. Loop targets closer than 0.15 to ±1 are skipped.
- **Validity of t-plane monodromy.** The t ↦ x map is a finite, degree-2 covering. For a t-plane loop λ, the lift
  to the fibre product of Γ and the t-line closes after at most squaring, and projects to a closed loop on Γ. The
  certificate is invariant under squaring and under the scalar gauge factors (φ′^{−1/2}, (ṫ²)^{1/4}B^{−1/2}, …),
  as proved in the axial registration. So a t-plane certificate is a certificate for the NVE on Γ.

## Gates, in order; each is reported to the bridge, committed and pushed

**Q1, invariance (exact).** At p1 and p2, ∂_y g_ab at y = 0, taken into ℚ(t, E), must be identically 0 for all five
lower components. Failure means NOT FEASIBLE.

**Q2, pipeline check.** At 3 points per form, r built in ℚ(t, E) must equal r from the raw formula (x-variable,
principal-branch evaluation near the real axis x > 1, mapped to t) to a relative difference below 1e−25.

**Q3, controls on the SAME solution type and pipeline** (the t-uniformised equatorial path; any misbehaviour stops
everything):
- **ZV δ=2 equatorial** at (E, L, μ²) = (1, 0, 4) and (1, 0, 9). The known answer is G = SL(2) (published, and
  Stage 1), so a certificate **must be found** at both.
- **Kerr equatorial, the q = 0 package files** at p1 and p2, at **all** target levels. Kerr is integrable, so a
  certificate **must NOT be found**.

**Q4, target.** MN at p1 and p2 at these levels, fixed now:
- L = 0: (E, μ²) = (1, 4) and (1, 9);
- **L ≠ 0: (E, L, μ²) = (1, 1, 4).**

That is 6 target rows. Kerr runs at the same 6 levels.

**Verdict wording.** A certificate on either form at a row gives **OBSTRUCTION**: for MN at P, H_{E,L} admits no
additional first integral meromorphic in a neighbourhood of the **equatorial** Γ, so it is not meromorphically
Liouville-integrable at that level. Otherwise the result is **INCONCLUSIVE**, never "integrable". The certifying
loops are named.

**Terminal condition.** There are no amendments to the frozen integrator or search policy on this stage (A5 was
the last). If Q4 comes back INCONCLUSIVE on any ground, this stage stops and the **axial verdict stands alone**.
Pipeline construction issues found before Q2 passes may be fixed, because they precede any control or target
result, but every such fix is recorded.

## Setup correspondence

**The claim an OBSTRUCTION would be quoted for.** "MN has no Carter-like integral", now including L ≠ 0.

**The condition actually tested.** No meromorphic first integral near the equatorial Γ, at the six stated
(P, E, L, μ²) combinations.

The two match only up to these gaps:
- meromorphic only;
- the tested levels only (one L ≠ 0 level);
- the supplied metric (a verified transcription; vacuum exact but pointwise);
- AI code; computer-assisted with rigorous Arb enclosures.

**Resources.** Detached, with the fixed watchdog: 2 GB tree, memory_pressure below 10 % free, disk 5 GB, and
≤ 3 h per row. deepstrain's network-only prefetch runs alongside. Everything is committed and pushed as it goes.
If the bridge is unreachable, notes go to `inbox/bridge`.

---

## Q1 OUTCOME (2026-09-28): **PASS.**

∂_y g_ab at y = 0 is **identically 0** in ℚ(t, E₁, E₂, E₃) for all five lower components, at p1 and p2 (exact;
`qsim/mr_mneq_Q1.json`). The equatorial plane is invariant. Every exp atom (value, first and second y-derivatives
at y = 0) decomposed **exactly** into integer powers of the three registered generators.
