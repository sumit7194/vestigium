# Pre-registration: comparing the s=6 zero-mode residual across two studies

**Written before the bridge's four-regulator number exists.** They have sent a
preview from two of four regulators; I am deliberately not fitting to it, and
this file is committed so the comparison criteria cannot be chosen after the
answer.

## Setup correspondence (the check bridge's own pre-registration lacked)

Both studies delete the k=0 mode per regulator and take the **non-common
residual** — the spread of the per-regulator shifts — as a fraction of the
**regulator signal**, the max−min of |B| across regulators. Both hold `l/L`
fixed at the grid their published result uses. **These are the same quantity in
the same condition; they are not the same geometry, lattice, or definition of
B, and that is the whole reason the comparison is worth anything.**

## What I have

| s | signal | non-common | fraction |
|---|---|---|---|
| 1 | 0.000789 | 0.0001705 | 21.6 % |
| 2 | 0.000115 | 0.0000477 | 41.5 % |
| 3 | 0.000055 | 0.0000151 | 27.5 % |

Non-monotone, no trend, measured at s=1,2,3. **My s=6 value does not exist yet**
— my replication is queued behind their run.

## Registered outcomes, and they are NOT branches of one premise

1. **Their fraction lands in 20–45 %.** Consistent with mine. Says the residual
   is a property of the *method* — deleting a common mode from a
   regulator-difference — rather than of either lattice. Would make it a
   systematic anyone doing this must carry.
2. **Their fraction is much smaller, ~5 %.** — ⚠️ **LEAK-INFORMED. THIS BUCKET
   IS NOT A PREDICTION.** The bridge sent two of four regulators' shifts
   (0.0101384, 0.0101390) and the B-range they sit against, in the sentence
   saying they were not sending them. I computed 5.5 % from that within a
   minute, and **this bucket's boundary was chosen after seeing it.** If their
   four-regulator fraction lands here, the pre-registration establishes nothing
   about it.

   **I cannot reconstruct what I would have registered without the leak**, and
   claiming I would have written the same thing is exactly the retrospective
   move this file exists to prevent. So it is marked rather than rewritten.

   What is *not* leak-informed is the **interpretation** attached to it: that a
   much smaller fraction would mean the residual is not method-intrinsic, and
   that the candidate causes are my smaller lattice at fixed `l/L`, my
   nine-point grid versus their five, or my regulators differing more in the
   bulk where the mode interacts. **The boundary is contaminated; the mechanism
   reasoning is mine.** Those are separable and only one is spoiled.
3. **Their fraction is much larger.** Then mine is optimistic and the open
   systematic on my corner spread is worse than recorded.
4. **Their four regulators do not give a stable fraction at all** — the two-of-
   four preview differs sharply from the four-of-four value. Then neither of us
   can size the residual from four regulators, and *that* is the finding: the
   quantity needs more regulators, not more resolutions.

These differ in what they imply about **where the residual comes from** —
method, my lattice, their lattice, or estimator noise — so they are not one
hypothesis wearing four labels.

## What no outcome establishes

**None of these settles whether the s⁻² drift survives the systematic.** That
needs the residual's *s-dependence*, and neither of us has more than one
resolution of it. A single agreeing number at s=6 would be two instruments
agreeing at one point, which today has repeatedly been worth less than it looks.

## Value of this file, after the leak

**Asymmetric.** Outcomes 1, 3 and 4 are uncontaminated — nothing in the preview
bore on where their fraction would land relative to 20–45 %, above it, or
whether four regulators would give a stable value at all. **Outcome 2 is
informed.** A later reader should weight the file accordingly rather than
treating all four buckets as equally earned.

## Pre-committed refusals

- I will **not** fit anything to a 4-point max−min of a 4-point max−min.
- If their number and mine agree, I will **not** report it as confirmation
  without checking whether a shared step manufactured the agreement — the
  confound they found in our s=6 memory convergence.
- If they disagree, I will **not** assume mine is the correct one.
