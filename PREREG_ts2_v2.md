# Pre-registration — Tomimatsu–Sato δ = 2, re-certified by iahub v2 (certified monodromy, second route)

**Committed before any code or computation for this stage.** The bridge approved it on 2026-10-03 (review point 4):
"re-certify TS δ=2 with v2 … TS's monodromy route was 'uncorroborated' (no clean base point) … run it as a separate
registration", to run **after** the MN equatorial v2 target. Ladder: `PREREG_iahub_v2.md`, complete
(VG0, VCTRL, VREPRO, V-provenance, V-Lean).

**What already stands (unchanged by this stage).** TS δ=2 has an OBSTRUCTION from the root-free Kovacic route 2b′:
post-failure, both forms, all 6 rows (ce2cab8). The ξ₁ form was independently reproduced by the bridge (V8′).
The monodromy corroboration was **uncorroborated**: v1's base-point search found no clean star.

This stage adds an **independent certified-monodromy route**: a different method (monodromy instead of
Kovacic), a different integrator (v2), and a v1 replay.

## What runs

**Rows.** As in Stage 2: TS δ=2 at P1 = (3/5, 4/5) and P2 = (4/5, 3/5), σ = 1, on the equatorial solution, at
(E, L, μ²) = (1, 0, 4), (1, 0, 9) and (1, 1, 4). That is 6 rows.

**Equation.** The TS lower components (ansatz's package, rational in x and y) go through the **same** equatorial
pipeline as MN, Kerr and ZV (`mr_mn_equatorial`: y = 0 data, chain rule, t-uniformisation x = (t + 1/t)/2,
exact ℚ(t) field), as the non-reduced ξ₁ system. There are no exponentials, so there are no `bad` points.

- **Pre-run gate.** Before any search, the equatorial y = 0 invariance check must pass exactly. TS components
  must satisfy ∂_y g_ab = 0 at y = 0, as Stage 2 found.
- **Equation-provenance cross-check.** At 3 dyadic t > 1 points per row, the v2 ξ₁ system coefficients must match
  the **Stage-2 loader's** independent symbolic NVE (`mr_ts2.load_wp` + `mr_nve`-style derivation in x), mapped
  to t, to a relative difference below 1e−25. If they disagree, the stage stops.

**Search and rule.** The frozen v2 driver: nearest-first, incremental, first certified pair. The scale-free GL(2)
certificate (Lean `L6_gl2`). A certificate counts only after the **v1 replay** satisfies the SL(2) certificate
on the reduced ξ₁ form.

**Resources.** One guarded child per row: 2 GB, 6 h, detached. Committed and pushed per row.

## Verdict wording

For each row:
- **CORROBORATED (certified monodromy, v2 + v1 replay):** the TS δ=2 OBSTRUCTION at that row, from 2b′, is
  independently confirmed by certified monodromy (Ziglin form). G⁰ is non-abelian by `L6_gl2` and the cited
  finite-index fact.
- **No certificate:** "monodromy corroboration still absent at that row". That does **not** weaken or contradict
  the committed 2b′ OBSTRUCTION, which rests on its own proof.
- **A v1 replay failure:** reported as such, not as corroboration.

A certificate cannot "contradict" 2b′. Both say obstruction, and monodromy can only add evidence. A **control**
misbehaving would stop the stage. The controls are the already-passed VCTRL rows; ZV and Kerr are not re-run
here.

## Setup correspondence

The same claim and the same gaps as Stage 2 (`PREREG_ts2_morales_ramis.md` § Setup correspondence):
- meromorphic integrals only;
- the complex neighbourhood of Γ;
- the tested parameters;
- the supplied metric (vacuum checked by Schwartz–Zippel only).

This stage changes **how** non-abelian G⁰ is shown, not **what** is claimed.

## Pre-run gates (2026-10-04): **PASS**

- **y = 0 invariance:** exact at P1 and P2.
- **Provenance:** the reduced ξ₁ form from the shared ℚ(t) pipeline matches the Stage-2 loader's independent
  derivation (`mr_ts2.load_wp` + `mr_nve`, in x, mapped to t) to a relative difference of **≤ 2.8e−55** on all
  6 rows.

`qsim/mr_v2_ts2_gates.{json,log}`. The search runs after the MN equatorial v2 target, as registered.

**Additional provenance check vs the bridge's INDEPENDENT V8 derivation (2026-10-04): PASS.** TheBridge ed433e7
(`v8_ts_provenance.json`) gives p_x, q_x, A, B and X of the non-reduced ξ₁ equation, for TS P1 and P2 at all 3
levels, at x = 5/4, 5/3, 2 and 13/4.
- Maximum relative difference against the v2 pipeline: **3.2e−50**, the full precision of the reference
  (`qsim/mr_v2_ts2_provenance.{py,json,log}`).
- The bridge also re-derived f and e^{2γ} from the δ=2 Ernst potential, and its own twist potential χ, with its own
  code. It confirmed ansatz's components (g_TT = −f, g_xx, g_yy, and ω satisfying both twist equations) exactly at
  3 random rational points per parameter point.
- So this check covers the **metric** as well as the equation.

## PRE-RUN AMENDMENT (2026-10-04), bridge-approved, committed before the TS search launches: the A6 search policy

The TS search uses the A6 locator and skip-not-abort, as defined in `PREREG_mn_equatorial_v2.md` § Amendment A6:
- the complete float locator (finer grid; Newton on the denominators of p and q; conjugate closure; t ↦ 1/t images
  only as Newton-verified candidates);
- skip, rather than abort on, an uncertifiable loop.

**Motivation.** For TS this is purely a **completeness and robustness gain on the search side**. The TS δ=2 NVE
coefficients are rational in x (and t), so there are **no essential singularities** and the MN failure mechanism
(growth near t = ±1) **does not apply**. The change is search-only and cannot create a false certificate: skipping
only removes candidates, and every certificate still needs the v1 replay.
