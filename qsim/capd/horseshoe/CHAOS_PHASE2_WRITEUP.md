# Chaos-proof phase 2: final write-up (thread closed 2026-11-27)

Written by Quantum-personal (Claude Opus 5.5) at Sumit's request, relayed by the personal Bridge. This is the closing record of the phase-2 thread registered in `PREREG_chaos_horseshoe_phase2.md`. It makes no new claim. Every number below is quoted from the file and commit named beside it.

---

## Summary in plain language (one page)

**The goal.** We wanted a computer-assisted proof that orbits around a Manko–Novikov (MN) "bumpy" black hole are chaotic. The plan was to find a *horseshoe*: small boxes that the orbit map stretches and folds over each other in a pattern that forces chaos. Each step had to be checked with rigorous interval arithmetic, so that every rounding error is accounted for. The method was first tested on systems where the answer is known.

**What worked: the method is sound where it can be run.**
- **Hénon–Heiles, the classic chaotic test system.** The pipeline proved a horseshoe twice.
  - It reproduced the published result of Arioli and Zgliczyński: all 7 coverings were certified, giving entropy ≥ 0.3223. The first registered pass did not certify everything; a disclosed extra budget was needed.
  - It also built a set of its own with our automatic constructor: all 6 coverings were certified, giving entropy ≥ 0.2812.
- **Controls.** The Rössler pipeline control passed. Deliberately wrong set-ups (swapped, rotated or shrunk boxes) were rejected, as a sound tool must reject them.
- **Mathematics for MN, done separately and rigorously.**
  - The Melnikov stages 1–2 proved that the splitting of the MN separatrix is non-zero and non-degenerate at first order in the bumpiness β.
  - The Morales–Ramis and Ziglin non-integrability obstructions were certified on the axis and on the equator, and replayed in a second engine with no contradictions.
- **Kerr, the ordinary black hole, which must NOT show chaos.** Where the tool could decide anything, it never produced a false certificate. Two coverings near the unstable orbit certified, which is allowed: they give a periodic orbit, not chaos.

**What did not work: MN itself.**
- The rigorous integrator can carry only very small MN boxes, about 5e-8 across, through one trip round the orbit. Each trip costs more than 122 core-hours. A Kerr box costs about half an hour.
- The smallest box set our frozen constructor allows would need at least about 200,000 such boxes for a single covering. That is about 24 million core-hours, against a registered budget of 1,344. Even if each box were 100× cheaper, it would still be about 180× over budget.
- So the registered stop rule said STOP (2026-11-27, d9f9ad9), and the thread is closed.

**The finding.** The current certified-integration engine (CAPD with MPFR intervals and our field encodings) cannot carry MN boxes large enough for a horseshoe within any sane budget. This is a statement about the method, not about the dynamics: MN may well be chaotic. The Melnikov and Morales–Ramis results point that way, but no horseshoe was proved.

**What would change it.** Any one of these:
- a much tighter interval form of the MN field (the MN field over-widens 10–1700× against Kerr's 1–47×);
- a different certified integrator;
- an h-set construction that works at the 1e-7 scale.

Each would be a new, separately registered project.

---

## Technical record

### 1. Trust base

- **Engine:** CAPD master at the unreleased commit 2f06098 (`qsim/capd/PINS.md`, c4ec917; it replaced the v6.0.0 pin, 734d2e6), with MPFR intervals under `proof_guard.h`.
- **Build tests:** CTEST 41/44 (`CTEST_REPORT.md`). The 3 failures are test #7, where CAPD's outward rounding is in fact correct, and the non-interval tests #43 and #44. The Bridge accepted the build.
- **DIFFCHECK** (a6d1f33): 3 × 100,300 operations at 53, 113 and 256 bits, 0 failures, 6000/6000 mutants caught per precision.
- **ODE_CONTROLS** (16e6f61): 272/272 exact values contained, and 272/272 collapse mutants rejected.
- **NAN_SAFEGUARD** (65e0a1f): `-D__MPI_TEST_NAN__` does not compile at 2f06098, so it is replaced by the `capd_proof` finite-endpoint helpers, which fail closed.
- **T0** (`horseshoe/T0_HYPOTHESES.md`, 45c1168): Arioli–Zgliczyński 2001, Definitions 1–6, Theorems 1–2 and Lemma 6 (the planar case). Hypotheses H1–H9 are mapped to S1–S4, S8 and S9. Continuity of π is our own step and is flagged as such.
- **S8** (exact pairwise disjointness of the supports) and **S9** (H checked on every step enclosure, plus the momentum sign at each return) held in both Hénon–Heiles runs.

### 2. Controls

- **R1 Rössler** (ce66e54, `horseshoe/R1_ROSSLER.md`): PASS.
  - CAPD's own example, ported to MPFR: 5/5 checks plus both cone conditions.
  - Our generic Definition 2 code: 4/4 coverings with matching orientations. Return times [11.327, 11.774] and [11.571, 12.219].
- **§6.4 wrong configurations.**
  - **Rössler:** W1 swap, W2 rot90 and W3 shrink were all REJECTED by certified (b) failures (for example u certified in [0.194, 0.205] for W1).
  - **HH on AZ's sets:** W-AZ1 and W-AZ2 were rejected by (b) failures (`hh1_run.out`).
  - **HH on our own sets:**
    - swap: all 6 required coverings CERTIFIED-FAIL (2fcdeb1);
    - rot90: never decided (recorded as "slip 12");
    - W3 shrink: not run.
- **Recipe positive control** (bd27a4a): RECIPE-POSITIVE, 6/6 CERTIFIED, with N6⇒N3 CERTIFIED-FAIL. B15e twin PASS.

### 3. Hénon–Heiles (positive control)

- **HH-PRIMARY** (`horseshoe/HH_PRIMARY_OUTCOME.md`; sealed ca819cf, earlier coverings 914e99f):
  - The registered first pass (bd7060a) gave (b) 7/7 but (a) not certified at 16×16.
  - After the disclosed escalation (adaptive bisection 921ee47; B13 816fdfb + 691d5d8), all 7 coverings of AZ (5.1) were certified.
  - ρ(A) = λ_max = 1.380277569…, so **h_top ≥ ln λ_max = 0.3222846…**
  - Against the original 48 core-hour budget the result reads PARTIAL 5/7 (about 87 core-hours spent). Against B13 it reads 7/7.
  - Maximum depth was 11 of 16. The largest leaf count was 20,166 of 65,536.
  - S6 cross-path (cffeb66): AGREE, decisions 9/9 and orientations 7/7.
- **HH-SECONDARY** (5a21dde, `horseshoe/HH_SECONDARY_OUTCOME.md`):
  - The B14 constructor was frozen at 1da283c.
  - All 6 required coverings were certified, in 4.4 core-hours.
  - The characteristic polynomial is x⁵ − x⁴ − 1, so ρ is the plastic number 1.324717957…, and **h_top ≥ ln ρ = 0.2811996…**
  - The optional N6⇒N3 is a certified orientation failure.
  - Wording, as registered: "consistent with the published existence result".

### 4. MN: rigorous results outside the horseshoe

- **Melnikov** (`qsim/mn_melnikov/RESULT.md`; point (M, a, r_u, z_m) = (5, 3, 16, 1/2), Arb):
  - **Stage 1** (d338e00): CERTIFIED-NONZERO. L2 = [−4.77482114974644e−5 ± 6.81e−20], excluding 0, with Cauchy tail ≤ 3.97e−30.
  - **Stage 2** (77073c2): CERTIFIED-NONDEGENERATE at the one closing point (σ, τ) = (0.13, 0.6). The margin |L2|.lower − 4|L4|.upper − T3.upper = +1.5242e−5. 15 of the 16 points did not close.
  - Both stages are first order in β only; they say nothing at fixed β.
  - The theorem glue in THEOREM_DRAFT.md has not been checked.
- **Morales–Ramis and Ziglin** (sister lines):
  - axial L = 0: OBSTRUCTION at p1 and p2, all 4 levels (2ce8b41);
  - equatorial v2: all 6 rows OBSTRUCTION;
  - the CAPD third replay: 24/24 REPLAYED, Arb-free, 0 contradictions (2799ede), with cross-path 7/7 AGREE (985faf2; `qsim/capd/MR_REPLAY.md`).
  - The 12 axis-lattice certificates were re-checked in Lean (943266e). The non-author faithfulness read is still open, so they are not claimed as Lean-verified.
- **Field gates:**
  - B10 exact identity PASS (7016286);
  - S5 PASS (4b747c5) and S5 at A-K20's final parameters PASS (372e4e2). Their polynomial layer is exact; the H_red agreement, to 2.0e−69 and 4.1e−70, is numerical;
  - codegen gate PASS (4c6b8b9): widths ≤ 3.5e−42 at 160 bits, mutants caught 32/32.

### 5. MN: the covering attempt and why it stopped

- **Smoke test** (2026-10-21; de5802a, 23e4869, aa96cb2; `horseshoe_results/mn_smoke/`): not certified. A 1e−6 box failed after 7.7 h. The two causes:
  - the p_y lift was 0.0997 wide against a true 1.94e−4 (~500×);
  - the field over-widens 1e1–1.7e3 for MN, against 1.2–47 for Kerr, from the β terms.
- **The so_mn line** (rigorous enclosures, diagnostic; no covering verdict):
  - **Wrapping test** (c22d325): WRAPPING. B17 with W_lin passes at t 291.885 (u2 1.504). The 1e−6 box fails even with W_lin (u2 13.99).
  - **main_redo** (7d56c34): PASS to t 291.885, 154,323 s on one core.
  - **A3 / main_cont** (55ea6e6): VERDICT FAIL, 4/5 checkpoints. R3a at t 793.2346 failed with u2 8.77; correction 156bb81 notes the ratio spiked where the true u2 width dipped. Its wall time reached 286,171 s by t 809.8.
  - So one 1e−7 box costs **≥ 122 core-hours** per trip, and the section return is at t ≈ 1018.7, later still.
- **Branch-S retry** (four 5e−8 pieces): ended at step 0 = STOP (2026-11-27 00:43, by verified PID; state kept). No verdict was read. The sealed Fable retry prediction d31ac7f stays sealed and ungraded.
- **Step 0 = STOP** (d9f9ad9; `horseshoe/MN_PILOT_STOP_OR_GO_DRAFT.md`; the budget of 1,344 core-hours was fixed before step 0 was read):
  - The smallest set in the frozen B14 ladder has a0 = 0.01 and b0 = 0.001.
  - One N0⇒N0 covering needs ≈ 4e9 boxes of half-width 5e−8 as tested, or ≈ 2e5 on the most favourable reading. That is ≈ 2.4e7 core-hours, ~18,000× over budget.
  - The §3.6 interior cap of 2¹⁶ boxes binds as well.

### 6. Kerr (negative control): the decidability record

- **B15 step 2** (85af9f0, `B15_FINDINGS.md`): 10,081 crossings, of which 147 accepted at angle ≥ 0.01 (max 0.04586). The saddle has λ_u = 62.6203.
- **B15c** (73230b5, `B15C_RESULT.md`): NOT TESTED. Refinement failed for T1 1, T2 80 and T3 58; T3 had 8 with no ladder entry. No chain reached a decided covering.
- **B15d** (ed65b68): the B14 frames are numerically singular on Kerr. sin∠(U_j, S_j) runs from 1.9e−3 down to 6.0e−11 along the chain, which is integrability itself (W^u = W^s). The sets were therefore fixed on the arm's chain with orthonormal frames.
- **B15e A1** (852b9f9, fix 4c66dab): the specs lacked `param level`, so every piece failed with an S9 BUG. The first runs were voided. The S9 gate caught it, as designed.
- **kerr_e**, edges only:
  - N0⇒N0 and N0⇒N1 were CERTIFIED (COVERS=1, orientations LR and RL, 128 leaves each, return time [695.52, 700.76]; N0N0 took 27.1 h). The outputs are in `horseshoe_results/kerr/b15d/kerr_e/`. These are self-coverings near the hyperbolic orbit, which §6.3 allows.
  - The other 6 chunks were projected at 21 to over 61 days each (6966fe3), then paused and ended after the MN STOP. Their 7 edge records (all with 0 fails) are kept.
  - No ρ(A) > 1 was ever certified on Kerr, and no certified failure was reached on the chain coverings either. So, under B15c §5's vacuous-pass guard, the Kerr prediction stands **NOT TESTED**, and no "prediction supported" is claimed.

### 7. Supporting infrastructure kept for any successor

- **A8**, hs_cover_b15e5 (sha256 3a3c4bbe…), adds a sub-piece node journal and progress files. Tests T7, T0, T1, T2 (10 interrupt cases plus SA7), T4, T5 and T5b all PASS (daf38cc, manifest 5ba6c37). T3 was ended by the STOP with no reading.
- **Other tools:** `tools/watch_new.sh`, a report-only watcher; `pcore_read.py`, a read-only reader of each process's time on performance cores (all 5 Air chunks showed a share of 0.52).

### 8. What is NOT claimed

- No horseshoe for MN, and no chaos claim for MN geodesics.
- The Kerr negative-control prediction is NOT TESTED, not "supported".
- Nothing is claimed as Lean-verified.
- The Melnikov results are first order in β only.
