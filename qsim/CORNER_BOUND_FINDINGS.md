# a(120°) fails the BWK16 bound — diagnosis

Reported by thebridge-f0 on behalf of another workspace. **The report is correct
and the committed number is wrong.** Root cause found, correction measured, bound
satisfied after correction.

## The bound is real and I verified it independently

`a(theta) >= (pi^2 C_T/3) log[1/sin(theta/2)]`, from SSA + Lorentz invariance
[CHL09] plus `sigma = pi^2 C_T/24` [FLP16]. For a real scalar `C_T = 3/(32 pi^2)`,
so the prefactor is **exactly 1/32**. No fitted parameter, no threshold.

| | bound | committed | ratio |
|---|---|---|---|
| a(60°) | 0.0216610 | 0.0242324 | 1.119 ✓ |
| a(90°) | 0.0108304 | 0.0116040 | 1.071 ✓ |
| a(120°) | **0.0044950** | **0.0038956** | **0.867 ✗** |

Self-consistency check on the two inputs: the bound must reduce to `sigma(pi-th)^2`
as `th -> pi`. It does, ratio `1.000000` at `th = 179.9°`. The normalisation is right.

## What it is not

**Not a short fit window.** That was my first hypothesis and the data refutes it.
Extending R at the original `N=160` makes it *worse*, monotonically, through zero
and negative:

| window | a(120°) |
|---|---|
| 4..14 | 0.0038960 |
| 10..20 | 0.0030028 |
| 16..26 | 0.0004281 |
| 22..32 | **−0.0046760** |

A negative corner coefficient is unphysical, so that collapse is itself an
artifact — and it points at the real cause.

## What it is: the IR regime was never in the CFT window

The extraction needs `R << xi << N`. Below `xi` the mass cuts the corner log;
above `N` the box, not the mass, is the real IR cutoff and the softest modes go
unregulated (`G_X(k=0) = 1/2m`).

**The committed run had `Rmax/xi = 0.14` (fine) but `xi/N = 0.62` (broken).**
`N=160` with `m=0.01` means the correlation length is 62% of the box.

Separating the two axes at a fixed window:

| varied | range | effect on a(120°) |
|---|---|---|
| `N` alone (160→480) | ξ/N 0.62→0.21 | **2.3%** |
| `m` alone (0.04→0.0025) | — | **61.0%** |

The mass dominates, and `a(120°)` rises monotonically as `m -> 0`. At `N=640` vs
`N=1024` the numbers agree to 0.002%, so box effects are exhausted; the residual
is entirely the mass and the region size.

## The corrected extraction

In a regime where the whole chain holds, sweeping R to 36:

**`N=1024, m=0.0025`** (ξ/N = 0.39, Rmax/ξ = 0.09) → plateau **0.0043706**, 0.972× bound.
**`N=2048, m=0.00125`** (ξ/N = 0.39, Rmax/ξ = 0.045) → plateau **0.0044650**, 0.993× bound.

The 3-parameter and 4-parameter fits **bracket** the answer and converge toward
each other — 3-param from below, 4-param from above, differing by `5.5e-05` at
the largest window and still narrowing. The original extraction had no such
crossing; its two fits *diverged* (0.0038960 vs 0.0035869).

### The `m -> 0` extrapolation, corrected

**The first version of this section claimed `BOUND SATISFIED` and it was wrong.**
It extrapolated with `r = 3.1` increments per halving of `m` — a ratio measured
at the **fixed `R = 4..14` window**, not at the plateau, and imported without
checking. The conclusion is sensitive to exactly that number:

| assumed `r` | a(120°) | vs bound |
|---|---|---|
| 2.0 | 0.0045594 | 1.0143 |
| 3.1 (imported) | 0.0045100 | 1.0033 |
| 4.0 | 0.0044965 | 1.0003 |
| 5.0 | 0.0044886 | 0.9986 |

It flips at `r ≈ 4.3`. With only two plateau points, `r` was unconstrained.

A third plateau point at `m = 0.005, N = 512` — chosen so `xi/N = 0.391` matches
the 0.39 of the other two, varying `m` alone at fixed geometry — **measures** it:

```
m = 0.005    a(120) = 0.0039402
m = 0.0025   a(120) = 0.0043706    increment +0.0004304
m = 0.00125  a(120) = 0.0044650    increment +0.0000944

measured r = 4.56   (not 3.1)
extrapolation m->0 : 0.0044650 + 0.0000265 = 0.0044915 = 0.9992x bound
```

**Still 0.08% below.** The honest statement:

- 3-param, extrapolated to `m -> 0`: **0.0044915, 0.9992× — marginally below**
- 4-param, measured directly at `m = 0.00125`: **0.0045195, 1.0054× — above**

So the bound is satisfied **within the bracket of the two fit models**, which
differ by 1.2% at that window, but the 3-parameter route alone does not clear it.
The deficit falls from **13.3% to 0.08%** — into the residual model ambiguity —
and that is all that can be claimed from measurement here.

**Correction to the committed value: +15.3%** (measured 0.0044650 against
0.0038956 is +14.6%; with the corrected extrapolation, +15.3%).

### What would actually settle it — and what would not

Worth stating, because the obvious next step is the wrong axis. The remaining
deficit is **0.08%**; the gap between the two fit models at the same window is
**1.22%** — model ambiguity dominates the shortfall by **15×**.

So pushing `m` lower (the next halving needs `N = 4096`) refines a 0.08% term
while a 1.22% term sits unresolved, and cannot decide PASS or FAIL however far
it is taken. **The limiting factor is the fit model, not the `m -> 0` limit.**
What would settle it is a better-conditioned extraction — more subleading terms
constrained over a longer lever arm in `R` — not a smaller mass.

Noting this explicitly because choosing to refine `m` here would be the same
error a fourth time: work on the axis that is already converged while the
dominant one is untouched.

### Same failure, third time in one session

The imported `r` is the third headline number in two days that rested on a
parameter held fixed and never varied: the LRL window quoted at fixed `a`; this
study's uncertainty quoted at fixed `(N, m, window)`; and now an extrapolation
quoted at an `r` imported from a different window. **In all three the instrument
was sound and the summary statistic carried an unexamined constant.**

## Independent confirmation on a different angle and shape

A fix that only repairs the number it was built around is not a fix. The same
protocol applied to triangles at 60°:

| | committed | corrected | change |
|---|---|---|---|
| a(60°) | 0.0242324 | 0.0256670 | +5.9% |

and there the 3-param and 4-param fits **agree to 0.05%** at the plateau
(0.0256735 vs 0.0256873). Same direction, same mechanism, independent geometry.

## The methodological finding, which is the transferable part

The committed study quoted its uncertainty as the **across-regulator spread,
1.85%**. All four regulators shared the same `N`, the same `m`, and the same fit
window. The dominant systematics are orthogonal to regulator choice:

```
across regulators (what was quoted) :  1.85 %
across fit window                   :  ~12  %
across N                            :  2.3  %
across m                            :  61   %
```

**The quoted precision measured the one axis that did not matter.** The four
regulators could not have disagreed about an IR regime they all shared, so that
control could not have failed — the same class as the degenerate `{L_z,A_x}=0=0`
check in `lrl_secular.py` and, per thebridge, as findings in two other workspaces
the same day.

The shape-independence control (A from triangles vs hexagons, <0.05%) is sound
and is not implicated. It constrains the **area** coefficient; the defect is in
the **log** coefficient, which that control does not touch.

## Process defect

`corner_angles.json` stored only fitted coefficients, never the raw `S(R)`. The
question "what happens if you refit over a different window" **could not be asked
without a full re-run**. All four diagnostic scripts here write their raw `S(R)`
to disk.

## Correction to the report as received

thebridge cited "your own README puts [the zero mode] at ~20% of B". The README
**retracts** that figure: the 22–41% number is recorded there as an artifact of
the kernel set (one further admissible kernel moves it 3.5×), and the systematic
was renamed *bulk-coupling* because the mode is identical across admissible
kernels by construction. The stale figure did not affect the conclusion, which
stands on its own.

## Status of the committed numbers

`qsim/corner_angles.json` values are **superseded**. `a(120°) = 0.0038956` is low
by 16% and violates a theorem; `a(60°) = 0.0242324` is low by ~6% and passes the
bound only because the bound is loose at 60°. The pre-registered *ordering* P1
(`a(60) > a(90) > a(120)`) survives the correction.
