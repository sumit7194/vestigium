# qsim — a quantum foundations laboratory, built in small verified steps

A from-scratch collection of exact quantum simulations, interactive apps, and
verified foundations experiments. House rules: **quantum properties live as
structured latent factors** (tensor product; entanglement = the part that won't
factorize), every build is **checked against exact analytics or real
experimental numbers**, and the neural network only enters where it earns its
keep. Grew out of a long grounded conversation working from the double slit to
the measurement problem.

Runs on the venv in `../sims/.venv` (Python 3.13 + torch/MPS):
```
PYTHONWARNINGS=ignore ../sims/.venv/bin/python <file>.py
```
Interactive apps are self-contained HTML — double-click, no server needed.
(A preview config exists: python http.server on port 8777, `.claude/launch.json`.)

---

## The staged simulator (states, entanglement, scale)
- **`stage0_polarization.py`** — one property as a latent: the Poincaré sphere,
  operations as rotations, Born sampling; verified vs Malus's law (45° → 0.5).
- **`stage1_entanglement.py`** — path ⊗ polarization; the marker *entangles*
  (S: 0 → 1 bit as tags go orthogonal, complementary to V = cos θ); the 45°
  eraser disentangles (S → 0, fringes back at 50% light).
- **`stage2_bell_eraser.py`** — two-photon Bell state; singles flat (no
  signaling, to 1e-15), coincidence fringes/anti-fringes, far analyzer dials
  near visibility as |sin 2φ|; delayed choice = order-independence.
- **`stage3_entanglement_at_scale.py` / `stage3_symmetric.py`** — the CNN
  neural quantum state holds many-body entanglement (SVD of amplitudes): area
  law vs critical growth; plain ansatz got energy right but entanglement wrong
  (spontaneous symmetry breaking) — fixed by baking Z2 symmetry in.
- **`bench.py`** — the composable exact engine
  (`DoubleSlit().source().mark().analyzer().visibility()`), self-testing.

## Interactive apps
- **`double_slit_app.html`** — the full bench: coherence dial, markers, eraser,
  Born-sampled dots, live V/D/entanglement meters, duality curve; plus a
  two-photon delayed-choice mode (sort by partner: fringes/anti-fringes).
- **`wave_double_slit.html`** — live 2-D Schrödinger solver: watch the packet
  spread, hit the absorbing wall, slip through the slits, build fringes.
- **`bell_game.html`** — playable CHSH: design any classical plan (capped 75%,
  with the parity proof) vs an entangled pair (85.36%); verified live.

## The projections program (PLAN_projections.md) — COMPLETE
The "fields stacked in hidden dimensions; we see projections" idea, run through
three engines:
- **A `kk_projection.py`** (numerical, here): mass = winding around a hidden
  loop; KK tower 1:2:3 to ≤0.7% — independently replicated by SpaceTime.
- **B `fractal_boundary.py`** (here): detector-wall structure gates clicks
  (67% efficiency swing at equal coverage) but never moves fringes.
- **C** (neural, SpaceTime project): a bottleneck net shown only projections
  *invents mass* and decodes the winding integer (their §157).
- **D** (symbolic, conjecture_machine): Kaluza's theorem machine-proven — 5D
  vacuum ⇔ 4D Einstein–Maxwell–**dilaton**; the "no scalar" shortcut REJECTED
  with the obstruction extracted (freezing the circle's size forces F² = 0).

## Foundations experiments (Round 2 — all verified)
- **`weak_measurement.py`** — collapse as a *process* (stochastic Schrödinger
  equation): a 70/30 cat commits gradually; **Born rule emerges** (30.6% vs
  30%); conditional variance rides the Riccati curve to V_ss = 1/√(8k);
  individual runs collapse while the ensemble decoheres (Lindblad-exact).
- **`decoherence_frames.py`** — 13-qubit collision model, machine-precision:
  V = cos^k(θ/2), V²+D²=1 throughout; **quantum Darwinism** (4 of 12 qubits
  already hold 95% of the record); **revival** at collision 16 with a recycled
  2-qubit environment — marker vs detector, quantified.
- **`bohmian_fan.py`** — pilot-wave trajectories from the guidance equation:
  the Philippidis fan; equivariance (20k paths rebuild Born fringes, 4.3%);
  0 axis crossings in 20,000.
- **`csl_toy.py`** — objective collapse (SSE minus the detector, k = κ₀N²):
  fringe death with size, V = exp(−kd²T) verified; real-units exclusion plot
  (Adler edge ~1e5 amu at Fein-class experiments; GRW ~1e9 amu → MAQRO).

## Classical-wave & reference figures
- **`diffraction_shapes.py` / `diffraction_quantum.py` / `diffraction_marked.py`**
  — aperture progression (slits → ring → disc): classical patterns, the same
  patterns dot-by-dot (Born), and with which-path markers (cross-term killed).
- **`config_space.py`** — why entangled particles live in configuration space
  (the diagonal blob that won't factor).
- **`matter_antimatter.py`** — same wave, opposite internal winding; annihilation
  as field-to-field energy handoff.

## Sibling work (kept separate on purpose)
`../sims/` — the NQS/VMC proof-of-concept (TFIM ground states, phase transition,
beating exact diagonalization at N=40, symmetry-aware CNN 100× accuracy).
SpaceTime and conjecture_machine are independent repos; exchanges happen via
written asks (see PLAN_projections.md "Handoffs").

Two independent runs agree, which confirms the result.
