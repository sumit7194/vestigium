# A3 R3a cause checks a′ and b′: results, read against PREDICTIONS_prime.md (b110310)

Ran 2026-11-24 with `checks_prime.py`: 19 s wall time, 1 core, nice 12, peak RSS 1.27 GB (1.5 GB was declared). Full
output: `checks_prime_out.txt`, `a_prime.json`, `b_prime.json`. These are diagnostics in double precision; A3's verdict is
unchanged (FAIL, controls hold). Written by Claude Opus 5.5 (Quantum).

## Controls: both PASS
- **a′0.** The hull widths w1 and w2 match the stored values to 1.0000 at all 8 time checkpoints (5% allowed).
- **b′0.**
  - Every state centre matches within 6.5e-9.
  - W_poly / w_true lies in [0.999, 1.001] at all 26 saved states, 792.02 included ([0.8, 1.25] allowed).
  - The (a)/(b) control failures were therefore the linear yardstick, as RESULTS.md said.

## a′: the true thin width (hull)
- w2(793.2346) = 1.8955e-7, the same as the stored value. Over 793.23 ± 0.5 it ranges from 9.9e-8 to 2.86e-7, within a
  factor 3 either way.
  - So H1/H3 are confirmed: a real, smooth low.
  - H4 (a wrong reference) is rejected.
- **Shape near the second passage.** It rises from 2.8e-9 at 784.5 to about 3.3e-7 at 789.5–790, falls to about 7e-8 at
  792.5, and then rises steeply: 1.9e-7 at 793.23, 5.2e-7 at 795 and 8.3e-7 at 800.
  - 793.23 sits on the steep rising wall just after a local minimum.
- **First passage.** It shows the same kind of deep lows: 1.1e-8 at 286.0 and 4.0e-8 at 294.5.

## b′: where the excess lives (thin direction u2(t_k))
- **H1: CONFIRMED by its stated tests.**
  - No saved interval holds more than half the log growth of W2_E from 292 to 792; the largest share is 0.44.
  - At 792.02, W2_E / excess = 1.00.
- **H2 (a late step event): NOT supported.** 772 → 792 holds 0.06 of the log growth (a 1.30× jump).
- **H3 (polynomial part too wide): NOT supported.** W_poly / w_true(792.02) = 1.001.
- **The ratio (W_poly + W_E) / w_true at 792.02 is 8.70.** This double-precision reader agrees with the run's own 128-bit
  8.77 at 793.23, which is a cross-check of the reader.
- **Descriptive.** The ratio is 1.07–2.87 for the whole flight up to 772 (2.47 there). At 792.02 it is 8.70, because
  w_true fell about 4× (6.1e-7 → 1.5e-7) while W2_E rose 1.3× (9.0e-7 → 1.17e-6).
  - W2_E along the turning thin direction is not monotone: it dips between 612 and 692. Over 692 → 792 it rises about
    30×.

## Reading (diagnostic)
- The R3a FAIL comes from the error part E built up along the thin direction over the flight, mostly from about 692 on.
  At 793.23 it met a pre-periapsis low of the true thin width.
- There is no sign of a late numerical event, a bad reference or an over-wide polynomial part.
- For a retry, the lever is E relative to the true width at the thin-width lows. Splitting the set into pieces scales the
  polynomial/true width by the piece size. Whether E shrinks faster than that depends on how E is injected (P2 against
  dDe), which the approved logged replay from st.t792.0198 measures.
