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

## Q2, first attempt: killed by the 2 GB guard at 901 s. Pipeline fix before Q2 passes (allowed by the registration; recorded)

**Profile** (`qsim/mr_mneq_build_profile.log`, MN p1, (1, 0, 4)):
- The y = 0 data takes 20 s and is small.
- **The ξ₁ form r₁ in ℚ(t, E) takes 35 s: 1389/1361 terms.**
- The ξ₂ intermediate p₂ is already 1426/1450 terms. r₂ is far heavier, and it and the raw symbolic reference used
  by Q2 are what exceeded memory.

**Fix (construction only; integrator, search policy and certificate rule untouched):**
1. **ξ₂ is built lazily**, only if ξ₁ yields no certificate at that row. It is then checked **inline** by the Q2
   criterion before any search on it. If building it exceeds the row's resources, ξ₂ is INCONCLUSIVE for that row.
2. **Q2 reference replaced.** Raw symbolic differentiation is replaced by **independent numerical differentiation**
   in mpmath at 60 digits:
   - the lower components are evaluated directly, numerically, from the package's srepr, not through the chain-rule
     or ℚ(t, E) code;
   - B uses `mp.diff` in y;
   - p₁ and p₁′ use `mp.diff` in x;
   - the result is mapped to t by `x′² r_x − S/2`.
   Criterion: relative difference < 1e−25, unchanged. Checked on ξ₁ at MN p1 and p2 at (1, 0, 4) and (1, 1, 4),
   Kerr p1, and ZV.

## Q2 OUTCOME (2026-09-28, under the pipeline fix): **PASS.**

The ξ₁ form built in ℚ(t, E) agrees with the **independent** numerical-differentiation reference (mpmath at
60 digits, direct component evaluation) with relative differences of **1.9e−52 and 2.0e−52** (MN p1), **1.1e−50**
(MN p2), **≤ 1.1e−56** (Kerr p1) and **≤ 4.8e−57** (ZV). That covers both (1, 0, 4) and the L ≠ 0 level (1, 1, 4);
the criterion was < 1e−25 (`qsim/mr_mneq_Q2.json`).

Before this: one crash in my check code (arb midpoint string conversion), fixed at 261c666, before any
comparison ran.

## Q3 OUTCOME (overnight, 2026-09-28): **PASS, 8/8.** (`qsim/mr_mneq_Q3.txt`, pushed at 2b2ce0f)

- **ZV δ=2 equatorial** at (1, 0, 4) and (1, 0, 9): certificate **found** (ξ₁, 7–8 s each).
- **Kerr equatorial**, p1 and p2 at (1, 0, 4), (1, 0, 9) and (1, 1, 4): **none**, 6/6 rows, both forms.

On the same solution type and the same pipeline, the known-answer tests behave correctly in both directions,
including the L ≠ 0 level.

## Q4, partial (as of 2026-09-28 10:36): rows 8–10 **INCONCLUSIVE, time limit**; rows 11–13 are running

MN p1 at (1, 0, 4), (1, 0, 9) and (1, 1, 4): the 3-h guard fired **during the ξ₁ certificate search**. ξ₁ was built
in 36 s (1389/1361 terms) and 8 singular points were located, but the search did not finish.

The row JSON still shows "building" for ξ₁. That is only because partial results are saved before the search, not
during it. The row log shows the true stage (`qsim/mr_mneq_row_8..10.log`).

The cost is the per-step series evaluation of a large 4-generator expression, plus small steps near the
essential singularities at t = ±1. By the registration there are **no amendments**. Rows 11–13 (p2) run to
completion or to their limit, and the final Q4 outcome is recorded when they finish.

## Q4 status (recorded 2026-10-03): row 11 **interrupted**; rows 12–13 **not run**

The overnight chain was stopped when the Claude session ended on 2026-09-28. Row 11 (MN p2, (1, 0, 4)) was
**cut off about 2 min into its ξ₁ certificate search** (4 located singular points); its own 3-h guard did not fire.
Rows 12–13 (p2 at (1, 0, 9) and (1, 1, 4)) never started. This is not a result.

**State of Q4:**
- p1, 3/3 rows: INCONCLUSIVE (time limit).
- p2: no completed row.

Resuming rows 11–13 is a re-run of registered rows with unchanged code and settings. It is **not** an amendment.

**Re-run of rows 11–13 (2026-10-03, user's decision).** The code and settings are unchanged, apart from a
row-filter option on the runner (`Q4 11,12,13`), so that p1 rows 8–10 are not repeated. The run is launched with
`nohup`, so it survives a session end. Output goes to `qsim/mr_mneq_Q4_p2.txt`.

## Q4 p2 re-run outcome (2026-10-03): stopped by a **false-positive box swap guard**

`qsim/mr_mneq_Q4_p2.txt`:
- **Row 11** (p2, (1, 0, 4)): killed at **10,720 s of its 10,800 s** budget, in the ξ₁ search, with no
  certificate. It ran 99.3 % of its budget, so in effect INCONCLUSIVE (time), like the p1 rows.
- **Rows 12 and 13:** killed after 1.1 s and 45.9 s. **They never ran**; not results.

**Cause.** macOS grows swap on demand (total 0 → 2 GB during the run). Just before a new swap file is added, free
swap dips below 512 MB even with 77–87 % of memory free. The watchdog's swap rule fired on that.

**Fix (resource policy, not science):** the swap rule now also requires system memory free below 20 %.
`memory_pressure` below 10 % free remains the main trigger.

**Rows 12 and 13 are re-run** under the fixed watchdog, with unchanged code and the user's approval for the p2
rows. Row 11 is not re-run, because it already used 99.3 % of its budget.

## FINAL OUTCOME of the v1 equatorial stage (2026-10-04)

**INCONCLUSIVE at every target row. No certificate. This says nothing about integrability.**
- Q1 (exact invariance), Q2 (pipeline check) and Q3 (controls, 8/8) PASSED.
- Q4 target rows:

| rows | outcome |
|---|---|
| p1, rows 8–10 | 3-h limit |
| p2, row 11 | 10,720 s of 10,800 s, then killed by the false-positive swap guard (fixed in 955b4c0) |
| p2, row 12 | 3-h limit |
| p2, row 13 | 3-h limit |

The cause is cost: per-step series evaluation of the 1389/1361-term reduced form, with tiny steps near t = ±1.

This stage is **superseded by an independent route,** `PREREG_mn_equatorial_v2.md` (iahub v2). The v2 route has
already given an OBSTRUCTION at p1, (1, 0, 4), replayed by v1 and reproduced by the bridge; further rows are in
progress. This stage's own result stands as recorded.
