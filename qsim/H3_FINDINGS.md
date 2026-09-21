# H3 — how a record is laid down, and why environments cannot yet be compared

Work of 2026-09-21/22, the first on this repo's founding question since 08-22.
Pre-registrations: `PREREG_darwinism_critical.md`, `PREREG_path_independence.md`,
`PREREG_sufficiency.md`. This document states **only what survives every correction
made along the way**, with the scope line attached to each claim.

## The instrument

One qubit dephased by coupling to a **single site** of an `L=10` transverse-field
Ising chain, exact in the full Hilbert space, so the record must *spread* rather than
being written everywhere at once.

**Four controls, all passing** (`darwinism_controls.json`):

| control | value |
|---|---|
| C1 trivial — `λ=0` gives `I(S:F)=0` **while the chain is entangled** (`S_half = 0.547`) | `9.4e-16` |
| C3 pure-state sum rule `I(S:all) = 2S(ρ_S)` | exact to 10 digits |
| C4 monotonicity of the partial-information plot | `+1.0e-02` |
| C2 known answer — independent qubits reproduce textbook Darwinism | plateau matches `S(ρ_S)` |

C1 is built to avoid the failure the LRL trivial control was built for: a zero that
comes from nothing being entangled proves nothing.

---

# What is defensible

## 1. The system's path-independence does **not** extend to the environment

For Gaussian pure dephasing the qubit's reduced state depends only on the scalar
decoherence function — weak-coupling-long and strong-coupling-brief are **provably
equivalent for the qubit**. They are **not** equivalent for the environment.

At `S(ρ_S) = 0.150000` held to **`4.7e-16`**, varying only the route
(`path_decisive.json`):

| `λ` | `t` | `I(S:i₀)/S` |
|---|---|---|
| 0.5 | 0.5333 | **0.7660** |
| 1.2 | 0.1760 | 0.9671 |
| 5.0 | 0.0411 | **0.9976** |

`i₀` is the coupling site — reached by every route **by definition**, so there is no
causal-reach escape. Single fragment: no averaging, no sampling, no noise floor.
The system's state is identical in every row; the record is not. **Span 0.2316.**

*Mechanism, and it is not subtle:* as `λ→∞`, `t→0` and the record has no time to
leave the site it was written on.

## 2. Matching decoherence **and** duration is still not enough

At `S* = 0.150000` and `t* = 0.35`, varying only the *temporal shape* of `λ` at the
same site moves `I(S:i₀)/S` from `0.8304` (front-loaded) to `0.9431` (back-loaded) —
**12.70%, monotone** (`sufficiency.json`). Control: two-step machinery reproduces the
single-step result to **`5.6e-16`**, so this is physics and not stepping error.

`(S*, t*)` is therefore a **protocol convention**, not a physical characterisation —
it works only because "constant `λ`" silently acts as a third condition.

## 3. Four scalar conditions are still not enough

With `S*`, `Σλ`, `Σλ²` and `Σλ³` all fixed, the record still varies by **`0.0752`**
across the remaining free direction — about **8.8% of the mean `I/S`**
(`order5.json`, 34 points, `S` held below `1.6e-10`).

## 4. Comparing environments at fixed coupling is confounded

Between `g=1` and `g=3` at identical `λ`, the **capacity** — the most which-path
information the environment can ever hold — differs by **44×** (`0.2935` vs
`0.0066`). Only **9.5×** of that is the local-operator variance falling, so
normalising `λ` by `√Var` would close 9.5 of 44 and leave 4.7.

**Two published studies compare environments at fixed coupling** (`arXiv:2011.13385`
states it explicitly; Mirkin & Wisniacki 2021 normalise the environment's *initial
condition*, not the decoherence outcome).

## 5. A small exact fact, useful to anyone building this comparison

For the TFI chain `ε(k) = 2J√(1+g²−2g cos k)`, the maximum group velocity is
**exactly `2J` for every `g ≥ 1`**. So on the paramagnetic side **equal time is equal
causal reach** — which makes "matched duration" a physical second condition rather
than an arbitrary one. *(For `g<1`, `v_max = 2Jg` and this fails; there the condition
must be matched `v_max·t`.)*

## 6. The capacity result is not new

A gapless environment records far better than a gapped one: this is **Quan, Song,
Liu, Zanardi & Sun, PRL 96, 140604 (2006)**. They couple to *all* spins; this is a
local-coupling variant. **It validates the instrument and is not a discovery.**

---

# What is NOT defensible

- **The shape of the decline across orders.** Spans `0.1661 → 0.1468 → 0.0961 →
  0.0752` do decline, but **every one moved when its coverage was fixed — by 73%,
  160%, 992% and 93% — against order-to-order differences of 12%, 35% and 22%.**
  The sweep sensitivity exceeds the signal. Each span is a **lower bound**; none is
  certified converged.
- **Whether finitely many conditions suffice.** Not resolvable by this method.
- **Which environment records more redundantly.** `R_δ` and `I(f=1)/S` point in
  opposite directions, because `R_δ = L/f_δ` assumes fragments are interchangeable
  and a spatially concentrated record makes them not.
- **Any critical-vs-gapped comparison of record structure.** Never measured —
  the comparison is not yet well-posed, which is the whole point of the above.
- **The original H3 hypothesis** (redundancy carrying a log correction with
  coefficient set by `c`). Untested. The matched comparison it needs does not exist.

# Scope

`L = 10`, one TFI chain, one coupling site, `g = 1` for all route work, `S* = 0.15`,
`t* = 0.35`, structure read from `I(S:i₀)`. Narrow. Nothing here is a statement about
the thermodynamic critical point: a 16-site chain at `g=1` has `ξ > L`, the regime
the ξ\* leg showed is not a meaningful axis.

# Corrections made along the way

Recorded because the result is the residue of them, not independent of them: a 1 GB
allocation from tracing to the larger side of a pure state; a linear scan floor that
reported "no crossing" for the **fastest** chain; a first path-independence analysis
that returned **PATH-INDEPENDENT** by comparing a paired spread against an unpaired
noise floor; an order-4 sphere 3.3× too small, whose correction I then failed to
apply to orders 2 and 3 — **both of which happened to be the ones supporting my
conjecture**; and an order-3 radial sweep that found only second crossings because
the constant-λ point lies on the curve.

# The one claim to carry forward

**Matching outcome scalars — however many — does not pin the environment's record.
Any comparison of how different environments record must declare its route
convention as an assumption.** Everything beyond that is below this method's
resolution.
