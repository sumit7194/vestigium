# Testing the secular-average lemma on the Kepler problem

**Lemma under test.** `H = H0 + e*H1`. If `Q` survives to first order, then
`A = <{H1,Q}>` over closed orbits of `H0` must vanish. `A != 0` proves `Q` does
not survive; `A = 0` proves nothing.

**Substrate.** `H0` = Kepler, `Q` = the Laplace–Runge–Lenz vector.
Instrument: [`qsim/lrl_secular.py`](qsim/lrl_secular.py). Gate:
[`qsim/lrl_gate.py`](qsim/lrl_gate.py) — 12 assertions, 3 negative, green.
No general relativity anywhere.

Two averaging routes sharing no code path: exact true-anomaly quadrature
(`dt = r^2 dth / L`) and DOP853 time-integration of the unperturbed orbit at
`rtol=1e-12`. They agree to `1.5e-10` worst case on the grid.

## Calibration, before any result was read

| identity | worst over 200 random states |
|---|---|
| `{H0, A_i} = 0` | `2.5e-09` |
| `{A_x, A_y} = -2 H0 L_z` (so(4)) | `7.2e-10` |
| `dA_i/dp_j` analytic vs finite difference | `1.3e-10` |

Two failures worth recording, because both would have produced a
green-looking instrument:

- I first wrote the so(3) relation as `{L_z,A_x} = -A_y`. The correct sign is
  `+A_y`. Caught because the check failed at exactly `2.00 = |2A_x|/|A|`.
- With perihelion along `+x`, `A_y` is *identically zero*, so `{L_z,A_x} = +A_y`
  reads `0 = 0` — a test that passes any implementation. The orbit is now
  rotated by 1.1 rad before the check, and the non-degenerate so(4) relation
  was added, which no choice of sign can satisfy accidentally.

## The three controls

`A_x` is omitted from the tables: **it is identically zero by parity for every
central perturbation** (`A_x ~ INT f'(r) r^2 sin th dth`), measured at `<2e-15`.
A test built on `A_x` alone returns zero for any central perturbation and is
worthless. That is a property of the lemma's substrate, not of this code.

### TRIVIAL — `dk/r`, the same Kepler problem with a different constant

The one the ask says people skip. Nine `(a,e)` points:

| | `A_y` theta-quad | `A_y` ODE-time | `|{H1,A}|` pointwise |
|---|---|---|---|
| worst on grid | `1.0e-16` | `1.9e-11` | **0.43 to 11.0** |

Machine zero, while the bracket being averaged is nonzero pointwise by up to
**11.0**. Both halves matter: had the bracket vanished pointwise the control
would have proved nothing about the averaging. Analytically `f' r^2 = dk` is
constant, so `A_y ~ INT cos th dth = 0` identically in `(a,e)` — not an
accidental zero.

### POSITIVE — `beta/r^2`, known to destroy LRL

`A_y = 2 pi beta e / (T a (1-e^2))`, agreeing with quadrature to **`1.4e-14`**
on every grid point. This is not a fit: the known perihelion advance for a
`1/r^2` term is `-2 pi beta / L^2` per orbit, and `|A| = k e`, giving the same
expression through `L^2 = k a (1-e^2)`.

Nonzero on an **open set**, smallest grid value `1.8e-02` — not a point.

But note `A_y ∝ e`: **it vanishes at `e = 0`.** That is exactly the accidental
zero the ask warns about, and it is degenerate rather than a false negative —
`|A_LRL| = k e` is itself zero on a circular orbit, so there is nothing there to
destroy. A test run only at `e = 0` would have reported "survives" for a
perturbation that demonstrably does not.

### POSITIVE — `F.r`, uniform field (non-central, tests vector structure)

`A_y` from `-1.33` to `-2.11` across the grid, both routes agreeing to
`1e-10`; `A_x < 2e-16`.

## Dynamical validation — without leaning on small `eps`

Integrating the **full** perturbed system and comparing to `-eps*A`:

| `eps` | turns | ratio | deviation |
|---|---|---|---|
| 0.0200 | -0.94 | 0.9675 | `-3.25e-02` |
| 0.0100 | -1.02 | 0.9879 | `-1.21e-02` |
| 0.0050 | -1.06 | 0.9949 | `-5.15e-03` |
| 0.0025 | -1.08 | 0.9977 | `-2.35e-03` |
| 0.00125 | -1.09 | 0.9989 | `-1.12e-03` |

Deviations halve as `eps` halves — `O(eps)`, as it should be. Richardson to
`eps = 0`: **`1.00011`**.

Two methodological points, both of which initially gave wrong answers:

- **The observable must be the angle, not `A_y`.** The secular motion of `A` is a
  *rotation*. Fitting a line to `A_y(t)` is valid only while the turn is small,
  which smuggles back the small-`eps` assumption the ask rules out. Tracking the
  unwrapped angle of `A` is linear for arbitrarily many turns.
- **`n_orb` must scale as `1/eps`.** At fixed `n_orb` the accumulated turn shrinks
  with `eps`, so the fit degrades exactly where it must be sharpest, and the
  ratio walks *away* from 1 as `eps -> 0`: 0.968, 0.993, 1.010, 1.030. That
  ascending sequence is an artifact of the diagnostic and would have been easy to
  report as a physical `O(eps)` correction with the wrong sign.

**Sign.** `dA/dt = eps {A,H1} = -eps {H1,A}`, and `A` averages `{H1,A}`. So `A`
as the ask defines it is **minus** the secular rate. Sign-only conclusions drawn
from `A` are inverted unless this is tracked.

## Convergence: not the problem

The ask asked whether the averaging integral is only conditionally convergent.
**It is not — it is absolutely convergent for every `e < 1` and every exponent.**
The integrand for `beta/r^n` is

```
f'(r) r^2 = -n beta (1 + e cos th)^(n-1) / p^(n-1)
```

bounded in `th`; the `r^2 dth` measure cancels the pericentre singularity
exactly. Checked at the worst case available, `n = 5` and `e = 0.99`, where `r`
varies by a factor of 199 and the *integrand* spans seven decades:

| `n` | `e` | `n=2001` vs `n=32001` |
|---|---|---|
| 2 | 0.99 | `4.0e-15` |
| 5 | 0.99 | `7.2e-15` |

## The hypothesis nobody states

This is the answer to the ask's last question, and it is not about convergence.

Averaging replaces `A(t)` by its mean drift and discards an oscillating
remainder `F1`:

```
A(t) = A(0) + eps <g> t + eps F1(t),    g = {H1, A}
```

"`F1` is bounded" is true **for each fixed orbit**. But the lemma is applied over
an **open set** of orbits, and the step needs the bound to be **uniform** there.
It is not:

| `e` | `|F1|` peak-to-peak | `|F1|(1-e)` | window `eps` | window `/[e(1-e)]` |
|---|---|---|---|---|
| 0.10 | 3.14 | 2.828 | 0.0318 | 0.354 |
| 0.30 | 3.71 | 2.595 | 0.0809 | 0.385 |
| 0.50 | 5.13 | 2.564 | 0.0975 | 0.390 |
| 0.70 | 8.77 | 2.630 | 0.0798 | 0.380 |
| 0.90 | 27.22 | 2.722 | 0.0331 | 0.367 |
| 0.95 | 54.79 | 2.740 | 0.0173 | 0.365 |
| 0.99 | 274.70 | 2.747 | 0.0036 | 0.364 |

`|F1|` grows by **87x** across this range while `|F1|(1-e)` is constant to 1%.
So `|F1| ~ C/(1-e)` with `C ~ 2.74`, and requiring the discarded oscillation to
stay below the quantity being tracked, `eps |F1| << |A_LRL| = k e`, gives

```
eps  <  (k/C) e (1-e)  ~  0.37 e (1-e)
```

The last column confirms this over the whole range (mean 0.372, spread 9.9%).
The window is not a fitted curve: `k/C = 1/2.74 = 0.365` is predicted from the
measured `C` and matches.

**The window vanishes at both ends, for different reasons:**

- `e -> 0` because `|A_LRL| = k e -> 0` — there is nothing to destroy, and the
  positive control's `A_y ∝ e` vanishes with it.
- `e -> 1` because `|F1| ~ (1-e)^-1` — the discarded oscillation diverges and
  swamps the drift.

So `A != 0` is a valid necessary condition on a **band** of eccentricities, not on
the open set as usually stated. Near-circular and near-parabolic orbits both need
`eps` far smaller than a naive reading suggests, and nobody writes this down.

## Verdict on the instrument

Passes in both directions with all three controls, including the trivial one at
`1e-15` while its bracket is nonzero pointwise by up to 11.0. It is not measuring
the parametrisation. The lemma is sound as a necessary condition, with two
caveats that are properties of the lemma rather than the code: the sign
inversion, and the non-uniform `F1` bound above.
