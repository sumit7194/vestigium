# CAPD third replay of the Morales–Ramis certificates (Arb-free)

Registered 2026-10-11, before any registered run. The design was reviewed by the bridge, and its four points were
adopted.

## Why

- **The existing certificates already have two implementations:**
  - **v2:** Rust/Arb, non-reduced form, GL(2) certificate.
  - **v1:** python-flint/Arb, reduced form, SL(2) certificate.
  - The Lean kernel re-checks the certificate *arithmetic*.
- **What v1 and v2 share:** the Arb library (FLINT/Arb 3.6.0, two builds), the field derivation (this repo's sympy
  code) and the loop discretisation.
- **This replay removes all three common modes:**
  - the engine is CAPD 2f06098 (C++ autodiff Taylor/Lohner), with no Arb anywhere on the CAPD side;
  - the arithmetic is MPFR 4.2.2 intervals, validated in DIFFCHECK.md and guarded per NAN_SAFEGUARD.md;
  - the fields are **the bridge's independent derivation**;
  - a homotopic secondary loop covers the discretisation.

## Remaining common modes (stated precisely)

- **Metric component files:** the bridge's derivation starts from the SAME metric component files this repo uses.
  TS row 0's export, for example, names `ts2_metric_components_t1o2.txt`. So "independent derivation" means
  independent from the metric components onward: the NVE, the t-chart and the reduction to p, q. The metric files
  themselves are a shared input. They are checked separately (the parse-integrity check and the sealed files).
- **Loops:** the primary loop geometry is shared by construction, because the point is a direct trace comparison.
  The secondary loops remove that.
- **To be confirmed with the bridge:** which source the MN (V9) derivation starts from.

## Fields: bridge-derived, gated exactly

- **Source:** the TS rows come from TheBridge `falsification/V8_ts2_obstruction_check/export_capd/`
  (export b2bdb79; exporter da94f2c, `v8_hp.rational_parts`). MN rows (V9) will follow.
- **Gate, run before any transport (`replay_gate.py`):**
  - the bridge's p and q must equal this repo's as rational functions, by the **exact** polynomial identity
    P_b·Q_m − P_m·Q_b ≡ 0;
  - row parameters and variable must match;
  - no exp factors for TS.
- **TS result: all 14 rows PASS** (`replay_gate_ts.json`).
- The CAPD vector field is generated from the **bridge's** coefficients.

## Engine (identical for every row)

- **Generation:** `mr_replay.py` turns the exact rationals into a C++ autodiff functor (`tests/gen/*.h`).
  - Coefficients are exact prec-bit dyadic enclosures, computed with Python integers.
  - The generic `tests/replay_driver.cpp` is built under the proof guard.
- **Solver:** prec 256, Taylor order 30, `MpIOdeSolver` + `MpITimeMap` + `MpC0Rect2Set`. The watchdog is set to 6 h.
- **System:** Y′ = [[0,1],[−q,−p]]·Y as an 8-real fundamental matrix with Φ(start of segment) = I.
  - exp factors E_k = exp(w_k) become extra state, E_k′ = w_k′·E_k (so the field is rational).
  - E_k at each vertex is enclosed independently, with MPFR exp and checked_cos/sin.
  - The transported E must overlap it (fail closed otherwise).
- **Path (PRIMARY):** the certificate's own loops, `ia_hub.loop_points(base, centre, radius, ngon=16)`.
  - These are exactly the float vertices v1 and v2 transported. Floats are exact dyadics, so the path is
    *identical*.
  - Each segment is t = a + (b − a)s for s ∈ [0, 1]. Segment matrices compose with later segments on the left.
- **Words and certificate:** words exactly as recorded ("a*b" = M_a·M_b, the same convention as v1/v2). The
  certificate is v2's GL(2) form:
  - w = tr²/det certainly ∉ [0, 4] for g and for h;
  - tr[g, h] certainly ≠ 2;
  - every decision goes through the `capd_proof::certainly_*` helpers (finite endpoints, fail closed).

## Verdicts per row

- **REPLAYED:** all three conditions hold.
- **NOT_REPLAYED:** a condition is undecided because the enclosures are too wide. One registered escalation is
  allowed: re-run that row at order 40 and prec 512. The settings are reported with every result.
- **FAILED-CLOSED:** an exception (non-finite value, E mismatch, singular step, watchdog). Reported verbatim.
- **Cross-engine consistency (must hold):** for tr g, tr h and tr[g, h], CAPD's interval and v2's recorded ball are
  rigorous enclosures of the same number, so they must **overlap**. A non-overlap is a **FAILURE** and must be
  traced before anything is claimed. v1's recorded values are compared the same way where v1 computed the same
  quantity.

## Secondary: an independent homotopic loop

The bridge's point 1: at least one certificate per spacetime is replayed on a **homotopic** loop. That checks that
no discretisation artefact is shared by all three engines.

- **The loop:**
  - 24-gon instead of 16-gon;
  - radius 0.8× the recorded one;
  - same base point and same approach ray.
- **Why it is homotopic:**
  - The recorded radius is 0.3 × (the distance to the nearest other located singular point).
  - So the disk of the recorded radius holds only the centre's singular point.
  - Both polygons and the connecting stretch of the approach ray lie inside that disk, and both polygons enclose the
    centre (the 16-gon's inradius is 0.98r > 0.8r).
  - This uses the located singular points, and the bridge's exported root lists are used to confirm it.
- **Requirement:**
  - every loop matrix entry overlaps the primary's;
  - the certificate verdict is again REPLAYED.
- **Rows:** TS row 0 (P1) and C1 (Dubeibe's far-field level, P2); MN equatorial row 0 once its fields arrive.

## Control through the same pipeline (registered here)

- **M6:** the Euler equation of ODE_CONTROLS.md M1 (p = (11/12)/t, q = (−1/12)/t²) is fed through **this
  generator and driver**.
  - Loop: a lasso based at 3, around centre 0, radius 1, 16-gon.
  - Exact values: tr = e^{2πi/3} + e^{−iπ/2} and det = e^{iπ/6}.
  - The pipeline's enclosures must contain them.
- **Wrong-equation control:** p perturbed by 10⁻²⁰. Its trace must certainly exclude the true one.

## Priority (bridge point 4)

1. TS rows: 0–5 (the plunging levels) and C1–C8 (the bound levels, including Dubeibe's).
2. MN equatorial row 0.
3. The rest as time allows.

## Engineering disclosure

Before the bridge's export existed, `mr_replay.py dev-mine ts2 0` ran the pipeline on TS row 0 with **this repo's
own** fields. Its purpose was to debug the generator and driver. Its output will be reported as dev, never as the
replay. The registered runs use the bridge's fields only.

## Amendment A1 (2026-10-11, before any registered row run): step tolerance

- **The change:** set CAPD's absolute and relative step tolerance to **10⁻⁴⁰** (`TOL` in the driver input).
- **Why:**
  - CAPD's default tolerance is 10^(−digits−3), about 10⁻⁸⁰ at 256 bits.
  - At order 30 that forces steps of about 0.003 × the radius of analyticity, so the M6 control took about 2 min
    per segment.
  - The tolerance only chooses step sizes. Every enclosure stays rigorous whatever its value.
  - The certificate margins are O(1), so widths of about 10⁻³⁰ are ample.
- **Unchanged:** precision (256) and order (30).
- **History:** M6 had been started with the default tolerance. It was stopped (by PID, mine) after 2 of 18
  segments, before producing any result, and it is re-run with A1, like every row.

## Amendment A2 (2026-10-11): watchdog 6 h → 24 h (resource only, still fail-closed)

- **Trigger:** the first registered run of tschaos row 0 (C1, Dubeibe's level) was stopped by its own 6 h watchdog:
  FAILED-CLOSED, rc 124, after 35 of 54 segments.
- **Why:** the C1 loops are based far out (base ≈ 4.76 + 4.94i). Their approach segments are about 6 long and pass
  0.087 from a singular point, so each one takes about 150 CAPD steps.
- **What A2 changes:** only the wall-clock limit. Engine, settings, fields and loops are unchanged. That attempt is
  recorded as FAILED-CLOSED, and C1 is re-run under A2.
- **The C2 run:** it had started under the 6 h driver one minute earlier. It was stopped (by PID, mine) before
  producing anything, and is re-run under A2.
- **The other rows:** ts2 row 0 (REPLAYED, 4.3 h) needs no re-run. ts2 row 1 was already running under the 6 h
  limit; if it trips, it is re-run under A2.

## Amendment A3 (2026-10-12): per-segment checkpointing (resource only)

- **What it does:**
  - Each finished segment matrix is appended, as exact hex enclosures, to `<tag>.<sha256(input)[:16]>.ckpt`.
  - On restart, those segments are reloaded rather than recomputed. Because the file is keyed by the exact input, a
    resume can only reuse identical work. A torn last line is ignored.
- **Why:** so rows can be interrupted (e.g. to free cores) without losing their progress.
- **Validation on the M6 control:**
  1. An uninterrupted run without a checkpoint.
  2. A checkpointed run, killed after 6 segments.
  3. A resumed run, which reloaded those 6 and computed the rest.
  - **The resumed output is byte-identical to the uninterrupted one** (`replay_results/ckpt_validation/`).
- **Scope:** it applies to rows compiled after this commit. The three rows already running (TS 4, C2, MN eq 0) keep
  the old in-memory driver; renice is safe for them, kill is not.

## Amendment A4 (2026-10-12, before any MN result): settings and codegen for the MN rows only

- **Trigger:** MN eq row 0 under the TS settings had not finished its first approach segment (about 100 steps) after
  7.5 h, so a full row (about 1,100 steps) was heading for roughly 80 h.
- **Why it is that slow:**
  - The generated MN field had 1,146 complex multiplications, against TS's 96. The per-E-group Horner scheme
    recomputed powers of t 44 times.
  - It carried 14 state dimensions, against TS's 8.
  - E₃ appears in no monomial of p or q.
- **The A4 settings, for the MN rows only:**
  - **(a) Codegen 2.** Powers of t are computed once and shared, real coefficients are applied as scalar products, and
    E-monomials are shared. It is the same polynomial with fewer operations: 123 complex multiplications plus 731
    scalar products.
  - **(b) Pruning.** E factors that appear in no monomial are dropped (E₃ for MN eq, so 12 dimensions).
  - **(c)** prec 128 and step tolerance 1e−25, at order 30. The certificate margins are O(1), so widths of about
    1e−20 are ample.
  - **(d)** Per-loop parallel layout (3 processes) with A3 checkpointing.
- **Unchanged:**
  - The fields, loops, words, certificate and every cross-engine consistency check, including entry-wise overlap with
    v2's exact G/H boxes. That overlap check would expose any codegen error as a FAILURE.
  - The TS rows keep codegen 1 at 256 bits. Their headers were verified byte-identical after the codegen change.
- **Escalation for MN:** order 40 at prec 256 with tol 1e−40.
- **Validation (`replay_results/control_m6_A4.json`):** M6 run through codegen 2 at prec 128 / tol 1e−25. The exact
  trace and det are contained (widths about 7e−22), and the wrong-p control certainly excludes the true trace.
  - The first attempt failed closed on the driver's exact-input check: a parameter enclosure had been rounded at
    256 bits through a stale Python default argument. That was fixed before any MN run.
- **History:** the MN eq 0 run under the old settings was stopped (by PID, mine) before producing any result.

## Amendment A5 (2026-10-12, before any MN replay output): local re-expansion (MN rows), with bridge additions 1–5

**Diagnosis (measured):** under A4, the MN steps stayed at Δs ≈ 6e−5 whatever the tolerance (1e−25 or 1e−15), the
order (30 or 15) or the E representation (state or direct).
- CAPD's field value and Jacobian at the segment start are tight: max |Df| = 2.1, widths about 1e−34.
- But the field's width over a time box grows like about 4.8e4·h. At h ≥ 1e−4 CAPD throws "Possible division by
  zero": the p-denominator enclosure is [−2.7e30, 3.2e31], against a true value of about 3.7e14.
- An interval interpreter run on the generated code shows **intra-group cancellation of about 1e5**: single E-group
  polynomials in t have terms of about 1e15 that sum to about 1e10. That is the dependency problem.

**A5, for the MN rows only:**
- **Splitting:** each straight segment is split into SUBSEG = 32 equal sub-segments, at exact dyadic points. The path
  is identical, so the homotopy class and the monodromy are unchanged.
- **Local re-expansion (codegen 3):** on each sub-segment t = c + Dσ, σ ∈ [0, 1], every polynomial is evaluated as
  P(c + Dσ) = Σ e_k σ^k. This covers each E-group of p and q (numerator and denominator) and each w_k numerator and
  denominator.
- **The coefficients:** the e_k are computed by the DRIVER, by Taylor shift (repeated synthetic division) followed by
  scaling by D^k, in **MPFR complex interval arithmetic**, starting from the exact base coefficients.
  - (Bridge 3) The e_k are enclosures, so CAPD integrates an interval-parameter family that contains the true
    field. The maximum absolute coefficient width is recorded (`A5_MAX_SHIFTED_COEF_WIDTH`).
  - (Bridge 5) The shift is done in MPFR, so the replay remains independent of FLINT/Arb.
- **E factors:** E_k = exp(w_k) is computed in the field, with the guarded `capd_proof::node_exp/node_cos/node_sin`.
  There is no E state. The watchdog covers the only failure mode of CAPD trig (slow reduction for huge arguments);
  here |Im w| < 2.
- **Settings:** as A4 (prec 128, tol 1e−25, order 30, 3 per-loop processes, checkpoints).

**(Bridge 2) Shift consistency gate, at EVERY sub-segment and for every polynomial.** At σ = 0, 0.5 and 1, the shifted
polynomial must overlap the direct interval evaluation of the original polynomial at c + Dσ. A failure throws a
dedicated, never-caught error (fail closed).

**(Bridge 4) Pre-registered response to a transport failure.**
- If CAPD throws on a sub-segment (for example "possible division by zero"), the sub-segment is halved dyadically and
  both halves are transported. This repeats up to 4 levels deep; beyond that, the row fails closed.
- Shift-gate failures are never halved.
- The number of halvings is reported (`A5_HALVINGS`).

**(Bridge 1) Positive control on real NVE data.**
- TS row 0 (already REPLAYED under the original settings) is re-run through the full A5 path (codegen 3, SUBSEG 32,
  prec 128, tol 1e−25, per-loop).
- It must give the same verdict (REPLAYED), with every cross-engine check true, including entry-wise overlap of g
  and h with v2's exact boxes.
- Its trace values must also overlap the original TS row-0 replay's.

**Control M6** goes through the A5 path too: the exact trace and det must be contained, and the wrong-p control
excluded.

**Probe (engineering, MN eq 0, loop g[0.1857], first segment):**
- about 30 s per sub-segment, so about 16 min per segment (against about a week before);
- 0 halvings;
- maximum shifted-coefficient width 9.5e−20 absolute (relative to coefficients of up to about 1e15).

## Amendment A6 (2026-10-12): TS rows with no output yet move to the A5 path (bridge-approved)

**Why:** the A5 positive control on TS row 0 reproduced the original-path certificate (same verdict, every
cross-engine check true, overlapping tr[g,h]) in 11 min instead of 4.3 h. The slow TS rows show the same dependency
problem.

**Exactly which rows run on which path:**

| row | path | status at registration |
|---|---|---|
| TS 0, TS 2, TS 3, C1, C2 | original (A1+A2) | REPLAYED (unchanged) |
| TS 4 | original | **running**: continues untouched, as a cross-check |
| C3 | original | **running**: continues untouched, as a cross-check |
| TS 1 | **A5** (`primary_a5`) | no output (its only attempt failed closed before A2) |
| TS 5 | **A5** (`primary_a5`) | not started |
| C4, C5, C6, C7, C8 | **A5** (`primary_a5`) | not started |
| TS 4, C3 | **A5** as well (`primary_a5`) | no output yet; compared with the original-path runs when those finish |
| TS-0 and C1 secondaries (24-gon, 0.8 r) | **A5** (`secondary_a5`) | not started |
| cross-path re-runs: TS 2, TS 3, C1, C2 | **A5** (`xpath_a5`) | for the cross-path table (TS 0's is the A5 control) |
| MN eq 0–5, MN axial 0–3 (+ secondaries) | A5 | queued (MN queue) |

**Cross-path rule (bridge condition 3, fixed now):** for every row that has both an original-path and an A5 result,
the verdicts must be equal and the enclosures of w_g, w_h and tr[g,h] must overlap. **A disagreement (non-overlap or
a verdict change) is a FAIL to investigate. It is never averaged or resolved by picking one path, and no TS row counts
as REPLAYED under A5 until it is resolved.**

**Cores:** the A6 queue runs 3 per-loop processes alongside the MN queue (3) and the two original-path rows (2): 8 of
10 cores, so the queues do not compete.

**Reporting (bridge condition 4):** the paper and the ledger say plainly that there are two validated configurations
of the same CAPD/MPFR stack, and give the cross-path table.

## Amendment A7 (2026-10-12): the complete escalation ladder for an undecided (NOT_REPLAYED) row

**Fixed BEFORE any escalated result exists.** The first case is C6 (tschaos 5), which is undecided at the A5 settings:
tr[g,h] ≠ 2 could not be decided, while every cross-engine overlap is true. The ladder applies to every row that ends
NOT_REPLAYED on the A5 path, TS or MN.

| step | settings | label |
|---|---|---|
| 0 | the row's registered A5 settings (prec 128, tol 1e−25, order 30, SUBSEG 32) | primary_a5 / primary |
| 1 | the registered escalation: **order 40, prec 256, tol 1e−40**, SUBSEG 32 | escalated_a5 / escalated |
| 2 | **only if step 1 is still undecided:** step 1's settings with **SUBSEG 128**, applied to all loops, on the bridge's reading that the width growth is wrapping along the loop | escalated2_a5 |

- **After step 2, stop.** If the row is still undecided, it is reported as **NOT_REPLAYED by CAPD (undecided;
  enclosures contain the v1/v2 values)**. There is no further tuning, and the v1/v2 certificate stands as it is.
- **Contradictions are a different case:** a non-overlap or verdict change is still a FAIL to investigate, never
  something to escalate past.
- Each step's settings, verdict and widths are recorded.

### A7 clarification (2026-10-12, before any cross-path xpath_a5 result exists): undecided is not a disagreement

The A6 cross-path rule says "a verdict change is a FAIL". It is made precise as follows.

- A **cross-path FAIL** is either of:
  - (i) non-overlapping enclosures of w_g, w_h or tr[g,h];
  - (ii) opposite **certain** decisions on any certificate condition, e.g. a condition certainly true on one path and
    certainly false on the other.
- A run that is **undecided** (NOT_REPLAYED because a condition is neither certainly true nor certainly false) is
  **not** a disagreement. That run goes through the A7 ladder, and its overlaps are still required at every step.
- Expected case: the C rows on the A5 path at prec 128 (C6 and C7 are already undecided there). C1 and C2's A5
  re-runs may also be undecided. That would not contradict their original-path REPLAYED results, provided the
  enclosures overlap.

## Amendment A8 (2026-10-12, scheduling only; bridge-suggested): the remaining C rows start at A7 step 1

The pattern is diagnosed: the far-out C bases exhaust 128 bits. So the C rows **not yet started** on the A5 path begin
directly at the A7 step-1 settings (prec 256, order 40, tol 1e−40):
- C3 primary_a5;
- the C1 secondary;
- the C1 and C2 cross-path re-runs.

This is strictly more precise and changes no decision rule. If such a row is undecided, it goes straight to A7 step 2.
C8 had already started at prec 128 when A8 was filed, so it runs the normal ladder. Implemented by a flag file
(`c_rows_start_step1`) that the runner reads at row start.

Outcome: to be appended below after the runs, unchanged rules.

**Correction note (2026-10-12):** commit 5b555b9's message says "all six TS plunging rows (0-5) now REPLAYED". That
is wrong. At that commit, TS rows 0, 1, 2, 3 and 5 were REPLAYED, and TS row 4 was still running on both paths.

**Cross-path table reporting rule (bridge, 2026-10-12):** a cross-path re-run that ends the ladder still undecided is
listed as **"overlap only (A5 undecided)"**, not as a verdict agreement, so the table does not overstate the
cross-check.

**Scheduling note (2026-10-12 ~23:50, bridge core plan):**
- The A6 queue is back to 3 per-loop processes from its next row.
- The A7 ladder now runs in parallel at 2 processes (env `REPLAY_PROCS`). It handles C6 and C7 immediately, then any
  later undecided rows after A6.
- The MN queue keeps 3. The total of my processes is ≤ 9.
- Scheduling only: no effect on results.

**Scheduling note (2026-10-13 ~00:20, tabula's MEGNO rerun on 3 workers for about 2 days):**
- My total is now ≤ 7 at normal priority. A6 drops to 2 processes from its next row, and the ladder to 1 from its
  next step (override files).
- The excess in-flight processes were reniced to +19, not stopped: PID 93980 (the C1 secondary's third loop) and PID
  95856 (the ladder's second process, on the C6 escalation).
- Scheduling only.

**Scheduling note (2026-10-13 ~01:25, bridge suggestion): MN eq 0 split.**
- **Why it is possible:** under the old layout, each of MN eq 0's three processes was computing ALL loops, so one
  process's output is a complete row.
- **What was done:**
  - All three processes were stopped (by PID, mine) at 34 of 54 segments each.
  - Partial determinism check before stopping: the 34 checkpointed segments are bit-identical across the 3 copies.
  - Process 1's EXACT input was re-run (`mn_eq0_resume.py`). Its sha256 reproduces the checkpoint name, verified.
    It reloads those 34 segments and computes the rest for all loops.
  - The combine then takes every loop from that single output, with the same CAPD combine and finish_row.
- **Freed cores:** two, used for the MN queue (from the eq 0 secondary on), on the fixed layout at 2 processes.
- Scheduling only; the computation is unchanged.

**Scheduling note (2026-10-13 ~03:15, bridge budget of 7 cores):**
- The MN queue is split into two parallel queues at 2 processes each: equatorial 1–5, and axial 0–3 plus the axial-0
  secondary.
- The MN eq-0 secondary keeps running (2), and its old queue shell was stopped so it would not start further rows.
- Total: 2 + 2 + 2 for MN, plus 1 for the original-path TS 4, which is 7. Scheduling only.

**TS row 4, original path (2026-10-13):** FAILED-CLOSED at the A2 24 h watchdog, after loop 1 of 3 and 12 of 18
segments of loop 2. The tiny r = 0.045 loops near a singular point make the original path take more than 24 h. This
is resource only, and nothing is contradicted. TS row 4 is REPLAYED on the A5 path. No original-path cross-path pair
exists for TS 4: the old run predates A3 checkpoints, so a re-run would take more than 30 h. Recorded as such; the
cross-path table has 6 other rows.
