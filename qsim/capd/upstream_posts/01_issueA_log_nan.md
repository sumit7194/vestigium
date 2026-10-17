**Title:** MpInterval: log of an interval reaching below 0 returns NaN endpoints instead of a domain error (and the NaN-test macros don't compile or don't fire)

**Body:**

Thank you for CAPD. Thanks also for PR #18 (`CAPD_INTERVAL_TYPE = NATIVE`) and PR #22 (host processor recognition):
with them, master builds and runs on Apple arm64 without filib and without any local patch. We are using the MPFR
interval layer for computer-assisted proofs, and report below a few things we found while auditing it.

**Environment.** CAPD master 2f060980d0685cc9bf88352e08c242197cd7d686 (HEAD as of 2026-10-17), built with `-DCAPD_INTERVAL_TYPE=NATIVE -DCAPD_ENABLE_MULTIPRECISION=ON` on Apple arm64 (macOS 26.5, Apple clang 21, MPFR 4.2.2, GMP 6.3.0).

**What happens.** For an `MpInterval` whose left endpoint is negative, `log(x)` returns an interval with a NaN left
endpoint, and a NaN right endpoint too if the whole box is negative, instead of throwing. `sqrt` on the same boxes
throws "MpInterval Function sqrt(x) - domain error", so the two behave inconsistently.

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
  std::cout << "[0,NaN]*2 = " << z * 2 << "\n";              // [0 ,0 ]  (the NaN is swallowed)
}
```

**Why.** `log` in `capdAlg/src/mpcapd/intervals/MpInterval.cpp` relies on `testNaN(res)`. But `testNaN` is a no-op
unless `__MPI_TEST_NAN__` is defined, and that define is commented out in `MpIntervalSettings.h`.

**Why it matters.** A NaN endpoint can pass silently through comparisons written as `!(a < b)`. It does not make a
wrong enclosure of a defined value, but a computer-assisted proof should fail loudly here.

**Related, found while trying to enable the check:**
- **It doesn't compile.** `-D__MPI_TEST_NAN__` fails because of an extra `)` at `MpInterval_Fun.hpp:36`:
  `if(isNaN(x.leftBound()) || isNaN(x.rightBound())))`.
- **It doesn't cover much.** Even when enabled, `testNaN` is only called for the sin/cos/tan arguments and the
  log/exp results, never in + − × ÷.
- **The INF macro does nothing.** The documented `__MPI_TEST_INF__` (in `MpIntervalSettings.h`) has no effect,
  because `MpInterval.cpp` tests `_MPI_TEST_INF_` (lines 79, 238 and 399).
- **NaNs can be swallowed.** Multiplication can turn a NaN endpoint next to a 0 endpoint into a finite result, as
  above: `[0, NaN] * 2 = [0, 0]`.
- **log seems to be the only source.** We found no way to create a NaN from finite inputs other than log. The search
  was exhaustive over a grid of reachable endpoints (±inf, ±MAX, ±1e9, ±1, ±tiny, ±0, 3) at 53 and 256 bits: + − × ÷
  on every pair of boxes, and sqrt, exp, sin and cos (|x| ≤ 1e12) on every box, 85,902 cases in all. None gave a NaN
  endpoint.

**Suggestion.**
- Add an explicit domain check in `log`, as `sqrt` has.
- Fix the parenthesis so that `__MPI_TEST_NAN__` can be enabled.
- Unify the INF macro name.

**Context: a differential check of the MPFR interval layer.** We ran 3 × 10⁵ random +, −, ×, ÷, sqrt, exp, log, sin
and cos operations on `MpInterval` at 53, 113 and 256 bits. The inputs were point, narrow, wide, near-tie and
huge/tiny boxes up to the MPFR exponent limits. Each result was checked against Arb enclosures of the true range at
≥ 1024 bits.
- **Every result contained the true range** (0 failures).
- Point-input results were at most 1 ulp wide.
- The checker's own mutation controls (collapsed intervals) were all detected.
- The only anomaly was the log NaN above.

Thank you for a very solid MPFR interval layer.
