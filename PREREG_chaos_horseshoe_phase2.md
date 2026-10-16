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
