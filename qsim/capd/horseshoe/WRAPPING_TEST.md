# Wrapping test: is the post-periapsis u2 leak genuine, or wrapping of E's box?

Written and committed 2026-11-17, BEFORE any segment ran. The reading in §4 is fixed now. If any part of it has to be
clarified after a stop, the clarification is committed before resuming, as in the 27.2 regression.

## 1. The question (the Bridge, 27 Oct)

In the fix test (fix_test/FULL_RESULT.txt), B17 at W0 = 1e-7:
- passes at t 290.8497 (u2 ratio 1.50);
- fails at t 291.8852 (u2 2.488e-6 against a true thin width of 1.963e-7, ratio 12.67; the fake check 3.71e-5 against
  4.76e-6, also a fail).

The error part E dominates: maxE is ~2.1e-6 there. E is held as one box re in a Lohner frame B (E ⊂ B·re), and it is
re-boxed in a new QR frame every step. Through a strongly shearing swing, a box's projection on the THIN direction can
grow by wrapping even when the true error set stays nearly one-dimensional along the stretching. Two readings:
- **Wrapping:** the fix is a better representation of E (a doubleton/tripleton for E, Berz–Makino shrink-wrapping, or
  a frame with the thin direction pinned). It is an implementation change, with the same claim.
- **Genuine:** the error set really is that wide in u2; the fix is subdivision (~400 pieces per piece at this
  checkpoint) or less injection.

## 2. Method

**What it replays.** The fix-test run is replayed EXACTLY from its own grid saves. mn_so.cpp and so_set.h gain two
log-only options (built as tests/mn_so_wrap, guarded build):
- **WRAP_DUMP:** after every step, write out the run's centre variational matrix D1c (the Lohner map of the error part)
  and the boxes the step injects into the error part. The total s is split into p0, p1, p2 and dDe = ([Dφ(K)] − D1c)·e,
  in the old coordinates. Also the new B and re, and, at each B17 checkpoint, every checkpoint covector (u1, u2, nH and
  the 4 off-manifold covectors) with the run's own projection on it. All as MPFR hex.
- **STOP_AFTER_T:** stop after the first step that ends at or past t. Unlike T_end, it does not change the solver's
  maximum step, so the steps are the original ones.

**Segments.** The windows are cut at the original grid saves, so 3 cores can work in parallel (segments.tsv):
- **Chain A:** W0 = 1e-7, t 290.0013 → 291.8852, 8 segments. Checkpoints 290.8497 and 291.8852. **Primary.**
- **Chain B:** W0 = 1e-6, t 290.0007 → 291.0014, 4 segments. Checkpoint 290.8497.
- **Chain C:** W0 = 1e-7, t 287.7668 → 290.0013, 9 segments. Run as C then A, this is the long window through the
  swing.

**Analysis** (wrap_adjoint.py, post-processing only). For a checkpoint at T and a covector u:
- **W_box** = Σ_j |⟨u, B_T e_j⟩| w(re_T,j). This is the error part of the run's own projection.
- **P** = W_tot − W_box. This is the polynomial part plus the centre; it does not depend on how E is held.
- **W_lin** is the u-width of the wrapping-free linear image of the same error sources over the window.
  - Recursion: e_k = D_k e_{k−1} + s_k, with D_k = mid(D1c_k).
  - Start: e_0 = B_0·re_0, the start state's parallelepiped, carried exactly.
  - Computed by the adjoint: w_T = u, w_{k−1} = D_kᵀ w_k, and
    W_lin = Σ_k Σ_i |w_k,i| w(s_k,i) + Σ_j |⟨w_0, B_0 e_j⟩| w(re_0,j).
  - W_lin is what an unreduced zonotope would hold for the run's own injections.
- **F** = W_box / W_lin, the wrapping factor.
- **The B17 check re-evaluated** with P + W_lin in place of W_tot for every covector (u1, u2, and fake from nH and
  off0–3), against the same thresholds (K = 5).
- **Logged:** the per-column box table at T, and W_lin split into the start parallelepiped and the injections, by part
  and by 0.25 time bin.

## 3. Controls (any failure means HARNESS-ERROR and no reading)

1. **K00 / K01:** mn_so_wrap's kr_ref (t 0 → 0.9, W0 1e-6), with the dump OFF and ON, must be byte-identical to
   so_mn/kr_ref. The hook must not change the computation.
2. **Every segment** (wrap_check.py) must meet all of these:
   - its own grid save is byte-identical to the original grid save it ends at (C09 also checks the immediate save
     .t289.7555);
   - every DIAG line equals the original's for that step (the eratio field is ignored);
   - every PROJ and CHECKPOINT line occurs verbatim in the original log;
   - it ends by STOP_AFTER_T, with no THREW or GUARD;
   - its dump is complete and consecutive.

   The first non-IDENTICAL result stops all further launches.
3. **The chain must join exactly:** the dump's last B, re and step equal the next segment's start state.
4. **F ≥ 1** (to within 1e-6) for every covector at every checkpoint. The box contains the mid-linear image of its own
   injections, so F < 1 means the harness is wrong.

## 4. Pre-registered reading

The primary quantity is **F at t 291.8852, covector u2, chain A**. "B17 with W_lin" means u1, u2 and fake, all with
P + W_lin, each ≤ K = 5.

| Outcome | Condition | Meaning / next step |
|---|---|---|
| **WRAPPING** | F ≥ 10, AND B17 with W_lin PASSES at 291.8852 | The leak is a representation artefact. Next: a better E representation (doubleton/tripleton, shrink-wrap or a pinned thin column), designed and registered with the Bridge, BEFORE any subdivision. |
| **GENUINE** | F ≤ 2 | The linear image of the run's own error sources really is that wide in u2. Next: subdivision (or less injection); the subdivision design proceeds. |
| **MIXED** | anything else: 2 < F < 10, or F ≥ 10 with B17 with W_lin failing | Wrapping contributes, but a better representation alone does not pass 291.885 at W0 = 1e-7. The numbers (F, the W_lin split, the per-column table) go to the Bridge, and the next step is decided together; nothing is launched on this reading alone. |

**Secondary, informational only (no verdict):**
- chain C+A: F at 291.8852 over the long window, which includes the wrapping accumulated before t 290 (chain A's start
  parallelepiped may itself carry it, so chain A's F is a LOWER estimate of the full effect);
- chain A at 290.8497;
- chain B (W0 1e-6) at 290.8497, for the W0 dependence of F.

**Caveats, stated now:**
- W_lin is a linearised estimate:
  - it uses mid(D1c); the widths of D1c are logged;
  - it takes the run's injected boxes as given, so pessimism in the injections themselves is not addressed;
  - it is a bound on what a wrapping-free representation could achieve with these injections, not a rigorous enclosure
    of anything new.

  A real doubleton or shrink-wrap implementation lands between W_box and W_lin. A WRAPPING reading licenses designing
  one, not a claim.
- The dDe injection is computed from the run's own (wrapped) e, so W_lin is slightly pessimistic.

## 5. Resources (the Bridge's slot, 2026-11-17 overnight)

- **Load:** 3 cores at nice 10, ~0.2 GB each (measured: 190 MB peak), dumps ~11 KB per step, ~15 MB in all.
  ~1100 + ~200 steps at ~70–90 s each, so ~30 core-hours, ~10 h wall on 3 cores. Chain A first, so the primary reading
  arrives after ~5–6 h.
- **Launch:** fully detached (tools/detach.sh).
- **Guards:** stop at < 5 GB free disk; no new launches while memory pressure is not normal or swap used > 2 GB, and a
  stop if that lasts 10 min.
- **Restarts:** resumable at segment boundaries (re-launch the runner after checking that no mn_so_wrap is running).
