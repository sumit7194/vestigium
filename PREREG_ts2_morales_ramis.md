# Pre-registration — Morales–Ramis tool, Stage 2: Tomimatsu–Sato δ = 2

**Committed before any computation on the target.** Stage 1 passed (third attempt, labelled post-failure,
commit 0ae727e; `PREREG_morales_ramis_tool.md`). The bridge coordinated Stage 2 on 2026-09-24 under the
user-approved fleet plan. The object and its scope manifest were supplied by ansatz-machine
(`conjecture_machine/data/sealed/TS2_for_quantum/TS2_METRIC.md`). Of that package I have read TS2_METRIC.md,
the two build logs, the Kerr control build log, and the first 1.5 kB of the Kerr t1o2 component file (to see
the format). I have not parsed or evaluated any component.

**Independence (bridge rules, restated so a reader can audit them).**
- I do not open `data/sealed/TS2_PREDICTION_SEALED.md`.
- I do not open anything about TS in the SpaceTime repo.
- I do not search the literature on TS integrability or chaos until this verdict is committed.
- The tool is exactly the Stage-1 code (`qsim/mr_kovacic.py`, `mr_monodromy.py`, `mr_nve.py`, `mr_watchdog.py`,
  state as of 0ae727e). The only new code is a **loader**: srepr components of the lower metric → inverse
  metric dict for `nve_equatorial`. Any change to the tool after a target row has run is an amendment with a
  post-failure label.

## The Hamiltonian and the particular solution

Coordinates `(T, x, y, φ)`. The lower components are `g_TT, g_Tφ, g_φφ, g_xx, g_yy`. Inverse:
`g^TT = g_φφ/Δ`, `g^Tφ = −g_Tφ/Δ`, `g^φφ = g_TT/Δ` with `Δ = g_TT g_φφ − g_Tφ²`, and `g^xx = 1/g_xx`,
`g^yy = 1/g_yy`. Here `p_T = −E` and `p_φ = L` are conserved, and `H = ½ g^{ab} p_a p_b = −μ²/2`. For fixed
`(E, L)` this is a 2-DOF Hamiltonian `H_{E,L}(x, y, p_x, p_y)`.

**Scale.** I set `σ = 1`. Scaling σ rescales every component by σ² once `T` is scaled with it, which is a
reparametrisation, and the sweep is over `(E, L, μ²)` anyway.

**Particular solution Γ: the equatorial plane `y = 0, p_y = 0`.** It is invariant iff every inverse
component is even in y. That holds structurally, because `N(x, −y) = N̄`, `D(x, −y) = D̄`, so
`E(x, −y) = Ē`: f is even, χ is odd, and ω is even. `nve_equatorial` also **checks** it, and raises if it fails.

**The NVE is rational.** Every component is in ℚ(x, y). Along Γ, `ẋ² = g^xx(y=0)·(−μ² − V₀)` with
`V₀ = g^TT E² − 2g^Tφ E L + g^φφ L²` at `y = 0`, so `ẋ² ∈ ℚ(x)` for rational `E, L, μ²`. The NVE in `(δy, δp_y)`
with independent variable x has coefficients `A/ẋ`, `B/ẋ`. After eliminating one variable, only `ẋ²` enters,
so `p, q ∈ ℚ(x)` and the reduced `r ∈ ℚ(x)`, exactly as in Stage 1. The change τ → x is a finite branched
covering (branched where ẋ² = 0), and it preserves G⁰. **μ enters only as μ².** I will report the degree and
pole structure of every r as computed.

**The ring singularity.** On y = 0, `N + D` is real, so `B(x, 0) = (p²x⁴ + 2p x³ − 2p x − 1)²`. Its root in x > 1
is the ring (1.1368… at p = 3/5, 1.0574… at p = 4/5, per the manifest).
- **How Γ keeps clear of it.** H is singular at the ring, so the ring is **not a point of Γ**. Γ is the
  complex phase curve with every point where H is not holomorphic removed, together with equilibria.
- The ring (and every other root of the denominators) appears as a **singular point of the NVE**, that is,
  a puncture. The Morales–Ramis theorem only needs integrals meromorphic in a **neighbourhood of Γ**, and such a
  neighbourhood can be taken to exclude the ring.
- The ring is an algebraic, not rational, point. The tool treats it through its irreducible factor over ℚ,
  as Stage 1 did.
- No numerical integration passes through it. The monodromy route integrates on loops around singular points
  at `ρ = 0.3 ×` the minimal separation.
- If the ring pole has order > 2, the NVE is not Fuchsian there. The monodromy route then returns
  NOT_APPLICABLE, and the row rests on the Kovacic route alone. The report flags such a row as **single-route**.

## Setup correspondence: is the run testing the claim it will be quoted for?

**The claim an OBSTRUCTION would be quoted for.** "The TS δ=2 geodesic flow has no Carter-like fourth integral."

**The condition actually tested.** "At (p, q) = P, σ = 1, and the stated (E, L, μ²), there is no first integral
of `H_{E,L}` that is meromorphic in a neighbourhood of the equatorial phase curve Γ." That condition runs on the
**supplied** rational metric (vacuum checked pointwise, not symbolically).

The two match only up to these gaps, which every report carries:
- **Meromorphic only.** Rational and polynomial-in-momenta integrals are covered; others are not.
- **Neighbourhood of Γ.** This is the complex continuation, so it excludes integrals that exist only on a real
  subdomain outside the ring.
- **Parameter points.** The result holds at the two P values and the tested levels. It is not a statement for
  all q, and special values are not excluded.
- **The supplied metric.** The result is about the metric as supplied, with the Schwartz–Zippel caveat above.

The Kerr controls test the tool's soundness on this pipeline. They do not re-establish Kerr's integrability,
which is known (Carter 1968).

## Rows (registered; nothing else is run on the target)

The target is TS δ=2 at `P1 = (p, q) = (3/5, 4/5)` (file t1o2) and `P2 = (4/5, 3/5)` (file t1o3), with σ = 1.

| row | (E, L, μ²) | role |
|---|---|---|
| T1-P1, T1-P2 | (1, 0, 4) | primary: the Stage-1 A values. At q = 0 this row *is* Stage-1 A. |
| T2-P1, T2-P2 | (1, 0, 9) | primary |
| T3-P1, T3-P2 | (1, 1, 4) | secondary (L ≠ 0 couples the rotation). Run only after all primary rows and controls. |

**In-stage controls, all through the same loader, same NVE code, same tool.** They run **before** any target row.
- **C1 (obstruction side).** q = 0, which is ZV δ = 2. I build it from the manifest's formulas at q = 0, p = 1
  (`f = ((x−1)/(x+1))²`, ω = 0, `e^{2γ} = (x²−1)⁴/(x²−y²)⁴`), written as *lower* components and passed through
  the loader, at `(1, 0, 4)`. Must give `OBSTRUCTION`, **and** its r must equal Stage-1 A's r (μ = 2) as an
  exact identity. That tests the loader and inversion against a known answer.
- **C2 (identity with the Stage-1 Kerr).** Ansatz's Kerr-WP at t1o3 (p = 4/5, so a/m = 3/5) with σ = 4/5, which
  gives m = σ/p = 1 and a = 3/5, i.e. the Stage-1 B metric. The BL radius is `r = σx + m = (4/5)x + 1` and
  `u = y`, so the reduced forms must satisfy `R_WP(x) = σ² R_BL(σx + 1)` **exactly**.
  - For B1 `(3, 0, 118)` it must hold with the same L.
  - For B2 `(1, 2, 125/63)` it must hold with L = 2 or with L = −2 (φ orientation). I record which.
  - Both rows must give `NO_OBSTRUCTION`.
- **C3 (Kerr at the target's own values).** Kerr-WP at t1o2 and at t1o3, σ = 1, at `(1, 0, 4)` and `(1, 0, 9)`
  (and `(1, 1, 4)` before T3 runs). Must give `NO_OBSTRUCTION`, because Kerr has the Carter integral, which is
  rational in coordinates and polynomial in momenta.

**Trust order, applied mechanically.**
- The target counts only if C1, C2 and C3 all pass.
- An `OBSTRUCTION` on a target row at a given P counts only if C3 passed at the same P and the same (E, L, μ²).
- A control that is INCONCLUSIVE or fails means **Stage 2 not passed**, and no target verdict is reported as a verdict.

**Per-row acceptance (the Stage-1 rule).** Both NVE forms (ξ₂ = δp_y, ξ₁ = δy) must give the same verdict, and
the monodromy route, where Fuchsian, must agree. Any disagreement is a **FAIL** of the row, not a verdict.

**Resources.**
- Each row runs as its own guarded child under `mr_watchdog.run_guarded`, with `mem_limit_mb = 1024`,
  `time_limit_s = 1800`, and the box guards (swap free ≥ 512 MB, disk free ≥ 5 GB).
- Rows run strictly sequentially, never in parallel.
- A killed row is `INCONCLUSIVE (resource limit)`.
- Once ansatz signals its long job has started, nothing more runs until it ends.

## Verdict wording (fixed now)

Stated per parameter point P and per row. **Never pooled into "TS is chaotic".**

- **OBSTRUCTION at P.** For TS δ=2 at P, the reduced geodesic flow `H_{E,L}` at the stated `(E, L)` admits **no
  first integral that is meromorphic in a neighbourhood of Γ and functionally independent of H**. Hence the
  geodesic flow is **not meromorphically Liouville-integrable** (in the Morales–Ramis sense) for that family.
  In particular there is no Carter-type fourth integral that is rational in the coordinates and meromorphic in
  the momenta, unless it degenerates on the tested levels.
  - It says **nothing** about integrals defined only on a real subdomain (for instance only outside the ring)
    that do not continue analytically.
  - It says nothing about how much chaos there is, KAM tori, or observable consequences.
- **NO_OBSTRUCTION at every row.** *Inconclusive*: the first-order necessary condition is met along this Γ.
  **It is not evidence of integrability**, and it is never reported as "integrable". Higher-order variational
  equations are a separate, unregistered step.
- **INCONCLUSIVE.** Reported as such, with the reason: the resource limit, a Kovacic step it could not decide,
  or a route disagreement.
- **P1 and P2 disagree.** Both are reported, not reconciled. Special parameter values can be exceptional.

## Named ways this fails

1. The loader inverts wrongly, or the conventions differ from the manifest. This is caught by C1 and C2
   (the exact identities).
2. The tool calls Kerr obstructed. This is caught by C2 and C3, and it voids every target OBSTRUCTION.
3. Cost: the TS NVE has high degree with algebraic poles, and the Kovacic case searches blow up. The result is
   an honest INCONCLUSIVE, not a verdict.
4. The metric is not exactly vacuum. The manifest's vacuum test is Schwartz–Zippel at 4 points, not a symbolic
   proof. A verdict is a statement about **the supplied metric**, and its physical meaning inherits that caveat.
5. y = 0 is not invariant. The loader raises and nothing is run.

## Environment

- Python/SymPy as in Stage 1, on the same machine, which is shared.
- Output files: `qsim/mr_ts2_*.json`, `qsim/mr_ts2_*.log`, and `qsim/mr_ts2_result.txt`.
- The report goes to the bridge.
