# Hazards for the Darwinism literature sweep — named BEFORE it runs

Committed before any search. The sweep's likely output is a **negative** ("nobody
has asked whether the redundancy structure is path-independent"), and a negative is
where a narrow query survives, because the absence cannot be falsified from inside
the sweep that produced it. That rule cost me the cusp/corner exclusion this morning;
these are the specific ways I expect it to bite again.

## H1 — Vocabulary miss on the OBJECT axis (the one that has already bitten twice today)

The same physics carries at least six names, and a sweep in one dialect returns a
clean, confident, wrong nothing:

- **quantum Darwinism** / redundancy / `R_δ`
- **objectivity** / objective classical reality
- **spectrum broadcast structure (SBS)** — the Korbicz–Horodecki school, a *different
  and stronger* criterion than mutual-information Darwinism
- **state broadcasting** / quantum broadcasting
- **central spin model** decoherence
- **Loschmidt echo** / decoherence factor — the same quantity in another dialect,
  which is how Quan 2006 is indexed

Two vocabulary misses were found in this fleet today, six hours apart: my
cusp/corner exclusion, and ansatz missing a 2013 paper for thirteen years because it
said "first integral" and never "Killing tensor". **Assume a third is waiting.**

## H2 — The variable-axis narrowness I committed this morning

On 09-05 I widened a sweep from "bound in terms of `C_T`" to "bound in terms of
anything" and reported the negative as strengthened — having never widened the
**object**. Here the analogous error is searching only for *"redundancy vs central
charge"* when the live question is whether anyone has examined **matched decoherence,
coupling normalization, or path-dependence** at all, in any environment.

## H3 — Right paper, wrong theorem

Papers *do* study Darwinism in spin-chain environments. Finding one does not answer
my question: if it compares environments at **fixed coupling**, it contains the exact
confound I hit (a nearly-frozen operator in the paramagnetic phase) and is evidence
that the question is **open**, not closed. The check is what each paper *held fixed*,
not what it studied.

## H4 — The unfalsifiable negative

If the sweep returns "nobody asked about path-independence", that claim cannot be
tested from inside the sweep. **Mitigation, fixed in advance:** the finding is only
reportable as *"not found in a sweep of N named vocabularies"*, with the
vocabularies listed, never as *"nobody has asked"*.

## What would make the planned run pointless

Finding a paper that (a) varies the environment's phase, (b) normalizes the coupling
so decoherence is matched rather than the coupling, and (c) reports the redundancy or
SBS structure at a level where a record is actually redundant. **That is the outcome
I am looking for** — finding it is cheaper than discovering it after building.

---

# Sweep result, part 1 of 2 — methodology (2026-09-21)

**The sharpest thing found, and it reframes the question.**

For the **system**, path-independence is a *theorem*: for Gaussian pure dephasing the
qubit's reduced state depends only on the scalar decoherence function
`Γ(t) = ∫dω J(ω) coth(βω/2)(1−cos ωt)/ω²`. Weak-coupling-long-time and
strong-coupling-short-time are equivalent **for the qubit**. Textbook.

For the **environment**, whether the internal record structure — which fragments hold
what — is likewise fixed by `Γ` alone was **not found in the sweep**. The
Darwinism/SBS literature studies redundant encoding but does not frame it as a
function of a single scalar decoherence parameter, and no "same `Γ`, different route"
comparison of fragment structure surfaced.

**So the question is not "is decoherence path-independent" — that half is settled.
It is: does the system's path-independence extend to the environment's record?**
The asymmetry is the question, and it is sharper than what I had.

Established vs not, from the sweep:

| | status |
|---|---|
| fixed **reorganization energy** `λ = (1/π)∫dω J(ω)/ω` across spectral densities | **established, standard practice** |
| susceptibility controls decoherence rate (not `λ` alone) | established mechanistically — Quan et al. 2006 |
| a named "normalize by `Var(σᶻ)`" convention | not found |
| **decoherence factor as the independent variable** instead of time | **no established convention found** |
| route-independence of the **environment's** internal structure | **not found — this is the gap** |

*Queries listed in the agent's report; the negative is reportable only as "not found
in a sweep of those terms", per hazard H4.*

## Two measurements of my own, run while the sweep was out

**1. My stated mechanism is incomplete.** I claimed the 44× capacity gap comes from
`σᶻ` going frozen in the paramagnet. Measured at `L=10`:

| `g` | `⟨σᶻ⟩` | `Var(σᶻ)` | Var ratio | capacity ratio | cap/Var |
|---|---|---|---|---|---|
| 1.0 | 0.6854 | 0.53027 | 1.000 | 1.000 | 0.554 |
| 1.5 | 0.8776 | 0.22981 | 0.433 | 0.227 | 0.290 |
| 2.0 | 0.9342 | 0.12722 | 0.240 | 0.089 | 0.205 |
| 3.0 | 0.9716 | 0.05596 | 0.106 | 0.023 | 0.119 |

`Var` falls **9.5×** while capacity falls **44×**, so `cap/Var` moves by 4.7× and is
not constant. **Normalizing `λ` by `√Var` would close 9.5× of 44× and leave 4.7×.**
The frozen-operator story is real but partial — consistent with the sweep's finding
that *susceptibility*, an integrated response, is what controls decoherence, not the
equal-time variance.

**This kills the normalize-by-variance design** and argues for letting `λ` float and
matching on the invariant directly.

**2. The λ-float design is feasible.** Gapped chains do reach the redundancy regime
if `λ` is allowed to rise: `g=3` reaches `S(ρ_S)=0.153` at `λ=3.0` and `0.999` at
`λ=6.0`, against `0.0067` at `λ=0.6`.

**New hazard found in the same table: capacity is NON-MONOTONIC in `λ`** (at `g=1`:
0.289, 0.876, 0.994, 0.849, 0.729 for `λ` = 0.6, 1.5, 3, 6, 12). So "solve for the
`λ` that reaches the target" has **multiple roots**, and the convention must be fixed
in advance — **smallest `λ`** — or the choice becomes a free parameter after the fact.
