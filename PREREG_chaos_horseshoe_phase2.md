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
