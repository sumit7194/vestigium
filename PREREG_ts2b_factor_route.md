# Pre-registration — Stage 2b: a root-free, factor-by-factor Kovacic route for TS δ = 2

**Committed before any 2b code exists and before any 2b computation.** Stage 2 (`PREREG_ts2_morales_ramis.md`,
outcome d00ce98) gave INCONCLUSIVE at all 8 target rows. The cause is that the NVE's turning-point sextic has
Galois group S6, while the Stage-1 tool needs explicit poles. The bridge approved Stage 2b on 2026-09-24. Its
instructions: register separately; verdict rule exactly as proposed; validate on the Stage-1 known answers first;
the same independence rules.

**Independence (unchanged from Stage 2).**
- Not opened: ansatz's `TS2_PREDICTION_SEALED.md`, and anything about TS in SpaceTime.
- No literature search on TS integrability or chaos until this verdict is committed.
- What is already known about the TS NVE is only the Stage-2 diagnostic in d00ce98: the denominator factors and
  their Galois groups. No 2b quantity (local exponents, logs, d-values) has been computed for any TS row.

## The route (new module `qsim/mr_factor_route.py`; the Stage-1 Kovacic code is not modified)

Input: reduced `y'' = r y`, with `r = s/t ∈ ℚ(x)`. Factor `t = ∏ g_j^{m_j}` over ℚ. No root is ever computed.

1. **Scope.** Every `m_j ∈ {1, 2}` (finite poles regular) and `ord∞ = deg t − deg s ≥ 2`. Otherwise the result
   is `INCONCLUSIVE (out of scope)`.
2. **Local data per factor.** For `m_j = 2`, `b_j = lim (x−c)² r` at a root c of `g_j`, computed in
   `ℚ(c) = ℚ[a]/(g_j)` by polynomial remainder. **If `b_j` is not a rational constant**, the exponents differ
   between conjugate roots, and the result is `INCONCLUSIVE (out of scope)`. If `b_j ∈ ℚ`, all `n_j = deg g_j`
   roots share `α± = ½ ± ½√(1+4b_j)`. For `m_j = 1`: `α = 1`. At ∞: `ord∞ > 2` gives `α∞ ∈ {0, 1}`;
   `ord∞ = 2` gives `α∞± = ½ ± ½√(1+4b∞)` with `b∞ = lc(s)/lc(t)`.
3. **Case-1 necessary condition (Kovacic step 2), exactly.** Since the exponents are constant on each factor,
   `d = α∞^± − Σ_j [k_j α_j⁺ + (n_j − k_j) α_j⁻]` depends only on the counts `k_j ∈ {0..n_j}`. **Every** count
   combination and both signs at ∞ are enumerated. For TS this is at most 2·2·5·7·9 = 1260 values.
   - Each √(1+4b) is written exactly as `q√m`, with `m` a squarefree integer (negative allowed).
   - `d ∈ ℤ≥0` iff every `√m`-coefficient with `m ≠ 1` vanishes (the {√m} are linearly independent over ℚ) and
     the rational part is a non-negative integer.
4. **Log point, Galois-symmetric.** At a factor with `b_j ∈ ℚ` and `√(1+4b_j) = N ∈ ℤ≥0`, the Laurent
   coefficients `f_k ∈ ℚ(c)` come from exact series division in `ℚ[a]/(g_j)`. The Frobenius recursion for the
   smaller exponent runs to k = N, and the point is logarithmic iff the k = N consistency term is non-zero in
   `ℚ(c)`. That is a statement about one root iff about all conjugates, because an element of `ℚ[a]/(g)` is 0 at
   one root iff it is 0 at all.
   - N = 0 is always logarithmic, and so is a simple pole (m = 1) of reduced r.
   - ∞ is handled the same way after `x = 1/w` when `ord∞ ∈ {2, 3}`; for `ord∞ ≥ 4` it is an ordinary point.
   - A log point gives a non-trivial unipotent local monodromy, which excludes Kovacic cases 2 and 3.
     This is the argument the Stage-1 pre-filter already uses.

**Verdict rule (as proposed to and approved by the bridge; the route never outputs NO_OBSTRUCTION):**

    OBSTRUCTION   iff  (a log point exists)  AND  (no count combination gives d ∈ ℤ≥0)
    INCONCLUSIVE  otherwise, including any surviving candidate d and any out-of-scope factor

Soundness: no d ∈ ℤ≥0 means case 1 is impossible (Kovacic's necessary condition). The log point excludes cases 2
and 3. So G = SL(2), G⁰ is non-abelian, and there is an obstruction.

**Second route: numerical monodromy with numeric poles.** A declared additive change to `mr_monodromy.py`: an
optional `poles=` argument. When it is given, the finite singular points come from high-precision numeric roots
of each factor (`nroots`, 30 digits) instead of `RationalR`. The default path is byte-for-byte unchanged.
Everything else is the Stage-1 classifier.

## Setup correspondence

This runs at exactly the Stage-2 condition: the same supplied metric, P1 and P2, σ = 1, the same (E, L, μ²),
and the same equatorial Γ, through the same loader and NVE. An OBSTRUCTION here supports exactly the Stage-2
claim, with exactly its gaps (see `PREREG_ts2_morales_ramis.md` § Setup correspondence), and nothing wider. The
only change is *how* G⁰ is decided: root-free necessary conditions instead of explicit-pole Kovacic.

## Validation, run first, all guarded; the order is fixed

**V-neg: must never be OBSTRUCTION** (a false OBSTRUCTION here voids 2b).
- Every Stage-1 calibration case whose expected verdict is NO_OBSTRUCTION. Those out of scope must give
  INCONCLUSIVE (out of scope).
- Two new poisons with log points at **non-rational algebraic** factors, built to be Liouvillian:
  `r = y₁''/y₁` for `y₁ = (x² − 2)^{1/2}` and for `y₁ = (x³ − 2)^{1/2}`. The double exponent gives a log; y₁ is
  algebraic. Expected INCONCLUSIVE (a d ∈ ℤ≥0 survives).
- Kerr: Stage-1 B1 and B2 (BL) and the Stage-2 C2 and C3 rows (WP), both forms.
- Schwarzschild: Stage-1 A″ (L = 1), both forms.

**V-pos: must be OBSTRUCTION** (the bridge's condition, which tests that the route has power).
- ZV δ=2, Stage-1 A at μ = 2 and 3, and the Stage-2 C1 row (through the WP loader), both forms.

**V-info: recorded, not gating.**
- Stage-1 calibration OBSTRUCTION cases. The route may say INCONCLUSIVE there; it is incomplete by design.
- `P(0, 0, 1/3)`, which is non-Liouvillian by Kimura, with a log at 0 and 1.

**V-mono.** Numeric-pole monodromy must reproduce the Stage-1/Stage-2 monodromy verdicts on Stage-1 A, B1 and
B2, and on the Stage-2 C1–C3 rows.

**2b passes validation iff:** V-neg has no OBSTRUCTION, V-pos is all OBSTRUCTION, and V-mono agrees everywhere.
Otherwise the TS rows are not run as a verdict.

## Target rows (the same 8 as Stage 2)

T1 `(1, 0, 4)`, T2 `(1, 0, 9)` and T3 `(1, 1, 4)` at P1 = (3/5, 4/5) and P2 = (4/5, 3/5), with σ = 1, through
the Stage-2 loader and NVE.

**Row verdict.**
- **OBSTRUCTION** iff the route gives OBSTRUCTION on **both** forms (ξ₂, ξ₁) **and** numeric-pole monodromy
  gives OBSTRUCTION (SL2) on both forms.
- A monodromy NO_OBSTRUCTION anywhere is a **FAIL**, a route disagreement.
- If monodromy cannot be computed, the row is reported as "route OBSTRUCTION, monodromy uncorroborated". That
  is a lesser grade, stated as such.
- If the route proves OBSTRUCTION on exactly one form, that is reported as a single-form proof, labelled below
  the house standard. The two forms are cyclic-vector presentations of one system, so it is mathematically
  sufficient.
- Anything else is INCONCLUSIVE.

**The wording on OBSTRUCTION is exactly the Stage-2 wording, per P and per (E, L).** For TS δ=2 at P, the reduced
geodesic flow `H_{E,L}` admits no additional first integral that is meromorphic in a neighbourhood of Γ; hence
it is not meromorphically Liouville-integrable, with all the setup-correspondence gaps of Stage 2
(meromorphic only, complex neighbourhood of Γ, the tested parameters, the supplied metric).

**Resources.** As in Stage 2: guarded children, ≤ 1024 MB, ≤ 1800 s each, strictly sequential. When the bridge
announces ansatz's go, I stop at a row boundary and report.

## Named ways this fails

1. `b_j` is irrational on some factor (likely candidate: the ξ₂-only octic). That form is then out of scope and
   the row rests on the other form.
2. A surviving d ∈ ℤ≥0 (for example from an apparent singularity with integer exponent difference): INCONCLUSIVE.
3. No log point at all: INCONCLUSIVE. This route cannot exclude case 2 without one.
4. Numeric monodromy fails to converge (19 singular points, some close together): uncorroborated.

**ERRATUM (before any 2b computation).** "The same 8" target rows is a miscount carried over from the Stage-2
outcome. The target is **6 rows**: T1, T2 and T3 at P1 and P2.

---

## OUTCOME OF VALIDATION, 2026-09-24. **2b as registered FAILS validation (V-pos).** The TS rows were not run.

`qsim/mr_ts2b_validation.txt` and `mr_ts2b_run.json`; rows 0–18, all guarded, peak ≤ 89 MB.

- **V-neg: PASS.** No OBSTRUCTION anywhere across the Stage-1 calibration NO_OBSTRUCTION cases, the two
  algebraic-factor poisons (log found at x² − 2 and at x³ − 2, d = 0 survives, INCONCLUSIVE as expected), Kerr BL
  B1 and B2, Kerr WP C2 and C3 (8 rows), and Schwarzschild A″ at μ = 2 and 3.
- **V-mono: PASS.** Numeric-pole monodromy equals the default-path monodromy on every Hamiltonian row: SL2 on
  ZV δ=2, and NO_OBSTRUCTION on Kerr and Schwarzschild.
- **V-info.** P(0, 0, 1/3) gives OBSTRUCTION, consistent with Kimura. The Stage-1 OBSTRUCTION calibration
  cases are out of scope or give no log point, so INCONCLUSIVE, as allowed.
- **V-pos: FAIL.** ZV δ=2 at μ = 2 and 3, and C1: route **INCONCLUSIVE** on both forms. The log point is found
  (x = 0, N = 2), but the case-1 **necessary** condition leaves `d ∈ {0, 1, 2, 3}` (ξ₂) and `{0, 1}` (ξ₁). Stage 1
  excluded these only by the P-search, a step this route does not have.

**Diagnosis: sound but underpowered.** The necessary condition alone does not exclude case 1 on the obstruction
control. No rule change is made here. A strengthened route is proposed to the bridge as a post-failure amendment
and needs its approval before it is registered.

---

## AMENDMENT 2b′ (2026-09-24), POST-FAILURE, approved by the bridge. Filed before any 2b′ code or computation.

This is labelled post-failure because 2b as registered failed V-pos (cbc61af). The failure stays on record, and
2b′ is weaker evidence than a first-attempt pass.

**Lemma.** Let `y'' = r y` with `r ∈ ℚ(x)`, and suppose it has a logarithmic singular point. If case 1 of
Kovacic's algorithm holds (a solution y with `ω = y'/y ∈ ℚ̄(x)`), then that ω is **unique** and **ω ∈ ℚ(x)**.

**Proof.**
1. At a regular singular point with integer exponent difference N and a logarithm, the exponents are `(1 ∓ N)/2`.
   Both `e^{2πi(1∓N)/2}` equal `(−1)^{1−N}`, so the local monodromy is `M = ±u`, with u unipotent and `u ≠ I`
   (the log term). Monodromy lies in the differential Galois group G (over `ℚ̄(x)`).
2. Solutions y with `y'/y ∈ ℚ̄(x)` correspond one-to-one to G-invariant lines in the solution space. For
   `σ ∈ G`, `σ(y) = λ_σ y` iff σ fixes `y'/y`. By the Galois correspondence, `y'/y` lies in the base field iff every
   σ fixes it.
3. A G-invariant line is M-invariant. `±u` with `u ≠ I` unipotent has exactly one eigenline, so G has **at most
   one** invariant line, and case 1 has at most one ω.
4. `r ∈ ℚ(x)`, so for `τ ∈ Gal(ℚ̄/ℚ)` acting on coefficients, `ω^τ` also solves `ω' + ω² = r`. By uniqueness,
   `ω^τ = ω` for all τ, so every coefficient of ω is fixed by `Gal(ℚ̄/ℚ)`, and `ω ∈ ℚ(x)`. ∎

**Consequence for the search.** In Kovacic's case 1 with every finite pole of order ≤ 2 and `ord∞ ≥ 2`,
`ω = Σ_c α_c/(x−c) + P'/P` with P monic, where the `α_c` range over the local exponents.
- **Scope condition (bridge).** Each factor's local coefficient b must be in ℚ, so that every root of `g_j` has the
  same pair `α_j±`. Any factor with `b ∈ ℚ(c) \ ℚ` gives **INCONCLUSIVE (out of scope)**. This was already the 2b
  rule, and it is kept.
- Given that, ω ∈ ℚ(x) forces the same `α_j` at every root of `g_j`. Its residues are Galois-conjugate, and
  conjugate roots of an irreducible g are permuted transitively. So `θ = Σ_j α_j g_j'/g_j ∈ ℚ(x)`.
- For P: its roots are the zeros of y off the singular set. That set is Galois-stable because `ω ∈ ℚ(x)`, so
  `P = exp ∫(ω − θ) ∈ ℚ[x]`, monic.
- **Why the counts drop.** This is where 2b′ is stronger than 2b: only the symmetric choices `k_j ∈ {0, n_j}` need
  enumerating, `2^{#order-2 factors} × 2` at ∞, and each surviving d gets the P-search.
- **Where the Stage-1 cases would apply.** At a factor with `N = 0` both exponents coincide; for simple poles α = 1.
  Other Stage-1 cases (order > 2 poles, `ord∞ < 2`) are out of scope as in 2b.

**Route 2b′ (a new function `analyse_v2` in `mr_factor_route.py`; `analyse` is kept unchanged for the record):**

1. Scope and local data exactly as 2b: m ∈ {1, 2}, `ord∞ ≥ 2`, b ∈ ℚ on every factor.
2. A log point is required. It is found exactly as in 2b.
3. For each symmetric choice, `d = α∞ − Σ_j n_j α_j`. If `d ∈ ℤ≥0` (exact, with square roots split as in 2b),
   solve for a monic `P ∈ ℚ[x]` of degree d with `P'' + 2θP' + (θ' + θ² − r)P = 0`. That is an exact linear
   system over ℚ, the Stage-1 `_monic_poly_solution`, degree cap 60. A cap hit gives INCONCLUSIVE.
4. **OBSTRUCTION** iff a log point exists AND no symmetric choice yields P. **INCONCLUSIVE** if a P is found:
   case 1 holds, and this route does not grade the Borel part. It is also INCONCLUSIVE when there is no log point,
   when something is out of scope, or when the cap is hit. It never outputs NO_OBSTRUCTION.

**Re-validation, in full, post-failure.**
- The same V-neg, V-pos, V-info and V-mono sets as 2b, with the same pass rule.
- **Plus a new poison aimed at the P-step:** the reduced Legendre equation for n = 2 and n = 3. It is reducible:
  `y₁ = P_n(x)·(1 − x²)^{1/2}` with P_n non-trivial, of degree n. It has a log at ±1 (double exponent). It must
  **not** be OBSTRUCTION; the expected result is INCONCLUSIVE, with P of degree n found.
- 2b′ passes iff V-neg has no OBSTRUCTION, V-pos (ZV δ=2 at μ = 2, 3, and C1) is all OBSTRUCTION, and V-mono
  agrees. Only then do the 6 TS rows run, under the row rule and wording of 2b.

**Noted, not used.** The bridge's message quotes `b = −3/16` at the TS turning points. **I have not computed any
TS local data**; that is the bridge's expectation from the general theory of turning points. It is not a result,
and it plays no part in this registration.

**CLARIFICATION to 2b′ (before any 2b′ code).** The step "ω ∈ ℚ(x) forces the same `α_j` at every root" holds
when the exponents `α_j± = ½ ± ½√(1+4b_j)` are **rational**. The residue of ω at c lies in ℚ(c) and
`α_{τc} = τ(α_c)`; a rational α is fixed by τ, and the roots are permuted transitively.

If `b_j ∈ ℚ` but `√(1+4b_j) ∉ ℚ`, the rule is:
- Summing the conjugate residues gives `Σ_c α_c = Tr_{ℚ(c)/ℚ}(α_c) ∈ ℚ`. With `α_c = ½ + ε_c √u/2`, this
  forces `Σ ε_c = 0`.
- **Odd `n_j`:** no such choice exists, so case 1 is **impossible**. That is proved, and the factor contributes
  no case-1 solution.
- **Even `n_j`:** a non-symmetric pattern is possible, and its θ is not in ℚ(x), so it cannot be P-searched
  root-free. The row is **INCONCLUSIVE (out of scope)**, unless the exact d-test (2b's split-radical test, with
  this factor contributing `n_j/2`) already leaves no `d ∈ ℤ≥0`.

The same applies at ∞, which is a rational point: an irrational `α∞` simply fails the exact integer test for d.
