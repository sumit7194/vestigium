# Brief for Fable 5.2 (Quantum-personal): a SEALED blind prediction of the branch-S retry

Written by Claude Opus 5.5 (session "Quantum") at the Bridge's request on 2026-11-26. This brief is self-contained. You
are an independent predictor, not the author of the runs. Everything you produce is labelled `[model: Fable 5.2]` and
UNVERIFIED.

## 1. Setup
- **The system.** A 4-D Hamiltonian flow (the "MN" geodesic model) is integrated with a rigorous second-order set
  method (`tests/mn_so.cpp`, the zonotope error representation "zsym", REDO on).
- **The set.** The start set is a small square box of half-width W0 in (x, p_x) about a fixed centre. The method
  carries the set as x + C r + H(r, r)/2 + E, with r ∈ [−1, 1]². E is a zonotope of accumulated error ("error part").
- **The B17 check at time checkpoint t_c.** It uses the centre orbit's singular directions of the flow derivative:
  - u1 is the thick (stretching) direction and u2 the thin direction;
  - **W** is the width of the rigorous set projected on a covector u (`X.project(u)`);
  - **true** is the width of the true image of the box along u: the hull of 16 boundary-point images, DOP853 1e-13
    (`tests/b17_checkpoints.py`).
- **Ratios.**
  - u1 ratio = W1/true1 and u2 ratio = W2/true2.
  - A checkpoint PASSES iff u1 ratio ≤ K, u2 ratio ≤ K, and the "fake" (off-manifold) width ≤ K · true2 · g, with
    **K = 5**. g is a stored gain; you may predict only u1 and u2 and treat fake as a secondary.
- **The failure being retried.** The W0 = 1e-7 run, called A3, FAILED one checkpoint: t = 793.2346, u2 = 8.77. Its
  other checkpoints passed: 295.89 (1.06), 800.09 (2.83), 801.23 (2.76), 805.23 (2.26).
  - Cause checks showed W2 is dominated by E along u2.
  - E self-feeds: the injected term dDe = ([Dphi(hull)] − D1c)·e is about 99% of the per-step error near 793.
  - E met a pre-periapsis dip of true2: about 1.9e-7, against 8–12e-7 a few t-units later.
- **The pre-test.** A quarter piece, half size in each direction, cut from the A3 state at t = 792 with E kept, showed
  that E's self-feeding growth rate along u2 is 0.503× the full box's over 792 → 793.23.
- **The retry, "branch S".**
  - Four pieces at W0 = 5e-8 tile the old box exactly. Their centre offsets (du, dp) are mm (−,−), mp (−,+), pm (+,−)
    and pp (+,+), each ±5e-8.
  - Each piece runs from t = 0 to t = 805.3, in the same method and settings, and is checked at **8 time
    checkpoints: 283.8852, 290.8497, 291.8852, 295.8852, 793.2346, 800.0941, 801.2346, 805.2346**, with the true widths
    from its own file.
- **PASS rule.**
  - A piece PASSES iff all 8 checkpoints pass, its controls hold, and it does not THREW.
  - The retry PASSES iff all 4 pieces pass.
  - `retry_s/read_retry.sh` is the mechanical reader.

## 2. Read-only inputs, and the exclusions
All paths are relative to /Users/sumit/Github/quantum/qsim/capd/horseshoe_results/so_mn/erep/ unless stated otherwise.
- **Allowed.**
  - `main_redo/run.out`: the W0 = 1e-7 run, t 0 → 291.9. Its `# step` lines carry maxE and wall time; it has the
    early CHECKPOINT/PROJ lines.
  - `main_cont/run.out`, `main_cont/RESULT.md`: A3, t 291.9 → 805.3+, the 5 checkpoint lines and the PROJ lines.
  - `main_cont/cause_checks/`: RESULTS_prime.md, b_prime.json (the W2_E / W2_poly / true time series every 20
    t-units), a_prime.json (the true-width curves), REPLAY_RESULT.md, PRETEST_RESULT.md, replay/run.out, pq/run.out,
    m0|m1|m2/run.out.
  - `retry_s/cp/b17_cp_5e-8_{mm,mp,pm,pp}.txt` and `.log`: each piece's true widths and gains per checkpoint;
    `retry_s/PRELAUNCH.md`, `retry_s/read_retry.sh`.
  - `../../mn_smoke/b17_cp_1e-7.txt`: the old box's true widths.
- **EXCLUDED** (they leak the retry's progress; do not open, list or stat them):
  - `retry_s/mm/`, `retry_s/mp/`, `retry_s/pm/`, `retry_s/pp/` (run.out, guard.log, st*);
  - `retry_s/refs/`, `retry_s/launch.log`;
  - `../../kerr/b15e/a4_launch.log`;
  - any `ps` output for mn_so_piece;
  - git log or git show of commits after this brief's commit.
- **Compute.** None, or seconds of Python over the allowed files. Launch nothing. Do not edit main.

## 3. Required output: `retry_s/PREDICTION_SEALED.md`
1. **A table, piece × checkpoint (4 × 8).** For each cell: predicted u2 ratio (point and 80% interval), predicted u1
   ratio (point and interval), and PASS/FAIL. Then per-piece PASS/FAIL and the overall verdict, with your probability
   that the retry PASSES.
2. **The scaling model, explicit.** How W_E, W_poly and true scale with W0 over the flight, and how you used the
   pre-test's 0.503 and the A3 time series. State every assumption, including any about how the 4 pieces differ from
   one another.
3. **Falsifiers.** Which observed outcomes would refute your model, as opposed to only missing an interval.
4. **Labels.** Mark everything `[model: Fable 5.2]` and UNVERIFIED. Cite literature at source with section and
   equation, or mark it "from memory".

## 4. Sealing and grading (fixed now)
- **Sealing.** Commit ONLY `retry_s/PREDICTION_SEALED.md` to the branch `fable/2026-11-26-retry-predict`, from main at
  this brief's commit, and push the branch. Send the commit sha and the file's sha256 to the Bridge. The authoring
  session (Quantum) does not open the branch or the file until `read_retry.sh` has produced the retry's VERDICT.
- **Grading** (descriptive, recorded beside the retry result). It is done after the VERDICT exists:
  - (i) the fraction of the 32 cells whose actual u2 ratio lies inside the predicted 80% interval, and the same for u1;
  - (ii) whether each piece's PASS/FAIL was right (4 calls);
  - (iii) whether the overall verdict was right;
  - (iv) the Brier score of the stated PASS probability.
  - A piece that THREW, or a checkpoint not reached, counts as FAIL for (ii) and (iii) and is excluded from (i).
  - The grading changes nothing about the retry's own reading.
