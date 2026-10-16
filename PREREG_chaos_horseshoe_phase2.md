# Pre-registration: chaos-proof phase 2 (B-5), a computer-assisted horseshoe for Manko–Novikov geodesics

*Quantum, 2026-10-16. DRAFT for the Bridge's agreement. Written BEFORE any phase-2 output: no control and no target
run has been made. Until the Bridge agrees, I write and compile code only; nothing registered below is run.*

**Decision (the user's, relayed by the Bridge on 2026-10-16).** Target B-5 (`TheBridge/fleet/MOONSHOT_REVIEW_2026-10-16.md` §1).
Manko–Novikov (MN) is the first target, Tomimatsu–Sato δ=2 (TS) the second. Quantum owns it.
Literature basis: `TheBridge/outreach/paper_ts_mn/LIT_SWEEP_chaos_proof.md` (2026-10-15).

**Scope of this document.**
- Rung 1: this registration.
- Rung 2: the three controls, registered in full here.
- Rung 5: the MN horseshoe, registered here up to the choices that need K20's output. Those choices are named, and
  each one must be fixed by an amendment committed BEFORE the run it governs.
- Not covered here: TS (rung 5b) and the Majumdar–Papapetrou warm-up (rung 4). Each gets its own amendment or
  registration.

---

## 1. Claim if it succeeds, stated now

> For the MN q-anomaly metric at parameter point P = (M, a, q), timelike geodesics with conserved E and L_z, the
> Poincaré return map 𝒫 (or an iterate 𝒫ⁿ) on the section Σ has h-sets N₁,…,N_k ⊂ Σ ∩ D. These sets satisfy
> certified covering relations N_i ⟹ N_j for every A_ij = 1, where A is a 0/1 transition matrix with spectral
> radius ρ(A) > 1. So there is a compact invariant set on which 𝒫ⁿ is semi-conjugate to the subshift of finite type
> (Σ_A, σ), and the topological entropy of 𝒫ⁿ is ≥ log ρ(A) > 0. Every orbit used stays, with a certificate, in the
> physical domain D (§3.4).

**What the claim rests on.**
1. CAPD 2f06098 with MPFR intervals, under `proof_guard.h`. The pins and trust checks are already done:
   `qsim/capd/PINS.md`, `DIFFCHECK.md`, `NAN_SAFEGUARD.md`, `ODE_CONTROLS.md`.
2. The topological covering-relation theorem, which is cited and not reproved. Before any claim is written, I read
   the theorem's exact statement in full text, from Zgliczyński–Gidea 2004 (JDE 202, 32) or from the CAPD::DynSys
   paper (arXiv:2010.07097), which states the version it uses. I record the hypotheses verbatim in the result file
   (action item T0, §5). If a hypothesis cannot be matched to a certified check, the claim is not made.
3. The second implementation (§4) agreeing.

**What it is NOT.**
- Not "MN geodesics are chaotic" in general. The claim holds only at the stated P, E, L_z and region.
- Not a statement about TS.
- Not a strict-limit fractal claim.
- Not a formalised proof of the topological theorem.

---

## 2. Success criterion (rung 5, MN), all required

| # | Check | Certified how |
|---|---|---|
| S1 | **Section and return.** 𝒫ⁿ is defined and continuous on every N_i: each orbit from N_i reaches Σ transversally (ẏ ≠ 0 as an interval, of the registered sign) after the registered number of crossings, with a finite, enclosed return time. | CAPD `PoincareMap` on MPFR intervals; transversality from the enclosure of ẏ at the crossing |
| S2 | **Covering inequalities** for every A_ij = 1, in each h-set's local coordinates (u, s) ∈ [−1,1]² (u unstable, s stable): (a) \|s(𝒫ⁿ(N_i))\| < 1 within N_j's frame; (b) 𝒫ⁿ(N_i^{l}) ⊂ {u_j < −1} and 𝒫ⁿ(N_i^{r}) ⊂ {u_j > 1}, or the reverse (degree ±1), for the left and right edges. This is the form of CAPD's Rössler example. | every inequality decided by interval comparison, no tolerance |
| S3 | **ρ(A) > 1.** | exact integer arithmetic: an exhibited n with trace(Aⁿ) ≥ 2 and a cycle structure that gives ρ > 1; ρ also computed exactly as an algebraic number |
| S4 | **Physical domain:** every CAPD step enclosure of every orbit segment used lies in D (§3.4). | interval evaluation on every step enclosure (not on a grid), fail-closed |
| S5 | **Exact field gate:** my Hamilton's equations equal the Bridge's independently derived ones, exactly (in the differential field with R and the exponentials as symbols, as in `replay_gate.py` mn_eq). | exact rational polynomial identity |
| S6 | **Second implementation** (§4) certifies every covering inequality in S2 and every S4 check, with overlapping enclosures and no opposite certain decisions. This is the MR cross-path rule. | separate run, separate code path |
| S7 | **Controls passed first:** Rössler PASS, Hénon–Heiles registered outcome recorded, Kerr shows no ρ(A) > 1 (§6). A Kerr certification stops everything. | §6 |

If S1–S7 all hold, the claim in §1 is made exactly as worded. If any one fails, no horseshoe claim is made, and the
failing check is reported with its numbers.

---

## 3. Fixed set-up

### 3.1 Metric

- **Source.** The MN q-anomaly subclass exactly as supplied in `conjecture_machine/data/MN_for_quantum/MN_METRIC.md`,
  read-only. Coordinates are (t, x, y, φ), prolate spheroidal.
- **Parameter points.** Primary: the two points already certified non-integrable by the MR tool,
  p1 (M, a, β) = (5, 3, 1/5) and p2 = (13, 5, −1/3).
- **Fallback point.** If K20 finds no usable chaotic sea at p1 or p2 (failure mode F5), the target may move. One
  candidate is near the literature's point, χ = 0.9, q = 0.95 (Lukes-Gerakopoulos et al. 2010), with rational
  k and α. Such a move needs an amendment committed before any run there. It also leaves a gap: a horseshoe at the
  new point would no longer sit on a Morales–Ramis certificate. The write-up must say so, or the MR tool must be run
  at the new point first.

### 3.2 Hamiltonian and reduction

- **Hamiltonian.** H = ½ g^{μν} p_μ p_ν = −½ (timelike, μ = 1). p_t = −E and p_φ = L_z are fixed, with E and L_z
  rational.
- **Reduced system.** 2 degrees of freedom: H_red(x, y, p_x, p_y) = ½(g^{xx} p_x² + g^{yy} p_y²) + V(x, y; E, L_z) = −½.
- **Time reparametrisation.** I may multiply the vector field by a factor λ(x, y) that is certified > 0 on D, for
  example to clear the (x² − y²) and (x² − 1) denominators. This changes neither the orbits nor 𝒫. λ is fixed by
  amendment before the MN runs, and the field gate S5 is applied to the reparametrised field.
- **Expression form.** Metric functions are evaluated as a DAG of shared nodes: R, the exponentials, A, B, C, then
  f and ω. They are not expanded into one polynomial; the MR work showed that expansion costs about 1e5 in
  cancellation (the dependency problem).

### 3.3 Section

- **Section.** Σ = {y = 0, p_y > 0} ∩ {H_red = −½}, with coordinates (x, p_x). p_y is recovered from the constraint
  by the positive square root, whose radicand is certified > 0.
- **If K20 finds the equatorial section unsuitable,** for example because the sea's orbits do not cross it
  transversally, another section may be registered by amendment before use. Equatorial reflection symmetry is not
  assumed anywhere.

### 3.4 Physical domain D (Han 2008's exterior check, adapted to vacuum MN)

Each condition below is certified on every step enclosure:
- (a) x − 1 ≥ δ_x, where δ_x = 0.10 at p1 and 0.15 at p2. This lies beyond the measured CTC regions: x < 1.075 at
  p1 and x < 1.122 at p2.
- (b) g_φφ > 0: no closed timelike curves.
- (c) R² = x² + y² − 1 ≥ 0.25, which is well outside the measured singular neighbourhood (R ≈ 0.22).
- (d) 1 − y² ≥ δ_y > 0. For L_z ≠ 0 this should hold automatically, because of the centrifugal barrier; it is
  certified, not assumed.
- (e) Every metric function is finite and B > 0 (`require_finite`, `certainly_positive`).
- (f) The Lorentzian signature holds: det g < 0 is certified.

The ergoregion (f < 0) is allowed, because it is physical. Orbits that leave D are treated as plunging, and an
h-set whose image leaves D is rejected; covering relations only need 𝒫 on N_i.

### 3.5 Engine and trust (unchanged from the third replay)

- CAPD 2f06098, MPFR only: `proof_guard.h` poisons the non-MPFR types, and `check_proof_object.sh` runs the nm check
  and the formula ban.
- Inputs are enclosed from exact rationals.
- Runs are checkpointed and keyed by the sha256 of their input.
- Runs are deterministic: a repeated run must be bit-identical, and this is spot-checked on one covering relation
  per target.

### 3.6 Resource ladder (the most a run may use before it counts as "not certified within budget")

| Setting | Allowed values |
|---|---|
| MPFR precision | 128 → 256 → 512 → 1024 bits |
| Taylor order | ≤ 40 |
| Edge and interior subdivision | ≤ 2¹² pieces per h-set edge and ≤ 2¹⁶ interior boxes per covering relation |
| Iterate | n ≤ 4 returns |

- **Compute budget:** at most 4 cores at nice +19, and at most 14 days of wall time for the first MN attempt at
  one point.
- **An exhausted budget is reported as "not certified within budget"** (F1–F3). It is NEVER a statement about the
  dynamics.

### 3.7 h-set construction (one automated procedure, the same for HH, Kerr and MN)

1. **Seeds.** Start from hyperbolic periodic points of 𝒫ⁿ, found numerically (double precision is allowed here,
   because the seeds are not part of the proof). For MN the seeds come from K20; for HH and Kerr, the same finder
   is run on their own sections.
2. **Frames.** Each h-set is a parallelogram aligned with the numerical eigenvectors of D𝒫ⁿ at its seed, with
   half-widths chosen by the registered rule: the unstable half-width is the largest one that keeps the edge images
   outside the target band, scanned on a fixed grid of 16 values, and the stable half-width is the largest of 0.25, 0.1 or 0.05 times the
   unstable one that keeps the image inside the stable band. The rule is applied identically to every system.
3. **Transition graph.** Candidates come from numerical images of the edges. Only certified edges enter A.

The constructor is frozen (by its commit hash) before the first Kerr run. If any of it changes later, every control
is re-run.

---

## 4. Second implementation (required for MN, optional for the controls)

As in V8/V9, the Bridge independently replays every covering relation and domain check. The minimum is:
- an independent derivation of the reduced Hamiltonian from the metric, gated exactly against mine (S5);
- the h-set data passed only as exact rational boxes and frames;
- an integration that differs from mine in at least one of: coordinates (Weyl (ρ, z) instead of prolate), section
  parametrisation, or interval engine.

The concrete second engine is fixed by amendment before the MN runs, not before the controls. Candidates are CAPD in
Weyl coordinates, or a Taylor-model integrator on the Arb core. Disagreement follows the MR cross-path rule: FAIL means
non-overlapping enclosures, or opposite certain decisions on any inequality.

The combinatorial layer is optional and is not a success criterion: a Lean check of A (ρ(A) > 1) and of the S2
inequalities, given the exported rational boxes.

---

## 5. Order of work and gates

| Step | What | Gate to the next step |
|---|---|---|
| T0 | Read the covering-relation theorem in full text (arXiv:2010.07097 and Zgliczyński–Gidea 2004 if accessible). Record the exact hypotheses. Map each one to S1–S4. | every hypothesis maps to a certified check; otherwise amend before any proof claim |
| R1 | Rössler control (§6.1) | PASS, or a pipeline bug is fixed and R1 is re-run in full |
| R2 | Hénon–Heiles control (§6.2) | the outcome is recorded either way (§6.2 says what a fail implies) |
| R3 | Kerr negative control (§6.3), after the constructor is frozen | no ρ(A) > 1 certified; the failing check is recorded |
| A-K20 | An amendment fixing the MN point, E, L_z, section, λ, the seeds and the second engine, using K20's output | committed before rung 5 |
| R5 | MN horseshoe (§2) | S1–S7 |

I do not wait for K20 during T0 and R1–R3.

---

## 6. Controls (rung 2)

### 6.1 Rössler, a = 5.7, b = 0.2 (pipeline)

**Port.** I port CAPD's own example, `capdDynSys/examples/RosslerChaoticDynamics/RosslerChaoticDynamics.cpp` in the
pinned 2f06098 source, to MPFR under `proof_guard.h`. The rest of the problem is kept identical:
- the field ẋ = −(y+z), ẏ = x + by, ż = b + z(x − a), with a = 57/10 and b = 2/10 as intervals;
- the section x = 0, crossing MinusPlus;
- order 20;
- the sets M = [−8.4, −7.6] × [0.028, 0.034] and N = [−5.7, −4.6] × [0.028, 0.034], with each decimal enclosed
  as an interval of the exact rational;
- the example's subdivisions: 200 pieces for the trapping region and 1 per edge;
- P², the four edge inequalities and the trapping check.

**PASS** means the example's six inequalities all come out true, giving the covering relations M⟹M, M⟹N, N⟹M,
N⟹N, plus the two cone conditions (80 and 40 boxes, Q = diag(1, −100)). The cone conditions are recorded, but only
the covering inequalities gate R1. The time taken is recorded and is not a criterion.

**Second check.** The same sets are checked through MY generic h-set and covering code (§3.7 steps 2–3, frames given
rather than constructed). This must reproduce the same six decisions. It is a test of my code, not of CAPD.

### 6.2 Hénon–Heiles at E = 1/6 (open-system positive control, on its own terms)

**Set-up.**
- H = ½(p_x² + p_y² + x² + y²) + x²y − y³/3, with E = 1/6 exact. At this energy the escape saddles lie exactly on
  the level.
- Section x = 0, p_x > 0, with coordinates (y, p_y) and p_x recovered from the constraint by the positive root.
- The h-sets come from the frozen constructor (§3.7) applied to HH. They are certified to lie in the bounded
  component inside the triangle, with every step enclosure kept at least 0.05 from each of the three saddle points.

**PASS** means S1–S4 hold for HH: some A with ρ(A) > 1 is certified, with the same resource ladder and at most
48 core-hours.

**Literature line (fixed now, per the Bridge on 2026-10-16).** The full texts of Arioli–Zgliczyński are paywalled and
will not be fetched. The write-up cites only what the abstracts state:
- 2001: symbolic dynamics at E = 1/6, computer-assisted;
- 2003: homo- and heteroclinic and hyperbolic periodic orbits in an interval containing 1/6, computer-assisted.

The write-up may say "consistent with the published existence result". It never says "reproduces their proof" or
"matches". If the papers or a preprint turn up later, the comparison gets its own amendment.

**FAIL** (budget exhausted, or no certified ρ > 1) does not refute anything, because chaos at E = 1/6 is published.
It means my constructor or my resources are inadequate for a 2-DOF Hamiltonian at an escape threshold. In that case
R5 does not start until the cause is diagnosed and any fix registered. A fix to the constructor re-runs R3 as well.

### 6.3 Kerr at matched (E, L_z) (negative control)

**Set-up.** The Kerr limits of the target points, q = 0: `mn_metric_components_KERR_p1/p2.txt`, with the same M and
a. Everything else is the same as the MN run: E, L_z, section, λ, D, the frozen constructor, ladder and budget.

**Two runs.**
- K-1: run the constructor exactly as for MN.
- K-2: if K-1 finds no hyperbolic seed in the region, seed instead at Kerr's own unstable orbit of the same (E, L_z)
  and its separatrix (Levin–Perez-Giz 2009), so that the covering machinery is actually exercised.

**Expected (registered prediction).** No transition graph with ρ(A) > 1 certifies. The reason: Carter's Q is
conserved and continuous on Σ, so 𝒫 maps each Q-level curve into itself. Any certified covering pattern would then
sit on 1-dimensional invariant curves, where the entropy is zero.

**What is recorded.**
- WHICH check fails first, and its margin: S2(a) stable band, S2(b) edge crossing, S1 return or transversality, or
  S4 domain.
- The certified Q-ranges of each h-set and of its images, as a diagnostic.
- Any single self-coverings N_i ⟹ N_i near a hyperbolic point. These are allowed and expected, because they give a
  periodic point, not entropy.

**PASS** means no ρ(A) > 1 within the full ladder. If Kerr certifies ρ(A) > 1, the pipeline is unsound: phase 2
STOPS, and the Bridge and the user are told before anything else is done. This control carries the sweep's caveat:
"a broken pipeline also fails to find a horseshoe", which is why WHICH check fails is the recorded output, not
just "no horseshoe".

---

## 7. Failure modes named in advance

| # | Mode | Symptom I will measure | Response (fixed now) |
|---|---|---|---|
| F1 | **Wrapping effect** | enclosure width of 𝒫ⁿ(edge) relative to the h-set width, per return and per precision | climb the ladder (§3.6), then subdivide; if exhausted, report "not certified within budget" |
| F2 | **Near-horizon or near-singular cost** (x → 1, R → 0, CTC boundary) | steps per return; the minimum of (x − 1), R² and g_φφ along the enclosures | an h-set whose orbit leaves D is rejected (S4); cost above budget is reported as F2 |
| F3 | **Expression size of the MN field** | CAPD cost per Taylor step at order 20 and 40, compared with Kerr on the same box. Profiled first, before any covering run, and committed | DAG form and λ reparametrisation (§3.2). If one step costs > 100× Kerr's, register a mitigation amendment before continuing |
| F4 | **Small splitting angle** | K20's numerical angle at the candidate homoclinic point | below 1e−6: start at 512 bits; near-tangent (no transversal intersection resolvable): out of scope for phase 2, reported as such (Wilczak–Zgliczyński 2009 tangency machinery is a later amendment) |
| F5 | **No usable chaotic sea at p1/p2** (K20) | K20's output | fallback point by amendment (§3.1), with the MR-certificate gap stated |
| F6 | **Section not transversal, or no return** on part of a candidate set | S1 fails on sub-boxes | shrink or move the h-set using the frozen constructor rule only |
| F7 | **Kerr certifies ρ > 1** | — | STOP (§6.3) |
| F8 | **Rössler fails** | — | pipeline bug; fix, then re-run R1 in full |
| F9 | **The two implementations disagree** | cross-path table | FAIL under the MR rule; no claim; diagnose |
| F10 | **Theorem hypotheses not matched** (T0) | — | no claim until amended |

---

## 8. Reporting

- **Where results go.** Every run writes a JSON file under `qsim/capd/horseshoe_results/` containing: the input
  sha256, the decisions, the margins, the resources used, the precision and the order.
- **The outcome section** is appended to this file. It lists every failure, including failed controls, with
  numbers.
- **Every amendment** is committed before the outputs it governs, and its commit hash is quoted in the result.
- **Each step is committed and pushed as it lands.** The Bridge is told at each gate in §5.
