# E representation: pre-registration of the implementation run

Status: REGISTERED. The Bridge AGREED as proposed on 2026-11-18 (1496a30 + 79fde97), and checked that K = 5 is mn_so.cpp's
existing B17 constant. The text below is unchanged from the proposal. Implementation and T1–T3 follow in later commits. Written by Claude Opus 5.5
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

## Amendment A1 (2026-11-18, Opus 5.5; before any T3 run, and before any zsym/zg MN width was produced)

**What it fixes.** T3 as registered ("the first 200 steps from t = 0 under `box` and `zsym`") breaks the registration's own
"< 30 min, no slot" condition. The box run's early steps cost ~17 s each (kr_ref.out: step 20 at 344 s, step 33 at
581 s), so 200 steps take about an hour per mode.

**Replacement.** T3 becomes T3a + T3b, still timing-only. The fallback rule is unchanged: ZG(256,128) if the projected
Z-sym wall exceeds 2x the box run's.

- **T3a.** The first 40 steps from t = 0 at W0 = 1e-7 under `box` and `zsym`, run in parallel at nice 10 (~12 min).
  It measures the per-step wall of each mode at small N and checks that zsym runs the real MN step end to end.
- **T3b.** `tests/erep_bench` times the zonotope operations alone on 8-D MPFR-128 data, at N = 1000, 4000, 10000 and
  20000. The 2404-step run reaches N ~ 1.9e4. One benchmark "step" counts the propagation, the injection, three hulls
  and seven projections (the projections are an upper bound: the run projects only at checkpoints).
- **Projection.** Z-sym wall over steps 1..2404 = box wall over the same steps + sum_k bench(N_k), with N_k = 8 + 8k
  (an upper bound: zero injected columns are skipped).
  - The box wall is the original W0 = 1e-7 run's wall over those steps, from its logs (fix_test, the run the wrap test
    reproduced).
  - Any S4 speed-up from a narrower hull is not counted, so the projection errs high.

## Amendment A2 (2026-11-19, Opus 5.5, session "Quantum"): a second registered run, Z-sym with SO_FIXED_REDO=1

Status: REGISTERED. The Bridge AGREED as proposed on 2026-11-19 (7e28f7d). The text below is unchanged from the proposal.
It was committed before any A2 test or run.
The Bridge's condition: launch only after the main run's registered outcome is recorded AND T1r/T4r pass. The reading
must carry the caveat that the fix test had REDO on only from t 287.756.
Sumit decided, relayed by the Bridge on 2026-11-19: YES to this run.
Order: (1) the main run above reaches its registered outcome and is recorded as registered; (2) SO_FIXED_REDO_AMENDMENT.md is
registered; (3) this A2. Nothing in A2 changes the main run's reading.

**Why.** The setup-correspondence line in §3 is wrong. The wrap-test runs, and the fix test the design was scored on,
ran with SO_FIXED_REDO=1 (wrap_run.py sets it), not OFF. With REDO OFF, the box method blows up through the swing
(so_mn/run_1e-7.out THREW at step 1465, t 289.05). At step 1400 the main run's maxE (8.86e-6) tracks that REDO-off box
run (1.29e-5), not the REDO-on box run (8.86e-10). This was noticed at 07:46 on 2026-11-19, while the main run was
still running, before any checkpoint after 283.885 had been reached.

**The run ("main_redo").** Identical to §3, except:
- the environment adds `SO_FIXED_REDO=1`;
- the outputs go to `horseshoe_results/so_mn/erep/main_redo/`.
Everything else is unchanged and stated in its launch.txt:
- the binary `tests/mn_so_erep`, with its sha256 recorded and the same binary as the main run;
- `SO_EREP=zsym`; W0 1/10000000; `mn_smoke/b17_cp_1e-7.txt`; from t = 0 to 291.9; `SAVE_FROM=287.5 SAVE_DT=0.25`;
  CKPT_SEC default.

**Corrected setup correspondence.** The claim is "B17 passes at t = 291.8852 for the MN W0 = 1e-7 piece". The run is at
that condition:
- the same piece and checkpoints;
- the same field, Taylor order 20, MPFR 128 and step control;
- SO_FIXED_REDO=1, as in the wrap-test and fix-test runs.
One difference from the fix test is stated plainly. The fix test ran the box with REDO ON only from t 287.756 (step 1304),
having resumed from the grid save of the REDO-OFF DIAG rerun. main_redo runs REDO ON from t = 0. Apart from that, only
`SO_EREP` differs.

**Pass criteria, reading and controls.** §5 and §6 unchanged: the primary is B17 at 291.8852 with u1, u2 and fake ratio each
<= K = 5; the secondary, C-floor, C-identity and C-steps are as written. Two additions, both pre-run tests (< 30 min each,
no slot), run and committed before the launch:
- **T1r, the REDO identity.** `mn_so_erep` with `SO_EREP=box SO_FIXED_REDO=1` replays wrap-test segment C01 (from
  `fix_test/fix_1e-7.state.t287.7668`, stop after 288.0, the wrap_run.py environment). Its grid save must be
  byte-identical to `fix_test/fix_1e-7.state.t288.0099`, the file C01 was checked against in the wrap test (segments.tsv). This shows the E-rep binary reproduces the REDO-on box
  path that the claim's comparison runs used.
- **T4r, resume on the REDO path.** As T4 (stop after t 0.02, resume, stop after t 0.04, compare with an uninterrupted
  run) with `SO_EREP=zsym SO_FIXED_REDO=1`. It must be byte-identical.
If T1r or T4r fails, nothing is launched, and the failure goes to the Bridge.

**Slot (the Bridge, 2026-11-19):** 1 core, nice 10, < 300 MB, ~1.5 days. The guard is the same as the main run's
(erep_guard.py): (swap > 2 GB AND level >= 2) or level >= 4, sustained 600 s; disk < 5 GB or the run's own footprint
> 300 MB stop it at once; verified-PID stops only; no automatic restart.
- It launches only after the main run has ended (one core).
- Estimate: the main run took ~15 h to step 1400. REDO adds two fixed-step Cn calls per step. The REDO-on box run took
  ~17 h from t 287.77 to 291.88. So ~35–45 h; reported at launch.

**Reporting.** A progress line to the Bridge about every 12 h, and at once on a guard stop, a BUG or a THREW.

## Amendment A3 (2026-11-21, Opus 5.5, session "Quantum"): main_cont, the continuation of main_redo to sec_return

- **Status: REGISTERED.** The Bridge AGREED as drafted (68b94bc) on 2026-11-21, before any main_cont output existed
  (launch kit a2d2bda, not launched). The text below is unchanged from the proposal.
- **The Bridge's plan (2026-11-21):** GO for one registered continuous run, R1–R4, starting when the Melnikov counted run
  ends. Read and report at every checkpoint as it lands. Time is not a constraint (Sumit's words).
- Nothing in A3 changes main_redo's registered reading (PASS, 7d56c34).

**The run ("main_cont").**
- **Start state.** A byte copy of main_redo's final state `main_redo/st` (t = 291.9, next checkpoint index 3 = t 295.8852),
  sha256 a41157473d07370e…. It goes to `horseshoe_results/so_mn/erep/main_cont/st`. main_redo's own files are not touched.
- **Resume.** As tested in T4r (byte-identical resume on the zsym + REDO path). The first line of run.out must read
  `# RESUMED … next checkpoint 3`; anything else is a harness error.
- **Binary.** `tests/mn_so_erep`, sha256 4a48b59ae87427ed…, the same binary as main and main_redo.
- **Environment.** `SO_EREP=zsym SO_FIXED_REDO=1`, CKPT_SEC default (1800), W0 1/10000000, `mn_smoke/b17_cp_1e-7.txt`,
  T_end 1018.7.
- **Grid saves.** `SAVE_FROM=292 SAVE_DT=20`. This is a disk choice: the states grow to about 30 MB, and main_redo's
  SAVE_DT 0.25 over ~727 time units would need about 70 GB.
- **Settings.** nice 10, 1 core, detached (tools/detach.sh).
- **Stages, all in this one run:**
  - R1: t 295.8852.
  - R2: sec_down 581.77.
  - R3: t 793.2346, 800.0941, 801.2346, 805.2346.
  - R4: sec_return 1018.6988.
- **Estimate.** About 3400 steps, about 62 h ± 20% at main_redo's measured cost.

**Section checkpoints are NOT measured by this run.**
- mn_so prints "sections SKIPPED". At sec_down and sec_return it saves the set at t_sec − 0.5 (`st.pre_sec_down`,
  `st.pre_sec_return`) and continues.
- Those sets are recorded with sha256 and nothing else. Measuring them on the section needs a tool that does not exist
  yet (a separate design, registered later).
- A3's criteria are therefore the five time checkpoints only.

**Criteria, reading and controls.**
- §5 and §6 are unchanged, applied at each time checkpoint.
  - B17: u1, u2 and the fake ratio each ≤ K = 5.
  - Each checkpoint is read and reported to the Bridge as it lands.
- C-floor: `tests/b17_containment.py` against `so_mn/contain/ref_1e-7_{mm,mp,pm,pp,zm,zp,mz,pz}.out`. These reference runs
  already contain PROJ lines at all five time checkpoints, so no new reference runs are needed.
- C-identity (the same binary hash) and C-steps (no BUG; resteps reported) are as written.
- §6 table: a FAIL at a checkpoint does not stop the run.
- **Overall reading:**
  - PASS if all five time checkpoints pass, with no THREW and the controls holding;
  - FAIL if the controls hold but a checkpoint fails or is not reached (THREW);
  - INVALID if a control fails.
- Each checkpoint's own line is also recorded (PASS or FAIL per checkpoint), so a partial outcome (for example R1 PASS
  and R3 FAIL) is visible and not merged.

**Stop conditions (the Bridge, 2026-11-21).** Each stop is by verified PID only. Each is reported at once, and there is
no automatic restart.
1. **A harness error.** Any `HARNESS-ERROR` line, or a missing or wrong RESUMED line.
2. **A guard stop.** erep_guard.py, as in A2: (swap > 2 GB AND level ≥ 2) or level ≥ 4, sustained 600 s; disk < 5 GB at
   once; own footprint > 500 MB at once (the A2 cap as replaced on 2026-11-19).
3. **Per-step cost drift above 2×.**
   - Baseline ("flat"): main_redo's mean of 63.9 s/step (154323 s / 2414 steps). Its 200-step windows ranged 57.9–70.1 s.
   - The cost watchdog reads the `# step` lines (every 20 steps). If the mean wall time over the latest 200-step window
     exceeds 2 × 63.9 = 127.9 s/step, it stops the run and logs COST-STOP.
   - **Early check:** after about 30 min (≥ 20 steps), the mean so far is reported to the Bridge. N is 19k at the start
     and grows by 8 columns per step to about 46k. Flat cost up to 19k is measured; beyond that it is not yet known.

**Registered caveat, carried over from A2.** The fix test had REDO on only from t 287.756. main_redo, and so main_cont, ran
with REDO on from t = 0.

**Monitoring.** A watcher that polls the PID and greps run.out every 10 min (never tail -F, after the 2026-11-21 hang).
Reports go to the Bridge:
- each checkpoint as it lands;
- the 30-min cost check;
- any stop;
- a progress line about every 12 h.
