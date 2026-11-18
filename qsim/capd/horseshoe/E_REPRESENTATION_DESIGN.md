# E representation for the MN second-order set: candidate designs

Status: DESIGN ONLY, for offline scoring. Nothing here has been run. Not registered with the Bridge yet.
Author: Quantum-personal session, 2026-11-18, on the brief relayed by Quantum.
Provenance (models, added 2026-11-18 because 3dc0e3e's trailer names only Opus 5.5): sections 0-6 were written by
Claude Fable 5.2 in the Quantum-personal session. The offline scorer `so_mn/wrap_test/e_score.py` and the first scores
are by Claude Opus 5.5 in the Quantum session (3dc0e3e). Section 7 (the ZG reduction and the C3 note) is by Claude
Opus 5.5 in the Quantum-personal session. Treat all of it as outside-reviewer input until it is registered with the Bridge.
Inputs read (through a digest, not line by line by me): `tests/so_set.h` (`step()`, `qr_frame`), `tests/mn_so.cpp` (dump code),
`WRAPPING_TEST.md`, `horseshoe_results/so_mn/wrap_test/RESULT.md` and `result_{A,B,CA}.txt`.

## 0. What the step needs from E

The step uses E in exactly three places:

1. `hull(E)`, a box. It enters `K = X.hull()` and `e` in `s += (D1K - D1c) * e` (the dDe injection).
2. The update: the new E must contain `{ A e + sigma : e in E, sigma in s }` for the real matrix `A = Dphi(x)`, `A in D1c`.
3. `project(u)`: the width of `u . E` for the checkpoint covectors (u1, u2, nH, off0..off3).

Any representation that supplies these three with a proof of (2) is admissible. The frame, the generators and any
non-rigorous numbers used to choose them do not enter the proof.

Notation for the scorer. Window steps k = 1..n. Dump record k gives `D_k` (D1c, interval 8x8), `S_k` (interval
8-vector, ambient coordinates at t_k, `S_k = P0_k + P1_k + P2_k + DDE_k`), and the run's new `B_k`, `re_k`.
`B_0`, `re_0` come from the start state of the window. `mid`, `mag(a) = max(|lo|,|hi|)`, `rad^(a)` = an upper bound
of the radius about the chosen midpoint. All interval operations rounded outward at 128 bits.

Two observations drive everything below.

**(a) W_lin is attainable rigorously.** For a linear map followed by a Minkowski sum with a box, the support
function along an adjoint-transported covector is propagated exactly: if `w_{k-1} = A^T w_k` then
`w_k . (A e + sigma) = w_{k-1} . e + w_k . sigma`. No frame appears, so nothing wraps. This is the W_lin formula of
WRAPPING_TEST.md read as an enclosure rule (candidate S). The dual statement, keeping every generator, is the
unreduced zonotope (candidate Z).

**(b) Pinning a column is the wrong object.** The leak is `sum_j |u2 . B e_j| w(re_j)`. It vanishes for a covector u
only if the pulled-back u is a ROW of `B^-1`, and that row must be transported by the adjoint flow. In an orthogonal
frame one such row can be held exactly (as a column), not the seven the B17 check uses. Candidate S holds any number.

## 1. Candidate Z: unreduced zonotope (recommended primary)

**Set.** `E = { c + G xi : xi in [-1,1]^N }`, `c` an interval 8-vector, `G` an interval 8xN matrix (every real
selection of `c`, `G` allowed).

**Rules.**

- Z.0 (start of window, from a box state): `c_0 = B_0 mid(re_0)`, `G_0 = B_0 diag(rad^(re_0))`. From t = 0, `B_0 = I`.
- Z.1 (step): pick the thin point `mu_k = mid(S_k)` and `rho_k,i = mag(S_k,i - mu_k,i)`. Then
  `c_k = D_k c_{k-1} + mu_k`, `G_k = [ D_k G_{k-1} | diag(rho_k) ]`. So `N_k = N_{k-1} + 8`.
- Z.2 (hull): `hull_k,i = c_k,i + [-1,1] * sum_j mag(G_k,ij)`.
- Z.3 (projection): `W_Z(u) = width(u . c_k) + 2 sum_j mag(u . G_k[:,j])`.
- In the real step: `e := hull` from Z.2 in `s += dD * e`, and in `K`. Nothing else in `step()` changes; `qr_frame`
  and `krawczykInverse` are no longer called.

**Rigour.** Induction. Let `e = c~ + G~ xi` with real selections. For real `A in D_k`, `sigma in S_k`, write
`sigma = mu_k + diag(rho~) zeta` with `|zeta_i| <= 1`, `rho~_i <= rho_k,i`. Then
`A e + sigma = (A c~ + mu_k) + [A G~ | diag(rho~)] (xi, zeta)`, and `A c~ in D_k c_{k-1}`, `A G~ in D_k G_{k-1}` by
inclusion isotonicity of the interval products. Z.2 and Z.3 are interval evaluations of the same expression. The
only overestimation is rounding (G entries stay thin to about 1e-38 relative per step).

**Variant Z-sym.** No centre: `rho_k,i = mag(S_k,i)`, `c = 0`. Keeps E symmetric and `0 in E`, the precondition stated
in SECOND_ORDER_STEP_DESIGN.md. Costs at most a factor 2 on the asymmetric part of S (P2 uses `rr(a,a) = [0,1]`).
My reading is that the mean-value split `M e = A e + (M - A) e` needs no `0 in E`, only `x(r), x(r)+e in K`; please
check whether S4/S9 or any driver consistency check uses `x in X`. Score both; they differ only in S handling.

**dDe.** The injection becomes `dD * hull(Z)`. Nothing tighter is available from ordering the product: for an
interval matrix dD that is wide relative to its midpoint, `sum_j mag((dD G)_ij)` equals `(mag(dD) * hull)_i`. The
gain is entirely that `hull(Z)` is the true box hull instead of the wrapped one, so the wrapping leaves the
feedback loop. If dDe still dominated after that (I expect P2 to dominate instead), the escalation is to carry the
cross term `D2phi(x)(C r, G xi)` as a bilinear coupling; not proposed now.

**Cost.** `64 N_k` interval multiply-adds per step, `N_k = 8(k+1)`. Window of 1100 steps: N up to 8.8e3, about 3e8
multiply-adds in total. Whole run of 2404 steps from t = 0: N up to 1.9e4, about 1.5e9 in total, memory of order
10 MB. These are counts, not timings: have the scorer time its own replay to convert.

**Offline scoring.**

- Mode Z0 (the run's injections as dumped): by construction `W_Z(u) = W_lin(u)`. This is a control, not a result.
- Mode Z1 (dDe feedback, bound without a re-dump). Let `e_{k-1} = B_{k-1} * re_{k-1}` (interval product, as the code
  forms it) and `h' = hull` of the replayed Z at k-1. Define
  `lambda_k = max_i max( max(hi(h'_i),0) / hi(e_{k-1,i}), max(-lo(h'_i),0) / (-lo(e_{k-1,i})) )`,
  and replay with `S'_k = P0_k + P1_k + P2_k + lambda_k * DDE_k`.
  Justification: `h'_i` is contained in `lambda_k e_{k-1,i}`, so `dD h'` is contained in `lambda_k (dD e_{k-1})`. It is an upper bound on
  the new dDe given the run's D1K, and the maximum over components makes it pessimistic. P2 and D1K are taken as dumped
  (they could only shrink, since the new K is contained in the old one).
- Mode Z2 (exact dDe): needs `D1K` (or `dD`) added to the dump, 64 intervals per step, and the segments re-run.
  Then `DDE'_k = (D1K_k - D_k) * h'`.
- Score Z1 on chain C+A first. Chain A's `G_0` is the box already wrapped by t = 290, so lambda stays near 1 there for a
  while and A understates the gain.

## 2. Candidate S: adjoint slabs beside the existing box (minimal change)

**Set.** `E` is contained in `(B re)` intersected with `{ e : w^(i) . e in a^(i), i = 1..M }`. The box and its update are exactly
today's. The slabs are a side-car: thin covectors `w_k^(i)` and intervals `a_k^(i)`.

**Templates.** One per check covector per future checkpoint: `w^(i)` at time t is `Phi(T_c, t)^T u_c^(i)`.
M = 7 x (checkpoints still ahead).

**Rules (offline, exact templates).**

- S.0: backward pass `w_n = u`, `w_{k-1} = mid(D_k)^T w_k` (what `wrap_adjoint.py` already does).
- S.1: `a_0 = (w_0^T B_0) . re_0`.
- S.2: `a_k = a_{k-1} + delta_k . hbox_{k-1} + w_k . S_k`, with `delta_k = D_k^T w_k - w_{k-1}` (interval, about 1e-30)
  and `hbox = B re` the run's box hull.
- S.3: at the checkpoint, `u . E` is contained in `(c a_n + eta . hbox_n)` intersected with (the box projection), with thin `c` and
  `eta = u - c w_n` (interval). Offline `c = 1`, `eta = 0`.

**Rules (production, forward).** Seeds `w_s^(i)` at a seed time `t_s` come from a non-rigorous pre-pass (the adjoint
along the centre orbit; any accuracy). `a_s = (w_s^T B_s) . re_s`. Each step: `w_k = mid( krawczykInverse(D_k)^T w_{k-1} )`
as a thin vector, then S.2 as written, then S.3 with `c = mid( (u . w_T) / (w_T . w_T) )`.

**Rigour.** For real `A in D_k`: `w_k . (A e + sigma) = w_{k-1} . e + (A^T w_k - w_{k-1}) . e + w_k . sigma`, and the
three terms lie in `a_{k-1}`, `delta_k . hbox_{k-1}`, `w_k . S_k`. This holds for ANY thin `w_k`; the choice only
affects tightness. S.3 is the same identity with `u = c w + eta`. A bad seed costs `mag(eta) . mag(hbox)` and is
visible in the output; it cannot make the bound wrong.

**Properties.**

- The run itself (x, C, H, B, re, t, step sizes, every dumped quantity) is byte-identical to today. Only
  `project()` at checkpoints gets an intersection. All existing identity regressions keep their meaning.
- Offline score: `width(a_n) = W_lin(u)` exactly, for every template. So S's numbers are already in
  `result_A.txt` / `result_CA.txt` (B17 with W_lin: PASS at 291.8852 on A and C+A). The scorer run is a control.
- Limitation: hull(E) is still the wrapped box, so dDe is unchanged and the box keeps growing. S makes the
  registered checkpoint pass but leaves the feedback loop in place; expect it to degrade at later checkpoints.
- Seeding from a box inherits that box's wrapping up to `t_s` (the "start E" term: 6.3e-8 of 9.76e-8 on A,
  3e-10 on C+A). Seed as early as the pre-pass accuracy allows; the cost of seed error is the `eta` term.

**Cost.** Per step: one 8x8 Krawczyk inverse, then M matrix-vector products and 2M dot products. Negligible.

## 3. Candidate ZR+S: bounded-order zonotope for the hull, slabs for the checks

For when N must stay bounded. The zonotope supplies `hull(E)` (so dDe and K are tight); the slabs of section 2,
with `hbox` replaced by the zonotope hull, supply the checkpoint projections, so reduction loss cannot reach the B17
covectors. Final projection = intersection of the two.

**Reduction rule ZR(N_max, N_keep),** applied after Z.1 whenever `N_k > N_max`:

1. `R` = the oldest `N_k - N_keep + 8` columns (the previously merged block sits at the front and is always in R).
2. In double: `U Sigma V^T = svd(mid(G_R))`; `Q = U` (8x8, completed to full rank if needed), stored thin.
3. `iQ = krawczykInverse(Q)`; `Y = iQ * G_R` (interval); `d_i = sum_{j in R} mag(Y_ij)`, rounded up.
4. Replace the columns of R by the 8 columns of `Q diag(d)` (interval products). The centre is untouched.

**Rigour.** For real selections, `sum_{j in R} g_j xi_j = Q sum_j (Q^-1 g_j) xi_j`, `Q^-1 in iQ`, and component i of
the inner sum lies in `[-d_i, d_i]`. So the old block is contained in `Q diag(d) [-1,1]^8`. Q is arbitrary.

**Why oldest-first with an SVD frame.** Old generators have been transported longest and have collapsed onto the
leading directions, so merging them loses least; the SVD frame is exact in its own 8 directions.

**Score** `(N_max, N_keep)` in {(64, 32), (256, 128), (1024, 512)}; report against Z in every covector and for
the hull (lambda as in Z1). Wrapping compounds on the front block once per reduction, so also report the number of
reductions.

## 4. Considered and not proposed

- **CAPD doubleton.** The set already is one: (x, C, H) in r plays the `C r0` role and `B re` with QR is the doubleton's
  error term. That term is what wraps.
- **CAPD tripleton.** As an idea (a second error parallelepiped) it is a member of the ZR family with N = 16 and a fixed
  reduction policy, so it should land between the box and Z. I did not read CAPD's C0TripletonSet source; its set
  classes drive CAPD's own C0/C1 `move`, while this step is hand-rolled on Cn jets, so only the idea transfers.
- **Berz-Makino shrink wrapping.** It absorbs the remainder into the linear coefficients of the polynomial, which
  needs an invertible n x n linear part. Here C is 8x2. Adding 8 or more parameters for E makes it Z with the
  bilinear coupling of section 1.
- **Pinned thin column.** See observation (b). S is the general form; a pinned column also changes the box and
  therefore the run.

## 5. Scorer controls and outputs

Controls (a failure means the scorer or my reading of the dump is wrong, not a result):

- C1: replaying today's rule (`qr_frame`, `krawczykInverse`, `ren = (iBn*AB)*re + iBn*s`) reproduces every dumped `B_k`, `re_k`.
- C2: Z in mode Z0 and S both reproduce W_lin for every covector and checkpoint in the result files.
- C3: in Z0, `hull(Z_k)` is contained in `B_k re_k` at every step (lambda_k <= 1). In Z1 the same.
- C4: every ZR width >= the Z width for the same injections.

Outputs per candidate, per checkpoint, per covector: `W_cand`, `W_cand/W_box`, `W_cand/W_lin`, and B17 re-evaluated
with `P + W_cand`. For Z1/ZR: lambda_k (min, median, max, and at the checkpoint), the injection split P2 vs DDE', `N_k`,
and replay wall time. For ZR: number of reductions.

My expectations, stated before any scoring so they can be wrong: Z0 = S = W_lin (identity). Z1 on C+A at 291.8852:
DDE' falls by roughly the hull ratio, P2 (about 1.3e-8 on u2) becomes the dominant injection, u2 ratio about 1.1.

## 6. Open points for the Bridge

1. Whether `0 in E` is a real precondition (Z versus Z-sym).
2. Whether to re-dump with D1K for exact Z2 scoring (a run; needs a slot if over 30 min).
3. How the slab seeds are produced in production, and the seed time.
4. Independent of the representation: taking `A = mid(D1K)` instead of `D1c` in the split `M e = A e + (M - A) e` is
   equally rigorous and replaces `mag(D1K - D1c)` by `rad(D1K)`, at most a factor 2 on dDe. Needs D1K to score.

## 7. After scoring (2026-11-18, Opus 5.5): ZR replaced by ZG; the C3 note

Scores: `so_mn/wrap_test/escore_{A,CA}.txt` (float64 replays of the dumps; estimates, not enclosures).

- **ZR as specified in section 3 fails.** Oldest-first merging into an SVD frame re-wraps the merged block at every
  reduction: (64,32) and (256,128) end wider than the run's own box, and (1024,512) fails B17 on chain A.
- **ZG(N_max, N_keep) replaces it.** When `N > N_max`, the `N - N_keep + 8` columns with the smallest
  `||g||_1 - ||g||_inf` (Girard's ordering) are replaced by one diagonal block `diag(d)`, `d_i = sum_j mag(G_ij)` over
  the merged columns, rounded up. Rigour: the merged sub-zonotope lies in its interval hull, which that block is.
  The large (stretched) generators are never touched, which is why it does not re-wrap.
  B17 at 291.8852 (u2 ratio / fake ratio):

  | mode | C+A | A |
  |---|---|---|
  | Z1 (unreduced) | 1.077 / 0.440 PASS | 1.388 / 0.609 PASS |
  | ZG(256,128) | 1.157 / 0.675 PASS | 1.429 / 0.728 PASS |
  | ZG(64,32) | 2.461 / 4.720 PASS | 1.990 / 2.715 PASS |
  | ZG(32,16) | 7.507 / 22.78 FAIL | 4.721 / 12.55 FAIL |
  | ZG(16,8) | FAIL | FAIL |

  C4 (every reduced width >= Z1) holds for all ZG and ZR modes.
- **C3 on the sym variants.** The only lambda above 1 is at k = 0 (1.0000013 on C+A, 1.0000015 on A): the symmetric
  start hull `B0 mag(re0)` is wider than the asymmetric start box by construction. From k = 1 the maximum is 0.9983
  (C+A) and 0.9992 (A). The scorer now judges C3 for the sym variants from k = 1 and prints the k = 0 value.
