# Pre-registration — a Morales–Ramis non-integrability tool, Stage 1 (build + known answers)

**Committed before any tool code exists.** Requested by the bridge on 2026-09-23, under the fleet plan the user approved. **Scope: Stage 1 only** — build the tool and pass known answers. **No new targets** (Manko–Novikov or others) until every Stage-1 criterion below has passed and the bridge coordinates Stage 2.

## What the tool proves, and what it cannot

**Morales–Ramis theorem.** Let `H` be a complex-analytic Hamiltonian and `Γ` a non-equilibrium integral curve. If `H` is Liouville-integrable with first integrals **meromorphic** in a neighbourhood of `Γ`, then the identity component `G⁰` of the differential Galois group of the variational equation along `Γ` is **abelian**. The same holds for the normal variational equation (NVE), and, by Morales-Ruiz–Ramis–Simó (2007), for every higher-order variational equation.

So the tool has **three outputs, and never merges them**:

| output | meaning | proves |
|---|---|---|
| `OBSTRUCTION` | `G⁰(NVE)` proven **non-abelian** | the system is **not** meromorphically integrable near `Γ` |
| `NO_OBSTRUCTION` | `G⁰(NVE)` proven **abelian** | **nothing about integrability** — the necessary condition is simply met at first order |
| `INCONCLUSIVE` | `G⁰` could not be determined (coefficients not rational after algebraisation, poles not exactly computable, degree bound exceeded, …) | nothing; **reported as such, never mapped to either of the other two** |

`NO_OBSTRUCTION` is **not** a proof of integrability. `INCONCLUSIVE` is **not** `NO_OBSTRUCTION`. A tool that fails silently must land in `INCONCLUSIVE`, which is the bridge's "honestly, not by failing silently" requirement, made mechanical.

## Method, from the published algorithms (not from anyone's code)

1. **Particular solution `Γ`** on an invariant submanifold; the variational equation; the NVE (a second-order linear ODE for 2-DOF systems).
2. **Algebraisation:** change the independent variable to make the coefficients rational. `G⁰` is invariant under this pullback (Morales–Ramis; Baider–Churchill–Rod–Singer).
3. **Reduced form** `y'' = r y`, `r ∈ ℚ̄(z)`, via `r = p²/4 + p'/2 − q`. This multiplies the group by at most a scalar factor, so whether `G⁰` is abelian is preserved.
4. **Kovacic's algorithm** (Kovacic 1986), implemented from the published statement: the necessary conditions for cases 1–3, then the case-1, case-2 and case-3 searches.
5. **From the Kovacic case to `G⁰`:**
   - **case 4** (no Liouvillian solution): `G = SL(2)` → `OBSTRUCTION`.
   - **case 3** (finite primitive): `G⁰ = {1}` → `NO_OBSTRUCTION`.
   - **case 2** (imprimitive): `G⁰ ⊂` diagonal torus → `NO_OBSTRUCTION`.
   - **case 1** (reducible, `y₁ = e^{∫ω}`): `G ⊂` Borel. **Not automatically abelian.** `G⁰` is the full Borel group, hence non-abelian, **iff** `y₁` is transcendental (its multiplicative part is `ℂ*`) **and** the additive part is non-trivial (no rational `R` solves `R' − 2ωR = 1`, i.e. `y₂ = y₁∫y₁⁻²` is not of exponential type). Otherwise `G⁰ ∈ {1, ℂ*, ℂ}` → `NO_OBSTRUCTION`. Both conditions are checked explicitly, not inferred.
6. **Independent routes** — the house rule of two routes sharing no code path:
   - **Kimura's criterion** where the NVE is a Riemann P-equation (three regular singular points); it must agree with Kovacic on Liouvillian vs. not.
   - **Numerical monodromy** where the NVE is Fuchsian. By Schlesinger's theorem `G` is the Zariski closure of the monodromy group. The monodromy matrices are computed by high-precision integration around the singular points; an `OBSTRUCTION` must be corroborated by monodromy that is not virtually abelian.

## Calibration suite — poison first

These run **before** any Hamiltonian control. Every expected answer comes from a classical theorem or holds by construction, not from any fleet output.

**Must NOT be called `OBSTRUCTION`** (Liouvillian with abelian `G⁰` by construction). A tool that misses these would manufacture false proofs:

| equation | why the answer is known | expected |
|---|---|---|
| `y'' = y` | `e^{±z}` | case 1, `G⁰ = ℂ*` → `NO_OBSTRUCTION` |
| `y'' = −2/(9z²) · y` | `z^{1/3}, z^{2/3}` algebraic | case 1, `G` finite → `NO_OBSTRUCTION` |
| `y'' = (ω' + ω²) y` for a chosen rational `ω` with algebraic `e^{∫ω}` and a second exponential solution | built to be diagonal/finite | `NO_OBSTRUCTION` |
| Bessel of order ½ in reduced form, `y'' = −y` | `e^{±iz}` | `NO_OBSTRUCTION` |
| Riemann P with exponent differences `(½, ⅓, ⅓)` | Schwarz: tetrahedral | **case 3**, `NO_OBSTRUCTION` |
| `(½, ⅓, ¼)` | octahedral | **case 3**, `NO_OBSTRUCTION` |
| `(½, ⅓, ⅕)` | icosahedral | **case 3**, `NO_OBSTRUCTION` |
| `(½, ½, ν)`, `ν` generic rational | dihedral | **case 2**, `NO_OBSTRUCTION` |

**Must be called `OBSTRUCTION`:**

| equation | why | expected |
|---|---|---|
| Airy `y'' = z y` | classically non-Liouvillian | case 4 |
| Bessel of order 0, reduced | classically non-Liouvillian | case 4 |
| Weber `y'' = (z² + 1) y` | **Liouvillian** (`e^{z²/2}`), but `y₂ ∝ e^{z²/2}∫e^{−z²}` has a non-trivial additive part and a transcendental multiplicative part → **full Borel `G⁰`** | case 1 **and** `OBSTRUCTION`. This is the poison for "case 1 ⇒ integrable". |
| Riemann P with a generic non-Schwarz triple, e.g. `(⅓, ⅕, ⅐)` | not in Schwarz's list, no odd-integer sum | case 4 |

**Must be called `INCONCLUSIVE`:** an input with non-rational coefficients (e.g. `r = sin z`). The tool must refuse it, not guess.

**Cross-route agreement:** on every Riemann-P entry, Kimura and Kovacic must agree. On every Fuchsian entry, numerical monodromy must be consistent (finite, abelian or non-abelian, as expected).

**Any calibration miss stops Stage 1.** No Hamiltonian control runs until the whole suite passes.

## The Hamiltonian controls

| control | system | expected | a FAIL is |
|---|---|---|---|
| **A** | Zipoy–Voorhees geodesics, `δ = 2` | `OBSTRUCTION` — reproducing Maciejewski, Przybylska & Stachowiak, PRD 88, 064003 (2013), arXiv:1302.4234 | `NO_OBSTRUCTION` or `INCONCLUSIVE` |
| **A′** | the **same family and particular solution at `δ = 1`** (Schwarzschild: integrable) | `NO_OBSTRUCTION` | **`OBSTRUCTION` — a false proof of non-integrability of an integrable system. The worst failure; it would also void A.** |
| **B** | Kerr geodesics (integrable: Carter constant) | `NO_OBSTRUCTION`, reached **positively** (a named Kovacic case with abelian `G⁰`) | `OBSTRUCTION` (tool broken) or `INCONCLUSIVE` (not passed) |

A′ was added here, not requested. It is the cleanest poison for A: one family, one particular solution, one parameter, with the answer flipping at a known value. **A is trusted only after A′ has passed.** **B is trusted only after the tool has said `OBSTRUCTION` on the calibration's non-abelian cases and on A.**

**The particular solutions are fixed by an amendment filed before any control runs.** They will follow the published setup of arXiv:1302.4234, read from its rendered pages. For Kerr, the analogous invariant submanifold is used, and wherever more than one natural particular solution exists, **at least two** are tested; every one must give `NO_OBSTRUCTION`.

**My own derivation, not the paper's formulas.** The NVE is derived here symbolically from the metric; the paper's printed NVE is used only as a comparison. If the two differ, that is a finding to resolve **before** any verdict, not a reason to adopt theirs.

## Setup correspondence — is the tool testing the claim it will be quoted for?

**The claim a future `OBSTRUCTION` will support:** "this deformed black hole has **no** extra conserved quantity of **any** degree." **The condition the tool actually tests:** "no additional first integral **meromorphic in a neighbourhood of one particular solution `Γ`**, at the chosen parameter values (`E`, `L_z`, the deformation)."

These match only up to three gaps, stated now so they cannot be dropped later:
- **Meromorphic vs. anything.** A non-meromorphic integral (e.g. one with essential singularities along `Γ`) is not excluded. "Of any degree" is justified only for polynomial (or rational) integrals in the momenta, which are meromorphic.
- **Near `Γ` vs. globally.** The theorem excludes integrals meromorphic near `Γ`, which is the strong form; it doesn't need global control.
- **At the tested parameters.** An obstruction at one parameter point shows non-integrability of the family *as a family*. It does **not** exclude integrable special values (Zipoy–Voorhees `δ = 1` is exactly one). Every target report must state the parameter point.

Conversely, a `NO_OBSTRUCTION` on Kerr corresponds to **"the necessary condition holds along this `Γ`"**, and to nothing stronger. The Kerr control tests the tool's *soundness*; it does not re-establish Kerr's integrability, which is known independently (Carter 1968).

## Pass criterion for Stage 1

**All** of: the calibration suite passes in full (including cross-route agreement); A = `OBSTRUCTION`, and its mechanism (Kovacic case, or criterion) is consistent with the paper's; A′ = `NO_OBSTRUCTION`; B = `NO_OBSTRUCTION` on every particular solution tested; **no control is `INCONCLUSIVE`.** Anything else: **Stage 1 FAILED**, reported to the bridge as failed, with the failing item named.

## Named ways this fails

1. **A Kovacic bug that misses solutions** → false `OBSTRUCTION`. Guarded by the constructed-Liouvillian entries, by A′, and by Kimura and monodromy.
2. **Case 1 treated as integrable** → a missed obstruction. Guarded by Weber.
3. **Algebraisation error** (a wrong change of variable, or a non-rational pullback accepted). Guarded by recomputing the NVE's singular points and exponents in both variables and checking they correspond.
4. **An NVE derivation error** (wrong metric component, wrong invariant manifold). Guarded by comparison with the printed NVE of arXiv:1302.4234, and by A′.
5. **Parameter specialisation.** Fixing `E` and `L` at particular values can land on a special, more-integrable locus. `OBSTRUCTION` at one generic choice proves non-integrability; `NO_OBSTRUCTION` at one choice proves nothing general. For B, two independent parameter choices are tested.
6. **Exact-arithmetic failures** (poles at algebraic numbers sympy cannot isolate, irrational exponents). These route to `INCONCLUSIVE`, never to a verdict.

## What Stage 1 cannot establish

Passing Stage 1 shows the tool **reproduces two textbook-class answers and a calibration suite**. It does not show the tool is correct on every input. And `NO_OBSTRUCTION` on any future target will say only that the first-order necessary condition is met; it says nothing that integrability holds.

## Environment and provenance

Built in the repo's own `sims/.venv` (sympy 1.14.0, mpmath 1.3.0); **no download**. The implementation follows Kovacic, J. Symbolic Comput. 2 (1986) 3–43, and published expositions. Pointers the bridge relayed (arXiv:2211.00804, 2309.04449, Morales-Ruiz–Ramis–Simó 2007) are **verified before being relied on**. No fleet code is used; ansatz's code in particular is not consulted.

---

## AMENDMENT 1 — particular solutions fixed (2026-09-24), filed BEFORE any control has run

**No Hamiltonian control has been run at the time of filing.** Calibration status
at this point: the Kovacic half passes 13/13 (`qsim/mr_calibration_kovacic.txt`).
The cross-route half (Kimura, monodromy) is **not yet done**, so Stage 1 has not
passed.

**The NVE derivation is validated before any verdict.** `qsim/mr_nve.py`, derived
here from the metric, reproduces arXiv:1302.4234 eqs. (16)–(17) **exactly**
(symbolic difference 0 for general `p₀, μ`), using their variable `ξ₂ = δp_y`. My
derivation and the paper's printed NVE agree on a 21-term polynomial, which
checks both the derivation and the transcription of the paper.

Each control is run on **both** NVE forms (`ξ₂ = δp_y` and `ξ₁ = δy`). They
describe the same system, so they must give the same verdict; a disagreement fails
the control.

| control | metric | particular solution | parameters |
|---|---|---|---|
| **A** | Zipoy–Voorhees `δ = 2`, `m = 1` | the paper's: `y = 0, p_y = 0, p_φ = 0` (equatorial straight line through the centre) | `p₀ = E = 1`; **`μ = 2` and `μ = 3`**, both generic. They avoid the paper's special values `μ ∈ {0, ±1, ±√5}`, where the generic argument doesn't apply. |
| **A′** | Zipoy–Voorhees `δ = 1` (Schwarzschild) | the same | the same `μ = 2, 3` |
| **B1** | Kerr, `M = 1`, `a = 3/5` | equatorial `u = cos θ = 0, p_u = 0`, **`L = 0`** | `E = 3`, `μ² = 118` |
| **B2** | Kerr, the same | equatorial, **`L = 2`** | `E = 1`, `μ² = 125/63` |

**Why these Kerr numbers.** Kovacic needs every pole exactly computable.
`a = 3/5` makes the horizons rational (`r± = 9/5, 1/5`). The equatorial radial
potential is `r × cubic` and is **linear in `μ²`**, so choosing a rational turning
point (`r₁ = 2` for B1, `r₁ = 3` for B2) and solving for `μ²` makes the cubic
`(r − r₁) × quadratic`, with exact roots. **The values were chosen for exact
computability, before any verdict, and no values were tried and discarded on the
basis of an outcome.**

---

## AMENDMENT 2 — a declared pre-filter (2026-09-24), filed BEFORE any control result

The first control run was **aborted after 10 minutes with no output**. No
verdict or partial result had been printed, so nothing was seen. The cause:
Kovacic's case 3 at `n = 12` over the six singular points of the ZV NVE is
~13⁶ exponent families, thousands of which need degree-40+ polynomial searches.

**Added — a mathematically rigorous pre-filter, not a change of criterion.** If a
singular point has an integer exponent difference **and** the Frobenius
recursion is inconsistent there (a logarithm), its local monodromy is a
non-trivial unipotent element. A finite group (case 3) contains none, and neither
does a subgroup of the diagonal/anti-diagonal group (case 2). **So a log point
excludes cases 2 and 3.** If case 1 has also failed, `G = SL(2)`, i.e. case 4.
arXiv:1302.4234 uses the same Frobenius argument.

**Validated before use:**
- **Verdicts are identical with and without the filter on all 18 calibration
  entries** (`qsim/mr_calibration_logfilter.txt`).
- **Detector unit tests** against equations with exact solutions
  (`qsim/mr_logfilter_unittests.txt`). **No false log** at integer differences 2,
  3 and 5 (`z^{3/2}, z^{−1/2}`; `z², z⁻¹`; `z³, z⁻²`), and logs found where they
  exist (a repeated exponent, a simple pole, Bessel-0).
- A bug caught before use: the first version fetched a fixed 6 Laurent
  coefficients. For `N > 5` it would have zero-padded the recursion, and so
  fabricated or hidden a log. It now fetches `N+1`, and the difference-5 unit test
  exercises this.

**Every `OBSTRUCTION` that rests on this filter says so in its reason string**
("cases 2 and 3 excluded: logarithmic point at …"), so a reader can always see
which argument carried the verdict.

---

## AMENDMENT 3 (2026-09-24) — filed after A's result, before any A′/A″/B result

**State at filing:** A has run and **passed**: `OBSTRUCTION` at `μ = 2, 3`, case 4
in both NVE forms, with monodromy independently finding `SL(2)`. A′ then
**crashed** before producing any verdict. A″ and B have not run.

**Cause:** the registered A′ (`δ = 1, L = 0`) is **degenerate**. By spherical
symmetry `∂²H/∂y² ≡ 0` (checked symbolically), so the NVE decouples into
`ξ₂′ = 0`, `ξ₁′ = aξ₂`, and `G⁰` lies in the additive group — abelian, **by an
analytic argument**. The `ξ₂` elimination divides by `B` and is undefined.
- The degenerate form now returns the analytic `NO_OBSTRUCTION`, **explicitly
  labelled as not a Kovacic verdict**. The `ξ₁` form still goes through Kovacic
  and must itself give `NO_OBSTRUCTION`.
- **This made A′ a weaker poison than intended**, so a **non-degenerate** one is
  added. **A″** is Schwarzschild (`δ = 1`) with `L = 1`, where
  `B = 1/(x+1)² ≠ 0`. It is integrable by spherical symmetry, so it must give
  `NO_OBSTRUCTION`, at `μ = 2, 3`, `E = 1`.
- The trust order now requires A′ **and** A″ before A counts.
- **A's own verdict is unaffected**; the rerun must reproduce it identically.
