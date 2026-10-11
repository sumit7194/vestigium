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

Outcome: to be appended below after the runs, unchanged rules.
