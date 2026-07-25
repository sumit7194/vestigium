# Plan: "fields stacked in hidden dimensions — we see the projection"

Four routes to make the idea precise and simulate it. Honest framing for all of them:
none can test whether OUR universe is built this way; they make the speculation exact,
show what it would explain (mass, charge) and what it would cost (unseen particle towers).

## A. Hidden-dimension wave demo (Kaluza–Klein toy)  — qsim  [START HERE]
Simulate a wave in 1 visible dimension + 1 tiny curled-up (periodic) dimension.
- A wave winding n times around the hidden loop behaves, in the visible projection,
  exactly like a MASSIVE particle: E² = k² + (n/R)² → mass m_n = n/R.
- Deliverables:
  1. Dispersion check: measure packet group velocity / oscillation vs winding number n,
     compare against the exact m_n = n/R prediction.
  2. Side-by-side animation frames: n=0 (massless, moves at c, no dispersion) vs
     n=1,2 (heavy: slower, buzzes at rest frequency, packet spreads) — SAME 2D wave,
     different winding; the projection sees different "particles."
  3. The "rest buzz": n≥1 packet at zero visible momentum still oscillates at m_n —
     ties back to our earlier "massive field buzzes at rest" discussion.
- Physics grounding: Kaluza 1921 / Klein 1926; KK tower m_n = n/R is textbook.
- Status: DONE (kk_projection.py, figure kk_projection.png).
  Measured rest-buzz omega for n=1,2,3: 1.0022, 2.0031, 3.0027 (exact: 1,2,3;
  errors 0.09-0.22%). Travel race at same kick k=1: v = 0.999, 0.703, 0.445 vs
  Klein-Gordon exact 1.000, 0.707, 0.447 (errors <=0.66%). The projection of one
  massless 2D wave reproduces the whole massive-particle tower.

## B. Fractal-boundary detector test — qsim
Take the 2D Schrödinger solver (wave_double_slit.html engine or a python port) and
give the absorbing detector wall structured absorption profiles:
- uniform wall vs Cantor-set (fractal) mask vs periodic mask (control).
- Accumulate detection statistics; compare landing distributions.
- Tests the defensible core of the fractal hunch: boundary structure co-decides where
  detections land (mode overlap / Fermi golden rule). No wormholes implied.
- Status: DONE (fractal_boundary.py, figure fractal_boundary.png).
  Results: uniform wall clicks track the fringes (corr 0.97). Periodic vs Cantor
  walls at IDENTICAL coverage (29.6%): click distributions differ strongly from
  uniform (JS divergence 0.34 / 0.44) and from each other; total detection
  efficiency differs by ~67% (0.0373 vs 0.0223) purely from segment PLACEMENT
  relative to the fringes. Fringe positions never move (gated, not shifted;
  corr(detected, incident x mask) = 0.86-0.92), with real edge spikes at segment
  boundaries (diffraction at absorber edges). Verdict: boundary structure DOES
  co-decide detection statistics -- via ordinary wave mechanics; nothing
  fractal-specific or higher-dimensional required.

## C. NN discovery of a hidden dimension — belongs to SpaceTime project (NOT here)
Generate observations from a higher-D field; train a bottleneck network; ask whether
the latent rediscovers the hidden coordinate. SpaceTime already did the KK/charge
version (r ≈ 0.9998) and has "3+1 Kaluza with vector potential" on its open threads.
→ If pursued, do it in the tabula-geometrica repo (github.com/sumit7194/tabula-geometrica), keeping projects separate.

## D. Symbolic proof route — belongs to conjecture_machine (NOT here)
Use the propose-verify-evolve GR engine (already runs in n=3..12 dimensions) to:
1. Verify symbolically: 5D vacuum Einstein with the Kaluza metric ansatz
   ⟺ 4D Einstein + Maxwell (rediscover Kaluza's theorem as a VERIFIED entry).
2. Then let GP hunt variants (different compactifications / extra scalars) and
   catalog which stackings project to which 3+1 physics.
→ If pursued, run inside the ansatz-machine repo (github.com/sumit7194/ansatz-machine).

## Order
1. A (build now)  2. B (next in qsim)  3. D / C in their own projects, on demand.

---

# Next experiments (qsim) — added 2026-07-03

## 1. Continuous weak measurement — watch collapse happen gradually  [TOP PICK]
Quantum-trajectory (stochastic Schrodinger equation) simulation of a monitored
wavepacket. Deliverables: (a) a two-hump "cat" wave under weak monitoring commits
gradually & stochastically to ONE hump — collapse as a process, not a jump;
(b) Born rule EMERGES: fraction of trajectories per hump matches amplitude^2
(70/30 test); (c) conditional variance saturates at the analytic steady state
sigma^2 = 1/sqrt(8k); (d) individual trajectory collapses while the ENSEMBLE
(ignoring the record) decoheres & spreads per the Lindblad prediction — the
"collapse = conditioning on the record" punchline.
Status: DONE (weak_measurement.py, figure weak_measurement.png).
Results: Born rule emerged — 30.6% of 400 runs committed to the 30% hump
(prediction 0.300 +/- 0.024); conditional variance rides the exact Riccati curve
and saturates at 1/sqrt(8k) to 0.2-1.0% for k = 0.0125/0.05/0.2; ensemble
variance matches the Lindblad (decoherence) cubic to 5% (sampling noise).
Note: first run exposed a sqrt(2) Ito-convention bug (exponential update needs
the -2k(x-<x>)^2 dt exponent so the Ito-expanded increment matches the SSE) —
caught by the steady-state check, fixed, all three verifications then passed.

## 2. Decoherence frame-by-frame
Double-slit qubit + ~10-qubit environment, collision model; watch visibility fall,
which-path record accumulate, entanglement rise; partial revivals for small envs.
Status: DONE (decoherence_frames.py, figure decoherence_frames.png). All exact
(13-qubit state vector): V(k) = cos^k(theta/2) to 2e-16; V^2+D^2 = 1 to 4e-16;
path entropy -> 0.9998 bits. Quantum Darwinism: I(S:m) hits 95% of the record at
m=4 of 12 qubits (redundant copying, 1-bit plateau, 2 bits only with the full
env). Revival: a 2-qubit recycled environment returns V to 1.0000 at collision 16
exactly as predicted -- small/held environment = erasable marker; fresh/leaky
environment = effectively irreversible detector.

## 3. Bohmian trajectories from our own 2D solver
Velocity field from the phase gradient -> Philippidis fan / Kocsis-style average
trajectories.
Status: DONE (bohmian_fan.py, figure bohmian_fan.png). Exact analytic two-Gaussian
guiding wave + guidance equation, RK4, 20,000 Born-sampled particles.
Verified: EQUIVARIANCE — the trajectory-endpoint histogram rebuilds the |psi|^2
fringes at the screen to 4.3% of peak (pure guidance, no Born rule imposed at the
end); NO-CROSSING — 0 of 20,000 trajectories crossed the symmetry axis. The
classic fan reproduced: definite one-slit paths bunching into bright fringes,
kinking away from dark ones; same velocity field Kocsis 2011 measured weakly.

## 4. Standard QM vs objective collapse (CSL toy)
Add stochastic localization with N^2 mass amplification; show the fringe-death
signature the Arndt experiments hunt. (Note: math = experiment 1's SSE minus the
detector — build after 1.)
Status: DONE (csl_toy.py, figure csl_toy.png).
Results: momentum fringes full/faded/gone at N=100/700/2500 with k = kappa0 N^2;
measured V(N) rides the analytic exp(-kappa0 N^2 d^2 T) (max dev 0.072 = the
1/sqrt(M) sampling floor at M=200); heavy cat localizes spontaneously in 100%
of runs with NO detector (right-fraction 0.41 vs 0.50, ~2.5 sigma with M=200);
real-units panel reproduces the actual exclusion logic: collapse edge
N* = sqrt(1/(lambda T)) -> Adler edge ~1e5 amu (right at Fein-class experiments,
why it's being squeezed), GRW edge ~1e9 amu (why it's still alive, needs
MAQRO-class). Caveats stated: quadratic/QMUPL small-separation form; strongest
real bounds are non-interferometric.

## 5. Bell/CHSH game, playable
75% classical vs 85% quantum coordination game, small interactive page.
Status: DONE (bell_game.html — self-contained page, same style as the eraser app).
User designs any of the 16 pre-agreed classical plans (live 4-pair win check +
the parity proof of why 4/4 is impossible); quantum team = one Bell pair/round
with the optimal CHSH angles (0/45, 22.5/-22.5). Both teams play the SAME
question stream. VERIFIED live: 40k rounds -> classical 74.56% (ceiling 75%),
quantum 85.30% (theory cos^2 22.5 = 85.36%); flipped plan drops to 24.5%
(= its exact 1/4 pair score); no console errors. No-signaling note included.

## Handoffs
- SpaceTime (Plan C): ANSWERED 2026-07-03 — full success, all gates passed.
  (a) K=1 bottleneck trained ONLY on visible-projection data discovers a single
  latent that orders the winding modes (isotonic R^2 = 1.000; held-out transfer
  R^2 = 0.9999). Forcing design: encoder sees one momentum, decoder must predict
  a DIFFERENT queried momentum -> the only transferable quantity is mass, so the
  net invents "mass". (b) Latent decodes integer n at 100% (clusters 58x spread);
  behavioral mass from inverting the decoder's own dynamics: m_hat =
  [0.055, 1.008, 1.992, 2.957] vs n = [0,1,2,3] (KK tower, spacings equal to 1.8%).
  (c) Sharpened our question: the projection depends on n only via
  omega^2 = k^2 + n^2/R^2, so winding ORIENTATION (+n vs -n) is PROVABLY invisible
  from the brane (bit-identical projections, gap exactly 0.0) — the latent cannot
  be the periodic coordinate; compactness manifests as (i) the quantized equal-
  spacing mass ladder + (ii) that orientation gauge certificate. BONUS: their
  independent FDTD replicated our toy's numbers (rest freqs 1.007/2.003/2.999,
  group velocities <=0.45% of Klein-Gordon) — separate codebases agreeing.
  Their deliverable: SpaceTime/curvature/notes/kk_mass_for_quantum.md +
  results/157_kk_mass_discovery.json (read-only; repos stay independent).
  PHYSICS NOTE for us: the +n/-n invisibility is the toy version of "winding
  direction (charge sign) only becomes observable through gauge coupling" — in
  full Kaluza-Klein, +n and -n couple oppositely to the emergent Maxwell field,
  i.e. they are the particle/antiparticle pair. Our toy has no gauge read-out,
  hence the exact degeneracy. Connects the antimatter-winding thread to the
  KK thread.
- conjecture_machine (Plan D): ANSWERED 2026-07-03 — both stages done, trap worked.
  Stage 1: Kaluza's theorem machine-VERIFIED (battery §111, 95 batteries green):
  5D vacuum Einstein with the Kaluza ansatz ⇔ 4D Einstein–Maxwell–DILATON.
  All coefficients re-derived by symbolic matching over free-function families
  (no textbook constants trusted); identities close to leftover zero; confirmed
  on a second independent family (magnetic monopole A = q cos(theta) dphi).
  THE TRAP: "5D vacuum = gravity + EM with the scalar frozen" → REJECTED, and
  the machine EXTRACTED the obstruction itself: freezing Phi forces F^2 = 0 —
  you cannot freeze the hidden circle's size while the EM field is on (F^2
  sources the dilaton). Boundary case A=0, Phi=1 (black string) → VERIFIED
  (consistent truncation when nothing sources the dilaton — the trap is sharp).
  Stage 2 (enumerated, exhaustive at this lattice): shift on + fibre dynamical =
  Einstein–Maxwell–dilaton VERIFIED; shift on + frozen = REJECTED (same
  obstruction); shift off + dynamical = Einstein + massless scalar VERIFIED;
  shift off + frozen = 4D vacuum/black string VERIFIED. One-line moral: the 5th
  dimension's SHIFT is Maxwell, its SIZE is a scalar you cannot freeze while the
  field is on. Their offer on the table: GP hunt one rung up (6D, two gauge
  fields, twisted fibres) where the ansatz space stops being enumerable.
  Repro: conjecture_machine scripts/111_kaluza_klein.py + _kk_reduce*.py.
- conjecture_machine ROUND 2 (2026-07-03, unprompted follow-through on their
  offer): 6D on T^2, two gauge fields (battery §112, 96 batteries green).
  Full machine-derived dictionary generalizes §111 with cross-couplings
  (each field's Maxwell density weighted by the OTHER fibre's volume; moduli
  gradients mix). HEADLINE — a constraint with NO 5D analogue: the mixed
  fibre-fibre Ricci component (T) = 1/4 Phi1^2 Phi2^2 F1.F2 has nothing to
  absorb it in the diagonal (untwisted) ansatz, so 6D vacuum FORCES F1.F2 = 0:
  two non-orthogonal gauge fields demand a dynamical TWIST. Obstruction map
  (each price machine-extracted): no twist -> F1.F2=0; freeze one radius ->
  that field dies (F_a^2=0); freeze the shape Phi1/Phi2 -> F1^2=F2^2. No
  truncation with two active fields survives the diagonal slice; the only
  consistent islands re-embed the 5D EMD. One-line moral: at one hidden
  dimension EM costs a scalar; at two, non-orthogonal fields also cost a twist.
  Honest note: grid beat GP at <=2 params (they said so); NEXT RUNG OFFERED:
  twisted fibre (chi != 0), where the F1.F2 source gets absorbed into the
  twist's own equation and the (T)-rejected stackings should turn VERIFIED —
  that's where GP earns its keep. Repro: scripts/112_kk6_two_fields.py.
- conjecture_machine ROUND 3 (2026-07-03): TWISTED RUNG CLIMBED (battery §113,
  97/97 green). §112's prediction confirmed exactly: with the off-diagonal
  internal-metric modulus chi(r) dynamical (M = [[Phi1^2, chi],[chi, Phi2^2]],
  parallel electric fields so F1.F2 != 0 — the exact configuration §112
  rejected), R^6(w1,w2) becomes a genuine 2nd-order EOM for chi (chi'' term)
  sourced by F1.F2. REJECTED -> VERIFIED. Frozen-twist limit collapses back to
  §112's bare constraint to the coefficient (the new theory contains the old
  no-go as its rigid limit). WHAT THE TWIST IS IN 4D: the AXION — real part of
  the T^2 complex-structure modulus; (Phi1, Phi2, chi) = volume + complex-
  structure moduli on the standard SL(2,R)/SO(2) axion-dilaton coset (three
  machine checks: chi'^2 kinetic term; 1/det M pole = hyperbolic coset metric;
  EOM source = F1.F2). 4D theory: Einstein-Maxwell(x2)-dilaton + axion on
  SL(2,R)/SO(2) — the generic string-compactification skeleton, machine-derived
  from pure 6D gravity. SHARP CAVEAT (theirs, correctly flagged): this is the
  METRIC axion (parity-even F1.F2 coupling), NOT the theta-term axion (F1^F2
  topological coupling, CP/instanton physics) — that needs a parity-odd
  Scherk-Schwarz/monodromy twist, offered as the next battery. Honesty: proven
  over free-function-of-r family (SymPy wall = general (r,theta)); they caught
  their own arithmetic slip in the coset check (check wrong, code right; fixed
  to the invariant test and re-gated). Repro: scripts/113_kk6_twisted.py.
  OPEN OFFER: the theta-odd twist rung (F^F axion), awaiting the word.

## PROJECTIONS PROGRAM: COMPLETE (A, B done here; C by SpaceTime; D by
## conjecture_machine). The user's "fields stacked in hidden dimensions" idea,
## run through three engines: numerical (mass = hidden winding, <1%), neural
## (an NN discovers mass as the hidden-dimension latent), symbolic (EM = hidden
## shift, PROVEN, with the unavoidable dilaton price tag). Honest boundary
## unchanged: no experimental evidence our universe is built this way.

---

# Round 3 (qsim) — added 2026-07-03

## 6. Quantum Zeno — a watched pot never boils  [BUILDING NOW]
The endpoint of the measurement-strength dial: repeated/continuous observation
FREEZES quantum evolution. (a) Projective: qubit Rabi-flipping |0>->|1>,
interrupted by N measurements: survival = [cos^2(pi/2N)]^N -> 1 as N grows
(Itano et al. 1990 did this with trapped ions). (b) Continuous: our SSE with
monitoring strength k — weak k: wobbly Rabi cycles; strong k: telegraph
dynamics (frozen + rare jumps), with flip rate suppressed as 1/k (Zeno scaling,
fit numerically).
Status: DONE (zeno.py, figure zeno.png). Projective: MC (20k runs) matches
[cos^2(pi/2N)]^N to 0.0055 across N=1..64 (N=64 -> 96% frozen; unwatched -> 0).
Continuous: telegraph dynamics at strong k; flip rate fits k^-0.96 (prediction
k^-1), prefactor within 11% of Omega^2/8k (hysteresis-counting bias). The
measurement-strength dial is now complete: k->0 unitary, k mid stochastic
collapse, k->inf frozen.

## 7. GHZ game — Bell without statistics
Three players, one GHZ state: classical plans cap at 75%, quantum wins 100% —
a PERFECT score, no inequalities needed. Candidate: add as a tab in
bell_game.html.
Status: DONE (bell_game.html now has CHSH + GHZ tabs). User designs any of the
64 classical 3-player plans (live 4-triple check + the parity contradiction);
quantum team measures X (asked 0) / Y (asked 1) on (|000>+|111>)/sqrt2, with
outcomes sampled from the physics (fair individual coins, triple product fixed
by the eigenvalue +1 for XXX, -1 for XYY/YXY/YYX — not hardcoded wins).
VERIFIED live: 40k rounds -> classical 74.77% (ceiling 75%), quantum 100.00%
with ZERO lost rounds; sabotaged plan drops to 25.04% (its exact 1/4 score);
CHSH tab regression clean (75.64%/85.32%); no console errors.
(Mermin 1990; Pan et al. 2000 realized it.)

## 8. Teleportation — collapse + classical channel
Exact qubit sim: teleport an unknown state with fidelity 1 using entanglement
+ 2 classical bits; benchmarks without each ingredient.
Status: DONE (teleport.py, figure teleport.png). 2000 Haar-random states:
full protocol min fidelity = 1.000000000000 (machine exact), outcome probs
1/4 to 3e-16. Bits withheld: Bob's state = I/2 EXACTLY (max dev 4e-16) ->
fidelity 1/2 for every state = constructive no-signaling (Alice's collapse
alone transmits nothing). No entanglement (best measure-and-resend): 0.6706
vs theory 2/3. (Note: the original plan line said "<=2/3 without the classical
bits" — sloppy; 2/3 is the NO-ENTANGLEMENT ceiling, bits-withheld gives 1/2.)
Grounding: Bennett 1993; Bouwmeester 1997; Micius satellite 1400 km, 2017.

## 9. Wigner's friend — measurement relative to the measurer
Friend qubit measures the system inside a sealed lab; outside superobserver can
still interfere friend+system coherently. Outcomes exist relative to who
decohered. The measurement-problem frontier as an exact small sim.
Status: DONE (wigner_friend.py, figure wigner_friend.png). Exact 3-qubit
(S/Friend/Env), leak angle phi. Sealed (phi=0): Wigner interference <X_S X_F>=1
(pure superposition, no absolute outcome), reversal fidelity=1 (Wigner can UNDO
the Friend's measurement), yet Friend's reduced state = I/2 (definite outcome
for the Friend). Leaked (phi=pi): interference=0, reversal=1/2 (outcome locked
in for everyone). Verified: Vwig = cos(phi/2) to 2e-16; Friend's outcome always
definite to 1e-16. Moral: measurement is RELATIVE until decoherence makes the
record irrecoverable. (Wigner 1961; reversible/extended version Proietti 2019.)

### ROUND 3 COMPLETE (#6 Zeno, #7 GHZ, #8 teleport, #9 Wigner). The whole qsim
### foundations lab (Rounds 1-3 + projections A/B + apps) is built & verified.

---

# Bridge round 6 (2026-07-10) — two numerics asks

## Ask 1: 6D twisted tower, direct numerics — DONE (kk6_twisted_tower.py + .json)
Blind protocol honored: integrator = geometry + stencils only (64^2 torus, mixed
d12 stencil); frequencies measured by mode-projection + FFT + parabolic peak;
formula m^2 = (n1^2 - 2 chi n1 n2 + n2^2)/(1-chi^2) scored AFTER measurement.
Results: all 10 sectors within 0.3% (= the predicted 2nd-order stencil
systematic; higher windings BETTER, 0.03-0.07%). Physics signature delivered:
(1,1)/(1,-1) split 0.00000 at chi=0, 0.44867 at chi=0.3 (target 0.44996);
(1,0)/(0,1) degenerate to 6.7e-16. The section-113 axion as a measured spectral
splitting. Multi-route object complete: qsim numerics + ansatz symbolic proof +
bridge's own simulator.

## Ask 2: entropic hinge (Longo identity) on a harmonic chain — IN PROGRESS
S_rel(coherent||vacuum)|wedge vs 2 pi INT x T00. Exact Gaussian S_rel = 1/2 d^T M d
via modular matrix M = 2i Om arccoth(2 i gamma Om).
BUGS CAUGHT (the self-check discipline paying rent):
 1. First Williamson construction FAILED its own symplecticity assert (a2=2.0)
    -> replaced by direct functional calculus (Hermitian eigs only).
 2. OPERATOR-ORDERING bug: arccoth(2 i Om gamma) vs arccoth(2 i gamma Om) —
    the plain thermal self-test CANNOT distinguish them (passes silently);
    caught by working the SQUEEZED one-mode case analytically. Squeezed
    regression test added (passes 2e-16). Lesson for the family: Gaussian
    modular machinery must be regression-tested on a squeezed state.
FLOAT64 VERDICT (honest): ALL swept packets are precision-limited — clip bands
~10-14% because wedge modular weights live in e^-100-scale covariance tails
(nu - 1/2 below float64 resolution). float64 rows are flagged precision_ok:false
in entropic_hinge.json and are NOT a verification.
CERTIFICATION LEG — DONE (hinge_mp.py, dps=60; hinge_mp_certification.json).
VERDICT: Longo identity VERIFIED. Six configs, two chains (N=100 m=0.10 and the
same physical setup on a 1.6x finer lattice N=160 m=0.0625):
  deviations = -0.019/+0.024/+0.169 % (N=100) and +0.018/+0.060/+0.206 % (N=160).
Residual anatomy (honest): rows at ~0.2% are packets whose 4-sigma support ends
exactly ~1 correlation length from the far wedge boundary on BOTH chains
(finite-wedge effect, same size in xi units); clean-geometry rows <= 0.06%.
Meta-lesson delivered to the family: this check is IMPOSSIBLE in float64
(modular data lives in e^-100 covariance tails); dps>=60 required. And the
squeezed-state regression test is mandatory (ordering bug invisible to thermal
self-tests). mp build cost: 22s (N=100) / 90s (N=160).

---

# Bridge ask: is "entropic time" a coarse-graining choice? (entropic_time.py)

Target: Barontini, "Testing the problem of time with cold atoms", arXiv:2509.07745,
Phys. Rev. Research 8, L022047 (2026). Split-BEC (bright/dark sectors, optical
barrier); an "entropic time" built from a coarse-grained entropy of the observed
sector orders events across expansion/recollapse cycles. Operationally the clock
counts bright-sector atoms (entropy per particle ~ 1 => S = Ns tracks N).

M2-species question (definitional robustness): does the constructed time depend on
WHICH coarse-graining you pick? Model: exact two-mode Bose-Hubbard, N=40,
time-independent H, start |N,0>; reduced bright state is Fock-diagonal so the
bright<->dark entanglement entropy = Shannon entropy of P(n) exactly.
Five legitimate clocks from the SAME dynamics: A count <nL> (Barontini's),
B full distribution entropy, C binned (4 and 8 bins), D linear/collision entropy.
Agreement measure: |Kendall tau| (orientation is a convention).

RESULT: SCHEME-DEPENDENT in the weak-interaction regime, ROBUST when interactions
dominate. Numbers:
 - same-family CONTROL |tau|(B, D) = 0.984 -> machinery sound, so divergence is
   structural, not numerical.
 - cross-family |tau|(A_count, B_entang) = 0.181 INSIDE the monotonic-flow window
   (the paper's own domain of validity). Full run: 0.002.
 - STEELMAN 1 (is it just fine wiggles the lab can't resolve?): coarsening the
   event set + smoothing to dt = 0.05..1.6 does NOT restore agreement
   (min|tau| = 0.165, 0.127, 0.133, 0.022, 0.200, 0.333). The disagreement is
   MACROSCOPIC, not sub-resolution.
 - STEELMAN 2 (regime map, the constructive find): min|tau| vs Lambda = NU/2J =
   0.013 (L=0), 0.004 (0.2), 0.165 (0.8), 0.863 (2), 0.990 (4), 0.935 (8),
   0.788 (16). So scheme-robustness switches ON near Lambda ~ 2-4: entropic time
   is a property of the system only when interactions dominate; in the coherent
   Josephson regime it is largely the experimenter's choice.
 - clock reversals in T=40: A_count 12, C_bin4 66, C_bin8 99, D_linear 111,
   B_entang 127 -> quantifies the paper's own "clock stops when flow stops"
   caveat: different schemes stop at different times, so they do not even agree
   on WHEN time is well defined.

FAIR READING (must accompany any relay): real split-BEC junctions are typically
interaction-dominated (large Lambda), i.e. the regime where we find agreement ->
this is CONDITIONAL SUPPORT for Barontini's construction PLUS a mapped boundary,
not a refutation. Honest limits of our probe: two-mode model vs his multimode
trap; no dissipation; we test ordering robustness only (not his effective
Schrodinger equation). Deliverables: entropic_time.json, entropic_time.png.

---

# L9 applied to the family's OWN species-3 label (log_coefficient_boundary.py)

Question: is the entanglement-entropy log coefficient "non-universal" permanently
(R6's standing species-3 label), or non-universal only in a REGIME with a locatable
boundary (the L9 amendment)?

PREDICTION PUT ON RECORD BEFORE RUNNING: universal at criticality, meaningless once
xi << L; control parameter xi/L, NOT the regulator.

Method: transverse-field Ising chain, exact free-fermion / Majorana covariance
(H = (i/4) A_mn a_m a_n, ground state from real Schur canonical form, block entropy
from eigenvalues of Gamma restricted to the block). Open BC, block = leftmost l
sites (single cut) so the CFT target is c/6 = 1/12 with c = 1/2. xi = 1/|1-g|.
Sizes L = 64/128/256/512; g swept to 1 +- 0.002 ... 0.4; even l only (parity
oscillations); fit S vs ln[(2L/pi) sin(pi l/L)].

RESULT — PREDICTION CONFIRMED, with a quantitative boundary:
 - CONTROLS: deep paramagnet S = 7.8e-3 (~0, product state); at criticality the
   fitted coefficient converges to the universal value as L grows:
   ratio to c/6 = 1.034 (L=64), 1.024 (128), 1.012 (256), 1.006 (512).
 - SCALING COLLAPSE: on the disordered branch the fitted coefficient is a function
   of xi/L ALONE — at matched xi/L the spread across different L is <= 0.058 and
   usually <= 0.02 (e.g. xi/L = 0.391: 0.405/0.392/0.386 for L = 128/256/512).
 - BOUNDARY: universal (within 10% of c/6) requires xi/L >~ 2.5; bracketed between
   xi/L = 1.95 (not universal) and 3.13 (universal). Below it the coefficient falls
   smoothly to zero — there is no log to have a coefficient.
 - DEGENERACY AUDIT (honest exclusion): the ORDERED branch (g<1) was excluded on
   physics, not convenience — its ground state is exponentially degenerate
   (lam_min -> 0; e.g. L=512, g=0.9 gave lam_min = 0.0 exactly and a nonsense
   ratio of 15.0), so "the" ground state is undefined and the Schur canonical form
   is ambiguous. 10 of 68 rows excluded, ALL on that branch; disordered-branch
   min lam = 8.9e-3 (safely unique).

READING FOR THE LEDGER: R6's "the log term isn't universal either" is regime-local,
exactly as the L9 amendment predicts. The label should read "non-universal for
xi/L <~ 2.5" — and the corollary for practice: measuring universal subleading
coefficients requires xi/L >~ 2.5, which is a design constraint on the simulation,
not a property of the quantity.

STILL OPEN (predicted, not yet built): the OTHER standing label, M2's area-law
coefficient kappa. Prediction on record: no switch-off in any regime (the leading
coefficient counts short-distance correlations at the cut, so it inherits the
regulator everywhere) BUT the boundary exists in a different direction — the
cutoff-free combinations (mutual information, relative entropy) are UV-finite
because the divergences cancel. That is the same mechanism that made the Longo
check work at 0.05% where the bare entropy is infinite. Needs 2D (in 1D the
"area" is two points, so kappa is not visible).
Deliverables: log_coefficient_boundary.json, log_coefficient_boundary.png.

---

# Bridge 2D build: kappa vs I(A:B) (kappa_vs_mutual_info.py)

Species-2 prescription ("change channel") applied to a species-3 wall. Bridge R8
established kappa is regulator-contaminated in EVERY regime (51.2% at m=0, 67.4%
gapped). So: is the nearby quantity I(A:B) regulator-free, and does the physics
survive there? Bridge's decisive spec: both on the SAME 2D lattice across the SAME
>=3 regulators, both spreads reported.

SETUP: free scalar, periodic LxL, Gaussian ground state, exact symplectic entropy.
FOUR regulators sharing the continuum limit m^2+k^2 (verified to 1e-6..1e-10 at
small k) but differing at k~pi: nn, improved (4th-order stencil), higher_deriv
(+0.25 K2^2), smeared (K2 exp(0.15 K2)). Geometry chosen so boundary bookkeeping
is exact: kappa from the SLOPE of S vs L for half-torus strips (projects out the
subleading constant); I(A:B) from two parallel strips (|bd A|+|bd B| = |bd(AuB)|
exactly, so every area term cancels).

RESULT — prediction confirmed:
 - kappa spread 41.6% (bridge R8: 51.2%; same order, different geometry/reg set),
   area law linear to R^2 > 0.9994 for every regulator.
 - I(A:B) spread 24.89% at g=1 (touching, no cancellation) falling to 0.25% at
   g=8 — a 165x suppression.
 - NUMERICAL FLOOR AUDIT (two independent probes: clip sweep over 4 decades, and
   a SECOND algorithm for the symplectic spectrum via sqrt(P)X sqrt(P) instead of
   sqrt(X)P sqrt(X)): floor = 1.25e-06 %. So the sub-percent residual is REAL,
   five orders above numerics — which is what the bridge flagged as needing care.
 - DECISIVE CONTINUUM SCAN (needs no xi measurement): hold physics fixed
   (m*L = 3.2, w/L = 1/16, g/L = 1/8), refine the lattice s = 1,2,3,4:
   I(A:B) spread = 2.178 / 0.336 / 0.165 / 0.096 % ~ s^-2.26, exactly the ~s^-2
   expected for regulators differing at O(k^4). I itself converges (0.09554 ->
   0.09563). So I(A:B) IS regulator-free in the continuum limit.
 - SYMMETRIC CONTROL (the contrast, made airtight): the SAME refinement leaves
   kappa's spread at 41.8% (s=1 physics) -> 41.7% (s=4 physics). Unmoved.

VERDICT for the ledger: kappa's regulator dependence is a fixed property of the
cut that no refinement removes; I(A:B)'s apparent residual is a vanishing lattice
artifact. "Change channel" works — the physics wanted from kappa survives in a
quantity that has a continuum limit.

DISCARDED LEG, left in the file on purpose: an attempt to IR-match the regulators
by tuning bare masses to equalise an arccosh effective-mass estimate of xi. The
estimator assumes a pure cosh correlator; a 2D correlator has a power-law
prefactor, so it read xi_eff = 7.98 where m = 0.05 implies ~20. Tuning to
equalise a biased quantity made the spread WORSE (0.336% -> 0.855% at g=8). The
continuum scan replaced it and needs no xi at all.

CAVEATS: single field theory (free scalar) and one universality class; strip
geometry only (no corners, so no corner-log contribution tested); Gaussian states
only; the four regulators all differ from each other at O(k^4) by construction, so
s^-2 is the expected rate and a regulator family differing at O(k^2) would decay
slower.
