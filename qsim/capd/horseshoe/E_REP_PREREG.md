# E representation: pre-registration of the implementation run

Status: PROPOSED to the Bridge, 2026-11-18. Nothing below has been implemented or run. Written by Claude Opus 5.5
(Quantum-personal session). It builds on E_REPRESENTATION_DESIGN.md, whose sections 0-6 are by Fable 5.2 and are treated as
outside-reviewer input. No subdivision and no implementation run happen before the Bridge agrees to this text.

## 1. What is registered

**Primary: Z-sym.** The error set E in `so::Set` becomes a centred zonotope with no centre:
`E = { G xi : xi in [-1,1]^N }`, with G an interval 8xN matrix in 128-bit MPFR. `B` and `re` are removed when the flag is on.

- Start: `G_0 = diag(mag(re_0))`, where re_0 is today's initial error box (B_0 = I).
- Step: `G_{k+1} = [ D1c G_k | diag(mag(s_k)) ]`, where s_k is today's injected box `p0 + p1 + p2 + dDe`.
- `hull(E)_i = [-1,1] * sum_j mag(G_ij)`. It is used in `K = X.hull()` and as `e` in `dDe = (D1K - D1c) * e`.
- `project(u)` error part: `[-1,1] * sum_j mag(u . G[:,j])`.
- Everything else in `step()` is unchanged: the thin and hull Cn calls, the polynomial part, step control,
  `SO_FIXED_REDO` OFF, and the S4/S9 checks.
- Flag: `SO_EREP` (`box` = today's code path, the default; `zsym`; `zg`).

**Bounded fallback: ZG(256,128).** Same as Z-sym, plus this reduction. When `N > 256`, take the `N - 128 + 8` columns
with the smallest `sum_i mag(G_ij) - max_i mag(G_ij)` and replace them by `diag(d)`, `d_i = sum_j mag(G_ij)` over
those columns, rounded up. The fallback is used ONLY if the timing test (section 4, T3) projects the Z-sym run above
2x the wall time of the box run over the same steps. That choice is made from timing alone, before any width is seen.

**Not in scope:** the adjoint slabs (S); the A = mid(D1K) split; a D1K re-dump (Z2 scoring); subdivision; W0 = 1e-6.
The float scorer already shows that W0 = 1e-6 fails even with the wrapping-free bound.

## 2. Rigour (why each update encloses)

- **Step.** For any real `A in D1c`, `sigma in s_k` and `e = G~ xi` (any real selection of G_k), write
  `sigma = diag(rho~) zeta` with `|zeta| <= 1` and `rho~ <= mag(s_k)`. Then
  `A e + sigma = [A G~ | diag(rho~)](xi, zeta)`, and `A G~` lies in `D1c G_k` by inclusion isotonicity.
  So the new set contains the true image. Together with the unchanged mean-value split, this gives
  `phi(x(r) + e) - phi(x(r)) - D1c e in (D1K - D1c) e`.
- **0 in E (Fable's open point 1: it is a GATE, and Z-sym meets it).** The mean-value step needs the segment from
  x(r) to x(r) + e inside K = hull(X_n) (SECOND_ORDER_STEP_DESIGN.md, review point (a)). x(r) lies in X_n only if
  0 is in E_n. Z-sym is centred, so 0 is in E by construction. Fable's section 1 remark ("no 0 in E needed") was wrong
  on this point, and the centred variant Z1 is dropped for this reason. Offline, Z1sym = Z1 to 4 digits at both
  checkpoints on both chains (escore_{A,CA}.txt).
- **ZG.** The merged columns' sub-zonotope lies in its interval hull, which is exactly `diag(d)`.
- **Hull and projection** are interval evaluations of the same sums, rounded outward.

## 3. The run

- W0 = 1e-7. From t = 0 (the K00 start), single process, through the checkpoint at t = 291.8852393126.
  Starting at t = 0 matters: any mid-run start inherits the wrapped box (chain A's "start E").
- Detached (tools/detach.sh), nice >= 10, checkpointed every segment (same cut times as the wrap test), with a guard
  on disk, swap and pressure.
- Slot: requested separately after the timing test T3, with a measured estimate. The box run's wrap-test segments
  took about 25 core-hours in total for chains A, B and C plus K00/K01. One Z-sym run should be of the same order;
  S4 cost may fall, because S4 bisects more when the hull is wide.

**Setup correspondence.** The claim to be tested is "B17 passes at t = 291.8852 for the MN W0 = 1e-7 piece". The run
is at that condition:
- the same piece and checkpoints: `mn_smoke/b17_cp_1e-7.txt`, W0 = 1/10000000;
- the same field, Taylor order 20, MPFR 128 and step control as the wrap-test runs, with SO_FIXED_REDO OFF;
- the same B17 rule (mn_so.cpp L235).

Only `SO_EREP` differs. The float scores in E_REPRESENTATION_DESIGN.md are a different quantity (estimates from the
box run's dumps, started mid-run) and are not the claim.

## 4. Pre-run tests (each < 30 min, no slot)

- **T1 Identity.** With `SO_EREP=box` the new binary reproduces K00/K01 byte-identically (the wrap-test control).
- **T2 Toys.** `tests/toys_so.cpp` (Toys A, B, C, E of SECOND_ORDER_STEP_DESIGN.md §7, with their negative controls),
  rebuilt under `zsym` and `zg`. Every enclosure must contain the toys' exact images, and every negative control must
  still FAIL containment.
- **T3 Timing.** The first 200 steps from t = 0 under `box` and `zsym`. The per-step cost is fitted against N to
  project the full run.

## 5. Pass criteria, judged on the REAL enclosure (not the float estimates)

**Primary (at t = 291.8852):** B17 with the run's own `X.project()`: u1, u2 and fake ratio each <= K = 5, as defined in
mn_so.cpp L235.

**Secondary:** the same at t = 290.8497, and every per-step S4/S9 check passes through 291.8852.

**Controls.** If any fails, the verdict is INVALID, not FAIL:

- **C-floor (a width the design must not beat).** `tests/b17_containment.py <run>.out
  so_mn/contain/ref_1e-7_{mm,mp,pm,pp,zm,zp,mz,pz}.out`. The run's PROJ intervals must contain the 8 rigorous
  reference point runs' projections (4 corners and 4 edge midpoints of the W0 box, CAPD 128-bit) at every checkpoint
  and on u1, u2 and nH. Also `W_tot >= tu` on u1 and u2. A narrower enclosure is a bug. The refs exist and are reused;
  no new reference runs are needed.
- **C-reduce (only if ZG is used).** On a 200-step window from t = 0, ZG's projection widths are >= Z-sym's for every
  covector (the real-arithmetic C4).
- **C-identity.** T1 passes on the binary used for the run.
- **C-steps.** No step throws a BUG. The resteps count is reported.

**Diagnostic, not a criterion:** the ratio of the run's u2 error width to the float scorer's Z1sym estimate. These
are different runs from t = 0, so only order-of-magnitude agreement is expected. A ratio above 10 is investigated
before the reading is written.

## 6. Reading

| Outcome | Condition | Next |
|---|---|---|
| PASS | primary met, all controls hold | Z-sym is adopted for MN W0 = 1e-7; subdivision at 291.8852 is not needed; the next checkpoints are planned with the Bridge |
| FAIL | controls hold, primary not met | the numbers go to the Bridge (u2 split into polynomial / E part, injection split P2 vs dDe); the subdivision design resumes |
| INVALID | any control fails | bug hunt; no reading |

Nothing is launched on a FAIL or INVALID reading alone.
