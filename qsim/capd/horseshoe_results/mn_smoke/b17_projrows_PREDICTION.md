# Prediction, written BEFORE the run (2026-10-23): B17 at 1e-12, reorganisation OFF, projected section rows

Change: at the two SECTION checkpoints only, each covector n of A is replaced by n' = n − (n·f(x̄)/f_y(x̄))·e_y (the
u1, u2, n_H and off-manifold rows; e_y is kept as is). x̄ is the centre's crossing state from the checkpoint file. On Σ,
n'·Δx = n·Δx, so the measured quantity is unchanged and the reference is unchanged. Time checkpoints are unchanged.

Prediction (agreed with the Bridge):
- sec_down and sec_return u2 drop to the time-checkpoint level, ≤ ~7× (they were 1,026× and 5,597×).
- u1 stays at ~1.0–1.2.
- Every time checkpoint is identical to the reorg-OFF run (same propagation).

Logged:
- the residue |n'·f(x̄)| per row (interval-evaluated);
- the offset of CAPD's image midpoint from x̄ in each row (CAPD's internal x0 is not exposed; the residue at x0 is
  bounded by |n'|·|Df|·|x0 − x̄|);
- w(rt) and a rough size of the second-order term ‖A·Df‖·w(dx)·w(dt).

Not done at 1e-12: the 200-point non-rigorous spread check. Double precision cannot resolve a 1e-12 box (B17a), so it is
planned for the 1e-7 and 1e-6 runs.
