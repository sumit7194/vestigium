# TODO — living list

*Open questions, unverified claims, and deferred work. Consolidated 2026-09-05 after EXP-011: nothing
settled is listed here. Settled items live in `report.md` (EXP-001 … EXP-011) and `RESULT.md` §10.*

## Open — actionable, unowned

- [ ] **The shape residual.** Why does the (σ, κ) trial function reproduce every computed curve to ≈1%
      ([BMW15b], [HHCWM16], [BCV21] all report it; none explains it)? Is the residual universal in
      sign (it overshoots every known curve: +0.9% Einstein at 26.6°, +0.2–0.6% free fields; BCV Fig. 2
      says smaller for μ < 0)? This is the half of the original problem the κ-band reframe leaves open.
- [ ] **The input any bound on κ needs** (RESULT.md §5–6, EXP-011): a growth condition on the
      bulk-channel density of the two-defect function that does not come from the tail itself.
      Named falsifier of the §6 classification: a third bridge (neither an inverted channel with a
      universal lowest state nor locality/anomaly). Entry points not surveyed here: defect fusion,
      Casimir energy of parallel conformal defects (no specific paper cited; verify before citing).
- [ ] **ECG t₄ sign.** [BCV21] Fig. 1 caption pairs μ = +0.00312 with t₄ = +4; [BCR18] eq. 129 gives
      t₄ = −1260 μ f∞²/(1−3μ f∞²), the opposite pairing. Adopted BCR18. EXP-002's obstruction is
      sign-independent; the fermion-side conflict is 3.5% (BCR18) or 1.4% (BCV21). An independent
      t₄(μ) for ECG would settle it.
- [ ] What orders scalar > fermion > ECG(t₄=−4) > Einstein > ECG(t₄=+4) in κ/C_T? Not t₄ (EXP-002).

## Caveats that travel with RESULT.md

- C4 at n = 1 (reflection positivity of the entropy correlation matrices, [CH12]) is a conjecture,
  checked there for free fields to 6×6 determinants. The negative result does not depend on it; any
  positive use of the spectral density ρ(s) would.
- O(N) Wilson–Fisher a₁(π/2)/C_T = 1.36(14), 1.3(1), 1.3(1) ([BMW15], [BWK16]): the Ising value behind
  1.36(14) is not printed in the cited [KHSM13]. *Partially verified.* Carries no information about κ.
- No four-digit free-field a(θ)/C_T exists below 45° (only [HHCWM16] ansatz/lattice pairs, ±1.3% at
  26.6°). The small-angle region is where the theories differ.
- Rényi-2 QMC ([LSZM24], [NCRCLM26]) disagrees with 2013–14 NLCE at 2–4σ; do not cite the old table.
- The Dirac/Rarita–Schwinger "same κ₄, different head" pair (EXP-011) is [AM26]'s statement; the
  edge-mode status of the spin-3/2 entropy was not examined.

## Parked — resume only on instruction

- **EXP-004 instrument** (parked 2026-09-05). Validated: `scripts/exp004_ch_solver.py` (double) on four
  exact smooth-limit coefficients to 7 digits and on published Rényi-2 values at 90°–153°;
  `scripts/exp004_mp.py` (mpmath, 25+3M digits, N-continuation) past the double-precision floor at
  M ≈ 4. Exists: Rényi-2 result to M = 15 (`scripts/exp004_renyi2_result_n24_24_p15.0_t1.json`);
  145 EE checkpoint nodes for M ≲ 1 in `scripts/exp004_nodes/`. To resume: run the known-answer
  controls first (σ = 1/256, s(π/2) = 0.01183, s(3π/4) = 0.002520, κ = 0.0397 for the scalar;
  σ = 1/128, s(π/2) = 0.02329, κ = 0.0722 for Dirac), then check smoothness of F in t at fixed M
  (branch flips), then decide the M > 15 tail (measured decay 0.83/unit M; ≈4·10⁻⁴ at 5°). Justified
  only if the shape residual becomes the target.
- Closed form of κ₂^f = (2/π)∫₀^∞ y² u²_{1/4}(y) dy (EXP-011): a Painlevé connection-type integral;
  integrable-systems curiosity; no bearing on the bound.
- Cross-dimensional log-convexity of the free-field κ_d (Mellin moments of one c-function, [AM26]
  eq. 4.17): free-field only; the [CH09] table needed to check it did not survive text conversion.
  Unchecked.

## Handed off — RESOLVED 2026-09-05 by `../quantum` (their commit `afc7ace`)

> **The bound was right and the lattice was wrong. The corrected value is CONSISTENT WITH the bound
> at the level the method can resolve — not PASS, and not FAIL.** Verified independently by the
> bridge; every figure reproduces.

    bound  a_min(120) = (1/32) log(2/sqrt3)  = 0.0044950     [pi^2 C_T/3 = 1/32 EXACTLY]
    committed      0.0038956   0.867x   13.3% below
    N=1024         0.0043706   0.972x
    N=2048         0.0044650   0.993x
    a(60)          0.0242324 -> 0.0256670  (+5.9%); vs expected 0.0264, was 8.2% low, now 2.8%

    3-param, m->0 extrapolated   0.0044915   0.9992x   marginally BELOW
    4-param, measured m=0.00125  0.0045195   1.0054x   ABOVE
      the two models differ 1.22% like-for-like at that window, and the bound sits INSIDE the gap
      correction to the committed value: +14.6% measured, +15.3% extrapolated

**~~PASS, m->0 = 0.0045099 at 1.003x~~ RETRACTED (`04db813`).** *That extrapolation imported
`r = 3.1` increments-per-halving, measured at the fixed R=4..14 window and carried to the plateau
without being re-measured there.* **The verdict is decided by that constant, not by the data:**

    r=2.0 -> 1.0143x   r=3.1 -> 1.0033x   r=4.0 -> 1.0003x   r=4.56 -> 0.9992x   r=5.0 -> 0.9986x
                                                     the sign flips at r ~ 4.3

**A third plateau point at m=0.005, N=512 — chosen so `xi/N = 0.391` matches the 0.39 of the other
two, so m varies alone at fixed geometry — measures `r = 4.56`, not 3.1.** *With only two plateau
points r was unconstrained.*

> **The deficit falls from 13.3% to 0.08%, into the residual model ambiguity, and that is the whole
> of what measurement supports.**

### Forward guidance from `../quantum` (`6ec989f`) — read this before resuming

    remaining deficit vs the bound       0.0786%
    3-param / 4-param gap, same window   1.2206%
    model ambiguity dominates by         15.5x

> **Pushing m lower CANNOT decide PASS or FAIL, however far it is taken.** The next halving needs
> N = 4096 and would refine a 0.08% term while a **1.22% term sits unresolved.**
> **The limiting factor is the fit model, not the m→0 limit.** What would settle it is a
> better-conditioned extraction — more subleading terms constrained over a longer lever arm in R —
> **not a smaller mass.**

*Their reason for flagging it, which is the part to keep:* **refining m is the intuitive move and it
would be the same error a fourth time — working the axis that is already converged while the
dominant one is untouched.** *That is this study's original defect (uncertainty quoted across
regulators while 61% sat in m) restated as forward guidance rather than as a post-mortem.*

**THE CAUSE, and it was not the short fit window this file proposed.** The extraction needs
`R << xi << N`. The committed run had `Rmax/xi = 0.14` (fine) but **`xi/N = 0.62` — the correlation
length was 62% of the BOX, so the box and not the mass was the IR cutoff and the softest modes went
unregulated.** Varying N alone moves a(120) by 2.3%; varying m alone by **61%**.

*This file's window hypothesis is refuted by the data: extending R makes it monotonically worse —
0.0038960, 0.0030028, 0.0004281, and **−0.0046760**, which is unphysical. The collapse was the clue,
not the answer.*

**A better plateau criterion than either fit alone, found on the way:** the 3- and 4-parameter fits
now **bracket** the answer and converge (5.5e-05 apart and narrowing); the committed pair **diverged**
(0.0038960 vs 0.0035869). *Confirmed on a second angle and shape, because a fix that only repairs the
number it was designed around is not a fix.*

**AND THE FIFTH INSTANCE OF THE CLASS, which is the transferable part.** The study quoted its
uncertainty as the **across-regulator spread, 1.85%** — and all four regulators shared the same N,
the same m and the same fit window. **That control could not have failed.** The real systematics are
orthogonal to it: **61% in m, ~12% in the window, 2.3% in N.**

> **The quoted precision measured the one axis that did not matter.**

**PROCESS DEFECT WORTH CARRYING.** `corner_angles.json` stored only fitted coefficients and never the
raw `S(R)` — so *"what happens if you refit over another window"* could not be asked without a full
re-run. **That is why the diagnosis took four scripts instead of one refit.** Store the raw data, not
just the fit.

*The shape-independence control was sound and is NOT implicated — it constrains the area coefficient,
not the log coefficient. It passed for the right reasons.*

**A correction the bridge owes:** this file cited *"the sibling's README puts the zero mode at ~20% of
B."* **Their README retracts that figure** — the 22–41% number is recorded there as an artifact of the
kernel set, moved 3.5× by one further admissible kernel, and the systematic was renamed
*bulk-coupling* because the mode is identical across admissible kernels by construction. **The
conclusion never depended on it; the number should not be carried onward.**

---

## Handed off — for the bridge, not for this session to fix

- **`../quantum` corner numbers vs the rigorous bound.**
  *The number:* `../quantum/qsim/corner_angles.json` gives, for a real massless scalar on a
  triangular lattice, a(120°) = 0.0038955 (3-parameter fit, mean over four regulators;
  per-regulator 0.003848–0.003920; 4-parameter fit 0.003499–0.003587) and a(60°) = 0.024232
  (4-parameter 0.024746–0.024934); `corner_coefficient.json` / `corner_s6.json` give
  a(90°) = 0.011604 (s=1) and 0.011673 (s=6) on the square lattice.
  *The bound:* for any CFT with finite C_T, a(θ) ≥ (π²C_T/3) log[1/sin(θ/2)] [BWK16] eq (II.2),
  a consequence of a'' ≥ −a'/sinθ (strong subadditivity + Lorentz invariance, [CHL09]) and of
  σ = π²C_T/24 (theorem, [FLP16]). For a real scalar C_T = 3/(32π²), so
  𝔞_min(120°) = (1/32) log(2/√3) = 0.004495, 𝔞_min(60°) = (1/32) log 2 = 0.02166,
  𝔞_min(90°) = (1/32) log √2 = 0.01083.
  *The comparison:* a(120°) is 13.3% BELOW the bound under the 3-parameter fit and 20–22%
  below under the 4-parameter fit; a(60°) passes the bound but is ≈8% below the expected
  value ≈0.0264; a(90°) passes and is 1.9% (s=1) / 1.3% (s=6) below the exact 0.011830 [CHL09].
  *Extraction parameters* (`qsim/corner_angles.py`): N = 160, m = 0.01 (ξ = 100, i.e. 0.6 N),
  triangles l ∈ {8,…,28} (3 corners, perimeter 3l), hexagons R ∈ {4,…,14} (6 corners,
  perimeter 6R), fit S = A·perimeter + B·ln(size) + C [+ D/size], a = −B/(number of corners);
  the shape-independence control (A from triangles vs hexagons) passed at < 0.05%.
  *Why the bound is the theorem and the lattice is the suspect:* the bound has no free
  parameter and uses only SSA, Lorentz invariance and C_T; the same code family gives the
  square-lattice a(90°) 1–2% low, and the triangular numbers come from smaller regions (R ≤ 14)
  with a log-fit over ln R ∈ [1.4, 2.6]. Candidate causes, not diagnosed: finite-size 1/size and
  zero-mode (k = 0) contamination (the sibling's README puts it at ~20% of B); the short ln-range
  making B degenerate with C and D. Not modified (read-only).
