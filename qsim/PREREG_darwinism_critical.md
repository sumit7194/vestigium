# Pre-registration — does a record crystallise differently in a critical environment?

**Written and committed before any measurement code exists.** H3 from `PROPOSALS.md`.
This is the founding question's thread: *when does a quantum possibility become a
fact?* One answer this repo already demonstrated is that the environment ends up
holding many redundant copies of the outcome — `decoherence_frames.py` measured 4 of
12 environment qubits already carrying 95% of the record.

**Every Darwinism result in this repo used a GAPPED, effectively structureless
environment.** The two halves of this repo — the decoherence lab and the exact
critical-chain machinery (`log_coefficient_boundary.py`) — have never been joined.
This joins them.

## The setup

- **System**: one qubit, prepared in `(|0⟩+|1⟩)/√2`.
- **Environment**: transverse-field Ising chain, `L` sites,
  `H_E(g) = −J Σ σˣᵢσˣᵢ₊₁ − h Σ σᶻᵢ`, `g = h/J`. Critical at `g = 1`.
- **Coupling**: pure dephasing to **one site** `i₀` (the middle), `H_int = λ σᶻ_S ⊗ σᶻ_{i₀}`.
  The record must then *spread* through the chain rather than being written
  everywhere at once — which is the whole point, and the opposite of the
  independent-qubit textbook case.
- **State**: `|Ψ(t)⟩ = (1/√2)(|0⟩|E₊(t)⟩ + |1⟩|E₋(t)⟩)` with
  `|E_±(t)⟩ = e^{−iH_±t}|E₀⟩`, `H_± = H_E(g) ± λσᶻ_{i₀}`, `|E₀⟩` the ground state of `H_E(g)`.
- **Observable**: the partial-information plot `I(S:F)` against fragment size `f`,
  and the redundancy `R_δ = L / f_δ`, where `f_δ` is the smallest fragment with
  `I(S:F) ≥ (1−δ) S(ρ_S)`. Default `δ = 0.1`.

**Two routes, sharing no code path** (house rule):
- **A**: exact full Hilbert space, `L ≤ 16`. Gives the *full* `I(S:F)` including
  coherences, so control C3 below is available. Cheap: `2^17` complex amplitudes.
- **B**: Gaussian/free-fermion branches with the fragment mixture built exactly,
  `L` up to a few hundred, `f ≤ 10`. Gives the Holevo quantity only.
- They must agree on the Holevo quantity at common `L`. If they do not, neither is
  reportable.

## Predictions, with falsifiers

**P1 — form of the approach.** At criticality the deficit `D(f) = χ∞ − χ(f)` decays
as a **power law** in `f`; in the gapped phase it decays **exponentially**, with a
scale set by `ξ`.
*Falsified if* the gapped case shows a power law, or the critical case shows a clean
exponential, over the same lever arm.

**P2 — direction.** At **matched decoherence** (see hazard H-a), redundancy is
**lower** at criticality than in the gapped phase. Reasoning: power-law correlations
between fragments mean the copies overlap rather than being independent, and
redundancy counts *independent* copies.
*Falsified if* `R_δ(critical) ≥ R_δ(gapped)` at matched decoherence.
**This is the one I most expect to lose** — the opposite argument (a critical chain
transports information further, so more fragments learn) is just as sayable, and I
am recording that I cannot currently rule it out.

**P3 — universality, the risky one.** The critical power-law exponent in P1 does not
move with the coupling `λ` or with time `t`, once decoherence is matched.
*Falsified if* the exponent moves with either.

## Controls that can fail

- **C1 TRIVIAL.** `λ = 0` ⇒ `I(S:F) = 0` to machine precision for every `f`, **while
  the chain itself is strongly entangled** (its own block entropy is large). If the
  bracket is zero only because nothing is entangled, the control proves nothing —
  the same failure the LRL trivial control was built to avoid.
- **C2 KNOWN ANSWER.** Set `J = 0` and couple every environment qubit to `S`: the
  textbook independent-qubit case. Must reproduce a **sharp plateau at `S(ρ_S)`** and
  `R_δ ≈ L`, matching `decoherence_frames.py`'s existing result.
- **C3 SUM RULE.** The global state is pure, so `I(S:F = all) = 2 S(ρ_S)` exactly.
  Machine precision, route A only. This is the check that catches a wrong partial
  trace.
- **C4 MONOTONICITY.** `I(S:F)` non-decreasing in `f` under fragment averaging.

## Setup correspondence — the condition this runs at, against the claim it makes

*Required by the pre-commit hook, and it is doing real work here: the claim says
"critical environment" and the condition says something narrower.*

**The claim is about a critical environment. The condition I run at is a FINITE
CHAIN AT `g = 1` WITH `ξ > L`.** Those are not the same thing, and the ξ\* leg
(scored `NOT COMPARABLE` earlier today) is exactly the precedent: there, a gate fired
in a regime where `ξ ≈ 13 N`, and the conclusion was that `ξ ≪ box` was not merely
unseparable but **not a meaningful axis at all**. A 16-site chain at `g = 1` is in
that same regime by construction. So every result here is a statement about a finite
chain at the critical coupling, and any sentence that says "at criticality" without
that qualifier is over-claiming. Recorded now, before a number exists, so the
qualifier cannot be dropped later by a version of me that likes the result.

**P2's comparison runs at matched `S(ρ_S)`, not matched `t`** — stated in the
prediction and restated here because the correspondence *is* the prediction in P2's
case. If the comparison is ever made at equal `t`, P2 is not being tested; a
different quantity is.

**Route A and route B run at different conditions and measure different quantities**
— A gives the full `I(S:F)` including coherences, B gives the Holevo quantity only.
They correspond *only* on the Holevo quantity at common `L`, and that overlap is the
only place they may be compared. A route-A number and a route-B number placed side
by side outside that overlap are about different things, which is the leg-7 failure
in miniature.

## Named ways this is expected to fail

1. **"Matched decoherence" doing the work (the dangerous one).** Critical and gapped
   chains decohere the system at *different rates*. Comparing at equal `t` would let
   any difference be a difference in how far decoherence has got, not in the
   environment's structure. **All comparisons are made at equal `S(ρ_S)`, never at
   equal `t`.** Recorded before the run because this is exactly the shape of the
   "held one axis fixed and varied the one I chose" error this repo has logged six
   times.
2. **Lever arm.** `L ≤ 16` gives `f ∈ [1, 8]` — three points in log space. A "power
   law" over that range is nearly unfalsifiable. Route B exists to extend it, and any
   P1 claim from route A alone is provisional and must say so.
3. **The light cone.** Information from `i₀` reaches distant sites only after a
   Lieb-Robinson time. At short `t`, `I(S:F)` depends on fragment *position*, not
   just size. Fragments are sampled uniformly at random, and the light-cone radius is
   reported alongside every plot.
4. **Fragment sampling convention.** Random subsets and contiguous blocks give
   different plots. **Fixed in advance: uniformly random subsets**, averaged over
   samples, with contiguous blocks reported separately as a secondary view and never
   substituted for the primary.
5. **Reading finite-size structure as physics.** A chain of 16 sites at criticality
   has `ξ > L`, which is the regime the ξ\* work just showed is *not a meaningful
   axis*. Any claim about "critical" behaviour here is a claim about a finite chain
   at `g = 1`, not about the thermodynamic critical point, and must be worded that way.

## What this cannot show

It cannot answer when a possibility becomes a fact. It can measure whether the
*record* that makes a fact objective is laid down differently when the environment
has structure at every scale. If P1–P3 all hold, the claim available is that the
approach to redundancy carries a universal exponent — not that the founding question
is answered.


---

# OUTCOME — 2026-09-21, route A, `L = 10`

Controls all pass: C1 `9.4e-16` at `λ=0` while the chain's own half-entropy is
`0.547` (so the zero is not trivial); C3 sum rule exact to ten digits; C4 monotone;
C2 reproduces textbook Darwinism.

## 1. Capacity — reproduces a known 2006 result, and is NOT new

The most which-path information each chain can ever hold, identical coupling `λ=0.6`:

| `g` | max `S(ρ_S)` | at `t` | ratio to `g=1` |
|---|---|---|---|
| 1.00 (critical) | **0.29352** | 58.8 | 1.000 |
| 1.20 | 0.16325 | 5.9 | 0.556 |
| 1.50 | 0.06656 | 0.65 | 0.227 |
| 2.00 | 0.02610 | 0.45 | 0.089 |
| 3.00 | 0.00664 | 0.25 | **0.023** |

A **44× spread**, and the critical chain is also fastest to any given level.

**This is Quan, Song, Liu, Zanardi & Sun, PRL 96, 140604 (2006)** — *Decay of
Loschmidt Echo Enhanced by Quantum Criticality* — a qubit coupled to a
transverse-field Ising chain, decoherence accelerated by criticality. They couple to
**all** spins; I couple to **one site**, so this is a local-coupling variant. **It
validates the instrument and it is not a new result.** Recorded that way because the
temptation to present it as the headline is exactly what this repo keeps catching.

## 2. The pre-registered comparison is DEGENERATE — and that is the finding

P2 required matching at equal `S(ρ_S)`. Correct, and hazard 1 was the right hazard.
But the capacity gap forces the common level to `≤ 0.8 × min capacity = 0.00531`,
and there:

| `g` | `t_match` | `f_δ` | `R_δ` | `I(f=1)/S` |
|---|---|---|---|---|
| 1.00 | 0.047 | 5 | **2.00** | 0.1174 |
| 1.20 | 0.057 | 5 | **2.00** | 0.1276 |
| 1.50 | 0.072 | 5 | **2.00** | 0.1373 |
| 2.00 | 0.099 | 5 | **2.00** | 0.1457 |
| 3.00 | 0.178 | 5 | **2.00** | 0.1517 |

**`f_δ = L/2` and `R_δ = 2.00` for every `g`.** Needing half the environment is the
*opposite* of a redundant record. At the only decoherence level all five chains can
reach, **the phenomenon under study does not exist**.

So: **P2 is NOT RESOLVED — neither confirmed nor falsified.** The design that
correctly avoids hazard 1 and the phenomenon it was built to measure are
**incompatible in this system**. P1 and P3 are untestable for the same reason.

**The non-preregistered measure, flagged as such.** `I(f=1)/S` is monotone in `g`
and runs the way P2's *reasoning* predicted — a single site carries 29% less of the
record at criticality than at `g=3`. **I am not promoting this to the result.** It
was not pre-registered, the spread is small, and elevating a secondary measure
because the registered one came out flat is the exact post-hoc move this repo has
logged repeatedly.

## 3. Two bugs, both mine, both found by watching rather than reasoning

**(a) 1 GB allocation on a shared box.** `rdm` built a `2^(L+1)` matrix — 8192×8192,
1.07 GB, at `f = L` for `L = 12`. The global state is **pure**, so `S(A) = S(Ā)`
exactly and the trace should always go to the smaller side; the identity was
available the whole time. Caught by watching RSS climb past 0.95 GB while ansatz had
just said RAM is the binding constraint and deepstrain had 2.4 GB live. Fixed: max
matrix `2^6` instead of `2^11`, sum rule still exact.

**(b) A scan floor that lied about the fastest case.** `match()` scanned linearly
from `t = 0.05` and reported **"no crossing" for the critical chain** — the one with
44× the capacity — because it passes the tiny target *before* `t = 0.05`. **A scan
floor is an assumption about rates, and it was wrong by the largest margin exactly
where the physics was fastest.** Fixed with log spacing from `1e-4`.

## 4. What is actually established

- The instrument is validated (four controls, one exact sum rule, one known-answer
  reproduction of a 2006 result).
- A gapless environment records which-path information far better than a gapped one
  — **known since 2006, reproduced here under local coupling.**
- **The redundancy question this was built to ask cannot be answered in this system**,
  because matched decoherence and measurable redundancy do not co-exist. Answering it
  needs a system where the capacity gap is small enough that both chains reach a
  decoherence level at which a record is actually redundant — a different setup, not
  a longer run.
