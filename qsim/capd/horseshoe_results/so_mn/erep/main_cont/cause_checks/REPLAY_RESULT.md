# A3 R3a injection replay: result, read under REPLAY_AND_RETRY_RULE.md (493e046)

The replay ran 2026-11-24 21:53–22:14: mn_so_inj (sha c43c049a…), 50 steps from a byte copy of st.t792.0198, wall time
4912 s, 1 core, nice 10. The must-fires are M0/M1/M2 (5 steps each). Outputs: `replay/run.out`, `m0/`, `m1/`, `m2/`.
This is diagnostic only; A3's verdict stays FAIL (controls hold). Written by Claude Opus 5.5 (Quantum).

## Checks
- **I1 identity: PASS.** The replay's three `PROJ t t=793.2346306025` lines and its `CHECKPOINT t` line are
  byte-identical to main_cont/run.out lines 335–338 (diff empty).
- **I2 consistency: PASS.** All 4 INJ lines end `new<=sum OK`; there are 0 VIOLATED.
- **Must-fires** (u2, `end` line, 5 steps):

  | Run | p0 | p1 | p2 | dDe | Status |
  |---|---|---|---|---|---|
  | M0 (baseline) | 0.0000 | 0.0000 | 0.0096 | 0.9904 | — |
  | M1 (e ×1000) | — | — | — | 1.0000 | **UNINFORMATIVE** by rule: M0's dDe share was already ≥ 0.9. Reported, not counted. |
  | M2 (p2 ×1000) | — | — | **0.9067** | — | **PASS** (≥ 0.9) and informative (M0 had 0.0096). The tagged p2 width scaled exactly ×1000 (3.3377e-11 → 3.3377e-08) while dDe was unchanged. |

- So the split measurement is usable. No must-fire threw.

## Reading (u2 INJ line at 793.2346)
- **Shares:** p0 0.0000, p1 0.0000, p2 0.0096, dDe 0.9904.
- **p2 + dDe = 1.000 ≥ 0.6, so BRANCH S (subdivide from t = 0) under the registered rule.** The u1 line agrees: dDe 0.9907.

## Registered limit, stated with the numbers
- The window's new columns carry 3.34e-8 of the u2 error width, against 1.437e-6 inherited at 792.02. That is about 2% of
  E along u2.
- So the reading describes the injection mix in the last 1.2 t-units. It does not describe what built the inherited E.
  The rule reads shares only, as registered, so the branch stands.
- A per-step dDe of 99% is consistent with E feeding itself: dDe = ([Dphi(K)] − D1c) e is proportional to e. But this
  window does not establish that the same mechanism built the inherited E.

The retry for branch S is drafted next. It goes to the Bridge, and its scale (about 4 × 3 days, ~300 core-h) needs Sumit's
go before any launch.
