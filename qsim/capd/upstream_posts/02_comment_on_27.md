**Comment on #27** (no title)

**Body:**

This reproduces on the MPFR path too: `MpIOdeSolver` / `MpITimeMap` with `MpC0Rect2Set` at 256 bits behave exactly
like the double `IOdeSolver`.
- For `x' = 10(1 − x)` with `x(0) = 1` as a point set, and t = 0.05, the solver throws "minimal time step reached".
- One ulp wider, `[1 − ulp, 1]`, both paths work: `x(0.05) ∈ [0.999999, 1.00001]`.

It fails loudly, so it is not a soundness problem.

**Environment.** CAPD master 2f060980d0685cc9bf88352e08c242197cd7d686 (HEAD as of 2026-10-17), built with `-DCAPD_INTERVAL_TYPE=NATIVE -DCAPD_ENABLE_MULTIPRECISION=ON` on Apple arm64 (macOS 26.5, Apple clang 21, MPFR 4.2.2, GMP 6.3.0).

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
