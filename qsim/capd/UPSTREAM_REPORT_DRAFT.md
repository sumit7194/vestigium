# Draft reports to CAPD upstream (github.com/CAPDGroup/CAPD) — FOR THE USER TO SEND

Drafted 2026-10-11; revised 2026-10-17 (quantum), see the revision note at the end. Nothing has been sent; the user
sends any outside message. Everything below is against master
commit 2f060980d0685cc9bf88352e08c242197cd7d686, built with `-DCAPD_INTERVAL_TYPE=NATIVE
-DCAPD_ENABLE_MULTIPRECISION=ON` on Apple arm64 (macOS 26.5, Apple clang 21, MPFR 4.2.2, GMP 6.3.0). Each section is
meant as a separate GitHub issue. **The reproducers are self-contained and pasted inline below**, because this
repository is private. Each was re-run on 2026-10-17 against the installed 2f06098 (still upstream master's HEAD on
that date). The sources and outputs are in `qsim/capd/upstream_repro/` (`run_all.sh`, `run_all.out`).

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
  We found no way to create a NaN from finite inputs other than log. The search was exhaustive over a grid of
  reachable endpoints (±inf, ±MAX, ±1e9, ±1, ±tiny, ±0, 3) at 53 and 256 bits: + − × ÷ on every pair of boxes, and
  sqrt, exp, sin and cos (|x| ≤ 1e12) on every box, 85,902 cases in all. None gave a NaN endpoint.

**Suggestion.** An explicit domain check in `log` (as `sqrt` has); fix the parenthesis so `__MPI_TEST_NAN__` can be
enabled; unify the INF macro name.

Reproducer (the output, as re-run on 2026-10-17, is in the trailing comment):
```cpp
#include "capd/mpcapdlib.h"
#include <iostream>
int main() {
  capd::MpFloat::setDefaultPrecision(113);
  capd::MpInterval a(-1, 1), b(-2, -1);
  std::cout << "log([-1,1])  = " << log(a) << "\n";          // [NaN ,0 ]
  std::cout << "log([-2,-1]) = " << log(b) << "\n";          // [NaN ,NaN ]
  try { std::cout << sqrt(b) << "\n"; }                       // throws "MpInterval Function sqrt(x) - domain error"
  catch (std::exception& e) { std::cout << "sqrt throws: " << e.what() << "\n"; }
  capd::MpInterval z(capd::MpFloat(0), log(a).leftBound());  // [0, NaN]
  std::cout << "[0,NaN]*2 = " << z * 2 << "\n";              // [0 ,0 ]
}
```

---

## Issue B — `MpInterval` `sin`/`cos`: argument-reduction cost is linear in |x| (≈20 s at 1e13, ≈200 s at 1e14)

**What happens.** The cost of `sin(MpInterval(x))` for a point x grows linearly in |x|. Measured on 2026-10-17 at
256 bits on an Apple M-series machine:

| \|x\| | time |
|---|---|
| 1e9 | 2.3 ms |
| 1e10 | 18 ms |
| 1e11 | 0.18 s |
| 1e12 | 2.0 s |
| 1e13 | 19.6 s |
| 1e14 | 197 s |

That extrapolates to hours by about 1e16. The enclosures are correct (we checked against Arb up to 1e12), so this is a
cost problem, not a soundness problem. It is related to #28, which reports the double path with large negative
arguments, but on the MPFR path it affects positive arguments too.

**Why.** `modulo4()` in `MpInterval.cpp` reduces the quadrant number with
`while (x > 32000) x = x - MpReal(64000);`, i.e. about |x|/(π/2)/64000 MPFR subtractions. In addition, once the
quadrant number's ulp exceeds the step, these subtractions are inexact. At that point the loop could stop making
progress, or compute a wrong quadrant. This happens near |x| ~ 1e81 at 256 bits, and near ~6e20 at 53-bit MpFloat
precision. *(Not tested. It follows from reading the code, and it may be the same mechanism as #28's double-path
hang.)*

**Suggestion.** Compute the quadrant modulo 4 directly, e.g. `mpfr_fmod(q, 4)` or via `mpz` from the (exact)
`floor` that `quadrant()` already produces.

Reproducer:
```cpp
#include "capd/mpcapdlib.h"
#include <chrono>
#include <iostream>
int main() {
  capd::MpFloat::setDefaultPrecision(256);
  for (double x : {1e9, 1e10, 1e11, 1e12, 1e13}) {
    auto t0 = std::chrono::steady_clock::now();
    capd::MpInterval s = sin(capd::MpInterval(x));
    std::cout << "sin(" << x << "): " << std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() << " s\n";
  }
}
```

Our workaround: proof code range-checks every trig argument (|x| ≤ 1e12, fail closed) and runs under a hard
wall-clock watchdog.

---

## Issue C — #27 also reproduces on the MPFR path

`x' = 10(1 − x)`, `x(0) = 1` as a point set, t = 0.05: `MpIOdeSolver` throws "minimal time step reached", exactly
as the double `IOdeSolver` does; one ulp wider, `[1 − ulp, 1]`, both work (`x(0.05) ∈ [0.999999, 1.00001]`). It
fails loudly, so it is not a soundness issue.

Reproducer (the output, as re-run on 2026-10-17, is in the comments):
```cpp
#include "capd/capdlib.h"
#include "capd/mpcapdlib.h"
#include <cmath>
#include <iostream>
template <class Map, class Solver, class TM, class Vec, class Set, class Itv>
void run(const char* tag, double lo, double hi) {
  try {
    Map map("var:x;fun:10*(1-x);"); Solver solver(map, 12);
    solver.setAbsoluteTolerance(1e-10); solver.setRelativeTolerance(1e-10);
    TM tm(solver); Vec u0(1); u0[0] = Itv(lo, hi); Set set(u0);
    Vec r = tm(Itv(0.05), set); std::cout << tag << " " << r << "\n";
  } catch (const std::exception& e) { std::cout << tag << " THROW " << std::string(e.what()).substr(0, 60) << "\n"; }
}
int main() {
  capd::MpFloat::setDefaultPrecision(256);
  run<capd::MpIMap, capd::MpIOdeSolver, capd::MpITimeMap, capd::MpIVector, capd::MpC0Rect2Set, capd::MpInterval>("Mp point", 1.0, 1.0);                    // THROW ... minimal time step reached
  run<capd::MpIMap, capd::MpIOdeSolver, capd::MpITimeMap, capd::MpIVector, capd::MpC0Rect2Set, capd::MpInterval>("Mp 1ulp ", std::nextafter(1.0, 0.0), 1.0);  // {[9.99999e-1 ,1.00001 ]}
}
```

---

## Issue D — `intervalTest` `parse_from_sstream` (ctest #7) expects a non-rigorous bound

The test parses `"[3.21312312, 4.324324324]"` into a double interval and requires `rightBound() ==
4.324324324` (0% tolerance), i.e. the nearest double, 4.32432432399999999717…, which is **below** the decimal. On
arm64 NATIVE, CAPD returns 4.32432432400000088534… (the smallest double ≥ the decimal), which is the correct
outward rounding; the left bound is likewise the largest double ≤ 3.21312312 (verified exactly,
see the reproducer below). We suggest the test assert containment (`leftBound() ≤ decimal ≤ rightBound()`, e.g. in
exact rational arithmetic) rather than equality with the nearest double.

Reproducer:
```cpp
#include "capd/capdlib.h"
#include <cstdio>
#include <sstream>
int main() {
  capd::interval a{}; std::istringstream s("[3.21312312, 4.324324324]"); s >> a;
  std::printf("left  %.17g  %a\nright %.17g  %a\n", a.leftBound(), a.leftBound(), a.rightBound(), a.rightBound());
  // arm64 NATIVE: left 3.2131231199999997 0x1.9b479e4f35f32p+1, right 4.3243243240000009 0x1.14c1bacf3825ep+2
}
```

---

## Issue E — ctest #43 (`DPoincareMapMaskTest`) and #44 (`SingularNaturalPowerTest`) tolerances on arm64

Both are non-interval tests with absolute tolerances tuned on x86:
- #43 uses `DMap` with tol 1e−12 (1e−14 for the normal form); arm64 differences are 1.07e−12 to 2.05e−12 and
  1.56e−14, consistent with FMA contraction or libm last-bit differences.
- #44 uses `LDVector` with tol 1e−13; on Apple arm64 `long double` is 64-bit double (not 80-bit extended), and the
  differences (1.1e−13 to 7e−13, one 1.46e−11) are consistent with that.
Suggestion: relative tolerances, or tolerances tied to `std::numeric_limits<T>::epsilon()`.

---

## Issue F (minor) — two `MpReal` constructors are declared but not defined

`MpReal(mpq_srcptr, RoundingMode, PrecisionType)` and `MpReal(mpfr_t, RoundingMode, PrecisionType)` are both declared
in `capd/multiPrec/MpReal.h`. Using either gives an undefined-symbol link error (arm64, 2026-10-17). Either define them
(for example `mpfr_init2` plus `mpfr_set_q` / `mpfr_set` with the given rounding mode) or remove the declarations.

The mpq constructor would be the natural way to enclose an exact rational outward. We currently use `mpfr_set_q` on
the underlying `mpfr_t` with `MPFR_RNDD` / `MPFR_RNDU` instead.

Reproducer (it fails at link time):
```cpp
#include "capd/mpcapdlib.h"
int main() {
  mpq_t q; mpq_init(q); mpq_set_ui(q, 1, 3);
  capd::MpFloat a(q, capd::MpFloat::RoundDown);       // undefined: MpReal::MpReal(__mpq_struct const*, mpfr_rnd_t, MpPrecision)
  mpfr_t r; mpfr_init2(r, 64); mpfr_set_ui(r, 1, MPFR_RNDN);
  capd::MpFloat b(r, capd::MpFloat::RoundDown);       // undefined: MpReal::MpReal(__mpfr_struct*, mpfr_rnd_t, MpPrecision)
  return a < b;
}
```

---

## Issue G — Hermite–Obreshkov sets (`C0HO*`) do not compile with MPFR scalars

`capd::MpC0HOTripletonSet` (and the other HO sets) fail to compile. `capd/dynset/HOData.h:56` computes
`ScalarType(sign)/binomial(p+q,q)`, and the `unsigned long long` returned by `binomial` is ambiguous for `MpReal`:
"conversion from 'unsigned long long' to 'const capd::multiPrec::MpReal' is ambiguous". Your published Rössler
example (`examples/RosslerChaoticDynamics`) uses `C0HOTripletonSet`, so its MPFR port has to fall back to
`MpC0TripletonSet`. A possible fix is an explicit conversion, for example
`ScalarType(sign) / ScalarType(static_cast<long>(binomial(p+q,q)))`, or a `TypeTraits`-based cast.

Reproducer (it fails at compile time):
```cpp
#include "capd/mpcapdlib.h"
int main() {
  capd::MpFloat::setDefaultPrecision(128);
  capd::MpIMap f("var:x,y;fun:-y,x;"); capd::MpIOdeSolver solver(f, 20); capd::MpITimeMap tm(solver);
  capd::MpIVector x(2); x[0] = 1; x[1] = 0;
  capd::MpC0HOTripletonSet s(x);                     // HOData.h:56: ambiguous conversion from unsigned long long
  return tm(capd::MpInterval(1), s).dimension() == 2 ? 0 : 1;
}
```

---

## Differential check of MPFR interval arithmetic (context, could accompany A/B)

We ran 3 × 10⁵ random +, −, ×, ÷, sqrt, exp, log, sin, cos on `MpInterval` at 53, 113 and 256 bits (point,
narrow, wide, near-tie and huge/tiny boxes up to the MPFR exponent limits), checking each result against Arb
enclosures of the true range at ≥ 1024 bits. **Every result contained the true range** (0 failures), point-input
results were at most 1 ulp wide, and the checker's own mutation controls (collapsed intervals) were all detected.
The only anomaly was Issue A (NaN from log below 0). Thank you for a very solid MPFR interval layer.

---

## Revision note (quantum, 2026-10-17)

- **Reproducers.** All are now self-contained and inline: the quantum repository is private, so outsiders cannot use
  the old pointers to `qsim/capd/tests/`. Each was re-run against 2f06098, which is still upstream master's HEAD
  (`qsim/capd/upstream_repro/run_all.out`).
- **Issue B corrected.** The earlier text said sin "does not return within minutes for |x| ≳ 1e13". Measured, it
  takes 19.6 s at 1e13 and 197 s at 1e14, linear in |x|. The new text gives the measured timings.
- **Issue F extended.** The mpq constructor is undefined as well.
- **Issue G added** (HO sets with MPFR). It was found while porting CAPD's Rössler example for our phase-2 pipeline
  control.
- **Unchanged:** Issues A, C, D and E. A and C were re-verified on 2026-10-17.
- **Still to decide (for the user):** whether to file six separate issues, or one combined issue plus the "Thanks"
  note.

