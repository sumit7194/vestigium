# A3 R3a cause checks (a) and (b): predictions, written and committed BEFORE either check runs

The Bridge gave the GO on 2026-11-24, for existing files only, 1 core, nice 12. These are diagnostics, NOT criteria:
nothing here changes A3's registered verdict (FAIL, controls hold). Written by Claude Opus 5.5 (Quantum).

Hypotheses for the R3a ratio u2 = W2/tu2 = 8.77:
- **H1 (my best guess): slow error build-up plus a small true width.** The zonotope error part E grows over the ~500
  t-unit flight between periapses. At 793.23 the true u2 width is at a pre-periapsis minimum, so E's excess shows.
- **H2: a local step-size / h-adaptation event** shortly before 793.23. E stays small, then jumps late.
- **H3: the polynomial part is too wide.** The C r + H(r,r)/2 part, not E, carries the excess.
- **H4: the reference is wrong.** The stored tu2 = 1.895e-7 is not the true u2 width.

## (a) True thin width along the centre orbit (Python, double, about 1 minute)
Method: b17_checkpoints.py's centre orbit and variational equations (DOP853 1e-13). The linear true width along the
thin singular direction is w2(t) = 2 W0 sum_j |u2(t) . (Phi(t) D_in)_j| = 2 W0 sigma2 |v2|_1, on t in [276, 300]
and [780, 806] with step 0.1. The same is done for u1.
- **Control a0:** at the 5 A3 time checkpoints and the 4 first-passage ones, the linear w1 and w2 must match the stored
  hull values (b17_cp_1e-7.txt) within 5%. If not, (a) is void and is reported.
- **H1/H3 predict:** w2 has a real, smooth minimum region near 793 (w2(793.23) within 5% of 1.895e-7, and w2 within a
  factor 3 of it over 793.23 +/- 0.5). The first passage shows the same kind of pre-periapsis low (about 2e-7 to 3e-7
  near 284-292).
- **H4 predicts:** recomputed w2(793.23) differs from 1.895e-7 by more than 5% (the stored value is too small), or w2
  is smooth at about 8e-7 near 793 with 793.23 an outlier.
- (a) cannot tell H1, H2 and H3 apart. That is what (b) is for.

## (b) Width split over the saved states (Python reader of st.t292.0030 ... st.t792.0198, 26 files, seconds each)
Method: for each saved state at time t_k, take the centre orbit's thin and thick directions u2(t_k), u1(t_k) from (a).
Then project the state on them, with sizes in double precision; this is a diagnostic, not rigorous:
- W_poly = the width of u.(C r + H(r,r)/2) over r in [-1,1]^2 (an 8 x 8 sub-box hull, as so::Set::project);
- W_E = 2 sum_j |u . g_j| over the error generators.
- **Control b0:** the state centre x(t_k) matches the DOP853 centre orbit within 1e-6 in each of the first 4 coordinates,
  and W_poly / w_true(t_k) is in [0.8, 1.25] at every k. If either fails, the split is reported as unreliable.
- **H1 predicts:** W_E grows over the whole flight, with no single 20 t-unit interval holding more than half of the total
  growth in log W_E from 292 to 792. At 792.02, W_E > 0.5 x (W_poly + W_E - w_true), so E carries most of the excess.
- **H2 predicts:** the growth is concentrated late: the 772 -> 792 interval holds more than half of the log growth, or
  W_E jumps by more than 3x between the last two saved states.
- **H3 predicts:** W_poly / w_true(792.02) > 1.5 while W_E is below half the excess.
- If none of these patterns fits, that is reported as "cause not identified by (b)".

Held for Sumit's word: the ~45 min logged replay from st.t792.0198 (the P2 vs dDe split of the injected error) and any
registered retry.
