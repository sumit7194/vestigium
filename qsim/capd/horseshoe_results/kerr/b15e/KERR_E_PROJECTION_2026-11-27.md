# kerr_e cost projection after 7 edge records (2026-11-27 00:2x)

Written by Quantum-personal (Claude Opus 5.5) at the personal Bridge's request. The trigger was 7 EP records in total: N1N2 has 3 and the Air has 4. This file makes no change to any job.

## Data

Each chunk has 2 sides × 64 = 128 edge pieces (`cover Ni Nj 16 16 64`, hs_cover.cpp:490). All 7 records so far have 4 leaves, which is 7 evaluations, and 3475–3683 replay steps.

| Chunk | Machine | Started | EP records (time) | Hours per piece |
|---|---|---|---|---|
| N1N2 | Mac mini, 1 core, nice 10 | 11-26 11:29:56 | E/0/0 15:13; E/0/2 23:12:59 | 3.7 for the first piece; 4.0 average for pieces 2 and 3 |
| N4N5 | Air | 11-26 12:59:19 | E/0/0 18:03:56; E/0/1 00:04:05 | 5.1, then 6.0 |
| N5N0 | Air | 12:59:19 | E/0/0 21:10:19 | 8.2 |
| N5N1 | Air | 12:59:19 | E/0/0 21:09:50 | 8.2 |
| N2N3 | Air | 12:59:19 | none by 00:22 | more than 11.4 |
| N3N4 | Air | 12:59:19 | none by 00:22 | more than 11.4 |

The Air runs 5 chunks on 4 performance cores and 4 efficiency cores, and it is fanless. N4N5's second piece took longer than its first, which may be thermal or scheduling slowdown.

## Projection

The projection is linear: 128 pieces at the rate seen so far. Each watchdog is HS_WATCHDOG_S=2592000 (30 d), set by a single alarm() at start. If it fires, the job ENDS with exit 124 and fails closed.

| Chunk | Projected total | Projected end | Watchdog fires | Binds? |
|---|---|---|---|---|
| N1N2 | ~21 d (3.7 + 125 × 4.0 h) | ~12-17 | 12-26 11:29:59 | no, ~9 d margin |
| N4N5 | ~29–32 d (126 × 5.5–6.0 h) | ~12-26 to 12-28 | 12-26 12:59:19 | borderline, likely yes |
| N5N0 | ~44 d (128 × 8.2 h) | ~01-09 | 12-26 12:59:19 | YES |
| N5N1 | ~44 d | ~01-09 | 12-26 12:59:19 | YES |
| N2N3 | more than 61 d (128 × >11.4 h) | after ~01-26 | 12-26 12:59:19 | YES |
| N3N4 | more than 61 d | after ~01-26 | 12-26 12:59:19 | YES |

Caveats:
- The first 1–3 pieces of each chunk cover only s ∈ [-1, -0.906] of side 0.
- If later pieces need more bisection (more leaves), the cost per piece rises.
- N1N2's step counts fall slowly (3683, 3679, 3675). That fits a smooth cost along the edge but does not prove it.

## Consequence

Every chunk takes about 3 weeks or more. On all five Air chunks, the 30-day watchdog would end the job before it finishes. Under the no-hard-caps rule that must not happen.

So TIMER_RAISE_PLAN.md (52f103c) now applies to the Air chunks. It needs Sumit at the Air: either `sudo DevToolsSecurity -enable` once, or approving the lldb prompts locally. Its decision date was about 12-06. Options for the Bridge and Sumit are in the message sent on 2026-11-27.
