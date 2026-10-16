# Pre-registration: chaos-proof phase 2 (B-5), a computer-assisted horseshoe for Manko–Novikov geodesics

*Quantum, 2026-10-16. **AGREED by the Bridge on 2026-10-16, with amendments B1–B5 and the S6 engine choice folded in
(§9).** First version 42eb8aa/4dbb671; this version was committed before T0. Originally a DRAFT for the Bridge's agreement. Written BEFORE any phase-2 output: no control and no target
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
| S7 | **Controls passed first:** Rössler PASS, Hénon–Heiles registered outcome recorded, Kerr shows no ρ(A) > 1 (§6), and the wrong-configuration controls (§6.4) REJECTED. A Kerr certification, or any accepted wrong configuration, stops everything. | §6 |
| S8 | **Disjointness (B1).** The h-sets N_1,…,N_k are pairwise disjoint. Where T0's reading of the theorem requires it for the coding, their images under 𝒫ⁿ are also disjoint from each other. T0 fixes the exact form, by amendment before R1. | certified separation in section coordinates: the interval hulls of the parallelograms are disjoint, or a separating line is certified |
| S9 | **Energy surface and branch (B2).** The flow is integrated in the full 4-D phase space (x, y, p_x, p_y). The eliminated momentum is obtained ONLY when a point is placed on Σ: p_y = +√(ρ(x, p_x)), where ρ is the constraint's radicand, and the radicand enclosure is certified > 0, so the root is a genuine enclosure on the positive branch. Gated, fail-closed: (a) every step enclosure and every return enclosure satisfies H_red(enclosure) ∋ −½, as a consistency check, since the true orbit has H = −½ exactly and an enclosure without it means a bug; (b) at each return, the crossing enclosure has p_y certified > 0 (the chosen branch and direction). For HH the same rule applies, with p_x and the level E = 1/6. Rössler is not Hamiltonian, so S9 does not apply to it. | interval evaluation of H on every enclosure; sign certified at each return |

If S1–S9 all hold, the claim in §1 is made exactly as worded. If any one fails, no horseshoe claim is made, and the
failing check is reported with its numbers.

---

## 2a. Setup correspondence: the condition this runs at, and whether it matches the claim

- **MN claim.**
  - Every check runs at the claim's own condition: the same exact rational (M, a, β), E and L_z, the same μ = 1,
    and the same section Σ and iterate n.
  - Nothing is certified at a neighbouring point and then transferred.
  - The claim names exactly the condition that was certified.
- **Relation to the Morales–Ramis certificates (a mismatch, stated now).**
  - The MR certificates at p1/p2 hold on the levels (E, L, μ²) = (1, 0, 4), (1, 0, 9) and (1, 1, 4). In the μ = 1
    normalisation these are E = 1/2 or 1/3, with L_z = 0 or 1/2. They rule out an additional meromorphic first
    integral there.
  - The horseshoe will run at whatever (E, L_z) K20 supplies, which is in general a different level.
  - So the write-up may say "same metric and parameter point as the non-integrability certificates". It may NOT say
    that the horseshoe and the MR result are statements about the same orbits or the same level, unless amendment
    A-K20 actually places the run on one of those levels. A-K20 prefers those levels when a usable sea exists there (B4).
- **HH.**
  - This runs at exactly E = 1/6, the condition the published abstract states for its symbolic-dynamics result.
  - The section, h-sets and alphabet are mine, because theirs are unread.
  - So the correspondence is "same system, same energy", and nothing finer. That is why the wording is restricted
    to "consistent with" (§6.2).
- **Kerr.** It runs at the same (M, a), E, L_z, section, domain and constructor as the MN run, with only q set to 0.
  That is what makes it a matched negative control. If the MN condition changes by amendment, Kerr is re-run at the
  new condition.
- **Rössler.** It runs at exactly the published example's parameters, sets, section, order and subdivisions (§6.1).
  The one deliberate difference is MPFR intervals in place of double intervals. It is recorded and does not weaken
  the correspondence, because the decisions are being reproduced, not timings.

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
  by the positive square root, whose radicand is certified > 0 (rule and gates: S9).
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
- **The best partial result is always recorded as data (B5):** which covering relations, disjointness checks and
  domain checks held, with their margins, and the largest certified sub-graph of A.
- **An exhausted budget is reported as "not certified within budget"** (F1–F3). It is a statement about the method,
  and NEVER a statement about the
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

**Second engine (fixed 2026-10-16 by the Bridge, who owns S6).** TaylorModels.jl (Julia), doing validated
Taylor-model integration through IntervalArithmetic.jl in Float64-interval mode. It is library-independent of CAPD
and of MPFR, which carried the third replay. Julia is installed by the Bridge and recorded under the reproducibility
policy.
- **Qualification first:** the Bridge's engine must reproduce my Rössler and HH decisions, including the
  wrong-configuration rejections of §6.4, before it replays any MN covering.
- **Fallback:** if it cannot handle the cost of the MN field, the fallback is CAPD in Weyl (ρ, z) coordinates. That
  fallback is written up as representation-independent but NOT library-independent.
- **Disagreement** follows the MR cross-path rule: FAIL means non-overlapping enclosures, or opposite certain
  decisions on any inequality.

The combinatorial layer is optional and is not a success criterion: a Lean check of A (ρ(A) > 1) and of the S2
inequalities, given the exported rational boxes.

---

## 5. Order of work and gates

| Step | What | Gate to the next step |
|---|---|---|
| T0 | Read the covering-relation theorem in full text (arXiv:2010.07097 and Zgliczyński–Gidea 2004 if accessible). Record the exact hypotheses. Map each one to S1–S4, S8 and S9; fix the exact disjointness form for S8. | every hypothesis maps to a certified check; otherwise amend before any proof claim |
| R1 | Rössler control (§6.1) | PASS, or a pipeline bug is fixed and R1 is re-run in full |
| R2 | Hénon–Heiles control (§6.2) | the outcome is recorded either way (§6.2 says what a fail implies) |
| R3 | Kerr negative control (§6.3), after the constructor is frozen | no ρ(A) > 1 certified; the failing check is recorded |
| A-K20 | An amendment fixing the MN point, E, L_z, section, λ and the seeds, using K20's output. Level preference (B4): the Bridge screens the MR levels (E, L, μ²) = (1,0,4), (1,0,9), (1,1,4) first, and a usable sea on one of them is preferred, so that the horseshoe and the MR certificate share a level; otherwise the gap is stated (§2a) | committed before rung 5 |
| R5 | MN horseshoe (§2) | S1–S9 |

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

**PASS** means the example's five covering-gating checks all come out true (the trapping check, which also gives
the stable-band condition, and the four edge inequalities), plus S8 (M and N disjoint). Together they give the
covering relations M⟹M, M⟹N, N⟹M, N⟹N. The two cone conditions (80 and 40 boxes, Q = diag(1, −100)). The cone conditions are recorded, but only
the covering inequalities gate R1. The time taken is recorded and is not a criterion.

**Second check.** The same sets are checked through MY generic h-set and covering code (§3.7 steps 2–3, frames given
rather than constructed). This must reproduce the same five decisions. It is a test of my code, not of CAPD.

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

### 6.4 Wrong-configuration controls on the covering code (B3; the analogue of the MR wrong-p control)

Each of these must be REJECTED (at least one registered check certifiably fails, or cannot be certified at the full
ladder). Each is run on BOTH Rössler and HH, through the same code as the real runs:
- **W1, swapped frame:** u and s exchanged in every h-set frame.
- **W2, rotated frame:** each frame rotated by 90° (for Rössler, the box's y and z roles exchanged in the covering
  test).
- **W3, shrunk set:** one h-set's unstable half-width shrunk by a factor of 10⁻³ about its seed, so that the edge
  images cannot leave the target's u-range.

**What is recorded:** which check rejects each, and its margin. An accepted wrong configuration means the covering code is unsound: STOP (F11).
The Bridge's second engine must reproduce these rejections (§4).

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
| F11 | **A wrong configuration is accepted** (§6.4) | — | covering code unsound: STOP; fix; re-run all controls |
| F12 | **Energy or branch gate fails** (S9): an enclosure misses H = −½, or p_y has the wrong or uncertain sign at a return | — | an enclosure missing H is a bug: stop and diagnose; an uncertain sign means that sub-box is rejected and subdivided |

---

## 8. Reporting

- **Where results go.** Every run writes a JSON file under `qsim/capd/horseshoe_results/` containing: the input
  sha256, the decisions, the margins, the resources used, the precision and the order.
- **The outcome section** is appended to this file. It lists every failure, including failed controls, with
  numbers.
- **Every amendment** is committed before the outputs it governs, and its commit hash is quoted in the result.
- **Each step is committed and pushed as it lands.** The Bridge is told at each gate in §5.

---

## 9. Amendment log

**B1–B5 and S6 engine (Bridge review, 2026-10-16), committed before T0.**
- **B1:** gate S8 (disjointness); T0 confirms the exact form.
- **B2:** gate S9 (rigorous energy-surface reduction and branch).
- **B3:** §6.4 wrong-configuration controls, plus F11.
- **B4:** A-K20 prefers the MR levels.
- **B5:** best partial result recorded as data; the budget exit is about the method.
- **S6:** TaylorModels.jl, owned by the Bridge, qualified on the controls first, with CAPD in Weyl coordinates as
  the fallback.
- **Correction:** the Rössler example has five covering-gating checks, not six as the first draft said.
