# Draft reports to CAPD upstream (github.com/CAPDGroup/CAPD) — FOR THE USER TO SEND

Drafted 2026-10-11. Nothing has been sent; the user sends any outside message. Everything below is against master
commit 2f060980d0685cc9bf88352e08c242197cd7d686, built with `-DCAPD_INTERVAL_TYPE=NATIVE
-DCAPD_ENABLE_MULTIPRECISION=ON` on Apple arm64 (macOS 26.5, Apple clang 21, MPFR 4.2.2, GMP 6.3.0). Each section is
meant as a separate GitHub issue; reproducers are in `qsim/capd/tests/` of this repo.

---

## Thanks (could go in the first issue)

Thank you for PR #18 (`CAPD_INTERVAL_TYPE = NATIVE`) and PR #22 (host processor recognition): with them master
builds and runs on Apple arm64 without filib and without any local patch. 41/44 ctest tests pass; we believe the
three failures below are test-side, not library defects.

---

## Issue A — `MpInterval` `log` returns a NaN endpoint for arguments reaching below 0 (no domain error)

**What happens.** For an `MpInterval` whose left endpoint is negative, `log(x)` returns an interval with a NaN
left endpoint (and NaN right endpoint if the whole box is negative) instead of throwing. Examples at 113 bits:
`log([-1, 1])` → `[nan, 0]`; `log([-2, -1])` → `[nan, nan]`. `sqrt` on the same boxes throws
`"MpInterval Function sqrt(x) - domain error"`, so the behaviour is inconsistent.

**Why.** `log` in `capdAlg/src/mpcapd/intervals/MpInterval.cpp` relies on `testNaN(res)`, but `testNaN` is a no-op
unless `__MPI_TEST_NAN__` is defined, and that define is commented out in `MpIntervalSettings.h`.

**Why it matters.** A NaN endpoint can pass silently through comparisons written as `!(a < b)`. It does not create a
wrong enclosure of a defined value, but a computer-assisted proof should fail loudly here.

**Related, found while trying to enable the check:**
- `-D__MPI_TEST_NAN__` does not compile: `MpInterval_Fun.hpp:36` has an extra `)` in
  `if(isNaN(x.leftBound()) || isNaN(x.rightBound())))`.
- Even when enabled, `testNaN` is only called for sin/cos/tan arguments and log/exp results, never in + − × ÷.
- The documented `__MPI_TEST_INF__` (in `MpIntervalSettings.h`) does nothing, because `MpInterval.cpp` tests
  `_MPI_TEST_INF_` (lines 79, 238, 399).
- Multiplication can turn a NaN endpoint next to a 0 endpoint into a finite result: `[0, NaN] * 2 = [0, 0]`.
  (We found no way to create a NaN from finite inputs other than log: `tests/g_nanreach.cpp`.)

**Suggestion.** An explicit domain check in `log` (as `sqrt` has); fix the parenthesis so `__MPI_TEST_NAN__` can be
enabled; unify the INF macro name.

Reproducer: `tests/diffcheck.cpp` (line `4 log -0x1p0 0x1p0` at precision 113).

---

## Issue B — `MpInterval` `sin`/`cos`: argument reduction is linear in |x| (effectively hangs for |x| ≳ 1e13)

**What happens.** `sin(MpInterval(x))` for a point x with |x| ≳ 1e13 (256 bits) does not return within minutes;
up to 1e12 it returns correct enclosures (checked against Arb). This is related to #28 (double path, large
negative arguments), but on the MPFR path it affects positive arguments too.

**Why.** `modulo4()` in `MpInterval.cpp` reduces the quadrant number with
`while (x > 32000) x = x - MpReal(64000);`, i.e. about |x|/(π/2)/64000 MPFR subtractions. In addition, once the
quadrant number exceeds 2^precision these subtractions are inexact, so for very large arguments the loop may not
terminate and the computed quadrant may be wrong.

**Suggestion.** Compute the quadrant modulo 4 directly, e.g. `mpfr_fmod(q, 4)` or via `mpz` from the (exact)
`floor` that `quadrant()` already produces.

Our workaround: proof code range-checks every trig argument (|x| ≤ 1e12, fail closed) and runs under a hard
wall-clock watchdog.

---

## Issue C — #27 also reproduces on the MPFR path

`x' = 10(1 − x)`, `x(0) = 1` as a point set, t = 0.05: `MpIOdeSolver` throws "minimal time step reached", exactly
as the double `IOdeSolver` does; one ulp wider, `[1 − ulp, 1]`, both work (`x(0.05) ∈ [0.999999, 1.00001]`). It
fails loudly, so it is not a soundness issue. Reproducer: `tests/reg27.cpp`.

---

## Issue D — `intervalTest` `parse_from_sstream` (ctest #7) expects a non-rigorous bound

The test parses `"[3.21312312, 4.324324324]"` into a double interval and requires `rightBound() ==
4.324324324` (0% tolerance), i.e. the nearest double, 4.32432432399999999717…, which is **below** the decimal. On
arm64 NATIVE, CAPD returns 4.32432432400000088534… (the smallest double ≥ the decimal), which is the correct
outward rounding; the left bound is likewise the largest double ≤ 3.21312312 (verified exactly,
`tests/parse7.cpp`). We suggest the test assert containment (`leftBound() ≤ decimal ≤ rightBound()`, e.g. in
exact rational arithmetic) rather than equality with the nearest double.

---

## Issue E — ctest #43 (`DPoincareMapMaskTest`) and #44 (`SingularNaturalPowerTest`) tolerances on arm64

Both are non-interval tests with absolute tolerances tuned on x86:
- #43 uses `DMap` with tol 1e−12 (1e−14 for the normal form); arm64 differences are 1.07e−12 to 2.05e−12 and
  1.56e−14, consistent with FMA contraction or libm last-bit differences.
- #44 uses `LDVector` with tol 1e−13; on Apple arm64 `long double` is 64-bit double (not 80-bit extended), and the
  differences (1.1e−13 to 7e−13, one 1.46e−11) are consistent with that.
Suggestion: relative tolerances, or tolerances tied to `std::numeric_limits<T>::epsilon()`.

---

## Issue F (minor) — `MpReal(mpfr_t, RoundingMode, PrecisionType)` is declared but not defined

Declared in `capd/multiPrec/MpReal.h` (line 114); using it gives an undefined-symbol link error. Either define it
(mpfr_init2 + mpfr_set with the rounding mode) or remove the declaration.

---

## Differential check of MPFR interval arithmetic (context, could accompany A/B)

We ran 3 × 10⁵ random +, −, ×, ÷, sqrt, exp, log, sin, cos on `MpInterval` at 53, 113 and 256 bits (point,
narrow, wide, near-tie and huge/tiny boxes up to the MPFR exponent limits), checking each result against Arb
enclosures of the true range at ≥ 1024 bits. **Every result contained the true range** (0 failures), point-input
results were at most 1 ulp wide, and the checker's own mutation controls (collapsed intervals) were all detected.
The only anomaly was Issue A (NaN from log below 0). Thank you for a very solid MPFR interval layer.
