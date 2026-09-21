# Pre-registration — is `(S*, t*)` a *physical* characterisation or a *protocol convention*?

Committed before the code exists. Tests the scheme in `DESIGN_two_condition_matching.md`.

## Choosing the third knob, and rejecting the obvious one

The design doc proposed a second coupling site as the free direction. **Rejected on
inspection.** Moving coupling strength from site `i₁` to site `i₂` changes *where the
record is written* — a change of model, not of route. It would trivially show
"structure moves" and prove nothing about the scheme. *(Also: two sites symmetric
about the chain centre would make the test degenerate under reflection — the
`A_x ≡ 0` parity trap from the LRL work, in a new costume.)*

**The legitimate third knob is the TEMPORAL SHAPE of `λ` at the same site.** Same
model, same geometry, same duration, same final decoherence — only the route differs.

Implemented as two-step piecewise-constant coupling: `λ = s·c_a` on `[0, t*/2]`,
`λ = s·c_b` on `[t*/2, t*]`. The shape `(c_a, c_b)` is the free direction; the scale
`s` is solved to hit `S*`. Both branches stay quadratic, so this is still exact.

## The question, stated precisely

The scheme matches `(S*, t*)`. But every route in it also has **constant `λ`** — an
assumption never written down as a condition.

- If shape does **not** matter: `(S*, t*)` is a **physical** characterisation. Scheme
  licensed.
- If shape **does** matter: `(S*, t*)` is a **protocol convention** that works only
  because "constant coupling" is silently doing work as a third condition. The scheme
  is then usable but must declare that third condition — and the count goes from two
  to three.

## Prediction

**P-SUFF: shape WILL matter; I expect falsification.** Front-loaded coupling writes
the record early and leaves time for it to spread; back-loaded writes it late with no
time. Recorded as an expectation, not a hope, because a test whose author expects
confirmation reads differently from one who expects the reverse.

*Falsified if* the record structure varies with shape beyond the noise floor, with a
consistent ordering in the front/back-loading parameter.

## Controls

- **C-REPRODUCE (known answer).** Two-step code with `c_a = c_b` must reproduce the
  single-step constant-`λ` result to machine precision. Without this, any difference
  between shapes could be two-step machinery rather than physics.
- **C-TARGET.** Every shape must land within `0.1%` of `S*`.
- **C-EXACT.** The decisive comparison uses `I(S : i₀)` — **one fragment, no
  sampling** — so there is no noise floor to argue about, as in the last test.

## Named failure modes

1. **The scale root is non-unique.** As before, capacity is non-monotonic. Convention
   fixed in advance: **smallest `s`**.
2. **Shape range too narrow to resolve.** If `c_a/c_b ∈ [0.25, 4]` moves nothing, the
   answer is *"not resolved over this range"*, not *"shape does not matter"*.
3. **Trotter/stepping error masquerading as physics.** Avoided by construction: the
   coupling is *exactly* piecewise-constant and each segment is evolved by exact
   diagonalisation, so there is no time-discretisation error at all. Stated because
   "it's a small numerical error" is how this failure usually survives.

## Setup correspondence

The claim is about whether `(S*, t*)` physically characterises "how much recorded,
how far spread". The condition is: `L=10` TFI chain at `g=1`, one coupling site,
two-step piecewise-constant `λ`, `S*` measured as `S(ρ_S)`, structure read from
`I(S:i₀)`. A null over two-step shapes does **not** establish sufficiency over
arbitrary `λ(t)` — it establishes it over the two-step family, and must say so.


---

# OUTCOME — 2026-09-21. **P-SUFF FALSIFIED.**

## The control first, because it is what makes the result readable

**C-REPRODUCE passes at `5.55e-16`.** Two-step machinery with equal steps reproduces
the single-step result to machine precision (`I(S:i₀) = 0.1333005352` both ways). So
every difference below is physics, not stepping machinery. **C-TARGET: 0.000%** — all
five shapes hit `S(ρ_S) = 0.150000` exactly.

## The result

`g=1`, `L=10`, `S* = 0.150000`, `t* = 0.35`, one coupling site, varying only the
*temporal shape* of `λ`:

| `c_a : c_b` | `λ_a` | `λ_b` | `S(ρ_S)` | `I(S:i₀)/S` |
|---|---|---|---|---|
| 4 : 1 (front-loaded) | 1.0181 | 0.2545 | 0.150000 | **0.8304** |
| 2 : 1 | 0.8677 | 0.4338 | 0.150000 | 0.8553 |
| 1 : 1 (constant) | 0.6573 | 0.6573 | 0.150000 | 0.8887 |
| 1 : 2 | 0.4335 | 0.8670 | 0.150000 | 0.9209 |
| 1 : 4 (back-loaded) | 0.2543 | 1.0172 | 0.150000 | **0.9431** |

**12.70% relative spread, monotone in the loading parameter**, with `S(ρ_S)` identical
to six decimals and `t*` identical by construction. Single fragment — no sampling, no
noise floor.

Direction is as predicted: **write early and the record spreads; write late and it
does not.**

## What it means

**`(S*, t*)` is a PROTOCOL CONVENTION, not a physical characterisation.** It works
only because "constant `λ`" is silently acting as a *third* condition that was never
written down. The scheme remains usable — but it must declare three conditions, not
two, and the third is an arbitrary choice of route rather than a physical quantity.

The count has gone **1 → 2 → 3** in two days:
- match the coupling → confounded (44× capacity gap)
- match `S(ρ_S)` → insufficient (record structure runs 0.766–0.998)
- match `(S, t)` → insufficient (12.70% spread over shape)

## The conjecture this suggests, stated as a conjecture

Each condition pins **one scalar**. The record is a **function** — `I(S : ·)` over all
fragments — with far more degrees of freedom than any finite list of scalars can fix.
So:

> **No finite set of scalar matching conditions makes two environments comparable.**
> Every such scheme is a convention that fixes the remaining freedom by fiat.

**This is NOT established here.** What is established is that it holds for the first
three. The test that would settle it: three-step coupling gives three knobs plus `t`;
impose `S*`, `t*`, and a *third* scalar (e.g. `∫λ dt`), leaving one free direction;
sweep it. If structure still moves at every order, the conjecture stands. If it stops
moving at some order, that order is the physical answer and is worth knowing.

**Until that runs, the reportable claim is the narrow one:** matching on decoherence
and duration is not sufficient, and any comparison of how different environments
record must declare its route convention as an assumption.


---

# ORDER-3 OUTCOME — 2026-09-21. **Structure still moves.**

Registered in `fea2840` before running, with both readings stated in advance.

## Controls

| control | value | |
|---|---|---|
| C-REPRODUCE — three equal steps vs single step | `2.11e-15` | PASS |
| C-TARGET — `|S − S*|/S*` | `0.0000%` | PASS |
| C-SUM — `|Σλ − A|` | `0.00e+00` (by construction) | PASS |
| **±θ degeneracy hazard** | `0.056545` | **not degenerate — the sweep is live** |

That last row matters: had `+θ` and `−θ` given identical structure, the sweep would
have been testing a symmetry rather than the physics — the `A_x ≡ 0` parity trap
again. It does not.

## The result

`S*`, `t*` **and** `∫λ dt` all held fixed; only the remaining free direction swept:

| `θ` | `λ_a` | `λ_b` | `λ_c` | `Σλ` | `S(ρ_S)` | `I(S:i₀)/S` |
|---|---|---|---|---|---|---|
| −0.30 | 0.4954 | 0.5565 | 0.9200 | 1.9719 | 0.150000 | **0.9157** |
| 0.00 | 0.6575 | 0.6569 | 0.6575 | 1.9719 | 0.150000 | 0.8887 |
| +0.30 | 0.9129 | 0.5675 | 0.4916 | 1.9719 | 0.150000 | **0.8592** |

**6.37% relative spread, monotone.** Three scalars fixed and the record structure is
still not determined. **The conjecture stands at order 3.**

## The comparison I must NOT make

It is tempting to read `12.70% → 6.37%` as *the residual halving with each added
condition*, which would suggest convergence rather than the conjecture. **That
comparison is invalid and I am recording why rather than making it quietly:**

- the order-2 sweep ranged `c_a/c_b` over `4 → 0.25`, a **16× range**;
- the order-3 sweep ranged `θ` over `−0.3 → +0.3` only, because **`θ = ±0.6` has no
  root** — no `q` reaches `S*` there.

Different sweep extents. The two spreads are **not comparable**, and any claim that
the residual is shrinking would be exactly the "measured at a different condition
than the claim" error this repo has logged eight times. *Whether the residual
converges with order is unresolved.*

## Limitation, stated plainly

Only **three θ points resolved**. Hazard 2 of this registration — "shape range too
narrow" — **fired**. The effect is monotone and far above the exact-arithmetic noise
floor, and the ±θ check rules out degeneracy, so *structure moves* is solid. But
three points cannot characterise a trend.

## What would settle convergence

Sweep ranges matched by a physical measure rather than by parameter name — e.g. equal
variance of `λ(t)` about its mean, or equal `L²` distance in coupling space — at
orders 2, 3 and 4. Only then does "the residual shrinks with order" become a
statement about physics rather than about how wide each parameter happened to be
swept.

**Reportable now:** three scalar conditions do not fix the record. Whether any finite
number does remains open, and the order-by-order trend is **not** measured.


---

# MATCHED-RANGE SWEEP, orders 2–4 — 2026-09-21

Response measured **per unit normalised arc length in coupling space**, so the sweeps
are matched physically rather than by parameter name. Each order imposes one more
scalar condition and keeps exactly **one** free direction.

| order | conditions fixed | `max|S−S*|` | mean `|d(I/S)/dD|` | sd | `span/arc` | arc |
|---|---|---|---|---|---|---|
| 2 | `S*` | 3.4e-06 | **0.0968** | 0.0035 | 0.0968 | 0.9899 |
| 3 | `S*`, `Σλ` | 5.0e-08 | **0.0996** | 0.0080 | 0.0989 | 0.5717 |
| 4 | `S*`, `Σλ`, `Σλ²` | 1.0e-08 | **0.0454** | 0.0233 | 0.0325 | 0.2695 |

## The clean result: the second condition bought nothing

**Orders 2 and 3 agree — `0.0968` vs `0.0996`**, on two independent measures
(mean local slope, and span/arc), both monotone sweeps. Adding `Σλ` as a second
condition **did not reduce the response per unit physical excursion at all.** That is
the matched comparison the order-3 run could not make, and it is now made.

## The order-4 verdict my own script printed, and why I am not keeping it

The script announced *"RESPONSE SHRINKS — conjecture WEAKENED"*. **I am overriding
it.** Three reasons, all visible in the table:

1. **The threshold was a hair.** The rule was `slope₄ < 0.5 × slope₂`; the measured
   ratio is **0.4690** against 0.5000 — a margin of 0.031, with order-4 scatter at
   **51% relative**. A verdict that flips on the third decimal of a ratio that noisy
   is not a verdict.
2. **The order-4 sweep TURNS.** Values run `0.8763, 0.8733, 0.8720, 0.8737, 0.8808` —
   down then up, through a stationary point. Orders 2 and 3 are monotone. A sweep
   crossing an extremum has a small mean slope for a geometric reason, not a physical
   one, and `span/arc` (0.0325) understates it further.
3. **The excursions are not the same size.** Order-4 arc is `0.2695` against order-2's
   `0.9899` — a **3.7× smaller** region explored. Normalising by arc length corrects
   this only if the response is locally linear, which the turning point shows it is
   not at order 4.

**So: the order-4 number is not comparable to orders 2 and 3**, and the hypothesis
that adding conditions reduces the residual is **neither supported nor refuted** by it.

## Where this leaves the conjecture

- **Supported at order 3**: one extra scalar condition, zero reduction in response.
- **Untested at order 4**: the run that was supposed to settle it produced a number
  its own controls disqualify.

**What order 4 needs to be readable:** an excursion matched in *size* to orders 2–3
(not just normalised after the fact), enough sweep points to resolve the turning point
rather than straddle it, and several `ψ` directions on the constraint sphere rather
than one — since a single direction through a stationary point is the worst possible
sample of a 1-parameter family.

I am recording the disqualification rather than the verdict, because the verdict was
generated by a threshold I wrote before seeing the scatter, and the scatter is what
makes it meaningless.
