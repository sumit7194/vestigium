# Row annotations for mnflow_grind0.jsonl (the jsonl itself stays append-only; the worker writes it)

Accepted by the Bridge on 2026-11-19 (relayed in this session). Rows 21 onward were written after the t_eval=[] memory fix (02391fb).
For these rows the logged final t in `solve_ivp` is the largest t at which the event function was evaluated, not `sol.t[-1]`.

Every annotated row reads: **status -1, logged t = max event-eval t (validated path).**
- The values come from `y_events` and do not depend on the logged t.
- The status -1 path was checked 6/6 bit-identical (d81ecb9).
- 19 of the 20 rows written before the fix share status -1: grind tasks fail after the crossing has been found.

| row | id | status | events | logged t | annotation |
|---|---|---|---|---|---|
| 21 | G3_044_P | -1 | True | 1313.7753 | status -1, logged t = max event-eval t (validated path) |
| 22 | G3_045_P | -1 | True | 1462.3194 | status -1, logged t = max event-eval t (validated path) |
| 23 | G3_061_P | -1 | True | 1924.1442 | status -1, logged t = max event-eval t (validated path) |
| 24 | G3_064_P | -1 | True | 1868.3977 | status -1, logged t = max event-eval t (validated path) |
| 25 | G3_068_P | -1 | True | 1457.7807 | status -1, logged t = max event-eval t (validated path) |
| 26 | G3_076_P | -1 | True | 1540.6834 | status -1, logged t = max event-eval t (validated path) |
| 27 | G3_079_P | -1 | True | 1244.1421 | status -1, logged t = max event-eval t (validated path) |

Rows appended later get the same annotation. b15b_gates_eval.py must carry this note into the gates result.

## Claim-worker rows (2026-11-19 23:45 to 2026-11-20 08:10; mnflow_claim{0,1,2}.jsonl)

These are written under the same fix, so each row reads: **status -1, logged t = max event-eval t (validated path)** unless a different status is stated.

| file | id | status | events | logged t | annotation |
|---|---|---|---|---|---|
| claim0 | G3_127_P | -1 | True | 1739.3759 | status -1, logged t = max event-eval t (validated path) |
| claim0 | G3_148_P | -1 | True | 1750.0013 | status -1, logged t = max event-eval t (validated path) |
| claim0 | G3_175_P | -1 | True | 1384.7242 | status -1, logged t = max event-eval t (validated path) |
| claim0 | G3_188_P | -1 | True | 1858.2693 | status -1, logged t = max event-eval t (validated path) |
| claim0 | G3_199_P | -1 | True | 1735.1089 | status -1, logged t = max event-eval t (validated path) |
| claim1 | G3_129_P | -1 | True | 1707.6620 | status -1, logged t = max event-eval t (validated path) |
| claim1 | G3_147_P | -1 | True | 1418.0456 | status -1, logged t = max event-eval t (validated path) |
| claim1 | G3_181_P | -1 | True | 1848.1469 | status -1, logged t = max event-eval t (validated path) |
| claim1 | G3_196_P | -1 | True | 1276.1481 | status -1, logged t = max event-eval t (validated path) |
| claim2 | G3_136_P | -1 | True | 1928.7422 | status -1, logged t = max event-eval t (validated path) |
| claim2 | G3_161_P | -1 | True | 1919.3025 | status -1, logged t = max event-eval t (validated path) |
| claim2 | G3_165_P | -1 | True | 1710.0740 | status -1, logged t = max event-eval t (validated path) |
| claim2 | G3_187_P | -1 | True | 1539.4386 | status -1, logged t = max event-eval t (validated path) |
| claim2 | G3_189_P | -1 | True | 1860.6147 | status -1, logged t = max event-eval t (validated path) |
