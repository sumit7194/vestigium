# SEALED blind prediction of the branch-S retry (4 pieces, W0 = 5e-8)

- **[model: Fable 5.2]. UNVERIFIED.** Written 2026-11-26 for the brief `BRIEF_FABLE_PREDICT.md` (commit 4bc659f).
- **Blindness.** I read only the allowed inputs of the brief, by exact path. I did not open, list or stat `retry_s/mm|mp|pm|pp|refs`, `retry_s/launch.log` or the b15e launch log, ran no `ps`, and ran no git log past 4bc659f.
- **Disclosure.** From this session's memory index and the commit subjects shown in its header (up to 4bc659f) I know that pieces mm and mp were launched before pm and pp, and that the launcher was paused. I know no number and no outcome of any piece.
- **Compute.** Seconds of Python over the allowed files. Nothing launched. Main not edited.
- **Units.** Ratios are the printed values of the `CHECKPOINT` lines (2 decimals). Intervals are inclusive.

## 1. Prediction

| Piece | Checkpoint | u2 point | u2 80% interval | u1 point | u1 80% interval | Call |
|---|---|---|---|---|---|---|
| mm | 283.8852 | 1.00 (model 1.000) | [1.00, 1.01] | 1.00 | [1.00, 1.01] | PASS |
| mm | 290.8497 | 1.00 (model 1.004) | [1.00, 1.01] | 1.00 | [1.00, 1.01] | PASS |
| mm | 291.8852 | 1.02 (model 1.020) | [1.01, 1.03] | 1.00 | [1.00, 1.01] | PASS |
| mm | 295.8852 | 1.01 (model 1.014) | [1.01, 1.02] | 1.00 | [1.00, 1.01] | PASS |
| mm | 793.2346 | 3.11 (model 3.110) | [2.65, 3.29] | 1.00 | [1.00, 1.01] | PASS |
| mm | 800.0941 | 1.38 (model 1.381) | [1.28, 1.46] | 1.00 | [1.00, 1.01] | PASS |
| mm | 801.2346 | 1.37 (model 1.367) | [1.27, 1.45] | 1.00 | [1.00, 1.01] | PASS |
| mm | 805.2346 | 1.27 (model 1.265) | [1.19, 1.33] | 1.00 | [1.00, 1.01] | PASS |
| mp | 283.8852 | 1.00 (model 1.000) | [1.00, 1.01] | 1.00 | [1.00, 1.01] | PASS |
| mp | 290.8497 | 1.00 (model 1.004) | [1.00, 1.01] | 1.00 | [1.00, 1.01] | PASS |
| mp | 291.8852 | 1.02 (model 1.020) | [1.01, 1.03] | 1.00 | [1.00, 1.01] | PASS |
| mp | 295.8852 | 1.01 (model 1.014) | [1.01, 1.02] | 1.00 | [1.00, 1.01] | PASS |
| mp | 793.2346 | 3.10 (model 3.101) | [2.64, 3.28] | 1.00 | [1.00, 1.01] | PASS |
| mp | 800.0941 | 1.38 (model 1.381) | [1.28, 1.46] | 1.00 | [1.00, 1.01] | PASS |
| mp | 801.2346 | 1.37 (model 1.366) | [1.27, 1.45] | 1.00 | [1.00, 1.01] | PASS |
| mp | 805.2346 | 1.27 (model 1.265) | [1.19, 1.33] | 1.00 | [1.00, 1.01] | PASS |
| pm | 283.8852 | 1.00 (model 1.000) | [1.00, 1.01] | 1.00 | [1.00, 1.01] | PASS |
| pm | 290.8497 | 1.00 (model 1.004) | [1.00, 1.01] | 1.00 | [1.00, 1.01] | PASS |
| pm | 291.8852 | 1.02 (model 1.020) | [1.01, 1.03] | 1.00 | [1.00, 1.01] | PASS |
| pm | 295.8852 | 1.01 (model 1.014) | [1.01, 1.02] | 1.00 | [1.00, 1.01] | PASS |
| pm | 793.2346 | 3.11 (model 3.113) | [2.65, 3.29] | 1.00 | [1.00, 1.01] | PASS |
| pm | 800.0941 | 1.38 (model 1.381) | [1.28, 1.46] | 1.00 | [1.00, 1.01] | PASS |
| pm | 801.2346 | 1.37 (model 1.366) | [1.27, 1.45] | 1.00 | [1.00, 1.01] | PASS |
| pm | 805.2346 | 1.27 (model 1.265) | [1.19, 1.33] | 1.00 | [1.00, 1.01] | PASS |
| pp | 283.8852 | 1.00 (model 1.000) | [1.00, 1.01] | 1.00 | [1.00, 1.01] | PASS |
| pp | 290.8497 | 1.00 (model 1.004) | [1.00, 1.01] | 1.00 | [1.00, 1.01] | PASS |
| pp | 291.8852 | 1.02 (model 1.020) | [1.01, 1.03] | 1.00 | [1.00, 1.01] | PASS |
| pp | 295.8852 | 1.01 (model 1.014) | [1.01, 1.02] | 1.00 | [1.00, 1.01] | PASS |
| pp | 793.2346 | 3.10 (model 3.101) | [2.64, 3.28] | 1.00 | [1.00, 1.01] | PASS |
| pp | 800.0941 | 1.38 (model 1.380) | [1.28, 1.46] | 1.00 | [1.00, 1.01] | PASS |
| pp | 801.2346 | 1.37 (model 1.366) | [1.27, 1.45] | 1.00 | [1.00, 1.01] | PASS |
| pp | 805.2346 | 1.26 (model 1.265) | [1.19, 1.33] | 1.00 | [1.00, 1.01] | PASS |

- **Per piece.** mm PASS, mp PASS, pm PASS, pp PASS (all 8 checkpoints each, no THREW, controls hold).
- **Overall verdict.** PASS.
- **Probability that the retry reads PASS: 0.90.** The rest: FAIL 0.04 (the scaling model is wrong), INVALID or THREW 0.06 (a control fails or a run throws, outside the model).
- **Fake width (ungraded).** At every checkpoint the piece's fake is at most half of A3's, against a threshold that also about halves. The tightest cell is 805.2346: at most 1.03e-6 against 1.50e-6. I expect about 1/8 to 1/4 of A3's fake.
- **Ungraded extra.** At 793.2346 the pieces' E width along u2 is 1.3e-7 to 1.84e-7 (A3: 1.4705e-6).

## 2. Scaling model

**Decomposition.** The checkpoint width along a covector is W = W_poly + W_E (the A3 line at 793.2346: 1.663e-6 = 1.925e-7 + 1.4705e-6). So

    ratio_u2(piece, t) = beta(t) + phi(t) * W_E,A3(t) / true2_piece(t),   phi := W_E(5e-8) / W_E(1e-7).

**True widths (no model: read from the 4 piece checkpoint files).**
- true u1 of a piece is half of A3's to 4 digits at all 8 checkpoints.
- true u2 of a piece is half of A3's except at 291.8852 (0.963 of half), 793.2346 (0.855 to 0.860 of half) and 805.2346 (0.991 of half). A fit true2 = a W0 + b W0^2 at 793.2346 gives a = 1.349e-7, b = 0.546e-7 at W0 = 1e-7: 29% of A3's thin width there is curvature. This is why the piece gains less than a factor 2 from the denominator at the failing checkpoint.

**W_poly.** beta = W_poly / true = 1.000 (A3: 0.999 to 1.001 at 26 states). Exception 793.2346, where A3 has beta = 1.016 (derived: 1.925e-7 / 1.8955e-7; the dense truth equals the stored truth there, so it is not a sampling effect). I assume the excess is of quadratic or cubic origin, so the piece has beta = 1.007, range 1.003 to 1.012.

**W_E,A3(t) along u2** (W minus true from the A3 lines; exact from the INJ line at 793.2346): 1.2e-10 or less (283.89), 1.01e-8, 1.45e-8, 1.91e-8, 1.4705e-6 (793.23), 1.525e-6, 1.544e-6, 1.517e-6 (805.23).

**phi: how E scales with W0.** Per step E receives s = p2 + dDe and is otherwise transported linearly (G <- D1c G), which does not depend on W0.
- p2 is cubic in W0. Evidence: the pre-test (quarter piece, E kept) has p2 4.014e-11 against 3.190e-10, ratio 0.1258.
- dDe is bilinear, dDe = c * W_K * |e|. Evidence: the pre-test's g_u2 ratio 0.5034 (dDe 1.664857e-8 against 3.306762e-8) at the same E. The 0.7% above one half is the E part of the hull K, which was not halved; it matches W_E(u1)/true(u1) = 7e-3.
- So with E = W0^3 f: f' = A f + p + W0 B |f|, f = a0 + a1 W0 + a2 W0^2 + ..., all a_i >= 0. Hence **phi <= 1/8 at every time and in every direction**, and phi = (1/8)(1 - sigma/2) when the dDe-descended share sigma of E is first order in W0 (fed from the p2-built thick part of E). The floor of that regime is 1/16.
- **Use of the A3 time series.** W_E(u1)/true(u1) is flat at 6e-3 to 7e-3 from t = 652 to 805, through the second periapsis: the thick part of E is transported like the set itself and is not self-amplified. The u2 part grows 30 times over 692 to 792, but a dDe rate at periapsis strength (0.29 * W_K * E_max, from the 792 to 793.23 replay) explains under 8% of that growth; the rest is linear transport. The replay gives 2.3% new in the last 1.21 t, and a rate that decays backwards with a time constant of about 7 t or less.
- **Values used.** First passage: sigma = 0.035 (from memory of this session's earlier Z1 scoring, not re-read), phi = 0.123. At 793.2346: sigma = 0.15 (range 0.05 to 0.55), phi = 0.116. At 800 to 805, after the periapsis injections: sigma = 0.35 (range 0 to 0.75), phi = 0.104.
- **Caps.** phi = 1/8 gives 3.28 (793.23), 1.46, 1.44, 1.32. phi = 1/16 gives 2.13, 1.23, 1.22, 1.16. A FAIL at 793.2346 needs phi > 0.22.

**u1.** A3 has W_E(u1)/true(u1) = 7e-3 late; the piece has at most 2 * (1/8) * 7e-3 = 0.0018, printed 1.00.

**How the 4 pieces differ.** Only through their own true u2 (within 0.6% of each other at 793.2346: mm 8.110e-8, mp 8.147e-8, pm 8.101e-8, pp 8.148e-8). I assume E is the same for the 4 pieces to about 1%: the linearised dynamics at the 4 centres agree (true u1 identical to 4 digits), and the piece's own u2 covector differs from A3's by a rotation of about 1e-4 or less, which leaks under 0.2% of E's thick part.

**Other assumptions.**
- The S4 subdivision is a domain check and does not enter the injection (from memory of the code, not re-read; the pre-test ratios support it).
- No source of E scales slower than W0^3 (the p0 and p1 terms are 1e-34).
- No Girard reduction fires (A3: reductions 0).
- The harness accepts W/true = 1.0000 at the early checkpoints, as it did for A3.
- Fake is built from E widths off the surface, plus a part that scales at least linearly in W0 (pre-test: 7.820e-7 against 8.375e-7 with E kept).

## 3. Falsifiers

**Refute the model (not just an interval miss):**
1. Any printed u2 ratio above the phi = 1/8 cap with margin: above 3.35 at 793.2346, 1.48 at 800.0941, 1.46 at 801.2346, 1.34 at 805.2346, 1.03 at 291.8852, 1.02 at 295.8852, 1.01 at 283.8852 or 290.8497. It would mean a source of E that shrinks slower than W0^3.
2. Any printed u2 ratio below the phi = 1/16 floor with margin: below 2.10 at 793.2346, 1.21 at 800.0941, 1.20 at 801.2346, 1.14 at 805.2346. It would mean A3's E was mostly self-amplified at second or higher order.
3. Pieces that differ from each other by more than 0.05 at 793.2346, or by more than 0.02 at any other checkpoint.
4. Any u1 ratio printed 1.02 or more, or below 1.00.
5. Any piece's fake above half of A3's fake at the same checkpoint.
6. Any FAIL cell, THREW, HARNESS-ERROR, BUG or containment FAIL. Each refutes the PASS call; the last four lie outside the model.

**Only miss an interval (the model stands, sigma was misjudged):** u2 at 793.2346 between 2.10 and 2.64; u2 at 800.0941, 801.2346 or 805.2346 between the floor of item 2 and my lower end.

## 4. Literature (all from memory, not checked at source)
- Lohner, QR representation of the error set against wrapping (1987 thesis; 1992 survey chapter).
- Wilczak and Zgliczynski, C^r-Lohner algorithm, Schedae Informaticae 20 (2011): the C1/C2 set propagation that CAPD implements.
- Kuhn, Rigorously computed orbits of dynamical systems without the wrapping effect, Computing 61 (1998): zonotope error sets.
- Girard, Reachability of uncertain linear systems using zonotopes, HSCC 2005: generator reduction.

No statement above depends on a specific section or equation of these.
