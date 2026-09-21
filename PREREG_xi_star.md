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
