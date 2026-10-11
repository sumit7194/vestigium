# NaN safeguard for CAPD proof code (bridge request, 2026-10-11)

**Bridge:** the log-NaN finding is a symptom of something broader. With `__MPI_TEST_NAN__` compiled out, ANY operation
that can produce NaN passes it through silently, and every NaN comparison is false. So a decision such as
"certainly < 0" or "certainly ≠ 2" on a NaN endpoint can take the wrong branch. The bridge asked for:
- **(a)** if possible, a rebuild with `-D__MPI_TEST_NAN__`;
- **(b)** finite-endpoint checks on every interval that enters a certificate decision, with a fired NaN control,
  including division by intervals containing 0.

## (a) Rebuild with `-D__MPI_TEST_NAN__`: NOT POSSIBLE without a source patch (recorded)

- **It does not compile at 2f06098.** `capd/intervals/MpInterval_Fun.hpp:36` reads
  `if(isNaN(x.leftBound()) || isNaN(x.rightBound())))`, which has an extra `)`; clang reports "extraneous ')' after
  condition". The option has evidently never been built. Our pin rule is no source patch, so (a) stops here.
- **Even patched, it would not be a global safeguard.** `testNaN` is called in only 5 places, all in
  `MpInterval.cpp`: on the ARGUMENT of sin, cos and tan, and on the RESULT of log and exp. It is never called in
  + − × ÷, sqrt or the set and ODE code. So inf − inf, inf/inf and the like would still pass NaN through.
- **The INF option is dead too.** `MpIntervalSettings.h` documents `__MPI_TEST_INF__`, but the `.cpp` tests
  `_MPI_TEST_INF_` (lines 79, 238, 399). Defining the documented macro does nothing.
- (b) is therefore the safeguard. It does not depend on the build.

## (b) What was added (`tests/proof_guard.h`, namespace `capd_proof`)

- **`require_finite`, `require_finite_all`:** throw unless both endpoints satisfy `isNumber` (mpfr_number_p, so
  neither NaN nor ±inf) and lo ≤ hi.
- **Decision helpers:** `certainly_positive`, `certainly_negative`, `certainly_less`, `certainly_disjoint` ("≠ c",
  e.g. tr[g,h] ≠ 2) and `certainly_in_interior` (covering and a-priori-bound checks).
  - Each one calls `require_finite` on every argument first. A non-finite argument THROWS (fail closed), never
    returns false or true.
- **RULE: every interval entering a certificate decision goes through these helpers. No raw bound comparisons in
  proof code.** To be enforced by review of each proof program.
- **`checked_sin` / `checked_cos` hardened:**
  - Now also require finite, ordered endpoints. Before this fix, an inverted box such as [+inf, 3] passed the
    range test (+inf ≥ −10¹² and 3 ≤ 10¹²) and sent CAPD's `quadrant()` into an endless loop.
  - Found by the reachability control below. The watchdog turned the hang into a fail-closed exit.
- **`checked_log` hardened the same way.**

## Fired controls

**`tests/g_nan.cpp`:**
- Each NaN-producing or division-by-zero case is run on raw CAPD. If CAPD returns an interval, all 7 helpers must
  throw on it.
- **Result: `G_NAN CONTROL PASS (0 slipped)`.** Raw CAPD behaviour, recorded:

  | case | raw CAPD MpInterval | caught by |
  |---|---|---|
  | inf − inf, inf + (−inf), inf / inf, [nan,nan] + 1, exp of [nan,nan], sqrt of [nan,nan] | [NaN, NaN] **silently** | helpers (all 7 throw) |
  | log of [−1, 1] / [−2, −1] | [NaN, 0] / [NaN, NaN] **silently** | helpers; checked_log refuses the input |
  | [0,1] · [1,inf], exp of [1e300], [1,inf] + 1, 1 / [tiny], inf / [1,2] | an infinite endpoint (correct, but not decidable) | helpers |
  | 1/[0,0], 0/[0,0], 1/[−0,0], 1/[0,1], 1/[−1,0], 1/[−1,1], [−1,1]/[−1,1], 1/entire, 1/[nan,nan] | **THROW** "Possible division by zero" | CAPD itself |
  | 0 · [inf,inf], entire · 0 | [0, 0] | (0 · x = 0 for real x; [inf, inf] holds no real number) |
  | **[0, NaN] · 2** | **[0, 0] (finite!)** | **NOT catchable after the fact**: see the reachability test below |

- Positive controls (finite intervals decide correctly): all correct.

**NaN swallowing.**
- Multiplication turns a NaN endpoint that sits next to a 0 endpoint into a finite result:
  - [0, NaN] · 2 = [0, 0];
  - [0, NaN] · [−1, 1] = [0, 0].
- Other cases keep the NaN: [1, NaN] · 2 = [2, NaN], [1, NaN] + 1, sqrt, exp, negation, and so on.
- Because a swallowed NaN cannot be detected later, the safeguard also has to show that **NaN cannot be CREATED**
  from the boxes a computation can actually reach.

**`tests/g_nanreach.cpp`: reachability.**
- With directed rounding, overflow sends a lower bound to −inf or to the largest finite number, and an upper bound
  to +inf or to −MAX. So reachable boxes have lo ∈ ℝ ∪ {−inf} and hi ∈ ℝ ∪ {+inf}.
- The test is exhaustive over the endpoint grid {−inf, −MAX, −1e9, −1, −tiny, −0, 0, tiny, 1e−9, 1, 3, 1e9, MAX,
  +inf} at 53 and 256 bits:
  - every + − × ÷ on every pair of reachable boxes;
  - sqrt, exp, checked_log, checked_sin and checked_cos on every box;
  - requirement: no NaN, no inversion, and containment of the op at every finite grid point inside the box.
- **Result: 85 902 cases, 14 244 THROW, 71 658 returned, 0 violations: `NANREACH PASS`.**
- **Control** (`g_nanreach control`, which adds the UNREACHABLE boxes with lo = +inf or hi = −inf): **34 733
  violations, `NANREACH CONTROL FIRED`**. For example, [−inf,−inf] + [0,inf] = [−inf, NaN].
- **Conclusion:**
  - From finite inputs, with log and trig behind their guards, CAPD's interval operations never create a NaN.
  - The only NaN sources are inputs that are already non-finite, or point-infinite, which is unreachable.
  - So `require_finite` on the INITIAL data plus the decision helpers on every certificate input closes the hole.
- **Caveat (stated):** this covers the scalar operations. NaN inside CAPD's ODE and set code would need one of
  those sources. The final sets are still passed through `require_finite_all` before any decision.

## Re-check

The full registered differential check was re-run with the hardened guard. It gave identical op and result hashes
at all three precisions and verdict PASS (see DIFFCHECK.md).

Environment: CAPD 2f06098, MPFR 4.2.2, GMP 6.3.0, Apple clang 21, macOS 26.5 arm64.
