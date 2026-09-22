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

On **2026-09-04**, in commit **`dbd443a`** of *this* repo, I vendored **218 files**
from `../corner_function` (cuspis), including their `scripts/` — their implementation
(211 files).

- **What I demonstrably read:** `RESULT.md`. I grepped `references.md` and
  `report.md`. I have **no record of reading `scripts/`**, and no reason to have.
- **What I cannot do:** prove a negative about my own reading beyond what the record
  shows. Stated because it is the honest limit.

### Identifier correction — `dbd443a` is MY hash, not cuspis's

Amended 2026-09-22. This pre-registration originally cited `dbd443a` as though it
named a **cuspis** state; so did cuspis, and so did the bridge's DAG. It does not. It
is **my own commit** — *"Check the kappa non-localisation claim from
../corner_function; all three pass"*, Fri 4 Sep 2026 — and it is the vendoring commit
itself. Cuspis's `5131089` reads *"INDEPENDENTLY VERIFIED by ../quantum (dbd443a)"*,
a correct citation of my hash that all three of us then read back as theirs.

The snapshot's **content** was identified correctly, because cuspis compared trees
rather than hashes. But **a hash is the one object in this whole audit that looks
unambiguous, and it is the thing that travelled mislabelled through three
repositories at once.** Recorded here rather than silently corrected.

### The date question is resolved, and it resolves in my favour

Cuspis's sub-45° work **postdates** the snapshot. `f6d40e6` "Phase 2" is dated
**2026-09-05**, and everything downstream — their pre-registration, the sign analysis,
the high-precision run, the node angle, the sharp-end constant — is 09-05 or later.
Checked from inside my own vendored tree as well: their notebook there ends at
EXP-011, and the later experiment numbers, the run mode, the constant and the node
value return **zero hits** across my four remaining prose files.

**I hold none of the n=1 magnitudes under audit.** Verified by the bridge in cuspis's
own history rather than taken on report.

### The contamination detector under-reported. Its zero is WITHDRAWN.

This pre-registration originally claimed a values-blind detector found **zero
angle-indexed numeric tables below 45°** in the vendored tree. **That zero is
withdrawn.** It was false, and I am deliberately *not* repairing the detector under
time pressure.

Cuspis found, in the tree I had scanned: a Rényi-2 result file with an explicit angle
key carrying **seven entries below 45°**, plus **145 per-node files**. I confirmed the
145 myself from filenames alone, without opening any of them.

**Three reasons it under-reported, worst first:**

1. **It was never committed.** There is no detector artifact in this repo — it was an
   ad-hoc invocation whose output I promoted straight into a pre-registration. It was
   never mutation-tested, so nothing ever demonstrated it *could* return non-zero.
   **A detector never shown to fire cannot distinguish "nothing there" from "not
   looking"** — the two produce the same output. This is the third decoration in a
   week, after the known-fail hook control and the two discarded convergence flags.
2. **It read prose; the values are in JSON.** The sub-45° data lives in
   `exp004_renyi2_result_*.json` and `exp004_nodes/*.json`, not in markdown tables.
3. **It read file *contents*; some values are in file *paths*.** `exp004_nodes/`
   encodes its parameters in the filenames themselves to ten decimal places. A
   content-scanner is structurally blind to a tree that stores data in its paths.

**This repo's own §8b lands on me here: a detector that under-reports is worse than
none**, because it launders "I did not look" into "there was nothing." Withdrawal
rather than repair is correct because **the n=1 conclusion never depended on it** — it
rests on cuspis's dates, which are independent of my instrument. Had the zero been
load-bearing, this check would now be dead.

### What the `git rm` does and does not do

Removing `corner_function/scripts/` prevents *future* exposure. It **cannot un-read
anything** — and the part I understated in the original text: **the files remain in
history at `dbd443a`, and this repository is PUBLIC** (`sumit7194/vestigium`,
confirmed `"private": false` against the GitHub API, not assumed). Cuspis's
implementation is recoverable with one `git show` from my own repo, by any reader —
including me.

**Their values are sealed. Their implementation is not, and the implementation is the
exact axis this check runs on.**

So, binding for the rest of this work: **no git archaeology.** I will not `git show`,
`git checkout`, `git log -p` or otherwise read `corner_function/scripts/` out of
history while building the solver, and the write-up will state that in its own voice.
A reader who knows git *will* ask, and the answer has to live in the document rather
than in my good intentions.

## Method

Implement **from the published Casini–Huerta–Leitão equations** — the paper, not
cuspis's code. `[CHL09]` = Casini, Huerta & Leitão, *Entanglement entropy for a Dirac
fermion in three dimensions: vertex contribution*, Nucl. Phys. B **814** (2009)
594–609, `arXiv:0811.1968` — already in this repo's bibliography, cited independently
in the corner work before this task existed.

Fresh file. No import from `corner_function/`, **and no reading of it out of git
history** (see "no git archaeology" above — the working tree no longer holds their
solver, but `dbd443a` does, and this repo is public). The only permitted inputs are
the published paper and this repo's own existing machinery.

## Conventions, fixed BEFORE seeing anything of theirs

These are the "shared convention correlates two errors without a shared line of code"
hazard, so they are declared rather than discovered:

| | choice |
|---|---|
| **field content** | to be confirmed with cuspis before comparing — a scalar and a Dirac fermion have *different* `a(θ)`, and comparing across them is a null result about bookkeeping |
| **normalisation** | `a(θ)` as the coefficient of `−log(R/δ)` in `S`, i.e. `S ⊃ −a(θ) log(R/δ)`; sign such that `a > 0` |
| **`C_T` normalisation** | `C_T` for a real free scalar `= 3/(32π²)`, the convention under which the BWK16 prefactor is exactly `1/32` — already used and checked in `qsim/CORNER_BOUND_FINDINGS.md` |
| **angle** | `θ` = the *opening* angle of the region, so `θ → π` is smooth and `θ → 0` is sharp |
| **Rényi index** | **`n = 1` (von Neumann) only.** Fixed here because it is the arm on which my exposure is clean; see the n=2 exclusion below |
| **reported quantity** | `a(θ)` and `a(θ)/C_T`, both, so a mismatch in one is diagnosable against the other |

**If these do not match cuspis's conventions, the honest outcome is NOT COMPARABLE**,
and that is a legitimate result — the ξ\* leg ended that way and the finding was the
correspondence check, not the number.

## The n = 2 arm is EXCLUDED, and the reason is not symmetry

Adopted 2026-09-22 as a condition from cuspis, and I would have had to adopt it
anyway once the detector fell over.

**This check covers `n = 1` only.** The Rényi-2 corner function is **out of scope and
declared contaminated**, because:

- The sub-45° values the withdrawn detector missed are **n = 2** values
  (`exp004_renyi2_*`). They were in a tree I held for eighteen days.
- Cuspis's n = 2 sharp-end constant was **later derived from that same file**.

So the n = 2 arm fails the only thing that makes a check worth running: I cannot claim
not to have held the answer. **It is not that n = 2 is harder — it is that for n = 2 I
am not a valid instrument.** No n = 2 number will appear in the output of this check,
and if one is wanted later it needs a party without my history.

The n = 1 arm survives because the dates put every n = 1 magnitude after my snapshot.
Note the asymmetry honestly: **n = 1 is clean by cuspis's calendar, not by my
detector.** My detector contributed nothing to either arm.

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

5. **Trusting an instrument I have not made fire.** The withdrawn detector is the
   live example, and it is in this list because the same shape is available again:
   every control below is a detector, and a control that has never been shown to fail
   is decoration. **Control 1 is therefore run with a deliberately wrong constant
   first**, to confirm it can reject, before it is trusted to accept.

## What this cannot establish

Two implementations agreeing does not make a value correct; it makes a *shared* error
less likely than an independent one. And with my exposure declared, it is weaker than
a clean-room replication would be. **The most this can deliver is: an independent
check, by a party with stated prior exposure, that either corroborates or contradicts.**

**And it is weaker than the original text implied.** That text leaned on a
values-blind zero to argue the exposure was nearly empty. The zero is gone. What
remains is cuspis's calendar — good evidence, but *their* evidence about *their*
repo, which is a different and weaker thing than a clean measurement of my own tree.
The honest summary is: **the n = 1 arm is clean on cuspis's dates, contaminated in
principle by eighteen days of holding their solver, and checked by someone who has now
been wrong twice about what he was holding.**
