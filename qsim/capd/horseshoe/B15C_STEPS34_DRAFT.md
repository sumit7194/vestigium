# B15c (2026-11-21): steps 3–4 for B15's candidate connections (sets, then rigorous coverings)

**Status: REGISTERED as B15c in PREREG_chaos_horseshoe_phase2.md (2026-11-21).**
- Drafted by Claude Opus 5.5 (session "Quantum"); the first draft is 947f1cf.
- The Bridge reviewed it and approved it with required changes (2026-11-21). The Bridge relays Sumit's decisions.
- The text below includes those changes. The registered copy in the prereg governs; this file is the drafting record.
- Nothing below had run when it was registered.

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

## 1. Candidates and order
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

## 2. Step 3: refine, orbit, frames
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

## 3. Step 4: the ladder
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

## 4. Rigorous stage (only for chains with an accepted ladder entry)
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

## 5. Reading the prediction (the vacuous-pass guard)
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

## 6. Controls (non-counted)
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

## 7. Order, resources, reporting
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

## 8. Post-result finding about B15's red-flag record (B15_FINDINGS.md §4)
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
