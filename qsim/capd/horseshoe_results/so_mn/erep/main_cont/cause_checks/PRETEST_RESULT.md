# Branch-S scaling pre-test (GATE): result, read under RETRY_S_REGISTRATION.md (9c5be24)

Ran 2026-11-24 22:19–23:42. Run P: a quarter piece from a byte copy of st.t792.0198, E kept, mn_so_inj (sha ed553578…),
wall time 5031 s, 1 core, nice 10. Read with `pretest_read.py`. Written by Claude Opus 5.5 (Quantum).

## Checks
- **F1 must-fire: PASS.** The replay's own run.out, put through the same reader, prints `ratio 1.0000 -> FAIL`, as
  required.
- **F0 identity: PASS.** The rebuilt binary with INJ_QUARTER unset reproduces m0's 5-step INJ and STOP lines byte for
  byte.
- **Consistency: PASS.** All of P's INJ lines end `new<=sum OK`.

## Reading
- **g_u2 = 1.158377e-02 against g_ref = 2.300969e-02, so the ratio is 0.5034 ≤ 0.70: PASS.**
- The u1 line, reported only, gives 3.7742e-04 against 7.4964e-04, the same ratio of 0.503.
- **Descriptive.**
  - The ratio is about 0.50, the value expected if dDe scales with the hull width.
  - The p2 share falls from 0.0096 to 0.0024, about 1/4.
  - S4 domain leaves: 11001, against the replay's about 206k by step 5400.
  - P's CHECKPOINT line compares a quarter piece with the whole box's true widths, so it is NOT read, as registered.

## Stated limit (unchanged)
This shows the mechanism in one late window (792 → 793.23), with E inherited from the W0 = 1e-7 run: halving the piece
halves E's self-feeding growth rate. It does NOT show that a from-t = 0 W0 = 5e-8 retry passes B17.

The gate is open. The 4-piece retry needs Sumit's go, which the Bridge will take to him, and then the labelled pre-launch
amendment: the piece checkpoint files, the C-floor reference runs, and the piece-centre lifts.
