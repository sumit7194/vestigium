# CAPD trust rule 3: differential check of CAPD's MPFR interval arithmetic against Arb

**Registered 2026-10-11 BEFORE the full run** (this file and the code are committed first). The rule comes from the
bridge: at least 10⁵ random operations (+ − × ÷ sqrt exp log sin cos) on MPFR intervals, including near-tie and
huge/tiny cases. CAPD's enclosure must contain Arb's tight ball at higher precision, and **a single
non-containment disqualifies.**

## What runs

- **Harness:** `tests/diffcheck.cpp`, CAPD `MpInterval` at commit 2f06098 on MPFR 4.2.2, built with
  `tests/guard_build.sh` under the proof guard.
  - Endpoints go in and out as exact MPFR hex (`%Ra`). An operand that is not exactly representable is reported
    `BADINPUT` and counted as a driver failure.
  - sin and cos go through the guarded `capd_proof::checked_sin` / `checked_cos`.
  - `log` is CAPD's raw log, so CAPD itself is characterised. `clog` is the guarded `capd_proof::checked_log`.
  - **Hard per-call timeout:** SIGALRM after 10 s prints `TIMEOUT` and the driver restarts after that line.
- **Driver:** `diffcheck.py`, using python-flint 0.9.0 (Arb 3.6.0).
  - Precisions: 53, 113 and 256 bits (256 is the working precision for proofs).
  - **N = 100 000 operations per precision** (3·10⁵ in total), seed 20261011, plus 300 `checked_log` controls per
    precision.
  - Case mix:
    - about 25% near-tie: 1 ± half-ulp, (1 ± 2⁻ʲ)², quotients a hair off a grid point, s² ± 1 under sqrt,
      exp/log next to 0/1, floats nearest to nπ/2 up to n = 10¹¹, tiny trig arguments, and 0;
    - about 15% huge/tiny: binary exponents up to ±(2³⁰ − 5), i.e. MPFR overflow and underflow; exp limited to
      |x| ≤ 2⁴⁰ and trig to the guard range;
    - about 2% of sin/cos are guard controls (|x| > 10¹²);
    - the rest are point, narrow (1–8 ulp) and wide boxes; wide sin/cos boxes of width up to about 7 are placed
      anywhere in |x| ≤ 10¹², so many contain extrema.

## What counts as correct

For every OK result, Arb encloses the **true range of the operation over the input box** at 1024 bits. On
ambiguity it refines to 4096 and then 16384 bits. CAPD's [L, R] must certainly contain:

- **+ and −:** all four corner values. They are compared exactly by rearrangement, (u − B) + w ≥ 0, because a
  huge + tiny sum cannot be enclosed tightly enough by a ball.
- **× and ÷:** all four corners.
- **sqrt, exp and log:** both endpoint values. log with lo ≤ 0 needs L = −∞. sqrt with lo < 0 needs [0, √hi].
- **sin and cos:** both endpoint values, plus +1 or −1 whenever a maximum or minimum point lies in the box. That is
  decided rigorously with Arb: is there an integer k with lo ≤ phase + 2πk ≤ hi?
- **Two random interior sample points** for every op. A sample is used only if its ball certainly lies inside the
  box.

## Verdict rules (fixed now)

- **DISQUALIFY** on any of:
  - a certain non-containment;
  - a NaN endpoint (except the registered log case below);
  - an inverted interval;
  - a TIMEOUT for an argument inside the guard range;
  - a THROW where the operation is defined on the whole box;
  - a guard that fails to fire.
- **Allowed THROW:**
  - a mathematical domain error: 0 in the divisor, or sqrt of a box reaching below 0;
  - the trig guard, for |x| > 10¹²;
  - the checked_log guard, for a box not certainly > 0.
- **UNDECIDED:** a case still ambiguous at 16384 bits. Any such case is reported, and the run is not a PASS until
  each one is resolved.
- **Registered known defect, counted separately and not a disqualification.** It was found in the seed-1 smoke run
  (N = 2000 per precision) while this harness was being built, before this registration:
  - CAPD's MpInterval log of a box whose lower endpoint is < 0 returns a **NaN lower endpoint** instead of
    throwing. The reason: `testNaN` is compiled out, because `__MPI_TEST_NAN__` is commented out in
    `MpIntervalSettings.h`. sqrt, by contrast, throws a domain error.
  - The log is undefined there, so this is a missing domain check, not a wrong enclosure of a defined value. The
    upper endpoint must still enclose log(hi) when hi > 0, and that is checked.
  - Proof code is protected three ways: `capd_proof::checked_log` throws unless lo > 0 and rejects a NaN result;
    bare `log` is poisoned; and `check_proof_object.sh` refuses a log or trig name inside a Map formula string.
  - This goes into the upstream report draft.
- **Fired controls:** the checker must reject deliberately broken enclosures. For up to 3000 contained results with
  L < R per precision, collapse CAPD's interval to [R, R] and to [L, L]. **Every mutant must be judged
  NON-CONTAINED.** If any is missed, the checker is not validated and the run is not a PASS. In the seed-1 smoke
  run, 4042/4042, 4064/4064 and 4024/4024 mutants were detected.

## Also found while building this (source reading, for the upstream report)

- **The sin/cos "hang" for |x| ≳ 10¹³ is linear-time argument reduction, not a true hang.**
  `modulo4()` in `capdAlg/src/mpcapd/intervals/MpInterval.cpp` reduces the quadrant number by subtracting 64000 in
  a loop, so the cost is about |x|/10⁵ MPFR operations.
  - Beyond 2^prec the subtraction is inexact, so for |x| ≳ 2^prec · π/2 the loop may never terminate (or the
    quadrant could be wrong).
  - The guard at 10¹² (quadrant below 6.4·10¹¹, under 2⁵³) keeps every reduction exact and at most about 10⁷
    iterations. The 10 s per-call timeout covers the rest.
- `MpReal(mpfr_t, …)` is declared in `MpReal.h` but never defined (link error). The harness sets the value through
  the representation instead.

## OUTCOME (2026-10-11, run on registered commit a6d1f33; rules unchanged): **PASS**

`python qsim/capd/diffcheck.py 100000 20261011` → `diffcheck_run.txt` and `diffcheck_results/summary.json` (per-op,
per-category statistics).

| prec | ops | contained | allowed domain THROW | guard THROW (trig + checked_log controls) | log NaN (registered defect) | **failures** | **undecided** | mutants detected |
|---|---|---|---|---|---|---|---|---|
| 53 | 100 300 | 98 036 | 968 | 562 | 734 | **0** | **0** | 6000 / 6000 |
| 113 | 100 300 | 98 054 | 975 | 527 | 744 | **0** | **0** | 6000 / 6000 |
| 256 | 100 300 | 98 063 | 980 | 583 | 674 | **0** | **0** | 6000 / 6000 |

- **Coverage per precision:** about 25 000 near-tie, 15 000 huge/tiny, 20 000 each of point, narrow and wide, and
  about 750 guard controls. 1524, 1481 and 1436 sin/cos boxes contained an interior extremum.
- **No TIMEOUT occurred** (every call stayed under 10 s, including trig arguments up to 10¹²).
- **Tightness (informational):** for point and near-tie inputs, every op's enclosure was at most 1 ulp wide
  (max relative width / 2^(1−prec) = 1.000 at all three precisions). That is the optimum for directed rounding.
- In the log-NaN cases the upper endpoint enclosed log(hi) wherever hi > 0, as checked.
- **Hashes:**

  | prec | ops sha256 | results sha256 |
  |---|---|---|
  | 53 | 670071747a63bd18… | e717c720e2a328a0… |
  | 113 | 8e0e90c85ebe26ab… | 1fdb95ed6913843d… |
  | 256 | 836e229077d5538a… | 3536199270f9a51f… |

  Full hashes are in summary.json.
- **Determinism:** the op stream is a pure function of the seed. Regenerating the prec-53 stream in a fresh
  process reproduced its hash. The ops/results `.gz` files (22 MB) are not committed, because they regenerate
  exactly.
- **Ruling:** CAPD MpInterval at 2f06098 on MPFR 4.2.2 satisfies trust rule 3, together with the registered log
  defect and its guard. Next come the ODE controls: an exact analytic solution, the Hénon–Heiles positive control
  and the Kerr negative control.

Environment: Python 3.13.12, python-flint 0.9.0 (Arb 3.6.0), CAPD 2f06098, MPFR 4.2.2, GMP 6.3.0, Apple clang 21,
macOS 26.5 arm64 (see ENVIRONMENT/).

### Re-check after the NaN-safeguard hardening of proof_guard.h (2026-10-11)

checked_sin, checked_cos and checked_log now also require finite, ordered endpoints (NAN_SAFEGUARD.md). The full
registered run was repeated with the rebuilt harness. Verdict: PASS, 0 failures, 0 undecided, 18 000/18 000 mutants
detected. **The op and result sha256 were identical to the registered run at all three precisions.** The committed
summary.json is the registered run's.
