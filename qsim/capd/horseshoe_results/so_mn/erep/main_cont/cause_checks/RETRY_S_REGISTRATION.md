# A3 branch S: scaling pre-test (a GATE) and the subdivision retry

Status: REGISTERED. The Bridge's instruction was "put the scaling pre-test IN the same draft, as a GATE". It is committed
before the pre-test or the retry runs, and before any quarter-piece number exists.

- **Go status.** The pre-test runs on the Bridge's go (given 2026-11-24, for the pre-test only, once registered). The
  retry needs Sumit's go, which the Bridge will take to him with the pre-test result.
- Diagnostic up to the retry. A3's verdict is unchanged. Written by Claude Opus 5.5 (Quantum).

## Why the pre-test is not "200 steps from t = 0"
- The W0 = 1e-7 run's first 200 steps (main_redo/run.out) have maxE of 1e-17 to 6e-17. That is a floor of Taylor
  remainder that does not depend on W0. Splitting the box would barely change it.
- So a from-t = 0 pre-test could FAIL even if subdivision helps later. The regime that failed A3 is the late,
  self-feeding one: dDe = ([Dphi(K)] − D1c)·e is 99% of the injection near 793. The gate tests that regime directly.

## 1. Pre-test (GATE)
- **Question.** Does E's self-feeding growth rate fall when the piece is smaller?
  - dDe ∝ ([Dphi(K)] − D1c), which grows with the hull K. K is dominated by the polynomial part along u1 (about 4e-3,
    against E about 1e-6).
  - So halving the piece should roughly halve the per-step dDe/E.
- **Run P (quarter piece).**
  - A byte copy of main_cont/st.t792.0198, with `INJ_QUARTER=1` (tests/mn_so_inj, sha256 ed553578…, guard passed).
  - The quarter piece r = rc + ρ/2 with rc = (−1/2, −1/2): x' = x + C rc + H(rc, rc)/2, C' = (C + H rc)/2, H' = H/4.
    **E is kept unchanged.**
  - The same environment and window as the replay: `SO_EREP=zsym SO_FIXED_REDO=1 INJ_LOG=1`, T_end 793.3.
  - About 50 steps, ~80 min, 1 core, nice 10, 0.5 GB declared.
- **Metric.** g = (dDe tagged width) / (inherited width), on the u2 `INJ cp` line at 793.2346: the window's self-feeding
  growth relative to the E it started with.
  - Reference g_ref, from the counted replay (d21fa6b) at the same line: 3.306762e-08 / 1.437117e-06 = 0.02301.
- **Pass rule (u2 primary; u1 reported).**
  - PASS if g_P ≤ 0.70 × g_ref. The expected value if dDe scales with the hull is about 0.5.
  - FAIL if g_P ≥ 0.90 × g_ref.
  - INCONCLUSIVE in between. The retry is not recommended; report.
- **Not read.** P's CHECKPOINT line compares a quarter piece with the whole box's true widths, so its PASS/FAIL or
  HARNESS-ERROR flag means nothing here.
- **Must-fire F1** (the W0 = 1e-7 set through the same pre-test code must FAIL the rule). The evaluation script `pretest_read.py`, applied to
  the replay's own run.out (no quarter), must output FAIL (g = g_ref, ratio 1.00 ≥ 0.90). If it does not, the reading is
  void.
- **Identity check F0** (the rebuilt binary changed nothing else).
  - 5 steps from a byte copy of st.t792.0198, with `INJ_LOG=1` and INJ_QUARTER unset, STOP_AFTER_T = 792.14.
  - Its INJ and STOP lines must be byte-identical to m0/run.out's. If not, P is void.
- **Consistency.** P's INJ lines end `new<=sum OK`.
- **Stated limits.**
  - This tests the MECHANISM, in one late window (792 → 793.23), with E inherited from the W0 = 1e-7 run. It does not
    show that a from-t = 0 retry passes B17.
  - The quarter piece is one of four, chosen in advance (rc = (−1/2, −1/2)).

## 2. The retry (only if the pre-test PASSES, and only on Sumit's go)
- **Pieces.** 4 pieces at W0 = 5e-8 (the 2 × 2 split of the W0 = 1e-7 box, centres at ±W0/2 in (x, px)), each from
  t = 0.
- **Settings.** zsym + SO_FIXED_REDO=1. Same binary as A3 (mn_so_erep 4a48b59a…), same Taylor order, MPFR 128 and step
  control.
- **Checkpoints and criteria.** B17 at the same time checkpoints. Each piece needs its own checkpoint file, with true
  widths from b17_checkpoints.py at that piece's centre and W0, and K = 5. The four files are generated and committed
  before any piece runs.
- **PASS** needs all 4 pieces to pass all 5 time checkpoints, with the A3 controls (C-floor containment against
  reference runs at the piece's corners, C-identity, C-steps). Any control failing → INVALID.
- **Cost.** About 4 × 3 days ≈ 300 core-h. The pieces can run in parallel. Each launch is a slot request to the Bridge.
- **Before launch** (a separate labelled amendment): the piece-centre lift parameters, the reference-run plan for
  C-floor, and the exact checkpoint files.
