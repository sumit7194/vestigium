# Plan A V2/V3 outcome (2026-10-11), evaluated exactly as registered (PREREG_cuspis_sub45_check.md, PLAN A, 2abb00d)

Data: `chl_planA_V23_nodes.jsonl` (98 jobs) → `chl_planA_V23_eval.py` → `chl_planA_V23_eval.json`.

**V2b, v2 sparse vs v2 dense (≤ 1e−10): PASS, 30/30 (worst 4.1e−14).**

**V2a, frozen v1 DENSE vs recorded Stage-2 sparse (≤ 1e−8): FAIL, 19/30.**
- **The 10 highest-M nodes (M ≈ 11.2–11.5, t ≈ 3.70–3.98) fail.** The recorded value, v1-dense and v2-sparse all
  differ (v1-dense is even negative), so no stepper is trustworthy there yet.
- **A heavy node also fails:** t = 0.224, q = 6.138 at 15°. The recorded value is 2.305465e−4, while
  v1-dense = v2 = 2.305477e−4, so the recorded value is off by 5.5e−6 relative.

**V3, the 3a-failed nodes with v2 (B vs C ≤ 1e−8, smooth decay): FAIL, 0/4.**
- t = 0.3, q = 22.8: B−C = 2.7e−8.
- t = 1.37, q = 23.9: B−C = 6.4e−6.
- q = 31.8 and q = 32.9: set B fails outright ("integrate_v2: step rejected 40 times" at x = 1.073 and x = 1.258).
  Set C was OK on all four nodes.

**Registered consequences:** Stage 2's in-grid values are re-audited first; V1 is that re-audit. Plan C is
considered. **Plan B is not registered.**

## Bridge ruling (3): bound on the 10 high-M nodes, replacing the earlier "negligible" estimate

`chl_planA_highM_bound.txt`:
- **Definition:** B(θ) = Σ over the 10 nodes of w·max(|rec|, |v1-dense|, |v2|), with w = wt·wq·q²/cosh²(πt) (the
  Stage-2 quadrature weight).
- **Conservative form:** the reported margin is 2B/a, because a correction could be as large as the difference
  between two candidates.

| θ | 2B/a | threshold |
|---|---|---|
| 40° | 2.1e−10 | 6.3e−6 |
| 30° | 1.9e−9 | 5.7e−5 |
| 26.565° | 4.0e−9 | 1.35e−4 |
| 20° | 2.1e−8 | 7.1e−4 |
| 15° | 1.2e−7 | 2.5e−3 |

- **Result:** below the threshold at every angle, by at least 4 orders of magnitude.
- **Caveat:** this bounds the nodes' effect only if each node's true value lies within the span of the three computed
  values. No stepper is certified at these nodes.

## Bridge ruling (5): the V3 smooth-decay criterion, computed and recorded

`chl_planA_V3_smooth.txt`:
- **NOT EVALUABLE AS REGISTERED.** The V3 job list computed no v2 nodes at the neighbouring q points (q ± 3 on the 3a
  grid), so the "per-step ratio within 10% of its neighbours" has no neighbours to compare with. My first evaluator
  marked it as passed by mistake: it read a dictionary of start-series coefficients as a boolean. That was caught
  before any write-up, and V3 fails on B−C regardless.
- **Proxy, labelled as such:**
  - f = q²·trG.
  - The per-3-unit ratios in the 3a stable region (set B, where B = C to ≤ 1e−8) are compared with the per-3 ratios
    implied by the V3 set-C values (a geometric mean over 9 units).

  | node | max consecutive change |
  |---|---|
  | t = 0.3, 15° | 1.3% |
  | t = 0.3, 40° | 0.6% |
  | t = 1.37, 15° | 12.8% |
  | t = 1.37, 40° | 8.6% |

  - At t = 1.37 and 15°, the change exceeds 10% **already inside the stable region** (11.6%). As worded, the 10%
    rule would not separate good from bad decay at that node.
  - This is recorded, not reinterpreted.

Environment: Python 3.13.12 (sims/.venv; numpy 2.5.0, scipy 1.18.0, mpmath 1.3.0, python-flint 0.9.0), macOS 26.5
arm64 (ENVIRONMENT/).
