**Title:** MpInterval sin/cos: argument-reduction cost is linear in |x| (≈20 s at 1e13, ≈200 s at 1e14)

**Body:**

This is related to #28, which reports the double path with large negative arguments. On the MPFR path, the cost of
`sin(MpInterval(x))` for a point x grows linearly in |x|, for positive arguments too.

**Environment.** CAPD master 2f060980d0685cc9bf88352e08c242197cd7d686 (HEAD as of 2026-10-17), built with `-DCAPD_INTERVAL_TYPE=NATIVE -DCAPD_ENABLE_MULTIPRECISION=ON` on Apple arm64 (macOS 26.5, Apple clang 21, MPFR 4.2.2, GMP 6.3.0).

Measured at 256 bits on an Apple M-series machine:

| \|x\| | time |
|---|---|
| 1e9 | 2.3 ms |
| 1e10 | 18 ms |
| 1e11 | 0.18 s |
| 1e12 | 2.0 s |
| 1e13 | 19.6 s |
| 1e14 | 197 s |

That extrapolates to hours by about 1e16. The enclosures are correct (we checked against Arb up to 1e12), so this is a
cost problem, not a soundness problem.

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

**Why.** `modulo4()` in `MpInterval.cpp` reduces the quadrant number with `while (x > 32000) x = x - MpReal(64000);`.
That is about |x|/(π/2)/64000 MPFR subtractions. In addition, once the quadrant number's ulp exceeds the step, these
subtractions are inexact. At that point the loop could stop making progress, or compute a wrong quadrant. This happens
near |x| ~ 1e81 at 256 bits, and near ~6e20 at 53-bit MpFloat precision. *(Not tested. It follows from reading the
code, and it may be the same mechanism as #28's double-path hang.)*

**Suggestion.** Compute the quadrant modulo 4 directly: for example `mpfr_fmod(q, 4)`, or via `mpz` from the exact
`floor` that `quadrant()` already produces.
