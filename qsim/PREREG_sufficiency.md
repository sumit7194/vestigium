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
