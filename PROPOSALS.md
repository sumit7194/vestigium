# Proposals — hypotheses this repo could test next, with the sisters

Written 2026-09-05 after a review of this repo's history and a capability-level
inventory of the four sibling projects (instruments and interfaces, not their
results). **Nothing here has been run.** Each proposal is stated with its controls,
its falsifiers, and — following thebridge's technique — the specific way it is
expected to fail, named before anything is computed.

Where this repo stands, in one line: the founding question ("when does a quantum
possibility become a fact?") got a complete verified lab on 2026-07-26 and has been
dormant since 08-22; everything after that is entanglement/corner physics and
verification instruments. The instrument that transfers most directly to a sister's
named open problem is the **secular-average lemma** (`qsim/lrl_secular.py`),
validated in both directions on Kepler/LRL on 09-02.

---

## H1 — First-order rigidity of hidden symmetry under deformations of Kerr  ★ primary

**Sister hook.** ansatz's `scripts/82_integrability_frontier.py` leaves "deformed-Kerr
integrability fate" **UNDETERMINED**; its symbolic Killing-tensor search on a
deformation swamped (7.5 h, no output, `85_no_carter_under_deformation.py`), and it
fell back to numeric SVD null-space fitting over sampled geodesics. ansatz has exact
"bumpy" metrics (Manko–Novikov, Zipoy–Voorhees), a Lyapunov harness and a Poincaré
box-dimension harness. thebridge's hidden-symmetry workspace was killed this week by
Kubizňák–Krtouš 2008 (a principal conformal Killing–Yano tensor alone forces type D,
separability and geodesic integrability, field equations not needed).

**The lemma, transferred.** For `H = H₀ + εH₁` with `H₀` integrable (Kerr) and `K`
the Carter constant, `K` survives to first order **only if** the torus average
`A(E, L_z, Q) = ⟨{H₁, K}⟩` vanishes on every bound-orbit torus. On non-resonant tori
the long-time average along one geodesic equals the torus average, so the
time-route of `lrl_secular.py` applies without closed orbits. `A ≠ 0` on an open set
**proves** destruction; `A = 0` proves nothing (necessary only). `H₁ = ½ δg^{μν} p_μ p_ν`
for a metric deformation, quadratic in momenta like `K`, so `{H₁, K}` is explicit.

**Hypothesis.**
(a) *Rigidity inside the family:* for every deformation that stays inside
Kerr–NUT–(A)dS, `A ≡ 0` identically over the whole bound-orbit space.
(b) *Fragility outside it:* for Manko–Novikov and Zipoy–Voorhees, `A ≠ 0` on an
open set of `(E, L_z, Q)`, and the set where `|A|` is largest coincides with where
ansatz's Lyapunov/box-dimension harness sees chaos first.
(c) **The new part** — *higher-rank symmetry is more fragile than rank 2:* for ansatz's
newly found 4D Lorentzian vacuum with an **irreducible rank-3 Killing tensor**
(`high_rank_killing`, imported to conjecture_machine 09-05), a generic small
deformation gives `A ≠ 0` for the cubic invariant on an open set, while the Kerr
rank-2 Carter tensor survives the corresponding in-family deformations. Nobody has
a secular map for a rank-3 invariant; the solution is weeks old.
(d) *The validity window is a map, not a number:* the bounded-`F₁` hypothesis found in
the LRL work (`LRL_FINDINGS.md`) becomes a **small-divisor** condition here: near
low-order resonant tori `ω·k ≈ 0`, `F₁` is unbounded even when `A = 0`. The
deliverable is `A(E, L_z, Q)` **together with** the window in which first-order
reasoning is trustworthy — the same two-condition discipline as `R ≪ ξ ≪ L`.

**Controls (all three, as in the LRL task).**
- TRIVIAL: Kerr → Kerr with `M → M+δM` or `a → a+δa` (reparametrisation inside the
  family). `A ≡ 0` to machine precision, while `{H₁, K}` is nonzero pointwise. *If this
  returns nonzero the instrument measures the parametrisation, and every other number
  is worthless.*
- NEGATIVE: Kerr → Kerr-NUT (small NUT charge) and Kerr → Kerr-(A)dS (small Λ). `A ≡ 0`.
- POSITIVE: Kerr → Manko–Novikov `q ≠ 0`; Zipoy–Voorhees `δ ≠ 1`. `A ≠ 0` on an open set.

**Cross-oracle structure (three routes, one object).**
1. quantum: first-order `A` map, minutes per deformation, CPU-light.
2. ansatz: numeric SVD null-space search for a surviving quadratic/cubic invariant at
   *finite* `ε` — their existing tool, on the same metrics.
3. ansatz/bridge: Lyapunov + box-dimension, dynamical.
Handoff by npz through thebridge's leg format so routes 2–3 never see route 1's map
before running (**blind by mechanism, not by promise** — this repo's own disclosure
ledger shows why that distinction matters).

**Falsifiers.**
- (a) fails → the generalisation is broken, or the NUT/Λ deformation was not
  actually in-family as parametrised. Instrument error until proven otherwise.
- (b) `A ≠ 0` but SVD finds a surviving quadratic invariant at finite `ε` → the
  perturbation is outside the class the lemma assumes, or the window closed. Either
  is a finding about the lemma.
- (c) `A ≡ 0` for the rank-3 invariant under generic deformation → higher-rank
  symmetry is *rigid*, H1(c) is false, and that is the more interesting outcome.

**Named ways this is expected to fail (pre-registered hazards).**
1. **A parity zero.** Kerr has `θ → π−θ` reflection symmetry. A deformation odd
   under it gives `A = 0` *by symmetry* regardless of physics — the exact analogue
   of `A_x ≡ 0` for central perturbations in the LRL work. Rule: any `A = 0` result
   ships only with the finite-`ε` SVD check attached; a bare zero is not a result.
2. **Resonant tori.** The time average along a resonant geodesic is an orbit average,
   not a torus average, and is *stricter*. Sample tori by frequency ratio, exclude
   low-order resonances from the `A = 0` claim, and report them as the window's edge.
3. **The trivial control passing for the wrong reason.** `M → M+δM` changes `K`'s
   normalisation too; `A` must be computed for the *correctly co-varied* `K`, or the
   control tests the bookkeeping. Check: the control must pass with `{H₁,K}`
   pointwise nonzero by O(1), not because the bracket vanished.
4. **Sign.** `A` as the lemma defines it is **minus** the secular rate
   (`dK/dt = −ε{H₁,K}`). Established once already; will be re-established.

**Cost.** Implementation ~1 day (general-n phase space, Kerr geodesics in Mino time,
Carter `K(x,p)` explicit, deformations as `δg^{μν}`). Runs: seconds per orbit,
hundreds of orbits per deformation, a few families — CPU-light, announced through
`preflight.py`, and **not before ansatz's 12-hour job finishes**.

**Honest scope.** "Which deformations of Kerr keep a Carter-like constant" is
partially charted (Johannsen-type metrics keep one *by construction*; that is a
sufficient condition). What is uncharted: the necessary-condition map over orbit
space, the validity window, and ansatz's rank-3 solution. The instrument is new to
the question; the question is not new.

---

### H1 REVISED 2026-09-21, after asking ansatz rather than reading them

Everything below this line comes from what ansatz told me directly. I did not open
their repo. They deliberately withheld their deformation basis and which members
survive — **echo hazard**: if they hand me their answer and I confirm it, I am
checking their arithmetic, not the physics. Any cross-check runs with both sides'
verdicts written down first and compared afterwards through the bridge.

**What they hold, with the scope line they attached.** A characterisation, not a
null: *keeps Carter ⟺ separable in the Benenti–Francaviglia sense, modulo gauge*,
both directions measured. But it holds **inside a finite, explicitly parametrised
family** (fixed angular patterns × fixed radial profiles), **first order** in the
deformation, **truncated at O(χ²)** in spin. It is not a theorem about all
deformations of Kerr.

**So the original H1 target is dead and a better one replaces it.** Inside their
family a first-order necessary condition is *strictly weaker* than the iff they
already have — I would be recovering one direction of their own result. Their
words: not worth the time. **Outside it they have nothing**, and Kerr-NUT,
Kerr-AdS and Manko-Novikov are not in their basis and cannot be expressed in it.

**The three places a cheap necessary condition is not redundant**, in their ranking:

1. **The resonant neighbourhoods.** Their method is algebraic and exact and says
   nothing about dynamics — it cannot see a resonance, a small divisor or a torus.
   If the verdicts agree everywhere *except* near low-order resonances, that residue
   is a new object neither method could have found alone. **The validity region is
   the deliverable, not the verdict inside it.**
2. **Deformations outside any polynomial ansatz.** Their search is over polynomials
   in the momenta — a restriction they had never written down as one until it bit
   them. A secular average does not care whether the conserved quantity is
   polynomial, so it covers a hole they recently learned they had.
3. **Exact solutions rather than truncations.** Theirs is O(χ²)-truncated and solves
   no field equation exactly; Kerr-NUT and Kerr-AdS are exact. A first-order
   statement about an exact solution and an exact statement about a truncation are
   **incomparable**, which is worth something on its own.

**Deliverable they asked for**, and it is narrower than what I proposed: the **open
set where `A ≠ 0`**, its validity region, and **explicitly the boundary** — the set
where `A = 0` and the method is silent. *Not* sign and magnitude over `(E, L_z, Q)`;
they have no way to use that and it invites over-reading. The boundary is where the
two methods can actually be compared.

**Correction to my rank framing, which survives with a check bolted on.** I had
treated a rank-3 Killing tensor as a rarer *independent* symmetry. What they measured:
Carter can die as a **polynomial** tensor and survive as a **rational** first
integral, whose powers then reappear as polynomial tensors at higher rank — so rank
was measuring the **pole order of one quantity**, and saturated. They are explicit
that this is *not* a theorem, only what happened in the cases examined, and is now a
mandatory check in their repo. **So the question "is higher-rank symmetry more
fragile" is not wrong; assuming the rank-3 object is independent is.** The fix is the
check — divide out powers of lower-rank rational integrals and see whether the
quotient solves the lower-rank equation — not abandoning the question.

**Control correction, and it costs me a "result".** I had listed **Zipoy–Voorhees as
a positive control**. It is **closed at every rank** — no additional meromorphic
first integral of any kind — in print since **2013** (Maciejewski, Przybylska &
Stachowiak, *PRD* **88**, 064003, via Morales-Ramis theory). So ZV stays as a
control with a *known* answer my instrument must reproduce, and is **not** a result.

> **Note the shape of how they missed that paper for thirteen years**: it says "first
> integral" and "Liouville" and never "Killing tensor". That is a **vocabulary** miss,
> not a reasoning one — the same class as my own cusp/corner miss recorded in
> `corner_function/PROVENANCE.md`, where the right literature was excluded because it
> used a different word for the same object. Two independent instances in one fleet,
> found six hours apart.

**Revised falsifier for the whole exercise:** if my verdicts agree with theirs
everywhere *including* near resonances, the instrument has added nothing beyond a
weaker rederivation, and H1 should be closed rather than written up.

## H2 — A pre-registered number for tabula's mass sweep  ★ RAN 2026-09-21 → NOT COMPARABLE

**Outcome: the correspondence check fired and no grade applies.** Blinding held
(their prereg and my seal both predate their number; they had read access here and
did not use it). Their setup used an *absolute* interval band at one system size,
so the `ξ/L` collapse that licenses quoting a single ratio was never established on
their side — and their instrument declined to produce the quantity anyway, since `ξ`
came out ~7.7× the box while being fitted inside `r ≤ N/4`. **The prediction remains
sealed and live.** Full scoring in [PREREG_xi_star.md](PREREG_xi_star.md).



tabula's J5 builds a kinematic-space metric from single-interval entropies `S(u,v)`
on a ring and reads the central charge off its Gaussian curvature; they reported
(via thebridge) that their criticality gate was a single gapped point, and are now
sweeping the mass to locate where constancy fails.

**Prediction, filed before their sweep lands.** Constancy of the curvature fails
where the direct log fit stops being universal: the composite threshold this repo
measured on the Ising chain, **`ξ/L ≈ 2.5`** (bracketed 1.95–3.13,
`log_coefficient_boundary.json`). Their chain, like mine, locks region scale to `L`,
so the composite (not the separated `R ≪ ξ` / `ξ ≪ L` pair) is the right variable.
Free-fermion `c=1` versus Ising `c=½` should not move it if the threshold is
kinematic rather than theory-dependent — **that** is the content; a `c`-dependent
threshold is the falsifier.

Cost: zero on my side beyond filing the number; it should go to thebridge as a
sealed prediction so it cannot be tuned after their sweep reports.

---

## H3 — The founding question, if it is to be resumed (not sister-testable)

Two halves of this repo have never been joined: the decoherence/Darwinism lab
(`decoherence_frames.py`: 4 of 12 environment qubits already hold 95 % of the
record) and the exact critical-chain entanglement machinery
(`log_coefficient_boundary.py`). Every Darwinism result here uses a *gapped* toy
environment.

**Hypothesis.** In a **critical** (gapless) environment the redundancy `R_δ` of a
record — how many disjoint environment fragments each carry the outcome — grows with
a **logarithmic correction whose coefficient is fixed by the central charge**, the
same `c/6` that governs the block entropy. If so, "how fast a possibility becomes a
fact" carries a universal number, and it is the one this repo already knows how to
measure. Falsifier: no log term, or a coefficient that moves with a non-universal
parameter at fixed `c`.

Testable entirely inside this repo (free-fermion Ising environment coupled to one
system qubit; exact). It is the only item here that touches the founding question.
It is offered separately because the user asked for something the *sisters* can test,
and no sister has a decoherence instrument.

---

## Not proposed, and why

- Anything routed through deepstrain's ringdown/no-hair `δ`: H1's deformation families
  do change QNM spectra, but the link from "loses a Carter constant" to "measurable
  `δ`" runs through waveform modelling no one here has. Downstream, not now.
- More `m → 0` on `a(120°)`: the fit model dominates the residual by 15.5×; the axis is
  converged. Recorded 09-04.
- The fifth out-of-family regulator: still the right test for the bulk-coupling
  residual, still unrun, but it is a within-repo item with no sister route.
