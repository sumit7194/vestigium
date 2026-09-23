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
