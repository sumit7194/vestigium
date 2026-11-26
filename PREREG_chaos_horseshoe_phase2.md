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
| S2 | **Covering inequalities** for every A_ij = 1, in each h-set's local coordinates (u, s) ∈ [−1,1]² (u unstable, s stable): (a) [B8: Def. 2(a) form] every image-enclosure box of a piece of N_i is certified disjoint from F_j = {\|u_j\| ≤ 1, \|s_j\| ≥ 1} (for M3-type sets, F_j = ℝ² ∖ (N_jˡ ∪ \|N_j\| ∪ N_jʳ)), certified on the whole support by subdivision. The originally written form, \|s(𝒫ⁿ(N_i))\| < 1, is recorded as data; (b) 𝒫ⁿ(N_i^{l}) ⊂ {u_j < −1} and 𝒫ⁿ(N_i^{r}) ⊂ {u_j > 1}, or the reverse (degree ±1), for the left and right edges. This is the form of CAPD's Rössler example. (a) as written is STRONGER than Definition 2(a) of Arioli–Zgliczyński and Zgliczyński–Gidea, which only forbids the image from meeting {\|u\| ≤ 1, \|s\| ≥ 1}. T0 may relax S2(a) to the exact form of the theorem by amendment before R1. The stronger form is always recorded as data. | every inequality decided by interval comparison, no tolerance |
| S3 | **ρ(A) > 1.** | exact integer arithmetic: an exhibited n with trace(Aⁿ) ≥ 2 and a cycle structure that gives ρ > 1; ρ also computed exactly as an algebraic number |
| S4 | **Physical domain:** every CAPD step enclosure of every orbit segment used lies in D (§3.4). | interval evaluation on every step enclosure (not on a grid), fail-closed |
| S5 | **Exact field gate:** my Hamilton's equations equal the Bridge's independently derived ones, exactly (in the differential field with R and the exponentials as symbols, as in `replay_gate.py` mn_eq). | exact rational polynomial identity |
| S6 | **Second implementation** (§4) certifies every covering inequality in S2 and every S4 check, with overlapping enclosures and no opposite certain decisions. This is the MR cross-path rule. | separate run, separate code path |
| S7 | **Controls passed first:** Rössler PASS, Hénon–Heiles registered outcome recorded, Kerr shows no ρ(A) > 1 (§6), and the wrong-configuration controls (§6.4) REJECTED. A Kerr certification, or any accepted wrong configuration, stops everything. | §6 |
| S8 | **Disjointness (B1; exact form fixed by T0/B8).** The SUPPORTS \|N_1\|,…,\|N_k\| are pairwise disjoint, as AZ Def. 6 requires. Disjoint images are not required (AZ Theorem 2). | exact rational arithmetic: a separating line between the convex parallelograms, or an exact polygon intersection for M3-type sets |
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
- **HH (amended B7).**
  - **PRIMARY runs at exactly the condition the published result runs at:** AZ 2001's H, h = 1/6, section Θ₁, map
    P₁, and their published t-sets M0–M4, with their Definition 2 applied literally.
  - The p_x formula is derived from H rather than copied: the printed form is a slip that the reproduction does not
    share.
  - The one deliberate difference is that (a) is certified on the whole support instead of via their Lemmas 3–4.
    That makes the result stronger, not a different quantity.
  - **SECONDARY** uses my own h-sets, so it is "same system, same energy" only, worded as "consistent with" (§6.2).
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
- **Fallback point (registered 2026-10-16, B6, before any K20 output).** This applies if p1 and p2 BOTH fail K20's
  usability criteria (F5). Tabula's full-text read finds that all published MN chaos sits at χ = 0.9, q = +0.95, and
  that islands have near-zero width for q ≲ 0.4. The fallback is the published point, in this exact form:
  - **F5-R (primary fallback): (M, a, q) = (89, 80, 19/20).**
    - Here χ = 80/89 = 0.89888…, which is the nearest Pythagorean point to 0.9 (k = √(89² − 80²) = 39 exactly).
      It gives α = −5/8 and β = qM³/k³ = 13394411/1186380 ≈ 11.29, all rational.
    - The MR tool's exact machinery runs over Q plus symbolic exponentials, so it applies unchanged.
    - |Δχ| = 1.1e−3 from the published 0.9. K20 screens THIS point, not only χ = 0.9, and its usability verdict at F5-R
      is the one that counts.
  - **F5-X (only if F5-R fails K20 but χ = 9/10 exactly passes):** the exact published point, χ = 9/10, q = 19/20.
    - Here k = M√19/10, and α is irrational. CAPD encloses √19 rigorously, so the horseshoe is unaffected.
    - The MR certificates would need Q(√19) arithmetic. Until they exist, the "shares a metric point" gap is stated.
  - **q convention:** q is as in `MN_METRIC.md`, β = qM³/k³, which is Gair–Li–Mandel 2008's. Tabula confirms this
    is the convention of the papers it read, before the screen counts.
  - **Morales–Ramis at the fallback point (quantum, conditional).** If the target moves, I add MR certificates there
    with the same machinery as the original ones: v2 certification, a v1 replay where it applies, the CAPD MPFR
    replay, and an exact field gate against the Bridge. The horseshoe and the obstruction then share a metric point.
    That gets its own registration, appended to `qsim/capd/MR_REPLAY.md` or a successor file, before it is run.
  - **F3 risk is higher here:** β ≈ 11.3 against 0.2 and −1/3, so the exponentials are much stiffer near R → 0. The
    F3 profile is redone at the new point.
  - The move itself is made by amendment A-K20, committed before any run there.

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

### 3.4 Physical domain D (Han 2008's exterior check, adapted to vacuum MN; amended B9, before any orbit)

Each condition below is certified on every step enclosure B. The enclosures come from the `TimeMap` replay of
T0/B8.

- **(a) CTC margin, pointwise and certified (B9).** g_φφ > 0 is certified on the inflated box
  B⁺ = B + [−0.025, 0.025] × [−0.025, 0.025], in (x, y). So every point within coordinate distance 0.025 of the
  orbit, in x and in y, is causal.
  - It also implies (b).
  - It uses NO measured quantity, so it has no knife-edge (see the B9 note).
  - It replaces the global δ_x rule of B6, which is withdrawn.
  - The minimum certified distance from the CTC region along the h-set orbits is reported in the result, and stated
    in the write-up.
- **(a′) Away from the degenerate boundary:** x − 1 ≥ 0.05, fixed.
- **(b) No closed timelike curves:** g_φφ > 0 on B itself, implied by (a).
- **(c) Away from the singular core:** R² = x² + y² − 1 ≥ 0.25, i.e. R ≥ 0.5, fixed.
  - The B6 rule R ≥ max(0.5, 2R_s) is withdrawn for the same reason as (a): R_s is a measured quantity.
  - The actual safety condition is (e), finiteness on every enclosure, which fails closed wherever the exponentials
    blow up.
- **(d) Off the axis:** 1 − y² > 0 is certified. For L_z ≠ 0 the centrifugal barrier should keep orbits off the axis
  anyway. The coordinate singularity there also shows up as non-finiteness in (e).
- **(e) Finite metric:** every metric function and every vector-field component is finite, and B > 0
  (`require_finite`, `certainly_positive`).
- **(f) Lorentzian signature:** det g < 0 is certified.

The ergoregion (f < 0) is allowed, because it is physical. Orbits that leave D are treated as plunging, and an h-set
whose image leaves D is rejected; covering relations only need 𝒫 on N_i. The screens (K20) report the fraction f_D
of the candidate sea inside D under both the B6 rule and the B9 rule, as data.

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

### 6.2 Hénon–Heiles at E = 1/6 (positive control; amended B7, 2026-10-16, before any HH run)

**Source.** The user obtained the full text of Arioli & Zgliczyński 2001 (AZ, JDE 171, 173–202); the 2003 paper is
still paywalled. I read the PDF myself and checked it against the Bridge's extract
(`TheBridge/outreach/chaos_proof/AZ2001_setup_extract.md`). These are the facts used here:
- H = (p_x² + p_y²)/2 + (x² + y²)/2 + x²y − y³/3, at energy h = 1/6 (their eq. 1.1).
- Θ₁ = {H = 1/6, x = 0, ẋ > 0}, in coordinates (y, p_y).
- P₁ is the first return to Θ₁. Crossings of x = 0 with ẋ < 0 do not count (their (2.1)–(2.2)).
- The t-sets are defined by line pairs p_y = a·y + b (§4.2).
- The covering is their Definition 2:
  - (a) f(|N₁|) ⊂ int(N₂ˡ ∪ |N₂| ∪ N₂ʳ);
  - (b) the two edges map into the interiors of the two opposite sides, in either orientation.
- Lemma 5 (5.1): M0 ⟹ M0 ⟹ M1 ⟹ M2 ⟹ M3 ⟹ M4 ⟹ {M0, M1}.
- Their Corollary 5 proof states that P₁ is the map on the |M_i| (the modified map 𝒫 differs from P₁ only away from
  the M chain). So (5.1) is read as a set of **P₁-coverings**.

**Two slips in the paper, registered now. Neither one affects the reproduction.**
1. **The p_x formula.** Their Lemma 1 prints p_x = √(2h − p_y² − y² + y³/3). Derived from H at x = 0 it is
   **p_x = √(2h − p_y² − y² + 2y³/3)**, and their own (3.2) is consistent with the 2y³/3 form. I use the derived form.
2. **The entropy bound.**
   - The (5.1) transition matrix on (M0…M4) has 1s exactly for M0→M0, M0→M1, M1→M2, M2→M3, M3→M4, M4→M0 and M4→M1.
   - Its characteristic polynomial is x(x⁴ − x³ − 1), which I checked exactly. λ_max is the real root of x⁴ − x³ − 1,
     1.3802775691…
   - Their Lemma 6 gives h_top(P₁) ≥ ln λ_max = **0.3222846…**
   - Their Corollary 6 prints "h_t(P₁) > 1.38027", which is the λ value, not its logarithm. **The registered
     comparison value is ln λ_max ≈ 0.32228.** 1.38 is never quoted as an entropy.

**HH-PRIMARY: reproduce Lemma 5 (5.1) on THEIR published t-sets.**
- **The sets.** M0–M4 exactly as printed in §4.2: each (a, b) is an exact decimal rational, so the sets are defined
  exactly and nothing needs enclosing.
  - Left side = above the first line of the first pair; right side = below its second line; support = the
    parallelogram cut out by both pairs.
  - **M3** uses its special sides, taken literally:
    - left side Mˡ₃ = {p_y ≥ −0.726y + 0.511} ∪ {p_y ≥ 0.300};
    - right side Mʳ₃ = {p_y ≤ −0.726y + 0.474} ∩ {p_y ≤ 0.290};
    - M3's edges are Mˡ₃ ∩ |M3| and Mʳ₃ ∩ |M3|, computed as exact polygons. They may be 2-D pieces, and their whole
      images are enclosed.
  - I checked the M3 inequality signs on the PDF page image, because the text extraction drops them.
- **The checks.** Each of the **seven** coverings is checked with their Definition 2, literally:
  - **(a)** every image-enclosure box B of a piece of |M_i| is certified disjoint from the closed forbidden set
    F_j = ℝ² ∖ (M_jˡ ∪ |M_j| ∪ M_jʳ). I certify (a) on the WHOLE support by subdivision, and do not use their
    boundary reduction (Lemma 4 plus Lemma 3's analytic well-definedness). That is stronger, and independent of
    their §3. The boundary-only result (a′) is recorded too.
  - **(b)** both edge images are certified inside the interiors of the opposite sides, in either orientation.
  - Bridge's message said "all six"; the count is seven.
- **P₁ on the CAPD side.** Section x = 0, crossing MinusPlus (ẋ = p_x > 0). Starting points are lifted by
  p_x = +√(1/3 − p_y² − y² + 2y³/3), with the radicand certified > 0. S9 applies: every enclosure contains H = 1/6,
  and p_x > 0 is certified at each return. The return time is enclosed (they report 6–10).
- **S8.** The five supports M0–M4 are certified pairwise disjoint (their (4.1)). This is what makes the
  semi-conjugacy defined. The N sets are not used: N0 ∩ M0 ≠ ∅ and N1 ∩ M1 ≠ ∅ (their (4.1)), so they give no
  semi-conjugacy.
- **Resources.** The §3.6 ladder, with at most 48 core-hours shared by PRIMARY and SECONDARY. Their run (Lohner,
  3rd-order Taylor, h = 0.05, 100–300 segments per edge, 2 h 40 min in 2000) is noted for scale only.
- **PASS** means all 7 coverings (a) and (b) are certified, plus S8 and S9.
  - The wording then becomes: "an independent implementation (CAPD/MPFR) **reproduces the covering relations (5.1)
    of Arioli–Zgliczyński 2001, Lemma 5**, on their published t-sets, with condition (a) certified on the whole
    support. With their Theorem 2 and Lemma 6, this gives h_top(P₁) ≥ ln λ_max ≈ 0.32228."
  - It is NOT "reproduces their proof", because their (5.2)–(5.4), the 24-set system and their Lemma 3 are not
    re-done.
- **PARTIAL** means k of 7 are certified. The number k is recorded, with the margins of the failures (B5), and none
  of the wording above is used.

**HH-SECONDARY: my own h-sets, on the same section.**
- The h-sets come from the frozen constructor (§3.7) applied to HH. They are certified to lie in the bounded component
  inside the triangle, with every step enclosure at least 0.05 from each of the three saddle points.
- **PASS** means S1–S4, S8 and S9 hold: some A with ρ(A) > 1 is certified.
- Its result is reported as "consistent with the published existence result". It is a test of the constructor that
  MN will use, not a reproduction.

**HH wrong-configuration controls (B3).** Each must be REJECTED, with the rejecting check recorded:
- **W-AZ1, M2 rotated:** M2's two line pairs are exchanged, so the second pair now defines its left and right sides.
- **W-AZ2, M2 shrunk:** the first-pair lines are moved toward their midline, to 10⁻³ of their separation.
- Rejection means at least one of M1 ⟹ M2 and M2 ⟹ M3 certifiably fails, or cannot be certified at the full ladder.
- Exchanging left and right alone is NOT a wrong configuration, because Definition 2(b) accepts either orientation.
- Plus W1–W3 (§6.4) on my own HH sets.

**A HH-PRIMARY FAIL refutes nothing.** It means my implementation or resources are inadequate, and R5 does not start
until the cause is diagnosed and any fix registered. The same holds for a SECONDARY fail. A fix to the constructor
re-runs R3 as well.

**Literature line.**
- **AZ 2001:** cited from the full text, as above.
- **AZ 2003:** cited from its abstract only: homo- and heteroclinic and hyperbolic periodic orbits in an interval
  containing 1/6, computer-assisted. Nothing from it is matched.

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

**B6 (Bridge relay of tabula's K20 literature read, 2026-10-16), committed before any K20 output.**
- The fallback point is F5-R = (89, 80, 19/20), with F5-X = exact χ = 9/10 as a second fallback (§3.1).
- Morales–Ramis certificates will be added at the fallback point if the target moves.
- The general margin rules for D(a) and D(c) are stated (§3.4).

**B7 (Bridge, 2026-10-16: the AZ 2001 full text obtained by the user), committed before any HH run.**
- HH-PRIMARY reproduces Lemma 5 (5.1) on the published M0–M4 with Definition 2 applied literally: SEVEN coverings,
  under P₁ (per their Corollary 5 proof).
- The p_x slip and the entropy slip are registered; the comparison value is ln λ_max = 0.3222846…
- My own h-set run becomes HH-SECONDARY.
- W-AZ1 (rotated M2) and W-AZ2 (shrunk M2) must be rejected.
- S2(a) is noted as stronger than Definition 2(a); T0 may relax it by amendment before R1.

**B8 (T0 outcome, 2026-10-16; `qsim/capd/horseshoe/T0_HYPOTHESES.md`), committed before R1.**
- **Theorem as used:** AZ 2001 Defs 1–6, Theorems 1–2 (from Zgliczyński 1997) and Lemma 6, in the planar
  one-unstable-direction case. Every target here is in that case.
- **Hypotheses mapped:** every hypothesis maps to a certified check, H1–H9.
- **S2(a)** is relaxed to the exact Def. 2(a) form, with the stronger form kept as data.
- **S8** is pairwise-disjoint supports only.
- **Claim wording** becomes h_top(𝒫ⁿ|Inv(N, 𝒫ⁿ)) ≥ ln ρ(A).
- **S1** relies on CAPD `PoincareMap`'s `checkTransversability`, which runs on every step enclosure touching the
  section; it throws, and the sub-box FAILS. That is AZ's (2.1)–(2.2).
- **S4/S9 in-flow checks** come from a `TimeMap` replay of every set to T_hi, with every step's `getLastEnclosure()`
  checked.

**B9 (decision on the domain rule, 2026-10-16), committed before any orbit.**
- **What prompted it.** The Bridge's V13 geometry (TheBridge a554dc6; no orbits computed) shows that the published MN
  sea at F5-R begins just outside the CTC region: the equatorial CTC edge is at x ≈ 1.885, and the inner bound region
  at (E, L_z) = (0.95, 3) is x ∈ [1.922, 5.03]. Off the equator the CTC region reaches x ≈ 2.42.
- **What the old rule would do.** B6's global rule gives δ_x = 1.45, i.e. x ≥ 2.45, which would discard most of that
  sea.
- **A reproducibility flaw in the old rule.** B6 depended on a measured x_CTC. At p1 the Bridge measures
  x_CTC = 1.07592, which puts δ_x at 0.15, not 0.10. My 0.10 came from the supplier's grid scan
  (`MN_METRIC.md`: "x from 1 to 1.075"), so the rule was not reproducible.
- **Decision.** Both measured-quantity rules (δ_x and R_s) are withdrawn. They are replaced by the certified,
  measurement-free rules (a) (inflated box with g_φφ > 0) and (c) (R ≥ 0.5 fixed), plus (a′) x − 1 ≥ 0.05.
  The safety intent is unchanged: causality is certified on every enclosure, now with a 0.025 neighbourhood.
- **Disclosed.** This change was made after seeing the V13 geometry and before any orbit. The write-up reports the
  orbits' minimum certified distance to the CTC region.

**Correction to the B9 note (Bridge, 2026-10-16; no rule changes).**
- The equatorial CTC edge at F5-R is **1.92192**, not 1.885: the 1.885 was a coarse-grid value.
- **At C0 the edge is 1.92983**, and the inner allowed region's lower edge coincides with it, because the allowed
  region is bounded where g_φφ → 0 (L_z²/g_φφ → ∞). So the inner region ABUTS the CTC boundary; it does not start
  0.04 beyond it.
- **Consequence under B9(a):** orbits that come within 0.025 of that edge fail closed. The usable sea is therefore
  the inner region minus a thin strip along it.
- **Counted rule:** tabula reports f_D under B9's exact form.

---

## OUTCOME log

- **R1 Rössler (2026-10-16): PASS.** The example port gives 5/5 covering checks plus the 2 cone conditions. The
  generic Def. 2 code gives 4/4 coverings. W1–W3 are all rejected by certified failures. Details and numbers are in
  `qsim/capd/horseshoe/R1_ROSSLER.md`.

**B10 (tabula's numerics finding, relayed and confirmed by the Bridge on 2026-10-16), committed before any MN or Kerr
run. It amends §3.2 "Expression form".**
- **Problem.** About 94% of the inner region at C0/F5-R is ergoregion, so orbits cross f = 0, i.e. A = 0.
  Evaluating f and ω through A puts canceling 1/A poles into V and into g_φφ. Interval enclosures of those blow up
  near A = 0, and B9(a)'s g_φφ > 0 test would straddle zero spuriously.
- **Fix.** The MN (and Kerr) field is evaluated ONLY in the A-free regularised form. It rests on the exact identity
  (x² − 1)(1 − y²)·B² − 4C² = A·Q, where Q is a polynomial in (x, y, a, b) and a, b are the two exponential factors.
  - **Independent check (quantum, 2026-10-16):** `sympy.div` of the expanded left side by A, as polynomials in
    (x, y, a, b) with a and b as independent symbols, leaves remainder exactly 0. Q has 46 terms, which matches the
    Bridge's count.
  - The regularised forms, with L′ = L_z + ω₀E (ω₀ = 4kα/(1 − α²)), are:
    - V = ½[e^{2ψ} A L′² − 4kC E L′ − e^{−2ψ} k² E² Q] / (ρ² B);
    - g_φφ = [e^{−2ψ} k² Q + 4kω₀C − e^{2ψ} ω₀² A] / B.
- **Gate before any MN or Kerr covering run.** I verify, in exact arithmetic in the differential field (R and the
  exponentials as symbols), that the regularised V, g_φφ and the full reduced Hamiltonian equal the original
  expressions identically. The S5 gate against the Bridge's field then applies to the regularised field. B9(a) and
  every S4 test use the regularised g_φφ.

**Disclosure on HH-PRIMARY ordering (2026-10-16), committed before the adaptive run starts.**
- **The registered run is the first pass** (`hh1_*`). The first pass used fixed subdivisions: 16×16 support boxes and
  64 pieces per edge. That is the first rung of the §3.6 subdivision ladder, launched from 0c5df05.
- **The order of events.** I read partial first-pass results first: four coverings had finished, with (b) passing and
  (a) failing on coarse boxes. Only after that did I write the adaptive-bisection checker (921ee47) and designate the
  adaptive run (`hh1a_*`) as "counted". So the adaptive scheme was chosen post hoc.
- **What the record will say:**
  - The first pass is reported as the registered run, with its outcome.
  - The adaptive run is reported as a **disclosed escalation within the registered §3.6 ladder**: the caps of 2¹⁶
    leaves for (a) and 2¹² per edge are unchanged. The bisection rule itself (split u first, with the u-depth at most
    the s-depth + 3) was fixed after seeing first-pass data.
  - Both passes' outcomes are reported.

**B11 (decision on the p2 level after the Bridge's V13 A5 move, 2026-10-16), committed before any MN run.**
- **Why the level moved.** At the MR level (1,0,4), L_z = 0, so orbits reach the symmetry axis. There the prolate
  chart is singular, and D(d) requires 1 − y² > 0. K20's shared p2 level is therefore (E, ℓ) = (9/10, 13/10).
- **Primary p2 target: K20's level (9/10, 13/10).** This is off the MR levels, so the §2a gap applies and is stated:
  "same metric point, not same level".
- **Optional secondary: a p2 horseshoe ON the MR level (1,0,4).** It is pursued only after the primary, and it needs
  a polar-crossing chart: θ with y = cos θ, so the meridional orbit passes θ = 0 smoothly, and D(d) is replaced by
  regularity of the metric functions in θ.
  - Its chart, its S5 field gate in the new chart, and its domain rule each get their own amendment before any run.
  - Nothing about the primary depends on it.

**Resource note (2026-10-16, during hh1a): the adaptive W-AZ re-runs were stopped.**
- **Why.** The adaptive checker bisects every failing (a)-box. For a genuinely wrong configuration those boxes never
  resolve, so the run would bisect to the 2¹⁶-leaf cap: about 90 core-hours per covering, well over the 48 core-hour
  HH budget.
- **Where the W-AZ verdicts come from.** The registered first pass (`hh1_W_AZ*`) already settles W-AZ1 and W-AZ2.
- **What was stopped.** The two `hh1a_W_AZ*` processes, my own PIDs 59714 and 72782, killed by explicit PID. They
  added no information. Their JSONs record the kill.
- **Change for future adaptive runs of wrong configurations:** stop at the first CERTIFIED failing check, or use the
  `caps` command with small caps.

**B12 (supersedes B11's p2 primary level, 2026-10-17), committed before any p2 orbit or MN run.**
- **Why.** The level (9/10, 13/10) is plunge-connected in 2-D: its allowed component reaches x → 1 and |y| → 1, and
  43% of it lies outside D_B9. Tabula found this and the Bridge confirmed it, from geometry only, with no orbit
  computed.
- **New p2 primary level:** the Bridge's V13 A8 level (326d21f), (E, ℓ) = (37/40, 3), equatorial x ∈ [3.3886, 5.7411],
  under the 2-D bound-inside-D criterion.
- **Unchanged from B11:**
  - it is off the MR levels, so "same metric point, not same level" applies;
  - the MR-level (1,0,4) run remains optional, needs a polar-crossing chart, and is registered separately before any
    run.

**B13 (2026-10-17): HH-PRIMARY M1⟹M2 and M3⟹M4 re-run after the reboot, with a depth-cap fix, checkpoints and
chunking. Committed before the re-run. This amendment is post hoc, and is disclosed as such.**
- **What happened.** A machine reboot (around 13:20 on 2026-10-17) killed the two adaptive coverings M1⟹M2 and
  M3⟹M4 after about 13 CPU-hours each. They had no checkpoints and left no results. The other five adaptive coverings
  had finished and are sealed (914e99f).
- **A bug found, now fixed.** The §3.6 caps (2¹⁶ leaves for (a), 2¹² per edge) counted only FINISHED leaves, so a
  persistently failing box was bisected depth-first without bound. This likely explains why those two coverings ran
  13+ h, against 20–95 min for the other five.
  - The fix adds depth limits: at most 16 halvings below a top-level (a)-piece, and 12 for an edge piece. A box that
    still fails at that depth is a final, counted failure.
  - This only enforces the registered caps. It is not a new rule.
  - The five finished coverings never went deeper than 5 halvings, so they are unaffected.
- **Checkpoint and restart.** Every finished top-level (a)-piece, together with its failure lines, is appended to a
  checkpoint file keyed by the spec, and fsync'ed. A restart reloads finished pieces.
- **Chunking.** Each covering runs as 2 processes:
  - u-pieces [0, 8) without the edges;
  - u-pieces [8, 16) with the edges.
  - The leaf cap is split 2¹⁵ + 2¹⁵, so the per-covering total stays 2¹⁶.
  - The covering is certified only if both chunks certify (a) and the edge chunk certifies (b). The per-leaf decision
    logic is unchanged.
- **Validation** of the new binary (built from this commit), on the Rössler M⟹N covering:
  - without the new commands, it is identical to the old binary;
  - two chunks merge to the unchunked result;
  - a run killed after 5 pieces and resumed gives an identical result;
  - with failing pieces (rotated M, depth 3), the reload reproduces the result line and all 34 failure lines.
- **The HH budget, post hoc.** The registered 48 core-hours would be exceeded by this re-run: about 34 are already
  used, including about 26 lost to the reboot.
  - On the user's instructions ("we want proper results", "don't worry about time", and on 2026-10-17 "please run
    again"), the re-run continues until each covering finishes WITHIN THE REGISTERED LEAF AND DEPTH CAPS, which bound
    the work. There is no core-hour cap.
  - **Both outcomes will be reported:**
    - under the original 48 core-hour budget, M1⟹M2 and M3⟹M4 are "not certified within budget";
    - under B13, they are whatever the re-run gives.

**B13 addendum (2026-10-18, scheduling only), committed before the re-split runs.**
- **Status.** Three hh1b chunks had finished. M3⟹M4's chunk c1 (u-pieces [8, 16), with the edges) had finished 52
  of its 128 (a)-pieces after about 16 CPU-hours, running alone on one core.
- **What was done.** It was stopped by PID, after its runner, so no partial merge was written. Its fsync'ed
  checkpoint was intact.
- **The re-split.** It is now three processes:
  - c1a: u-pieces [8, 12), leaf cap 16 384;
  - c1b: [12, 14), cap 8 192;
  - c1c: [14, 16) plus the edges, cap 8 192.
  - The caps sum to c1's 32 768, so the per-covering 2¹⁶ is unchanged.
- **Seeding.** Each new checkpoint is seeded with c1's finished pieces in its range. The piece keys are unchanged
  (M3>M4/i/k), so nothing finished is recomputed.
- **Unchanged:** the per-leaf decision logic and the depth caps.
- **Merge.** Both coverings are merged from their chunk JSONs: (a) must hold in every chunk, and (b) in the edge
  chunk.

- **HH-PRIMARY (2026-10-18), full record in `qsim/capd/horseshoe/HH_PRIMARY_OUTCOME.md`:**
  - **The registered first pass:** (b) holds 7/7; (a) is not certified at 16×16; W-AZ1 and W-AZ2 are rejected.
  - **After the disclosed post-hoc escalation** (adaptive bisection, then the B13 re-run): **all 7 coverings of AZ
    2001 (5.1) are certified.** S8 and S9 hold, and h_top(P₁|Inv) ≥ ln λ_max = 0.3222846.
  - **Both budget readings:**
    - original 48 core-hours: PARTIAL, 5/7;
    - B13: 7/7.
  - **Correction:** B13's "persistently failing box" speculation was wrong. No box reached the depth cap.
- **B10 gate (2026-10-18): PASS** (`qsim/capd/horseshoe/mn_field_gate.py`, `mn_field_gate.json`).
  - **Exact, for general k, α, E and L:** (x² − 1)(1 − y²)B² − 4C² = A·Q with remainder 0 (Q has 46 terms). The
    regularised g_φφ, the regularised V, and the full H_red built from the inverse metric are identical to the
    originals. det of the (t, φ) block is −ρ².
  - **Conventions:** my metric construction matches the supplied components (p1, p2 and both Kerr limits; all 5
    components at 6 random points each), with relative difference exactly 0 at 60 digits.
  - **Mutation controls:** a sign flip of ω₀ and f scaled by 1.001 are both detected.
  - **Still to do before any MN or Kerr run:** the S5 gate against the Bridge's field.
- **S5 field gate (2026-10-18): PASS** (`qsim/capd/horseshoe/mn_s5_gate.py`, `mn_s5_gate.json`), against the
  Bridge's independent V13 field (`TheBridge/.../V13_mn_chaotic_sea/code/v13_field.py`, imported read-only).
  - **How S5 is carried out:** the polynomial layer (A, B, C, Q) is compared EXACTLY. The transcendental layer is
    written differently on the two sides, so the full H_red is compared NUMERICALLY at 70 digits rather than as a
    symbolic identity.
  - **Result:** the worst relative difference is 4.1e−70 over 12 random phase-space points per case. The cases are
    p1, p2, F5-R and C0 at (E, L) = (19/20, 3), plus their Kerr limits, which differ by exactly 0.
  - **Mutation control:** L → 1.001 L is detected at 5e−6 to 6e−5 in every case.
  - **Note:** this C0 uses (M, a) = (10, 9) and β = 0.95·M³/k³. The gate only needs the same inputs on both sides.

**B14 (2026-10-18): the h-set constructor (replaces §3.7 steps 1–3). Written AFTER non-rigorous exploration on HH
(disclosed below) and BEFORE any rigorous HH-SECONDARY run. It is applied unchanged to Kerr (R3) and MN (R5).**

**Why §3.7 needed replacing.** As written, §3.7 put sets only at periodic points, with frames from their eigenvectors.
That cannot produce a horseshoe: the sets must follow a homoclinic or heteroclinic excursion, as AZ's M0→…→M4 chain
does.

**The constructor** (`qsim/capd/horseshoe/hs_construct.py`, non-rigorous double precision; only hs_cover's MPFR run
counts):
1. **Saddles.** Hyperbolic fixed points of P (period 1 first), found by Newton on P(w) − w. P comes from DOP853,
   rtol 1e−12, with DP from the variational equations.
   - For HH: from seeds in the registered region, keeping real-eigenvalue saddles.
   - For Kerr and MN: from K20's UPO list in A-K20.
2. **Connections.** Arcs of W^u(p) and W^s(q) are traced from a fundamental segment of length 10⁻⁴ through 5 forward
   and backward iterates, refined to 0.01 spacing. Transverse crossings must have angle ≥ 0.01 rad.
   - The chosen connection minimises |k_u| + |k_s|, with ties broken by the largest angle.
   - It is refined by Newton on the two manifold parameters, to a residual below 1e−10.
3. **The chain.** The orbit x₀ … x_m of the connection, with x₀ on W^u(p) and x_m on W^s(q).
   - N0 sits at p, with frame (a0·e_u, b0·e_s).
   - Chain sets sit at x_j, with frames (a·U_j, b·S_j). U_j is the W^u tangent, propagated forward with DP. S_j is the
     W^s tangent, pulled back with DP⁻¹.
   - The chain uses the contiguous run j₁ … j₂ of orbit points whose sets are disjoint from N0 and from each other.
4. **The ladder,** in this fixed order, accepting the FIRST passing entry:
   - a0 ∈ (0.03, 0.02, 0.015, 0.01);
   - a ∈ (0.01, 0.005, 0.0025);
   - b0/a0 ∈ (0.5, 0.25, 0.1);
   - b/a ∈ (0.5, 0.25, 0.1).
   - **Acceptance:** every REQUIRED covering passes the sampled check (12 points per edge and an 8×8 interior grid,
     using the true map). The required coverings are N0⇒N0, N0⇒N_{j₁}, N_j⇒N_{j+1}, and N_{j₂}⇒N0.
   - The extra edge N_{j₂}⇒N_{j₁} is attempted rigorously too, but it is NOT required. The required graph has cycles of
     lengths 1 and L through N0, so ρ > 1 by itself.
5. **Freezing.** The constructor is frozen at the commit that registers this amendment's outputs (hh2 specs). Any
   change re-runs every control (§3.7, unchanged).

**Disclosure (exploration on HH, non-rigorous):**
- **The saddle finder reproduces AZ's Π₄ = (−0.24979, 0) and Π₅, Π₆ = (0.37677, ±0.30672)**, all with λ_u = 7.2625.
  The Jacobian is FD-checked, with det = 1.
- **The connection:** the Π₄ homoclinic with k_u + k_s = 8 and angle 0.98.
- **The rule was arrived at in two steps.**
  1. A first scan, with small sets near Π₄, passed all sampled coverings but violated S8.
  2. The disjointness requirement and the larger a0 ladder were then added.
- **What the second scan found.** Its FIRST entry (a0 = 0.03, a = 0.01, b0/a0 = b/a = 0.5) gives the chain x₃ … x₆.
  Every REQUIRED covering passes there; only the optional N6⇒N3 fails.
- **What was fixed after seeing exploration output:** the ladder values and the required/optional split.
- **No rigorous HH-SECONDARY computation has been run.**

**HH-SECONDARY rigorous run (registered now):**
- **Sets:** the accepted sets, converted to exact rationals (centres and frames rounded to 1e−10). The sets are then
  defined exactly by those rationals.
- **Gate:** S8 must hold exactly before the run.
- **Run:** hs_cover with the B13 settings (adaptive bisection, depth caps 16 and 12, leaf caps 2¹⁶ and 2¹² per
  covering, checkpoints), MPFR 128 bits, order 20, S9 on.
- **PASS:** all 6 required coverings certified ⇒ ρ(A) > 1, with ρ the root of λ⁵ = λ⁴ + 1 (≈ 1.3247), so
  h_top ≥ ln ρ ≈ 0.2812.
- **Wording:** "consistent with the published existence result" (§6.2), and a test of the constructor.
- **HH-SECONDARY (2026-10-19): PASS** (`qsim/capd/horseshoe/HH_SECONDARY_OUTCOME.md`).
  - All 6 required coverings are certified on the B14 constructor's sets. The optional N6⟹N3 is a certified
    orientation failure.
  - ρ is the plastic number 1.3247, so h_top ≥ 0.28120. This is "consistent with" AZ 2001.
- **HH embargo lifted (2026-10-20).** The Bridge's V14 Q2 HH decisions are committed (TheBridge 8e73970). The
  Bridge may now open the sealed HH files (ca819cf and 5a21dde) for the S6 cross-path comparison.
- **S5 re-run at A-K20's exact FINAL parameters (2026-10-20): PASS** (`mn_s5_gate_ak20.py` and `.json`). The cases
  are F5-R (89, 80, 13394411/1186380) and C0 (1, 9/10, (19/20)/(19/100)^{3/2}), at E = 19/20 and L_z = 3M, plus their
  Kerr limits. The worst relative difference in H_red is 2.0e−69; the Kerr limits differ by exactly 0.
- **Citation correction:** A-K20's FINAL text is TheBridge **a713523**. Commit 0e42f37 is only the rename, with the
  old DRAFT labels; the physics content is identical.
- **R3 Kerr at matched (E, L_z) (2026-10-20):** no hyperbolic seed in Kerr's allowed region in either registered
  branch, so the failing check is constructor step 1 and no covering was attempted
  (`qsim/capd/horseshoe/R3_KERR_OUTCOME.md`).
  - This is consistent with the prediction, but it is the weak form of the control.
  - A stronger Kerr control, at a level with a bound unstable spherical orbit, is to be proposed as B15.

**B15 (2026-10-20): the strong Kerr negative control. Registered before any B15 run, and run BEFORE the MN covering
run (agreed with the Bridge).**
- **Why.** R3 at A-K20's level never reached constructor steps 2–4. This control does: it puts the FROZEN B14
  constructor on an integrable system that HAS a bound hyperbolic orbit with a non-transversal homoclinic separatrix
  (Levin & Perez-Giz 2009).
- **System.** Kerr, (M, a) = (89, 80), q = 0. The field is my B10/S5-gated one, with β = 0.
- **The level, from the exact radial double root** (in units M = 1). R(r) = [E(r² + a²) − aL]² − Δ[r² + (L − aE)² + Q]
  with R = R′ = 0:
  - At L_z = 3M (A-K20's), every unstable spherical orbit has E > 1 (1.12 to 1.38 for Q from 0 to 12): none is bound.
  - The nearest round value with a bound one is **L_z = 5M/2 (= 445/2), with E = 49/50**.
  - The double root is at **r_s = 1.806812911814262M** with **Q_s = 0.740762452760964M²** (physical
    Q = 5867.58). R″(r_s) = 6.08 > 0, so the orbit is unstable. The other real roots are 0.0989M and 46.79M, so the
    homoclinic is bound and turns at 46.79M.
  - **Section fixed point:** x_s = (r_s − M)/k = 1.8411884397812655, p_x = 0, on Σ = {y = 0, p_y > 0}. It is inside D:
    x − 1 = 0.84, R = 1.53, and Kerr has no CTCs outside r < 0.
- **Procedure:** B14 unchanged, with the same thresholds as MN.
  1. **Saddle:** Newton from (x_s, 0). Record λ_u.
  2. **Manifolds:** arcs with eps = 1e−4, K = 5, dmax = 0.01, and crossings with min angle 0.01.
     - **Recorded as DATA:** every crossing found, with its angle and its local discretisation floor
       θ_floor = κ̂·(ℓ_u + ℓ_s). Here κ̂ is the polyline turning angle per unit length at the crossing, and ℓ_u, ℓ_s
       are the two crossing segments' lengths.
     - **Expected noise level:** two polylines through the same smooth curve cross at angles up to about θ_floor.
     - **Red flag:** a crossing with angle > 10·θ_floor.
  3–4. Steps 3–4 run ONLY if step 2 returns an accepted connection.
- **Registered prediction:** step 2 finds no transverse crossing above the red-flag level, so the constructor builds no
  sets. Which check fails is recorded either way.
- **If sets are built anyway,** they go to rigorous hs_cover with the same B13 settings. The prediction is that the
  rigorous coverings do not give ρ > 1.
- **STOP rule (F7):** any rigorous ρ > 1 on Kerr STOPS the MN claim.
- **Resources:** the constructor stage is one Python process (about 0.2 GB RAM) at nice 10, for an estimated 1–4 h.
  A rigorous stage, if one is reached, would need the CAPD MN/Kerr field, which is not built yet. Its launch plan
  would be sent to the Bridge first.
- **MN/Kerr CAPD field: codegen gate (2026-10-20): PASS** (`mn_codegen_gate.py`, `mn_codegen_gate.json`).
  - **The field** (gen/mn_field.h) is generated from ONE sympy source after CSE. Every function is a template on S:
    CAPD Node for the integrator, MPFR intervals for the S4 and S9 checks.
  - **A printer bug was caught first,** by a smoke test, before any run used the field: integer powers were printed
    unparenthesised, so a/b³ became a/b·b·b. It is fixed.
  - **Gate:** each function (field, H, g_φφ, B, g^xx, g^yy, V) is evaluated by C++ at 160 bits at 8 random exact
    points, for F5-R, F5-R's Kerr limit, and Kerr at the B15 level. Each enclosure must contain the 80-digit mpmath
    value of the same sympy expression. All are enclosed, with relative widths ≤ 3.5e−42.
  - **Mutation control:** L × 1.001 lies outside the enclosure in all 32 of 32 L-dependent outputs per case.
  - **Correction disclosed:** the first draft of the criterion wrongly expected ẋ and ẏ to depend on L.
- **hs_cover gains system `mn`.**
  - Section y = 0 (MinusPlus), coordinates (x, p_x); p_y > 0 is lifted from H = −½ on the piece hull, with the
    radicand certified > 0.
  - S9: H ∋ −½ on every step enclosure and at the return, and p_y > 0 certified at the return.
  - S4 on every step: g_φφ > 0 on the ±0.025 box, x − 1 ≥ 0.05, R² ≥ 0.25, 1 − y² > 0, B > 0 (which certifies
    det g < 0), and finiteness.
  - It is identical to the previous binary on Rössler and HH.

**B16 (2026-10-20): no wall-time cap. Committed BEFORE any MN or B15-rigorous run; it supersedes the time parts of
§3.6.**
- **Basis:** the user's standing instruction (2026-10-20): "we never cut down the tests because of time … science and
  rigour and our methods and completeness are the better criteria". This matches the Bridge's recorded user notes of
  2026-10-03, 10-10, 10-11 and 10-12.
- **(a) Verdicts.** The only verdicts are CERTIFIED, REJECTED (a certified failing check), and UNDECIDED at the
  RESOLUTION caps (depth and leaf caps; the MPFR precision and Taylor-order ladder). Wall time and core-hours never
  produce a verdict. The 14-day cap on the first MN attempt, and any core-hour cap, are removed.
- **(b) Interruptions.** A reboot, a resource hold or any other interruption is a PAUSE. The run resumes from
  checkpoint, and the pause is logged with its time and cause.
- **(c) Resources.** On weekdays (the user's office machine): ≤ 4 cores, nice 19, checkpointed, with memory and disk
  checked before a launch. A weekend scale-up is announced to the Bridge first.
- **(d) Progress.** For any run longer than a day, a daily progress record of leaves finished and queued per covering,
  plus CPU time, goes in the run's log. A stuck run is visible as data, never a reason to stop.
- **(e) Methods.** No check, test or verification step is weakened, merged or skipped to save time. A method change is
  considered only if it improves rigour or completeness, or is rigour-neutral and needed for a run to be possible at
  all. Every method change is registered before use.
- **The HH runs are unchanged.** HH-PRIMARY keeps its two disclosed budget readings (B13): this amendment is not
  retroactive.

**B17 (2026-10-23): MN swing-fix diagnostic success criterion.** Drafted by quantum and reviewed by the Bridge
(gain-weighting, the peak-stretch checkpoint and the k_c sanity rule are the Bridge's). Registered BEFORE any
set-propagation fix result is read against it.

- **Scope.** The diagnostics that evaluate changes to set propagation for the MN reduced flow at F5-R: reorganisation
  policy, needle-frame Q re-seed, moving integration frame, or a custom second-order C⁰ step. These produce no covering
  verdict. Any change that reaches `hs_cover` needs its own amendment (see the last item).
- **Test object.**
  - The smoke box: centre at F5-R UPO 2, (x, p_x) = (36419361737/10¹⁰, 60360992808/10¹⁰); y = 0; p_y > 0 on H = −½.
  - Half-widths W₀ ∈ {1e-6, 1e-7}, plus every piece size later proposed for coverings. All W₀ tested are reported; none
    is selected.
  - The 8-D augmented field (`mn_codegen8.py`), with the correlated p_y and a/b/E2/eG lifts.
  - CAPD 2f06098, MPFR 128 bits, Taylor order 20. The set type and policy are stated per run.
- **Metrics,** in the NEEDLE frame of the centre orbit at each checkpoint:
  - u₁ and u₂ (SVD of Φ(t, 0)·D_in), n_H (the unit ∇H), and the a/b/E2/eG off-manifold directions.
  - The set's projected widths along these directions.
  - The true u₁ and u₂ widths come from the hull of at least 16 boundary-point images, integrated with DOP853 at 1e-13.
    The true off-shell and off-manifold widths are 0.
  - The gains g_d are measured from the centre variational: the 4-D one for u₁, u₂ and n_H, and the 8-D augmented one
    for the off-manifold directions. Each g_d runs from the checkpoint to the next checkpoint, and after the last swing
    to the Σ return.
- **Checkpoints.** The times t_p1 and t_p2 are the first and second periapsis times of the centre orbit, and t*_1 and
  t*_2 are the times of peak true stretch in each swing: the argmax of ‖Φ(t, t_p − 7)·M‖, with M the set's true span.
  All four are computed and logged before any fix run.
  - **Swing 1:** t_p1 − 7, t*_1, t_p1 + 1, t_p1 + 5.
  - **Between the swings:** the first y = 0 crossing with ẏ < 0, as a section enclosure.
  - **Swing 2:** t_p2 − 7, t*_2, t_p2 + 1, t_p2 + 5.
  - **The return:** to Σ = {y = 0, ẏ > 0}, the first crossing after t = 1, as a section enclosure (the P image).
- **Threshold:** provisional k = 5.
  - **Real directions:** at every checkpoint, set / true ≤ k along u₁ and along u₂.
  - **Fake directions** (zero true width), gain-weighted: Σ_d width_d·g_d ≤ k·(true u₂ width)·g_u₂, summed over n_H and
    the four off-manifold directions.
  - **Before any covering run,** k is replaced, in its own amendment, by k_c = (stable margin of the target h-set) /
    (true stable-direction image width × s), with safety factor s = 2.
  - **Sanity rule:** if k_c < 1, the h-set is wrong. That is a constructor issue, and is reported as such; it is never
    "fixed" by loosening k or anything else.
- **Pass rule.** A fix passes for a given W₀ if and only if:
  - the integration completes to the Σ return;
  - S4, S9 and the augmented-state consistency check hold on every step;
  - every checkpoint meets the threshold.
  - Any throw, or any failed check, is a FAIL. A pass licenses THAT W₀ only; any other piece size needs its own pass.
- **Data recorded (not criteria):** wall time, CPU time and step count per run. Compute is not a criterion (B16).
  Piece counts implied by k are planning information. If they are large, the budget is amended, not k.
- **Runs started before B17** are INFORMATIONAL and are not read against B17. These are the QRESEED = 1 and 10 probes
  (2026-10-23 09:00), the 8-D 1e-7 and 1e-8 pairs, and diag8_noreorg. A fix found during them is re-run under B17 from
  scratch.
- **Before any fix is used for coverings:**
  - a soundness note for the changed set algorithm;
  - for a second-order step, the toy positive control first;
  - the Bridge's independent check: a review of the derivation and code, and a containment test in which
    high-precision point images of random boxes along the orbit lie inside every step's enclosure;
  - its own registered amendment;
  - the user's OK on the launch plan.

**B18 (2026-10-23): S4 implementation amendment.** The predicate is unchanged; only the enclosure method changes.
Agreed with the Bridge. Registered BEFORE any run uses it, and applied to `hs_cover` too before its next MN run.

- **The finding.** The registered S4 check (B9: g_φφ > 0 on the ±0.025 inflated box, plus B > 0 on the enclosure and
  the other domain conditions) could not be evaluated on MN as implemented. The 4-D generated g_φφ (division-form Q),
  evaluated naively on the 0.05 × 0.05 inflated box, hits an interval division by zero at the first step. This surfaced
  in the B17 harness's positive control. `hs_cover`'s smoke test never reached the replay where S4 runs, so S4 had never
  been exercised on MN.
- **What changes.**
  - B and g_φφ are evaluated in the structured, A-free form: the Bridge's structured Q, v13's grouped A, B and C, and
    sqr for squares. This is `gen/mn_field8.h` mn8_domain, as functions of (x, y). B is the only denominator.
  - Gate: at 40 random exact rational points in the orbit tube, the 160-bit C++ enclosures contain the 60-digit mpmath
    values of the ORIGINAL expressions (`tests/domain_gate.py`: 40/40 PASS). A symbolic point check shows equality to
    40 digits.
  - A box that does not certify is bisected along its longer side, down to a depth cap of 12. The cap is a resolution
    cap (B16). A box uncertified at the cap is an S4 FAIL, never a skip. A sub-box whose evaluation throws counts as
    uncertified.
- **Tile cache** (optional, for efficiency only): not implemented. If it is ever added, it requires rigorous coverage
  (outward-rounded enclosure bounds against exact rational tile edges), certification of each tile by the same
  predicate, and a regression cross-check against per-step bisection on random steps.
- **Unchanged:** the predicate, the ±0.025 inflation, the other S4 conditions, and S9.

**B17a and B18a (2026-10-23): harness corrections found by the B17 controls.** Agreed with the Bridge and registered
before the controls are re-run. The negative control (1e-6, default policy) FAILED as expected, at t = 283.9: u2 was
472× true. The positive control (1e-12) exposed two procedure defects.

- **B17a (true widths).**
  - **The defect:** at W₀ = 1e-12 the set came out narrower than its "true" width (0.19×). That is impossible for a
    rigorous enclosure. The double-precision DOP853 hull (error ~1e-11) is inadequate for W₀ ≲ 1e-8.
  - **The fix:** for W₀ ≤ 1e-8 the true u₁/u₂ widths are the variational (linearised) widths, which equal the hull to
    O(W₀²); hull/linear = 1.00 was verified at 1e-6 and 1e-8 through the swing. A hull spot check with ≥ 30-digit point
    images is done at one checkpoint.
  - **Sanity rule:** if set / true < 0.98 at any checkpoint (the tolerance comes from the reference's own error), the
    run is flagged HARNESS ERROR. That is neither a pass nor a fail.
- **B18a (S4 near the CTC boundary).**
  - **The defect:** at t = 290.43, g_φφ > 0 on the ±0.025 box was not certified at depth 12. Sampling says the predicate
    is TRUE but tight. The g_φφ ≤ 0 region at F5-R reaches x ≈ 1.921 for |y| ≤ 0.37, and the UPO's periapsis is at
    x = 1.9423. The sampled minimum of g_φφ on the box is 1.4e4 at periapsis.
  - **The fix:** on each sub-box, the mean-value form g(c) + ∇g(box)·(box − c), with ∇g by CAPD AD of the same
    structured function, is intersected with the plain enclosure. The predicate, the ±0.025 box and the depth cap of 12
    are unchanged. A box uncertified at the cap is still an S4 FAIL.
  - **Logged as data:** the certified lower bound of g_φφ along the orbit.
- **Physics note.** The B9 margin of 0.025 is nearly saturated at the UPO's periapsis. A piece that genuinely fails S4
  is a domain result and is reported as such. The margin is never shrunk to rescue a piece.

**B15b (2026-10-24): a compiled map for the B15 constructor stage.** Drafted by quantum and reviewed by the Bridge
over three revisions (B15_MAP_AMENDMENT_DRAFT.md, commits ce3a599, b3d579c, c71b44f, 325193b). Registered with the
user's OK BEFORE any gate (G0–G5) was run. Only the implementation of the constructor's map calls changes; B15's
procedure, thresholds and registered prediction are unchanged.
- **Before anything is used:** no counted B15 run uses a compiled map until this text, as finally reviewed, is in
  PREREG_chaos_horseshoe_phase2.md with the user's OK, and gates G0–G5 have passed. G6 runs alongside the counted run.
- **State of the Python B15:** b15_kerr.py, the original NON-checkpointed script, PID 24176, has been running for
  about 4 days.
  - It finished step 1, and its W^u arcs (26,047 points in 300,804 s).
  - It is **still running.** It will be stopped at the macOS 27.0.1 update (the user's decision) and not relaunched.
  - Its arc points exist only in that process's memory. No journal was written, so none can be reused.

**B15b — Why.**

The Python B15 (MNFlow, scipy DOP853) averaged about 11.5 s per W^u arc point. The compiled maps take about 4.5 ms
per return with the Jacobian, near the saddle.

**B15b — What changes, and what does not.**

- **Changes:** only the implementation of P, Pinv and py_of that the frozen B14 constructor calls through
  `mn_numerics.plug_into_constructor`. The adapter is `kerr_compiled.CompiledFlow`, with MNFlow's signatures and
  return conventions.
- **Unchanged:**
  - hs_construct.py;
  - every B14 and B15 threshold;
  - TMAX = 1e6;
  - the seed, the step logic, and the registered prediction;
  - pcache journalling, which is now used, so the run is checkpointed.
- **Primary implementation:** `kerr_rs` (Rust).
- **Second implementation:** `kerr_p.cpp` (C++, Boost.Odeint). It has the same field and C ABI, and is used for
  cross-checks only.
- **Reference:** MNFlow.

**Integrator and event changes, required before the gates.** These follow the Bridge's points 2 and 3. Each
implementation gets them through its own code.

- **E1. Event located in the step's local variable.** Bisection runs on θ = (t − t0)/h ∈ [0, 1] of the accepted step,
  to |Δθ| ≤ 4e-16. That is relative to the step, not to t.
- **E2. Step to the event.** One real integrator step of length θ*·h is taken from the accepted step's start, and
  that state is used, not the interpolant. Its error estimate must pass the same tolerance, or the step is halved
  and repeated.
- **E3. Logged for every crossing:**
  - the bound |ẏ|·h·Δθ;
  - the difference between the interpolated and the stepped state;
  - the event time.
- **E4. The return time** is accumulated as Σ(t0 + θ*·h) in compensated (Kahan) summation, so the ulp of t does not
  enter the state. Only T itself carries it.
- **E2-check. The re-step is a check, not only a log.**
  - Criterion: the interpolated and stepped states agree to ≤ 1e-11 relative, block by block: the 4 state components
    relative to max(1, ‖state‖∞), and the 16 variational components relative to max(1, ‖Φ‖∞). Block by block is
    stricter than one norm over all 20, which Φ ~ 1e3 would dominate.
  - If exceeded: the event step is redone from its start with the step halved, up to 10 times, and each retry is
    counted. If it still fails, the call FAILS.
- **E5. One crossing per step, checked on every step.**
  - On every accepted step, not only the event step, the section function y is sampled at the step's endpoints and
    at 8 interior points of the dense output.
  - Criterion: at most one sign change, and on the event step exactly one, in the registered direction.
  - Anything else (two changes, or a change the endpoints do not show) means the step is redone with h halved, up to
    10 times. If it still fails, the call FAILS.
  - The transversality margin |ẏ| at each accepted crossing is logged.
  - **This is a detection heuristic, not a guarantee:** 10 samples can miss a root pair that falls between samples.
    That is acceptable for a numerical constructor stage, and it is not claimed as more.
  - The event-step check catches a near-tangent double root. The every-step check also catches a crossing pair
    hidden inside one step, which the endpoints never show; that would silently skip a return.
- **A FAILED call is not "no return".** The C ABI gets a distinct return code (−1: integration check failed), next to
  0 (no return within tmax) and 1 (success). The adapter raises an exception on −1, so the constructor can never read
  a numerical failure as the geometric fact "no return", which it acts on. pcache does not journal a raised call. A
  run that hits one stops with a HARNESS-ERROR, and that is reported.
- **Common mode, noted:** the two compiled implementations share the event DESIGN (E1–E5), coded separately.
  MNFlow (brentq on DOP853's dense output, no re-step) is the one reference with a different event design, so it
  stays the reference in G1 and G4.

MNFlow locates events with brentq (xtol = rtol = 4·EPS in t) on DOP853's dense output, which is 7th order. Its event
state is therefore an interpolant, and its t-resolution is ~1e-16·t. This is recorded as a property of the
reference, not changed.

**B15b — Disclosure: a bug in kerr_p.cpp, found by the second implementation.**

As committed in 18c33e0, kerr_p.cpp's slide-back correction ran in place. The i = 1 iteration zeroed V[1] before the
p_x and p_y rows used it:

- det DP came out 0.57–0.61 instead of 1;
- the DP entries were off by up to 1.3e-2;
- the x row was unaffected.

The Rust port copies the y row first. It matched central finite differences to about 1e-8, with det DP = 1.000000.
The fix is in ce3a599. **No counted result used kerr_p's DP.**

**B15b — Field provenance (common mode).**

All three implementations evaluate expressions from one sympy source:

- the C++ and Rust code is generated from it after CSE;
- MNFlow lambdifies it.

SHA-256 prefixes at registration:

| File | SHA-256 prefix |
|---|---|
| mn_codegen.py | 6034250777bd41c0 |
| gen/mn_field.h | 4c1c7b57bcbead23 |
| kerr_rs/src/mn_field.rs | 7ae5ec20f8da42e0 |
| mn_codegen_rs.py | 9e242873f870d538 |
| mn_numerics.py | 4728b71569201e31 |
| hs_construct.py (frozen) | ae198d966bfff241 |


**Correction:** I find no "V15 Ricci-flat" validation of this source in the repo. The vacuum checks on record are
for the supplied metrics of the MR and TS work, and are pointwise. This source's gate is the B10 codegen gate,
which checks C++ against mpmath of the same sympy expressions, so it is not independent of the source.

For B15 the system is Kerr, which gives a source-independent physics check: G0b below.

**B15b — Gates.**

Criteria are fixed here, before any gate output is read.

**G0. Field accuracy in double, along the real excursion.**

- Points: 100 states sampled at equal arc length along two compiled W^u orbits from the G4 rule, covering
  x ∈ [1.05, 110] and the y range they visit.
- Compared: the generated field (Rust, C++, and MNFlow's lambdified field) against 50-digit mpmath of the same sympy
  expressions, at the same double inputs.
- Criterion: |Δf_i| ≤ 1e-12·‖f_ref‖∞ for every component at every point. Componentwise relative errors are also
  reported, but a component near zero cannot carry a relative criterion.
- On a failure: a rewritten far-field form, never a looser gate.
- **Correction to the review:** the excursion turns at 46.79M. That is r ≈ 4164 in the field's M = 89 units, so
  x = (r − M)/k ≈ 104.5, not r ≈ 4.7e7. The concern still stands at x ~ 100, with high-degree polynomials in x,
  just less extreme.

**G0b. Kerr integrals, independent of the sympy source.** Split into two parts, as the Bridge proposed.

- **G0b-field, the source check: EXACT.**
  - At β = 0 every exp in the source is a constant, and Rr enters only through β-terms, so the Kerr field is
    rational in (x, y, p_x, p_y).
  - Test: evaluate the Poisson bracket {Q, H} exactly, in rational arithmetic, at 20 random rational points of the
    domain (Schwartz–Zippel). Every coordinate has a numerator and denominator of ≥ 64 bits, drawn inside the domain
    (x > 1, |y| < 1), with the seed recorded, so the sample set is large relative to the degree. Q is Carter's constant from the textbook Boyer–Lindquist expression; H is the source's
    Hamiltonian at the B15 parameters.
  - Criterion: exactly 0 at all 20 points. A sympy `cancel` of the full bracket is attempted as well, and reported.
  - **Correction to the review (two points):**
    - A 1e-12 bar is a double-precision bar. At 50 digits a correct source gives ~1e-45, so 1e-12 would hide a
      genuine error between 1e-45 and 1e-12. Exact rational arithmetic removes the question.
    - The H half is vacuous as a source check. mn_codegen builds the field as the Hamiltonian vector field of H, so
      ∇H·f ≡ 0 for ANY H. Only {Q, H} = 0 tests whether H is Kerr's.
  - **Convention mapping, fixed before the test runs:**
    - x = (r − M)/k and y = cos θ, so p_x = k·p_r and p_θ = −sin θ·p_y;
    - μ² = −2H as a phase-space function, so Q is a phase-space function, not only an on-shell one;
    - the relation of the source's (E, L) to Kerr's (E, L_z, a), including the shift L' = L + w0·E in V and the sign
      of a.
    This derivation is written down and committed BEFORE the first evaluation. If the bracket is nonzero, the
    result is reported as a FAIL first. Any later "convention error" diagnosis is a disclosed correction with its
    own commit, never a silent fix.
- **G0b-drift (diagnostic, no bar):**
  - Logged at every G4 point: the drift of H and of Q per return, for each map.
  - Compared with the convergence study: drift that does not shrink with rtol points to the field, which G0b-field
    should already have caught.
- **For the later MN work (not B15):** TheBridge's independently transcribed MN build (V15, whose vacuum residual is
  ≤ 7e-160 at the ring points) can serve as an independent SOURCE check of the MN sympy expressions: g_tt, g_tφ,
  g_φφ and e^{2γ} at about 20 shared points. This goes on the open-threads list.

**G1. Against MNFlow.**

- Run: `kerr_p_gate.py 12 2000 <lib>`, for kerr_rs and the fixed kerr_p, after E1–E4.
- Criterion: max relative difference ≤ 1e-10 in py, P, T, DP and Pinv. A return mismatch is a FAIL.
- The gate run started on 2026-10-24 loaded the unfixed kerr_p.dylib. It is a demonstration of the bug, not G1.

**G2. Cross-implementation.**

- Run: `kerr_rs_cross.py 200 2000 1`, after E1–E4.
- Criterion: ≤ 1e-10 in everything, with 0 mismatches.
- **Disclosed:** the pre-E1–E4 version has already been run:

  | Quantity | Worst relative difference |
  |---|---|
  | P | 2.2e-11 |
  | DP | 7.9e-13 |

  So G2 is not blind.

**G3. Symplectic check.**

- Criterion: |det DP − 1| ≤ 1e-8 at every G1, G2 and G4 point, for both libraries and MNFlow.

**G4. Long returns, with the criterion unscaled.**

- **Points, fixed now:**
  - seeds z* + s·e_u, for s ∈ {1e-4, 1e-3}, on both branches;
  - each iterated with kerr_rs until it comes back within 0.01 of z*, or until 200 returns;
  - from each of the 4 orbits, the first iterate past x = 2, 5, 10, 20, 50, 100, plus the iterate with the largest T.
    That gives ≤ 28 points. Ties go by iterate index.
  - **Pinv mirror:** seeds z* + s·e_s, s ∈ {1e-4, 1e-3}, on both branches, iterated with kerr_rs's Pinv, with the
    same x-thresholds and the same largest-T pick. These points are compared through Pinv.
  - **Near-saddle returns:** on each of the 8 orbits, the 2 iterates closest to z* after the first iterate past x = 5
    (ties by index). These have the largest gain and the longest near-saddle T.
  - That gives ≤ 72 points in all.
  - These are not constructor outputs. **Correction:** no journal of the main run exists, and the kill-test journal
    only reaches x ≤ 2.24 and T ≤ 730.
- **Compared:** one return (P, or Pinv for the mirror points) by kerr_rs, kerr_p and MNFlow (tmax 1e6).
- **Criterion:** ≤ 1e-10 relative in P, T and DP, unscaled.
- **Reference accuracy:** MNFlow self-convergence (rtol = atol = 1e-11, 1e-12, 1e-13) at the 3 points with the
  largest T. The reference is accepted only if its 1e-12 value is within 1e-11 relative of its 1e-13 value. A
  reference that fails this cannot gate.
- **On a failure:** self-convergence of each implementation at rtol = atol = 1e-11, 1e-12, 1e-13, 1e-14 on the failing
  points, to measure each one's actual error.
  - If a real floor appears, it gets its own registered amendment, with the measured error model and its cause.
  - Otherwise the tolerance is tightened and the whole gate set is rerun.
  - No scaled criterion.

**G5. End-to-end step 1.**

- Run: `find_periodic` from the seed with kerr_rs.
- Criterion: z within 1e-9 of the recorded Python step 1, and λ_u within 1e-8 relative of 62.62026858030255.
- This is a validation, since the Python step 1 is known.

**G6. Decision margins (runs alongside the counted run).**

- The constructor stays frozen. Margins are computed by a read-only wrapper and from the recorded data, not by
  editing hs_construct.
- **The decisions:**
  - Newton convergence (step 1);
  - the saddle classification;
  - each crossing's angle against the 0.01 minimum;
  - each angle against 10·θ_floor;
  - the accept/reject of a connection.
- eps, K and dmax are construction parameters, not comparisons. They are not decisions and get no margin.
- **Criterion:** margin ≥ 10 × (map error × local gain).
  - The map error is the measured G4 self-convergence error at the matching T.
  - The local gain is ‖DP‖ composed over the returns from the arc's initial segment to the decision point, taken
    from the map's own Jacobians; near the saddle that is about 62 per return.
- **A thin margin** is flagged. The calls feeding it are recomputed at rtol = atol = 1e-14.
- **Rule when the decision changes, fixed now:**
  - the 1e-14 decision is used;
  - both decisions are reported;
  - the step's result carries a flag;
  - every flag goes into the findings that the user sees.
- **If the 1e-14 margin is also thin** (below 10 × its own measured error × gain), the decision is UNRESOLVED. It is
  reported as such, and the step outcome is UNRESOLVED, not decided either way. (Quantum's addition, agreed by the Bridge: without it,
  a margin at the double-precision floor would be decided by noise.)

**On any failure:** fix the implementation or tighten the tolerances, and rerun all of G0–G5. A criterion is never
relaxed (B16 and the rigour rule). A criterion change is a new registered amendment, with its reason.

**B15b — The run (after G0–G5).**

- Script: b15_kerr_ck.py with B15_MAP=rust (default MNFlow), under pcache.
- New journal and JSON names. The Python step 1 is compared (G5), not reused.
- Resources: one process, not low-priority. No wall-time cap (B16).

**B15b-1 (2026-10-24): plunging orbits and step-size collapse in the compiled B15 maps.** Drafted by quantum and
reviewed by the Bridge over three revisions (B15B1_AMENDMENT_DRAFT.md; commits eeae26b, adc4daf, 302e6be, ffa111b,
bec3553). Registered with the user's OK BEFORE G0, G1, G3, G4, G5 or G6 was run; G2 (all its points return) is
unaffected. It amends B15b's failure codes and adds gate G0c. B15's procedure, thresholds and prediction are unchanged.
**B15b-1 — What was found.**

A development check of two returns (kerr_rs_cross.py, 100 points, n = 2, tmax 4000; not a registered gate) hung
for over an hour.

- **The point:** index 44 of that sample, w = (1.84065670, 5.39481249e-4). The first return is fine (T = 696.8). Its
  second return plunges toward the horizon.
- **Diagnosis:** scipy DOP853 with MNFlow's own field and tolerances:
  - x falls to 1.000000 and p_x to −6.9e10;
  - the step size collapses to 1.5e-12 at t ≈ 617;
  - solve_ivp stops with status −1, "Required step size is less than spacing between numbers".
- **Why it hangs:** x = 1 is a coordinate singularity of this chart. The integration cannot pass it, so t never
  reaches tmax, the h < 1e-300 guard never triggers, and both compiled maps loop.
- **What MNFlow does:** it returns None ("no return") for this orbit, and it gets there through an integrator
  FAILURE (t_events is empty after status −1).

**Finding about the registered reference, and a limitation of the running Python B15.** MNFlow maps EVERY scipy
failure to None, which is the geometric statement "no return", plunge or not. The Python B15 run (b15_kerr.py,
PID 24176, non-checkpointed, to be stopped at the macOS update) therefore treats any non-plunge integrator failure
as geometry, silently. Its in-memory state cannot be audited. This is stated as a limitation of that run's results.
MNFlow itself is not changed, since B15 registered it.

**B15b-1 — Semantics: unchanged from MNFlow, except for WHY "no return" is given.**

The registered semantics stay as they are: integrate until the next upward crossing of y = 0, or until the
integration cannot continue.

**Correction to revision 1 and to the review's (a).** A trigger at x − 1 < 0.05 would CHANGE the semantics:

- an orbit inside x < 1.05 can still cross y = 0 upward before it reaches the horizon;
- MNFlow counts such a crossing as a genuine return;
- a 0.05 trigger would turn it into "no return".

So there is no domain threshold. The trigger is the step-size collapse, which is the same point at which MNFlow
gives up. The certificate then justifies "no return" for that orbit, or the call fails.

**P1. Step-size collapse.**

- If an accepted step has h < 1e-14·max(1, |t|), the library stops and returns −2 ("collapsed"), together with the
  state at the collapse.
- −1 keeps its registered meaning: an E2 or E5 check failed.
- The h < 1e-300 guard stays as a backstop and returns −1.

**P2. The plunge certificate (Kerr only; exact rational arithmetic).** It is run by the adapter on every −2.

- **Constants from the START of the call, exactly.** The integrated orbit starts at the doubles (x0, 0, px0, py0),
  with py0 being the lifted double the integration actually used. Its constants are exact rationals of those
  doubles: E and L (the B15 parameters), μ² = −2H(start) and Q(start). There is no dependence on integration drift.
- **The orbit's position from the collapse state.**
  - r_c = M + k·x_c, and the margin is r₁ = M + k·(x_c + δ), where M + k = r₊ = 128 exactly, since k = 39.
  - δ = max(1e-6, 100 × the largest G4-measured state error) covers the integration error of the non-rigorous
    map. It is derived from G4, not chosen, and fixed before the run. The R > 0 interval's upper end is pushed OUT by
    δ, so the interval is conservative (the review's condition 1).
  - **δ measured AT the plunge (the review's condition 2).** The G4 error comes from regular returns, and the collapse
    state sits in the chart's singular regime (p_x ~ 1e10). So on EVERY −2, in the gates and in the counted run, the
    same call is recomputed at rtol = atol = 1e-14.
    - **Where the difference is taken:** at a COMMON time t* = 0.999 × the smaller of the two collapse times, using a
      plain integration to t* with no events (a new library entry, kerr_state_at).
    - **What is compared:** the two states' r = M + k·x and y.
    - **Why not compare the collapse states directly:** the two tolerances stall at different points along the orbit,
      so their collapse states are not at the same time.
    - **Two common times, not one (the Bridge's addition):** the difference is taken at t* = 0.99 and at
      t* = 0.999 × the smaller collapse time. If it grows by more than 10× between the two, the plunge is −1: the error
      is growing steeply in the last 0.1%, where p_x blows up, so the difference cannot be extrapolated to the
      collapse.
    - **Requirement:** δ ≥ 10 × the larger of the two values of max(|Δr|/k, |Δy|). Otherwise the plunge is −1 (raise),
      not certified. A failure of the 1e-14 recompute is also −1.
  - A fixed 0.01 margin was considered and rejected. In (ii) it would fail every plunge with |y_c| < 0.01, which is roughly
    1% of them if y_c is spread evenly (an estimate, not measured), each as a run-stopping HARNESS-ERROR, for an error that is really around 1e-10.
- **(i) No turning point.** R(r) > 0 on [r₊, r₁], where
  R(r) = [E(r² + a²) − aL]² − Δ[μ²r² + (L − aE)² + Q].
  - It is certified twice, independently, and both must certify:
    - a Sturm root count of 0 on [r₊, r₁] (sympy, exact rationals);
    - an interval evaluation by bisection (mpmath.iv), down to 2⁻⁴⁰ of the interval.
  - With ṙ < 0 at the collapse (the sign of p_x), the orbit reaches r₊ without turning.
- **(ii) No section crossing before the horizon.** The certificate in (i) proves a plunge, not "no return": the θ
  motion could still cross y = 0 between r_c and r₊. In Mino time λ the motions separate, so this is bounded:
  - the remaining Mino time is Λ ≤ (r₁ − r₊) / min over [r₊, r₁] of √R (interval bound);
  - |dy/dλ| ≤ √(Q + a²·|E² − μ²|).
  - Certified "no return" requires |y_c| > Λ·√(Q + a²|E² − μ²|) + δ, with the same δ for the state's error.
- **(iii) The certifier's dependencies.** The certifier uses the convention mapping of G0b-field (x ↔ r, y ↔ cos θ,
  p_x = k·p_r, the source's (E, L) and the w0 shift ↔ Kerr's (E, L_z), and the SIGN of a). R depends on a·L and
  a·E, so the sign matters here, whereas G0b-field's Q only sees a². Hence a new gate:
  - **G0c (exact):** at 20 random rational points, as in G0b-field, (Σ·k·ẋ)² = R(r) exactly, with
    Σ = r² + a²y² and ẋ from the source's field. This validates the E/L/a mapping, the sign of a, and that the
    field's time is the one R refers to: if the field's time were regularised, the identity would fail.
  - The certifier may be used only after G0b-field and G0c pass.
- **Outcome:**
  - Both certifiers succeed on (i) and (ii): the adapter returns None (no return) to the frozen constructor, and
    logs the reason 'plunge-certified' with the start, the collapse state and the certificate data.
  - Anything else: MapCheckFailed (HARNESS-ERROR).

**P3. Diagnostics: every certified plunge seen in G1, G2 or G4, and in the run.**

- MNFlow from the same start, with its None ROUTE recorded.
- Optionally, the compiled orbit continued (diagnostic switch) to show x − 1 < 1e-3.

**P4. Reference None routes, in G1 and G4 (the review's (c), adopted).**

- Every MNFlow None is labelled by route: 'tmax' (sol.t reached tmax with no event), 'status −1', or 'other'.
- **Agreement:** MNFlow None via status −1 and compiled 'plunge-certified'. This agrees, with the reason logged.
  So does MNFlow None via 'tmax' and compiled 0 (tmax).
- **Every other combination** with a None on one side is a mismatch, and therefore a FAIL, as registered.

**P5. In the counted run.**

- The summary counts certified plunges and −1/−2 failures by kind. The expectation for uncertified collapses is 0.
- G6 gains a decision, "no return (certified plunge)", with the certificate's slack as its margin: the minimum of R
  over [r₊, r₁], and |y_c| minus the bound. A slack below its registered margins is already a −1, so G6 logs it for
  completeness.

**B15b-1 — What it does not change.**

- MNFlow, and the frozen constructor's reading of None.
- Every registered B15b gate and criterion. G0c is added.
- **For the later MN work**, which is non-integrable and has no radial certificate: a threshold-plus-MNFlow fallback
  would need its own amendment then.

**B15b-2 (2026-10-24): crossings on chords across dropped arc points.** Drafted by quantum, agreed by the Bridge
with no changes (B15B2_AMENDMENT_DRAFT.md, 5cf2b35), registered with the user's OK BEFORE G6 was implemented and
before any counted B15 run. It governs only how step 2's output is classified.
**B15b-2 — The finding.**

- **What the code does:** hs_construct.manifold_arcs drops an arc point whose image is None (no return) and joins its
  surviving neighbours directly. Under the compiled maps (B15b-1), every None is a certified plunge (or tmax).
- **The consequence:** across a plunge cut, the polyline contains a CHORD, a straight segment where the true manifold
  falls into the black hole. hs_construct.crossings treats a chord like any other segment.
- **So:** a crossing of W^u and W^s found ON a chord is a polyline artefact, not a manifold crossing. If the only
  accepted crossings (D6, angle ≥ 0.01) lie on chords, B15's step 2 would report a connection that is an artefact.

**B15b-2 — The rule (fixed before any counted run).**

1. **Chords** are identified by G6's replica of manifold_arcs' bookkeeping (original parameters and drops). The
   replica must reproduce the saved arcs bit for bit (B15b G6, completeness).
   - A segment at level k is a chord if any point whose original parameter lies strictly between its two endpoints'
     parameters was dropped at any level ≤ k.
2. **A D6-accepted crossing on a chord** (on either curve) is UNRESOLVED, not a connection. It is reported and
   flagged to the user.
3. **D8 (connection accepted)** counts only crossings that are not on chords.
   - If the only D6 accepts are on chords, the step-2 outcome is UNRESOLVED.
   - If at least one non-chord crossing is accepted, D8 holds as registered, and the chord accepts are still reported.
4. **Chord crossings that D6 rejected** (angle < 0.01) are recorded as data. They do not change the outcome.
5. **If the replica does NOT reproduce the arcs,** chords cannot be identified. G6 is then INCOMPLETE, and any D8
   accept is UNRESOLVED (the conservative reading), with no exception.

**B15b-2 — Also recorded.**

- **A limitation of the old Python B15 run** (MNFlow; stopped at the macOS update and not relaunched): its arcs had
  the same drop-and-join behaviour. Its Nones also include scipy failures, not only plunges (B15b-1). That run's
  in-memory arcs cannot be audited.
- **The scope limit of steps 3–4:** b15_kerr_ck.py stops with "steps 3–4 required" if a connection is accepted, and
  implements neither step.
  - If that happens, the run ends with that status (not an exception), and the findings say: "registered prediction
    NOT CONFIRMED because of an implementation scope limit (steps 3–4 not implemented); this is not a negative
    result."
  - Steps 3–4 would need code and their own amendment before running.

**B15b-2 — What it does not change.**

The frozen constructor, every B14 and B15 threshold, and the registered prediction. The rule only governs how the
run's step-2 output is classified.

**B15c (2026-11-21): steps 3–4 for B15's candidate connections (sets, then rigorous coverings).** Drafted by quantum
(first draft 947f1cf); the Bridge approved it with required changes, folded in here, and relayed it for registration on
2026-11-21. Registered BEFORE any B15 step 3–4 computation; nothing below has run. Drafting record:
`qsim/capd/horseshoe/B15C_STEPS34_DRAFT.md`. This text governs.

**What already governs this, unchanged:**
- **B14:** the frozen constructor, `hs_construct.py`, unedited: its steps 3–4 text, the ladder, S8, and the
  required/optional split.
- **B15:**
  - steps 3–4 run only if step 2 returns an accepted connection (angle ≥ 0.01);
  - any sets that are built go to rigorous hs_cover with the B13 settings;
  - the prediction is "no rigorous ρ > 1".
- **F7:** any rigorous ρ > 1 on Kerr STOPS the MN claim.
- **B15b / B15b-1 / B15b-2:** the compiled rust map, the plunge certificates, and the chord rule.
- **B16:** no wall-time cap.

B15c supplies the implementation and the order that step 2's outcome now requires. B15_FINDINGS.md records 147
accepts and "steps 3-4 required". No threshold, ladder value or prediction changes.

**B15c — 1. Candidates and order.**
**T1, the counted chain.** B14 builds ONE chain: from the connection minimising |k_u| + |k_s|, with ties broken by
the largest angle. On the recorded step 2 (b15_kerr_rust.json), that is **crossing #4155**:
- k_u = k_s = −3, angle 0.045861, point (104.50074766, −1.1e−10);
- it is a measured-error accept.

The 147 accepts split as follows:

| (k_u, k_s) | count | error |
|---|---|---|
| (−3, −3) | 81 | measured |
| (−4, −3) | 33 | extrapolated |
| (−3, −4) | 33 | extrapolated |

**The tiers:**
- **T1 (COUNTED, the registered B15 path):** steps 3–4 on #4155, exactly as in B14.
- **T2:** the other 80 measured accepts, each its own chain, through the same steps 3–4. Order: B14's
  (|k_u| + |k_s|, then −angle, then crossing index).
- **T3:** the 66 extrapolated accepts, after T2, in the same order and under the same rules. They are labelled
  "extrapolated-error accepts".

**F7 covers every tier:** any rigorous ρ > 1 on any Kerr chain (T1, T2, T3, or the diagnostic arm of §4) STOPS the MN
claim.

**Duplicates:** if two chains produce byte-identical exact-rational specs, only the first is covered. The later one is
recorded as a duplicate of it.

**B15c — 2. Step 3: refine, orbit, frames.**
**The driver.** `b15_steps34.py` calls only the frozen `hs_construct` functions, through
`mn_numerics.plug_into_constructor` with the compiled map, as b15_kerr_ck.py does:
- B15_MAP = rust;
- kerr_rs with its sha256 checked against the step 1–2 run (42ea6c3c…);
- delta_floor and the plunge log as in that run;
- a NEW journal name.

A MapCheckFailed stops the run as a HARNESS-ERROR. It is never recorded as a rejection.

**For each candidate c:**
1. **Signs.** k_u = |c.k_u| and k_s = |c.k_s|. s_u = sign(c.k_u), or +1 if that is 0; s_s likewise. This is the HH
   driver's handling (hs_construct_hh_chain.py), which HH-SECONDARY used.
2. **Refinement.** Call `refine_connection(z, s_u e_u, z, s_s e_s, k_u, k_s, c.point)`.
   - If it returns None, the chain stops at **"step 3: refinement failed"**.
   - Recorded as DATA:
     - t, τ and the residual;
     - the 2×2 FD Jacobian at the solution, recomputed by the same formula, and its condition number;
     - **the solution's distance to the saddle,** ‖h − z‖;
     - **|Q(X_m) − Q_s| and max_j |Q(X_j) − Q_s|.** Here Q(X) = p_y(X)², with p_y from the map's py_of. On y = 0, Q = p_y²
       (B15b-1). Q_s is B15's registered 0.740762452760964 M² × 89².

   A "converged" refinement that sits on the family of coinciding manifolds can then be read as such, and not taken for
   a transversal connection.
3. **Orbit and frames.** m = k_u + k_s.
   - X_j = tangent_fwd(z, s_u e_u, t, j)[0], with U_j from the same call;
   - S_j = tangent_back(z, s_s e_s, τ, m − j)[1];
   - for j = 0 … m.

   Recorded: ‖X_m − (z + τ s_s e_s)‖.

**Disclosures:**
- **A frozen HH constant.** refine_connection's coarse start scans |t|, |τ| ∈ geomspace(1e−4, 7.3e−4). The 7.3 is HH's
  λ_u. Kerr's fundamental segment is [1e−4, 6.26e−3] (λ_u = 62.62). The constant is NOT changed. If T1 fails at
  refinement, the diagnostic arm of §4 runs.
- **Expected degeneracy.** Kerr is integrable. On the section, both manifolds lie on the separatrix level {Q = Q_s},
  whose only singular point is the saddle. So W^u and W^s coincide as curves, and the Newton system for (t, τ) is
  singular up to integration noise. Refinement may fail, wander, or converge ill-conditioned. Whichever happens is the
  recorded outcome.

**B15c — 3. Step 4: the ladder.**
B14's text, implemented as in hs_construct_hh_chain2.py:
- **Ladder order:** a0 ∈ (0.03, 0.02, 0.015, 0.01), a ∈ (0.01, 0.005, 0.0025), b0/a0 ∈ (0.5, 0.25, 0.1) and
  b/a ∈ (0.5, 0.25, 0.1).
- **The sets:** N0 = (z, a0 e_u, (b0/a0)·a0·e_s). The chain is the contiguous run j₁…j₂ of orbit points whose sets are
  disjoint from N0 and from each other.
- **The check:** `sampled_cover(…, n_edge=12, n_int=8)`.
- **Acceptance:** the FIRST entry where every REQUIRED covering passes. The required coverings are N0⇒N0, N0⇒N_{j₁},
  N_j⇒N_{j+1} and N_{j₂}⇒N0. The optional N_{j₂}⇒N_{j₁} is recorded but not required.
  - Disclosure: hs_construct_hh_chain2.py's own stopping test also included the optional edge. B14's text (required
    only) governs, and HH-SECONDARY used it.
- **No return:** a None from sampled_cover (a sample with no return, i.e. a certified plunge) means that covering FAILS.
- **No pass:** if no entry passes, the chain stops at **"step 4: no ladder entry"**. Per entry, n_ok/n and the failing
  edges are recorded.

**B15c — 4. Rigorous stage (only for chains with an accepted ladder entry).**
**The spec,** exactly as in hs_run.hh2:
- Sets are converted to exact rationals rounded to 1e−10.
- **S8 gate:** S8 must hold exactly (convex_disjoint). If it fails, the chain stops at "S8" and nothing is launched.
- Header: `system mn`, `prec 128`, `order 20`, `iter 1`, and the params k = 39, alpha = −5/8, beta = 0, E = 49/50,
  L = 445/2. These are the B15 level; the codegen gate's B15_KERR case passed there.
- Then `caps 65536 4096`, `depth 16 12` and `cover x y 16 16 64`, with one checkpoint per covering.
- S4 and S9 are on. There is no piececap (B16).

**The binary.**
- It is a fresh guarded build (proof_guard.h) of hs_cover.cpp at the registration commit. Its sha256 is recorded before
  any run.
- **Gate GB:** before the counted coverings, the binary must exactly reproduce the R1 generic Rössler COVER lines and
  the HH-SECONDARY N0⇒N0 COVER line.

**Outcome classes per covering,** from hs_cover's own output:

| Class | Condition |
|---|---|
| CERTIFIED | `COVERS=1`, `DONE` present, and no `FAILPIECE … CERTIFIED` line |
| CERTIFIED-FAIL | at least one `FAILPIECE … CERTIFIED` line, with `COVERS` ≠ 1 |
| UNDECIDED | anything else (see below) |
| HARNESS-ERROR | both `COVERS=1` and a `FAILPIECE … CERTIFIED` line; this is never given a class |

UNDECIDED includes:
- only uncertified FAILPIECE lines (cap, depth, S4/S9 fail-closed, exceptions);
- `FATAL`;
- no `DONE`, even with `COVERS=1`.

**Per chain:**
- **ρ > 1** when every required covering is CERTIFIED. This triggers the **F7 STOP**.
- **CERTIFIED-FAIL** when some required covering is CERTIFIED-FAIL.
- **UNDECIDED** otherwise.

**Diagnostic arm (agreed).** It runs only if T1 stops at "step 3: refinement failed".
- It repeats T1's refinement with the coarse scan scaled to Kerr's fundamental segment, geomspace(1e−4, 1e−4·|λ_u|).
  Everything else is identical, through every later stage.
- It is labelled **UNFROZEN / NOT COUNTED**. F7 still applies to it.

**B15c — 5. Reading the prediction (the vacuous-pass guard).**
"No rigorous ρ > 1" is trivially true when no chain reaches a decided covering. So:
- **A chain supports the B15 prediction ONLY if it ends CERTIFIED-FAIL.**
- **A chain that stops anywhere else is NOT TESTED for the prediction.** That means "step 3: refinement failed",
  "step 4: no ladder entry", "S8", or UNDECIDED.
- **The B15 headline must give the counts at each stage, per tier:** refinement failed / no ladder entry / S8 /
  UNDECIDED / CERTIFIED-FAIL / ρ > 1 / duplicate.
- **It then states one of:**
  - "B15 prediction: supported by N chains" (N = CERTIFIED-FAIL chains, with T1's own status given first);
  - "B15 prediction: NOT TESTED" (N = 0);
  - "F7 STOP" (any ρ > 1).
- **It is never a bare "no ρ > 1 found".**
- T1's status is the counted B15 outcome. T2, T3 and the arm add chains but do not replace it.
- **The red-flag sub-prediction** (B15 step 2: "no transverse crossing above the red-flag level") is recorded as
  **"NOT TESTED: degenerate as implemented (θ_floor = 0 at 9437/10081)"**. See §7.

**B15c — 6. Controls (non-counted).**
Each control exercises a clause and can produce the outcome it guards. The scorer is `b15c_controls.py`. All controls
must PASS before T1 runs, and before the rigorous stage for the rigorous ones. A control that comes back "not decided"
is reported to the Bridge, and the stage it guards waits.

1. **Selection.**
   - On the recorded step-2 list the T1 selector returns #4155, and it still does on a shuffled copy.
   - On a toy list with a tie in |k_u| + |k_s| it returns the larger angle.
   - The T2 and T3 orders equal B14's sort.
2. **Positive control: the driver reproduces HH-SECONDARY.** The driver, with the HH map plugged in (the HH originals are
   saved before Kerr is plugged), is applied to HH's recorded Π4 crossing. It must reproduce:
   - hh_chain_explore.json's X, U and S (to 1e−12);
   - the ladder entry (0.03, 0.01, 0.5, 0.5) with chain [3, 4, 5, 6];
   - byte-identical hh2 exact sets.

   It runs in the same process after a Kerr candidate, so the map switch is exercised too.
3. **Planted reject, discriminating** (the Bridge's rule: a control must be able to produce the outcome it guards).
   - **Primary.** HH-SECONDARY's known-passing chain (entry (0.03, 0.01, 0.5, 0.5), chain [3, 4, 5, 6]) with U ↔ S in
     every set. Its ladder is run with the HH map.
     - It is seeded into the T2 list at a position drawn from a seed. The seed is sealed in gitignored scratch and only
       the scorer reads it.
     - It must give "step 4: no ladder entry". **FAIL** if any entry passes.
     - The unswapped chain passes at that entry (HH-SECONDARY), so the ladder can accept. The control therefore
       discriminates.
   - **Extra, not deciding.** A copy of #4155 with U ↔ S, seeded the same way, with its result reported. Integrable
     Kerr may give no ladder entry for #4155 itself, so this copy cannot decide the control.
   - **Rigorous twin (deciding).** HH-SECONDARY's CERTIFIED sets (hh2, COVERS = 1 on every required covering) under the
     GB binary, run twice:
     - (a) with U ↔ S;
     - (b) with U rotated by 90°. If that makes a frame singular, R1's W2 form (U and S both rotated) is used instead,
       and this is recorded.

     Each variant must be CERTIFIED-FAIL in at least one required covering. UNDECIDED counts as "control not
     decided", not as a pass. T1-based twins may run as extras, but they do not decide.
4. **Plunge clause.** On the toy flow (b15b_toyflow) with a planted None at one sample, sampled_cover must return None,
   the covering must FAIL, and the run must continue.
5. **MapCheckFailed clause.** A toy map that raises MapCheckFailed must stop the driver with a HARNESS-ERROR. No
   rejection may be recorded.
6. **S8 clause.** A planted overlapping pair must trip the exact S8 gate, and no hs_cover process may start.
7. **Outcome classifier,** on canned hs_cover outputs:

   | Canned output | Must give |
   |---|---|
   | COVERS=1 + DONE | CERTIFIED |
   | a FAILPIECE…CERTIFIED + DONE | CERTIFIED-FAIL |
   | only cap/depth FAILPIECEs + DONE | UNDECIDED |
   | FATAL | UNDECIDED |
   | no DONE | UNDECIDED |
   | COVERS=1 AND a FAILPIECE…CERTIFIED | HARNESS-ERROR |
   | uncertified FAILPIECEs only | UNDECIDED, never CERTIFIED-FAIL |
   | COVERS=1 without DONE | UNDECIDED |

   Chain-level checks:
   - an all-CERTIFIED Kerr chain writes the F7 STOP flag;
   - a chain with one UNDECIDED required covering does NOT give ρ > 1;
   - the headline writer, fed only NOT TESTED chains, prints "NOT TESTED", never "no ρ > 1".
8. **Duplicates.** Two identical candidates: the second is marked as a duplicate, and only one hs_cover spec is
   written.

**B15c — 7. Order, resources, reporting.**
**Order:**
1. Melnikov stage-2 verdict committed.
2. A3 launched.
3. The controls (1–2 and 4–8, and 3's constructor parts).
4. T1 steps 3–4. If T1 stops at refinement, the diagnostic arm runs.
5. The T2 constructor stage, then the T3 constructor stage.
6. A slot request to the Bridge, then gate GB and control 3's rigorous twin.
7. T1's rigorous coverings, then a report.
8. T2's rigorous coverings, then T3's, after the Bridge confirms the slot.

**Resources:**
- **Constructor stage:** one Python process at nice 10, with an RSS guard at 1 GB and a disk guard.
- **Rigorous stage:** up to 4 cores (within the 8-core fleet limit, checked by the Bridge against the other sisters),
  at nice ≥ 10, with a guard on every process.

**Reporting:**
- Per chain: the stage where it stopped, the §2–§3 data, and per covering the class with its leaf and fail counts.
- The §5 headline.
- UNDECIDED is never merged into "fails".

**B15c — 8. Post-result finding about B15's red-flag record (B15_FINDINGS.md §4).**
- **Duplicate points.** The frozen manifold_arcs appends a point before its refinement check, and the `continue`
  revisits it. So every refinement leaves a duplicate point. For example, u_−3 has 2192 zero-length segments out of
  4423.
- **Effect on the floor.** B15's floor_at takes the turn between neighbouring segments, which often have zero length. So
  θ_floor = 0 at 9437 of the 10081 crossings, and the red-flag clause is **NOT TESTED: degenerate as implemented**.
- **A post-result DIAGNOSTIC only, not the red-flag test.** With duplicates removed, all 147 accepts have angle / θ_floor
  of 0.16–0.82 (#4155: 0.59). This is not presented as the red-flag test passing.
- **Arc resolution.** The arcs also exceed dmax: u_−3 has 2178 segments longer than 0.01, the longest 0.146, because the
  maxpts cap is reached.
- **Crossing detection is unaffected,** because zero-length segments have den = 0 and are skipped.
- **The steps 3–4 trigger is B14's angle ≥ 0.01,** so T1 runs.

**B15c-1 (2026-11-21): a certified ORIENTATION failure counts as CERTIFIED-FAIL.** Found by quantum while writing the
classifier, before any B15c computation. The Bridge agreed to the wording, with one added control case. Registered
BEFORE any run.
- **The gap.** hs_cover reports a certified orientation failure only on the COVER line, as `orient_certified_fail=1`
  (certified edge landings that contradict every consistent orientation), never as a `FAILPIECE … CERTIFIED` line.
  - Precedent: HH-SECONDARY's optional N6⇒N3, `COVERS=0 … orient_certified_fail=1`, has no FAILPIECE lines. The prereg
    calls it "a certified orientation failure".
  - Under B15c §4 as first registered, such a covering would have been UNDECIDED.
- **The rule (it replaces B15c §4's CERTIFIED-FAIL and HARNESS-ERROR rows):**
  - **CERTIFIED-FAIL** = `DONE` present, `COVERS` ≠ 1, AND (at least one `FAILPIECE … CERTIFIED` line OR
    `orient_certified_fail=1` on the COVER line).
  - **HARNESS-ERROR** = `COVERS=1` together with a `FAILPIECE … CERTIFIED` line, or `COVERS=1` together with
    `orient_certified_fail=1`. The code makes either combination impossible, so it signals a harness or parse fault and
    is never given a class.
  - CERTIFIED and UNDECIDED are unchanged.
- **Control 7 gains three canned cases:**
  - the HH N6⇒N3 COVER line, verbatim from hh2_run.out, with DONE → CERTIFIED-FAIL;
  - `COVERS=1` with `orient_certified_fail=1` → HARNESS-ERROR;
  - `COVERS=0` with `orient_certified_fail=0`, no FAILPIECE lines, and DONE → UNDECIDED. This guards against the new OR
    branch swallowing plain undecided outputs (the Bridge's addition).
- Nothing else in B15c changes.

**B15d (2026-11-21): the rigorous stage on Kerr, with fixed sets on the B15c arm's chain.** Drafted by quantum (first draft
3a2e55b); the Bridge approved it with one added control (the frame-recipe positive control) and one wording change, both
folded in, and relayed it for registration. Registered BEFORE any B15d computation. Drafting record:
`qsim/capd/horseshoe/B15D_DRAFT.md`. This text governs.

**What it tests.** Rigorous hs_cover on integrable Kerr data, in two respects:
- **Soundness:** it must never certify a false covering. F7 applies unchanged: any ρ > 1 STOPS the MN claim.
- **Decidability:** whether hs_cover can decide coverings at all across the long Kerr homoclinic swing (out to r = 46.8M).

It is explicitly a test of the rigorous stage, not of the frozen constructor. The chain comes from the UNFROZEN
diagnostic arm, and the sets are fixed here instead of chosen by the sampled ladder.

**B15d — 1. The chain.**
- **Source.** The arm's refined orbit (horseshoe_results/kerr/b15c/ARM.json, committed 73230b5):
  - X_0 … X_6 (m = 6) and U_j, the propagated W^u tangents;
  - the saddle z with e_u and e_s.
- It lies on the separatrix level set: |Q(X_j) − Q_s| ≤ 2.8e−10 relative.

**B15d — 2. A finding that shapes the sets: the B14 frames are numerically singular on Kerr.**
- Along the arm's chain, the B14 frame (U_j, S_j) has |sin∠(U_j, S_j)| equal to:

  | j | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
  |---|---|---|---|---|---|---|---|
  | sin∠(U_j, S_j) | 1.9e−3 | 5.3e−7 | 3.7e−10 | 2.6e−10 | 6.0e−11 | 5.7e−8 | 2.2e−4 |

- This is integrability itself: W^u = W^s, so the two tangents are parallel up to noise.
- With |U| = a = 0.01, the transverse extent of N_2 … N_4 is ~1e−12. That is below the registered 1e−10
  rationalisation, so the exact sets would be artefacts of rounding.
- **B14 frames are therefore NOT proposed for B15d.** They are recorded as a finding (it also bears on B15c's reading:
  sampled covers on such slivers are uninformative).

**B15d — 3. Sets (fixed now).**
**Frames:**
- **N0:** B14's own frame at the saddle, (a0 e_u, (b0/a0)·a0·e_s). It is well conditioned, sin∠(e_u, e_s) = 0.031.
- **Chain sets, an orthonormal frame:** U_j as above (unit), and **S_j^⊥ = U_j rotated by +90°**. So
  N_j = (X_j, a·U_j, (b/a)·a·S_j^⊥).

**Sizes:** HH-SECONDARY's ladder entry (a0, a, b0/a0, b/a) = (0.03, 0.01, 0.5, 0.5), fixed. There is no ladder.

**Chain:** the B14 rule (hs_construct_hh_chain2.py) applied to these frames and sizes. It is the contiguous run
j₁…j₂ ⊂ {1 … m−1} of orbit points whose sets are disjoint from N0 and from each other.
- If no such run exists, B15d stops at "no chain". It is recorded as NOT TESTED, with no fallback.

**Coverings (B14):**
- required: N0⇒N0, N0⇒N_{j₁}, N_j⇒N_{j+1} and N_{j₂}⇒N0;
- optional: N_{j₂}⇒N_{j₁}.

**Exact sets:**
- rationals rounded to 1e−10, as in hh2;
- S8 must hold exactly, or B15d stops at "S8" (NOT TESTED);
- a singular exact frame stops it at "singular frame".

**What the orthonormal frame means physically:**
- Along S^⊥ the sets cross the separatrix level set. On one side lie the bounded orbits; the other side includes
  orbits that plunge, which hs_cover's S4 domain check fails closed.
- So UNDECIDED pieces are expected. A certified failure needs only one certified leaf or orientation contradiction (the
  B15c-1 rule).

**B15d — 4. The rigorous run.**
- **Spec, as B15c §4:**
  - `system mn` at the B15 level (k 39, α −5/8, β 0, E 49/50, L 445/2);
  - prec 128, order 20, iter 1;
  - caps 65536 4096, depth 16 12, `cover x y 16 16 64`;
  - checkpoints; S4 and S9 on; no piececap (B16).
- **Classes:** the B15c / B15c-1 classifier, unchanged (CERTIFIED / CERTIFIED-FAIL / UNDECIDED / HARNESS-ERROR). All
  required and optional coverings run, even after a CERTIFIED-FAIL, so that decidability is measured.
- **Gates and controls before the counted coverings** (B15c §4 and §6.3, unchanged):
  - **gate GB:** the fresh guarded hs_cover build reproduces the R1 generic Rössler COVER lines and HH-SECONDARY's N0⇒N0
    line exactly;
  - **control 3's rigorous twin:** HH-SECONDARY's CERTIFIED sets with U ↔ S, and with U rotated 90° (W2 fallback if
    singular), must each be CERTIFIED-FAIL in ≥ 1 required covering. All 6 required coverings run for each variant.
    UNDECIDED means "control not decided", and B15d waits.
  - **Frame-recipe POSITIVE control (the Bridge, required).** The SAME recipe is applied to HH-SECONDARY's Π4 chain
    (hh_chain_explore.json: X_j, U_j, m = 8; saddle eigen-frame for N0): N0 = (z, a0 e_u, (b0/a0)·a0·e_s); chain sets
    (X_j, a·U_j, (b/a)·a·U_j⊥); sizes (0.03, 0.01, 0.5, 0.5); the B14 chain rule; exact sets at 1e−10 with S8; hs_cover
    with system hh and the B13 settings, all required and optional coverings.
    - **RECIPE-POSITIVE:** every required HH covering is CERTIFIED (so ρ > 1 for HH under the recipe). The recipe can
      succeed, and a Kerr CERTIFIED-FAIL is informative.
    - **RECIPE-NEGATIVE:** anything else (a required covering CERTIFIED-FAIL or UNDECIDED, or a stop at "no chain",
      "S8" or "singular frame"). A Kerr CERTIFIED-FAIL is then NOT support (§5).
    - It is read from its own hs_cover outputs, before any Kerr covering result is read.

**B15d — 5. Prediction and reading (registered before the run).**
- **Prediction:** NOT ρ > 1, and CERTIFIED-FAIL in at least one required covering.
- **Readings:**
  - **ρ > 1:** F7 STOP. This would be a soundness failure of the rigorous stage, or a physics error, and is treated as the
    STOP rule requires.
  - **CERTIFIED-FAIL** in ≥ 1 required covering, and the recipe control RECIPE-POSITIVE: reported as **"B15d: the
    rigorous stage certified a failure on integrable Kerr data with a recipe that certifies HH (unfrozen-derived chain)"**.
    Never as a bare "prediction supported". It is not a test of the frozen constructor.
  - **CERTIFIED-FAIL** in ≥ 1 required covering, but the recipe control RECIPE-NEGATIVE: **"soundness only: no false
    certificate on Kerr"**. This is NOT support for the B15 prediction, since badly aligned sets fail even on chaotic
    systems.
  - **UNDECIDED** on every required covering: **"tool limit on Kerr"**. This is NOT support. It is reported with the
    per-covering leaf and fail counts, the piece failure reasons (S4/S9/enclosure), and the return times. That
    decidability record is a direct input to the MN covering plans.
- **The headline gives** per covering: class, leaves, fails, certified fails, orient_certified_fail, return time, replay
  steps and wall time.

**B15d — 6. Resources and order.**
- **Order:** gate GB; then the HH twin (6 required coverings × 2 variants) and the frame-recipe control (its required
  and optional coverings); HH's coverings took 17–80 min each in hh2. Then B15d's Kerr coverings: L + 2 required for a
  chain of length L (3 to 7), plus 1 optional.
- **Slot (the Bridge, 2026-11-21):** 2 hs_cover processes now, rising to 4 when the Bridge says so.
- **Cuspis night condition (firm):** on the night Sumit picks for Cuspis's r = 8 run, every hs_cover process of this line
  is STOPPED by verified PID before he closes the app (they are checkpointed), and resumed afterwards. A3 may keep
  running.
- **Compute:** at most 4 hs_cover processes at once, nice 10, one guard each (RSS cap 1 GB, disk < 5 GB at once). Wall
  time for Kerr returns is unknown; B16 sets no cap. Everything is checkpointed and detached.
- **Expected disk:** small (hh2's checkpoints were 268 KB in total).

**B15d-1 / GB-1 (2026-11-21): how gate GB compares outputs.** Found by quantum before the gate ran; the Bridge agreed to
the wording and asked for the reason to be recorded. Registered BEFORE GB runs.
- **Why byte-exactness is impossible for R1.** The R1 generic Rössler COVER lines were written by the R1 binary (ffd94bf,
  2026-10-16), in hs_cover's OLD output format (`pieces_a`, `pieces_b`, `replay_steps=0`). Since adaptive bisection
  (921ee47), hs_cover prints other fields: `leaves_a/leaves_b`, `certified_fail_b`, `orient_certified_fail`,
  `maxdepth_a`, and the real `replay_steps`. No current build can reproduce those lines byte for byte. The gate is
  changed because of that format change only, not for convenience.
- **The rule.**
  - **HH-SECONDARY N0⇒N0:** the FULL current-format COVER line must match exactly (hs_cover_v4 already wrote it in this
    format), run with a fresh checkpoint path so that reloaded_pieces = 0 as in the original.
  - **R1 generic MM / MN / NM / NN:** the fields common to both formats must match exactly: a, b, strong_a, orient,
    fail_a, fail_b, return_time and COVERS. The new-format-only fields are recorded.
  - Any mismatch, a return_time mismatch included, is a FAIL. It holds B15d and goes back to the Bridge. Nothing is
    loosened after the fact.

**B15d-2 (2026-11-22): edges first, a labelled schedule amendment.** Proposed by quantum and approved by the Bridge
(2026-11-22, Sumit's standing rule). Registered BEFORE any edge-chunk (b) result exists: no `arange 0 0` run had been
made, and the two running twin coverings (rot90 N0⇒N0, rot90 N0⇒N3) were still in part (a) when this was written.
- **Why.** In hs_cover a certified failure can come only from part (b) (an edge leaf certainly in neither side:
  `certified_fail_b`) or from the orientation check (`orient_certified_fail`). Part (a) can never certify a failure: a
  failing (a)-piece only spends leaves. On the twin, failing (a)-pieces cost ~3.2k depth-cap leaves and ~4 h each, so
  part (a) of a single covering can take days before (b) is reached. Running (b) first makes the control's decisive
  outcome reachable in hours.
- **(ii) Nothing about the check changes.** Same binary (hs_cover_b15d, sha256 fb5fcbfc…), same exact sets, prec 128,
  order 20, iter 1, caps 65536 4096, depth 16 12, `cover <i> <j> 16 16 64`, S4/S9 on, no piececap. The only spec
  differences are the existing B13 options:
  - **edge chunk** = the registered spec + `arange 0 0` (no (a)-piece runs), no checkpoint line;
  - **(a) chunk** = the registered spec (same checkpoint path) + `noedges`.
- **Merge (the classifier never sees a chunk alone).** An edge chunk's own COVER line reads `a=1 … COVERS=1` vacuously
  whenever its edges pass, so a chunk output is NEVER passed to the classifier by itself. The merged classifier input
  is: the FAILPIECE lines of both chunks, then one merged COVER line, then DONE (only if both chunks end in DONE with
  no FATAL; otherwise no merged COVER line, so UNDECIDED).
  - Validation, any failure ⇒ HARNESS-ERROR:
    - exactly one COVER line in each chunk, for the same source and target;
    - the (a) chunk shows `b=skip orient=skip COVERS=chunk-a-only` and `chunk_a=[0,nu) edges=no`;
    - the edge chunk shows `chunk_a=[0,0) edges=yes a=1 fail_a=0 leaves_a=0 maxdepth_a=0`.
  - Merged COVER line, in hs_cover's own field order:
    - from (a): `a`, `strong_a`, `fail_a`, `leaves_a`, `maxdepth_a`;
    - from (b): `b`, `orient`, `fail_b`, `certified_fail_b`, `orient_certified_fail`, `leaves_b`;
    - `replay_steps` = the sum; `return_time` = the hull of the two printed intervals (`none` if both are `none`);
    - `COVERS = 1` iff a=1 and b=1, else 0;
    - suffix `chunk_a=[0,nu) edges=merged reloaded_pieces=<(a)'s>`.
  - Printed endpoints are MPFR round-to-nearest decimals of the bounds. Rounding is monotone, so the hull of the printed
    intervals equals the printed hull. The classifier itself (B15c / B15c-1) is unchanged.
- **Edge-fixed class.** If an edge chunk ends in DONE, passes validation, and shows a certified edge FAILPIECE or
  `orient_certified_fail=1`, then b = 0 is certain. So COVERS = 0 for ANY (a) outcome, and the covering's class is
  CERTIFIED-FAIL ("edge-fixed"). The (a) chunk still runs to completion (the registered rule: all coverings run, so
  decidability is measured in full). The merged class must then equal CERTIFIED-FAIL, or the covering is HARNESS-ERROR.
- **(i) Merge positive control MC (before any twin edge chunk runs).**
  - HH-SECONDARY N0⇒N0, the covering GB already reproduced (CERTIFIED, `leaves_a=337`), is run as an (a) chunk with a
    fresh checkpoint path and as an edge chunk, then merged.
  - PASS iff the merged COVER line up to ` chunk_a=` is byte-identical to GB's unchunked line (gb/hh2_N0N0.out) AND the
    merged class equals GB's class (CERTIFIED).
  - Canned merge cases must also pass first, with no hs_cover run:
    - an edge chunk alone with `COVERS=1`, merged with `a=0` ⇒ COVERS=0, UNDECIDED;
    - a certified edge FAILPIECE, or `orient_certified_fail=1` ⇒ edge-fixed CERTIFIED-FAIL, and merged CERTIFIED-FAIL
      for any (a);
    - mismatched source/target, an (a) chunk that does not cover [0,nu), or an edge chunk with leaves_a > 0 ⇒
      HARNESS-ERROR;
    - a missing or unfinished (a) chunk ⇒ UNDECIDED merged, with the edge-fixed class still reported;
    - a hull with `none`.
  - MC FAIL ⇒ the split is not used; B15d reverts to unchunked runs and goes back to the Bridge.
- **(iii) The running (a) work is kept.** The two in-flight twin processes (rot90 N0⇒N0 PID 90952, rot90 N0⇒N3 PID
  90954) are PAUSED with SIGSTOP by verified PID, not terminated. Their finished pieces are in their checkpoints, and
  their in-progress piece stays in memory, so nothing is discarded.
  - The old orchestrator (PID 62244) is then ended with SIGKILL by verified PID. Its SIGTERM handler would send SIGTERM
    to the paused children, which would be held pending and kill them on resume.
  - The new runner adopts the two paused PIDs (guard included) and resumes them with SIGCONT in the twin (a) phase. They
    finish under their ORIGINAL unchunked specs (edges included), so their record is their own unchunked COVER line.
  - Their edge chunk, run early, must agree with that line on b, orient, fail_b, certified_fail_b,
    orient_certified_fail and leaves_b, or the covering is HARNESS-ERROR. This is a second, free check of the split.
  - Cuspis-night rule: a stop sends SIGTERM and then SIGCONT to a paused process, so it really ends; it resumes from its
    checkpoint.
- **Order within the same slots (still 2; 4 only on the Bridge's word).**
  1. MC (two chunks).
  2. The twin edge chunks, all 12, in registered order (swap, then rot90; required order N0N0 … N6N0).
  3. The twin (a) phase: resume the two paused processes, plus the (a) chunks of the other 10.
  4. Recipe, then Kerr: unchanged, unchunked, as registered.
  - This amendment covers the twin only; recipe and Kerr keep their registered form unless a later amendment changes
    that.
- **Twin reading.**
  - Per covering: the merged class (or, for the two adopted processes, the unchunked class) once complete; before that,
    the edge-fixed class if there is one, else "pending".
  - A variant PASSes as registered (CERTIFIED-FAIL in ≥ 1 required covering, no HARNESS-ERROR). An edge-fixed
    CERTIFIED-FAIL counts, because it is final.
  - An EARLY twin reading is logged after step 2 and goes to the Bridge. The registered TWIN line is logged when every
    twin covering is complete. Kerr still runs only after twin PASS and the recipe stage, as registered.

**B15d-3 (2026-11-22): Kerr edges first, plus a restart-safe runner.** Proposed by quantum after the Bridge offered it
(the prediction is a certified failure, and only (b) or orientation can certify one). Registered long BEFORE any Kerr
covering runs (Kerr is gated behind twin PASS and the recipe stage).
- **Kerr coverings** (required N0N0, N0N1, N1N2, N2N3, N3N4, N4N5, N5N0; optional N5N1) are each split exactly as in
  B15d-2: an edge chunk (`arange 0 0`, no checkpoint) and an (a) chunk (`noedges`, same checkpoint path).
  - Same merge rule, the same MC (it tests the merge code, which is shared), and the same edge-fixed rule.
  - Order: all 8 edge chunks (required in chain order, then optional), then a logged KERR-EARLY reading, then all 8 (a)
    chunks, then the KERR reading.
  - The per-covering class comes ONLY from the merged input. chain_class over the required merged classes is the
    registered B15d result, read with the registered B15d §5 wording, which depends on the recipe reading.
  - KERR-EARLY is "CERTIFIED-FAIL (edge-fixed; final unless a HARNESS-ERROR appears)" if any required covering is
    edge-fixed. With one required CERTIFIED-FAIL, ρ > 1 is impossible and chain_class can only be CERTIFIED-FAIL or
    HARNESS-ERROR. Otherwise it is "pending". It goes to the Bridge as an early reading, never as the result.
- **Recipe stays unchunked** (the Bridge: its expected outcome is CERTIFIED, which needs (a) in full anyway).
- **Restart safety.**
  - On start, the runner adopts every live hs_cover_b15d process of mine on a spec under b15d/ that is not paused:
    verified owner and command line, guarded, counted in the slot, and not restarted.
  - So the runner can be replaced without killing or re-running a child. (Before this, a restarted runner would have
    started a second process on a still-running spec and truncated its output.)
  - The recipe stage now runs through this adoption-safe loop instead of b15d_run.run_stage; its classes are logged the
    same way.
  - The runner swap itself: SIGKILL of the running runner by verified PID (children are in their own sessions and keep
    running), then a relaunch that adopts them.
- Nothing about the check changes: binary, sets, caps, depth, precision and the classifier are as registered.

**B15d-4 (2026-11-22): recipe control before the remaining twin (a) chunks; a labelled schedule amendment.** Proposed by
quantum (option B) after TWIN-EARLY; chosen by the Bridge. Registered BEFORE any recipe covering or any twin (a) chunk
runs. Only the paused rot90 pair (rot90 N0N0 and N0N3, resumed under B15d-2 at 06:25:54) is running.
- **Why.** TWIN-EARLY (2fcdeb1): every swap covering is edge-fixed CERTIFIED-FAIL (final), and every rot90 covering has
  b = 1 with a certified orientation. So each rot90 covering can end only CERTIFIED or UNDECIDED, and rot90 N0⇒N0
  already holds finished depth-cap failures in (a). Unless a HARNESS-ERROR appears, the registered twin reading will be
  "control not decided", and B15d holds. The remaining twin (a) work can take days on these slots: a covering that
  spends its 65536-leaf cap takes about 90 h on one core. The recipe result is informative whatever happens to B15d,
  because it says whether the recipe can certify HH at all.
  - The Bridge records the rot90 clause as slip 12: the rot90 variant was required to produce CERTIFIED-FAIL, but on HH
    rotating U by 90° breaks neither the edges nor the orientation, and only those two can certify a failure.
- **Change: order only.**
  - After TWIN-EARLY, the runner runs one queue: the recipe coverings (N0N0, N0N3, N3N4, N4N5, N5N6, N6N0, then N6N3),
    then the twin (a) chunks in registered order.
  - The two rot90 processes keep running and count toward the slot.
  - The RECIPE line is logged as soon as every recipe covering is complete. The TWIN line is logged when every twin
    covering is complete, then the registered hold.
- **Unchanged.** Every twin covering still runs to completion for the record. Nothing is skipped, merged or loosened:
  binary, sets, caps, depth, precision, classifier, merge rule and both readings are as registered. B15d's "control not
  decided" (if that is how the TWIN line reads) stays on record. Kerr does not run under B15d unless twin PASS.
- **Slots: 4** from this amendment (the Bridge, 2026-11-22: tabula's §213 run has finished; load 6.5 on 10 cores).
- **Runner swap,** as in B15d-3: SIGKILL of runner PID 34523 by verified PID, then a relaunch that adopts the running
  pair. Slots are raised only after the new runner is up, so no twin (a) chunk starts ahead of the recipe.

**B15e (2026-11-22): B15d's Kerr test re-registered with a ONE-VARIANT twin negative control.** Drafted by quantum at the
Bridge's request (B15E_DRAFT.md, 4eede41); the Bridge chose option (i) and the slot order. Registered BEFORE any Kerr
covering runs and before the RECIPE line exists (the recipe is running under B15d-4).
- **One-variant negative control; rot90 "not decided" (B15d) and stab "S8 stop" (pre-check) remain on record.**
  - The twin = swap alone: HH-SECONDARY's certified sets with U ↔ S. Its 6 required coverings are edge-fixed
    CERTIFIED-FAIL (twin_e/*.out, 2fcdeb1; binary fb5fcbfc). Under B15d-2 that class is final. Reused, not rerun.
  - Twin PASS (B15e) = swap PASS as computed by b15d_split.twin_table() (CERTIFIED-FAIL in ≥ 1 required covering, no
    HARNESS-ERROR). A HARNESS-ERROR in any swap merge voids the twin and therefore the B15e Kerr reading.
  - **Why there is no second independent variant (argued, float, not a proof).** On HH the return map stretches every
    direction with an unstable component, so the u-edges of such a frame are pushed out of the target and (b) and the
    orientation pass (rot90: b = 1 and orientation certified in all 6). Only a u-direction along the stable direction
    contracts and can be certified failing (swap). A stable-aligned frame with N0's long side along S overlaps N6, the
    last set on the approach along W^s (stab: S8 false on N0|N6). A further candidate chosen now would be chosen
    knowing what passes, and would repeat swap's mechanism. So none is added.
  - What the twin shows: the pipeline CAN reach CERTIFIED-FAIL on wrongly aligned HH sets, through the edge route, in
    6 of 6 coverings. Whether the recipe can certify HH comes from RECIPE.
- **Recipe:** the B15d RECIPE line from the B15d-4 queue, unchanged, logged before any Kerr covering starts.
- **Kerr:** B15d §3's chain and sets and the B15d-3 split (kerr_e/, kerr_a/ specs as committed), unchanged. The
  prediction and the §5 readings are B15d's, word for word. The headline says "B15e", that it was re-registered after
  B15d's twin slip (slip 12), and that the negative control is one variant.
- **Order (one runner queue, 4 slots).**
  1. The recipe coverings still running or queued (B15d-4).
  2. Once every recipe covering is complete: the RECIPE line. Then, if twin PASS (B15e), the 8 Kerr edge chunks in
     B15d-3's order, then KERR-EARLY (to the Bridge, never as the result).
  3. Then the remaining twin (a) chunks interleaved with the 8 Kerr (a) chunks, each list in its registered order
     (twin_a[0], kerr_a[0], twin_a[1], kerr_a[1], …; the twin list's tail runs after the Kerr list ends). The rot90 pair
     keeps running and counts in the slot.
  4. When everything is complete: B15d's TWIN line and B15d's hold (unchanged), then B15e's twin line, then KERR.
  - **KERR is final only once every twin merge is complete with no HARNESS-ERROR.** If one appears, the Kerr reading
    is withheld and goes back to the Bridge.
  - If twin PASS (B15e) fails at step 2, no Kerr covering runs; the twin (a) chunks still run for the record.
- **Runner swap** as in B15d-3 (SIGKILL of runner 7337 by verified PID; the relaunch adopts the running recipe
  coverings and the rot90 pair). Nothing about the check changes: binary, sets, caps, depth, precision, classifier and
  merge rule are as registered. F7 applies: any ρ > 1 STOPS.

**B15e A1 (2026-11-22): spec slip, missing `param level` (approved by the Bridge after an independent check).**
Registered BEFORE any smoke, gate test or counted Kerr chunk under A1. Found by quantum at 19:1x; prereg F12 applied.
- **The slip.** For `system mn`, hs_cover lifts every point onto H = −½ (hard-coded in `lift`). S9 compares sys_H
  against SYS.level, which is set only by a `param level` line. The B15c §4 header as registered (k, alpha, beta, E, L)
  has no `param level`, and all 16 B15d Kerr specs (kerr_e/, kerr_a/) copied it. So every Kerr piece fails
  "S9: … misses the energy level (BUG)" whatever the dynamics, and every Kerr covering would be a vacuous UNDECIDED.
  kerr_e N0N0/N0N1 (PIDs 54961/54963, about 7.5 h each, 34 S9-BUG FAILPIECE lines each, no COVER line) were
  SIGSTOPped under F12. The slip is shared: the Bridge approved that header. The recipe, twin and gb gates ran on
  `system hh` (`param level 1/6`), so the mn path was never smoke-tested before counted Kerr chunks. RECIPE-POSITIVE,
  swap PASS and A3 are unaffected.
- **Fix (spec only).** `param level -1/2` is inserted right after `param L 445/2` in the 8 kerr/*.spec sources and
  the 16 kerr_e/kerr_a specs, and in b15_steps34.KERR_HEAD. Nothing else changes: binary (fb5fcbfc…), sets, caps,
  depth, precision, grid, split, classifier, merge rule and readings are as registered. Old and new spec sha256 go in
  kerr/a1_specs.json.
- **Runner gate.** b15d_split.run_jobs refuses, before launch, any spec whose `system mn` lacks exactly one
  `param level -1/2` line (or whose `system hh` lacks exactly one `param level 1/6`). It logs
  "REFUSED <stage>/<tag> … (B15e A1 gate); not launched" and drops the job, so the queue ends in a hold.
  - **Known-answer test (NOT COUNTED):** a copy of the fixed kerr_e/N0N0.spec WITHOUT `param level` is passed through
    run_jobs with process launch disabled. It must be REFUSED, with no launch; the fixed spec must pass the gate. The
    result is logged in run.log. If it fails, nothing further runs and it goes back to the Bridge.
- **S9 smoke with a must-fail twin (NOT COUNTED; slip-12 rule).** Outputs in horseshoe_results/kerr/b15e/a1_smoke/.
  - S+ = the fixed kerr_e/N0N0 header and sets, `caps 65536 4096`, `depth 0 0`, `cover N0 N0 1 1 1`. So three
    top-level pieces: (a) the whole N0, and edges L and R whole, each evaluated once.
  - S− = S+ with `param level -499/1000` (−½ + 1/1000). The lift ignores the level, so both evaluate identical pieces.
  - **PASS** needs all of:
    1. both runs end with a COVER line and DONE;
    2. S− has ≥ 1 FAILPIECE with "S9: return enclosure misses the energy level (BUG)"; call those pieces P;
    3. S+ has no "S9" reason and no "(BUG)" anywhere;
    4. some piece in P, in S+, either passes (no FAILPIECE line) or fails with a geometric reason (starts "u="),
       which means its return check and full in-flow replay passed S9.
  - **Inconclusive** if S− has no S9 line (no piece reached S9). Then, once only, stage 2: the same pair with
    `cover N0 N0 16 16 64`, `arange 0 1`, `noedges`, `depth 0 0` (column 0 of the registered grid, 16 pieces), same
    criteria. If still inconclusive, or if S+ shows any S9/BUG: Kerr stays held and goes back to the Bridge.
  - On PASS, counted chunks start without waiting for a reply; the smoke result is reported to the Bridge first.
- **Void outputs.** kerr_e/N0N0.out and N0N1.out are HARNESS (void, the A1 slip). They are moved, not deleted, to
  kerr_e_void_nolevel/, and both chunks rerun from scratch.
- **Runner swap** as before: SIGKILL of runner 15193 by verified PID, only after the specs are fixed and the gate test
  and smoke PASS. Then the two paused kerr_e are killed by verified PID only. A relaunch adopts the rot90 pair
  (90952/90954) and reruns kerr_e from N0N0 in B15d-3's order. Order, slots (4) and everything else are as in B15e.
- **Headline wording, for KERR-EARLY and KERR:** "B15e A1: the registered B15c spec header omitted param level, so
  the first two kerr_e chunks (~7.5 h each) were void (HARNESS) and rerun."

**B15e A1, smoke stage 3 (2026-11-22; the Bridge's pre-stated fallback, registered while stage 2 runs, before its
result).** It runs ONLY if stage 2 is INCONCLUSIVE. NOT COUNTED. Same S+ / S− pair, same PASS rule as stage 1.
- **Pieces:** those already known to reach the S9 return check: the first 4 edge-L leaves that threw the S9 return BUG
  in the void kerr_e/N0N0 output, s ∈ [−1 + i·2⁻¹⁷, −1 + (i+1)·2⁻¹⁷] for i = 0…3 (cover 16 16 64, top edge piece
  2⁻⁵ wide, 12 bisections).
- **How (a deviation in form, stated):** hs_cover prints nothing for a passing leaf until its covering's COVER line,
  and the void chunk's own settings would take days to get there. So each leaf is evaluated as the edge L of its own
  source set N0p<i>:
  - c′ = c + s_m·S, U′ = U, S′ = 2⁻¹⁸·S, A′ = [U′ S′]⁻¹, all exact rationals, where s_m is the leaf centre;
  - `cover N0p<i> N0 1 1 1`, `arange 0 0`, `depth 16 0`, target N0 unchanged.
  - Edge L of N0p<i> equals leaf i of N0 exactly as a set (checked in exact arithmetic: both endpoints and A′·[U′ S′] = I;
    b15e_a1._piece_tsets). Interval rounding may differ in the last bits. Edge R of each N0p<i> is evaluated too and is
    simply reported.
- **Known answer:** S− must throw the S9 return BUG on these leaves, as the void run did. If it does not, the stage is
  INCONCLUSIVE and goes back to the Bridge. S+ must pass S9 or fail with a geometric reason (rule 4). Any S9 or
  "(BUG)" in S+ means FAIL: Kerr stays held and goes back to the Bridge.

**B15e A1-flush (2026-11-23; the Bridge asked for it as a pre-launch amendment): hs_cover output is line-buffered from
now on.** Registered before smoke stage 3 and before the Kerr rerun.
- **Finding.** hs_cover's stdout to a file is block-buffered (4 KB) and flushed only when a spec command ends; there is
  no signal handler. So a stopped process discards its finished pieces' lines, and an empty file says nothing about
  progress. The void kerr_e outputs show it: 4105 bytes, ending mid-line.
- **Fix without a binary change.** Every hs_cover launch is wrapped as `nice -n 10 /usr/bin/stdbuf -oL <binary> <spec>`.
  stdbuf execs the same binary (same PID, sha fb5fcbfc… unchanged, so GB still holds). libc++'s std::cout writes
  through C stdio, which stdbuf sets to line-buffered. This is done in b15d_split.run_jobs and in the smoke stage-3
  launches.
- **Known-answer check (NOT COUNTED, horseshoe_results/kerr/b15e/a1_flush_kat/).** twin_e/swap_N0N0.spec with
  `depth 0 0` (128 single-evaluation edge pieces), run twice in parallel and SIGKILLed mid-cover after 90 s.
  - Control, no wrapper: 0 FAILPIECE lines, 9 bytes.
  - stdbuf -oL: 9 complete FAILPIECE lines, 1472 bytes.
  - So finished pieces' lines survive a kill. (A first 60 s attempt at the registered depth finished no piece in
    either run, so it was inconclusive; it is recorded as such.)
- **Unchanged:** the binary, specs, caps, depth, grid, classifier, merge rule and readings. Running processes (rot90,
  stage 2) keep their original buffering.

**B15e A1, smoke stage 3 time bound (2026-11-23 ~07:40; the Bridge's request; committed while both stage-3 outputs hold
only the 9-byte `PREC 128` header, so before any S9 line).**
- Bound = 3 x 680 s per leaf x 4 leaves = 8160 s = 2.27 h from the launch at 07:34:27, i.e. **2026-11-23 09:50:27**.
- Basis: the void run (depth 16 12) measured <= 680 s per finished edge-L leaf, and that figure includes the time
  spent on the parent bisections. Stage 3 evaluates each leaf directly as a whole source set (depth 16 0, edge depth
  0, arange 0 0, the same interior setting as the void run), so 680 s per leaf is conservative. No reason to widen it.
- At the bound, with either run lacking COVER + DONE:
  - INCONCLUSIVE, and it goes back to the Bridge.
  - Stop 59188/59191 by verified PID.
  - Record every FAILPIECE line already printed (stdbuf -oL keeps them). Record them only; they are not read as PASS.
- With both runs done before the bound, the registered stage-3 reading applies unchanged.

**B15e A1, kerr_e expected wall time and check-in bound (2026-11-23 ~09:20; the Bridge's request). Committed while
kerr_e/N0N0.out and N0N1.out hold only the 9-byte header, so before any S9 or FAILPIECE line.**
- Measured basis (two sources):
  - Smoke stage 3 S+ (level -1/2, same binary, nice 10): 8 passing edge evaluations (4 leaves x L/R, no bisection) in
    5483 s (07:34:27 to the output's last write at 09:05:50), so about 685 s per passing edge piece.
  - The void run: <= 680 s per finished edge-L leaf (parent bisections included).
- Leaf count: each kerr_e chunk is `cover Ni Nj 16 16 64` with `arange 0 0` and `depth 16 12`, i.e. edges only:
  2 edges x 64 top pieces = 128 edge pieces (recipe outputs show leaves_b=128 at this grid).
- Expected wall time per chunk, if no top piece needs bisection: 128 x 685 s = 87680 s = 24.4 h. For N0N0/N0N1 (started
  09:07:49) that is about 2026-11-24 09:29.
- This is a lower bound in the no-bisection case. Two things can make it longer:
  - 2^-5 pieces are 2^12 times wider than the smoke leaves, so their per-piece cost may differ;
  - each failed piece adds 2 children, up to edge depth 12.
- **Check-in bound: 3 x 24.4 h = 263040 s = 73.1 h per chunk from its own start**; for N0N0/N0N1 that is
  2026-11-26 10:11:49. A chunk still running at its bound is reported to the Bridge. That is a check-in, not a stop: no
  reading changes, and a stop needs the Bridge's word.
- Phase total: 8 chunks run 2 at a time while rot90 holds 2 of 4 slots, so kerr_e takes at least about 4 x 24.4 h, roughly
  4 days. That is stated for planning only, not as a bound.
- Unchanged: the specs, gate, classifier, F12 and every reading. Any S9 "(BUG)" line in a kerr_e output -> F12 stop,
  and it goes to the Bridge.

**B15e A2 (2026-11-23; labelled; memory policy from Sumit, relayed by the Bridge and Cuspis): memory and load INFORM, they never kill.**
Sumit's words: "caps should inform, not kill, unless the mac starts to suffer". This replaces the memory and load stop
rules of the running jobs' guards. It changes no reading, no criterion, no binary and no spec; only the guards change.
The jobs keep running; the guards are restarted, or for the B15d runner, the orchestrator only.
- **Own footprint over its cap** (A3: 500 MB; B15d children: 1024 MB): a WARN line, nothing else.
- **Pressure** ((swap > 2 GB and level >= 2) or level 4): squeeze begin/end lines, WARN only.
- **Red (level 4) sustained 600 s:** PAUSE by verified SIGSTOP, and resume by SIGCONT when the level is back to green.
- **Disk < 5 GB free:** still a stop, as before (the only remaining kill).
- **A3 cost watch:** COST-STOP (> 127.9 s/step over 200 steps) becomes a logged COST-WANT, because other jobs' load
  or a pause would trigger it. The HARNESS-ERROR and RESUMED checks still stop.
- **Implementation:** erep_guard.py and erep_cost_watch.py with `--inform`; b15d_run.guard_loop rewritten.

**B15e A3 (2026-11-23 ~21:50; labelled; slots raised on the Bridge's word): 7 slots for the registered Kerr queue.**
The Bridge (2026-11-23 evening): "the box has spare cores overnight... add up to 3 more"; load was 6 of 10 cores busy,
76% of memory free, swap 315 MB, disk 12 GB free. The B15d-4 rule was "4 only on the Bridge's word"; this is the same
kind of word, for 7.
- **Slots: 7** (`slots.txt` = 7). The hard cap in `b15d_run.slots()` goes from 4 to 7. The runner is swapped
  (orchestrator SIGKILLed by verified PID and relaunched); it adopts the 4 live kerr_e chunks via scan_running and starts
  the next 3 queued kerr_e chunks in the registered order (N3N4, N4N5, N5N0). N5N1 starts when a slot frees.
- **Unchanged:** the binary and its sha, the specs, the A1 gate (every new chunk passes `spec_gate` before launch), the
  nice 10 + stdbuf launch, the queue order, the A2 inform-only guards, F12, the classifier and every reading. At least
  1 core stays free for Cuspis.
- **Lowering:** writing a smaller number to `slots.txt` takes effect at the next loop and only holds back NEW launches;
  it never stops a running chunk. The Bridge may lower it at any time (e.g. for Sumit's office hours).
- **Disk:** kerr_e outputs are ~4 KB each after 10 h, rot90's full outputs were 7 MB after ~30 h, and all checkpoints
  together are 12 MB, so 7 chunks add well under 100 MB overnight against 12 GB free and the 5 GB floor.
- **Planning only (lower bounds, no-bisection case, 24.4 h per chunk):** N0N0/N0N1 ~2026-11-24 09:29; N1N2/N2N3 ~11-24
  19:30; N3N4/N4N5/N5N0 ~11-24 22:20; N5N1 (starting ~11-24 09:29) ~11-25 09:55, so kerr_e is complete about
  2026-11-25 10:00, against ~11-25 20:00 on 4 slots. Each chunk keeps its own 73.1 h check-in bound.
- **A3-fix (2026-11-23 21:49; harness only, found during the swap).** The first relaunch (runner 6446, 21:48:56) adopted
  the 4 live chunks and then exited with "B15e queue ended at stage 0 ... HARNESS; held". `run_jobs` entered its loop
  only if `todo` or `running` was non-empty. With every recipe job done and no paused PID left (rot90 had ended),
  it never called `on_tick`, so kerr_e was never re-queued. The earlier swap (3653) worked only because the paused rot90
  PIDs were still alive. Fix: `run_jobs` ticks at least once. Canned merge test PASS. The relaunch (runner **6602**,
  21:49:51) logged RECIPE and twin PASS, adopted 79482/79486/54059/54063 (not relaunched), and started kerr_e N3N4
  (PID 6670), N4N5 (6675) and N5N0 (6677), all through the A1 gate with no REFUSED line. The 4 chunks ran unguarded for
  about 1 minute (21:48:56 to 21:49:51); nothing else changed. The "stage 0 ... HARNESS" line in run.log is this
  harness slip, not a reading.

**B15e A4 (2026-11-25; labelled; the Bridge approved option (B)): kerr_e chunks hit hs_cover's hard 48 h watchdog; a
configurable watchdog, and the reruns.**
- **Finding.**
  - kerr_e N1N2 and N2N3 (54059/54063) ended at 19:05:44 on 2026-11-25, exactly 48 h after their start, with
    `WATCHDOG TIMEOUT: proof program exceeded its wall-clock limit (fail closed)`: no COVER, no DONE, 0 FAILPIECE, no S9.
  - The limit is `capd_proof::watchdog(48 * 3600)` (hs_cover.cpp main), compiled into the registered binary fb5fcbfc….
  - N3N4, N4N5 and N5N0 (6670/6675/6677) reach 48 h at 21:50 and cannot be saved: an alarm in a running process cannot
    be extended, and hs_cover's `checkpoint` covers (a)-pieces only, while kerr_e is edges-only.
  - N0N0/N0N1 had taken about 27 h on a lighter box. Load has since been about 10–13, with swap up to 4.5 GB.
- **Registration slip (disclosed).** B15e A1's expected-time entry (24.4 h lower bound, 73.1 h check-in) did not list
  the binary's 48 h watchdog, so the 73.1 h check-in was unreachable. New rule: every registration lists the binary's
  hard limits (watchdog, memory caps) next to its time estimates.
- **The runner's "stage 1 … HARNESS; held" line**, which appears when the last kerr_e exits, is this harness slip, not
  a reading.
- **Change.**
  - hs_cover.cpp reads `HS_WATCHDOG_S` (positive integer seconds, at most 30 days). Unset or invalid = the original 48 h,
    and nothing is printed either way.
  - New binary `hs_cover_b15e`, sha256 c924b03bf3328a4960673879b61ab3c0679bdae685270a9145da80f155f7b903, guard passed.
  - The registered fb5fcbfc… came from hs_cover.cpp at 4c6b8b9. A fresh build of that unmodified source is not
    sha-identical (b76c2357…: output name and link data), so identity is checked on OUTPUTS.
- **Identity checks** (before any rerun; each can fail):
  - (i) With HS_WATCHDOG_S unset, hs_cover_b15e reproduces the stored outputs BYTE FOR BYTE on b15d/gb/r1_MM, r1_MN,
    r1_NM, r1_NN (about 2.5 min each) and gb/hh2_N0N0 (about 22 min).
  - (ii) **Must-fire.** With `HS_WATCHDOG_S=60` on a long case (kerr_e/N1N2.spec), it must exit 124 with the WATCHDOG
    line between 55 and 120 s after start.
- **Reruns.**
  - The chunks are N1N2, N2N3, N3N4, N4N5 and N5N0. N5N1 stays on the old binary and joins the list only if it also
    times out (11-26 20:43).
  - Settings: the same specs (gate-checked), the same nice 10 + stdbuf -oL launch, `HS_WATCHDOG_S=432000` (120 h).
  - The failed outputs move, never deleted, to `kerr_e_void_watchdog/`. Each rerun writes `kerr_e/<chunk>.out` afresh.
  - Reading: unchanged (B15d-2/-3, B15e).
- **Cores.** kerr_e reruns take each freed core FIRST, then branch-S pm, pp and refs. The fleet stays at ≤ 9 cores
  while Sumit works.
- **Later stages.** twin(a)/kerr(a) chunks run on the runner's binary, which still has the 48 h limit. Whether they
  move to hs_cover_b15e with a raised limit is a separate decision for the Bridge, to be registered before KERR-EARLY.
- **Timer rescue (record, 2026-11-25 19:41; Sumit's go via the Bridge, who did it and approved the admin prompt).**
  - On kerr_e PIDs 6670 (N3N4), 6675 (N4N5), 6677 (N5N0) and 93687 (N5N1), running the REGISTERED binary fb5fcbfc….
  - The pending watchdog alarm was CANCELLED by debugger (`lldb -p PID`, `expr alarm(0)`, detach, then `kill -CONT`).
    The timers had 7740, 7738, 7737 and 90132 s left, matching the 21:50 and 11-26 20:43 deadlines.
  - The computation was not touched; all four were confirmed back in state R.
  - A dry run on a dummy first showed that alarm(0) cancels the timer and that detach leaves the process stopped, hence
    the `kill -CONT`.
  - Log: TheBridge/fleet/kerr_e_timer_rescue_2026-11-25.log.
  - These four chunks are no longer limited in wall time, and their outputs are read exactly as registered.
  - **A4 reruns are now needed only for N1N2 and N2N3.**

**B15e A5 (2026-11-26; labelled; the Bridge's decision after the 06:52 power loss): edge-leaf checkpointing in hs_cover,
then all six kerr_e chunks relaunch.**
- **Why.** Every kerr_e chunk died in the outage. Edges had no checkpoint, so about 214 core-h were lost; with the
  watchdog deaths, about 450 core-h in all.
- **Change** (hs_cover.cpp, do_cover).
  - With a `checkpoint` line, every finished TOP-LEVEL edge piece (side, i) is appended to the checkpoint file and
    fsync'ed, as `EF <key> <FAILPIECE line>` lines plus one `EP <key> leaves fail cert_fail dL dR nsteps rtflag
    [rt_lo rt_hi]` line.
  - A restart reloads those pieces instead of recomputing them. Their stats are merged exactly as the leaves would
    have been: sums, and an interval hull of exact endpoints. The leaf-cap accounting continues from the running
    total, and the saved FAILPIECE lines are printed in their original order.
  - After a resume, one extra line `EDGES RELOADED <n>` is printed. The COVER line format is unchanged.
  - Without a checkpoint line, the original code path runs unchanged.
  - The (a) reader ignores EP/EF lines.
  - New binary **hs_cover_b15e2**, sha256 a2f4ca1856e74425b9e122d1464d958fd0734a0beaac1a30a94d76b1783e4501, guard passed.
    HS_WATCHDOG_S (A4) is kept.
- **Identity tests** (each can fail; run serially on 1 core before any relaunch):
  - **T1:** no checkpoint line. b15d/gb/r1_MM, MN, NM and NN must be byte-identical to the stored outputs.
  - **T3:** an uninterrupted run with a fresh checkpoint on twin_e/swap_N0N0's spec (HH, edges only, 289 edge leaves,
    138 FAILPIECE of which 125 are certified, about 20 min). It must be byte-identical to the stored
    twin_e/swap_N0N0.out (registered binary fb5fcbfc…).
  - **T4: deliberate interruption.** The same spec with a second fresh checkpoint is stopped by SIGTERM once the
    checkpoint holds ≥ 32 EP lines (not a timer), then restarted. The restart's output, with its single `EDGES RELOADED
    k` line removed, must be byte-identical to the stored output, with 0 < k < 128.
  - **T5: must-fire.** T3's complete checkpoint with ONE EP line tampered (its dL count +1). The rerun's COVER line must
    DIFFER from the stored one. This shows the test can fail.
- **Relaunch (after T1–T5 pass, on the Bridge's word).**
  - All six kerr_e chunks (N1N2, N2N3, N3N4, N4N5, N5N0 and the optional N5N1) from zero, on hs_cover_b15e2 with
    HS_WATCHDOG_S=2592000.
  - Each spec gains exactly one line, `checkpoint …/b15d/ckpt/kerr/<chunk>.ckpt` (old/new sha recorded). Everything
    else is unchanged.
  - The old outputs move to `kerr_e_void_outage/`, never deleted.
  - Each chunk is guarded by kerr_guard (pause/resume/inform only). A future crash then loses at most the edge piece in
    progress.
- **Hard limits (the A4 rule).** The watchdog is 30 d (effectively none); there are no memory or step caps. The leaf
    and depth caps produce FAILPIECE results, not kills.
- **A5 correction (labelled; before any A5 test ran): crash-safe checkpoint reading.**
  - A power cut mid-append could leave a partial last EP line, which would be parsed with missing fields, or orphan EF
    lines, which would duplicate FAILPIECE output later.
  - Now every EP line ends with a ` #` marker and counts only if all its fields parse. EF lines attach to their key
    only when that key's complete EP line follows, and the last complete record wins. A partial record is ignored and
    that piece is recomputed.
  - The binary is rebuilt: **hs_cover_b15e2 sha256 f34415e5007205267370c8bdb4d95b76be64a147e16a83ebbbf31b65a32939d7**
    (guard passed). It replaces a2f4ca18…, which was never run.
  - **Added test T6.** T3's complete checkpoint is truncated mid-way through a late EP line, and one orphan EF line for a
    later key is appended. The rerun's output, with its EDGES RELOADED line removed, must be byte-identical to the
    stored output.
  - Noted, not changed: hs_cover's existing (a)-piece reader has the same partial-line weakness; that is out of scope.
- **A5 correction 2 (labelled; before any A5 test ran).** On startup, if the checkpoint file does not end in a newline
  (a cut mid-line), one newline is appended first, so the next record cannot be glued onto the partial line. T6
  exercises this. Binary rebuilt: **hs_cover_b15e2 sha256 d3747eb04ba66977cf76dcb40709fe0d037b84db9dfe807859b8b0951ffd95cc** (guard passed); it replaces f34415e5…, which was never
  run.

**B15e A5b (2026-11-26; labelled; the Bridge asked for it BEFORE any kerr_a/twin_a interior chunk runs): crash-safe
(a)-piece checkpoint reading.**
- **Change (reader only; the (a) writer is unchanged, so existing checkpoint files stay valid).**
  - The file is append-only and each record ends with its own newline. So: a last line without `\n` is dropped, and
    any line holding NUL is dropped.
  - A `P` line counts only if all its fields parse. `F` lines attach to their key only when that key's complete `P`
    line follows, and the last complete record wins. (The old reader concatenated F lines across duplicate records.)
  - A missing final newline is repaired before anything is appended.
  - Binary **hs_cover_b15e3** sha256 0d9a6af672697a35dbdafc07482d36779d963b46fa7ce28505d7cb84f44472f2, guard passed. It
    includes A4 and A5. The kerr_e relaunch stays on the A5-tested b15e2. Interior chunks (kerr_a, twin_a) use b15e3
    only after these tests pass.
- **Tests** (gb/hh2_N0N0.spec with fresh checkpoint paths; 256 (a)-pieces + 128 edge pieces; reference = the stored
  gb/hh2_N0N0.out from the registered binary). "Normalised" means the `EDGES RELOADED` line removed and
  `reloaded_pieces=<k>` set to 0.
  - **B1:** uninterrupted. Byte-identical to the reference.
  - **B2:** SIGTERM (deliberate, not a timer) once the checkpoint holds ≥ 64 P lines, then restart. Normalised output
    byte-identical to the reference, with 0 < k < 256.
  - **B3 (backward compatibility):** a COPY of the old-format ckpt/gb/hh2_N0N0.ckpt (the original GB run; untouched). It
    reloads all 256, and the output is byte-identical to a4_identity/hh2_N0N0.out, which is the same situation under
    hs_cover_b15e.
  - **B4:** B1's complete checkpoint cut mid-way through its 200th P line, with an orphan F line for a later key placed
    before the cut. Normalised output byte-identical to the reference, with no orphan text. **B4b:** a second restart,
    the same.
  - **B5 (must-fire):** B1's checkpoint with ONE P line's leaf count +1. The COVER line must differ from the reference.
- **A5/A5b test run 1 (recorded, not hidden) and correction 3 (labelled; before any rerun).** Run 1 on hs_cover_b15e2
  d3747eb0…: T1 (4/4), T3, T4 (EDGES RELOADED 32) and T6 (EDGES RELOADED 99) all PASS, but two failed:
  - **T5 FAILED, a test-design flaw.** It tampered with dL, a landing count that the COVER line never shows. In this case
    the edges already fail and the orientation is already "none", so dL cannot change the output. The must-fire was
    therefore unable to fire. Corrected: T5 tampers the EP leaf count, which enters `leaves_b`.
  - **T6b FAILED, a real bug.** The orphan EF line was held as pending under its key. When that piece was recomputed
    later, its real record appended and the orphan attached too, so its FAILPIECE text appeared on the second restart.
    The A5b (a) reader had the same flaw, so its test run was ABORTED at B1 (a test process only) and nothing was read.
  - **Fix (both readers).** A record is its EF/F lines IMMEDIATELY followed by its EP/P line, written in one atomic
    append. The buffer holds lines for ONE key only; any other line (a different key, a bad or other line) discards it,
    and a complete EP/P takes the buffer only for the same key.
  - **Binary.** One binary now carries A4 + A5 + A5b: **hs_cover_b15e2 sha256
    77eb34a6a3cf9df54b6e678449b58b971e40d96a11c16314a287517933a42940** (guard passed; hs_cover_b15e3 is a byte copy).
    Used for both the kerr_e relaunch and the interior chunks.
  - **ALL tests are rerun on it** (T1, T3–T6b and B1–B5, unchanged except T5's target). Run 1's results are kept as
    a5_tests/results_run1_FAILED.txt and a5b_tests/results_run1_ABORTED.txt.
