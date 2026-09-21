# The two-condition matching scheme

Written 2026-09-21 after `PREREG_path_independence.md` falsified the one-condition
version. Feasibility measured before proposing; numbers below are runs, not sketches.

## Why one condition is not enough

- **Fixed coupling is confounded.** Measured: a **44× capacity gap** between `g=1`
  and `g=3` at identical `λ`, of which only **9.5×** is local-operator variance. Two
  published studies do exactly this (`arXiv:2011.13385`; Mirkin & Wisniacki 2021).
- **Fixed decoherence is insufficient.** Measured: at identical `S(ρ_S) = 0.150000`,
  the fraction of the record on the coupling site alone runs **0.766 → 0.998** as the
  route changes. The system's state is identical; the environment's record is not.

So a comparison must pin **how much** has been recorded *and* **how far** it has
spread. Two conditions, failing independently.

## The scheme

**Knobs:** `λ` (coupling) and `t` (time) — two.
**Conditions:** `S(ρ_S) = S*` and `t = t*` — two.
**Fully determined**, with no residual freedom, which is the point.

```
1.  Choose S* in the redundancy regime (S* = 0.15 works; 0.005 does not — at
    0.005 every chain gives f_δ = L/2 and R = 2.00, i.e. no redundancy exists).
2.  Choose a common time t*.
3.  For each environment g, solve for λ_g with S(ρ_S; g, λ_g, t*) = S*.
    CONVENTION, fixed in advance: the SMALLEST λ root. Capacity is non-monotonic
    in λ, so the target has several, and picking one after seeing the answer
    would be a free parameter.
4.  Compare the record structure at (g, λ_g, t*).
```

## Why "matched time" is the right second condition and not a fudge

**Measured**, not assumed. For the TFI chain `ε(k) = 2J√(1+g²−2g cos k)`:

| `g` | 0.5 | 1.0 | 1.5 | 2.0 | 3.0 | 5.0 |
|---|---|---|---|---|---|---|
| `v_max` | 1.000 | **2.000** | **2.000** | **2.000** | **2.000** | **2.000** |

`v_max = 2J` for **every `g ≥ 1`**. So on the paramagnetic side **equal time is
equal causal reach**, exactly — the second condition is physical, not a
convenience.

*(For `g < 1`, `v_max = 2Jg` and this breaks. There the second condition must be
`v_max·t` matched, not `t`. Stated because the scheme is otherwise silently wrong
in the ordered phase.)*

**It is also non-circular**, which matters more. `t` is a *control parameter*.
Matching on an *outcome* that measures spreading — the record's second moment, or
its participation ratio — would be matching on the answer, since participation ratio
is close to redundancy itself.

## Feasibility — measured

Solving step 3 for `S* = 0.15`:

| `t*` | reach `2t` | `λ(g=1.0)` | `λ(g=1.5)` | `λ(g=2.0)` | `λ(g=3.0)` |
|---|---|---|---|---|---|
| 0.15 | 0.30 | 1.396 | 2.264 | 3.467 | 11.554 |
| **0.35** | **0.70** | **0.657** | **1.179** | **2.270** | **3.740** |
| 0.70 | 1.40 | 0.454 | 1.055 | 1.631 | 3.393 |

Every chain matchable at every `t*` tried. **The scheme is feasible.**

## What it does NOT fix, stated rather than buried

1. **`λ` still differs across chains** — 0.657 vs 3.740 at `t*=0.35`, a 5.7× spread.
   That is unavoidable: escaping the fixed-coupling confound *requires* letting `λ`
   float. It must be **reported as a measured residual**, not assumed harmless.
2. **Injected energy is not matched.** Two knobs, two conditions, nothing left. Any
   third quantity one might want matched cannot be, and must be measured and
   reported alongside.
3. **Sufficiency cannot be checked from inside.** With `(S*, t*)` pinning the state
   uniquely, there is no residual direction to vary — so the analogue of today's
   path-independence check is *unavailable*. This scheme cannot verify itself.

## The sufficiency test, which needs a third knob

Add one: couple to **two** sites with independent strengths `(λ₁, λ₂)`. Then there
are three knobs against two conditions, leaving **one free direction**. Sweep it at
fixed `(S*, t*)` and ask whether the record structure moves.

- **It does not move** → `(S, t)` is sufficient within that family, and the scheme
  is licensed.
- **It moves** → two conditions are not enough either, and the honest conclusion is
  that comparing how different environments record may not be well-posed at all
  with these variables.

That is the same shape as the check that killed the one-condition version, and it
should be run **before** the comparison, not after — which is the one thing today
established beyond the physics.
