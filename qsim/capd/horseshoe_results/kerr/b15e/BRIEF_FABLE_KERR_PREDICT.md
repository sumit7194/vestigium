# Brief for Fable 5.2 (Quantum-personal): a SEALED blind prediction of the Kerr negative control (B15e)

Written by Claude Opus 5.5 (session "Quantum") at the Bridge's request on 2026-11-26. This brief is self-contained. You
are an independent predictor. Everything you produce is labelled `[model: Fable 5.2]` and UNVERIFIED.

## 1. Setup
- **The claim being guarded.** A computer-assisted horseshoe (topological chaos) for the MN geodesic flow.
- **The negative control.** The same rigorous covering pipeline (`hs_cover`, CAPD 128-bit) runs on the Kerr flow at
  matched (E, L_z). Kerr is Liouville-integrable (Carter's constant), so the registered prediction is that NO
  transition graph with ρ(A) > 1 certifies. Rule F7: any rigorous ρ > 1 on Kerr STOPS the MN claim.
- **The Kerr chain.** Fixed sets N0…N5 with a registered chain.
  - Required coverings: **N0N0, N0N1, N1N2, N2N3, N3N4, N4N5, N5N0**. Optional: **N5N1**.
  - Each covering Ni⇒Nj is split into an **edge chunk** (kerr_e: the "(b)" edge pieces, 128 edge leaves) and an
    **interior chunk** (kerr_a: the "(a)" pieces, up to 2^16 leaves).
- **Per-covering classes** (b15_steps34 / B15c classifier): CERTIFIED, CERTIFIED-FAIL (a certified failure: a
  certified FAILPIECE, or a certified orientation failure), UNDECIDED, or HARNESS-ERROR.
  - "Edge-fixed" CERTIFIED-FAIL from the edge chunk alone is final (B15d-2).
- **Chain class.**
  - RHO>1 if every required covering is CERTIFIED;
  - CERTIFIED-FAIL if any required covering is CERTIFIED-FAIL;
  - otherwise UNDECIDED;
  - HARNESS-ERROR overrides all.
- **Already completed** (allowed to use): the edge chunks of N0N0 and N0N1 both gave `COVERS=1 … b=1 … fail_b=0`,
  leaves_b = 128 (b15d/kerr_e/N0N0.out and N0N1.out). The other edge chunks and all interior chunks are not finished.

## 2. Read-only inputs, and the exclusions
All paths are under /Users/sumit/Github/quantum/.
- **Allowed.**
  - `PREREG_chaos_horseshoe_phase2.md`, **lines 1–1973 ONLY** (everything before "B15e A3"): §6.3 Kerr, F7, the
    OUTCOME log, B15c, B15d, B15d-1…4, B15e, B15e A1/A1-flush/A2.
  - `qsim/capd/horseshoe_results/kerr/b15c/`: T1/T2/T3/ARM/controls json and seal_record.txt.
  - `qsim/capd/horseshoe_results/kerr/b15d/kerr/build.json` and the specs `kerr/*.spec`, `kerr_e/*.spec`,
    `kerr_a/*.spec`.
  - `kerr_e/N0N0.out` and `kerr_e/N0N1.out`: complete, final.
  - `twin_e/`, `twin/`, `recipe/`, `gb/` and `mc/` outputs (HH controls and gates).
  - `qsim/capd/horseshoe/hs_cover.cpp`, `b15d_split.py`, `b15_steps34.py`.
- **EXCLUDED** (live progress; do not open, list or stat them):
  - every other file in `kerr_e/` and `kerr_a/` outputs (`*.out`);
  - `kerr_e_void_watchdog/`, `kerr_e_void_nolevel/`;
  - `b15d/run.log`, `kerr_guard*.out`, `ckpt/kerr/`;
  - `kerr/b15e/a4_launch.log`, `a4_identity/` outputs;
  - PREREG lines from 1974 on;
  - any `ps` output for hs_cover;
  - git log or git show of commits after this brief's commit.
- **Compute.** None, or seconds of Python over the allowed files. Launch nothing. Do not edit main.

## 3. Required output: `kerr/b15e/KERR_PREDICTION_SEALED.md`
1. **A table, 8 coverings × 3 columns** (N0N0 and N0N1 edges are known; predict their interiors):
   - (i) the edge-chunk result: b = 1 with no certified failure, or edge-fixed CERTIFIED-FAIL, or not finishing;
   - (ii) the final per-covering class after the interior chunk: CERTIFIED / CERTIFIED-FAIL / UNDECIDED, with a
     probability for each;
   - (iii) where any failure appears: an edge or an interior piece, and why.
2. **The chain class**, with probabilities: CERTIFIED-FAIL / UNDECIDED / RHO>1 / HARNESS-ERROR. Then
   **P(no horseshoe certified) = 1 − P(RHO>1)**.
3. **The reasoning.** How integrability, through invariant tori and the twist map, shows up in these coverings, and why
   the edge or the interior part would fail. Use the B15c arm's behaviour and the HH twin and recipe results.
4. **Falsifiers.** Which outcomes would refute the reasoning, as opposed to missing a probability.
5. **Labels.** Mark everything `[model: Fable 5.2]` and UNVERIFIED. Cite literature at source with section and
   equation, or mark it "from memory".

## 4. Sealing and grading (fixed now)
- **Sealing.** Commit ONLY `qsim/capd/horseshoe_results/kerr/b15e/KERR_PREDICTION_SEALED.md` to the branch
  `fable/2026-11-26-kerr-predict`, from main at this brief's commit, and push the branch. Send the commit sha and the
  file's sha256 to the Bridge. Quantum does not open it until the registered KERR reading exists: B15e step 4, "KERR
  (B15e, final)" or "KERR WITHHELD".
- **Grading** (descriptive, recorded beside the KERR result):
  - (i) the edge column: correct calls out of 6 (N1N2 … N5N1);
  - (ii) the final per-covering class: the log score of the stated probabilities over the coverings actually decided;
  - (iii) the chain class: whether the modal call was correct, and the Brier score of P(RHO>1).
  - A covering that never completes (or reads HARNESS-ERROR) is excluded from (i) and (ii) and recorded as such.
  - The grading changes nothing about the registered Kerr reading.
