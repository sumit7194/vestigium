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

---

## AMENDMENT 4 (2026-09-24) — resource incident, watchdog, and a radical-free certificate search

**State at filing:** A passed. A′ passed (degenerate: analytic argument, plus
Kovacic on the `ξ₁` form). **No A″, B1 or B2 result has been produced.**

**Incident, mine.** The controls process ran over an hour on A″ and reached a
**10 GB footprint** on the shared machine, with swap at 3.1/4.1 GB. It had no
watchdog. RSS read only 0.8 GB, because most of the footprint was compressed or
swapped, so RSS is not a usable signal. The bridge flagged it and I killed it.
Cause: A″'s NVE has order-2 poles at the three roots of the irreducible cubic
`3x³ + x² − 6x − 6` (Galois group `S₃`). sympy wrote them as nested Cardano
radicals, and the Laurent and linear algebra over those radicals swelled.

**Fixes (algorithmic; A″'s definition and expected outcome are unchanged, per the
bridge):**
1. **Watchdog** (`qsim/mr_watchdog.py`): every control runs in its own child
   process. The parent polls the **physical footprint** (macOS `footprint`) and
   kills the child above 4 GB or after 30 minutes. **Box guards:** it also kills if
   free swap < 512 MB or free disk < 5 GB. A killed control is recorded as
   `INCONCLUSIVE (resource limit)`, never as a verdict.
2. **A Galois-symmetric case-2 certificate search over ℚ**, with no radicals: one
   exponent per irreducible factor, so `θ` is rational. **Whatever it finds is
   checked by an exact rational identity that is a proof on its own:** for rational
   `φ`, with `Δ = 4r − φ² − 2φ′`, the conditions `Δ′ + 2φΔ ≡ 0` and `Δ ≢ 0` make
   `(φ ± √Δ)/2` two distinct Riccati solutions, which puts `G⁰` in a torus. **If the
   search finds nothing, the full search still runs, guarded**, and a failure there is
   `INCONCLUSIVE`, never an obstruction by default.
   - Validated: the calibration still passes 18/18, and both known case-2 equations
     are now found through this path and certified.
   - Poison test: the identity **rejects** `φ + 1/z`, `φ + 1/7` and `φ + 1/(z−3)`
     on both.
3. **Physics expectation, recorded before the run:** Schwarzschild with `L ≠ 0` is
   spherically symmetric, so the out-of-plane perturbations are `∝ e^{±iφ(x)}`.
   Their logarithmic derivatives are algebraic of degree 2 (through `ẋ = √rational`),
   so **A″ should come out as Kovacic case 2.** This is an expectation, not a
   criterion; the criterion is still `NO_OBSTRUCTION`.

---

## OUTCOME of guarded run 1, and AMENDMENT 5 (2026-09-24)

**Guarded run 1: FAILED under the registered rule.** A and A′ pass. A″ (`μ = 2`),
B1 and B2 gave **Kovacic `NO_OBSTRUCTION` (case 2, certified by the exact identity)
but monodromy `OBSTRUCTION`**, and the routes must agree. A″ (`μ = 3`) hit the
30-minute limit and was recorded `INCONCLUSIVE`. **That failure stays on the record.**

**Resolved on an independent known answer, not by preferring the route I liked.**
The monodromy classifier looked for the invariant pair of lines only among the
eigenvectors of each generator. A *swap* (trace 0, order 4 — the local monodromy
at an exponent difference ½, e.g. a turning point) has eigenvectors that are not the
pair, so a group generated entirely by swaps fell through to `SL(2)`.
**Demonstrated on `P(½,½,√2)`**, an infinite dihedral group whose two finite
generators both have trace 0: Kovacic says case 2, Kimura family 1, and monodromy
said `SL(2)`. The calibration never caught it, because its only dihedral entry was
finite, so the BFS closed before the imprimitive branch ran. **A coverage gap in my
own calibration.**

**Fixes:**
1. Imprimitive candidates now include pairwise products of generators: two swaps of
   one pair multiply to a diagonal element whose eigenvectors are the pair.
   `P(½,½,√2)` is added to the calibration. **The full calibration passes on all
   three routes** (`qsim/mr_calibration_allroutes.txt`), and `SL(2)` detection is
   intact (`P(⅓,⅕,⅐)` is still `SL(2)`).
2. The case-2 certificate search runs **before** case 1. A verified certificate
   proves `G⁰` abelian on its own, so the verdict no longer waits on the radical
   case-1 search that timed out.

**Guarded run 2 follows, and it must re-establish A as well:** the change touches the
classifier that corroborated A.

---

## AMENDMENT 6 (2026-09-24) — run 2 aborted; the second attempt is labelled post-failure

**Guarded run 2 was aborted by me.** Its only completed row, Control A, hit the
30-minute limit (`INCONCLUSIVE`). Cause, mine: amendment 5 moved the case-2
certificate search ahead of everything. On Control A's six singular points that
search is slow, whereas the log check excludes case 2 there immediately. Fixed:
the log check now runs first, and the certificate search runs only when there is no
log point. Control A is back to `OBSTRUCTION` in 6.5 s, and the calibration is
unchanged (18 entries plus `P(½,½,√2)`).

**The next run is the SECOND ATTEMPT, post-failure.** It comes after a monodromy
bug fix and a search-order fix, both found by guarded run 1. **Guarded run 1's FAIL
stays on the record beside it.** The controls, parameters and expected outcomes are
unchanged; nothing about A″, B1 or B2 was altered.

---

## OUTCOME — SECOND ATTEMPT (post-failure), 2026-09-24. **Stage 1 NOT PASSED: one control INCONCLUSIVE.**

(`qsim/mr_controls_attempt2_result.txt`.) This attempt follows guarded run 1, which
**FAILED**, and that failure stands beside it.

| control | verdict | routes | |
|---|---|---|---|
| A, ZV δ=2, μ=2 and μ=3 | `OBSTRUCTION` | Kovacic case 4 in both forms; monodromy `SL(2)` in both | pass |
| A′, Schwarzschild L=0, μ=2 and μ=3 | `NO_OBSTRUCTION` | analytic (degenerate `ξ₂`); `ξ₁` certified case 2; monodromy agrees | pass |
| A″, Schwarzschild L=1, μ=2 | `NO_OBSTRUCTION` | case-2 certificate in both forms; monodromy agrees | pass |
| **A″, Schwarzschild L=1, μ=3** | **`INCONCLUSIVE`** | **30-minute limit** | **not passed** |
| B1, Kerr L=0 | `NO_OBSTRUCTION` | case-2 certificate in both forms; monodromy agrees | pass |
| B2, Kerr L=2 | `NO_OBSTRUCTION` | case-2 certificate in both forms; monodromy agrees | pass |

**By the registered criterion** — no control may be `INCONCLUSIVE`, and A counts
only after A′ and A″ — **Stage 1 has not passed.** Nothing returned a wrong verdict:
every row that finished agrees with its expected outcome, and the two independent
routes agree on every row that ran. The single gap is a resource limit on one
parameter point.

What a pass needs: A″ at μ=3 to finish. That's an algorithmic question, and the
same rule applies as for A″ before: fix the algorithm, never the control. Not
started tonight, because ansatz's job is queued behind this machine's current work.

---

## AMENDMENT 7 (2026-09-24) — the A″ μ=3 stall was the LOG CHECK; third attempt, post-failure

**Diagnosed with stage timings, guarded (≤1 GB).** A″ at μ=3 stalled inside
`has_log_point`, which expanded Laurent series at every pole. Here the poles sit at
the roots of the irreducible cubic `8x³ + 6x² − 11x − 11`, so those expansions ran
through Cardano radicals — the same swell amendment 4 removed from the certificate
search, one layer up. The exponent data at that factor, computed without radicals:
`b = −3/16`, so `1+4b = 1/4` (a turning point, difference ½). That matches μ=2; the
two points are not structurally different.

**Fix (algorithmic; the control is unchanged).** The log check now works **per
irreducible factor over ℚ**. A log requires an integer exponent difference
`√(1+4b)`, which is possible only if `b` is rational and `1+4b` is a rational square.
`b` comes from the radical-free routine, and only a genuinely integer difference at a
non-linear factor falls back to radicals. The calibration is unchanged (18 plus
`P(½,½,√2)`), and so are the log unit tests. **A″ μ=3 now takes 10 s** (peak 61 MB),
and a case-2 certificate is found in both NVE forms.

**Because the log check feeds every row, the entire control set is re-run as the
THIRD ATTEMPT, post-failure.** Guarded run 1 (FAILED) and the second attempt
(NOT PASSED: A″ μ=3 INCONCLUSIVE) stay on the record. Controls, parameters and
expected outcomes are unchanged. Per the bridge: ≤1 GB and ≤30 min per child.

---

# OUTCOME — THIRD ATTEMPT (post-failure), 2026-09-24. **STAGE 1 PASSES.**

(`qsim/mr_controls_attempt3_result.json`.) Guarded, 1 GB cap per child; every
child peaked below 100 MB, and the whole set took about 100 s.

| control | verdict | Kovacic | monodromy | |
|---|---|---|---|---|
| A, ZV δ=2, μ=2 | `OBSTRUCTION` | case 4, both forms | `SL(2)`, both | pass |
| A, ZV δ=2, μ=3 | `OBSTRUCTION` | case 4, both forms | `SL(2)`, both | pass |
| A′, Schwarzschild L=0, μ=2 | `NO_OBSTRUCTION` | analytic + case-2 certificate | agrees | pass |
| A′, Schwarzschild L=0, μ=3 | `NO_OBSTRUCTION` | analytic + case-2 certificate | agrees | pass |
| A″, Schwarzschild L=1, μ=2 | `NO_OBSTRUCTION` | case-2 certificate, both forms | agrees | pass |
| A″, Schwarzschild L=1, μ=3 | `NO_OBSTRUCTION` | case-2 certificate, both forms | agrees | pass |
| B1, Kerr L=0 | `NO_OBSTRUCTION` | case-2 certificate, both forms | agrees | pass |
| B2, Kerr L=2 | `NO_OBSTRUCTION` | case-2 certificate, both forms | agrees | pass |

Trust-ordered: A′ and A″ pass, so A counts; A passes, so B counts; nothing is
`INCONCLUSIVE`. **Every pre-registered Stage-1 criterion is met.**

**How to read this pass.** It's the third attempt. Guarded run 1 **FAILED** (the
routes disagreed, which exposed a monodromy bug), and the second attempt was **NOT
PASSED** (A″ μ=3 hit its time limit, which exposed a log-check swell). Each fix was
algorithmic. Each was confirmed on an independent known answer or by re-running the
full calibration, and none changed a control, a parameter or an expected outcome.
**A pass reached after two documented failures, with their fixes on record, is
weaker evidence than a first-attempt pass, and it is reported as exactly that.**

**What the tool now rests on, for Stage 2:**
- every `NO_OBSTRUCTION` is backed by an **exact rational certificate**
  (`Δ′ + 2φΔ ≡ 0`, `Δ ≢ 0`), which is a stand-alone proof, or by an explicitly
  labelled analytic argument;
- every `OBSTRUCTION` is backed by Kovacic case 4 (or case 1 with a full Borel
  group), **plus** an independent numerical `SL(2)` from monodromy wherever the NVE
  is Fuchsian;
- every run is guarded (footprint, time, free swap, free disk), and a killed run is
  always `INCONCLUSIVE`, never a verdict.
