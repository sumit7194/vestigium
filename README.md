# vestigium

**When does a quantum possibility become a fact?**

*vestigium* — Latin for **trace**, **record**, **footprint**. All three are the same object
here: the partial *trace* is the operation at the heart of nearly every script below; the
*record* is what turns a superposition into an outcome; and the *footprint* left in the
environment is why observers agree on what happened.

This is a laboratory for the measurement problem, built in small verified steps. Nothing in
it is new physics — every result reproduces something already known, some of it for a
century. That is the point: **each experiment is checked against exact analytics or a real
published measurement**, so when the machinery is later pointed at an open question, the
machinery itself is not in doubt. Two of our own bugs were caught by exactly these checks
(both documented below).

---

## Foundations experiments

Each is a standalone script with its verification printed at the top of the run.

| Experiment | What it shows | Verified against |
|---|---|---|
| [`weak_measurement.py`](qsim/weak_measurement.py) | collapse as a **gradual process** under continuous monitoring | Born rule *emerged*: 30.6% of runs committed to the 30% branch (predicted 0.300 ± 0.024); conditional variance rides the exact Riccati curve to steady state 1/√(8k) within 0.2–1.0% |
| [`decoherence_frames.py`](qsim/decoherence_frames.py) | the which-path record accumulating collision by collision; **quantum Darwinism**; **revival** | V = cosᵏ(θ/2) to 2×10⁻¹⁶; V²+D² = 1 to 4×10⁻¹⁶; 4 of 12 environment qubits already hold 95% of the record; a recycled 2-qubit environment returns V to 1.0000 at collision 16 exactly as predicted |
| [`zeno.py`](qsim/zeno.py) | a watched quantum system **freezes**; telegraph dynamics at strong monitoring | survival matches [cos²(π/2N)]ᴺ to 0.0055 across N = 1…64 (Itano et al. 1990, trapped ions); flip rate fits k^−0.96 vs. the Zeno prediction k^−1 |
| [`bohmian_fan.py`](qsim/bohmian_fan.py) | pilot-wave **trajectories** from the guidance equation (the Philippidis fan) | equivariance: 20,000 guided paths rebuild the Born fringes to 4.3% of peak with no Born rule imposed; **0 of 20,000** trajectories crossed the symmetry axis |
| [`csl_toy.py`](qsim/csl_toy.py) | **objective collapse** (CSL-type): superpositions die with *size*, no observer required | V(N) rides exp(−κ₀N²d²T); real-units panel reproduces the actual exclusion logic — Adler's rate puts the edge at ~10⁵ amu (right at Fein-class experiments), GRW's at ~10⁹ amu |
| [`teleport.py`](qsim/teleport.py) | entanglement + **2 classical bits** moves an unknown state; neither ingredient works alone | fidelity 1.000000000000 over 2000 Haar-random states; with the bits withheld Bob's state is *exactly* I/2 (4×10⁻¹⁶) — no-signaling, constructively; entanglement-free ceiling 0.6706 vs. theory 2/3 |
| [`wigner_friend.py`](qsim/wigner_friend.py) | whether "a measurement happened" is **relative to the observer** | sealed lab: interference ⟨X_S X_F⟩ = 1 *and* reversal fidelity = 1, while the friend's own state is a definite I/2; once the record leaks both fall to 0 and ½. ⟨X_S X_F⟩ = cos(φ/2) to 2×10⁻¹⁶ |
| [`bell_game.html`](qsim/bell_game.html) | **CHSH and GHZ as games you can lose** | 40,000 rounds: classical 74.56% against its 75% ceiling, quantum 85.30% vs. cos²22.5° = 85.36%; GHZ **100.00%, zero losses in 40,000 rounds** where every classical plan caps at 75% |

## Hidden dimensions — the projections program

The idea *"maybe fields are stacked in dimensions we don't see and we watch the shadow"*,
made precise and run through three independent engines. Full write-up in
[`PLAN_projections.md`](qsim/PLAN_projections.md).

| | | |
|---|---|---|
| [`kk_projection.py`](qsim/kk_projection.py) | **mass = motion in a hidden dimension** (Kaluza–Klein) | rest-buzz frequencies 1.0022 / 2.0031 / 3.0027 against the exact tower 1 / 2 / 3; group velocities within 0.66% of Klein–Gordon |
| [`kk6_twisted_tower.py`](qsim/kk6_twisted_tower.py) | two hidden loops with a **twist** — the axion as a measurable spectral splitting | blind protocol (formula scored only after measurement): all 10 winding sectors within 0.3%; the (1,1)/(1,−1) pair splits by 0.44867 vs. 0.44996 predicted, while (1,0)/(0,1) stay degenerate to 6.7×10⁻¹⁶ |
| [`fractal_boundary.py`](qsim/fractal_boundary.py) | does a **structured detector wall** change where particles land? | yes for *how many* — periodic vs. Cantor masks at identical 29.6% coverage differ by ~67% in detection efficiency — but the fringes never move: the wall gates, it does not shift |

The neural leg (*can a network discover the hidden dimension from projections alone?*) and the
symbolic leg (*is the Kaluza reduction a theorem?*) live in the sister repos below. All three
agreed.

## Cross-validation probes

Independent numerics for the [trivium](https://github.com/sumit7194/trivium) cross-validation
project — deliberately implemented without sharing code, so agreement means something.

- **[`entropic_hinge.py`](qsim/entropic_hinge.py) + [`hinge_mp.py`](qsim/hinge_mp.py)** — the
  Longo relative-entropy identity underpinning the 2026 entropic-gravity result
  ([Dorau & Much, PRL](https://arxiv.org/abs/2510.24491)): relative entropy of a coherent
  excitation on a wedge = 2π × its boost energy. **Verified to 0.02–0.21%** on a harmonic
  chain at two lattice resolutions. Two findings worth more than the check: this computation
  is **impossible in double precision** (the modular weights live in e⁻¹⁰⁰-scale covariance
  tails — every float64 sweep carried 10–14% clip bands), and the Gaussian modular matrix has
  an **operator-ordering trap** that a thermal self-test passes silently — only a *squeezed*
  state distinguishes them. Both now permanent regression tests.
- **[`entropic_time.py`](qsim/entropic_time.py)** — does the "entropic time" of
  [Barontini, PRR 2026](https://arxiv.org/abs/2509.07745) depend on *which* coarse-graining
  you choose? Five legitimate clocks from one exact two-mode Bose–Hubbard run. Same-family
  control agrees at |τ| = 0.984; the cross-family test **disagrees at 0.181** inside the
  paper's own domain of validity, and coarsening the event set does not rescue it. But the
  regime scan is the real answer: agreement **switches on near Λ ≈ 2–4**. Reported as
  *conditional support with a mapped boundary, not a refutation* — real split-BEC junctions
  are interaction-dominated, so the construction is likely robust where it was run; the
  critique is the missing qualifier.
- **[`log_coefficient_boundary.py`](qsim/log_coefficient_boundary.py)** — is the entanglement
  log coefficient non-universal *permanently*, or only in a regime? Prediction recorded before
  the run, then confirmed: exact free-fermion Ising chain gives a **scaling collapse in ξ/L
  alone** (matched ξ/L agrees to ≤0.058 across L = 64→512), converging on the universal c/6 to
  0.6% at criticality, with universality **switching on at ξ/L ≈ 2.5**. The ordered branch is
  excluded on physics, not convenience — its ground state is exponentially degenerate, and the
  run self-flagged it (a ratio of 15.0 with the smallest mode energy at exactly 0.0).

- **[`kappa_vs_mutual_info.py`](qsim/kappa_vs_mutual_info.py)** — if a quantity is
  regulator-contaminated in *every* regime, the move is not to hunt for a clean regime but to
  **change channel**. On one 2D lattice with four regulators sharing a continuum limit, the
  area-law coefficient κ spreads by **41.6%** — and the *same* lattice refinement that drives
  the mutual information's spread from 2.18% down to **0.096%** (as s^−2.26, converging) leaves
  κ's spread at 41.8% → 41.7%, unmoved. So κ's regulator dependence is a fixed property of the
  cut, while I(A:B)'s residual is a vanishing lattice artifact. Includes a two-probe numerical
  floor audit (1.25×10⁻⁶%, so the sub-percent residual is real, not noise) and one **discarded
  leg left in the file** — an IR-matching attempt built on an effective-mass estimator that is
  biased in 2D, which made the spread worse and was replaced.

- **[`corner_coefficient.py`](qsim/corner_coefficient.py)** — the successor: strips have no
  corners, and in 2D the corner term is the coefficient that is supposed to be genuinely
  universal. On **one** lattice with the **same four regulators**, the area coefficient spreads
  by **36.3%** and stays there under refinement (36.3% → 36.2%), while the corner coefficient
  spreads by **1.7% → 0.2%** — below the method's own measured systematic floor, and consistent
  with exactly zero. **Model-dependence, added after an independent check:** that 1.7% assumes the
  3-parameter model; adding the physically-expected 1/ℓ correction gives **3.3%** instead, and a 1%
  unmodelled contamination moves the extracted coefficient by 7%. So no single-resolution number
  should be quoted as *the* answer. What is robust is the **refinement behaviour** — the spread falls
  under lattice refinement under *either* model, while the area coefficient does not move at all.
  Independently extended by the bridge session to **two further resolutions I never ran** (s=3, L=480
  and s=4, L=640): corner **1.69 → 0.25 → 0.12 → 0.068%** against area **36.26 → 36.24 → 36.23 →
  36.225%**. The corner spread went straight through 0.1% and kept falling, so there is **no floor** —
  the coefficient is universal with no measurable residual, not universal-to-a-tolerance. And it is not
  a numerical artifact: sweeping the symplectic-eigenvalue clip across five decades moves the s=4 spread
  by 3×10⁻⁵ percentage points, **2254× smaller** than the spread itself.
  The law is cleaner than any local exponent: **spread × s² = 1.081 at both s=3 and s=4, agreeing to
  0.15%** — the s⁻² expected from four regulators that agree to O(k⁴). (s=1 is 56% off that constant
  and s=2 is 7.5% off; both lattices are simply too coarse.) Prediction on record for s=5: **0.043%**. Two independent extractions agree (1.7% vs 2.1%); the verdict is unchanged
  at two masses. **One control failed and is kept in the file**: a strip control returned a
  spurious log (B ≈ −0.496), diagnosed rather than explained away — driving ξ/L from 1.79 to
  0.06 sends it to −0.005, confirming finite-size contamination in a badly chosen control
  geometry. It was replaced by rectangle-minus-square, where the corners cancel identically, and
  that control's residual **is** the quoted 4.1% floor.

- **[`corner_angles.py`](qsim/corner_angles.py)** — turning that single point into a **curve**.
  A square lattice can only make 90° corners cleanly, so this moves to a **triangular lattice**,
  where equilateral-triangle regions (three 60° corners) and hexagonal regions (six 120° corners)
  are exact and need no staircase. Prediction registered before running: a(60°) > a(90°) > a(120°).
  **Confirmed** — 0.0242 / 0.0116 / 0.0039, monotone, with a(90°) coming from the *square* lattice,
  so the curve is **lattice-independent as well as regulator-independent**. Across-regulator spread
  is **0.5% at 60° and 1.9% at 120% against 33% for the area coefficient** on the same runs. New
  control that can fail: the area coefficient must not depend on the region's *shape*, and triangles
  vs hexagons agree to **0.03%**.

The transferable lesson, now a standing entry in the family ledger: **when probing whether a
definition is robust, scan the physical regime — the interesting answer is usually a boundary,
not a yes/no.**

## Interactive apps

Self-contained HTML, no build step, no server needed — open the file.

- **[`double_slit_app.html`](qsim/double_slit_app.html)** — the full bench: coherence dial,
  which-path markers, the eraser, Born-sampled dots landing one at a time, live V / D /
  entanglement-entropy meters and duality curve, plus a two-photon delayed-choice mode
  (sort by the partner photon to pull fringes or anti-fringes out of flat noise).
- **[`wave_double_slit.html`](qsim/wave_double_slit.html)** — a live 2-D time-dependent
  Schrödinger solver: watch the packet spread, hit the absorbing wall, slip through the slits
  and build fringes.
- **[`bell_game.html`](qsim/bell_game.html)** — design any classical strategy you like and
  watch it hit the 75% wall, then watch entanglement walk through it (85.4% for CHSH, a
  perfect 100% for GHZ).

## Neural quantum states

[`sims/`](sims) — the machine-learning leg, kept separate on purpose.

- [`nqs_tfim.py`](sims/nqs_tfim.py) — a neural network *as* a wavefunction (variational Monte
  Carlo) finds the transverse-field Ising ground state to ~0.4% of exact at criticality
- [`nqs_phase_transition.py`](sims/nqs_phase_transition.py) — sweeping the field reproduces
  the quantum phase transition
- [`nqs_scaling.py`](sims/nqs_scaling.py) — runs to N = 40 spins (Hilbert space ~1.1×10¹²),
  where exact diagonalization dies around N ≈ 20
- [`nqs_cnn.py`](sims/nqs_cnn.py) — baking translation symmetry into the ansatz buys ~100× in
  accuracy. And a lesson: the plain ansatz got the **energy** right everywhere but the
  **entanglement** wrong in the ordered phase (it spontaneously broke the Z₂ symmetry) —
  entanglement is the stricter probe. Fixed in
  [`stage3_symmetric.py`](qsim/stage3_symmetric.py).

## Running it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install numpy scipy matplotlib mpmath torch      # torch only for sims/
python qsim/weak_measurement.py
```

Each script prints its own verification and writes its figure beside itself. The
high-precision leg (`hinge_mp.py`) needs `mpmath` and takes ~2 minutes.

## What this is not

- **Not new physics.** Everything here reproduces known results. The value is a verified
  instrument and a legible account of *why* each result is what it is.
- **Not a proof of anything speculative.** The hidden-dimension work shows what the idea
  would explain (mass, charge) and what it would cost (unseen particle towers). There is no
  experimental evidence our universe is built that way, and the repo says so wherever it comes up.
- **Honest about limits.** Where a result rests on a convention, a lattice artifact, a
  finite-size effect, or an arbitrary tolerance, that is stated next to the number rather than
  in a footnote. Where a check was impossible at the precision first attempted, the failed
  attempt is left in the file.

## Family

Four sibling projects, cross-validated against each other:

- [**ansatz-machine**](https://github.com/sumit7194/ansatz-machine) — propose → verify →
  evolve, hunting exact solutions of Einstein's field equations. Proved the Kaluza reduction
  used here, dilaton price tag and all.
- [**tabula-geometrica**](https://github.com/sumit7194/tabula-geometrica) — can a neural
  network invent spacetime geometry from raw observation? It discovered *mass* as the hidden
  dimension's latent, and independently replicated this repo's Kaluza–Klein numbers.
- [**DeepStrain**](https://github.com/sumit7194/DeepStrain) — deep-learning searches of real
  LIGO/Virgo data for black-hole signatures.
- [**trivium**](https://github.com/sumit7194/trivium) — the bridge: cross-validating the
  independent projects against one another, which is where several of the probes above came from.

## License

MIT — see [LICENSE](LICENSE).
