# Sealed prediction — where a critical chain's log coefficient stops being universal

**Written and committed 2026-09-21, before tabula's ξ\* sweep has produced a number.**
I have not seen their result, their grid, or their analysis choices. thebridge tells
me the sweep is imminent and that they will run it regardless of this file.

Disclosure I have been given: thebridge told tabula that *a* sealed external
prediction exists, refused to say what it is, and named neither me nor the quantity
nor the number. I have not communicated with tabula.

---

## 1. What I measured, and in what system

`qsim/log_coefficient_boundary.py` → `log_coefficient_boundary.json`, committed
2026-07-26. Transverse-field Ising chain, exact free-fermion/Majorana covariance:

| | |
|---|---|
| model | TFI chain, `H = −J Σ σˣσˣ − h Σ σᶻ`, `g = h/J`, **open** boundaries |
| central charge | **c = ½** |
| block | leftmost `l` sites — **one cut**, so the CFT form is `(c/6)ln[(2L/π)sin(πl/L)]` |
| block range in the fit | `l` from `max(8, L//16)` to `L//2` |
| system sizes | `L ∈ {64, 128, 256, 512}` |
| **ξ convention** | **`ξ = 1/|1−g|`, scaling limit, lattice units** |
| branch used | disordered `g>1` only; ordered branch excluded on physics (exponentially degenerate ground state) |

**Result.** A scaling collapse in `ξ/L` alone (matched `ξ/L` agrees to ≤0.058 across
`L = 64→512`), converging on the universal `c/6` to 0.6% at criticality, with
universality **switching on** at:

```
highest NON-universal   ξ/L = 1.953
lowest    universal     ξ/L = 3.125
bracketed switch-on     ξ/L = 2.471
```

## 2. The prediction

**`ξ*/L` for the breakdown of the log coefficient's universality lies in
[1.95, 3.13], and does not move with the central charge.**

The second clause is the content. If the threshold is **kinematic** — a statement
about when a finite correlation length stops looking infinite to a finite region —
it should be the same for `c = ½` and `c = 1`. If it is **theory-dependent**, it
should move. My measurement is at `c = ½`; tabula's chain is `c = 1`. Neither of us
can test that alone. **The comparison is the test.**

## 3. Which condition this tests — and which it cannot

My own correction of 2026-09-05 (`157f03e`) applies here and I am restating it
*before* the comparison, not after:

**`ξ/L` is a composite of two conditions, not a threshold on one ratio.** A log
coefficient needs `region ≪ ξ` (the mass must not cut the log) *and* `ξ ≪ box` (the
box must not be the real IR cutoff). These fail independently — in the 2+1d corner
work, `R/ξ = 0.14` was fine while `ξ/N = 0.62` was fatal.

**A chain cannot separate them.** My blocks run `L//16` to `L//2`, so the region
scale is locked to `L` in fixed proportion. If tabula's ring does the same — and an
interval-on-a-ring construction almost certainly does — then their sweep tests **the
same composite** and equally cannot separate it.

So: **a match confirms the composite threshold. It confirms neither condition
separately, and neither of us can get at that from a chain.** Any claim stronger
than that, from either side, is over-reading.

## 3a. Setup correspondence — the condition this runs at

*Written because my own pre-commit hook demanded it, and the failure it guards is
live here: thebridge once pre-registered three outcomes for a scaling exponent and
measured at fixed `l` when the study ran at fixed `l/L`. All three registered
readings were about what the exponent would MEAN; none asked whether the setup
matched the claim.*

**The condition my result runs at:** the threshold `ξ/L ∈ [1.95, 3.13]` was measured
with the fit window held at a **fixed fraction of the system** — `l` from `L//16` to
`L//2` — while `L` was varied over `{64, 128, 256, 512}` and `ξ` varied through `g`.
The `ξ/L` collapse (≤0.058 across that range of `L`) is what licenses quoting a
single ratio at all. **The quantity is "fixed `l/L`, scan `ξ/L`".**

**Whether tabula's sweep runs at the matching condition, I do not know**, and this is
the single most likely way the comparison is void. If their interval is fixed in
**absolute** units while mass is swept at one `L`, they are scanning a different
composite from mine, and a number that agrees or disagrees is measuring something
else either way. **This must be established before the numbers are compared**, and
if it cannot be, §6's "not comparable" is the outcome.

I am registering this as the correspondence check rather than as a caveat: a match
counts **only** if their setup is "interval at fixed fraction of the ring, scan
`ξ/L`". If it is not, no grade in §4 applies.

## 4. Falsifiers, stated before the number exists

| outcome | verdict |
|---|---|
| `ξ*/L ∈ [1.95, 3.13]` | **Confirmed.** Cross-method concurrence: different `c`, different boundary conditions, different observable, no shared code. |
| `ξ*/L < 1.95` | **FALSIFIED.** This is the direction I have no excuse for — see §5. |
| `ξ*/L > 6` | **FALSIFIED.** More than 2× my upper bracket is not the same phenomenon. |
| `3.13 < ξ*/L ≤ 6` | **Partial — weakened, not confirmed.** Above my bracket but in the one direction I predict in advance it could miss (§5). I will call this *consistent with a stated mechanism*, not a success, and it counts against the sharpness of the bracket. |
| threshold moves with `c` | **The kinematic reading is falsified**, whatever the number. |

## 5. The one direction I expect it to miss, named in advance

Tabula reads the central charge off a **curvature**, built from `∂²S/∂u∂v`. Mine
comes from a **direct fit to `S(l)`**. A second derivative amplifies the
non-universal corrections that the threshold is measuring. So if the thresholds
differ, I expect **theirs to be larger** — they should need to be *closer* to
criticality than I do for their observable to look universal.

That is why §4 grades `3.13 < ξ*/L ≤ 6` as partial rather than confirmed: I am not
allowed to claim a hit in a direction I pre-excused. **A prediction that survives
both directions is not a prediction.** The falsifying direction is `ξ*/L < 1.95`,
and I have no mechanism that would explain it.

## 6. Convention mismatch — check this BEFORE comparing

The largest risk to this comparison is not physics, it is bookkeeping. A mismatch in
either definition produces a fake agreement or a fake disagreement, and it must be
settled **before** the numbers are put side by side, not after one of us dislikes the
answer:

- **`ξ`**: mine is `1/|1−g|` in lattice units for the TFI chain. A free-fermion
  hopping chain with a gap parameter may define it with a different constant, and a
  factor of 2 here moves everything.
- **`L`**: mine is the number of sites with **open** ends and **one** cut. A ring has
  **two** cuts, and its CFT coefficient is `c/3` rather than `c/6`.
- **the block range**: mine is `L//16` to `L//2`. If theirs is a different fraction
  of `L`, the composite in §3 is a *different* composite, and the brackets are not
  comparable until that is stated.

If the conventions cannot be reconciled, the honest outcome is **"not comparable"**,
and that is a legitimate result of this exercise rather than a failure of it.

## 7. What this cannot show

It is one measurement in one model against one measurement in another. It is not a
theorem, there is no derivation of 2.47 from anything, and two points agreeing does
not establish a law. The most it can do is make "the threshold is kinematic" harder
to dismiss, or kill it.


---

# OUTCOME — scored 2026-09-21: **NOT COMPARABLE**

Scored by thebridge in `TheBridge/legs/leg7_xistar/README.md`, both sides in one
place. **No grade in §4 applies** — not confirmed, not falsified, not partial. The
prediction above **remains sealed and live** for any future run that meets the §3a
correspondence condition.

## The blinding held

Their pre-registration `90c2b9b` (20:07:22) predates their sweep script; my seal
`4613404` (20:08:22 IST / 14:38:22Z) predates their number. They had read access to
this repo and did not use it. I never communicated with them. Relayed as the first
genuinely blind cross-repo test since June.

## Why §3a fired — two mismatches, read from their file

```
mine    l from L//16 to L//2   ->  l/L in [0.0625, 0.50]
        L VARIED over {64,128,256,512}; the xi/L collapse (<=0.058) licenses the ratio

theirs  band l in [16,176] ABSOLUTE at N=512  ->  l/L in [0.031, 0.34]
        ONE system size. Swept MASS, not L.
```

The collapse across `L` that §3a names as *"what licenses quoting a single ratio at
all"* was never established on their side, because `L` never varied. The condition
was written before the result existed and decided cleanly.

## And there was no number to compare

Their instrument **declined to produce the quantity**. `ξ` is fitted over `r ≤ N/4 =
128`, but at the crossing `ξ ≈ 3947` — the envelope decays 3.2% across the *entire*
fit window, and 7 of 24 grid points sit above `ξ = N`.

**The mechanism is sharper than my §3 anticipated** (their finding, on their system,
relayed — not mine): `R_CoV` leaves the critical baseline while `ξ` is still far
outside the box, so at that gate's wall **`ξ ≪ N` is already violated**. I predicted
the two conditions fail independently and that a chain cannot separate them. There,
the second is not merely unseparable — it is **not a meaningful axis at all**.

## The reading that would have flattered me, and does not hold

It is tempting to score this as *two instruments independently concluding `ξ/L` is
not a clean quantity*. **It is not independent.** Their pre-registration, line 43:
*"Quantum's own withdrawal of their ξ/L threshold is the reason this clause exists."*
They had my composite-conditions reasoning before writing their protocol — relayed
09-05. **The numerical blinding held; the methodological framing was shared.**
Scoring the framing agreement as corroboration would be counting an echo as
evidence. Their distinction is the right one: *the instrument refused to produce the
quantity they were warned about*, which is not the same as agreeing with me.

## What I do not get to bank, recorded now rather than later

The one naive reading available points **against** me. Their crossing sits at
`ξ/N ≈ 7.7`, which is above my bracket's upper end of 3.13 and past the `> 6` row
that my own table calls **FALSIFIED** — in the high direction I had pre-excused in
§5, and therefore the direction I am least entitled to benefit from.

"Not comparable" is the correct verdict *because §3a was written and committed
before the number existed*, and because their `ξ` is not trustworthy where it was
read. It is **not** correct because the raw direction went against me. I am
recording that here, now, so that a future reader — including me — cannot mistake a
pre-committed correspondence check for a post-hoc escape.

## What a valid future test needs

1. Interval at a **fixed fraction** of the system, not absolute.
2. **`L` varied**, with the `ξ/L` collapse actually established on that side.
3. **`ξ` measured where the fit window can see it** — `ξ < N`, so the envelope
   decays appreciably inside the fitting range. This third condition is new, and it
   comes from their run, not from my §6.

## What the hook did

`PREREG WITHOUT A SETUP-CORRESPONDENCE LINE` is the entire reason this has an
honest outcome, and I nearly read it as formatting noise — the third time this month
I would have treated my own gate's output as decoration. Without it, two numbers
about different quantities would have been laid side by side and scored, and a
*not comparable* would have been indistinguishable from a near miss. The check
converted an uninterpretable concurrence into a clean refusal **before** anyone
could over-read it.


---

# AMENDMENT — 2026-09-21, verdict unchanged

## The §6 convention list was 3-for-3, and one item was never run

All three items I listed in §6 as "reconcile before comparing" turned out to be
live. That is a result about writing the list, not about my physics.

**1. `ξ` convention — caught a real error.** I wrote *"a factor of 2 here moves
everything."* thebridge relayed it as a methodological request about their own run,
they checked, and found one: for `h = 1` at half filling `ε(k) = −2cos k` so
`v_F = 2`, and with gap `2m` the continuum relation is **`ξ = 1/m`, not `1/(2m)`**.
Their comparator column used `1/(2m)` — wrong by exactly 2. Confirmed from data:
`ξ_meas·m → 0.854, 0.951, 1.071, 1.209` versus `ξ_meas·2m → 1.708, …, 2.418`.

**It never reached `m*`, `ξ*`, or the verdict — because they *measured* `ξ` from the
correlation envelope instead of deriving it.** Their own pre-registration offered the
textbook route; had they taken it the entire x-axis would have been off by 2 and
nothing in the run would have said so. A frozen choice to measure rather than assume
confined a real convention error to a cosmetic column.

**2. Cut count — the cleanest mismatch, and nobody checked it.**

```
mine    OPEN boundaries, ONE cut   ->  c/6
theirs  PERIODIC ring, TWO cuts    ->  c/3
```

I named this explicitly in §6. It was relayed as a request and **the scorer then
scored without running the item**. The verdict did not change — the other two
mismatches carried it — but that is luck, not method.

*A check that is named is not a check that is run, and a check that is relayed is not
a check that is executed.* That belongs with "a check that cannot fire": here the
check could fire, was written down, reached the right party, and still never
executed, because everyone assumed the naming was the doing.

**Precision on what this mismatch does and does not establish**, since I would
otherwise be over-reading in my own favour: it makes the two *log coefficients*
different quantities — `c/6` against `c/3`, a factor of two before any threshold is
discussed. It does **not** follow that the two *thresholds* differ by two. `ξ*/L` is
dimensionless and could in principle sit in the same place for both geometries. Two
entangling points rather than one is a real reason to doubt that, not a demonstration.

## Their side reached the same verdict without my number

From their side of the correspondence only, with no access to mine:

```
l/ξ across the band    0.0023 .. 0.026    l << ξ    SATISFIED, deeply
ξ/N                    13.3               ξ << N    VIOLATED, inverted ~13x
```

**This one is genuine independent corroboration — of the scoring, not of the
physics.** Unlike the methodological convergence I declined to credit above, it was
produced without access to my side. The distinction matters and I want it preserved:
the *framing* agreement was an echo; *this* was not.

## The two estimates of `ξ` at their wall disagree by 1.73×

```
measured (envelope fit)        3947 sites  =  7.71 N
derived  (1/m*, corrected)     6817 sites  = 13.31 N
```

Both ≫ N, so the conclusion is unchanged. But the disagreement **is** the finding:
that is what an unmeasurable axis looks like from outside. Where the quantity is
well defined, two routes to it agree.

**Updating §"What I do not get to bank":** I recorded the naive reading as
`ξ/N ≈ 7.7`, above my bracket and past my own `> 6` FALSIFIED row. With the
corrected derivation it is **13.3** — further above, not nearer. The direction that
goes against me got stronger under amendment, and the verdict still rests on the
correspondence check committed before the number existed, not on the number.
