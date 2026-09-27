# Pre-registration — Manko–Novikov on the symmetry axis: a certified-monodromy (Ziglin-form) obstruction test

**Committed before any route code and before any MN computation beyond the feasibility look.** The feasibility
opinion was sent to the bridge on 2026-09-27. The bridge relayed the user's approval, and the user approved the
python-flint download in my own chat.

This is the fleet's interval-arithmetic hub. The reusable part goes in `qsim/ia_hub.py`; the MN-specific part
goes in `qsim/mr_mn_axis.py`.

**Environment.**
- python-flint **0.9.0** from PyPI, wheel `python_flint-0.9.0-cp313-cp313-macosx_11_0_arm64.whl`,
  sha256 `70e965a6f8096b3f40cd335d16227715a61c59e27a1cf9979e57717cfae4e6da`.
- Installed with `uv pip` into `sims/.venv` only (Python 3.13.12, arm64).
- Everything else is the Stage-1/2 environment.

**Independence (unchanged).**
- Ansatz's `data/sealed/MN_PREDICTION_SEALED.md` stays unopened.
- No MN integrability or chaos literature until this verdict is committed.
- Nothing from tabula.
- Already seen: the package manifest, and the feasibility look. That look found the exponential arguments on
  y = 1 and y = 0; then the watchdog's (since-fixed) swap bug killed it.

## Why Kovacic is not used, and what replaces it

The MN metric is transcendental in (x, y). On the axis y = 1 every exponential is a power of `E = exp(2β/x³)`,
and `R = √(x² + y² − 1) = x`. So the axial NVE has coefficients in `ℚ(x, E)`, not `ℚ(x)`, and Kovacic's algorithm
does not apply.

**The theorem used (Ziglin; Morales–Ramis over the field M(Γ) of meromorphic functions on the phase curve).** If
H is integrable with first integrals meromorphic in a neighbourhood of Γ, then G⁰ is abelian, where G is the
differential Galois group of the NVE over M(Γ). The monodromy group of the NVE along closed loops **in Γ** is
contained in G. No rationality of coefficients is needed, and an essential singularity (here x = 0) is simply a
puncture of Γ.

**Certificate rule and its proof (fixed now).** Suppose two monodromy elements g, h ∈ SL(2, ℂ) satisfy three
conditions, each **certified** by ball arithmetic:
- (i) tr g ∉ [−2, 2];
- (ii) tr h ∉ [−2, 2];
- (iii) tr(g h g⁻¹ h⁻¹) ≠ 2.

Then G⁰ is non-abelian.

*Proof.* Condition (i) or (ii) means the element is loxodromic: it has distinct eigenvalues μ, μ⁻¹ with |μ| ≠ 1.
So it has infinite order, and it is diagonalisable with exactly two eigenlines. In SL(2), tr[g, h] = 2 iff g and
h have a common eigenvector, so (iii) says they have none. Now take the three possibilities for an abelian
identity component, G⁰ ∈ {1, 𝔾_m, 𝔾_a} up to conjugacy:
- **G⁰ = 1:** G is finite, contradicting the infinite order of g.
- **G⁰ = 𝔾_a:** G normalises 𝔾_a, so G ⊂ Borel. Then g and h share an eigenvector, contradicting (iii).
- **G⁰ = 𝔾_m:** G ⊂ N(T). Elements of N(T) \ T have trace 0 ∈ [−2, 2], so g, h ∈ T. They commute, so
  tr[g, h] = 2, contradicting (iii). ∎

**Invariances used.**
- Every condition is invariant under g ↦ λg for scalars λ: the eigenvalue ratio and the commutator are
  unchanged. So scalar gauge factors between the reduced x-equation and the NVE on Γ (for example
  (ẋ²)^{1/4} B^{−1/2}) do not matter.
- Loops in the x-plane lift to closed loops on Γ (a double cover branched at the odd zeros of ẋ²) at least after
  squaring. And (g, h) satisfies (i)–(iii) iff (g², h²) does: a loxodromic g² has the same eigenlines as g, and its
  eigenvalues μ² still have modulus ≠ 1. So the certificate transfers to Γ **without** invoking the
  covering lemma.

## Certified integrator (`ia_hub.py`)

- The reduced equation `y'' = r(z) y` is transported along polylines by Taylor steps.
- **One step** from z_a with step h uses a disk radius ρ = 2h:
  - The Taylor coefficients of r at z_a come from exact truncated power-series ball arithmetic (Arb `acb_series`),
    up to order N.
  - **M** is a rigorous bound on |r| over the box enclosing the disk, from a single ball evaluation of r.
  - If that ball is unbounded or contains a pole, the step is halved. No step is ever taken on a disk that isn't
    certified.
- **Tail bound, majorant method.** With |r_k| ≤ M ρ^{−k} (Cauchy), the majorant coefficients satisfy
  `n(n−1) A_n = Σ_{k=0}^{n−2} M ρ^{−k} A_{n−2−k}`, and `|a_n| ≤ A_n` by induction. Set `B_n = A_n ρⁿ` and
  `S_n = Σ_{j≤n} B_j`; then `S_n ≤ S_{n−1}(1 + Mρ²/(n(n−1)))`. For all n > N this gives
  `B_n ≤ S* := S_N exp(Mρ²/N)`. At |t| ≤ h = ρ/2 the truncation error in y is ≤ `S* 2^{−N}`, and in y′ it is
  ≤ `S* ρ^{−1} Σ_{n>N} n 2^{−(n−1)}` (closed form). Both are added as ball radii.
- The fundamental matrix (two basis solutions) is propagated in ball arithmetic at 192 bits (raised if balls
  grow). det = 1 is reported as a consistency check, **not** used as a proof.
- **Loops:** a base point z₀; for a target singular point c, the segment from z₀ to c + ρ_c·(z₀ − c)/|z₀ − c|, an
  inscribed 16-gon of radius ρ_c around c, and back. Approximate singular locations come from floating-point root
  finding. They only choose loops: every loop is closed and certified to avoid singularities, so **every** loop
  gives a genuine monodromy element, whatever it encloses.
- **Candidate elements:** the generators γ_i for the located singular points with |c| ≥ ρ₀ (away from the
  essential singularity at 0), and the pairwise products γ_iγ_j. The certificate search tests pairs from this
  finite list in a fixed order and stops at the first pair satisfying (i)–(iii).

## Setup correspondence

**The claim an OBSTRUCTION would be quoted for.** "MN (the q-anomaly subclass) has no Carter-like fourth integral."

**The condition actually tested.** At (M, a, β) = p1 or p2 and L = 0 with the stated (E, μ²), there is no first
integral of H_{E,0} that is meromorphic in a neighbourhood of the **axial** phase curve. The test runs on the
supplied closed-form metric.

The two match only up to these gaps, which every report carries:
- **Meromorphic only.**
- **The L = 0 sector only.** The axis forces L = 0. A Carter-like integral would restrict to this sector; an
  integral that exists only for L ≠ 0 levels is not excluded.
- **The tested points only.**
- **The supplied metric,** whose vacuum was checked pointwise and exactly in a formal field. It is a
  transcription of the published MN form, verified but not derived.

## Gates, in order; each gate is reported to the bridge

**G0: validation of the integrator on equations with known monodromy.** Failure stops everything.
- (a) Reduced Riemann P with exponent differences (1/3, 1/5, 1/7) at 0, 1, ∞. The certified enclosure of
  tr(local monodromy around 0) must contain −2cos(π/3), and around 1 it must contain −2cos(π/5).
- (b) An exponential-path test that exercises `E` and the essential singularity. Pull the same P-equation back by
  `w = exp(2/x³)` into a reduced equation in x with coefficients in ℚ(x, E). A small loop around a root x₁ of
  E(x) = 1, with x₁³ = 2/(2πi), maps to a single loop around w = 1. Its trace must contain −2cos(π/5).
- (c) The enclosures must be tight enough to decide (i)–(iii) on (a): at least 10 correct digits.

**G1: the ω gate (exact, symbolic).**
- ω = −g_tφ/g_tt at y = +1 must vanish identically, at both MN points. This is decided exactly with E as a
  symbol. If it fails, there is no regular L = 0 axial solution on that half-axis, and it is **NOT FEASIBLE**.
- y = −1 is also checked and reported. Γ lies on y = +1 and never meets y = −1.
- Evenness in θ is automatic: every function of y = cos θ is even.

**G2: controls on this same route.** A misbehaving control stops everything and is reported.
- **ZV δ=2, equatorial, (E, L, μ²) = (1, 0, 4):** G = SL(2) is known (published, and our Stage 1). A certificate
  **must be found**.
- **Kerr (MN at β = 0, p1 and p2), axial, the same levels as the target:** Kerr is integrable, so a certificate
  **must NOT be found**. Finding one means a bug.
- **Info, not gating:** ZV δ=2 axial; Kerr equatorial.

**G3: target.** MN at p1 and p2, axial, L = 0, (E, μ²) = (1, 4) and (1, 9).

**Axial NVE.**
- Coordinates (x, θ) with y = cos θ; Γ is θ = 0, p_θ = 0.
- `A = g^θθ|₀`, where `g_θθ = g_yy sin²θ`.
- `B = ∂²H/∂θ²|₀ = −∂_y H|_{y=1}`, with p_θ = 0 and p_x² eliminated through the constraint.
- `g^tt = f ω²/ρ² − 1/f`, which needs G1.
- Reduced ξ₂- and ξ₁-forms as in `mr_nve`. They are derived symbolically, with E a symbol, then evaluated.
- B ≡ 0 (degenerate) gives INCONCLUSIVE for that form.

**Verdict wording.** A certificate on **either** form at P gives **OBSTRUCTION**: for MN at P, the reduced flow
H_{E, L=0} admits no additional first integral meromorphic in a neighbourhood of the axial phase curve Γ, so it is
not meromorphically Liouville-integrable at that level. The caveats:
- computer-assisted: rigorous ball arithmetic, but AI-written code;
- meromorphic integrals only;
- the tested levels only;
- the supplied metric (pointwise-exact vacuum only);
- nothing about how much chaos there is.

**No certificate gives INCONCLUSIVE, never "integrable".**

**Resources.** Every run goes through `mr_watchdog.run_guarded` (fixed in bed3891), ≤ 2 GB and ≤ 30 min per job,
and runs detached if it is long. Logs go in `qsim/`. Everything is committed and pushed.

## Named ways this fails

1. G0(b) fails: the E-series or the essential-singularity handling is wrong. Stop.
2. Enclosures blow up before closing a loop. The result is INCONCLUSIVE (loss of precision), not a verdict.
3. G1 fails (ω ≠ 0 on the axis): the axial route is not available.
4. The axial NVE is degenerate at L = 0 (B ≡ 0): INCONCLUSIVE.
5. The axial G⁰ is genuinely abelian for MN (possible, since the axis is a special orbit): no certificate, so
   INCONCLUSIVE. This would **not** be evidence of integrability.

---

## G0 OUTCOME (2026-09-27): **PASS on the third attempt.** The two failed attempts are on record.

- **Attempt 1: FAIL.** The balls exploded to about 1e600. Step policy: disks that nearly touched a pole gave
  finite but huge M (about 1e5), so the rigorous tail exp(Mρ²/N) blew up. Nothing false was produced: the gate
  refused them on digits (NaN).
  - **Fix (step policy only; every accepted step stays rigorous):** reject disks with Mρ² > 4 (`MRHO2_MAX`), and
    take h ≤ 0.2 × dist, down from 0.4.
- **Attempt 2: FAIL on the registered 10-digit rule.** The enclosures contained the exact values, but test (b)
  had 9.7 digits. **Fix:** Taylor order N = 60 → 100 (the tail is about 2⁻ᴺ per step).
- **Attempt 3: PASS.** Loop around 0: `[−1.000… ± 1.1e−23]` ∋ −2cos(π/3). Loop around 1:
  `[−1.6180339887498948482046 ± 2.9e−23]` ∋ −2cos(π/5). **(b), the pullback by exp(2/x³):**
  `[−1.618033988749894848205 ± 6.6e−22]` ∋ −2cos(π/5). About 22 digits each, det = 1 inside the balls.
  `qsim/mr_mn_G0.json` and `mr_mn_G0.log`.

These settings are frozen for G1–G3: `MRHO2_MAX = 4`, h ≤ 0.2 dist, N = 100, 192 bits.

## G1 OUTCOME (2026-09-27): **PASS.**

ω = −g_tφ/g_tt reduces **exactly to 0** at y = +1 and at y = −1, at both p1 and p2 (`qsim/mr_mn_G1.json`). The
regular L = 0 axial particular solution exists.

## G2 OUTCOME (2026-09-27): **PASS.**

`qsim/mr_mn_G2.txt`, `mr_mn_G2_run.json`, `mr_mn_row_0..5.{log,json}`.

- **ZV δ=2 equatorial (1, 0, 4), which must find a certificate:** **found on both forms** (332 s).
- **Kerr p1 and p2 axial at (1, 4) and (1, 9), which must not find one:** **not found**, 4/4 rows, both forms.
- **Info:** ZV δ=2 **axial** has **no certificate** (2 located singular points).

**Scope note (bridge, recorded).** The positive control is **equatorial**; the MN target is **axial**. G2 shows the
certificate machinery can fire. It does not show power on axial solutions specifically, and the ZV axial info row
found nothing there. G0(b) covers the loop mechanics near an essential singularity. So an axial INCONCLUSIVE would
be uninformative, and an axial OBSTRUCTION stands on its own certificate. The verdict's scope says so.

## G3, first attempt (2026-09-27): **all 4 rows INCONCLUSIVE, resource limit.** No verdict.

MN p1 and p2 at (1, 4) and (1, 9): the memory guard (2 GB) fired at 55–81 s, **before the NVE was built**, in the
symbolic derivation or simplification of the 92 kB components. The certified integration never started.
(`qsim/mr_mn_G3.txt`, `mr_mn_row_6..9.*`.) An earlier launch failed on a path error before any computation; the
relaunch is this attempt. Next: a guarded profiling diagnostic, then an amendment, labelled post-failure.

## AMENDMENT A1 (2026-09-27), POST-FAILURE: no global symbolic simplification. Filed before the code change.

**Diagnosis** (`qsim/mr_mn_profile.log`, guarded). The y-derivatives and y = 1 substitutions are cheap: the
largest expression is about 6.3·10³ operations, under 0.5 s. The 2 GB blow-up is the **global simplification**
step: `simplify(B)` for the degeneracy test and `cancel` over ℚ(x, E). Neither is needed for rigour.

**Change.**
1. **Degeneracy.** B ≢ 0 is proved by **one certified ball evaluation** at a fixed point (x = 2.3 + 0.7i), with
   B certainly ≠ 0. A nonzero value is a proof. If the ball contains 0, a second point is tried; failing both gives
   INCONCLUSIVE for the ξ₂ form.
2. **The reduced forms** are built by `sp.diff` only, with no simplify, cancel or factor. They are compiled with
   `cse` and evaluated directly in ball arithmetic, exp() included. The evaluator still refuses non-integer
   powers.
3. **The exp check** is kept, on the exp **atoms only**: every exp must be `E^m`, with m rational.
4. **Pole location (float, loop choice only)** uses `1/r` directly, without `together`.

The integrator (G0-validated) is unchanged. **Re-validation:** G2 is re-run in full through the amended path.
The Kerr axial rows must not find a certificate, and ZV equatorial must find one. Only then is G3 re-run
(attempt 2). The committed attempt-1 outcome stands.

## AMENDMENT A2 (2026-09-27), POST-FAILURE: a sharper majorant constant. Filed before the code change.

**Observation (A1 G2 re-run).** ZV equatorial passes again (certificate on both forms). But the first **raw**
Kerr axial row runs for more than 20 min: with unsimplified expressions, the single box evaluation of |r| over
the step disk is heavily overestimated (the dependency problem), so the Mρ² ≤ 4 guard forces tiny steps. If that
row hits its time limit, it is recorded as FAIL (did not run), and G2 stops by rule.

**Change (integrator; rigour unchanged, bound sharper).** In the majorant, replace the Cauchy bound M ρ^{−k} for
**all** k with:
- the **exact** |r_k| (the ball upper bounds of the Taylor coefficients already computed) for k ≤ N;
- the Cauchy bound `M′ ρ′^{−k}` for k > N, with **ρ′ = 1.5ρ**. Here M′ = sup |r| on the box enclosing the disk
  of radius ρ′, which must be certified finite.

With `m_k = |r_k| ρ^k`, the recursion `n(n−1) B_n = ρ² Σ_k m_k B_{n−2−k}` gives, as before,
`S_n ≤ S_{n−1}(1 + M̄ρ²/(n(n−1)))`, where `M̄ = max(max_{k≤N} m_k, M′ (2/3)^{N+1})`. At N = 100 the factor
(2/3)^{101} ≈ 10⁻¹⁸, so an overestimated M′ is harmless. S_N uses the exact m_k. The step guard becomes
`M̄ ρ² ≤ 4`. Everything else is unchanged.

**Re-validation, in order:**
1. G0 again, in full. The same exact traces must be enclosed with ≥ 10 digits.
2. G2 again, in full.
3. Only then G3 (attempt 2).

**A1 G2 re-run: stopped by me (2026-09-27).** It was stopped before the A2 code change could reach any row:
each row child imports `ia_hub` fresh, so later rows would have run the A2 integrator. Row 0 (ZV equatorial)
had PASSED under A1. Row 1 (raw Kerr axial) was still in its first certificate search after 16 min. PIDs 9915
and 11094 were mine and are killed. `qsim/mr_mn_G2_A1.txt` is kept. G0 and G2 are now re-run under A2.
