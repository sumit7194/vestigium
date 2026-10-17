**Title:** arm64 NATIVE: three ctest failures (#7, #43, #44) that look test-side, not library defects

**Body:**

On Apple arm64 with `CAPD_INTERVAL_TYPE=NATIVE`, 41 of the 44 ctest tests pass. We believe the three failures are
in the tests, not the library.

**Environment.** CAPD master 2f060980d0685cc9bf88352e08c242197cd7d686 (HEAD as of 2026-10-17), built with `-DCAPD_INTERVAL_TYPE=NATIVE -DCAPD_ENABLE_MULTIPRECISION=ON` on Apple arm64 (macOS 26.5, Apple clang 21, MPFR 4.2.2, GMP 6.3.0).

**1. `intervalTest` `parse_from_sstream` (ctest #7) expects a non-rigorous bound.**

The test parses `"[3.21312312, 4.324324324]"` into a double interval and requires `rightBound() == 4.324324324` (0%
tolerance). That is the nearest double, 4.32432432399999999717…, which is **below** the decimal. On arm64 NATIVE, CAPD
returns 4.32432432400000088534…, the smallest double ≥ the decimal, which is the correct outward rounding. The left
bound, 3.21312311999999966616…, is likewise the largest double ≤ 3.21312312. Both were checked in exact rational
arithmetic.

We suggest the test assert containment in exact rational arithmetic, `leftBound() ≤ decimal ≤ rightBound()`, rather
than equality with the nearest double.

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

**2. ctest #43 (`DPoincareMapMaskTest`) and #44 (`SingularNaturalPowerTest`): absolute tolerances tuned on x86.**

Both are non-interval tests.
- **#43** uses `DMap` with tolerance 1e−12 (1e−14 for the normal form). The arm64 differences are 1.07e−12 to
  2.05e−12, and 1.56e−14. That is consistent with FMA contraction or with last-bit differences in libm.
- **#44** uses `LDVector` with tolerance 1e−13. On Apple arm64, `long double` is a 64-bit double, not 80-bit
  extended. The differences (1.1e−13 to 7e−13, and one of 1.46e−11) are consistent with that.

We suggest relative tolerances, or tolerances tied to `std::numeric_limits<T>::epsilon()`.
