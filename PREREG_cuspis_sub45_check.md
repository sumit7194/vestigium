# Pre-registration — independent CHECK of cuspis's sub-45° corner-function magnitudes

**Committed before fetching the source equations and before writing any solver.**
Nothing of cuspis's sub-45° region has been read. The conventions and the agreement
criterion below are fixed *now*, so neither can be chosen after seeing their numbers.

## Scope: this is a CHECK, not a REPLICATION

Per the fleet's `SCOPE_MANIFEST` field 9: *if SHARED INPUT WITH is non-empty you may
claim a CHECK; you may not claim a REPLICATION unless the construct was sealed and the
score was blind.* **My field is non-empty.** So this is an independent check with
declared prior exposure, and the write-up will say so in its own voice — not in a
footnote.

## Declared prior exposure, in full

On **2026-09-04** (`dbd443a`) I vendored **218 files** from `../corner_function`
(cuspis) into this repo, including their `scripts/` — their implementation.

- **What I demonstrably read:** `RESULT.md`. I grepped `references.md` and
  `report.md`. I have **no record of reading `scripts/`**, and no reason to have.
- **What I cannot do:** prove a negative about my own reading beyond what the record
  shows. Stated because it is the honest limit.
- **Values-blind contamination check (2026-09-22):** I ran a detector over the
  vendored tree that reports **only counts, never values**, so running it could not
  contaminate the reader. It found **zero angle-indexed numeric tables below 45°**.
  My snapshot is frozen at 09-04.
- **Mitigation taken before starting:** `git rm` of `corner_function/scripts/`.
  This **prevents future exposure; it cannot un-read anything**, and the files remain
  in history at `dbd443a`. The detector result is the stronger fact, not the removal.
- **Open condition:** whether cuspis's sub-45° work predates or postdates 09-04.
  If it postdates, I hold none of it. If it predates, this proceeds anyway — as a
  check, with the exposure declared louder.

## Method

Implement **from the published Casini–Huerta–Leitão equations** — the paper, not
cuspis's code. `[CHL09]` = Casini, Huerta & Leitão, *Entanglement entropy for a Dirac
fermion in three dimensions: vertex contribution*, Nucl. Phys. B **814** (2009)
594–609, `arXiv:0811.1968` — already in this repo's bibliography, cited independently
in the corner work before this task existed.

Fresh file. No import from `corner_function/`. The only permitted inputs are the
published paper and this repo's own existing machinery.

## Conventions, fixed BEFORE seeing anything of theirs

These are the "shared convention correlates two errors without a shared line of code"
hazard, so they are declared rather than discovered:

| | choice |
|---|---|
| **field content** | to be confirmed with cuspis before comparing — a scalar and a Dirac fermion have *different* `a(θ)`, and comparing across them is a null result about bookkeeping |
| **normalisation** | `a(θ)` as the coefficient of `−log(R/δ)` in `S`, i.e. `S ⊃ −a(θ) log(R/δ)`; sign such that `a > 0` |
| **`C_T` normalisation** | `C_T` for a real free scalar `= 3/(32π²)`, the convention under which the BWK16 prefactor is exactly `1/32` — already used and checked in `qsim/CORNER_BOUND_FINDINGS.md` |
| **angle** | `θ` = the *opening* angle of the region, so `θ → π` is smooth and `θ → 0` is sharp |
| **reported quantity** | `a(θ)` and `a(θ)/C_T`, both, so a mismatch in one is diagnosable against the other |

**If these do not match cuspis's conventions, the honest outcome is NOT COMPARABLE**,
and that is a legitimate result — the ξ\* leg ended that way and the finding was the
correspondence check, not the number.

## Agreement criterion, fixed before any number exists

For each angle compared:

| outcome | verdict |
|---|---|
| relative difference `< 1e-6` | **AGREES** — independent implementations converging at solver precision |
| `1e-6` to `1e-3` | **AGREES WITH A DISCREPANCY TO EXPLAIN** — reportable, but the source must be found before either is called confirmed |
| `> 1e-3` | **DISAGREES** — and the disagreement is the finding |
| conventions irreconcilable | **NOT COMPARABLE** — no grade applies |

**Precision floor declared in advance:** my implementation must demonstrate its own
convergence *independently* — agreement with cuspis is not evidence that either is
converged. I will report my value at two working precisions and show the digits are
stable before any comparison.

## Known-answer controls, which must pass before the sub-45° region is touched

1. **`θ = π/2`.** Exact published value for the free scalar is `0.011830` (CHL09).
   My implementation must reproduce it. *This is the whole basis for trusting the
   sub-45° output* — the region where no published value exists is checked by an
   instrument validated where one does.
2. **Smooth limit.** `a(θ) → σ(π−θ)²` as `θ → π` with `σ = π²C_T/24`. Verified in
   this repo already to ratio `1.000000` at `θ = 179.9°`.
3. **BWK16 bound.** `a(θ) ≥ (π²C_T/3)·log[1/sin(θ/2)]` must hold at every angle
   computed. Below 45° this bound is *strong*, so it is a live constraint there and
   not a formality.
4. **Sharp limit.** `a(θ) → κ/θ` as `θ → 0`.

**If control 1 fails, nothing below 45° is reportable**, and I will say the
instrument failed rather than quietly widening the tolerance.

## Setup correspondence — am I computing the same quantity at all?

*Required by the pre-commit hook, which has now caught this omission three times.
Here it is not a formality: the correspondence IS the risk.*

**The claim is "cuspis's sub-45° magnitudes are right/wrong." The condition is my
solver, at the conventions above, for a specific field content, at a specific
normalisation of `a(θ)`, with `θ` defined as the opening angle.** Those are the same
statement **only if** every one of those choices matches theirs.

They are not free parameters I may reconcile afterwards. A scalar and a Dirac fermion
have genuinely different `a(θ)`; a factor of 2 in the `log` normalisation or an
opening-vs-deficit angle convention produces a clean-looking disagreement that is
pure bookkeeping. **Both must be established before the numbers are placed side by
side, not after one of us dislikes the answer** — the ξ\* leg died exactly here, and
that verdict was correct.

So the gating order is fixed: **conventions reconciled → my controls pass → then and
only then a comparison.** If conventions cannot be reconciled, the result is
**NOT COMPARABLE** and no grade in the agreement table applies. That is a legitimate
outcome of this exercise and not a failure of it.

**And the asymmetric part:** my sub-45° numbers will exist whether or not the
correspondence holds. The temptation on finding a mismatch will be to hunt for the
convention that removes it. Registering the order in advance is what makes that
visible if I do it.

## Named ways this fails

1. **A shared convention correlating two errors.** The failure that needs no shared
   code. Mitigated by declaring conventions above, *before* comparing — but only
   mitigated, not eliminated, since we may both inherit a convention from CHL09.
2. **My prior exposure leaking through structure rather than values.** I have read
   `RESULT.md`. If my implementation unconsciously mirrors their decomposition, a
   match is worth less than it looks. Mitigated by implementing from the paper and by
   this declaration; **not** eliminated.
3. **Agreement at an unconverged value.** Two implementations can converge to the same
   wrong number if both inherit the same truncation. Hence the independent
   convergence demonstration above, required *before* comparison.
4. **The sub-45° region being where the method is weakest.** As `θ → 0` the integrand
   stiffens. A solver that silently returns its initial guess produces a plausible
   number — the exact fault audited in this repo yesterday. Every solve reports its
   convergence flag, and a discarded flag is a defect.

## What this cannot establish

Two implementations agreeing does not make a value correct; it makes a *shared* error
less likely than an independent one. And with my exposure declared, it is weaker than
a clean-room replication would be. **The most this can deliver is: an independent
check, by a party with stated prior exposure, that either corroborates or contradicts.**
