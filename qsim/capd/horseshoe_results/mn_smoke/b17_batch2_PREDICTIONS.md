# Predictions, written BEFORE the runs (2026-10-24): B17 batch 2

All jobs use projected section rows (PROJ_ROWS) and Taylor order 20 unless stated, at nice 19. Each logs its number of
CAPD reorganisation events (steps after which B is exactly the identity).

| job | change from the reorg-OFF + projrows 1e-12 run | prediction |
|---|---|---|
| J1 | 1e-12, reorganisation factor 100 | absolute (W-independent) errors still trigger folds often: many events; u2 at Σ ≫ 10× (default-like). FAIL |
| J2 | 1e-12, factor 1e3 | fewer events; u2 at Σ between J1 and reorg-off (10–1000×). FAIL |
| J3 | 1e-12, factor 1e4 | few or no events; ≈ reorg-off (u2 at Σ within 2× of 8.15). FAIL at k = 5 |
| J4 | 1e-7, reorganisation off | the second-order seed dominates in swing 1: throws near t ≈ 296 (the earlier 8-D 1e-7 reorg-off diagnostic died at 296.28). FAIL |
| J5 | 1e-6, reorganisation off | throws near t ≈ 290.5 (diag8_noreorg died at 290.50). FAIL |
| J6 | 1e-12, reorganisation off, ORDER = 25 | the excess is representation-driven, not truncation: u2 at t = 793.2 and at Σ within ±20% of 6.58 and 8.15. FAIL at k = 5 |

Interpretation fixed in advance:
- If J6 moves by > 20%, the remaining excess is truncation/step-driven. Otherwise the "C0 tripleton floor" hypothesis
  gains support (it is not established by this alone).
- k = 5 stands for these records. Any k_c is a separate amendment, computed from the h-set margins without these
  numbers, and registered before any re-verdict.
- The 200-point non-rigorous section-spread check is done for J4 and J5's W0 when they reach a section (they are
  predicted not to). If they do not, it is done on the 1e-7 and 1e-6 centre-box images at the first time checkpoint.
