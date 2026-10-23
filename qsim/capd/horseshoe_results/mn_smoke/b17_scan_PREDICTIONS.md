# Predictions, written BEFORE the runs (2026-10-24): W-scan under the final first-order configuration

Configuration: 8-D augmented field, correlated lifts, reorganisation OFF, projected section rows, order 20, nice 19.
W₀ ∈ {1e-8, 1e-9, 1e-10}, full return, B17 (k = 5). For W₀ ≤ 1e-8 the references are variational (B17a).

Model: the first-order floor F_i comes from the 1e-12 run (u2 ratios 1.00 1.03 1.45 1.46 2.44 6.58 2.12 2.11 2.11
8.15). The second-order excess at checkpoint i is E_i(W) = ratio_i(W) − F_i, assumed ∝ W^p with p ≈ 1. At t = 284
this is already seen: 1e-7 gives 5.96 (E ≈ 5.0) and 1e-6 gives 53.9 (E ≈ 52.9), so p ≈ 1.0 and E ≈ 5.3e7·W at 284.

Predictions:

| W₀ | at t = 284 | through and after the swings | B17 |
|---|---|---|---|
| 1e-8 | u2 ≈ 1.5 | swing 1 amplifies E strongly, so u2 ≫ 5 after swing 1 (an earlier 8-D 1e-8 run was ~80× fat in x at 296) | FAIL, likely already at t_p1 + 1 or + 5 |
| 1e-9 | u2 ≈ 1.05 | borderline: u2 at t_p1 + 5 within 2–20× | FAIL or marginal |
| 1e-10 | u2 ≈ 1.0 | ≈ the floor (within 20% of the 1e-12 ratios) | FAIL at k = 5 (the floor already exceeds 5 at 793.2 and at Σ) |

Scaling fit: at each post-swing-1 checkpoint, fit E_i ∝ W^p over the points that survive. If p is not within 1 ± 0.3,
the second-order story is in doubt and the second-order step would be aimed at the wrong mechanism.

Feasibility of entrance subdivision, fixed in advance: the entrance has d = 2 (the section is 2-D; on Σ, or at a time
cut, the box's image spans the 2-D on-shell needle). Splitting is needed only along the directions whose excess drives
the failure, which the scan does not separate. So the count is estimated as (W_piece / W_s)^2 for the worst case and
(W_piece / W_s) if only the needle's long axis needs splitting, with W_s the largest surviving W₀ at k = 5 (or at
k_c later). Cost per piece is ~70–85 min wall per full return at nice 19.
