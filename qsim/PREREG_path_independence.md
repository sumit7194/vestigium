# Pre-registration — does the environment's record depend only on *how much* decoherence, or on the *route*?

**Committed before the measurement code exists.** Follows the 2026-09-21 sweep, which
found (in a sweep of six vocabularies) no treatment of this question.

## Why it is the load-bearing question

For the **system**, path-independence is a theorem: under Gaussian pure dephasing the
qubit's reduced state depends only on the scalar decoherence function `Γ`. Weak
coupling for a long time and strong coupling briefly are **provably equivalent for
the qubit**.

Nothing says the same of the **environment**. If the record's structure also depends
only on `Γ`, then matching two environments on `S(ρ_S)` is legitimate and every
comparison downstream is licensed. If it does not, then fixed-coupling comparisons
are confounded (already shown: 44× capacity gap) **and** matched-decoherence ones are
ill-posed — which would mean there is currently no sound way to compare how different
environments record, and that is a bigger result than the comparison it was meant to
enable.

## The tension in the design, named before running

`S(ρ_S)` is reached **fast** at large `λ` and **slowly** at small `λ`. But the record
can only spread at the Lieb–Robinson velocity. For the TFI chain the single-particle
dispersion is `ε(k) = 2J√(1+g²−2g cos k)`; at `g=1` this gives `v_max = 2J`, so the
causal radius from the coupling site is `≈ v_max·t`.

**So a fast route physically cannot have spread the record as far as a slow one.**
Path-dependence of the *raw* plot may therefore be true for a trivial reason —
causality — and finding it would not be interesting on its own.

The test is built to separate the two:

- **Raw PIP** — `I(S:F)/S` over uniformly random fragments. Expected to differ.
  Differing here is *not* the finding.
- **Causally-normalised PIP** — fragments drawn **only from inside the causal region**
  of each route, plotted against `f / (sites inside the light cone)`. This asks
  whether the record is *structured* differently, with the trivial size effect divided
  out. **This is the real test.**

The causal radius is **measured**, not taken from the formula: the largest distance
`d` from `i₀` at which a single site carries `I(S:site) > 10⁻⁶`. The formula value is
reported alongside as a cross-check, and a disagreement between them is itself worth
recording.

## Predictions

**P1 (raw).** Routes differ in the raw PIP. *Expected, uninteresting, and stated so
it cannot later be presented as the result.*

**P2 (the test).** Once normalised to the causal region, the routes **agree** — the
record's structure depends only on `Γ`, and the apparent path-dependence is entirely
causality.
*Falsified if* the normalised curves differ by more than the noise floor (below), with
a consistent ordering in `λ`.

**P3 (if P2 fails).** The direction is monotone in `λ`: stronger, briefer coupling
produces a **less** redundant record at equal `S(ρ_S)` and equal causal reach.
*This is the outcome that would matter*, and it is the one I have no mechanism for,
so I am recording it as a guess rather than a prediction.

## Controls

- **C-NOISE (the control the whole test rests on).** The *same* route, rerun with a
  different fragment-sampling seed, must agree with itself. This measures the noise
  floor, and **without it "the curves differ" is uninterpretable.** A route-to-route
  difference counts only if it exceeds `3×` the seed-to-seed spread.
- **C-TARGET.** Every route must land within `1%` of the same `S(ρ_S)`. If the
  matching is sloppy, the comparison is between different decoherence levels and the
  whole test is void.
- **C-λ-ROOT.** Capacity is non-monotonic in `λ` (measured: 0.289, 0.876, 0.994,
  0.849, 0.729 at `g=1` for `λ = 0.6…12`), so the target has multiple roots. **Fixed
  in advance: always the smallest `t` root at a given `λ`.** Recorded because
  choosing the root after seeing the answer would be a free parameter.

## Named ways this fails

1. **The noise floor swamps the signal.** With `L=10` and modest sampling the
   seed-to-seed spread may exceed any route effect. Then the answer is *"cannot
   resolve"*, not *"path-independent"* — and those must not be conflated, because a
   null from insufficient resolution reads identically to a null from physics.
2. **Light-cone measurement is threshold-dependent.** `10⁻⁶` is arbitrary. The causal
   radius is reported at three thresholds; if the conclusion moves with the threshold,
   it is a threshold artefact and is reported as one.
3. **Too few sites inside the cone.** A fast route may have a causal region of 2–3
   sites, leaving no room for a fragment-size sweep. If so the route is **excluded and
   said to be excluded**, not quietly dropped.
4. **`Γ` is not directly available here.** The chain is not a Gaussian boson bath, so
   the theorem's exact hypothesis does not hold; `S(ρ_S)` is used as the proxy for
   "how much decoherence". **The result is therefore about `S(ρ_S)`-matching, not
   about `Γ`-matching**, and any claim must say so.

## Setup correspondence

**The claim is about "the environment's record depends only on how much decoherence
has occurred". The condition is: a finite `L=10` TFI chain at fixed `g`, one system
qubit, dephasing coupling at one site, `S(ρ_S)` as the decoherence measure, fragments
sampled uniformly at random.** These are not the same statement, and the gap is
hazard 4 above. The test runs at a *single* `g` at a time — this is a within-chain
question, not a between-chain one, and no conclusion about comparing *different*
environments follows until the within-chain answer is in.


---

# OUTCOME — 2026-09-21. **P2 FALSIFIED.**

## The decisive number

At **identical** `S(ρ_S) = 0.150000` (six decimals, control C-TARGET passes exactly),
`g = 1`, `L = 10`, varying only the route:

| `λ` | `t` | `v_max·t` | `I(S : i₀)` | `/S` |
|---|---|---|---|---|
| 0.5 | 0.5333 | 1.067 | 0.114899 | **0.7660** |
| 0.8 | 0.2753 | 0.551 | 0.139079 | 0.9272 |
| 1.2 | 0.1760 | 0.352 | 0.145068 | 0.9671 |
| 2.0 | 0.1036 | 0.207 | 0.148090 | 0.9873 |
| 3.0 | 0.0687 | 0.137 | 0.149091 | 0.9939 |
| 5.0 | 0.0411 | 0.082 | 0.149643 | **0.9976** |

`i₀` is the coupling site, reached by every route **by definition**, so there is no
causal-reach escape. This is a **single fragment**: no averaging, no sampling, no
noise floor to argue about. The numbers are exact.

**The system's reduced state is identical across all six rows. The environment's
record is not.** The fraction of the record held by one site runs from 77% to 99.8%.

**So: the system's path-independence theorem does NOT extend to the environment.**
Under Gaussian pure dephasing the qubit's state depends only on the scalar
decoherence function; the environment's record does not. As `λ → ∞`, `t → 0` and the
record has no time to leave the site it was written on — `I(S:i₀)/S → 1`.

## What this costs the programme, which is the point of having run it first

**Matching on `S(ρ_S)` is necessary but NOT sufficient** to compare how two
environments record. The fix I proposed three hours ago for the fixed-coupling
confound is itself insufficient. A sound comparison needs **matched decoherence AND
matched spreading** — two conditions, failing independently.

That is the **seventh** instance of this repo's recurring shape, and the first found
**before** a study was built on the bad assumption rather than after. The check cost
an hour; the study it would have invalidated was a day.

## P1 and P3

**P1 (raw plots differ): confirmed, and uninteresting** — recorded in advance as not
the finding.

**P3 (direction): NOT cleanly answered, and I am not going to force it.** Two
measures point opposite ways. The record *concentrates* at high `λ` (99.8% on one
site), which by the "how many independent copies" reading is **less** redundant. But
the average over *uniformly random* single fragments **rises** with `λ`
(0.0783 → 0.0965), because a concentrated record with a high value beats a thin one
for the mean. `R_δ = L/f_δ` assumes fragments are interchangeable and they are not
here. **A direction claim needs a redundancy measure that survives a spatially
inhomogeneous record, and `R_δ` is not it.**

## Hazards that fired

- **H2 (threshold-dependent light cone): fired.** The measured causal radius was
  `3,3,2,2,2` at `10⁻⁴` but **saturated at 5 — the chain edge — for every route** at
  `10⁻⁶` and `10⁻⁸`. The causal normalisation the design rested on was therefore
  **inert**, and P1/P2 were never separated the way the registration intended. The
  decisive test above replaced it and is stronger, being exact.
- **H3 (too few sites inside the cone): fired.** At `λ = 3`, `v_max·t = 0.14` — under
  one lattice spacing. Strictly, *no* site but `i₀` is inside the hard cone; what is
  measured at distance ≥ 1 is the Lieb–Robinson exponential tail. This is why the
  decisive test uses `i₀` alone.
- **A flaw in my own first analysis, caught before it was reported.** The first pass
  compared a **paired** route spread (same fragments for every route, so sampling
  noise cancels in the difference) against an **unpaired** noise floor (measured
  across different seeds). That inflates the floor and biased toward
  path-independence — it returned "PATH-INDEPENDENT, ratio 0.68". The tell was that
  the ordering was monotone in `λ` in every column, which noise does not do. Redone
  paired, then replaced entirely by the exact single-fragment test.
