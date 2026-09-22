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

**DEFECT, recorded 2026-09-22 — control 1 cannot certify beyond `2.1e-4`.** The
published `0.02366` has four significant figures, so the real-scalar value
`0.01183` derived from it carries a half-ulp of `2.1e-4` relative. Control 1 can
therefore reject a solver wrong by more than that and **cannot see anything finer**.
The `< 1e-6` AGREES band below remains meaningful as a statement about **two
implementations agreeing with each other** — but the absolute anchor for that
agreement is only `2.1e-4` from control 1. The one control that certifies to high
precision is σ, where `1/256` is exact; and it certifies only the smooth end.
**So a `< 1e-6` agreement with cuspis below 45° would establish that we agree,
not that either of us is right to `1e-6`.** Written down now so it cannot be
rounded up later.

**Precision floor declared in advance:** my implementation must demonstrate its own
convergence *independently* — agreement with cuspis is not evidence that either is
converged. I will report my value at two working precisions and show the digits are
stable before any comparison.

## Known-answer controls, which must pass before the sub-45° region is touched

1. **`θ = π/2`.** Real free scalar: **`0.011830`**. *This is the whole basis for
   trusting the sub-45° output* — the region where no published value exists is
   checked by an instrument validated where one does.

   **AMENDED 2026-09-22 — this control was sourced from cuspis, not from the
   literature, and it arrived with their citation error attached.** See
   "The control values were inherited" below. Re-sourced from primary literature:
   `0.02366` is printed in **Table 1 of arXiv:0811.1968** for a **complex** scalar;
   the real scalar is **half** that by the explicit rule at **hep-th/0606256 p.7,
   eq. (40)** — *"for a real scalar field (half the complex scalar result)"*.
   So `0.02366/2 = 0.01183`. **The number is not printed anywhere**; it is derived
   from a printed 4-significant-figure value, which sets a hard precision floor of
   `2.1e-4` relative — see the defect note under the agreement criterion.
2. **Smooth limit.** `a(θ) → σ(π−θ)²` as `θ → π` with `σ = π²C_T/24`. Verified in
   this repo already to ratio `1.000000` at `θ = 179.9°`. Real scalar
   `σ = 1/256 = 0.00390625` exactly. **Independently confirmed against CHL's
   numerics** — see the σ cross-check below, which is the one piece of this that
   cuspis could not have handed me.
3. **BWK16 bound.** `a(θ) ≥ (π²C_T/3)·log[1/sin(θ/2)]` must hold at every angle
   computed. Below 45° this bound is *strong*, so it is a live constraint there and
   not a formality.
4. **Sharp limit.** `a(θ) → κ/θ` as `θ → 0`. Real scalar `κ = 0.0397`
   (`0.0794/2`, Table 1 `c₋₁⁽⁰⁾`, same halving rule). Also inherited — see below.

**If control 1 fails, nothing below 45° is reportable**, and I will say the
instrument failed rather than quietly widening the tolerance.

## The control values were INHERITED FROM CUSPIS. Hazard 1 has fired.

Found 2026-09-22 while re-sourcing the controls, and it is the most serious thing
in this document.

`0.011830` appears in exactly two places in my working tree: this
pre-registration, and **cuspis's own prose**. `corner_function/TODO.md` line 43
reads:

> *"run the known-answer controls first (σ = 1/256, s(π/2) = 0.01183,
> s(3π/4) = 0.002520, κ = 0.0397 for the scalar; σ = 1/128, s(π/2) = 0.02329,
> κ = 0.0722 for Dirac)"*

**That is my four known-answer controls. All four values, the scalar/Dirac split,
and the ordering.** I did not assemble this control set from the literature and
then discover cuspis had the same one. I took theirs.

**The citation error corroborates it; the verbatim line match proves it.** This document cited **CHL09 — the Dirac
fermion paper — for a free-scalar value.** Anyone reading the primary sources
would cite the scalar paper (CH07, `hep-th/0606256`) for a scalar number; the
fermion paper's own abstract says it *"extend[s] a previous work in which the
scalar case was treated."* *(Softened 2026-09-22 at the bridge's correction: CHL09's Table 1 **does**
print the complex scalar beside the fermion, so citing it for the real scalar is
**imprecise** — a comparison table instead of the original paper, plus an unstated
halving — rather than a field error. Two readers independently making both moves is
unlikely, so it corroborates; but the conclusion rests on the line match, not on
this.)* The shared attribution is a **corroborating fingerprint**, and
`corner_function/TODO.md` line 153 carries the identical attribution: *"below the
exact 0.011830 [CHL09]"*. **I inherited cuspis's number together with cuspis's
mistake, and the mistake is how I can tell.**

`hep-th/0606256` likewise appears in my tree only in **cuspis's**
`references.md`. My own bibliography has the fermion paper and not the scalar one.
So this document's claim that the citation was *"already in this repo's
bibliography, cited independently in the corner work before this task existed"* was
**true of CHL09 and false of the paper the control actually needed.**

**This is hazard 1 of this very document** — *"a shared convention correlating two
errors; the failure that needs no shared code"* — and it fired on the citation
before a line of solver existed. Recorded rather than quietly repaired, because a
corrected citation with no note would have destroyed the only evidence that the
inheritance happened.

### And I hold more sub-45° information than "values sealed" implied

The same `TODO.md` — one of the four prose files I **kept** — also carries
`"measured decay 0.83/unit M; ≈4·10⁻⁴ at 5°"`. That is a truncation-tail
magnitude, not `a(5°)`, so it does not give me the answer. **But it is a
quantitative statement about the sub-45° region, in a file I retained and said I
had grepped.** It names the Rényi-2 result file and the 145 nodes outright, too.

So the withdrawn detector has a **fourth** failure mode, and it is the worst one:
**the information was in a file I kept, not only in the files I deleted.** The
detector was pointed at `scripts/`. The prose describing `scripts/` was never in
its field of view.

### Implementation-axis exposure, picked up while tracing the number

Declared because hazard 2 (*"my prior exposure leaking through structure rather
than values"*) is about exactly this, and I read it on 2026-09-22 in the grep
output that located `0.011830`. The same `TODO.md` passage states that cuspis's
production route used **mpmath at "25+3M digits" with N-continuation**, hit a
**double-precision floor at M ≈ 4**, and ran the Rényi-2 result to **M = 15** with
a **measured tail decay of 0.83 per unit M**.

That is **method**, not values — but method is the axis this check runs on. It
tells me in advance where double precision will fail and roughly how far in `M`
the integral must go. **If my implementation independently hits a floor near
M ≈ 4, that is not independent confirmation of theirs**; it may be me reaching for
arbitrary precision at the point I was told to. Recorded so that any such
coincidence is read at its discounted value.

### What survives

The inheritance does **not** make the controls wrong — re-sourced from primary
literature, all four of cuspis's values are **correct**. It makes them **not
independent**, which is a different defect and the one that matters for a check.
Corrected standing:

- Every control value is now cited to its **printed** source and the published
  halving rule, with the derivation shown.
- The **σ cross-check below is the only control genuinely independent of cuspis**,
  because it comes from a relation they never used.
- This is declared in the write-up in its own voice, not a footnote.

## The σ cross-check — the one control cuspis could not have handed me

CHL09 Table 1 gives `c₂⁽ᵖⁱ⁾ = 7.81253×10⁻³` for a complex scalar, computed
numerically in 2009. Halved for a real scalar: **`3.906265×10⁻³`**.

My convention, fixed in this document *before* any source was fetched, gives
`σ = π²C_T/24` with `C_T = 3/(32π²)`, i.e. **`3/768 = 1/256 = 0.00390625` exactly**.

**Relative difference `3.8×10⁻⁶`** — precisely the resolution of CHL's printed six
figures. So CHL's numerically-computed coefficient *is* the exact rational `1/256`.

This matters for three reasons:

1. **It validates my `C_T` normalisation against an independent number.** The
   `σ = π²C_T/24` relation is [FLP16]; CHL's `c₂` is 2009 numerics. **Neither
   paper cites the other** — the agent's full-text grep found **no occurrence of
   `C_T` in any of the three CHL papers.** Two literatures seven years apart,
   agreeing to their stated precision.
2. **It is immune to the inheritance above**, because cuspis's route to `1/256`
   was not through `C_T` at all.
3. **It explains a "coincidence" CHL flagged and could not account for.** They
   write that *"the quadratic coefficients of s_D(x) and s_S(x) turn out to be
   equal"* and call it remarkable. It is not remarkable: in d = 3,
   `C_T(complex scalar) = 2 × 3/(32π²) = 3/(16π²) = C_T(Dirac)`, verified
   identical here to machine precision. **Equal `C_T` ⇒ equal σ.** *Claimed as an
   explanation, not a discovery* — the relation is published and anyone holding
   both facts gets this immediately. It is recorded because it is a second,
   independent confirmation that my normalisation is the right one.

### The bound is live at the angles where a value exists

| θ | `a(θ)` real scalar | BWK16 bound | ratio |
|---|---|---|---|
| 90° | 0.011830 | 0.01083042 | 1.0923 |
| 135° | 0.002520 | 0.00247418 | **1.0185** |

135° clears by **1.85%**. The bound is not slack here, so control 3 is a real
constraint and not a formality — and below 45° it is stronger still.

### My own lattice route, for scale

This repo's pre-exposure square-lattice run gives `a(90°) = 0.011720`, **0.93%
below** 0.011830. CHL check their own continuum results against lattice numerics
and report *"perfect accord (around one percent error)"*. So the lattice route
sits exactly where CHL's own lattice checks sit. **Consistent — and it is a
genuinely independent third point**, being pre-exposure, a different method, and
neither cuspis's nor the one being built.

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
