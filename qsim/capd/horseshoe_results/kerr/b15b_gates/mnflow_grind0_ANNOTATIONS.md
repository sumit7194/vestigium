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
